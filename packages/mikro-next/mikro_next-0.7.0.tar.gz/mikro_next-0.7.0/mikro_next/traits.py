"""
Traits for mikro_next

Traits are mixins that are added to every graphql type that exists on the mikro schema.
We use them to add functionality to the graphql types that extend from the base type.

Every GraphQL Model on Mikro gets a identifier and shrinking methods to ensure the compatibliity
with arkitekt. This is done by adding the identifier and the shrinking methods to the graphql type.
If you want to add your own traits to the graphql type, you can do so by adding them in the graphql
.config.yaml file.

"""

from typing import Awaitable, List, Type, TypeVar, Tuple, Protocol, Optional
import numpy as np
from numpy.typing import NDArray
from pydantic import BaseModel
import xarray as xr
import pandas as pd
from typing import TYPE_CHECKING
from dask.array.core import from_zarr  # type: ignore
from zarr.storage import FsspecStore
from .scalars import FiveDVector
from rath.scalars import ID
from typing import Any
from rath.turms.utils import get_attributes_or_error


TwoDArray = NDArray[np.float_]
OneDArray = NDArray[np.float_]


if TYPE_CHECKING:
    from pyarrow.parquet import ParquetDataset  # type: ignore
    from mikro_next.api.schema import HasZarrStoreAccessor


class HasZarrStoreTrait(BaseModel):
    """Image Trait

    Implements both identifier and shrinking methods.
    Also Implements the data attribute

    Attributes:
        data (xarray.Dataset): The data of the representation.

    """

    @property
    def data(self) -> xr.DataArray:
        """The data of this image as an xarray.DataArray"""
        from dask.array.core import Array

        store: HasZarrStoreAccessor = get_attributes_or_error(self, "store")

        array: Array = from_zarr(store.zarr_store)

        return xr.DataArray(array, dims=["c", "t", "z", "y", "x"])

    @property
    def multi_scale_data(self) -> List[xr.DataArray]:
        """The multi-scale data of this image as a list of xarray.DataArray"""
        scale_views = get_attributes_or_error(self, "derived_scale_views")

        if len(scale_views) == 0:
            raise ValueError("No ScaleView found in views. Please create a ScaleView first.")

        sorted_views = sorted(scale_views, key=lambda image: image.scale_x)
        return [x.image.data for x in sorted_views]

    async def adata(self) -> Awaitable[xr.DataArray]:
        """The Data of the Representation as an xr.DataArray. Accessible from asyncio.

        Returns:
            xr.DataArray: The associated object.

        Raises:
            AssertionError: If the representation has no store attribute quries
        """
        pstore = get_attributes_or_error(self, "store")
        return await pstore.aopen()

    def get_pixel_size(self, stage: ID | None = None) -> Tuple[float, float, float]:
        """The pixel size of the representation

        Returns:
            Tuple[float, float, float]: The pixel size
        """
        from mikro_next.api.schema import AffineTransformationView

        views = get_attributes_or_error(self, "views")

        for view in views:
            if isinstance(view, AffineTransformationView):
                if stage is None:
                    return view.affine_matrix.as_matrix().diagonal()[:3]  # type: ignore
                else:
                    if get_attributes_or_error(view, "stage.id") == stage:
                        return view.affine_matrix.as_matrix().diagonal()[:3]  # type: ignore

        raise NotImplementedError(
            f"No pixel size found for this representation {self}. Have you attached any views?"
        )


class PhysicalSizeProtocol(Protocol):
    """A Protocol for Vectorizable data

    Attributes:
        x (float): The x value
        y (float): The y value
        z (float): The z value
        t (float): The t value
        c (float): The c value
    """

    x: float | None
    y: float | None
    z: float | None
    t: float | None
    c: float | None

    def __init__(
        self,
        x: Optional[float] = None,
        y: Optional[float] = None,
        z: Optional[float] = None,
        t: Optional[float] = None,
        c: Optional[float] = None,
    ) -> None:
        """Initialize the PhysicalSizeProtocol."""
        ...


