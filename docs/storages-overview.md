Overview
========

The following storages are supported

| Storage                   | Configuration class |
| ------------------------- | ------------------- |
| Local bash                | LocalStorage        |
| [Google Cloud Storage]    | GoogleCloudStorage  |
| [Azure Blob Storage]      | AzureStorage        |
| [Azure Data Lake Storage] | AzureStorage        |
| SFTP                      | SftpStorage         |

[Google Cloud Storage]: https://cloud.google.com/storage
[Azure Blob Storage]: https://azure.microsoft.com/en-us/products/storage/blobs
[Azure Data Lake Storage]: https://azure.microsoft.com/en-us/products/storage/data-lake-storage/


Function support matrix
-----------------------

| Configuration class   | Read | Write | Delete | Client |
| --------------------- | ---- | ----- | ------ | ------ |
| LocalStorage          | Yes  | Yes   | Yes    | Yes    |
| GoogleCloudStorage    | Yes  | Yes   | Yes    | Yes    |
| AzureStorage          | Yes  | Yes   | Yes    | Yes    |
| SftpStorage           | Yes  | Yes   | Yes    | No     |

```{note}
A `Move` operation is not implemented by design. Most of the blob storages do not
support this and it is not a best practice on a data lake to move files from one
place to another.

When you really need to move files, consider copying the file and then deleting
it from its old location.
```
