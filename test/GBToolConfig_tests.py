from src.glacier_backup_tool.GBToolConfig import GBTool
from src.glacier_backup_tool.GBToolConfig import ConfigInstance
from src.glacier_backup_tool.GBToolConfig import LastUpdated
import pytest
import pathlib
import os
import time

test_conf = pathlib.Path(pathlib.Path(__file__).parent, 'resources/test_config.toml')


@pytest.fixture
def default_sut():
    """Default GBTool with default config"""
    return GBTool()


@pytest.fixture
def nd_sut():
    """GBTool with a non-default config. Different values.
    These should be used for test."""
    return GBTool(test_conf)


@pytest.fixture()
def test_vals_conf():
    """Instance of Config class with the test config file passed in."""
    return ConfigInstance(test_conf)


@pytest.fixture()
def last_updated():
    return LastUpdated()


def test_default_config_path(default_sut):
    assert default_sut.config_dir == pathlib.Path(os.path.expanduser('~'), '.gbtool')


def test_default_config_file_placed(default_sut):
    assert os.access(default_sut.config_file, os.R_OK)


def test_non_default_config_path(nd_sut):
    assert nd_sut.path == test_conf.parent


def test_non_default_config_file(nd_sut):
    assert nd_sut.config_file.name == 'test_config.toml'


def test_test_config_extensions(test_vals_conf):
    assert test_vals_conf.extensions == ['.m4v', '.mov', ]


def test_test_config_directories(test_vals_conf):
    assert pathlib.Path('/Users/dan/PycharmProjects/glacier_backup_tool/test/resources') in test_vals_conf.directories


def test_last_updated(last_updated):
    assert last_updated.file == pathlib.Path(os.path.expanduser('~'), '.gbtool', '.ls_update.dat')
    assert os.access(pathlib.Path(os.path.expanduser('~'), '.gbtool', '.ls_update.dat'), os.R_OK)


def test_update_latest_store():
    sut = LastUpdated()
    sut.latest_timestamp = time.time()
    first_time = sut.latest_timestamp

    sut.latest_timestamp = time.time()
    assert sut.latest_timestamp > first_time


def test_last_updated_non_default_path():
    # Be sure non-default path is used if provided
    pass
