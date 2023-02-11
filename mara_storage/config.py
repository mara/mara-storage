"""Configuration of storage connections"""

import mara_storage.storages
from typing import Dict


def storages() -> Dict[str, mara_storage.storages.Storage]:
    """The list of storage connections to use, by alias"""
    return {}
