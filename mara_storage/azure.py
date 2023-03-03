import datetime

from mara_storage.client import StorageClient
from . import storages

from azure.storage.blob import BlobClient, BlobServiceClient


def init_client(storage: storages.AzureStorage, path: str = None) -> BlobClient:
    client = BlobClient.from_blob_url(storage.build_uri(path))
    return client

def init_service_client(storage: storages.AzureStorage, path: str = None) -> BlobServiceClient:
    client = BlobServiceClient.from_connection_string(storage.connection_string())
    return client


class AzureStorageClient(StorageClient):
    def __init__(self, storage: storages.AzureStorage):
        super().__init__(storage)

        self.__blob_service_client: BlobServiceClient = None
        self.__container_client = None

    @property
    def _blob_service_client(self):
        if not self.__blob_service_client:
            self.__blob_service_client = init_service_client(self._storage)

        return self.__blob_service_client

    @property
    def _container_client(self):
        if not self.__container_client:
            self.__container_client = self._blob_service_client.get_container_client(self._storage.container_name)

        return self.__container_client

    def creation_timestamp(self, path: str) -> datetime.datetime:
        blob_client = self._container_client.get_blob_client(path)
        properties = blob_client.get_blob_properties()

        return properties.creation_time

    def last_modification_timestamp(self, path: str) -> datetime.datetime:
        blob_client = self._container_client.get_blob_client(path)
        properties = blob_client.get_blob_properties()

        return properties.last_modified

    def iterate_files(self, file_pattern: str):
        blobs = self._container_client.list_blobs(name_starts_with=file_pattern)

        for blob in blobs:
            if blob:
                yield blob.name
