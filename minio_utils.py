'''
Utilizacao:

python minio_utils.py [OPERATION] [ITEMS] -v (optional)

OPERATION : download | upload
ITEMS : list of paths to files seperated by space (' ') - for both download and upload
-v : Verbose

Exemplo pra download:

python minio_utils.py download item1.py pastaDoMinio/item2.py texto.txt


Exemplo para upload:

python minio_utils.py upload ./item1.py minhaPasta/item2.py texto.txt
'''

import os
import argparse

from minio import Minio


class MinioUtils:

    def __init__(self, url, access_key, secret_key, bucket_name, secure=False):
        self.url = url
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket_name = bucket_name
        self.secure = secure

    def download(self, items_list=[], verbose=False):
        client = Minio(
            self.url,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=False
        )

        # for item in client.list_objects(self.bucket_name, recursive=True):
        for item in items_list:
            if verbose:
                print('Downloading: ', item)
            client.fget_object(
                self.bucket_name,
                object_name=item,  # path in minio
                file_path=item  # local path to download
            )

    def upload(self, items_list=[], verbose=False):
        client = Minio(
            self.url,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=self.secure
        )

        for item_path in items_list:
            if verbose:
                print('Uploading: ', item_path)

            client.fput_object(
                self.bucket_name,
                item_path,
                item_path
            )


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('op', type=str, choices=['download', 'upload'], help='Operation')
    parser.add_argument('items', nargs='*', default=[], help='Items list')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    # print(args.verbose)
    # print(args.op)
    # print(args.items)

    minio = MinioUtils(
        os.getenv('MINIO_ENDPOINT'),
        os.getenv('MINIO_ACCESS_KEY'),
        os.getenv('MINIO_SECRET_KEY'),
        os.getenv('BUCKET_NAME')
    )

    if args.op == 'download':
        minio.download(args.items, verbose=args.verbose)

    elif args.op == 'upload':
        minio.upload(args.items, verbose=args.verbose)
