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
    def __init__(self, bucket_name: str, project_id: str = None, location: str = None,
        service_account_file: str = None, service_account_info: dict = None):
        """
        Connection information for a Google Cloud Storage bucket

        Args:
            bucket_name: name of the GCS bucket
            project_id: Google Cloud project ID for new buckets
            location: Default geographic location to use when creating buckets
            service_account_file: The name of the private key file provided by Google when creating
                                  a service account. (it's a JSON file).
            service_account_info: The (parsed JSON) content of a service account file (use when you
                                  don't want to provide a `service_account_file`)
        """
        self.bucket_name = bucket_name
        self.project_id = project_id
        self.location = location
        self.service_account_file = service_account_file
        self.service_account_info = service_account_info

    @property
    def base_uri(self):
        """Returns the base URI for the storage bucket"""
        return f'gs://{self.bucket_name}'

    def build_uri(self, path: str):
        """Returns a URI for a path on the storage"""
        return f"{self.base_uri}/{path}"
