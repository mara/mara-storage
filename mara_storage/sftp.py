import pysftp

from mara_storage import storages


def connection(storage: storages.SftpStorage):
    return pysftp.Connection(host=storage.host,
                             port=storage.port if storage.port else 22,
                             username=storage.user,
                             password=storage.password)
