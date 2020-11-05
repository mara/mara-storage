import datetime
import importlib.util
import subprocess

from mara_storage import storages
from mara_storage.client import StorageClient


class GoogleCloudStorageClient(StorageClient):
    def __new__(self, storage: storages.GoogleCloudStorage):
        if importlib.util.find_spec('storage', package='google.cloud'):
            return GoogleCloudStorageModuleClient(storage)
        else:
            # fallback client using 'gsutil' module
            return GoogleCloudStorageShellClient(storage)


class GoogleCloudStorageModuleClient(StorageClient):
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

        return blob.updated ## TODO need to test if the type and timezone is right here!

    def iterate_files(self, file_pattern: str):
        blobs = self._client.list_blobs(self._storage.bucket_name, prefix=file_pattern)

        for blob in blobs:
            if blob:
                yield blob


class GoogleCloudStorageShellClient(StorageClient):
    def __init__(self, storage: storages.GoogleCloudStorage):
        super().__init__(storage)


    def last_modification_timestamp(self, path: str) -> datetime.datetime:
        #raise NotImplementedError()
        command = (f"gsutil stat {self._storage.build_uri(path)} | \\\n"
                    + "grep 'Update time:' | \\\n"
                    + "sed 's/Update time://g' | \\\n"
                    + "sed 's/^[ \\t]*//'")
        (exitcode, stdout) = subprocess.getstatusoutput(command)

        if exitcode != 0:
            return None

        # NOTE: There is a known issue that python does not read the timezone when using
        #       datetime.strptime with parameter '%Z'. When the local timezone is different
        #       as the GCS timezone, you might run into issues with this.
        return datetime.datetime.strptime(stdout, '%a, %d %b %Y %H:%M:%S %Z').astimezone()

    def iterate_files(self, file_pattern: str):
        command = (f"gsutil ls {self._storage.build_uri(file_pattern)}")
        (exitcode, stdout) = subprocess.getstatusoutput(command)

        if exitcode != 0:
            return None

        for file in stdout.split('\n'):
            if file:
                yield file
