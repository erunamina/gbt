import pathlib
import os
import shutil
import importlib.resources
from configparser import ConfigParser
import sys
import ast
import time

from src.glacier_backup_tool.PathService import PathService


DEFAULT_CONFIG_NAME = 'gbtool_config.toml'


class GBTool(PathService):
    """
    Manages a config for Glacier Backup Tool. Inherits PathService so that we can configure a default
    path per user. Puts down a default file upon first execution in ~/.gbtool
    """

    def __init__(self, file=None):
        """If a file is provided, it must exist.
        If no file is provided, and none exists, place default config."""
        if file is not None:
            self._config_name = os.path.basename(file)
            super().__init__(file.parent)
            if not os.access(pathlib.Path(self._directory, os.path.basename(file)), os.R_OK):
                print(f'Could not find file {file}')
                sys.exit()

        else:
            self._config_name = DEFAULT_CONFIG_NAME
            super().__init__(file)
            if not os.access(pathlib.Path(self._directory, DEFAULT_CONFIG_NAME), os.R_OK):
                self.place_config()

    @property
    def config_dir(self):
        return self.path

    @property
    def config_file(self):
        if not os.access(pathlib.Path(self._directory, self._config_name), os.R_OK):
            # todo: add checking to log and deal with corruption of existing file
            self.place_config()
        return pathlib.Path(self._directory, self._config_name)

    def place_config(self):
        """If no config exists, place one. Do not call this if a config is passed to __init__()"""
        try:
            src = importlib.resources.files('config')
        except ModuleNotFoundError:
            src = pathlib.Path(pathlib.Path(__file__).parent.parent.parent, 'resources')
        config_name = DEFAULT_CONFIG_NAME
        cfg = src / config_name
        dest = pathlib.Path(self.path, config_name)
        print(f'Placing a default config file at {dest}. If this is your first time using gbtool, '
              f'please view and edit this file to suit your needs.')
        with importlib.resources.as_file(cfg) as default_conf:
            shutil.copy(default_conf, dest)


class ConfigInstance:

    # Config Categories
    MAIN = 'main'
    AWS = 'aws'

    # Param names in config file
    VAULT_NAME_CFG_PARAM = 'vault_name'
    AWS_REGION_CFG_PARAM = 'aws_region'
    EXTENSIONS_CFG_PARAM = 'extensions'
    DIRECTORIES_CFG_PARAM = 'directories'

    def __init__(self, file=None):
        """The config instance. Read config from the file provided.
        If None provided, it is passed, prompting default file to be used or placed if it does not exist.
        """
        self.cf = GBTool(file)
        self.config_file = self.cf.config_file

        self._extensions = None
        self._paths = None
        self._vault_name = None
        self._aws_region = None

        if not os.access(self.cf.config_file, os.R_OK):
            print(f'Could not access the path: {self.cf.path}. Exiting.')
            sys.exit()

        with open(self.cf.config_file, 'r') as config_file:
            config = ConfigParser()
            config.read_file(config_file)

            # Read in file extensions. If none specified, use .*
            if not config.has_option('main', 'extensions'):
                print(f'Config does not specify any extensions. ALL DIRECTORIES WILL BE BACKED UP.')
                self._extensions = '.*'
            else:
                extensions = config.get('main', 'extensions')
                self._extensions = ast.literal_eval(extensions)
                print(f'File extensions to back up from config: {extensions}')

            # Read in directories. Some funny parsing going on. Save a list of pathlib.Path
            if not config.has_option('main', 'directories'):
                print('No directories specified. Using root. ALL FILETYPES WILL BE BACKED UP')
                self._paths = pathlib.Path('/')
            else:
                paths = ast.literal_eval(config.get('main', 'directories'))
                self._paths = [pathlib.Path(item) for item in paths]
                print(f'Directories to back up: {paths}')

            # Read in s3 bucket name
            if not config.has_option('aws', 'vault_name'):
                print('No bucket name specified. Upload will not be successful.')
            else:
                self._vault_name = config.get('aws', 'vault_name')
                print(f'Set bucket to {self._vault_name}')

            # Read in s3 region
            if not config.has_option('aws', 'region'):
                print('No region was specified for AWS. Upload will not be successful.')
            else:
                self._aws_region = config.get('aws', 'region')
                print(f'Set aws region to {self._aws_region}')

    @property
    def directories(self):
        return self._paths

    @property
    def paths(self):
        return self.directories

    @property
    def extensions(self):
        return self._extensions

    @property
    def file_extensions(self):
        return self.extensions

    @property
    def bucket_name(self):
        return self._vault_name

    @property
    def aws_region(self):
        return self._aws_region

    @property
    def vault_name(self):
        return self._vault_name


class LastUpdated(PathService):
    """Stores the last updated time in the config directory.
    Must manually set LastUpdated().latest_timestamp in calling classes to protect integrity.
    LastUpdated().latest_timestamp IS NOT AUTOMATICALLY SET BY SELF AND MUST BE SET BY CALLERS
    """

    LAST_UPDATED_STORE = '.ls_update.dat'

    def __init__(self, path=None):
        # The path can be set for testing so system-level configs don't get overwritten. Else use default.
        if path is not None:
            self._file_path = pathlib.Path(path, self.LAST_UPDATED_STORE)
        else:
            self._file_path = pathlib.Path(os.path.expanduser('~'), '.gbtool', self.LAST_UPDATED_STORE)

        super().__init__()
        if not os.access(pathlib.Path(self._directory, self.LAST_UPDATED_STORE), os.R_OK):
            self.place_file()

    @property
    def latest_timestamp(self):
        return self._read_latest_store()

    @latest_timestamp.setter
    def latest_timestamp(self, tm):
        if tm is None:
            tm = time.time()
        with open(self.file, 'w') as latest_store:
            latest_store.write(str(tm))

    @property
    def dir(self):
        return self._directory

    @property
    def file(self) -> pathlib.Path:
        if not os.access(pathlib.Path(self._directory, self._file_path), os.R_OK):
            self.place_file()
        return pathlib.Path(self._file_path)

    def place_file(self):
        """If no store exists, place one.
        """
        dest = self._file_path
        print(f'Placing a last-updated store at {dest}. Do not change this file manually.')
        with open(self._file_path, 'w') as new_file:
            new_file.write(str(0))

    def _read_latest_store(self) -> float:
        with open (self.file, 'r') as latest_store:
            num = latest_store.readline()
            self._latest_update_time = float(num)
            return self._latest_update_time
