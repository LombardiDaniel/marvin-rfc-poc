'''
nao sei como faz pra chamr o marvin de diferentes repositorios
'''

import os
import shutil
import json
from uuid import uuid4 as uuid_gen

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
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)

        self.default = MarvinDefaults()

    def compile_pipeline(self, verbose, debug, *args, **kwargs):
        '''
        Loads and compiles the user defined pipline.
        # NOTE: does NOT support imports atm

        Args:
            - verbose (bool) : if true will print out verbose (progress) information.
            - debug (bool) : if true will save the intermediate (compiled) python
                file in usr project_dir.
        '''

        usr_pipeline = {}
        with open(self.project_path, 'r', encoding='UTF-8') as file:
            usr_pipeline = yaml.load(file, Loader=yaml.FullLoader)

        p = Parser(project_path=self.project_path, user_defined_yaml=usr_pipeline)


        # TODO: precisa tirar os hashes do arquivinho python gerado ???
        # NAO DA!!! -> pq o arquivo gerado precisa passar parametros fixos pro KFP?
        r = Renderer()

        target_file_name = ''
        with open('test.json', 'w', encoding='UTF-8') as f:
            f.write(json.dumps(p.dict))
