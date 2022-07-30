from kfp import dsl
from kubernetes.client.models import V1EnvVar


class ContainerWrapper:
    '''
    Wrapper for dsl.ContainerOp. Already manages file parsing through pipeline steps.
    '''

    MINIO_SCRIPT_URL = 'https://raw.githubusercontent.com/LombardiDaniel/marvin-rfc-poc/main/minio_utils.py'
    SCRIPT_NAME = '__download_script_for_minio_in_container.py'

    COMMAND = '/usr/local/bin/python -m pip install --upgrade pip'
    COMMAND += 'pip install minio && '
    COMMAND += f'curl {MINIO_SCRIPT_URL} -o {SCRIPT_NAME} && '
    COMMAND += f'python {SCRIPT_NAME} '

    def __init__(self, name='name', image='python:3.7', file_inputs: list = [], file_outputs: list = [], verbose=False, *args, **kwargs):
        self.file_inputs = file_inputs
        self.file_outputs = file_outputs
        self.image = image
        self.env_vars = kwargs
        self.name = name
        self.verbose = verbose

    def push(self):
        pass

    def pop(self):
        pass

    def run(self, script_to_wrap):
        download_command = ''
        upload_command = ''

        if self.file_inputs != []:
            download_command = ContainerWrapper.COMMAND + 'download '
            for file in self.file_inputs:
                download_command += f' {file} '
            download_command += '-v' if self.verbose else ''

        if self.file_outputs != []:
            upload_command = f' && python {ContainerWrapper.SCRIPT_NAME} upload '
            for file in self.file_outputs:
                upload_command += f' {file} '
            upload_command += '-v' if self.verbose else ''

        final_command = download_command
        final_command += script_to_wrap
        final_command += upload_command

        container_op = dsl.ContainerOp(
            name=self.name,
            image=self.image,
            command=[
                '/bin/sh', '-c', final_command
            ]
        )

        for k, v in self.env_vars.items():
            container_op.container.add_env_variable(
                V1EnvVar(
                    name=k,
                    value=v
                )
            )

        return container_op
