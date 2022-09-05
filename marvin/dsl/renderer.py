import os
from textwrap import indent

from jinja2 import Template
import black
import json

# from s3_utils import S3Utils


class Renderer:
    '''
    Renderer class is responsible for taking in the parsed yaml dict and rendering
    using the jinja2 template.
    Currently the idea is that the generated file will contain all needed functions
    and/or classes needed for future deploy. It will then be called using python
    sys execve, and passing in command line arguments to control what should be done
    (upload pipeline, just compile the pipeline, upload local dependencies to
    cloudStorage etc.)

    Attributes:
        - self.parsed_yaml (dict) : Parsed yaml created from user-defined yaml
        pipeline.

    Methods:
        - self.render() : Renders the pipeline from template file, also formats the
            file (using python black) for better user readability.

        @staticmethods
        - make_step_function_name() : Helper function for renderer function naming.
        - make_step_function_pointer_name() : Helper function for renderer function naming.
        - make_pipeline_function_name() : Helper function for renderer function naming.
    '''

    TEMPLATES_DIR = f'{os.getcwd()}/../templates/lang'

    STEP_FUNCTION_SUFFIX = '_step_func'
    STEP_FUNCTION_POINTER_SUFFIX = '_step_pointer_func'
    PIPELINE_FUNCTION_SUFFIX = '_pipe_func'

    def __init__(self, parsed_yaml, uuid_str):
        self.parsed_yaml = parsed_yaml
        self.parsed_yaml['uuid'] = uuid_str

    @staticmethod
    def make_step_function_name(step_name):
        '''
        Helper function to generate the step funcion name to be used in the
        rendered file.
        '''
        return step_name + Renderer.STEP_FUNCTION_SUFFIX

    @staticmethod
    def make_step_function_pointer_name(step_name):
        '''
        Helper function to generate the step funcion pointer name to be used in
        the rendered file.
        '''
        return step_name + Renderer.STEP_FUNCTION_POINTER_SUFFIX

    @staticmethod
    def make_pipeline_function_name(pipeline_name):
        '''
        Helper function to generate the pipeline funcion name to be used in the
        rendered file.
        '''
        return pipeline_name + Renderer.PIPELINE_FUNCTION_SUFFIX

    def render(self, target_path=None, auto_format=True):
        '''
        Renders the pipeline file. It also containes the needed files for
        uploading needed files to s3 storageBucket.

        Args:
            - target_path (str) : Path used to save the pipelien.py file.
            - auto_format (bool) : if True, will use 'black' python module to
                format the generated file.

        Returns:
            rendererd_pipelinme (str) : contents of the generated python pipeline
                file.
        '''

        # TODO: criar um outro arquivo que importa o q a gnt fez e ele sobe os arquivos pro minio
        # template_file = ''
        # with open('templates/pipeline.py.j2', 'r', encoding='UTF-8') as file:
        #     template_file = file.read()

        # pipeline_template = Template(template_file)
        pipeline_template = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "templates/lang/pipeline.py.j2"
        )
        with open(pipeline_template, 'r') as f:
            template = Template(f.read())
        template.globals['make_pipeline_function_name'] = Renderer.make_pipeline_function_name
        template.globals['make_step_function_pointer_name'] = Renderer.make_step_function_pointer_name
        template.globals['make_step_function_name'] = Renderer.make_step_function_name

        with open('output.yaml', 'w') as f:
            f.write(json.dumps(self.parsed_yaml, indent=4))

        print(self.parsed_yaml['defaultParams']['envVars'])
        rendered_pipeline = template.render(pipeline=self.parsed_yaml)

        with open('output.py', 'w') as f:
            f.write(rendered_pipeline)

        if auto_format:
            rendered_pipeline = black.format_str(
                rendered_pipeline,
                mode=black.FileMode(line_length=82)
            )

        if target_path is not None:
            with open(target_path, 'w', encoding='UTF-8') as file:
                file.write(rendered_pipeline)

        return rendered_pipeline
