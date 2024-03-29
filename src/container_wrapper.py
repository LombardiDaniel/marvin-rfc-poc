'''
Containes a wrapper for dsl.ContainerOp. This should be used instead.
'''

from kfp import dsl, gcp
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
        - export (list) : list of env vars that are convertable to int

    Methods:
        - run(script_to_wrap) : Generates the ContainerOp instance with all needed env vars (
            BUG FIX: Any env var that is capable of being converted to floar/int will be exported
            using bash export command.
        ) and the user script
    '''

    S3_SCRIPT_URL = 'https://raw.githubusercontent.com/LombardiDaniel/marvin-rfc-poc/main/src/s3_utils.py'  # noqa: E501 # pylint: disable=C0301
    UTILS_REQUIREMENTS_URL = 'https://raw.githubusercontent.com/LombardiDaniel/marvin-rfc-poc/main/__S3_UTILS_requirements.txt'  # noqa: E501 # pylint: disable=C0301
    UTILS_REQUIREMENTS_NAME = '__S3_UTILS_requirements.txt'
    SCRIPT_NAME = '__SCRIPT_FOR_S3_IN_CONTAINER.py'

    COMMAND = '/usr/local/bin/python -m pip install --upgrade pip && '
    COMMAND += f'curl {UTILS_REQUIREMENTS_URL} -o {UTILS_REQUIREMENTS_NAME} && '
    COMMAND += f'pip install -r {UTILS_REQUIREMENTS_NAME} && '
    COMMAND += f'curl {S3_SCRIPT_URL} -o {SCRIPT_NAME} && '
    COMMAND += f'python {SCRIPT_NAME} '

    def __init__(self,
                 name='name',
                 image='python:3.7',
                 file_inputs=[],
                 file_outputs=[],
                 setup_command='pip install -r requirements.txt',
                 verbose=False,
                 env_vars={},
                 gpu_spec=None,
                 tpu_spec=None,
                 **kwargs
                 ):

        self.file_inputs = file_inputs
        self.file_outputs = file_outputs
        self.image = image
        self.env_vars = {**env_vars, **kwargs}
        self.export = []
        self.name = name
        self.verbose = verbose
        self.usr_setup = setup_command
        self.gpu_spec = gpu_spec
        self.tpu_spec = tpu_spec

        # We need to explicitly (use `export` bash command) on cases the envVar
        # is convertable to a number. This is to circumvent an error in kfp,
        # thus we use this self.export attribute
        for k, v in self.env_vars.items():
            try:
                float(v)
            except ValueError:
                continue
            else:
                self.export.append(
                    {
                        'key': k,
                        'value': v
                    }
                )

        for item in self.export:
            self.env_vars.pop(item['key'])

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

        export_command = ''
        download_command = ''
        upload_command = ''

        for item in self.export:
            export_command += f'export "{item["key"]}"="{item["value"]}" && '

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

        final_command = export_command
        final_command += download_command
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

        if self.gpu_spec is not None:
            container_op.set_gpu_limit(self.gpu_spec['gpuLimit'])

            if 'label_name' in self.gpu_spec:  # if 'label_name' is in the spec, value is too
                container_op.add_node_selector_constraint(
                    self.gpu_spec['label_name'],
                    self.gpu_spec['value']
                )

        if self.tpu_spec is not None:
            container_op.apply(gcp.use_tpu(
                tpu_cores=self.tpu_spec['tpu_cores'],
                tpu_resource=self.tpu_spec['tpu_resource'],
                tf_version=self.tpu_spec['tf_version']
            ))

        for k, v in self.env_vars.items():
            container_op.container.add_env_variable(
                V1EnvVar(
                    name=k,
                    value=str(v)
                )
            )

        return container_op
