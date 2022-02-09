import pathlib
import pytest
import subprocess

from mara_storage.compression import Compression, compressor, file_extension as compression_file_extension
from mara_storage import storages, info, shell, manage


from .local_config import GCS_PROJECT_ID, GCS_SERVICE_ACCOUNT_FILE

TEST_READ_FILE_NAME = 'read_test.txt'
TEST_WRITE_FILE_NAME = 'write_test.txt'
TEST_DELETE_FILE_NAME = 'delete_test.txt'
TEST_CONTENT = 'THIS IS A TEST CONTENT'


if not GCS_PROJECT_ID:
    pytest.skip("skipping GCS tests: variable GCS_PROJECT_ID not set in tests/local_config.py", allow_module_level=True)


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


def test_write_file_command(storage: object):
    command = shell.write_file_command(storage, file_name=TEST_WRITE_FILE_NAME)
    assert command

    (exitcode, _) = subprocess.getstatusoutput(f'echo "{TEST_CONTENT}" | {command}')
    assert exitcode == 0

    assert info.file_exists(storage, file_name=TEST_WRITE_FILE_NAME)


def test_read_file_command(storage: object):
    command = shell.write_file_command(storage, file_name=TEST_READ_FILE_NAME)
    assert command

    (exitcode, _) = subprocess.getstatusoutput(f'echo "{TEST_CONTENT}" | {command}')
    assert exitcode == 0
    assert info.file_exists(storage, file_name=TEST_READ_FILE_NAME)

    command = shell.read_file_command(storage, file_name=TEST_READ_FILE_NAME)
    assert command

    (exitcode, stdout) = subprocess.getstatusoutput(command)
    assert exitcode == 0
    assert stdout == TEST_CONTENT


def test_delete_file_command(storage: object):
    command = shell.write_file_command(storage, file_name=TEST_DELETE_FILE_NAME)
    assert command

    (exitcode, _) = subprocess.getstatusoutput(f'echo "{TEST_CONTENT}" | {command}')
    assert exitcode == 0
    assert info.file_exists(storage, file_name=TEST_DELETE_FILE_NAME)

    command = shell.delete_file_command(storage, file_name=TEST_DELETE_FILE_NAME)
    assert command

    (exitcode, _) = subprocess.getstatusoutput(command)
    assert exitcode == 0
    assert not info.file_exists(storage, file_name=TEST_DELETE_FILE_NAME)
