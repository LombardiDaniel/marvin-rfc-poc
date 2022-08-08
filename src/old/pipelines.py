'''
'''

import os
import shutil

from errors import ExecutorError, FileDependencieNotFound


class MarvinInstance:
    '''
    '''

    MARVIN_DATA_PATH = os.getenv('MARVIN_DATA_PATH', '~/marvin/data')


class MarvinPipelineFile:
    '''
    '''

    MARVIN_DATA_PATH = os.getenv('MARVIN_DATA_PATH', '~/marvin/data')


    def __init__(self, project_name, file_path):
        self.project_name = project_name
        self.original_path = file_path

        self.internal_path = os.path.join(
            MarvinPipelineFile.MARVIN_DATA_PATH,
            self.project_name
        )


    def save_file(self):
        '''
        '''

        shutil.copyfile(self.original_path, self.internal_path)


class MarvinSteps(MarvinPipelineFile):
    '''
    '''

    def __init__(self, project_name, file_path):
        super().__init__(project_name, file_path)


class MarvinPipeline:
    '''
    tmp
    '''

    def __init__(self, ctx, exec_path, *args, **kwargs): # pylint: disable=W0613
        self.ctx = ctx
        self.env_vars = []
        self.file_dependencies = []
        self.exec_path = None
        self.executor = None
        # exec path eh o novo generico pra "notebookPath" (mais generico)
        MarvinPipeline._raise_errors(kwargs)

        if 'executor' not in kwargs:
            exec_extension = os.path.splitext(exec_path)

            if exec_extension == '.py':
                self.executor = 'python'

            if exec_extension == '.ipynb':
                self.executor = 'papermill'

        else:
            self.executor = kwargs['executor']


        if 'envVars' in kwargs:
            self.env_vars = kwargs['envVars']



        for file in file_dependencies:
            pass # copiar pra dentro do marvinData/project





    def save_ctx(self):
        '''
        tmp
        '''



    @staticmethod
    def _raise_errors(kwargs_dict):
        '''
        Checks for individual errors on parameters that are linked.
        '''

        if 'notebookPath' in kwargs_dict:
            if kwargs_dict['executor'] != 'papermill':
                raise ExecutorError(
                    'Executor for Jupyter Notebooks must be "papermill"'
                )

        if 'fileDependencies' in kwargs_dict:
            for file in kwargs_dict['fileDependencies']:
                status = os.path.exists(os.path.abspath(file))
                if not status:
                    FileDependencieNotFound(
                        f"Dependency Not Found: {file}"
                    )
