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


@ensure_storage.register(storages.GoogleCloudStorage)
def __(storage: storages.GoogleCloudStorage):
    import shlex
    import subprocess

    # command returning 0 when storage exists
    test_exists_command = f'gsutil -q ls {shlex.quote(storage.base_uri)}'

    # command returning 0 when bucket was created
    create_storage_command = ('gsutil mb '
                              + (f'-l {storage.location}' if storage.location else '')
                              + (f'-p {storage.project_id} ' if storage.project_id else '')
                              + shlex.quote(storage.base_uri))

    (exitcode, stdout) = subprocess.getstatusoutput(f'{test_exists_command} || {create_storage_command}')
    if exitcode != 0:
        raise Exception(f'An error occured while creating a GCS bucket. Stdout:\n{stdout}')
    assert exitcode == 0


# -----------------------------------------------------------------------------


@singledispatch
def drop_storage(storage: object, force: bool = False):
    """
    Drops a storage. The storage must be empty.

    Args:
        force: If True, the storage is dropped including its content. If the storage does not
               exist, no action is taken.
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
            raise FileNotFoundError(errno.ENOENT,
                                    os.strerror(errno.ENOENT),
                                    str(storage.base_path.absolute))

        storage.base_path.rmdir()


@drop_storage.register(storages.GoogleCloudStorage)
def __(storage: storages.GoogleCloudStorage, force: bool = False):
    import shlex
    import subprocess

    command = ('gsutil '
               + ('rm -r ' if force else 'rb -f ')
               + shlex.quote(storage.base_uri))

    (exitcode, stdout) = subprocess.getstatusoutput(command)
    if exitcode != 0:
        raise Exception(f'An error occured while dropping a GCS bucket. Stdout:\n{stdout}')
    assert exitcode == 0
