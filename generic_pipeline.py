'''
Generic pipeline to work as example. Also to later be used to generate jinja template.
'''

import secrets
import os

import kfp
import kfp.components as comp
from kfp import dsl

from container_wrapper import ContainerWrapper as Container
from s3_utils import S3Utils


# - Variables for user project - #
PROJECT_NAME = 'generic_pipeline_housing-prices'

MINIO_ENDPOINT_VAR = 'my_minio_uri.ai'
MINIO_ACCESS_KEY_VAR = 'minio_key'
MINIO_SECRET_KEY_VAR = 'minio_secret'
BUCKET_NAME_VAR = 'my_bucket_name'  # generated using project name and hash from external?


def get_valid_bucket_name():
    '''
    Gets a valid bucket name using hash token.
    '''

    hash = secrets.token_urlsafe(16)
    bucket_name = f"{PROJECT_NAME}_{hash}"

    while client.bucket_exists(bucket_name):
        hash = secrets.token_urlsafe(16)
        bucket_name = f"{PROJECT_NAME}_{hash}"

    return bucket_name


def create_container(**kwargs):
    '''
    Wraps container with env vars, forwards env vars with kwargs.
    '''

    return Container(
        setup_command='pip install -r housing-prices/requirements.txt',
        verbose=True,
        S3_ENDPOINT=MINIO_ENDPOINT_VAR,
        S3_ACCESS_KEY=MINIO_ACCESS_KEY_VAR,
        S3_SECRET_KEY=MINIO_SECRET_KEY_VAR,
        BUCKET_NAME=BUCKET_NAME_VAR,
        **kwargs
    )


def setup_minio_pipeline_dependencies(files=[]):
    '''
    Manually sets up the minio objects for the first container.
    '''

    minio = MinioUtils(
        MINIO_ENDPOINT_VAR,
        MINIO_ACCESS_KEY_VAR,
        MINIO_SECRET_KEY_VAR,
        BUCKET_NAME_VAR,
    )

    minio.upload(files)


# - USER DEFINED PIPELINE - #
def acquisitor():
    # - FIRST PIPELINE STEP MUST BE DIFF. - #
    container = create_container(
        MY_EXTRA_ENV_VAR_FOR_THIS_CONTAINER_ONLY='0123456789',
    )
    container.name = 'acquisitor'

    container.file_inputs = [
        'housing-prices/acquisitor.py',
        'housing-prices/train.csv',
        'housing-prices/test.csv',
        'housing-prices/requirements.txt',
    ]

    # - UPLOADS DEPENDENCIES FOR PIPELINE (FRIST STEP) - #
    # User's computer must be able to access the S3 instance via the network
    setup_minio_pipeline_dependencies(cointainer.file_inputs)

    return container.run('python housing-prices/acquisitor.py')


def data_prep():

    container = create_container()
    container.name = 'data_prep'

    container.file_inputs = [
        'housing-prices/data_prep.py',
        'housing-prices/train.csv',
        'housing-prices/test.csv',
        'housing-prices/requirements.txt',
    ]

    container.file_outputs = [
        'housing-prices/X_train.csv',
        'housing-prices/y_train.csv',
        'housing-prices/X_test.csv',
        'housing-prices/y_test.csv',
    ]

    return container.run('python housing-prices/data_prep.py')


def train_model():

    container = create_container()
    container.name = 'train_model'

    container.file_inputs = [
        'housing-prices/X_train.csv',
        'housing-prices/y_train.csv',
        'housing-prices/X_test.csv',
        'housing-prices/y_test.csv',
        'housing-prices/train_model.py',
        'housing-prices/requirements.txt',
    ]

    container.file_outputs = [
        'housing-prices/regressionTree',
        'housing-prices/regressionLinear',
        'housing-prices/randomForest',
    ]

    return container.run('python housing-prices/train_model.py')  # returns ContainerOp


def evaluate():

    container = create_container()
    container.name = 'evaluate'

    container.file_inputs = [
        'housing-prices/X_train.csv',
        'housing-prices/y_train.csv',
        'housing-prices/X_test.csv',
        'housing-prices/y_test.csv',
        'housing-prices/regressionTree',
        'housing-prices/regressionLinear',
        'housing-prices/randomForest',
        'housing-prices/evaluate.py',
        'housing-prices/requirements.txt',
    ]

    container.file_outputs = [
    ]

    return container.run('python housing-prices/evaluate.py')


@dsl.pipeline(
    name='my_generic_pipeline',
    description='testing minio download from within the container'
)
def my_pipeline_name():

    acquisitor_pipe = acquisitor()

    data_prep_pipe = data_prep()
    data_prep_pipe.after(acquisitor_pipe)

    train_model_pipe = train_model()
    train_model_pipe.after(data_prep_pipe)

    evaluate_pipe = evaluate()
    evaluate_pipe.after(train_model_pipe)


if __name__ == '__main__':

    global BUCKET_NAME_VAR
    BUCKET_NAME_VAR = get_valid_bucket_name()

    kfp.compiler.Compiler().compile(my_pipeline_name, 'housing-prices_testing_WRAPPER.tar.gz')
