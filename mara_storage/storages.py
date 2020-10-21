"""Abstract definition of storage connections"""

import functools
import pathlib


@functools.lru_cache(maxsize=None)
def storage(alias):
    """Returns a storage configuration by alias"""
    from . import config
    storages = config.storages()
    if alias not in storages:
        raise KeyError(f'storage alias "{alias}" not configured')
    return storages[alias]


class Storage:
    """Generic storage connection definition"""

    def __repr__(self) -> str:
        return (f'<{self.__class__.__name__}: '
                + ', '.join([f'{var}={"*****" if (var == "password" or "secret" in var) else getattr(self, var)}'
                             for var in vars(self) if getattr(self, var)])
                + '>')


class LocalStorage(Storage):
    def __init__(self, base_path: pathlib.Path):
        """
        Connection information for a local path data bucket
        """
        self.base_path = base_path


class GoogleCloudStorage(Storage):
    def __init__(self, bucket_name: str, project_id: str = None):
        """
        Connection information for a Google Cloud Storage bucket

        Args:
            bucket_name: name of the GCS bucket
            project_id: Google Cloud project ID for new buckets
        """
        self.bucket_name = bucket_name
        self.project_id = project_id
    
    @property
    def base_uri(self):
        return f'gs://{self.bucket_name}'