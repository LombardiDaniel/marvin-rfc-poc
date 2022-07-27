import os

from minio import Minio


def upload(url, access_key, secret_key, bucket_name, upload_path, items_list=[], secure=False, verbose=False):
    client = Minio(
        url,
        access_key=access_key,
        secret_key=secret_key,
        secure=secure
    )

    for item in items_list:
        client.fput_object(bucket_name, upload_path + item.split('/')[-1], item)


if __name__ == '__main__':
    upload(
        os.getenv('MINIO_ENDPOINT'),
        os.getenv('MINIO_ACCESS_KEY'),
        os.getenv('MINIO_SECRET_KEY'),
        os.getenv('BUCKET_NAME'),
        os.getenv('UPLOAD_PATH'),
        os.getenv('ITEMS_LIST').split(',')
    )
