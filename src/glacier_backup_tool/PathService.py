import pathlib
import os

version = '1.0.0'


class PathService:

    _directory = None
    DEFAULT_DIR = '.gbtool/'

    def __init__(self, directory=None):
        self.set_path(directory)

    @property
    def path(self) -> pathlib.Path:
        return self._directory

    @path.setter
    def path(self, directory: pathlib.Path):
        self.set_path(directory)

    @classmethod
    def set_path(cls, directory: pathlib.Path = None) -> pathlib.Path:
        # If a directory is provided, set it, printing if overwriting an existing value.
        if directory is not None:
            if cls._directory is not None:
                print(f'Replacing directory {cls._directory} with {directory}')
            cls._directory = directory

        # If a directory is not provided, set to default no matter what
        else:
            cls._directory = pathlib.Path(os.path.expanduser('~'), cls.DEFAULT_DIR)

        # Check if need to create the dir
        if not os.path.isdir(cls._directory):
            os.makedirs(cls._directory)

        return cls._directory
