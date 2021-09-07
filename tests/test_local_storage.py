import datetime
import pathlib
import pytest
import subprocess

from mara_storage.compression import Compression, compressor, file_extension as compression_file_extension
from mara_storage.client import StorageClient
from mara_storage import storages, info, shell, manage


TEST_TOUCH_FILE_NAME = 'empty-file.txt'
TEST_FILE_NOT_EXISTS_FILE_NAME = 'file-does-not-exist.txt'
TEST_READ_FILE_NAME = 'read_test.txt'
TEST_WRITE_FILE_NAME = 'write_test.txt'
TEST_CONTENT = 'THIS IS A TEST CONTENT'


@pytest.fixture
def storage():
    return storages.LocalStorage(pathlib.Path('tests/test-storage'))


@pytest.fixture(autouse=True)
def test_before_and_after(storage: object):
    manage.ensure_storage(storage)
    yield
    manage.drop_storage(storage, force=True)


def test_file_exists(storage: object):
    assert isinstance(storage, storages.LocalStorage)

    # prepare
    file_path = storage.base_path / TEST_TOUCH_FILE_NAME
    (exitcode, _) = subprocess.getstatusoutput(f'touch {file_path}')
    assert exitcode == 0
    assert file_path.is_file()

    # test
    assert info.file_exists(storage, file_name=TEST_TOUCH_FILE_NAME)
    assert not info.file_exists(storage, file_name=TEST_FILE_NOT_EXISTS_FILE_NAME)


def test_read_file_command(storage: object):
    assert isinstance(storage, storages.LocalStorage)

    # prepare
    file_path = storage.base_path / TEST_READ_FILE_NAME
    compressions = [
        Compression.NONE,
        Compression.ZIP,
        Compression.GZIP,
        Compression.TAR_GZIP]

    (exitcode, _) = subprocess.getstatusoutput(f'echo "{TEST_CONTENT}" > {file_path}')
    assert exitcode == 0
    assert file_path.is_file()

    for compression in compressions:
        if compression == Compression.NONE:
            continue
        file_extension = compression_file_extension(compression)
        (exitcode, _) = subprocess.getstatusoutput(f'{compressor(compression)} {file_path} > {file_path}.{file_extension}')
        assert exitcode == 0
        assert file_path.is_file()

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
    assert isinstance(storage, storages.LocalStorage)

    # prepare
    file_path = storage.base_path / TEST_WRITE_FILE_NAME
    compressions = [
        Compression.NONE,
        Compression.ZIP]

    assert storage.base_path

    # test
    for compression in compressions:
        print(f'Test compression: {compression}')
        file_extension = compression_file_extension(compression)
        file_extension = f'.{file_extension}' if file_extension else ''
        command = shell.write_file_command(storage, file_name=f'{TEST_WRITE_FILE_NAME}{file_extension}', compression=compression)
        assert command

        (exitcode, _) = subprocess.getstatusoutput(f'echo "{TEST_CONTENT}" | {command}')
        assert exitcode == 0

        assert file_path.is_file()


def test_delete_file_command(storage: object):
    assert isinstance(storage, storages.LocalStorage)

    # prepare
    file_path = storage.base_path / TEST_TOUCH_FILE_NAME
    (exitcode, _) = subprocess.getstatusoutput(f'touch {file_path}')
    assert exitcode == 0
    assert file_path.is_file()

    # test
    command = shell.delete_file_command(storage, file_name=TEST_TOUCH_FILE_NAME)
    assert command

    (exitcode, _) = subprocess.getstatusoutput(command)
    assert exitcode == 0
    assert not file_path.is_file()

    # test if force option works as expected
    command = shell.delete_file_command(storage, file_name=TEST_TOUCH_FILE_NAME, force=True)
    assert command

    (exitcode, _) = subprocess.getstatusoutput(command)
    assert exitcode == 0
    assert not file_path.is_file()


def test_last_modification_date(storage: object):
    assert isinstance(storage, storages.LocalStorage)

    # prepare
    file_path = storage.base_path / TEST_TOUCH_FILE_NAME
    (exitcode, _) = subprocess.getstatusoutput(f'touch {file_path}')
    assert exitcode == 0
    assert file_path.is_file()

    #test
    storage_client = StorageClient(storage)
    assert storage_client
    from mara_storage.local_storage import LocalStorageClient
    assert isinstance(storage_client, LocalStorageClient)

    last_modification_date = storage_client.last_modification_timestamp(TEST_TOUCH_FILE_NAME)
    assert last_modification_date
    assert isinstance(last_modification_date, datetime.datetime)
    assert last_modification_date.tzinfo
    assert (datetime.datetime.now().astimezone() - last_modification_date).total_seconds() <= 1
