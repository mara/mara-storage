"""
Shell command generation for
- reading/writing/deleting files in storages via their command line clients
"""

from functools import singledispatch
import shlex

from mara_storage.compression import Compression, uncompressor, file_extension
from mara_storage import storages


@singledispatch
def read_file_command(storage: object, file_name: str, compression: Compression = Compression.NONE) -> str:
    """
    Creates a shell command that reads a file and sends it to stdout

    Args:
        storage: The storage where the file is stored
        file_name: The file name within the storage
        compression: The compression to be used to uncompress the file

    Returns:
        A shell command string
    """
    raise NotImplementedError(f'Please implement read_file_command for type "{storage.__class__.__name__}"')


@read_file_command.register(str)
def __(alias: str, file_name: str, compression: Compression = Compression.NONE) -> str:
    return read_file_command(storages.storage(alias), file_name=file_name, compression=compression)


@read_file_command.register(storages.LocalStorage)
def __(storage: storages.LocalStorage, file_name: str, compression: Compression = Compression.NONE) -> str:
    return f'{uncompressor(compression)} '+shlex.quote(str( (storage.base_path / file_name).absolute() ))


@read_file_command.register(storages.SftpStorage)
def __(storage: storages.SftpStorage, file_name: str, compression: Compression = Compression.NONE):
    if compression not in [Compression.NONE]:
        raise ValueError(f'Only compression NONE is supported from storage type "{storage.__class__.__name__}"')
    return ('curl -s'
            + (' -k' if storage.insecure else '')
            + (f' -u {storage.user}:' if storage.user else '')
            + (f'{storage.password}' if storage.user and storage.password else '')
            + (f' --key {storage.identity_file}' if storage.identity_file else '')
            + (f' --pubkey {storage.public_identity_file}' if storage.public_identity_file else '')
            + f' sftp://{storage.host}'
            + (f':{storage.port}' if storage.port else '')
            + f'/{shlex.quote(file_name)}'
            + (f'\\\n  | {uncompressor(compression)} - ' if compression != Compression.NONE else ''))


@read_file_command.register(storages.GoogleCloudStorage)
def __(storage: storages.GoogleCloudStorage, file_name: str, compression: Compression = Compression.NONE) -> str:
    return ('gsutil '
            + f'-o Credentials:gs_service_key_file={shlex.quote(storage.service_account_file)} '
            + 'cat '
            + shlex.quote(storage.build_uri(file_name))
            + (f'\\\n  | {uncompressor(compression)} - ' if compression != Compression.NONE else ''))


@read_file_command.register(storages.AzureStorage)
def __(storage: storages.AzureStorage, file_name: str, compression: Compression = Compression.NONE):
    if storage.sas:
        return (f'curl -sf {shlex.quote(storage.build_uri(path=file_name))}'
                + (f'\\\n  | {uncompressor(compression)} - ' if compression != Compression.NONE else ''))

    azlogin_env = ('AZCOPY_AUTO_LOGIN_TYPE=SPN '
                   + f'AZCOPY_TENANT_ID="{storage.spa_tenant}" '
                   + f'AZCOPY_SPA_APPLICATION_ID="{storage.spa_application}" '
                   + f'AZCOPY_SPA_CLIENT_SECRET="{storage.spa_client_secret}" '
                   ) if not storage.sas else ''

    return (f'{azlogin_env}azcopy cp '
            + shlex.quote(storage.build_uri(file_name, storage_type='blob'))
            + ' --from-to BlobPipe'
            + (f'\\\n  | {uncompressor(compression)} - ' if compression != Compression.NONE else ''))


# -----------------------------------------------------------------------------


@singledispatch
def write_file_command(storage: object, file_name: str, compression: Compression = Compression.NONE) -> str:
    """
    Creates a shell command that writes a file content from stdin

    Args:
        storage: The storage where the file will be stored
        file_name: The file name within the storage
        compression: The compression to be used to compress the file

    Returns:
        A shell command string
    """
    raise NotImplementedError(f'Please implement write_file_command for type "{storage.__class__.__name__}"')


@write_file_command.register(str)
def __(alias: str, file_name: str, compression: Compression = Compression.NONE) -> str:
    return write_file_command(storages.storage(alias), file_name=file_name, compression=compression)


@write_file_command.register(storages.LocalStorage)
def __(storage: storages.LocalStorage, file_name: str, compression: Compression = Compression.NONE) -> str:
    if compression not in [Compression.NONE, Compression.GZIP, Compression.ZIP]:
        raise ValueError(f'Only compression NONE, GZIP and ZIP is supported from storage type "{storage.__class__.__name__}"')

    full_path = (storage.base_path / file_name).absolute()
    if compression == Compression.GZIP:
        return 'gzip > ' + shlex.quote(str( full_path ))
    elif compression == Compression.ZIP:
        # the name which shall be used in the zip file
        if full_path.suffix[1:] == file_extension(compression):
            zip_file_name = full_path.stem
        else:
            zip_file_name = full_path.name

        return f'(zip {shlex.quote(str( full_path ))} - \\\n' \
               + f'     && printf "@ -\\n@={shlex.quote(zip_file_name)}\\n" | zipnote -w {shlex.quote(str( full_path ))})'
    else:
        return 'cat - > ' + shlex.quote(str( full_path ))


