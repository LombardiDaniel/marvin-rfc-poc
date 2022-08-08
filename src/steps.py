from container_wrapper import ContainerWrapper as Container


class MarvinPipelineStep:
    '''
    MarvinPipelineStep is the instance that will create each step/ContainerOp in
    the pipeline. The main "rendering" obj is the self.step_dict, a field containing
    "None" indicates no input has been recieved from the user.

    Attributes:
        - self.yaml (dict) : the dict described in the yaml by the user
        - self.step_dict = {
            'name': None,                   (str) : name of the step
            'image': None,                  (str) : docker image accessible
            'conditionForActivation': None, (str|path) : NOT YET IMPLEMENTED
            'description': None,            (str) : description of the step

            'notebookPath': None,           (str) : path to the notebook for execution
            'scriptPath': None,             (str) : path to the notebook for execution
            'executionEngine': None,        (str) : name of the engine (papermill)
            'entrypoint': None,             (str) : final command used by the container

            'envVars': [],                  (list of dicts) : follows: {'key': envVarName, 'value': envVarValue}
            'fileDependencies': [],         (list of str) : list of str containing file inputs for step
            'fileOutputs': [],              (list of str) : list of str containing file outputs for step
            'varsOutput': [],               (list of str) : NOT YET IMPLEMENTED
        }
        - self.container_op (ContainerOp) : The ContainerOp for this pipeline step.
        - self.setup_command (str) : setup command to be used in container (e.g.: pip install, etc.)

    Methods:
        - self._parse_dict():
        - self.build_entrypoint(): buils the entrypoint key if it was not specified.
    '''

    @property
    def container_op(self):
        '''
        '''

        return Container(
            name=self.name,
            image=self.image,
            file_inputs=self.file_inputs,
            file_outputs=self.file_outputs,
            setup=self.setup_command,
            verbose=False,
        )

    def __init__(self, yaml, setup_command):
        self.yaml = yaml
        self.setup_command = setup_command

        self.step_dict = {
            'name': None,
            'image': None,
            'conditionForActivation': None,
            'description': None,

            'notebookPath': None,
            'scriptPath': None,
            'executionEngine': None,
            'entrypoint': None,

            'envVars': [],
            'fileDependencies': [],
            'fileOutputs': [],
            'varsOutput': []
        }

        for k, v in self.yaml.items():
            self.step_dict['name'] = k

        for k, v in self.yaml[self.step_dict['name']].items():
            if k != 'envVars':
                self.step_dict[k] = v
            else:
                for kk, vv in v:
                    self.step_dict['envVars'] = {
                        'key': kk,
                        'value': vv
                    }

        if self.step_dict['entrypoint'] is None:
            self.build_entrypoint()

        for k, v in self.step_dict.items():
            self.__setattr__(k, v)

    def _parse_dict(self):
        '''
        '''

        self.description = self.step_dict['description']

    def __str__(self, *args, **kwargs):
        print(f"{self.step_dict['name']}:", *args, **kwargs)

        for k, v in self.step_dict:
            if k != 'name':
                print(f"\t{k}: {v}", *args, **kwargs)

        print(*args, **kwargs)

    def build_entrypoint(self):
        '''
        Buidls the default entrypoint based on other params.
        '''
        cmd_ext_dict = {
            'ipynb': 'papermill',
            'py': 'python'
        }
        exec_file_ext = ''
        exec_file_path = ''

        if self.step_dict['executionEngine'] is None:
            if self.step_dict['notebookPath'] is not None:
                exec_file_ext = 'ipynb'
                exec_file_path = self.step_dict['notebookPath']

            elif self.step_dict['scriptPath'] is not None:
                exec_file_ext = self.step_dict['scriptPath'].split('.')[-1]
                exec_file_path = self.step_dict['scriptPath']

            self.step_dict['executionEngine'] = cmd_ext_dict[exec_file_exta]

        self.step_dict['entrypoint'] = self.step_dict['executionEngine'] + " " + self.step_dict['notebookPath']
