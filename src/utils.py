'''
General Utils for other modules.
'''

import os
import shutil

import click


class Utils:
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

            if prompt_overwrite:
                yes = click.prompt(f'{destination} already exists, overwrite? (y/n)', type=str)

                if yes != 'y':
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
