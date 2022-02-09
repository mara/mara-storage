import datetime
import importlib.util
import subprocess
import shlex
import typing as t

from mara_storage import storages
from mara_storage.client import StorageClient


class GoogleCloudStorageClient(StorageClient):
    def __new__(cls, storage: storages.GoogleCloudStorage):
        if storage is None:
            raise ValueError('Parameter storage is required')

        if cls is GoogleCloudStorageClient:
            if importlib.util.find_spec('storage', package='google.cloud'):
                cls = GoogleCloudStorageModuleClient
            else:
                # fallback client using 'gsutil' shell command
                cls = GoogleCloudStorageShellClient
            return cls(storage)
        else:
            return super(GoogleCloudStorageClient, cls).__new__(cls, storage)

    def __init__(self, storage: storages.GoogleCloudStorage):
        super().__init__(storage)


class GoogleCloudStorageModuleClient(GoogleCloudStorageClient):
    def __init__(self, storage: storages.GoogleCloudStorage):
        super().__init__(storage)

        self.__client = None

    @property
    def _client(self):
        import google.oauth2.service_account
        import google.cloud.storage

        if not self.__client:
            if self._storage.service_account_file:
                credentials = google.oauth2.service_account.Credentials.from_service_account_file(self._storage.service_account_file)
            elif self._storage.service_account_info:
                credentials = google.oauth2.service_account.Credentials.from_service_account_info(self._storage.service_account_info)
            else:
                raise AttributeError('Either service_account_file or service_account_info needs to be set')

            self.__client = google.cloud.storage.Client(project=credentials.project_id,
                                                        credentials=credentials)
        return self.__client

    def last_modification_timestamp(self, path: str) -> datetime.datetime:
        bucket = self._client.bucket(self._storage.bucket_name)
        blob = bucket.get_blob(path)

        return blob.updated

    def iterate_files(self, file_pattern: str):
        blobs = self._client.list_blobs(self._storage.bucket_name, prefix=file_pattern)

        for blob in blobs:
            if blob:
                yield blob


class GoogleCloudStorageShellClient(GoogleCloudStorageClient):
    def last_modification_timestamp(self, path: str) -> datetime.datetime:
        command = ('gsutil '
                    + (f'-o Credentials:gs_service_key_file={shlex.quote(self._storage.service_account_file)} ' if self._storage.service_account_file else '')
                    + f"stat {shlex.quote(self._storage.build_uri(path))} | \\\n"
                    + "grep 'Update time:' | \\\n"
                    + "sed 's/Update time://g' | \\\n"
                    + "sed 's/^[ \\t]*//'")
        (exitcode, stdout) = subprocess.getstatusoutput(command)

        if exitcode != 0:
            raise Exception('An error occured while getting the last modification time of a file' +
                            f' in a GCS bucket. Stdout:\n{stdout}')

        # NOTE: There is a known issue that python does not read the timezone when using
        #       datetime.strptime with parameter '%Z'. When the local timezone is different
        #       as the GCS timezone, you might run into issues with this.
        return datetime.datetime.strptime(stdout, '%a, %d %b %Y %H:%M:%S %Z').astimezone()

    def iterate_files(self, file_pattern: str) -> t.Iterator[str]:
        command = ('gsutil '
                   + (f'-o Credentials:gs_service_key_file={shlex.quote(self._storage.service_account_file)} ' if self._storage.service_account_file else '')
                   + f"ls {shlex.quote(self._storage.build_uri(file_pattern))}")
        (exitcode, stdout) = subprocess.getstatusoutput(command)

        if exitcode != 0:
            raise Exception('An error occured while iterating over files in a GCS bucket.' +
                            f' Stdout:\n{stdout}')

        for file in stdout.split('\n'):
            if file:
                yield file
