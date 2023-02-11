SFTP
====================

Accessing a SFTP drive.

Installation
------------

Use extras `sftp` to install all required packages.


.. code-block:: shell

    $ pip install mara-storage[sftp]


Configuration examples
----------------------

.. tabs::

    .. group-tab:: User and password login

        .. code-block:: python

            import mara_storage.storages
            mara_storage.config.storages = lambda: {
                'data': mara_storage.storages.SftpStorage(
                    host="<your_sftp_host>",
                    user="<your_login_user>",
                    password="<your_secure_user_password>",

                    # optional:
                    insecure = True  # allow insegure SSL connections and transfers
            }

    .. group-tab:: Private key file

        .. code-block:: python

            import mara_storage.storages
            mara_storage.config.storages = lambda: {
                'data': mara_storage.storages.SftpStorage(
                    host="<your_sftp_host>",
                    user="<your_login_user>",
                    identity_file="~/.ssh/id_rsa",            # path to your private key file
                    public_identity_file="~/.ssh/id_rsa.pub",  # path to your public key file

                    # optional:
                    insecure = True  # allow insegure SSL connections and transfers
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

.. autoclass:: SftpStorage
    :special-members: __init__
    :inherited-members:
    :members:
