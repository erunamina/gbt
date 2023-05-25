import time

from src.glacier_backup_tool.file_service import FileWatcher
from src.glacier_backup_tool.GBToolConfig import LastUpdated
from src.glacier_backup_tool.GlacierService import GlacierService


def process():
    print('Running LastUpdated')
    lu = LastUpdated()
    print('Running FileWatcher')
    fw = FileWatcher()
    files_for_upload = fw.find_new_files()
    lu.latest_timestamp = time.time()  # todo: possible race condition here if upload fails
    if len(files_for_upload) > 0:
        print(f'Number of files to upload: {len(files_for_upload)}')
        zipped = fw.zip_files(files_for_upload)
        # todo: implement failure handling
        GlacierService().upload_file(zipped)
    else:
        print(f'No new files to upload. Exiting.')


if __name__ == '__main__':
    process()

