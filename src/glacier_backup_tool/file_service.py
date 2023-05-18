from src.glacier_backup_tool.GBToolConfig import ConfigInstance, LastUpdated
import time
import pathlib
import glob
from zipfile import ZipFile


class FileWatcher:

    def __init__(self, config_file: pathlib.Path = None):
        self.config = ConfigInstance(config_file)

        self._dirs = self.config.directories
        self._exts = [e.split('.')[-1] for e in self.config.extensions]

        self._latest_update_file = LastUpdated()

        self._relevant_files = None

    def find_new_files(self) -> list:
        """Find files in all configured paths that have been created since the
        last update (self._latest_update_file.latest_timestamp, as set
        by filter_files_by_st_ctime())"""
        files = []
        for p in self._dirs:
            print(f'Checking path {p}')
            f = glob.glob(str(p) + '/**/*.*', recursive=True)
            print(f'Found files: {f}')
            files.extend(f)

        relevant_files = [fi for fi in files if str(fi).split('.')[-1] in self._exts]
        print(f'Media files: {relevant_files}')
        ret_val = self.filter_files_by_st_ctime(relevant_files)
        print(f'Media files filtered by last updated time: {ret_val}')
        return ret_val

    def filter_files_by_st_ctime(self, files: list) -> list:
        """Remove files from list that were created before self._latest_update_files.latest_timestamp"""
        temp = []
        for f in files:
            file = pathlib.Path(f)
            print(f'Latest timestamp: {self._latest_update_file.latest_timestamp}')
            print(f'File update time: {file.stat().st_ctime}')
            if file.stat().st_ctime > self._latest_update_file.latest_timestamp:
                temp.append(file)
                print(f'Adding file: {file}')
        print(f'Returning files filtered by last updated timestamp: {temp}')
        return temp

    def zip_files(self, files: list) -> pathlib.Path:
        """Create a zip file, and add all files in the list passed in. Close file before exiting."""
        fn = self.create_zip_file_name()
        zip_obj = ZipFile(fn, 'w')
        for file in files:
            print(f'Adding to zip archive: {file}')
            zip_obj.write(file)

        zip_obj.close()
        return pathlib.Path(self.config.cf.path, fn)

    def create_zip_file_name(self) -> str:
        """Create a file name based on datetime. Format: YYYYMMDDHHMMSS.zip"""
        path = self.config.config_file.parent
        fmt = '%Y%m%d%H%M%S'
        filename = time.strftime(fmt)
        return f'{path}/{filename}.zip'
