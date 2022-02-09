import datetime
import pathlib
import pytest
import subprocess

from mara_storage.compression import Compression, compressor, file_extension as compression_file_extension
from mara_storage import storages, info, shell, manage
from mara_storage.google_cloud_storage import GoogleCloudStorageShellClient


from .local_config import GCS_PROJECT_ID, GCS_SERVICE_ACCOUNT_FILE

TEST_TOUCH_FILE_NAME = 'empty-file.txt'


if not GCS_PROJECT_ID:
    pytest.skip("skipping GCS module client tests: variable GCS_PROJECT_ID not set in tests/local_config.py", allow_module_level=True)


@pytest.fixture
def storage():
    import random
    bucket_name = f'mara_storage_test_{random.randint(0, 2147483647)}'
    return storages.GoogleCloudStorage(bucket_name=bucket_name, project_id=GCS_PROJECT_ID, service_account_file=GCS_SERVICE_ACCOUNT_FILE)


@pytest.fixture(autouse=True)
def test_before_and_after(storage: object):

    assert storage.bucket_name

    manage.ensure_storage(storage)
    yield
    manage.drop_storage(storage, force=True)


def test_last_modification_date(storage: object):
    assert isinstance(storage, storages.GoogleCloudStorage)

    # prepare
    command = f'echo "" | {shell.write_file_command(storage, file_name=TEST_TOUCH_FILE_NAME)}'
    (exitcode, _) = subprocess.getstatusoutput(command)
    assert exitcode == 0
    assert info.file_exists(storage, file_name=TEST_TOUCH_FILE_NAME)

    #test
    storage_client = GoogleCloudStorageShellClient(storage)
    assert storage_client

    last_modification_date = storage_client.last_modification_timestamp(TEST_TOUCH_FILE_NAME)

    assert last_modification_date
    assert isinstance(last_modification_date, datetime.datetime)
    assert last_modification_date.tzinfo

    print(f'last_modification_date={last_modification_date}')
    print(f'last_modification_date.tzinfo={last_modification_date.tzinfo}')
    print(f'datetime.datetime.now().astimezone()={datetime.datetime.now().astimezone()}')

    assert (datetime.datetime.now().astimezone() - last_modification_date).total_seconds() <= 10
