'''
Base classes inherited by other marvin modules.
'''

import os
import configparser
import uuid

import yaml


MARVIN_PATH = os.getenv('MARVIN_PATH', '~/usr/bin/marvin')
USR_TEMPLATES_DIR = os.path.join(MARVIN_PATH, 'project_templates')
MARVIN_TEMPLATE_OPTIONS = os.listdir(USR_TEMPLATES_DIR)


class MarvinBase:  # pylint: disable=R0903
    '''
    MarvinBase specifies common attributes shared by other marvin modules.
    '''

    INTERNAL_PYTHON_PATH = 'venv/bin/python3'
    TEMP_PIPELINES_DIR = '/tmp/marvin_pipelines'

    def __init__(self, *args, project_path=os.getcwd(), **kwargs):  # pylint: disable=W0613
        self.project_path = os.path.abspath(project_path)
        self.tmp_dir = os.path.join(os.getenv('HOME'), MarvinBase.TEMP_PIPELINES_DIR)

        if not os.path.exists(self.tmp_dir):
            os.makedirs(self.tmp_dir)

        self.python3_path = os.path.join(MARVIN_PATH, MarvinBase.INTERNAL_PYTHON_PATH)

    # criar alguns objs no marvin base


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

        if self.project_path is not None:
            project_config_path = os.path.join(self.project_path,
                                               MarvinDefaults.MARVIN_DEFAULTS_FILE_NAME)
            if os.path.exists(project_config_path):
                self._config_file_path = project_config_path

            config.read(self._config_file_path)
            self.__dict__.update(dict(config['PIPELINE']))  # load user config into obj attributes
