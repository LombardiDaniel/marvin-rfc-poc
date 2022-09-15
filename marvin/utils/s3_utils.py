import os
import logging
from minio import Minio
from .storage import Storage 

HASH_SIZE = 16

class S3Utils(Storage):
    def __init__(self,
                 url,
                 access_key,
                 secret_key,
                 project_name='',
                 secure=False,
                 bucket_name=None,
                 bucket_path=''
                 ):
        self.url = url
        self.access_key = access_key
        self.secret_key = secret_key
        self.secure = secure
        self.bucket_name = bucket_name
        self.project_name = project_name
        self.bucket_path = bucket_path

    def download(self, items_list=[]):
        client = Minio(
            self.url,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=self.secure
        )

        # for item in client.list_objects(self.bucket_name, recursive=True):
        for item in items_list:
            item_path = os.path.join(self.bucket_path, item)
            logging.info('Downloading: ', item_path)
            client.fget_object(
                self.bucket_name,
                object_name=item_path,  # path in s3
                file_path=item  # local path to download
            )

    def upload(self, items_list=[]):
        client = Minio(
            self.url,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=self.secure
        )

        for item in items_list:

            logging.info('Uploading: ', item)

            client.fput_object(
                self.bucket_name,
                object_name=os.path.join(self.bucket_path, item),
                file_path=item
            )