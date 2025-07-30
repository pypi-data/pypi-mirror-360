"""Module for uploading various data types to a DataLayer using asynchronous methods."""

import os
from typing import TYPE_CHECKING
from mikro_next.scalars import ArrayLike, ImageFileLike, MeshLike, ParquetLike, FileLike
import asyncio
import s3fs  # type: ignore
from aiobotocore.session import get_session  # type: ignore
import botocore  # type: ignore
from concurrent.futures import ThreadPoolExecutor

from .errors import PermissionsError, UploadError
from zarr.storage import FsspecStore
import zarr.api.asynchronous as async_api
import aiohttp

if TYPE_CHECKING:
    from mikro_next.api.schema import Credentials, PresignedPostCredentials
    from mikro_next.datalayer import DataLayer


async def astore_xarray_input(
    xarray: ArrayLike,
    credentials: "Credentials",
    endpoint_url: str,
) -> str:
    """Stores an xarray in the DataLayer"""

    if endpoint_url.startswith("https://"):
        os.environ["AWS_REQUEST_CHECKSUM_CALCULATION"] = (
            "when_required"  # TODO: This is a workaround for a bug in aiobotocore and s3fs https://github.com/fsspec/s3fs/issues/931
        )

    filesystem = s3fs.S3FileSystem(
        secret=credentials.secret_key,
        key=credentials.access_key,
        client_kwargs={
            "endpoint_url": endpoint_url,
            "aws_session_token": credentials.session_token,
        },
        asynchronous=True,
    )

    # random_uuid = uuid.uuid4()
    # s3_path = f"zarr/{random_uuid}.zarr"

    array = xarray.value.transpose("c", "t", "z", "y", "x")

    s3_path = f"{credentials.bucket}/{credentials.key}"
    store = FsspecStore(filesystem, read_only=False, path=s3_path)

    try:
        await async_api.save_array(store, array.to_numpy(), zarr_version=3)  # type: ignore
        return credentials.store
    except Exception as e:
        raise UploadError(f"Error while uploading to {s3_path} on {endpoint_url}") from e


def _store_parquet_input(
    parquet_input: ParquetLike,
    credentials: "Credentials",
    endpoint_url: str,
) -> str:
    """Stores an xarray in the DataLayer"""
    import pyarrow.parquet as pq  # type: ignore
    from pyarrow import Table  # type: ignore

    filesystem = s3fs.S3FileSystem(
        secret=credentials.secret_key,
        key=credentials.access_key,
        client_kwargs={
            "endpoint_url": endpoint_url,
            "aws_session_token": credentials.session_token,
        },
    )

    table: Table = Table.from_pandas(parquet_input.value)  # type: ignore

    s3_path = f"s3://{credentials.bucket}/{credentials.key}"
    try:
        pq.write_table(table, s3_path, filesystem=filesystem)  # type: ignore
        return credentials.store
    except Exception as e:
        raise UploadError(f"Error while uploading to {s3_path}") from e


async def astore_mesh_file(
    mesh: MeshLike,
    credentials: "PresignedPostCredentials",
    datalayer: "DataLayer",
) -> str:
    """Store a mesh file in the DataLayer using presigned POST credentials."""
    endpoint_url = await datalayer.get_endpoint_url()

    async with aiohttp.ClientSession() as session:
        form_data = aiohttp.FormData()
        form_data.add_field("key", credentials.key)
        form_data.add_field("policy", credentials.policy)
        form_data.add_field("x-amz-algorithm", credentials.x_amz_algorithm)
        form_data.add_field("x-amz-credential", credentials.x_amz_credential)
        form_data.add_field("x-amz-date", credentials.x_amz_date)
        form_data.add_field("x-amz-signature", credentials.x_amz_signature)
        form_data.add_field(
            "file",
            mesh.value,
            filename="mesh.obj",
            content_type="application/octet-stream",
        )

        url = endpoint_url + "/" + credentials.bucket

        async with session.post(url, data=form_data) as resp:
            if resp.status not in {200, 204}:
                body = await resp.text()
                raise UploadError(f"Error while uploading mesh: HTTP {resp.status}: {body}")

    return credentials.store


async def astore_media_file(
    file: ImageFileLike,
    credentials: "PresignedPostCredentials",
    datalayer: "DataLayer",
) -> str:
    """Store a media file in the DataLayer using presigned POST credentials."""
    endpoint_url = await datalayer.get_endpoint_url()

    async with aiohttp.ClientSession() as session:
        form_data = aiohttp.FormData()
        form_data.add_field("key", credentials.key)
        form_data.add_field("policy", credentials.policy)
        form_data.add_field("x-amz-algorithm", credentials.x_amz_algorithm)
        form_data.add_field("x-amz-credential", credentials.x_amz_credential)
        form_data.add_field("x-amz-date", credentials.x_amz_date)
        form_data.add_field("x-amz-signature", credentials.x_amz_signature)
        form_data.add_field(
            "file",
            file.value,
            filename=file.file_name,
            content_type="application/octet-stream",
        )

        url = endpoint_url + "/" + credentials.bucket

        async with session.post(url, data=form_data) as resp:
            if resp.status not in {200, 204}:
                body = await resp.text()
                raise UploadError(f"Error while uploading mesh: HTTP {resp.status}: {body}")

    print("Successfully uploaded media file", credentials)
    return credentials.store


async def aupload_bigfile(
    file: FileLike | ImageFileLike,
    credentials: "Credentials",
    datalayer: "DataLayer",
) -> str:
    """Store a DataFrame in the DataLayer"""
    session = get_session()

    endpoint_url = await datalayer.get_endpoint_url()

    async with session.create_client(  # type: ignore
        "s3",
        region_name="us-west-2",
        endpoint_url=endpoint_url,
        aws_secret_access_key=credentials.secret_key,
        aws_access_key_id=credentials.access_key,
        aws_session_token=credentials.session_token,
    ) as client:
        try:
            print(credentials, file.value)
            await client.put_object(Bucket=credentials.bucket, Key=credentials.key, Body=file.value)  # type: ignore
        except botocore.exceptions.ClientError as e:  # type: ignore
            if e.response["Error"]["Code"] == "InvalidAccessKeyId":  # type: ignore
                return PermissionsError("Access Key is invalid, trying to get new credentials")  # type: ignore

            raise e

    print(credentials)
    return credentials.store


async def aupload_xarray(
    array: ArrayLike,
    credentials: "Credentials",
    datalayer: "DataLayer",
) -> str:
    """Store a DataFrame in the DataLayer"""
    return await astore_xarray_input(array, credentials, await datalayer.get_endpoint_url())


async def aupload_parquet(
    parquet: ParquetLike,
    credentials: "Credentials",
    datalayer: "DataLayer",
    executor: ThreadPoolExecutor,
) -> str:
    """Store a DataFrame in the DataLayer"""
    co_future = executor.submit(
        _store_parquet_input, parquet, credentials, await datalayer.get_endpoint_url()
    )
    return await asyncio.wrap_future(co_future)
