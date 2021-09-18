# Changelog

## 1.0.0

- adding support to write piped data in ZIP compression to local storage
- fix missing extra requirements for Google Cloud Storage

## 0.9.4 (2021-07-10)

- fix ValueError exception was not thrown when compression was used in write_file_command

## 0.9.3 (2020-11-20)

- fix write_file_command when using storage alias

## 0.9.2 (2020-11-11)

- support alias call for `client.StorageClient`, remove `client.init_client`
- fix GCS delete_file_command

## 0.9.1 (2020-11-05)

- add google cloud storage client
- deprecate function `client.init_client`, use class `client.StorageClient` instead

## 0.9.0 (2020-10-28)

- Initial version
