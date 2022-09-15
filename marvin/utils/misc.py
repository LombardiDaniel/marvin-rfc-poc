import os
from .s3_utils import S3Utils

def check_marvin_package(path):
    path = os.path.join(path, '.marvin')
    if os.path.exists(path):
        return True
    return False

def get_project_name(path):
    path = os.path.join(path, '.marvin')
    with open(path, 'r') as f:
        file_cont = f.read().replace('\n', '')
        return file_cont

def filter_tar(tarinfo):
    if 'dependencies' in tarinfo.path:
        return None
    return tarinfo
