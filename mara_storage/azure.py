from azure.storage.blob import BlobClient, BlobServiceClient

from . import storages


def init_client(storage: storages.AzureStorage, path: str = None):
    client = BlobClient.from_blob_url(storage.build_uri(path))
    return client

def init_service_client(storage: storages.AzureStorage, path: str = None):
    client = BlobServiceClient.from_connection_string(storage.connection_string())
    return client
