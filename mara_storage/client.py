from functools import singledispatch
import datetime
import typing as t

from mara_storage import storages


class StorageClient():
    """A base class for a storage client"""
    def __new__(cls, storage: t.Union[str, storages.Storage]):
        if storage is None:
            raise ValueError('Please provide the storage prameter')

        if cls is StorageClient:
            cls = storage_client_type(storage)
            return cls(storage)
        else:
            return super(StorageClient, cls).__new__(cls)

    def __init__(self, storage: t.Union[str, storages.Storage]):
        if isinstance(storage, str):
            self._storage = storages.storage(storage)
        else:
            self._storage = storage

    def last_modification_timestamp(self, path: str) -> datetime.datetime:
        """Returns the last modification timestamp for a object (path or file) on a storage"""
        raise NotImplementedError(f'Please implement last_modification_timestamp for type "{self._storage.__class__.__name__}"')

    def iterate_files(self, file_pattern: str) -> t.Iterator[str]:
        """
        Iterates over files on on a storage

        Args:
            file_pattern: the file pattern, e.g. 'subfolder/*.csv'
        """
        raise NotImplementedError(f'Please implement iterate_files for type "{self._storage.__class__.__name__}"')


@singledispatch
def storage_client_type(storage: object):
    """Returns the client type for a storage configuration"""
    raise NotImplementedError(f'Please implement storage_client_type for type "{storage.__class__.__name__}"')

@storage_client_type.register(str)
def __(alias: str) -> StorageClient:
    return storage_client_type(storages.storage(alias))

@storage_client_type.register(storages.LocalStorage)
def __(storage: storages.LocalStorage):
    from .local_storage import LocalStorageClient
    return LocalStorageClient

@storage_client_type.register(storages.GoogleCloudStorage)
def __(storage: storages.GoogleCloudStorage):
    from .google_cloud_storage import GoogleCloudStorageClient
    return GoogleCloudStorageClient
