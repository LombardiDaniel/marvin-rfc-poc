'''
nao sei como faz pra chamr o marvin de diferentes repositorios
'''

import os
import shutil
import json
import subprocess
from uuid import uuid4

import click
import yaml

from marvin_base import MarvinBase, MarvinDefaults
from renderer import Renderer
from parser import Parser
from utils import Utils


MARVIN_PATH = os.getenv('MARVIN_PATH', '~/usr/bin/marvin')
USR_TEMPLATES_DIR = os.path.join(MARVIN_PATH, 'project_templates')
MARVIN_TEMPLATE_OPTIONS = os.listdir(USR_TEMPLATES_DIR)


class Marvin(MarvinBase):
    '''
    Abstraction/Class to be used by the CLI

    Attributes:
    '''

    def __init__(self, *args, uuid=None, **kwargs):
        super().__init__(self, *args, **kwargs)

        self.default = MarvinDefaults()
        self.uuid = uuid4() if uuid is None else uuid
        self.pipeline_py = None

    def _render_pipeline(self, verbose, debug):
        '''
        Also sets self.pipeline_py attribute.
        Loads and compiles the user defined pipline.
        # NOTE: does NOT support imports atm

        Args:
            - verbose (bool) : if true will print out verbose/progress information.
            - debug (bool) : if true will save the intermediate (compiled) python
                file in usr project_dir.
        '''

        usr_pipeline = {}
        with open(self.project_path, 'r', encoding='UTF-8') as file:
            usr_pipeline = yaml.load(file, Loader=yaml.FullLoader)

        p = Parser(project_path=self.project_path, user_defined_yaml=usr_pipeline)

        r = Renderer(p.dict, str(self.uuid))

        self.pipeline_py = Utils.clean_dirname(p.dict['pipelineName'])
        if debug:  # save temporary files in project directory
            r.render(target_path=self.pipeline_py)
        else:
            self.pipeline_py = os.path.join(self.tmp_dir, self.pipeline_py)
            r.render(target_path=self.pipeline_py)

    def _compile_pieline(self, verbose, debug):
        '''
        Compiles using the subprocess module.
        '''

        final_command = f'{self.python3_path} {self.pipeline_py} compile_pieline -h "{self.uuid}"'

        try:
            subprocess.run(
                ['/bin/sh', '-c', final_command],
                check=True
            )
        except subprocess.CalledProcessError as exp:
            click.prompt(f'{exp}::Error in Compiling pipeline: "{self.pipeline_py}"')

    def compile_pieline(self, *args, **kwargs):
        '''
        '''

        self._render_pipeline(*args, **kwargs)
        self._compile_pieline(*args, **kwargs)
