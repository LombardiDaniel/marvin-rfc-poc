import os
import shutil
import logging
from datetime import datetime
from uuid import uuid4

import click


MARVIN_PATH = os.getenv('MARVIN_PATH')
MARVIN_LOG_PATH = os.path.join(MARVIN_PATH, '/logs/')


class BColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = ENDC


class Utils:
    '''
    Simple Utils for helping other modules.
    '''

    @staticmethod
    def dumpfile(file_name, contents, uuid=False):
        '''
        Dumps content of file to a log folder.
        '''

        uuid = f'_{uuid4()}' if uuid else ''
        file_name = f"{datetime.strftime()}_{file_name}{uuid}.log"

        with open(file_name, 'w', encoding='UTF-8') as file:
            file.write(contents)


    @staticmethod
    def get_logger(file_name='marvin.log'):
        '''
        Generates the 'logging' instance to be used by other modules.
        Simple wrapper for initialization.
        '''

        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter("%(asctime)s:%(name):%(message)s")
        file_handler = logging.FileHandler(
            os.path.join(MARVIN_LOG_PATH, file_name)
        )
        file_handler.setFormatter(formatter)

        # stream_handler = logging.StreamHandler()

        logger.addHandler(file_handler)

        return logger

    @staticmethod
    def fix_key_values(k_v_dict):
        '''
        Fix the "dict keys should not contain information" problem. Particularly
        usefull for environment variable lists in user defined files.

        Args:
            - k_v_dict (dict) : dict containing a single key and value pair (with
                incorrect logic).

        Returns:
            - fixed_dict (dict) : lst in the model:
                {
                    'key': $KEY,
                    'value': $VALUE
                }
        '''

        for k, v in k_v_dict.items():
            return {
                'key': k,
                'value': v
            }

    @staticmethod
    def copy_dir_from_template(src: str, dst: str, prompt_overwrite=True):
        '''
        equivalent of:
            `cp $SRC/* $DST`
        '''

        for file_name in os.listdir(src):
            # construct full file paths
            source = os.path.join(src, file_name)
            destination = os.path.join(dst, file_name)

            if os.path.exists(destination) and prompt_overwrite:
                answ = click.prompt(
                    f'"{BColors.WARNING}{destination}{BColors.ENDC}" already exists, overwrite? (y/n)',  # noqa: E501 # pylint: disable=C0301
                    type=str
                )

                if answ != 'y':
                    continue

            shutil.copy(source, destination)

    @staticmethod
    def clean_dirname(dirname):
        '''
        removes invalid chars from dirname
        '''

        invalid_chars = '/ <>:\\/|?*\0'

        for char in invalid_chars:
            dirname = dirname.replace(char, '-')

        return dirname
