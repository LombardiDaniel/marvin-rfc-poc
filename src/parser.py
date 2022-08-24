'''
Parser to generate JSON/dict from user defined YAML.
'''

from marvin_base import MarvinBase, MarvinDefaults
from utils import Utils


class Parser(MarvinBase):
    '''
    # TODO: ainda nao suporta envfile pra gerar o json_obj
    '''

    @property
    def json(self):
        '''
        Generates the json needed for the Renderer.
        '''

        defaults = MarvinDefaults(self.project_path)

        json_obj = self.yaml

        # Fix dependencies
        for i, file_name in enumerate(json_obj['defaultParams']['dependencies']):
            if isinstance(file_name, str):  # first we set defaults to local
                json_obj['defaultParams']['dependencies'][i] = {
                    file_name: defaults.pipelineFileDependencies
                }

        # then we fix the vars
        for i, item in enumerate(json_obj['defaultParams']['dependencies']):
            json_obj['defaultParams']['dependencies'][i] = Utils.fix_key_values(
                item
            )

        # Fix defaultParams envVars
        for i, item in enumerate(json_obj['defaultParams']['envVars']):
            json_obj['defaultParams']['envVars'][i] = Utils.fix_key_values(
                item
            )

        # Fix pipelineSteps envVars
        for i, step in enumerate(json_obj['pipelineSteps']):
            if 'envVars' in step:
                for j, item in enumerate(step['envVars']):
                    json_obj['pipelineSteps'][i]['envVars'][j] = Utils.fix_key_values(
                        item
                    )

        return json_obj

    def __init__(self, user_defined_yaml, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.yaml = user_defined_yaml

    def check_yaml(self):
        '''
        checks yaml for errors?
        '''


if __name__ == '__main__':
    import yaml
    import json

    y = {}
    with open('../examples/housing_prices_pipeline/pipeline.yaml', 'r', encoding='UTF=8') as f:
        y = yaml.load(f, Loader=yaml.FullLoader)

    p = Parser(project_path='.', user_defined_yaml=y)

    with open('test.json', 'w', encoding='UTF-8') as f:
        f.write(json.dumps(p.json))