@write_file_command.register(storages.SftpStorage)
def __(storage: storages.LocalStorage, file_name: str, compression: Compression = Compression.NONE):
    if compression not in [Compression.NONE]:
        raise ValueError(f'Only compression NONE is supported from storage type "{storage.__class__.__name__}"')
    return ('curl -s'
            + (' -k' if storage.insecure else '')
            + (f' -u {storage.user}:' if storage.user else '')
            + (f'{storage.password}' if storage.password else '')
            + (f' --key {storage.identity_file}' if storage.identity_file else '')
            + (f' --pubkey {storage.public_identity_file}' if storage.public_identity_file else '')
            + ' -T'
            + ' -' # source
            + f' sftp://{storage.host}' # destination
            + (f':{storage.port}' if storage.port else '')
            + f'/{shlex.quote(file_name)}')


@write_file_command.register(storages.GoogleCloudStorage)
def __(storage: storages.GoogleCloudStorage, file_name: str, compression: Compression = Compression.NONE) -> str:
    if compression not in [Compression.NONE, Compression.GZIP]:
        raise ValueError(f'Only compression NONE and GZIP is supported from storage type "{storage.__class__.__name__}"')
    return ('gsutil '
            + f'-o Credentials:gs_service_key_file={shlex.quote(storage.service_account_file)} '
            + 'cp '
            + ('-Z ' if compression == Compression.GZIP else '')
            + '- '
            + shlex.quote(storage.build_uri(file_name)))


@write_file_command.register(storages.AzureStorage)
def __(storage: storages.AzureStorage, file_name: str, compression: Compression = Compression.NONE):
    if compression not in [Compression.NONE, Compression.GZIP]:
        raise ValueError(f'Only compression NONE and GZIP is supported from storage type "{storage.__class__.__name__}"')

    azlogin_env = ('AZCOPY_AUTO_LOGIN_TYPE=SPN '
                   + f'AZCOPY_TENANT_ID="{storage.spa_tenant}" '
                   + f'AZCOPY_SPA_APPLICATION_ID="{storage.spa_application}" '
                   + f'AZCOPY_SPA_CLIENT_SECRET="{storage.spa_client_secret}" '
                   ) if not storage.sas else ''

    return ((f'gzip \\\n  | ' if compression == Compression.GZIP else '')
            + f'{azlogin_env}azcopy cp '
            + shlex.quote(storage.build_uri(file_name, storage_type='blob'))
            + ' --from-to PipeBlob')


# -----------------------------------------------------------------------------


@singledispatch
def delete_file_command(storage: object, file_name: str, force: bool = True, recursive: bool = False) -> str:
    """
    Creates a shell command that deletes a file on a storage

    When the file does not exist, the command should silently end
    without error (exit code 0)

    Args:
        storage: The storage where the file is stored
        file_name: The file name within the storage
        force: If True, the command will silently end without error (exit code 0)
               when the file does not exist
        recursive: The folder with content will be deleted

    Returns:
        A shell command string
    """
    raise NotImplementedError(f'Please implement delete_file_command for type "{storage.__class__.__name__}"')


@delete_file_command.register(str)
def __(alias: str, file_name: str, force: bool = True, recursive: bool = False) -> str:
    return delete_file_command(storages.storage(alias), file_name=file_name, force=force, recursive=recursive)


@delete_file_command.register(storages.LocalStorage)
def __(storage: storages.LocalStorage, file_name: str, force: bool = True, recursive: bool = False) -> str:
    options = ''
    if force:
        options += 'f'
    if recursive:
        options += 'r'

    return ('rm '
            + (f'-{options} ' if options else '')
            + shlex.quote(str( (storage.base_path / file_name).absolute() )))


@delete_file_command.register(storages.SftpStorage)
def __(storage: storages.SftpStorage, file_name: str, force: bool = True, recursive: bool = False):
    if not force:
        raise ValueError(f'Only force=True is supported from storage type "{storage.__class__.__name__}"')

    return ((f'sshpass -p {storage.password} ' if storage.password else '')
            + 'sftp'
            + (' -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null' if storage.insecure else '')
            + (f' {storage.user}@' if storage.user else '')
            + storage.host
            + (f':{storage.port}' if storage.port else '')
            + (f' -i {storage.identity_file}' if storage.identity_file else '')
            + f' << EOF\nrm '
            + ('-r ' if recursive else '')
            + f'{shlex.quote(file_name)}\nquit\nEOF')


@delete_file_command.register(storages.GoogleCloudStorage)
def __(storage: storages.GoogleCloudStorage, file_name: str, force: bool = True, recursive: bool = False) -> str:
    return ('gsutil '
            + (f'-o Credentials:gs_service_key_file={shlex.quote(storage.service_account_file)} ' if storage.service_account_file else '')
            + 'rm '
            + ('-f ' if force else '')
            + ('-r ' if recursive else '')
            + shlex.quote(storage.build_uri(file_name)))


@delete_file_command.register(storages.AzureStorage)
def __(storage: storages.AzureStorage, file_name: str, force: bool = True, recursive: bool = False):
    if storage.sas and not force and not recursive:
        return (f'curl -sf -X DELETE {shlex.quote(storage.build_uri(path=file_name))}')

    azlogin_env = ('AZCOPY_AUTO_LOGIN_TYPE=SPN '
                   + f'AZCOPY_TENANT_ID="{storage.spa_tenant}" '
                   + f'AZCOPY_SPA_APPLICATION_ID="{storage.spa_application}" '
                   + f'AZCOPY_SPA_CLIENT_SECRET="{storage.spa_client_secret}" '
                   ) if not storage.sas else ''

    return (f'{azlogin_env}azcopy rm '
            + shlex.quote(storage.build_uri(file_name, storage_type='blob'))
            + (' --recursive=true' if recursive else ''))
