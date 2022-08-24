'''
General Utils for other modules.
'''

import configparser
import os


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
