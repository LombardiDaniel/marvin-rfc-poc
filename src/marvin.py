'''
'''

import os
import json
import subprocess
from uuid import uuid4

import click
import yaml

from marvin_base import MarvinBase, MarvinDefaults
from renderer import Renderer
from parser import Parser
from utils import Utils, BColors

from errors import MarvinTemplateNotFoundError


MARVIN_PATH = os.getenv('MARVIN_PATH', '~/usr/bin/marvin')
USR_TEMPLATES_DIR = os.path.join(MARVIN_PATH, 'project_templates')
MARVIN_TEMPLATE_OPTIONS = os.listdir(USR_TEMPLATES_DIR)


class Marvin(MarvinBase):
    '''
    Abstraction/Class to be used by the CLI

    Attributes:
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)

        self.default = MarvinDefaults()
        # self.uuid = uuid4() if uuid is None else uuid
        self.pipeline_py = None

    def init_project(self, template, project_name, force_overwrite):
        '''
        Initializes the project, will use cookiecutter in the future, as of now
        simply copies the '.marvin' file into the project dir and populates base
        fields.
        '''
        template_src = os.path.join(USR_TEMPLATES_DIR, template)

        # lst = [item for item in os.listdir(USR_TEMPLATES_DIR) if os.path.isdir(item)]

        if template not in os.listdir(USR_TEMPLATES_DIR):
            raise MarvinTemplateNotFoundError(
                f'Template "{template}" not in "{USR_TEMPLATES_DIR}".'
            )

        Utils.copy_dir_from_template(template_src, self.project_dir, force_overwrite)

        self.setup_marvin_base_file(project_name)


    def _render_pipeline(self, usr_yaml, verbose, debug, *args, **kwargs):
        '''
        Also sets self.pipeline_py attribute.
        Loads and compiles the user defined pipline.
        # NOTE: does NOT support imports atm
        # NOTE: Compiling a new pipeline will generate a new hash/uuid to be used in
        future commands in same pipeline. If you re-compile it, marvin will assume
        that the pipeline has changed. Thus it needs a new hash as to not interfere
        with old storage buckets.

        Args:
            - verbose (bool) : if true will print out verbose/progress information.
            - debug (bool) : if true will save the intermediate (compiled) python
                file in usr project_dir.
        '''

        self.uuid = uuid4()
        usr_pipeline = {}
        with open(usr_yaml, 'r', encoding='UTF-8') as file:
            usr_pipeline = yaml.load(file, Loader=yaml.FullLoader)

        p = Parser(project_path=self.project_dir, user_defined_yaml=usr_pipeline)

        try:
            r = Renderer(p.dict, str(self.uuid))
        except Exception as exp:  # pylint: disable=W0703
            # dumps the dict content in a json file in tmp_folder
            dump_contents = p.yaml
            dump_path = os.path.join(self.logs_dir, f'usr_yaml.{self.uuid}.json')
            with open(dump_path, 'w', encoding='UTF-8') as file:
                file.write(json.dumps(dump_contents))

            click.prompt(
                BColors.FAIL,
                f"{exp}::Error in generating final dict, check '{dump_path}'",
                BColors.RESET
            )

        self.pipeline_py = Utils.clean_dirname(p.dict['pipelineName'] + '.py')
        if debug:  # save temporary files in project directory
            r.render(target_path=self.pipeline_py)
        else:
            self.pipeline_py = os.path.join(self.tmp_dir, self.pipeline_py)
            r.render(target_path=self.pipeline_py)

    def _compile_pipeline(self, verbose, debug, *args, **kwargs):
        '''
        Compiles using the subprocess module.
        '''

        final_command = f'{self.python3_path} {self.pipeline_py} compile_pipeline -h "{self.uuid}"'

        try:
            subprocess.run(
                ['/bin/sh', '-c', final_command],
                check=True
            )
        except subprocess.CalledProcessError as exp:
            click.prompt(f'{exp}::Error in Compiling pipeline: "{self.pipeline_py}"')

    def create_bucket(self, verbose, debug, *args, **kwargs):
        '''
        Compiles using the subprocess module.
        '''

        final_command = f'{self.python3_path} {self.pipeline_py} create_bucket -h "{self.uuid}"'

        try:
            subprocess.run(
                ['/bin/sh', '-c', final_command],
                check=True
            )
        except subprocess.CalledProcessError as exp:
            click.prompt(f'{exp}::Error in Creating Bucket from pipeline: "{self.pipeline_py}"')

    def prepare_env(self, verbose, debug, *args, **kwargs):
        '''
        Compiles using the subprocess module.
        '''

        final_command = f'{self.python3_path} {self.pipeline_py} prepare_env -h "{self.uuid}"'

        try:
            subprocess.run(
                ['/bin/sh', '-c', final_command],
                check=True
            )
        except subprocess.CalledProcessError as exp:
            click.prompt(
                f'{exp}::Error in Preparing Environment from pipeline: "{self.pipeline_py}"'
            )

    def create_run(self, verbose, debug, *args, **kwargs):
        '''
        Compiles using the subprocess module.
        '''

        final_command = f'{self.python3_path} {self.pipeline_py} create_run -h "{self.uuid}"'

        try:
            subprocess.run(
                ['/bin/sh', '-c', final_command],
                check=True
            )
        except subprocess.CalledProcessError as exp:
            click.prompt(
                f'{exp}::Error in Creating Run from pipeline: "{self.pipeline_py}"'
            )

    def create_recurring_run(self, verbose, debug, *args, **kwargs):
        '''
        Compiles using the subprocess module.
        '''

        final_command = f'{self.python3_path} {self.pipeline_py} create_recurring_run -h "{self.uuid}"'

        try:
            subprocess.run(
                ['/bin/sh', '-c', final_command],
                check=True
            )
        except subprocess.CalledProcessError as exp:
            click.prompt(
                f'{exp}::Error in Creating Recurring Run from pipeline: "{self.pipeline_py}"'
            )


    def compile_pipeline(self, *args, **kwargs):
        '''
        '''

        self._render_pipeline(*args, **kwargs)
        self._compile_pipeline(*args, **kwargs)
