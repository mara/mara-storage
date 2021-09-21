"""Information functions for storage file/directory information"""

from functools import singledispatch

from mara_storage import storages


@singledispatch
def file_exists(storage: object, file_name: str) -> bool:
    """
    Check if a file exists on a storage
    """
    raise NotImplementedError(f'Please implement file_exists for type "{storage.__class__.__name__}"')


@file_exists.register(str)
def __(alias: str, file_name: str):
    return file_exists(storages.storage(alias), file_name=file_name)


@file_exists.register(storages.LocalStorage)
def __(storage: storages.LocalStorage, file_name: str):
    return (storage.base_path.absolute() / file_name).is_file()


@file_exists.register(storages.SftpStorage)
def __(storage: storages.SftpStorage, file_name: str):
    from . import sftp
    with sftp.connection(storage) as sftp:
        return sftp.exists(file_name)


@file_exists.register(storages.GoogleCloudStorage)
def __(storage: storages.GoogleCloudStorage, file_name: str):
    import subprocess
    import shlex

    command = ('gsutil '
               + (f'-o Credentials:gs_service_key_file={shlex.quote(storage.service_account_file)} ' if storage.service_account_file else '')
               + '-q '
               + 'stat '
               + shlex.quote(storage.build_uri(file_name)))

    (exitcode, _) = subprocess.getstatusoutput(command)
    return exitcode == 0


@file_exists.register(storages.AzureStorage)
def __(storage: storages.AzureStorage, file_name: str):
    from . import azure
    client = azure.init_client(storage, path=file_name)
    return client.exists()
