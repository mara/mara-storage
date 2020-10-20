import click
from functools import singledispatch

from mara_storage import storages


@singledispatch
def ensure_storage(storage: object):
    """Creates the storage if it do not exist"""
    raise NotImplementedError(f'Please implement ensure_storage for type "{storage.__class__.__name__}"')    


@ensure_storage.register(str)
def __(alias: str):
    ensure_storage(storages.storage(alias))


@ensure_storage.register(storages.LocalStorage)
def __(storage: storages.LocalStorage):
    storage.base_path.mkdir(parents=True, exist_ok=True)


# -----------------------------------------------------------------------------


@singledispatch
def drop_storage(storage: object, force: bool = False):
    """
    Drops a storage. The storage must be empty.
    
    Args:
        force: If True, the storage is dropped including its content. If the storage does not exist, no action is taken.
    """
    raise NotImplementedError(f'Please implement drop_storage for type "{storage.__class__.__name__}"')    


@drop_storage.register(str)
def __(alias: str, force: bool = False):
    drop_storage(storages.storage(alias), force=force)


@drop_storage.register(storages.LocalStorage)
def __(storage: storages.LocalStorage, force: bool = False):
    if force:
        import shutil
        shutil.rmtree(storage.base_path.absolute())
    else:
        if not storage.base_path.is_dir():
            import errno
            import os
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), str(storage.base_path.absolute))

        storage.base_path.rmdir()