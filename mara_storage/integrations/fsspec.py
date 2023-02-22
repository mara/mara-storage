from functools import singledispatch
import fsspec
from fsspec.spec import AbstractFileSystem
from typing import Union
from mara_storage import storages
import pathlib


@singledispatch
def filesystem(storage: Union[str, storages.Storage], **storage_options) -> AbstractFileSystem:
    """
    Returns a fsspec compatible filesystem

    Args:
        db: the storage as alias or class
        **kargs: additional arguments to be passed to the 
    """
    raise NotImplementedError(f'Please implement filesystem for type "{storage.__class__.__name__}"')


@filesystem.register(str)
def __(storage_alias: str, **kargs):
    return filesystem(storages.storage(storage_alias), **kargs)


@filesystem.register(storages.LocalStorage)
def __(storage: storages.LocalStorage, **kargs):
    return fsspec.filesystem('file',
                             root_marker=kargs.pop('root_marker', str(pathlib.Path(storage.base_path).absolute())),
                             **kargs)


@filesystem.register(storages.SftpStorage)
def __(storage: storages.SftpStorage, **kargs):
    return fsspec.filesystem('sftp',
                             host=kargs.pop('host', storage.host),
                             hostname=kargs.pop('hostname', storage.host),
                             port=kargs.pop('port', storage.port or 22),
                             username=kargs.pop('username', storage.user),
                             password=kargs.pop('password', storage.password),
                             key_filename=kargs.pop('key_filename', storage.identity_file),
                             **kargs)


@filesystem.register(storages.GoogleCloudStorage)
def __(storage: storages.GoogleCloudStorage, **kargs):
    return fsspec.filesystem('gcs',
                             project=kargs.pop('project', storage.project_id),
                             default_location=kargs.pop('default_location', storage.location),
                             **kargs)



@singledispatch
def build_path(storage: Union[str, storages.Storage], path: str) -> str:
    """
    Builds a path for fsspec including storage specific information e.g. the
    storage container or bucked which is defined in mara in the Storage class.

    Args:
        storage: the storage as alias or class
        path: the path inside the storage. E.g. `my_table/*.parquet`

    Returns:
        A absolute URI or path to be used inside fsspec. E.g. `my_container/path`
    """
    raise NotImplementedError(f'Please implement build_uri for type "{storage.__class__.__name__}"')


@build_path.register(str)
def __(storage_alias: str, path: str):
    return build_path(storages.storage(storage_alias), path=path)


@build_path.register(storages.LocalStorage)
def __(storage: storages.LocalStorage, path: str):
    return str((pathlib.Path(storage.base_path) / path).absolute())


@build_path.register(storages.GoogleCloudStorage)
def __(storage: storages.GoogleCloudStorage, path: str):
    if not storage.bucket_name:
        raise ValueError(f"Storage {storage.__class__.__name__} must have a buckt name")
    return f'{storage.bucket_name}/{path}'


@build_path.register(storages.SftpStorage)
def __(storage: storages.SftpStorage, path: str):
    return path
