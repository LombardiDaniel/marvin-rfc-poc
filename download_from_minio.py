import os

from minio import Minio


def download(url, access_key, secret_key, bucket_name, items_list=[], secure=False, verbose=False):
    client = Minio(
        url,
        access_key=access_key,
        secret_key=secret_key,
        secure=secure
    )

    for item in client.list_objects(bucket_name, recursive=True):
        if verbose:
            print('Downloading: ', item.object_name, 'to: ', item.object_name)
        client.fget_object(bucket_name, item.object_name, item.object_name)


if __name__ == '__main__':
    download(
        os.getenv('MINIO_ENDPOINT'),
        os.getenv('MINIO_ACCESS_KEY'),
        os.getenv('MINIO_SECRET_KEY'),
        os.getenv('BUCKET_NAME'),
        os.getenv('ITEMS_LIST').split(',')
    )
