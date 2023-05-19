

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

    # def upload_file(self, file_path: pathlib.Path = None):
    #     if file_path is None:
    #         print("No file path provided.")
    #         sys.exit()
    #
    #     try:
    #         response = self._glacier_client.initiate_multipart_upload(
    #             vaultName='string',
    #             archiveDescription='string',
    #             partSize='string'
    #         )
    #
    #         self._upload_id = self.parse_upload_id(response)
    #
    #     except ClientError as e:
    #         print(f'S3 client error: {e}')
    #         raise e
    #     print(f's3 upload response: {response.text}')
    #
    #     try:
    #         self.send_multipart(file_path)
    #     except EOFError as e:
    #         print(f'Returned from upload in error: {e}')
    #         raise
    #
    #     return

    # def send_multipart(self, file_path):
    #     with open(file_path, 'rb') as zipfile:
    #         while zipfile:
    #             if self._file_read_offset < self.filesize:
    #                 bt = self.get_next_increment(zipfile)
    #                 if bt is not None:
    #                     try:
    #                         self._glacier_client.upload_multipart_part(
    #                             vaultName=self._cf.vault_name,
    #                             uploadId=self._upload_id,
    #                             range=self.range,
    #                             body=bt
    #                             # todo: calculate hash of part and add to request
    #                         )
    #                     except ClientError as e:
    #                         raise e
    #             return
    #     raise EOFError(f'Reached end of {file_path} but did not exit upload loop.')
    #
    # def get_next_increment(self, file, increment=None):
    #     if increment is None:
    #         increment = self._part_size_mb
    #     segment = file.read(increment)
    #     if segment is not None:
    #         yield segment
    #     yield None

    # @staticmethod
    # def parse_upload_id(resp):
    #     # todo: verify this syntax
    #     return resp.json()['upload_id']

    # def initiate_multipart(self) -> str:
    #     try:
    #         response = self._glacier_client.initiate_multipart_upload(
    #             vaultName=self._vault_name,
    #             archiveDescription=self._arc_desc,
    #             partSize=self._part_size_mb
    #         )
    #
    #     except ClientError as e:
    #         print(f'S3 client error: {e}')
    #         raise e
    #
    #     try:
    #         self._upload_id = self.parse_upload_id(response)
    #     except json.
    #     return self._upload_id
