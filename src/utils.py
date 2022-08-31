'''
General Utils for other modules.
'''

import os
import shutil
import re

import click


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

    @staticmethod
    def format_one(string, arg):
        '''
        Equivalent of String.format(), but it will only format the first "{}" found.
        '''
        return re.sub('\{.*?\}', arg, string, count=1)  # noqa: W1401, W605 # pylint: disable=W1401
