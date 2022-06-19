Local storage
=============

Accessing a local storage via bash tools.

Installation
------------

There are no special requirements for a local storage.


Configuration examples
----------------------

.. tabs::

    .. group-tab:: Default

        .. code-block:: python

            import pathlib
            import mara_storage.storages
            mara_storage.config.storages = lambda: {
                'data': mara_storage.storages.LocalStorage(
                    path=pathlib.Path('data')),
            }

|

|

API reference
-------------

This section contains database specific API in the module.


Configuration
~~~~~~~~~~~~~

.. module:: mara_storage.storages
    :noindex:

.. autoclass:: LocalStorage
    :special-members: __init__
    :inherited-members:
    :members:
