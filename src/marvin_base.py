'''
Base classes inherited by other marvin modules.
'''

import os
import configparser
from uuid import uuid4

import yaml

from utils import Utils


MARVIN_PATH = os.getenv('MARVIN_PATH', '~/usr/bin/marvin')
USR_TEMPLATES_DIR = os.path.join(MARVIN_PATH, 'project_templates')
MARVIN_TEMPLATE_OPTIONS = os.listdir(USR_TEMPLATES_DIR)


class MarvinBase:  # pylint: disable=R0903
    '''
    MarvinBase specifies common attributes shared by other marvin modules.
    '''

    INTERNAL_PYTHON_PATH = 'venv/bin/python3'
    TEMP_PIPELINES_DIR = '/tmp/marvin_pipelines'

    @property
    def uuid(self):
        '''
        '''
        curr_uuid = self._get_marvin_dict()['LAST_UUID']
        if curr_uuid in ['None', '{}', None, 'NONE', 'none']:
            self.uuid = str(uuid4())

        return self._get_marvin_dict()['LAST_UUID']

    @uuid.setter
    def uuid(self, new_uuid):
        '''
        '''

        curr_dict = self._get_marvin_dict()
        curr_dict.update({
            'LAST_UUID': new_uuid
        })

        self._set_marvin_dict(
            curr_dict
        )

    def __init__(self, *args, project_dir=os.getcwd(), **kwargs):  # pylint: disable=W0613
        self.project_dir = os.path.abspath(project_dir)

        self.tmp_dir = os.path.join(os.getenv('HOME'), MarvinBase.TEMP_PIPELINES_DIR)
        if not os.path.exists(self.tmp_dir):
            os.makedirs(self.tmp_dir)

        self.logs_dir = os.path.join(self.tmp_dir, '/logs/')
        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)

        self.python3_path = os.path.join(MARVIN_PATH, MarvinBase.INTERNAL_PYTHON_PATH)

        # self._load_marvin_dict()
        # self.uuid = self.PROJECT_UUID

    def setup_marvin_base_file(self, project_name):
        '''
        '''

        n_d = self._get_marvin_dict()

        n_d.update({
            'PROJECT_NAME': Utils.clean_dirname(project_name)
        })

        self._set_marvin_dict(
            new_dict=n_d
        )

    def _get_marvin_dict(self):
        '''
        '''

        marvin_dict = {}
        with open(os.path.join(self.project_dir, '.marvin'), 'r', encoding='UTF-8') as f:
            for line in f.readlines():
                k, v = line.splitlines()[0].split('=', maxsplit=1)
                marvin_dict[k] = v

        return marvin_dict

    def _set_marvin_dict(self, new_dict):
        '''
        '''

        # if new_dict is None:
        #     new_dict = {}

        contents = ''
        for k, v in new_dict.items():
            contents += f'{k}={v}'
            contents += '\n'

        with open(os.path.join(self.project_dir, '.marvin'), 'w', encoding='UTF-8') as f:
            f.write(contents)


class MarvinDefaults(MarvinBase):  # pylint: disable=R0903
    '''
    MarvinDefaults class is used to retrieve defaults from project or marvin install
    dir.
    '''

    MARVIN_DEFAULTS_FILE_NAME = 'marvin_defaults.conf'

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)

        config = configparser.ConfigParser()
        config.optionxform = str  # this option allows us to have upper case letters in our .conf file check for more: # noqa: E501 # pylint: disable=C0301
        # https://docs.python.org/2/library/configparser.html#ConfigParser.RawConfigParser.optionxform
        # https://stackoverflow.com/questions/19359556/configparser-reads-capital-keys-and-make-them-lower-case

        # Initially load default marvin_defualts.conf, after we update the in-mem. dict
        # with the user defined file
        self._config_file_path = os.path.join(
            os.getenv('MARVIN_PATH', './'),  # default path is set as './' for current testing
            MarvinDefaults.MARVIN_DEFAULTS_FILE_NAME
        )
        config.read(self._config_file_path)
        self.__dict__.update(dict(config['PIPELINE']))  # load default config into obj attributes

        if self.project_dir is not None:
            project_config_path = os.path.join(self.project_dir,
                                               MarvinDefaults.MARVIN_DEFAULTS_FILE_NAME)
            if os.path.exists(project_config_path):
                self._config_file_path = project_config_path

            config.read(self._config_file_path)
            self.__dict__.update(dict(config['PIPELINE']))  # load user config into obj attributes
