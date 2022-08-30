#!/usr/bin/env python3
# !/usr/bin/marvin -> alias para: $MARVIN_PATH/venv/bin/python3
'''
nao sei como faz pra chamr o marvin de diferentes repositorios
'''

import os
import shutil
import json
from uuid import uuid4 as uuid_gen

import click
import yaml

from renderer import Renderer
from parser import Parser
from utils import Utils, BColors
from marvin import Marvin

MARVIN_PATH = os.getenv('MARVIN_PATH', '~/usr/bin/marvin')
USR_TEMPLATES_DIR = os.path.join(MARVIN_PATH, 'project_templates')
MARVIN_TEMPLATE_OPTIONS = os.listdir(USR_TEMPLATES_DIR)


@click.group()
@click.option('-v', '--verbose', is_flag=True, default=False)
def cli(verbose):
    if verbose:
        print(f'{BColors.WARNING}verbose set{BColors.ENDC}')


@cli.command()
@click.option(
    '--project_dir',
    type=click.Path(exists=True),
    default=os.getcwd()
)
@click.option('-v', '--verbose', is_flag=True, default=False)
@click.option(
    '--template',
    type=click.Choice(MARVIN_TEMPLATE_OPTIONS, case_sensitive=False),
    default='clean'
)
@click.option(
    '--name',
    default=lambda: os.path.basename(os.getcwd())
)
def init(project_dir, verbose, template, name):
    '''
    # TODO: substituir pelo cookiecutter (e ver cmo funciona -> n to achando)
    '''
    project_name = Utils.clean_dirname(name)
    template_src = os.path.join(USR_TEMPLATES_DIR, template)

    if template == 'clean':

        Utils.copy_dir_from_template(template_src, project_dir)

        name_line = ''
        with open(os.path.join(project_dir, '.marvin'), 'r', encoding='UTF-8') as f:
            name_line = f.read().format(project_name)

        with open(os.path.join(project_dir, '.marvin'), 'w', encoding='UTF-8') as f:
            f.write(name_line)


@cli.command()
@click.option(
    '-f',
    '--pipeline-file',
    type=click.Path(exists=True),
    default='pipeline.yaml'
)
@click.option('-v', '--verbose', is_flag=True, default=False)
@click.option('-d', '--debug', is_flag=True, default=False)
def compile(pipeline_file, verbose, debug):
    '''
    '''

    m = Marvin()
    m.compile_pipeline(pipeline_file, verbose, debug)


if __name__ == '__main__':

    # cli.add_command(init)

    cli()  # pylint: disable=E1120

    # tmp:
    # if user_command == 'marvin pipeline upload_dependencies':
    #     COMMAND = 'python pipeline.py --op upload_to_s3 --bucket_name = '
    #
    #     subprocess.run(
    #         ['/bin/sh', '-c', COMMAND]
    #     )

# from repo home folder:
# export "MARVIN_PATH"="$(pwd)/src" && export PATH=$PATH:$MARVIN_PATH
