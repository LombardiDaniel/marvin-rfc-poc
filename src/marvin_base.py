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
    '''

    MARVIN_DEFAULTS_FILE_NAME = 'marvin_defaults.conf'

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        config = configparser.ConfigParser()
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

        # for k, v in config['PIPELINE'].items():
        #     print(k, v)
        #     self.__dict__[k] = v
        
        self.__dict__['pipelineFileDependencies'] = config['PIPELINE']['pipelineFileDependencies']
        # self.pipelineFileDependencies = config['PIPELINE']['pipelineFileDependencies']
