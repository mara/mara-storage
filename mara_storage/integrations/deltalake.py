"""
Helper functions interacting with module deltalake.
"""
from functools import singledispatch
from pathlib import Path
from typing import Self, Union, Optional, Dict

import deltalake

from mara_storage import storages


@singledispatch
def deltalake_build_uri(storage, path: str):
    """
    Creates a URI path for deltalake
    """
    raise NotImplementedError(f'Please implement deltalake_build_uri for type "{storage.__class__.__name__}"')


@deltalake_build_uri.register(str)
def __(storage: str, path: str):
    return deltalake_build_uri(storages.storage(storage), path=path)


@deltalake_build_uri.register(storages.AzureStorage)
def __(storage: storages.AzureStorage, path: str):
    return f'abfs://{storage.container_name}/{path}'


@deltalake_build_uri.register(storages.GoogleCloudStorage)
def __(storage: storages.AzureStorage, path: str):
    return f'gs://{storage.bucket_name}/{path}'



@singledispatch
def deltalake_storage_options(storage):
    """
    Returns the storage options required for the deltalake module.

    See as well:
        https://docs.rs/object_store/latest/object_store/azure/enum.AzureConfigKey.html#variants

    Args:
        storage: The storage as alias or class.
    """
    raise NotImplementedError(f'Please implement deltalake_storage_options for type "{storage.__class__.__name__}"')


@deltalake_storage_options.register(str)
def __(storage: str):
    return deltalake_storage_options(storages.storage(storage))


@deltalake_storage_options.register(storages.AzureStorage)
def __(storage: storages.AzureStorage):
    return {
        # See https://docs.rs/object_store/latest/object_store/azure/enum.AzureConfigKey.html#variants
        'account_name': storage.account_name,
        'account_key': storage.account_key,
        'sas_key': storage.sas
    }


@deltalake_storage_options.register(storages.GoogleCloudStorage)
def __(storage: storages.GoogleCloudStorage):
    return {
        # See https://docs.rs/object_store/latest/object_store/gcp/enum.GoogleConfigKey.html#variants
        'bucket_name': storage.bucket_name,
        'service_account': storage.service_account_file
    }


class DeltaTable(deltalake.DeltaTable):
    def __new__(cls: type[Self], path: str = None, version: Optional[int] = None, storage_options: Optional[Dict[str, str]] = None,
                without_files: bool = False, table_uri: Union[str, Path] = None, storage: Union[str, storages.Storage] = None, **kargs) -> Self:
        """
        Create the Delta Table from a path with an optional version.
        Multiple StorageBackends are currently supported: AWS S3, Azure Data Lake Storage Gen2, Google Cloud Storage (GCS) and local URI.
        Depending on the storage backend used, you could provide options values using the ``storage_options`` parameter.
        :param path: the path of the DeltaTable. When you want to use URI, use parameter `table_uri`.
        :param version: version of the DeltaTable
        :param storage_options: a dictionary of the options to use for the storage backend
        :param without_files: If True, will load table without tracking files.
                              Some append-only applications might have no need of tracking any files. So, the
                              DeltaTable will be loaded with a significant memory reduction.
        :param table_uri: the path of the DeltaTable. If set, parameter `path` is ignored.
        :param storage: the mara storage as alias or class
        """

        if table_uri is None:
            if storage:
                table_uri = deltalake_build_uri(storage, path)
            elif path:
                table_uri = path
            else:
                raise ValueError('You either have to ')

        if storage_options is None:
            storage_options = {}

        if storage:
            storage_options = deltalake_storage_options(storage).update(storage_options)

        return DeltaTable(
            table_uri=table_uri,
            version=version,
            storage_options=storage_options,
            without_files=without_files)
