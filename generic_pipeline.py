import os
import kfp
import kfp.components as comp
from kfp import dsl

from container_wrapper import ContainerWrapper as Container

from minio_utils import MinioUtils

MINIO_ENDPOINT_VAR = 'my_minio_uri.ai'
MINIO_ACCESS_KEY_VAR = 'minio_key'
MINIO_SECRET_KEY_VAR = 'minio_secret'
BUCKET_NAME_VAR = 'my_bucket_name'  # generated using project name and hash


def create_container(**kwargs):
    '''
    Wraps container with env vars, forwards env vars with kwargs.
    '''
    return Container(
        setup_command='pip install -r housing-prices/requirements.txt',
        verbose=True,
        MINIO_ENDPOINT=MINIO_ENDPOINT_VAR,
        MINIO_ACCESS_KEY=MINIO_ACCESS_KEY_VAR,
        MINIO_SECRET_KEY=MINIO_SECRET_KEY_VAR,
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
    name='my_pipeline_from_minio',
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
    kfp.compiler.Compiler().compile(my_pipeline_name, 'housing-prices_testing_WRAPPER.tar.gz')
