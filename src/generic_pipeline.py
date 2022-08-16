'''
Generic pipeline to work as example. Also to later be used to generate jinja template.
'''

import uuid
from datetime import datetime

import kfp
from kfp import dsl

from container_wrapper import ContainerWrapper as Container
from s3_utils import S3Utils


# - Variables for user project - #
PROJECT_NAME = 'generic_pipeline_housing-prices'

MINIO_ENDPOINT_VAR = 'my_minio_uri.ai'
MINIO_ACCESS_KEY_VAR = 'minio_key'
MINIO_SECRET_KEY_VAR = 'minio_secret'
BUCKET_NAME_VAR = 'my_bucket_name'  # generated using project name and hash from external?
BUCKET_PATH = ''

# TODO: need to calculate all files that need to be uploaded and upload before
# first conainer is generated


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
        BUCKET_PATH=BUCKET_PATH,
        **kwargs
    )


def setup_minio_pipeline_dependencies(files=[]):
    '''
    Manually sets up the minio objects for the first container.
    '''

    minio = S3Utils(
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
    setup_minio_pipeline_dependencies(container.file_inputs)

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
def housing_prices_pipeline():

    acquisitor_step = acquisitor()

    data_prep_step = data_prep()
    data_prep_step.after(acquisitor_step)

    train_model_step = train_model()
    train_model_step.after(data_prep_step)

    evaluate_step = evaluate()
    evaluate_step.after(train_model_step)


if __name__ == '__main__':
    # global BUCKET_NAME_VAR
    # global PROJECT_NAME
    # global BUCKET_PATH

    BUCKET_PATH = S3Utils.replace_invalid_bucket_name_chars(PROJECT_NAME)

    hash = uuid.uuid4()  # o proprio marvin passa o hash pro arquivo final -> template recebe o hash
    date_str = datetime.now().strftime('%Y-%m-%d')
    BUCKET_PATH = f'{PROJECT_NAME}-{date_str}-{hash}'

    pipeline_file_path = f'{PROJECT_NAME}.yaml'

    kfp.compiler.Compiler().compile(housing_prices_pipeline, pipeline_file_path)

    # upload to kfp
    # precisa do client params
    # ver: https://kubeflow-pipelines.readthedocs.io/en/stable/source/kfp.client.html#kfp.Client.create_run_from_pipeline_func
    client = kfp.Client()
    pipeline = client.pipeline_uploads.upload_pipeline(pipeline_file_path, name=BUCKET_NAME_VAR)
    # precisa entrar e clicar "run"


# TODO: colocar algo do .run_after() pra melhorar a ideia
