'''
Renderer Class, to be used by the MARVIN.ai CLI.
'''

import os
import sys

from jinja2 import Environment, FileSystemLoader
import black
import click

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

    TEMPLATES_DIR = f'{os.path.dirname(os.path.realpath(__file__))}/templates'

    STEP_FUNCTION_SUFFIX = '_step_func'
    STEP_FUNCTION_POINTER_SUFFIX = '_step_pointer_func'
    PIPELINE_FUNCTION_SUFFIX = '_pipe_func'

    def __init__(self, parsed_yaml, uuid_str):
        self.parsed_yaml = parsed_yaml
        self.parsed_yaml['uuid'] = uuid_str

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

        env = Environment(loader=FileSystemLoader(Renderer.TEMPLATES_DIR))
        # helper functions:
        env.globals['make_pipeline_function_name'] = Renderer.make_pipeline_function_name
        env.globals['make_step_function_pointer_name'] = Renderer.make_step_function_pointer_name
        env.globals['make_step_function_name'] = Renderer.make_step_function_name
        env.globals['string_or_var'] = Renderer.string_or_var

        # pipeline_template = Template(template_file)
        pipeline_template = env.get_template("pipeline.py.j2")
        rendered_pipeline = pipeline_template.render(
            pipeline=self.parsed_yaml,
            target_path=target_path
        )

        if auto_format:
            rendered_pipeline = black.format_str(
                rendered_pipeline,
                mode=black.FileMode(line_length=82)
            )
            # try:
            #     rendered_pipeline = black.format_str(
            #         rendered_pipeline,
            #         mode=black.FileMode(line_length=82)
            #     )
            # except Exception:
            #     exc_type, exc_obj, exc_tb = sys.exc_info()
            #     fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            #     click.prompt(exc_type, fname, exc_tb.tb_lineno)

        if target_path is not None:
            with open(target_path, 'w', encoding='UTF-8') as file:
                file.write(rendered_pipeline)

        return rendered_pipeline

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
    def string_or_var(var):
        '''
        Helper function to allow passtrhough of extra/optional parameters for
        kfp run creations. More info on:
            https://kubeflow-pipelines.readthedocs.io/en/latest/source/kfp.client.html#create_run_from_pipeline_package

        Returns either None or str(var).
        '''

        if not isinstance(var, str):
            return var

        return f'"{str(var)}"'

    @staticmethod
    def make_pipeline_function_name(pipeline_name):
        '''
        Helper function to generate the pipeline funcion name to be used in the
        rendered file.
        '''
        return pipeline_name + Renderer.PIPELINE_FUNCTION_SUFFIX

    # @staticmethod
    # def make_tarball_name(yaml_path):
    #     '''
    #     Helper func
    #     '''
    #
    #     orig_name = yaml_path


# TODO: remover isso aqui e criar arquivo de test
if __name__ == '__main__':
    import json
    import uuid

    d = {}
    with open('../examples/housing_prices_pipeline/pipeline.json', 'r', encoding='UTF=8') as f:
        d = json.load(f)

    r = Renderer(d, uuid.uuid4())

    r.render('rendered_file.py', )
