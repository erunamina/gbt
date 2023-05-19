

from src.glacier_backup_tool.GBToolConfig import ConfigInstance

import boto3
from botocore.exceptions import ClientError
import pathlib
import sys

import glacier_upload.upload
import json

# for multipart upload:
# https://www.filestack.com/fileschool/python/amazon-s3-multipart-uploads-python-tutorial/
# NOW USING https://github.com/tbumi/glacier-upload/tree/main


class GlacierService:

    def __init__(self, directory: pathlib.Path = None):
        self._dir = directory
        self._glacier_client = boto3.client('glacier', 'us-west-2')

        self._cf = ConfigInstance()
        self._vault_name = self._cf.vault_name
        self._region = self._cf.aws_region

        self._arc_desc = 'temporary placeholder'  # todo: update to include datetimestamp

        self._upload_id = None
        self._file_read_offset = 0
        self._part_size_mb = 100000000
        self._range = None

        # todo: figure out how/when to set filesize; might not need to using glacier-upload
        # os.path.getsize(filepath)
        self.filesize = None

    @property
    def upload_id(self):
        if self._upload_id is not None:
            return self._upload_id

    @upload_id.setter
    def upload_id(self, uid):
        self._upload_id = uid

    @property
    def range(self):
        return f'{self._file_read_offset}-{self._part_size_mb + self._file_read_offset}/*'

    # Attempt using the glacier_upload function. Save time over implementing my own.
    def upload(self, file_path: pathlib.Path):

        glacier_upload.upload.upload_archive(self._vault_name,
                                             file_path.name,
                                             self._arc_desc,
                                             self._part_size_mb,
                                             4,
                                             None)
