"""Abstract definition of storage connections"""

import functools
import pathlib
import urllib.parse


@functools.lru_cache(maxsize=None)
def storage(alias):
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


class HadoopStorage(Storage):
    def __init__(self, name_node_host: str, port: int = None):
        self.name_node_host = name_node_host
        self.port = port
    
    def build_uri(self, file_name: str) -> str:
        return (f'hdfs://{self.name_node_host}'
                + (f':{self.port}' if self.port else '')
                + '/'
                + urllib.parse.quote(file_name))