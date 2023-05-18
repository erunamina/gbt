from src.glacier_backup_tool.GBToolConfig import ConfigInstance

import boto3
from botocore.exceptions import ClientError
import pathlib
import sys
import json

# for multipart upload:
# https://www.filestack.com/fileschool/python/amazon-s3-multipart-uploads-python-tutorial/


class GlacierService:

    def __init__(self, dir: pathlib.Path = None):
        self._dir = dir
        self._glacier_client = boto3.client('glacier', 'us-west-2')

        self._cf = ConfigInstance()
        self._vault_name = self._cf.vault_name
        self._region = self._cf.aws_region

        self._upload_id = None
        self._file_read_offset = 0
        self._increment = 100000000
        self._range = None

        # todo: figure out how/when to set filesize
        # os.path.getsize(filepath)
        self.filesize = None

    @property
    def upload_id(self):
        if self._upload_id is not None:
            return self._upload_id

    @upload_id.setter
    def upload_id(self, id):
        self._upload_id = id

    @property
    def range(self):
        return f'{self._file_read_offset}-{self._increment + self._file_read_offset}/*'

    def upload_file(self, file_path: pathlib.Path = None):
        if file_path is None:
            print("No file path provided.")
            sys.exit()

        try:
            response = self._glacier_client.initiate_multipart_upload(
                vaultName='string',
                archiveDescription='string',
                partSize='string'
            )

            self._upload_id = self.parse_upload_id(response)

        except ClientError as e:
            print(f'S3 client error: {e}')
            raise e
        print(f's3 upload response: {response.text}')

        try:
            self.send_multipart(file_path)
        except EOFError as e:
            print(f'Returned from upload in error: {e}')
            raise

        return

    def send_multipart(self, file_path):
        with open(file_path, 'rb') as zipfile:
            while zipfile:
                if self._file_read_offset < self.filesize:
                    bt = self.get_next_increment(zipfile)
                    if bt is not None:
                        try:
                            self._glacier_client.upload_multipart_part(
                                vaultName=self._cf.vault_name,
                                uploadId=self._upload_id,
                                range=self.range,
                                body=bt
                                # todo: calculate hash of part and add to request
                            )
                        except ClientError as e:
                            raise e
                return
        raise EOFError(f'Reached end of {file_path} but did not exit upload loop.')

    def get_next_increment(self, file, increment=None):
        if increment is None:
            increment = self._increment
        segment = file.read(increment)
        if segment is not None:
            yield segment
        yield None

    @staticmethod
    def parse_upload_id(resp):
        # todo: verify this syntax
        return resp.json()['upload_id']
