Google Cloud Storage
====================

Accessing a Google Cloud Storage (GCS) with the shell tool `gsutil`.

Installation
------------

You need to install `gsutil`. Take a look at `Install gsutil <https://cloud.google.com/storage/docs/gsutil_install>`_.


Configuration examples
----------------------

.. tabs::

    .. group-tab:: Service account via file

        .. code-block:: python

            import pathlib
            import mara_storage.storages
            mara_storage.config.storages = lambda: {
                'data': mara_storage.storages.GoogleCloudStorage(
                    bucket_name='my-gcs-bucket',
                    project_id='<gcloud-project-id>',
                    service_account_file='service-account.json'),
            }

    .. group-tab:: Service account from raw json

        .. code-block:: python

            import pathlib
            import mara_storage.storages
            mara_storage.config.storages = lambda: {
                'data': mara_storage.storages.GoogleCloudStorage(
                    bucket_name='my-gcs-bucket',
                    project_id='<gcloud-project-id>',
                    service_account_info=
            '''
            {... content of service-account.json }
            '''
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

.. autoclass:: GoogleCloudStorage
    :special-members: __init__
    :inherited-members:
    :members:
