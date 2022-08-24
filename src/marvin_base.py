'''
Base classes inherited by other marvin modules.
'''

import os
import configparser


class MarvinBase:
    '''
    '''

    def __init__(self, *args, project_path='.', **kwargs):  # pylint: disable=W0613
        self.project_path = os.path.abspath(project_path)

    # criar alguns objs no marvin base


class MarvinDefaults(MarvinBase):
    '''
    MarvinDefaults class is used to retrieve defaults from project or marvin install
    dir.
    '''

    # TODO: fazer buscar rimeiro no marvin base dpois no projeto
    MARVIN_DEFAULTS_FILE_NAME = 'marvin_defaults.conf'

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)

        config = configparser.ConfigParser()
        config.optionxform = str  # this option allows us to have upper case letters in our .conf file check for more: # noqa: E501 # pylint: disable=C0301
        # https://docs.python.org/2/library/configparser.html#ConfigParser.RawConfigParser.optionxform
        # https://stackoverflow.com/questions/19359556/configparser-reads-capital-keys-and-make-them-lower-case
        self._config_file_path = os.path.join(
            os.getenv('MARVIN_PATH', './'),  # default path is set as './' for current testing
            MarvinDefaults.MARVIN_DEFAULTS_FILE_NAME
        )

        if self.project_path is not None:
            project_config_path = os.path.join(self.project_path,
                                               MarvinDefaults.MARVIN_DEFAULTS_FILE_NAME)
            if os.path.exists(project_config_path):
                self._config_file_path = project_config_path

        config.read(self._config_file_path)
        pipeline_config = dict(config['PIPELINE'])

        self.__dict__.update(pipeline_config)
