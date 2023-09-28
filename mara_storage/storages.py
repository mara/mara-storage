"""Abstract definition of storage connections"""

import functools
import pathlib


@functools.lru_cache(maxsize=None)
def storage(alias) -> 'Storage':
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


class SftpStorage(Storage):
    def __init__(self, host: str, port: int = None, user: str = None, password: str = None,
        insecure: bool = False, identity_file: str = None, public_identity_file: str = None):
        """
        Connection information for a SFTP server

        Args:
            host: host name
            port: tcp port
            user: username
            password: password
            insecure: if True, the known_hosts file will not be checked
            identity_file: path to a private key file to be used for private/public key
                           authentication
            public_identity_file: path to a public key file to be used for
                                  private/public key authentication
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.insecure = insecure
        self.identity_file = identity_file
        self.public_identity_file = public_identity_file


class GoogleCloudStorage(Storage):
    def __init__(self, bucket_name: str, project_id: str = None, location: str = None,
        service_account_file: str = None, service_account_info: dict = None):
        """
        Connection information for a Google Cloud Storage bucket

        Args:
            bucket_name: name of the GCS bucket
            project_id: Google Cloud project ID for new buckets
            location: Default geographic location to use when creating buckets
            service_account_file: The name of the private key file provided by Google
                                  when creating a service account. (it's a JSON file).
            service_account_info: The (parsed JSON) content of a service account file
                                  (use when you don't want to provide a
                                  `service_account_file`)
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


class AzureStorage(Storage):
    def __init__(self, account_name: str, container_name: str, sas: str = None,
                 storage_type: str = 'blob', account_key: str = None,
                 spa_tenant: str = None, spa_application: str = None, spa_client_secret: str = None):
        """
        Connection information for a Azure sstorage bucket

        Possible authentication methods:
            SAS => "Shared access signature", see https://docs.microsoft.com/en-us/azure/storage/common/storage-sas-overview
            SPA => "Service principal"

        Args:
            account_name: The storage account name
            container_name: The container name within the storage
            storage_type: The storage type. Supports 'blob' or 'dfs'.
            sas: The SAS token
            account_key: The storage account key
            spa_tenant: The service principal tenant id
            spa_application: The service principal application id
            spa_client_secret: The service principal client secret
        """
        if sas is None and account_key is None and spa_client_secret is None:
            raise ValueError('You have to provide either parameter sas, account_key or spa_client_secret for type AzureStorage.')
        self.account_name = account_name
        self.account_key = account_key
        self.container_name = container_name
        self.storage_type = storage_type
        self.sas = (sas[1:] if sas.startswith('?') else sas) if sas else None
        self.spa_tenant = spa_tenant
        self.spa_application = spa_application
        self.spa_client_secret = spa_client_secret

    @property
    def base_uri(self):
        return self.build_base_uri()

    def build_base_uri(self, storage_type: str = None):
        return f'https://{self.account_name}.{storage_type or self.storage_type}.core.windows.net/{self.container_name}'

    def build_uri(self, path: str = None, storage_type: str = None):
        """Returns a URI for a path on the storage"""
        if path and not path.startswith('/'):
            path = '/' + path
        return (f"{self.build_base_uri(storage_type)}{path}"
                + (f'?{self.sas}' if self.sas else ''))

    def connection_string(self):
        # see https://docs.microsoft.com/en-us/azure/storage/common/storage-configure-connection-string
        if self.account_key:
            return f'DefaultEndpointsProtocol=https;AccountName={self.account_name};AccountKey={self.account_key}'
        else:
            return ('DefaultEndpointsProtocol=https'
                    + f';BlobEndpoint=https://{self.account_name}.{self.storage_type}.core.windows.net'
                    + f';SharedAccessSignature={self.sas}')
