Mara Storage
============

[![mara-storage](https://github.com/mara/mara-storage/actions/workflows/build.yaml/badge.svg)](https://github.com/mara/mara-storage/actions/workflows/build.yaml)
[![PyPI - License](https://img.shields.io/pypi/l/mara-storage.svg)](https://github.com/mara/mara-storage/blob/master/LICENSE)
[![PyPI version](https://badge.fury.io/py/mara-storage.svg)](https://badge.fury.io/py/mara-storage)
[![Slack Status](https://img.shields.io/badge/slack-join_chat-white.svg?logo=slack&style=social)](https://communityinviter.com/apps/mara-users/public-invite)

Mini package for configuring and accessing multiple storages in a single project. Decouples the use of storages and their configuration by using "aliases" for storages.

The file [mara_storage/storages.py](https://github.com/mara/mara-storage/blob/main/mara_storage/storages.py) contains abstract storage configurations for local disk and cloud storages. The storage connections of a project are configured by overwriting the `storages` function in mara_storage/config.py:

``` python
import pathlib
import mara_storage.config
import mara_storage.storages

## configure storage connections for different aliases
mara_storage.config.storages = lambda: {
    'data': mara_storage.storages.LocalStorage(base_path=pathlib.Path('data')),
    'gcs-bucket-1': mara_storage.storages.GoogleCloudStorage(bucket_name='my_data_lake_bucket_1', project_id='my_awesome_project')
}

## access individual storage configurations with `storages.storage`:
print(mara_storage.storages.storage('data'))
# -> <LocalStorage: base_path=data>
```

This packages gives the possibility to configure, manage and access multile storages in mara.

&nbsp;


## Batch processing: Accessing storages with shell commands

The file [mara_storage/shell.py](https://github.com/mara/mara-storage/blob/main/mara_storage/shell.py) contains functions that create commands for accessing storage files via their command line clients.

For example, the `read_file_command` function creates a shell command that reads a file from a storage and returns its content to stdout:

```python
import mara_storage.shell

file = 'my_domain.com/logs/2020/11/15/nginx.node-1.error.log'

print(mara_storage.shell.read_file_command('data', file_name=file))
# -> cat /mara/data/my_domain.com/logs/2020/11/15/nginx.node-1.error.log

print(mara_storage.shell.read_file_command('gcs-bucket-1', file_name=file))
# -> gsutil cat gs://my_data_lake_bucket_1/my_domain.com/logs/2020/11/15/nginx.node-1.error.log
```

The function `write_file_command` creates a shell command that receives a data on stdin and writes it to the storage:

```python
import mara_storage.shell

command = 'echo "Hello World!"'
command += ' | '
command += mara_storage.shell.write_file_command('data', file_name='hello-world.txt')

print(command)
# -> echo "Hello World!" | cat - > /mara/data/hello-world.txt
```

Finally, `delete_file_command` creates a shell command that deletes a file from the local storage:

```python
import mara_storage.shell

print(mara_storage.shell.delete_file_command('data', file_name='hello-world.txt'))
# -> rm -f /mara/data/hello-world.txt
```

&nbsp;


The following **command line clients** are used to access the various databases:

| Storage | Client binary | Comments |
| --- | --- | --- |
| Local storage | unix shell | Included in standard distributions. |
| SFTP storage | `sftp`, `curl` |  |
| Google Cloud Storage | `gsutil` | From [https://cloud.google.com/storage/docs/gsutil_install](https://cloud.google.com/storage/docs/gsutil_install). |
| Azure Storage | `azcopy`, `curl` | From [https://docs.microsoft.com/en-us/azure/storage/common/storage-use-azcopy-v10](https://docs.microsoft.com/en-us/azure/storage/common/storage-use-azcopy-v10)

&nbsp;


Installation
------------
To use the library directly, use pip:

```bash
pip install mara-storage
```

or

```
pip install git+https://github.com/mara/mara-storage.git
```

## Links

* Documentation: https://mara-storage.readthedocs.io/
* Changes: https://mara-storage.readthedocs.io/en/latest/changes.html
* PyPI Releases: https://pypi.org/project/mara-storage/
* Source Code: https://github.com/mara/mara-storage
* Issue Tracker: https://github.com/mara/mara-storage/issues
