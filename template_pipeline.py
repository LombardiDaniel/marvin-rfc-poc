'''
Generic pipeline to work as example. Also to later be used to generate jinja template.
'''

import kfp
# import kfp.components as comp
from kfp import dsl

from container_wrapper import ContainerWrapper as Container
from s3_utils import S3Utils


# - Variables for user project - #
PROJECT_NAME = 'generic_pipeline_housing-prices'

MINIO_ENDPOINT_VAR = 'my_minio_uri.ai'
MINIO_ACCESS_KEY_VAR = 'minio_key'
MINIO_SECRET_KEY_VAR = 'minio_secret'
BUCKET_NAME_VAR = 'my_bucket_name'  # generated using project name and hash from external?


# TODO: need to calculate all files that need to be uploaded and upload before
# first conainer is generated


def get_valid_bucket_name():
    '''
    Gets a valid bucket name using hash token.
    '''

    return S3Utils(
        MINIO_ENDPOINT_VAR,
        MINIO_ACCESS_KEY_VAR,
        MINIO_SECRET_KEY_VAR,
        project_name=PROJECT_NAME
    ).create_bucket(try_new_hash=True)


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


# - USER DEFINED PIPELINE - #

# Uploads dependencies
setup_minio_pipeline_dependencies(
    {% for file in pipeline.file_dependencies %}
        {{ file }},
    {% endfor %}
)

# Generate funcions
{% for step in pipeline_steps %}
def {{ step.name }}():
    container = create_container(
    {% for env_var in step.local_env_vars %}
        {{ env_var.key }}="{{ env_var.value }}",
    {% endfor %}
    )
    container.name = {{ step.name }}

    container.file_inputs = [
    {% for file in step.file_inputs %}
        {{ file }},
    {% endfor %}
    ]

    container.file_outputs = [
    {% for file in step.file_outputs %}
        {{ file }},
    {% endfor %}
    ]

    return container.run('{{container.entrypoint}}')
{% endfor %}


@dsl.pipeline(
    name='{{ pipeline.name }}',
    description='{{ pipeline.description }}'
)
def {{ pipeline.name }}():

    {% for step in pipeline_steps %}
    {{ step.name }}_step = {{ step.name }}()
    {% if loop.index != 0 %}
    {{ step.name }}_step.after({{ pipeline_steps[loop.index - 1] }})
    {% endif %}
    {% endfor %}


# falta montar a main certa
if __name__ == '__main__':
    global BUCKET_NAME_VAR

    BUCKET_NAME_VAR = get_valid_bucket_name()

    kfp.compiler.Compiler().compile(my_pipeline_name, 'housing-prices_testing_WRAPPER.tar.gz')


    # CERTO
    pipeline_file_path = 'pipelines.yaml' # extract it from your database
    pipeline_name = 'Your Pipeline Name'

    client = kfp.Client()
    pipeline = client.pipeline_uploads.upload_pipeline(pipeline_file_path, name=pipeline_name)
