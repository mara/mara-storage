import datetime
import glob
import os
import pathlib
import typing as t

from mara_storage import storages
from mara_storage.client import StorageClient


class LocalStorageClient(StorageClient):
    def __init__(self, storage: storages.LocalStorage):
        super().__init__(storage)

    def last_modification_timestamp(self, path: str) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(
            os.path.getmtime(self._storage.base_path.absolute() / path)).astimezone()

    def iterate_files(self, file_pattern: str)-> t.Iterator[str]:
        for file in glob.iglob(str(self._storage.base_path / file_pattern)):
            yield str(pathlib.Path(file).relative_to(self._storage.base_path))
