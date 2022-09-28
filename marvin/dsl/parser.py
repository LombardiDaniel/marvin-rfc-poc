'''
Parser to generate JSON/dict from user defined YAML.
'''

import os

from marvin_base import MarvinBase, MarvinDefaults
from utils import Utils


class Parser:
    '''
    Parser class is responsible to transform the user defined pipeline.yaml file
    into the expected json (in-memory dict obj) to be forwarded to the renderer.
    Attributes:
        - self.dict (dict) : forwards the (parsed) yaml.
        - self.yaml (dict) : the yaml parsed from the user.
        - self.raw_yaml (dict) : the raw yaml specified from the user.
    Methods:
        - self.check_yaml() : idk yet (# TODO: fazer esse aqui, busca erros?) ~> busca chaves necessárias
        - self.insert_env_file() : Checks for env files and replaces them in the
            yaml attribute.
        - self.fix_all_key_values(): Wrapper for Utils.fix_key_values() for user
            defined pipelines.
        - self.generate_gpu_and_tpu_specs(): Generates the specs used in by the
            ContainerWrapper for performance/resource specifications in containerOp creation.
    '''

    @property
    def dict(self):
        '''
        Generates the json needed for the Renderer.
        '''

        return self.yaml

    def __init__(self, user_defined_yaml, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.raw_yaml = user_defined_yaml
        self.yaml = user_defined_yaml

        self.fix_all_key_values()

        self.insert_env_file_in_pipe()
        self.spread_values_from_default()
        self.generate_gpu_and_tpu_specs()

    def check_yaml(self):
        '''
        checks yaml for errors?
        '''

    def spread_values_from_default(self):
        '''
        Spreads / copies values from 'defaultParams' to 'pipelineSteps'.
        Example: Specified docker image is copied from defaultParams to each pipeline step.
        '''
        self._spread_values('image', overwrite=False)

    def generate_gpu_and_tpu_specs(self):
        '''
        Checks pipeline steps for 'GPUs' and 'TPUs' keys, if they are present, generates
        the appropriate keys to be used in the ContainerWrapper.
        '''

        for i, step in enumerate(self.yaml['pipelineSteps']):
            if 'GPUs' in step:
                self.yaml[i]['gpu_spec'] = {
                    'gpuLimit': step['gpuLimit']
                }

                if 'nodeSelector' in step:
                    for k, v in step['nodeSelector'].items():
                        self.yaml[i]['gpu_obj'].update({
                            'label_name': k,
                            'value': v
                        })

            if 'TPUs' in step:
                self.yaml[i]['tpu_spec'] = self.yaml[i]['TPUs']

    def _spread_values(self, value_key, overwrite=False):
        '''
        Spreads / copies values from 'defaultParams' to 'pipelineSteps'.
        Example: Specified docker image is copied from defaultParams to each pipeline step.
        Args:
            - value_key (str) : key to have its contents copied to every pipeline step.
            - overwrite (bool) : If True will overwrite existing values in pipeline steps.
        '''

        if value_key == 'envVars':
            return

        default_value = None
        for k, v in self.yaml['defaultParams'].items():
            if k == value_key:
                default_value = v

        for i, step in enumerate(self.yaml['pipelineSteps']):
            if overwrite or value_key not in step:
                self.yaml['pipelineSteps'][i][value_key] = default_value

    def insert_env_file_in_pipe(self):
        '''
        [WRAPPER] Checks the pipeline.yaml for envFile directives, then replaces them in
        the in-memory json. NOTE: COMPILED KFP PIPELINE FILE CONTAINS ***ALL*** ENV
        VARS AS PLAIN TEXT (this is a KFP limitation).
        '''

        if 'envFile' in self.yaml['defaultParams']:
            self.yaml['defaultParams'] = self._insert_env_file(self.yaml['defaultParams'])

        for i, step in enumerate(self.yaml['pipelineSteps']):
            if 'envFile' in step:
                self.yaml['pipelineSteps'][i] = self._insert_env_file(step)

    def _insert_env_file(self, ctx):
        '''
        Inserts the envFile in the envVars dict (only for specified ones).
        Args:
            - ctx (dict) : dict where 'envFile' key is found.
        Returns:
            - ctx (dict) : the same context, but with added envVars IN PLAIN TEXT.
        '''

        env_file_path = os.path.join(self.project_dir, self.yaml['defaultParams']['envFile'])
        env_vars_from_file = []
        with open(env_file_path, 'r', encoding='UTF-8') as f:  # pylint: disable=W0621, C0103
            block = f.readline().replace(' ', '').replace('\n', '').split('=', maxsplit=1)
            env_vars_from_file.append({
                'key': block[0],
                'value': block[1]
            })

        defaults = MarvinDefaults(self.project_dir)

        for i, env_var in enumerate(ctx['envVars']):
            if env_var['value'].startswith(defaults.envVarFromEnvFilePrefix):  # pylint: disable=E1101
                env_var_name_in_file = env_var['value'].split(defaults.envVarFromEnvFilePrefix, maxsplit=1)[-1]  # noqa: E501 # pylint: disable=E1101, C0301

                # we replace the env var in the yaml from the one present in the env_file
                for file_env_var in env_vars_from_file:
                    if file_env_var['key'] == env_var_name_in_file:
                        # print(ctx['envVars'][i])
                        ctx['envVars'][i]['value'] = file_env_var['value']

        return ctx

    def fix_all_key_values(self):
        '''
        Fixes all key/values incorrect logic (logic is incorrect because it makes more sense for
        user defined pipeline). Note: ALL DICTS WILL FOLLOW THE MODEL:
            {
                'key': $KEY,
                'value': $VALUE
            }
        '''

        prj_defaults = MarvinDefaults(self.project_dir)

        # Fix dependencies
        for i, file_name in enumerate(self.yaml['defaultParams']['dependencies']):
            if isinstance(file_name, str):  # first we set defaults to local
                self.yaml['defaultParams']['dependencies'][i] = {
                    file_name: prj_defaults.pipelineFileDependencies  # pylint: disable=E1101
                }

        # then we fix the vars
        for i, item in enumerate(self.yaml['defaultParams']['dependencies']):
            self.yaml['defaultParams']['dependencies'][i] = Utils.fix_key_values(
                item
            )

        # Fix defaultParams envVars
        for i, item in enumerate(self.yaml['defaultParams']['envVars']):
            self.yaml['defaultParams']['envVars'][i] = Utils.fix_key_values(
                item
            )

        keys = ['runParams', 'recurringRunParams']
        for key in keys:
            for i, item in enumerate(self.yaml['defaultParams'][key]):
                self.yaml['defaultParams'][key][i] = Utils.fix_key_values(
                    self.yaml['defaultParams'][key][i]
                )

        # Fix pipelineSteps envVars
        for i, step in enumerate(self.yaml['pipelineSteps']):
            if 'envVars' in step:
                for j, item in enumerate(step['envVars']):
                    self.yaml['pipelineSteps'][i]['envVars'][j] = Utils.fix_key_values(
                        item
                    )
