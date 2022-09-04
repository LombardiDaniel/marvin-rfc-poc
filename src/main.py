#!/usr/bin/env python3
# !/usr/bin/marvin -> alias para: $MARVIN_PATH/venv/bin/python3
'''
nao sei como faz pra chamr o marvin de diferentes repositorios
'''

import os
import shutil
import json

import click
import yaml

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
@click.option('-f', '--force-overwrite', is_flag=True, default=False)
def init(project_dir, verbose, template, name, force_overwrite):
    '''
    # TODO: substituir pelo cookiecutter (e ver cmo funciona -> n to achando)
    # TODO: passar isso aqui pra Marvin Class
    '''
    project_name = Utils.clean_dirname(name)

    m = Marvin(project_dir=project_dir)
    m.init_project(template, project_name, force_overwrite)


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


@cli.command()
@click.option(
    '-f',
    '--pipeline-file',
    type=click.Path(exists=True),
    default='pipeline.yaml'
)
@click.option('-v', '--verbose', is_flag=True, default=False)
@click.option('-d', '--debug', is_flag=True, default=False)
def incremental_create_bucket(pipeline_file, verbose, debug):
    '''
    '''

    m = Marvin()
    m.create_bucket(pipeline_file, verbose, debug)


@cli.command()
@click.option(
    '-f',
    '--pipeline-file',
    type=click.Path(exists=True),
    default='pipeline.yaml'
)
@click.option('-v', '--verbose', is_flag=True, default=False)
@click.option('-d', '--debug', is_flag=True, default=False)
def incremental_prepare_env(pipeline_file, verbose, debug):
    '''
    '''

    m = Marvin()
    m.prepare_env(pipeline_file, verbose, debug)


@cli.command()
@click.option(
    '-f',
    '--pipeline-file',
    type=click.Path(exists=True),
    default='pipeline.yaml'
)
@click.option('-v', '--verbose', is_flag=True, default=False)
@click.option('-d', '--debug', is_flag=True, default=False)
def incremental_crete_run(pipeline_file, verbose, debug):
    '''
    '''

    m = Marvin()
    m.create_run(pipeline_file, verbose, debug)


@cli.command()
@click.option(
    '-f',
    '--pipeline-file',
    type=click.Path(exists=True),
    default='pipeline.yaml'
)
@click.option('-v', '--verbose', is_flag=True, default=False)
@click.option('-d', '--debug', is_flag=True, default=False)
def incremental_crete_recurring_run(pipeline_file, verbose, debug):
    '''
    '''

    m = Marvin()
    m.create_recurring_run(pipeline_file, verbose, debug)


@cli.command()
@click.option(
    '-f',
    '--pipeline-file',
    type=click.Path(exists=True),
    default='pipeline.yaml'
)
@click.option('-v', '--verbose', is_flag=True, default=False)
@click.option('-d', '--debug', is_flag=True, default=False)
def compile_and_run(pipeline_file, verbose, debug):
    '''
    '''

    m = Marvin()
    m.compile_pipeline(pipeline_file, verbose, debug)
    m.create_bucket(pipeline_file, verbose, debug)
    m.prepare_env(pipeline_file, verbose, debug)
    m.create_run(pipeline_file, verbose, debug)



if __name__ == '__main__':
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
