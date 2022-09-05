import os
import shutil
import json
import subprocess
from uuid import uuid4

import click
import yaml

from marvin.dsl.renderer import Renderer
from parser import Parser
from marvin.utils.utils import Utils

class Compiler():
    def __init__(self, *args, uuid=None, **kwargs):
        super().__init__(self, *args, **kwargs)

        self.uuid = uuid4() if uuid is None else uuid
        self.pipeline_py = None

    def render_pipeline(self, usr_yaml, verbose, debug, *args, **kwargs):
        usr_pipeline = {}
        with open(usr_yaml, 'r', encoding='UTF-8') as file:
            usr_pipeline = yaml.load(file, Loader=yaml.FullLoader)

        p = Parser(project_path=self.project_path, user_defined_yaml=usr_pipeline)

        r = Renderer(p.dict, str(self.uuid))

        self.pipeline_py = Utils.clean_dirname(p.dict['pipelineName'] + '.py')
        if debug:  # save temporary files in project directory
            r.render(target_path=self.pipeline_py)
        else:
            self.pipeline_py = os.path.join(self.tmp_dir, self.pipeline_py)
            r.render(target_path=self.pipeline_py)

    def compile_and_run_pipeline(self, verbose, debug, *args, **kwargs):
        final_command = f'{self.python3_path} {self.pipeline_py} compile_pipeline -h "{self.uuid}"'

        try:
            subprocess.run(
                ['/bin/sh', '-c', final_command],
                check=True
            )
        except subprocess.CalledProcessError as exp:
            click.prompt(f'{exp}::Error in Compiling pipeline: "{self.pipeline_py}"')
