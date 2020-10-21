from functools import singledispatch
import datetime

from mara_storage import storages


class StorageClient:
    """A base class for a storage client"""
    def __init__(self, storage: object):
        self._storage = storage

    def last_modification_timestamp(self, path: str) -> datetime.datetime:
        """Returns the last modification timestamp for a object (path or file) on a storage"""
        raise NotImplementedError(f'Please implement last_modification_timestamp for type "{self._storage.__class__.__name__}"')

    def iterate_files(self, file_pattern: str):
        """
        Iterates over files on on a storage
        
        Args:
            file_pattern: the file pattern, e.g. 'subfolder/*.csv'
        """
        raise NotImplementedError(f'Please implement iterate_files for type "{self._storage.__class__.__name__}"')


@singledispatch
def init_client(storage: object) -> StorageClient:
    """Initiates a storage client for a storage configuration"""

@init_client.register(str)
def __(alias: str) -> StorageClient:
    return init_client(storages.storage(alias))

@init_client.register(storages.LocalStorage)
def __(storage: storages.LocalStorage):
    from .local_storage import LocalStorageClient
    return LocalStorageClient(storage)