class PhysicalSizeTrait:
    """Additional Methods for PhysicalSize"""

    def is_similar(
        self: PhysicalSizeProtocol,
        other: PhysicalSizeProtocol,
        tolerance: float = 0.02,
        raise_exception: Optional[bool] = False,
    ) -> bool:
        if hasattr(self, "x") and self.x is not None and other.x is not None:
            if abs(other.x - self.x) > tolerance:
                if raise_exception:
                    raise ValueError(
                        f"X values are not similar: {self.x} vs {other.x} is above tolerance {tolerance}"
                    )
                return False
        if hasattr(self, "y") and self.y is not None and other.y is not None:
            if abs(other.y - self.y) > tolerance:
                if raise_exception:
                    raise ValueError(
                        f"Y values are not similar: {self.y} vs {other.y} is above tolerance {tolerance}"
                    )
                return False
        if hasattr(self, "z") and self.z is not None and other.z is not None:
            if abs(other.z - self.z) > tolerance:
                if raise_exception:
                    raise ValueError(
                        f"Z values are not similar: {self.z} vs {other.z} is above tolerance {tolerance}"
                    )
                return False
        if hasattr(self, "t") and self.t is not None and other.t is not None:
            if abs(other.t - self.t) > tolerance:
                if raise_exception:
                    raise ValueError(
                        f"T values are not similar: {self.t} vs {other.t} is above tolerance {tolerance}"
                    )
                return False
        if hasattr(self, "c") and self.c is not None and other.c is not None:
            if abs(other.c - self.c) > tolerance:
                if raise_exception:
                    raise ValueError(
                        f"C values are not similar: {self.c} vs {other.c} is above tolerance {tolerance}"
                    )
                return False

        return True

    def to_scale(self) -> List[float]:
        """Get the scale of the physical size
        Returns:
            List[float]: The scale of the physical size
        """
        return [
            getattr(self, "t", 1),
            getattr(self, "c", 1),
            getattr(self, "z", 1),
            getattr(self, "y", 1),
            getattr(self, "x", 1),
        ]


class IsVectorizableTrait:
    """Additional Methods for ROI"""

    @property
    def vector_data(self) -> TwoDArray:
        """A numpy array of the vectors of the ROI

        Returns:
            np.ndarray: _description_
        """
        return self.get_vector_data(dims="yx")

    def get_vector_data(self, dims: str | list[str] = "yx") -> TwoDArray:
        """Get the vector data of the ROI as a numpy array"""
        vector_list = get_attributes_or_error(self, "vectors")
        assert vector_list, (
            "Please query 'vectors' in your request on 'ROI'. Data is not accessible otherwise"
        )
        vector_list: list[list[float]]

        mapper = {
            "y": 4,
            "x": 3,
            "z": 2,
            "t": 1,
            "c": 0,
        }

        return np.array([[v[mapper[ac]] for ac in dims] for v in vector_list])

    def center(self) -> FiveDVector:
        """The center of the ROI

        Caluclates the geometrical center of the ROI according to its type
        and the vectors of the ROI.

        Returns:
            InputVector: The center of the ROI
        """
        from mikro_next.api.schema import RoiKind, FiveDVector

        kind = get_attributes_or_error(self, "kind")
        if kind == RoiKind.RECTANGLE:
            return FiveDVector.validate(self.get_vector_data(dims="ctzyx").mean(axis=0))

        raise NotImplementedError(f"Center calculation not implemented for this ROI type {kind}")

    def crop(self, data: xr.DataArray) -> xr.DataArray:
        """Crop the data to the ROI

        Args:
            data (xr.DataArray): The data to crop

        Returns:
            xr.DataArray: The cropped data
        """
        vector_data = self.get_vector_data(dims="ctzyx")
        return data.sel(  # type: ignore
            x=slice(vector_data[:, 3].min(), vector_data[:, 3].max()),
            y=slice(vector_data[:, 4].min(), vector_data[:, 4].max()),
            z=slice(vector_data[:, 2].min(), vector_data[:, 2].max()),
            t=slice(vector_data[:, 1].min(), vector_data[:, 1].max()),
            c=slice(vector_data[:, 0].min(), vector_data[:, 0].max()),
        )  # type: ignore

    def center_as_array(self) -> OneDArray:
        """The center of the ROI

        Caluclates the geometrical center of the ROI according to its type
        and the vectors of the ROI.

        Returns:
            InputVector: The center of the ROI
        """
        from mikro_next.api.schema import RoiKind

        kind = get_attributes_or_error(self, "kind")
        if kind == RoiKind.RECTANGLE:
            return self.get_vector_data(dims="ctzyx").mean(axis=0)
        if kind == RoiKind.POINT:
            return self.get_vector_data(dims="ctzyx")[0]

        raise NotImplementedError(f"Center calculation not implemented for this ROI kind {kind}")


class HasParquestStoreTrait(BaseModel):
    """Table Trait

    Implements both identifier and shrinking methods.
    Also Implements the data attribute

    Attributes:
        data (pd.DataFrame): The data of the table.

    """

    @property
    def data(self) -> pd.DataFrame:
        """The data of this table as a pandas dataframe

        Returns:
            pd.DataFrame: The Dataframe
        """
        store: "HasParquetStoreAccesor" = get_attributes_or_error(self, "store")
        return store.parquet_dataset.read_pandas().to_pandas()  # type: ignore


V = TypeVar("V")


class HasZarrStoreAccessor(BaseModel):
    """Zarr Store Accessor

    Allows to access the python zarr store of
    a ZarrStore object.


    """

    _openstore: Any = None

    @property
    def zarr_store(self) -> FsspecStore:
        """The zarr store of the ZarrStore object"""
        from mikro_next.io.download import open_zarr_store

        if self._openstore is None:
            id = get_attributes_or_error(self, "id")
            self._openstore = open_zarr_store(id)
        return self._openstore


