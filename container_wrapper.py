from kfp import dsl
from kubernetes.client.models import V1EnvVar


class ContainerWrapper:
    '''
    Wrapper for dsl.ContainerOp. Already manages file parsing through pipeline steps.

    Attributes:
        - name (str) : Component name used in the ContainerOp creation
        - file_inputs (list) : files that the container will download before running user's command
        - file_outputs (list) : files that the container will upload after running user's command
        - image (str) : accesible docker image URI to be used in the container
        - env_vars (list) : enviornment variables to be safely passed to the container
        - verbose (bool) : if True will announce steps in stdout
        - usr_setup (str) : setup command defined by the user
    '''

    MINIO_SCRIPT_URL = 'https://raw.githubusercontent.com/LombardiDaniel/marvin-rfc-poc/main/minio_utils.py'
    SCRIPT_NAME = '__script_for_minio_in_container.py'

    COMMAND = '/usr/local/bin/python -m pip install --upgrade pip'
    COMMAND += 'pip install minio && '
    COMMAND += f'curl {MINIO_SCRIPT_URL} -o {SCRIPT_NAME} && '
    COMMAND += f'python {SCRIPT_NAME} '

    # @property
    # def setup_command(self):
    #     '''
    #     Setup command will run on every container (eg: 'pip install -r requirements.txt')
    #     or wtvr else is specified by the user.
    #     '''
    #     setup_command = ContainerWrapper.COMMAND + self.usr_setup + ' && '
    #     return setup_command

    def __init__(self,
                 name='name',
                 image='python:3.7',
                 file_inputs=[],
                 file_outputs=[],
                 setup_command='pip install -r requirements.txt',
                 verbose=False,
                 *args,
                 **kwargs
                 ):
        self.file_inputs = file_inputs
        self.file_outputs = file_outputs
        self.image = image
        self.env_vars = kwargs
        self.name = name
        self.verbose = verbose
        self.usr_setup = setup_command

    def run(self, script_to_wrap):
        '''
        Creates the ContainerOp will all enviornment variables set by the user in the
        __init__ method, all files scripted to be automatically downloaded and uploaded
        by the pipeline steps:
            setup -> download_files -> run_user_script -> upload_files
        (files are managed via min.io/Amazon S3)

        Args:
            - script_to_wrap (str) : user's sript to run in the container (e.g.:
            "python main.py > my_ouput_file.txt")
        '''

        download_command = ''
        upload_command = ''

        if self.file_inputs != []:
            download_command = ContainerWrapper.COMMAND + 'download '
            for file in self.file_inputs:
                download_command += f' {file} '
            download_command += '-v && ' if self.verbose else ' && '

        if self.file_outputs != []:
            upload_command = f' && python {ContainerWrapper.SCRIPT_NAME} upload '
            for file in self.file_outputs:
                upload_command += f' {file} '
            upload_command += '-v' if self.verbose else ''

        final_command = download_command
        final_command += self.usr_setup + (' && ' if self.usr_setup != '' else ' ')
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
