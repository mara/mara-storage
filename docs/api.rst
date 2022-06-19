API
===

.. module:: mara_storage

This part of the documentation covers all the interfaces of Mara Storage. For
parts where the package depends on external libraries, we document the most
important right here and provide links to the canonical documentation.


Storages
--------

Provides a generic configuration interface for storages.

.. module:: mara_storage.storages

.. autofunction:: storage


Storage client
--------------

Provides a generic storage client.

.. module:: mara_storage.client

.. autoclass:: StorageClient
    :members:


File compression
----------------

Adds support to compress/uncompress file compressions while
reading or writing (blob) data.

.. module:: mara_storage.compression

.. autoenum:: Compression
    :members:

.. autofunction:: file_extension

.. autofunction:: compressor

.. autofunction:: uncompressor


Shell commands
--------------

Functions to create shell commands to interact with a storage.

.. module:: mara_storage.shell

.. autofunction:: read_file_command

.. autofunction:: write_file_command

.. autofunction:: delete_file_command