class HasParquetStoreAccesor(BaseModel):
    """Parquet Store Accessor"""

    _dataset: Any = None

    @property
    def parquet_dataset(self) -> "ParquetDataset":
        """The Parquet Dataset of the ParquetStore object"""
        from mikro_next.io.download import open_parquet_filesystem

        if self._dataset is None:
            id = get_attributes_or_error(self, "id")
            self._dataset = open_parquet_filesystem(id)
        return self._dataset


class HasDownloadAccessor(BaseModel):
    """Download Accessor"""

    _dataset: Any = None

    def download(self, file_name: str | None = None) -> "str":
        """Download the file from the presigned URL

        Args:
            file_name (str | None): The name of the file to save the downloaded file as
                If None, the key from the presigned URL will be used as the file name.
        Returns:
            str: The path to the downloaded file
        """
        from mikro_next.io.download import download_file

        url, key = get_attributes_or_error(self, "presigned_url", "key")
        return download_file(url, file_name=file_name or key)


class HasPresignedDownloadAccessor(BaseModel):
    """Presigned Download Accessor

    TODO: THis should probablry bre refactored to a more generic download accessor

    """

    _dataset: Any = None

    def download(self, file_name: str | None = None) -> str:
        """Download the file from the presigned URL

        Args:
            file_name (str | None): The name of the file to save the downloaded file as
                If None, the key from the presigned URL will be used as the file name.
        Returns:
            str: The path to the downloaded file
        """
        from mikro_next.io.download import download_file

        url, key = get_attributes_or_error(self, "presigned_url", "key")
        return download_file(url, file_name=file_name or key)


class Vector(Protocol):
    """A Protocol for Vectorizable data

    Attributes:
        x (float): The x value
        y (float): The y value
        z (float): The z value
        t (float): The t value
        c (float): The c value
    """

    x: float
    y: float
    z: float
    t: float
    c: float

    def __init__(
        self,
        x: Optional[int] = None,
        y: Optional[int] = None,
        z: Optional[int] = None,
        t: Optional[int] = None,
        c: Optional[int] = None,
    ) -> None: ...


T = TypeVar("T", bound=Vector)


class HasPixelSizeTrait:
    """Mixin for PixelTranslatable data"""

    @property
    def pixel_size(self) -> Tuple[float, float, float]:
        """The pixel size of the representation

        Returns:
            Tuple[float, float, float]: The pixel size
        """
        kind, matrix = get_attributes_or_error(self, "kind", "matrix")

        if kind == "AFFINE":
            return tuple(np.array(matrix).reshape(4, 4).diagonal()[:3])

        raise NotImplementedError(f"Pixel size not implemented for this kind {kind}")

    @property
    def position(self) -> Tuple[float, float, float]:
        """The pixel size of the representation

        Returns:
            Tuple[float, float, float]: The pixel size
        """
        kind, matrix = get_attributes_or_error(self, "kind", "matrix")

        if kind == "AFFINE":
            return tuple(np.array(matrix).reshape(4, 4)[:3, 3])

        raise NotImplementedError(f"Pixel size not implemented for this kind {kind}")


class HasFromNumpyArrayTrait:
    """Mixin for Vectorizable data
    adds functionality to convert a numpy array to a list of vectors
    """

    @classmethod
    def list_from_numpyarray(
        cls: Type[T],
        x: TwoDArray,
        t: Optional[int] = None,
        c: Optional[int] = None,
        z: Optional[int] = None,
    ) -> List[T]:
        """Creates a list of InputVector from a numpya array

        Args:
            vector_list (List[List[float]]): A list of lists of floats

        Returns:
            List[Vectorizable]: A list of InputVector
        """
        assert x.ndim == 2, "Needs to be a List array of vectors"
        if x.shape[1] == 4:
            return [cls(x=i[1], y=i[0], z=i[2], t=i[3], c=c) for i in x.tolist()]
        if x.shape[1] == 3:
            return [cls(x=i[1], y=i[0], z=i[2], t=t, c=c) for i in x.tolist()]
        elif x.shape[1] == 2:
            return [cls(x=i[1], y=i[0], t=t, c=c, z=z) for i in x.tolist()]
        else:
            raise NotImplementedError(
                f"Incompatible shape {x.shape} of {x}. List dimension needs to either be of size 2 or 3"
            )

    @classmethod
    def from_array(
        cls: Type[T],
        x: OneDArray,
    ) -> T:
        """Creates a InputVector from a numpy array"""
        assert x.ndim == 1, "Needs to be a 1D array of floats"
        return cls(x=x[4], y=x[3], z=x[2], t=x[1], c=x[0])


class FileTrait:
    """A trait for file-like objects that can be downloaded
    because they have a big file store attached to them.
    """

    def download(self, file_name: str | None = None) -> "str":
        """Download the file from the store

        Args:
            file_name (str | None): The name of the file to save the downloaded file as
                If None, the key from the store will be used as the file name.
        Returns:
            str: The path to the downloaded file
        """
        store: "HasPresignedDownloadAccessor" = get_attributes_or_error(self, "store")
        return store.download(file_name=file_name)
