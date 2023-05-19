

from src.glacier_backup_tool.GBToolConfig import ConfigInstance

import boto3
import pathlib
import os

import glacier_upload.upload

# for multipart upload:
# https://www.filestack.com/fileschool/python/amazon-s3-multipart-uploads-python-tutorial/
# NOW USING https://github.com/tbumi/glacier-upload/tree/main


class GlacierService:

    def __init__(self, directory: pathlib.Path = None):
        self._dir = directory

        self._cf = ConfigInstance()
        self._vault_name = self._cf.vault_name
        self._region = self._cf.aws_region

        self._glacier_client = boto3.client('glacier', self._region)

        self._arc_desc = None

    # Attempt using the glacier_upload function. Save time over implementing my own.
    def upload_file(self, file_path: pathlib.Path):
        print(f'Vaults: {self._glacier_client.list_vaults()}')

        print(f'File to upload: {file_path}: {os.fspath(file_path)}')

        if self._arc_desc is None:
            self._arc_desc = f'Updated files as of {file_path.name.split(".")[-1]}'

        glacier_upload.upload.upload_archive(self._vault_name,
                                             [os.fspath(file_path)],
                                             #self._region,
                                             self._arc_desc,
                                             part_size_mb=1024,
                                             num_threads=4,
                                             upload_id=None,
                                             region=self._region
                                             )
