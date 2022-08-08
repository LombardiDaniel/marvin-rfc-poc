'''
Utilizacao:

python s3_utils.py [OPERATION] [ITEMS] -v (optional)

OPERATION : download | upload
ITEMS : list of paths to files seperated by space (' '), for both download and upload
-v : Verbose

Exemplo pra download:

python s3_utils.py download item1.py pastaDoMinio/item2.py texto.txt


Exemplo para upload:

python s3_utils.py upload ./item1.py minhaPasta/item2.py texto.txt
'''

# TODO: Fix bucket name for allowed chars

import secrets
import os
import argparse

from minio import Minio


def log(*args, **kwargs):
    print('[INFO][MinioUtils]::', *args, **kwargs)


HASH_SIZE = 16

class S3Utils:
    '''

    Attributes:
        - project_name (str) : Used to generate bucket_name (if needed)
        - url (str) : S3 URI endpoint
        - access_key (str) : S3 Access Key
        - secret_key (str) : S3 Secret Key
        - secure (bool) : True for https, False for http
        - bucket_name (str) : S3 bucket name (may be generated or passed as argument by jinja2)

    Methods:
        - download(items_list=[], verbose=False) : downloads all objs from items_list to current dir
        - upload(items_list=[], verbose=False) : uploads all objs from items_list to S3 bucket
        - create_bucket(try_new_hash=False) : Creates the bucket, if try_new_hash is enabled, tries generating a new
            hash in the case that the current bucket already exists
    '''

    def __init__(self, url, access_key, secret_key, project_name='', secure=False, bucket_name=None):
        self.project_name = project_name.replace('_', '-')
        self.url = url
        self.access_key = access_key
        self.secret_key = secret_key
        self.secure = secure
        self.bucket_name = bucket_name  # if bucket_name is not None else ''

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
                log('Downloading: ', item)
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

        for item in items_list:
            if verbose:
                log('Uploading: ', item)

            client.fput_object(
                self.bucket_name,
                item,
                item
            )

    def create_bucket(self, try_new_hash=False):
        '''
        Creates the bucket to be used in the project, it should already recieve
        the bucket name with the project hash.
        '''

        client = Minio(
            self.url,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=self.secure
        )

        if try_new_hash:
            hash = secrets.token_hex(int(HASH_SIZE / 2))
            bucket_name_tmp = f"{self.project_name}_{hash}"

            while client.bucket_exists(bucket_name_tmp):
                hash = secrets.token_hex(int(HASH_SIZE / 2))
                bucket_name_tmp = f"{self.project_name}_{hash}"

            self.bucket_name = bucket_name_tmp

        client.make_bucket(self.bucket_name)

        return self.bucket_name


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('op', type=str, choices=['download', 'upload'], help='Operation')
    parser.add_argument('items', nargs='*', default=[], help='Items list')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    # print(args.verbose)
    # print(args.op)
    # print(args.items)

    minio = S3Utils(
        os.getenv('S3_ENDPOINT'),
        os.getenv('S3_ACCESS_KEY'),
        os.getenv('S3_SECRET_KEY'),
        bucket_name=os.getenv('BUCKET_NAME')
    )

    if args.op == 'download':
        minio.download(args.items, verbose=args.verbose)

    elif args.op == 'upload':
        minio.upload(args.items, verbose=args.verbose)


# f"python download_utils.py {DOWNLOAD_ENGINE} download {ARQ}"
