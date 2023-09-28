import pytest
import subprocess

from mara_storage import storages, info, shell, manage


from .local_config import AZ_STORAGE_ACCOUNT_NAME, AZ_STORAGE_ACCOUNT_KEY, AZ_STORAGE_TYPE, AZ_STORAGE_SAS

TEST_TOUCH_FILE_NAME = 'empty-file.txt'
TEST_FILE_NOT_EXISTS_FILE_NAME = 'file-does-not-exist.txt'
TEST_READ_FILE_NAME = 'read_test.txt'
TEST_WRITE_FILE_NAME = 'write_test.txt'
TEST_DELETE_FILE_NAME = 'delete_test.txt'
TEST_CONTENT = 'THIS IS A TEST CONTENT'


if not AZ_STORAGE_ACCOUNT_NAME:
    pytest.skip("skipping azcopp tests: variable AZ_STORAGE_ACCOUNT_NAME not set in tests/local_config.py", allow_module_level=True)


@pytest.fixture
def storage():
    import random
    container_name = f'mara-storage-test-{random.randint(0, 2147483647)}'

    return storages.AzureStorage(
        account_name=AZ_STORAGE_ACCOUNT_NAME,
        account_key=AZ_STORAGE_ACCOUNT_KEY,
        container_name=container_name,
        sas=AZ_STORAGE_SAS,
        storage_type=AZ_STORAGE_TYPE)

@pytest.fixture(autouse=True)
def test_before_and_after(storage: object):
    assert storage.account_name
    assert isinstance(storage, storages.AzureStorage)

    manage.ensure_storage(storage)
    yield
    manage.drop_storage(storage, force=True)


def test_file_exists(storage: object):
    command = shell.write_file_command(storage, file_name=TEST_TOUCH_FILE_NAME)
    assert command

    # prepare
    (exitcode, _) = subprocess.getstatusoutput(f"echo '' | {command}")
    assert exitcode == 0

    # test
    assert info.file_exists(storage, file_name=TEST_TOUCH_FILE_NAME)
    assert not info.file_exists(storage, file_name=TEST_FILE_NOT_EXISTS_FILE_NAME)


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
