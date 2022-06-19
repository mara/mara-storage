Testing framework
=================

Multiple functions have been added to be able to test a storage. These functions might change or be removed in the future
and should (`RFC2119`_) not be used.

.. _RFC2119: https://datatracker.ietf.org/doc/html/rfc2119


Managing storages
-----------------

.. module:: mara_storage.manage

.. autofunction:: ensure_storage

.. autofunction:: drop_storage


Blob and file info
------------------

.. module:: mara_storage.info

.. autofunction:: file_exists
