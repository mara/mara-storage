Google Cloud Storage
====================

Accessing a Azure Blob Storage (GCS) with the shell tool `azcopy`.

Installation
------------

You need to install `azcopy`. Take a look at `Get started with Azcopy <https://learn.microsoft.com/en-us/azure/storage/common/storage-use-azcopy-v10>`_.


Configuration examples
----------------------

```{note}
Currently some of the functions require a SAS token, and some of the functions
require a account key. It is recommended to provide both a SAS token
and a account key.
```

.. tabs::

    .. group-tab:: SAS token

        .. code-block:: python

            import pathlib
            import mara_storage.storages
            mara_storage.config.storages = lambda: {
                'data': mara_storage.storages.AzureStorage(
                    account_name='account-name',
                    container_name='container-name',
                    sas='sp=racwdlm&st=2022-05-11T10:04:05Z&se=2023-05-11T18:04:05Z&spr=https&sv=2020-08-04&sr=c&sig=u7tqxugyv5MbyrtFdEUp22tnou4wifBoUfIaLDazeRT%3D'),

                    # optional
                    storage_type = 'dfs'  # use a dfs client instead of 'blob' (default value)
            }

    .. group-tab:: Account key

        .. code-block:: python

            import pathlib
            import mara_storage.storages
            mara_storage.config.storages = lambda: {
                'data': mara_storage.storages.AzureStorage(
                    account_name='account-name',
                    container_name='container-name',
                    account_key='<key>',

                    # optional
                    storage_type = 'dfs'  # use a dfs client instead of 'blob' (default value)
                    ),
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

.. autoclass:: AzureStorage
    :special-members: __init__
    :inherited-members:
    :members:
