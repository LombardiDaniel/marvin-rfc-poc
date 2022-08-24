'''
Parser to generate JSON/dict from user defined YAML.
'''

import os

from marvin_base import MarvinBase, MarvinDefaults
from utils import Utils


class Parser(MarvinBase):
    '''
    Parser class is responsible to transform the user defined pipeline.yaml file
    into the expected json (in-memory dict obj) to be forwarded to the renderer.

    Attributes:
        - self.json (dict) : forwards the (parsed) yaml.
        - self.yaml (dict) : raw user defined yaml.

    Methods:
        - self.check_yaml() : idk yet (# TODO: fazer esse aqui, busca erros?)
        - self.insert_env_file() : Checks for env files and replaces them in the
            yaml attribute.
        - self.fix_all_key_values(): Wrapper for Utils.fix_key_values() for user
            defined pipelines.
    '''

    @property
    def dict(self):
        '''
        Generates the json needed for the Renderer.
        '''

        return self.yaml

    def __init__(self, user_defined_yaml, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.yaml = user_defined_yaml

        self.fix_all_key_values()

        self.insert_env_file_in_pipe()

    def check_yaml(self):
        '''
        checks yaml for errors?
        '''

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

        env_file_path = os.path.join(self.project_path, self.yaml['defaultParams']['envFile'])
        env_vars_from_file = []
        with open(env_file_path, 'r', encoding='UTF-8') as f:  # pylint: disable=W0621, C0103
            block = f.readline().replace(' ', '').replace('\n', '').split('=', maxsplit=1)
            env_vars_from_file.append({
                'key': block[0],
                'value': block[1]
            })

        defaults = MarvinDefaults(self.project_path)

        for env_var in ctx['envVars']:
            if env_var['key'].startswith(defaults.envVarFromEnvFilePrefix):  # pylint: disable=E1101
                env_var_name_in_file = env_var['key'].split(defaults.envVarFromEnvFilePrefix)[-1]  # pylint: disable=E1101

                # we replace the env var in the yaml from the one present in the env_file
                ctx['envVars']['value'] = env_vars_from_file[env_var_name_in_file]  # noqa: E501 # pylint: disable=C0301

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

        prj_defaults = MarvinDefaults(self.project_path)

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

        # Fix pipelineSteps envVars
        for i, step in enumerate(self.yaml['pipelineSteps']):
            if 'envVars' in step:
                for j, item in enumerate(step['envVars']):
                    self.yaml['pipelineSteps'][i]['envVars'][j] = Utils.fix_key_values(
                        item
                    )


if __name__ == '__main__':
    import yaml
    import json

    y = {}
    with open('../examples/housing_prices_pipeline/pipeline.yaml', 'r', encoding='UTF=8') as file:
        y = yaml.load(file, Loader=yaml.FullLoader)

    p = Parser(project_path='.', user_defined_yaml=y)

    with open('test.json', 'w', encoding='UTF-8') as f:
        f.write(json.dumps(p.dict))
