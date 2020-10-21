"""Configuration of storage connections"""
import pathlib
import typing

import mara_storage.storages


def storages() -> {str: mara_storage.storages.Storage}:
    """The list of storage connections to use, by alias"""
    return {}
