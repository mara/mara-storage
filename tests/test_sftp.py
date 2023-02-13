import datetime
import pathlib
import pytest
import subprocess

from mara_storage.compression import Compression, compressor, file_extension as compression_file_extension
from mara_storage.client import StorageClient
from mara_storage import storages, info, shell, manage


from .local_config import SFTP_HOST, SFTP_PORT, SFTP_USERNAME, SFTP_PASSWORD, SFTP_INSECURE, SFTP_IDENTITY_FILE, SFTP_PUBLIC_IDENTITY_FILE

TEST_TOUCH_FILE_NAME = 'empty-file.txt'
TEST_FILE_NOT_EXISTS_FILE_NAME = 'file-does-not-exist.txt'
TEST_READ_FILE_NAME = 'read_test.txt'
TEST_WRITE_FILE_NAME = 'write_test.txt'
TEST_CONTENT = 'THIS IS A TEST CONTENT'

if not SFTP_HOST:
    pytest.skip("skipping SFTP tests: variable SFTP_HOST not set in tests/local_config.py", allow_module_level=True)


@pytest.fixture
def storage():
    return storages.SftpStorage(host=SFTP_HOST, port=SFTP_PORT, user=SFTP_USERNAME, password=SFTP_PASSWORD,
                                insecure=SFTP_INSECURE, identity_file=SFTP_IDENTITY_FILE,
                                public_identity_file=SFTP_PUBLIC_IDENTITY_FILE)


@pytest.fixture(autouse=True)
def test_before_and_after(storage: object):
    #manage.ensure_storage(storage)
    yield
    #manage.drop_storage(storage, force=True)


def test_file_exists(storage: object):
    assert isinstance(storage, storages.SftpStorage)

    # prepare
    write_commnand = shell.write_file_command(storage, TEST_TOUCH_FILE_NAME)
    (exitcode, _) = subprocess.getstatusoutput(f"echo '' | {write_commnand}")
    assert exitcode == 0
    assert info.file_exists(storage, TEST_TOUCH_FILE_NAME)

    # test
    assert info.file_exists(storage, file_name=TEST_TOUCH_FILE_NAME)
    assert not info.file_exists(storage, file_name=TEST_FILE_NOT_EXISTS_FILE_NAME)

    # clean up test
    delete_command = shell.delete_file_command(storage, TEST_TOUCH_FILE_NAME)
    (exitcode, _) = subprocess.getstatusoutput(delete_command)
    assert exitcode == 0


def test_read_file_command(storage: object):
    assert isinstance(storage, storages.SftpStorage)

    # prepare
    compressions = [
        Compression.NONE]
    write_commnand = shell.write_file_command(storage, TEST_READ_FILE_NAME)
    (exitcode, _) = subprocess.getstatusoutput(f'echo "{TEST_CONTENT}" | {write_commnand}')
    assert exitcode == 0
    assert info.file_exists(storage, TEST_READ_FILE_NAME)

    for compression in compressions:
        if compression == Compression.NONE:
            continue
        raise NotImplementedError()

    # test
    for compression in compressions:
        print(f'Test compression: {compression}')
        file_extension = compression_file_extension(compression)
        file_extension = f'.{file_extension}' if file_extension else ''
        command = shell.read_file_command(storage, file_name=f'{TEST_READ_FILE_NAME}{file_extension}', compression=compression)
        assert command

        (exitcode, stdout) = subprocess.getstatusoutput(command)
        assert exitcode == 0
        assert stdout == TEST_CONTENT


def test_write_file_command(storage: object):
    assert isinstance(storage, storages.SftpStorage)

    command = shell.write_file_command(storage, file_name=TEST_WRITE_FILE_NAME)
    assert command

    (exitcode, _) = subprocess.getstatusoutput(f'echo "{TEST_CONTENT}" | {command}')
    assert exitcode == 0

    assert info.file_exists(storage, file_name=TEST_WRITE_FILE_NAME)

def test_delete_file_command(storage: object):
    assert isinstance(storage, storages.SftpStorage)

    # prepare
    write_commnand = shell.write_file_command(storage, TEST_TOUCH_FILE_NAME)
    (exitcode, _) = subprocess.getstatusoutput(f"echo '' | {write_commnand}")
    assert exitcode == 0
    assert info.file_exists(storage, TEST_TOUCH_FILE_NAME)

    # test
    command = shell.delete_file_command(storage, file_name=TEST_TOUCH_FILE_NAME)
    assert command

    (exitcode, _) = subprocess.getstatusoutput(command)
    assert exitcode == 0
    assert not info.file_exists(storage, TEST_TOUCH_FILE_NAME)

    # test if force option works as expected
    command = shell.delete_file_command(storage, file_name=TEST_TOUCH_FILE_NAME, force=True)
    assert command

    (exitcode, _) = subprocess.getstatusoutput(command)
    assert exitcode == 0
    assert not info.file_exists(storage, TEST_TOUCH_FILE_NAME)
