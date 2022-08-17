'''
Jinja template for pipeline creation.
'''

from datetime import date

import kfp
from kfp import dsl

from container_wrapper import ContainerWrapper as Container
from s3_utils import S3Utils


# - ***Variables for user project*** - #
PROJECT_NAME = 'pipeline_housing_prices'

S3_ENDPOINT_VAR = 'minio_uri'
S3_ACCESS_KEY_VAR = 'minio_key'
S3_SECRET_KEY_VAR = 'minio_secret'
BUCKET_NAME_VAR = S3Utils.replace_invalid_bucket_name_chars('housing_prices')

def create_container(**kwargs):
    '''
    Wraps container with env vars, forwards env vars with kwargs.
    '''

    return Container(
        setup_command='pip install -r requirements.txt',
        verbose=True,
        S3_ENDPOINT=S3_ENDPOINT_VAR,
        S3_ACCESS_KEY=S3_ACCESS_KEY_VAR,
        S3_SECRET_KEY=S3_SECRET_KEY_VAR,
        BUCKET_NAME=BUCKET_NAME_VAR,
        **kwargs
    )


def setup_storage_pipeline_dependencies(files=[]):
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


# - ***USER DEFINED PIPELINE*** - #

# Uploads dependencies -> colocar isso aqui na main
setup_minio_pipeline_dependencies(
    
    'requirements.txt',
    
    'test.csv',
    
    'train.csv',
    
    'acquisitor.py',
    
    'data_prep.py',
    
    'train_model.py',
    
    'evaluate.py',
    
)

# Generate funcions

def acquisitor():
    container = create_container(
    
        MY_ENV_VAR='test_specific_env',
    
    )
    container.name = acquisitor

    container.file_inputs = [
    
        'test.csv',
    
        'train.csv',
    
    ]

    container.file_outputs = [
    
    ]

    return container.run('python acquisitor.py')

def data_prep():
    container = create_container(
    
    )
    container.name = data_prep

    container.file_inputs = [
    
        'test.csv',
    
        'train.csv',
    
    ]

    container.file_outputs = [
    
        'X_train.csv',
    
        'y_train.csv',
    
        'X_test.csv',
    
        'y_test.csv',
    
    ]

    return container.run('python data_prep.py')

def train_model():
    container = create_container(
    
    )
    container.name = train_model

    container.file_inputs = [
    
        'X_train.csv',
    
        'y_train.csv',
    
        'X_test.csv',
    
        'y_test.csv',
    
    ]

    container.file_outputs = [
    
        'regressionTree',
    
        'regressionLinear',
    
        'randomForest',
    
    ]

    return container.run('python train_model.py')

def evaluate():
    container = create_container(
    
    )
    container.name = evaluate

    container.file_inputs = [
    
        'X_train.csv',
    
        'y_train.csv',
    
        'X_test.csv',
    
        'y_test.csv',
    
        'regressionTree',
    
        'regressionLinear',
    
        'randomForest',
    
    ]

    container.file_outputs = [
    
    ]

    return container.run('python evaluate.py')



@dsl.pipeline(
    name='pipeline_housing_prices',
    description='Pipeline for presentation of famous housing_prices problem'
)
def pipeline_housing_prices_func():

    


# falta montar a main certa
if __name__ == '__main__':
    # TODO: colocar algum tipo de if aqui, q usa sys.args, e a gnt passa na hr de compilar, se entrar no if, sobe os arquivos e o pipe, cria a run e bora

    PROJECT_NAME = S3Utils.replace_invalid_bucket_name_chars(PROJECT_NAME)

    # hash = uuid.uuid4()  # o proprio marvin passa o hash pro arquivo final -> template recebe o hash
    # TODO: só entra aqui SE tiver especificado que vai criar run?
    hash = '2e888b26-ca5b-495f-b22a-56a6472bf64b'
    date_str = datetime.now().strftime('%Y-%m-%d')
    BUCKET_PATH = f'{PROJECT_NAME}-{date_str}-{hash}'

    pipeline_file_path = f'{PROJECT_NAME}.yaml'

    

    kfp.compiler.Compiler().compile(pipeline_housing_prices_func, pipeline_file_path)


    