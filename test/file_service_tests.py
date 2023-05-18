import pathlib
import os
import pytest
import time

from src.glacier_backup_tool.GBToolConfig import LastUpdated
from src.glacier_backup_tool.file_service import FileWatcher

# Tests will use test directory so as not to interfere with system config and time store.
test_conf = pathlib.Path(pathlib.Path(__file__).parent, 'resources/test_config.toml')
test_resources_dir = pathlib.Path(pathlib.Path(__file__).parent, 'resources')
# todo: implement second test directory
secondary_resources_dir = pathlib.Path(test_resources_dir.parent, 'rec2')

# These are the expected files
expected_files = [f'{test_resources_dir}/test1.mp4',
                  f'{test_resources_dir}/test2.mov,'
                  f'{test_resources_dir}/recur_test/test4.mov']


@pytest.fixture
def setup():
    """Configure the last updated time. Only a fixture so that we know we have a last updated time placed.
    Use test resources directory so we don't interfere with the system settings
    (this in case we're testing on the system where the util is running)"""
    lu = LastUpdated(test_resources_dir)
    lu.latest_timestamp = time.time()
    return lu


def test_file_filter(setup):
    fw = FileWatcher(test_conf)
    assert fw.find_new_files().sort() == expected_files.sort()


def test_multiple_paths_for_backup(setup):
    # todo: implement test for multiple file paths provided
    pass


def test_zip_file_placement(setup):
    # todo: implement test for zip file creation
    pass


def test_dir_with_deleted_files(setup):
    # todo: implement test for directory with deleted files
    pass


def test_dir_with_deleted_and_new_files(setup):
    # todo: implement test for directory with deleted files that have synced and new files that haven't synced
    pass

