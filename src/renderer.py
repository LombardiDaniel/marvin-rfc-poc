'''
'''
import json
import uuid

import json

import jinja2

from s3_utils import S3Utils


class Renderer:
    '''
    '''

    # esse complete_yaml tenq ser a U (uniao) dos yaml la, fzer tipo:
    # for k, v in steps.items():
    #     if k not in pipeline.keys():
    #         # mais um for k, v aqui dnetro
    #         pipeline[k] = v
    #
    def __init__(self, parsed_yaml):
        self.parsed_yaml = parsed_yaml
        self.parsed_yaml['envVars'] = {}

        # for env_var in parsed_yaml['envVars']:  # special case for global env vars, key contains information
        #     self.parsed_yaml['envVars'][k] = v

        self.parsed_yaml['uuid'] = uuid.uuid4()

    def render(self, target_path=None, upload=False):
        '''
        '''

        # env = jinja2.Environment(
        #     loader=jinja2.PackageLoader('templates'),
        #     autoescape=jinja2.select_autoescape()
        # )
        #
        # pipeline_template = env.get_template('pipeline.py.j2')
        template_file = ''
        with open('templates/pipeline.py.j2', 'r', encoding='UTF-8') as file:
            template_file = file.read()

        pipeline_template = jinja2.Template(template_file)
        rendered_pipeline = pipeline_template.render(
            pipeline=self.parsed_yaml,
            upload=upload
        )

        with open(target_path, 'w', encoding='UTF-8') as file:
            file.write(rendered_pipeline)

        return rendered_pipeline


d = {}
with open('/Users/daniellombardi/Desktop/UFSCar/MARVIN.nosync/marvin-rfc-poc/examples/housing_prices_pipeline/pipeline.json', 'r') as f:
    d = json.load(f)

r = Renderer(d)

r.render('test_renderer.py')
