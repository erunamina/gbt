from src.glacier_backup_tool.PathService import PathService
import pytest
import pathlib
import os
import shutil


@pytest.fixture
def config_path_service():
    return PathService()


def test_default_location(config_path_service):
    assert config_path_service.path == pathlib.Path(os.path.expanduser('~'), '.gbtool')


def test_non_default_location():
    cps = PathService(pathlib.Path(os.path.expanduser('~'), 'Documents/.gbtool'))
    assert cps.path == pathlib.Path(os.path.expanduser('~'), 'Documents/.gbtool')
    os.rmdir(pathlib.Path(os.path.expanduser('~'), 'Documents/.gbtool'))


def test_set_path(config_path_service):
    config_path_service.set_path(pathlib.Path(os.path.expanduser('~'), '.testdir'))
    assert config_path_service.path == pathlib.Path(os.path.expanduser('~'), '.testdir')
    os.rmdir(pathlib.Path(os.path.expanduser('~'), '.testdir'))


def test_new_system_with_no_path():
    test_path = pathlib.Path(os.path.expanduser('~'), '.gbtool')
    shutil.rmtree(test_path)
    assert not os.access(test_path, os.R_OK)

    psvc = PathService()
    assert os.access(psvc.path, os.R_OK)
