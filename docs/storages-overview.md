Overview
========

The following storages are supported

| Storage                | Configuration class | 
| ---------------------- | ------------------- | 
| Local bash             | LocalStorage        | 
| [Google Cloud Storage] | GoogleCloudStorage  | 

[Google Cloud Storage]: https://cloud.google.com/storage


Function support matrix
-----------------------

| Configuration class   | Read | Write | Delete | Client |
| --------------------- | ---- | ----- | ------ | ------ |
| LocalStorage          | Yes  | Yes   | Yes    | Yes
| GoogleCloudStorage    | Yes  | Yes   | Yes    | Yes

```{note}
A `Move` operation is not implemented by design. Most of the blob storages do not
support this and it is not a best practice on a data lake to move files from one
place to another.

When you really need to move files, consider copying the file and then deleting
it from its old location.
```
