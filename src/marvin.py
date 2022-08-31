'''
nao sei como faz pra chamr o marvin de diferentes repositorios
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

    def init_project(self, template, project_name):
        '''
        Initializes the project, will use cookiecutter in the future, as of now
        simply copies the '.marvin' file into the project dir and populates base
        fields.
        '''
        template_src = os.path.join(USR_TEMPLATES_DIR, template)

        if template not in [item for item in os.listdir(USR_TEMPLATES_DIR) if os.path.isdir(item)]:
            raise MarvinTemplateNotFoundError(
                f'Template "{template}" not in "{USR_TEMPLATES_DIR}".'
            )

        Utils.copy_dir_from_template(template_src, self.project_dir)

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

        # dumps the dict content in a json file in tmp_folder
        try:
            r = Renderer(p.dict, str(self.uuid))
        except Exception as exp:  # pylint: disable=W0703
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

    def compile_pipeline(self, *args, **kwargs):
        '''
        '''

        self._render_pipeline(*args, **kwargs)
        self._compile_pipeline(*args, **kwargs)
