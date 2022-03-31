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
def __(alias: str, file_name: str, compression: Compression = Compression.NONE):
    return read_file_command(storages.storage(alias), file_name=file_name, compression=compression)


@read_file_command.register(storages.LocalStorage)
def __(storage: storages.LocalStorage, file_name: str, compression: Compression = Compression.NONE):
    return f'{uncompressor(compression)} '+shlex.quote(str( (storage.base_path / file_name).absolute() ))


@read_file_command.register(storages.GoogleCloudStorage)
def __(storage: storages.GoogleCloudStorage, file_name: str, compression: Compression = Compression.NONE):
    return ('gsutil cat '
            + storage.build_uri(file_name)
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
def __(alias: str, file_name: str, compression: Compression = Compression.NONE):
    return write_file_command(storages.storage(alias), file_name=file_name, compression=compression)


@write_file_command.register(storages.LocalStorage)
def __(storage: storages.LocalStorage, file_name: str, compression: Compression = Compression.NONE):
    if compression not in [Compression.NONE, Compression.ZIP]:
        raise ValueError(f'Only compression NONE and ZIP is supported from storage type "{storage.__class__.__name__}"')

    full_path = (storage.base_path / file_name).absolute()
    if compression == Compression.ZIP:
        # the name which shall be used in the zip file
        if full_path.suffix[1:] == file_extension(compression):
            zip_file_name = full_path.stem
        else:
            zip_file_name = full_path.name

        return f'(zip {shlex.quote(str( full_path ))} - \\\n' \
               + f'     && printf "@ -\\n@={shlex.quote(zip_file_name)}\\n" | zipnote -w {shlex.quote(str( full_path ))})'
    else:
        return 'cat - > ' + shlex.quote(str( full_path ))


@write_file_command.register(storages.GoogleCloudStorage)
def __(storage: storages.GoogleCloudStorage, file_name: str, compression: Compression = Compression.NONE):
    if compression not in [Compression.NONE, Compression.GZIP]:
        raise ValueError(f'Only compression NONE and GZIP is supported from storage type "{storage.__class__.__name__}"')
    return ('gsutil cp '
            + ('-Z ' if compression == Compression.GZIP else '')
            + '- '
            + storage.build_uri(file_name))


# -----------------------------------------------------------------------------


@singledispatch
def delete_file_command(storage: object, file_name: str, force: bool = True) -> str:
    """
    Creates a shell command that deletes a file on a storage

    When the file does not exist, the command should silently end
    without error (exit code 0)

    Args:
        storage: The storage where the file is stored
        file_name: The file name within the storage
        force: If True, the command will silently end without error (exit code 0)
               when the file does not exist

    Returns:
        A shell command string
    """
    raise NotImplementedError(f'Please implement delete_file_command for type "{storage.__class__.__name__}"')


@delete_file_command.register(str)
def __(alias: str, file_name: str, force: bool = True):
    return delete_file_command(storages.storage(alias), file_name=file_name, force=force)


@delete_file_command.register(storages.LocalStorage)
def __(storage: storages.LocalStorage, file_name: str, force: bool = True):
    return ('rm '
            + ('-f ' if force else '')
            + shlex.quote(str( (storage.base_path / file_name).absolute() )))


@delete_file_command.register(storages.GoogleCloudStorage)
def __(storage: storages.GoogleCloudStorage, file_name: str, force: bool = True):
    return ('gsutil rm '
            + ('-f ' if force else '')
            + storage.build_uri(file_name))


# -----------------------------------------------------------------------------


@singledispatch
def move_file_command(storage: object, source_file_name: str, target_file_name: str, force: bool = False) -> str:
    """
    Creates a shell command that moves a file on a storage to another location.

    Args:
        storage: The storage where the file is stored
        source_file_name: The source file name within the storage
        target_file_name: The target file name within the storage
        force: If True, the command will override the target_file_name if it already exist.
               IF False, the shell command will fail when the file already exist.

    Returns:
        A shell command string
    """
    raise NotImplementedError(f'Please implement delete_file_command for type "{storage.__class__.__name__}"')


@move_file_command.register(str)
def __(alias: str, source_file_name: str, target_file_name: str, force: bool = True):
    return move_file_command(storages.storage(alias), source_file_name=source_file_name, target_file_name=target_file_name, force=force)


@move_file_command.register(storages.LocalStorage)
def __(storage: storages.LocalStorage, source_file_name: str, target_file_name: str, force: bool = True):
    source_file_path = str( (storage.base_path / source_file_name).absolute() )
    target_file_path = str( (storage.base_path / target_file_name).absolute() )

    return ((f'[ ! -f {shlex.quote(source_file_path)} ] && ')
            +'mv '
            + ('-f ' if force else '')
            + shlex.quote(source_file_path)
            + ' '
            + shlex.quote(target_file_path))


#@delete_file_command.register(storages.GoogleCloudStorage)
#def __(storage: storages.GoogleCloudStorage, file_name: str, force: bool = True):
#    return ('gsutil -m mv -p '
#            + ('-f ' if force else '')
#            + storage.build_uri(file_name))
