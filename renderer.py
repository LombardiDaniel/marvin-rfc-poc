'''
'''

import jinja2

from s3_utils import S3Utils


class Renderer:
    '''
    '''

    # esse complete_yaml tenq ser a U (uniao) dos yaml la, fzer tipo:
    # for k, v in steps.items():
    #     if k not in pipeline.keys():
    #         # mais um for k, v aqui dnetro
    #         pipeline[k] = v
    #
    def __init__(self, complete_yaml):
        self.parsed_yaml = Renderer._parse_yaml(complete_yaml)

    @staticmethod
    def _parse_yaml(complete_yaml):
        '''
        Fixes the "keys should not contain data" problem.
        '''

        for step, i in enumerate(complete_yaml['pipelineExecutionOrder']):
            # in here, all items will be either a dictionary (linear) or a list (parallel)
            if isinstance(step, dict):
                for k, v in step.items():  # step will only have one key
                    complete_yaml['pipelineExecutionOrder'][i] = {
                        'name': k,
                        'metadata': v
                    }

            elif isinstance(step, list):
                for parallel_step, j in enumerate(step):
                    for k, v in parallel_step.items():
                        complete_yaml['pipelineExecutionOrder'][i][j] = {
                            'name': k,
                            'metadata': v
                        }

        return complete_yaml

    def calculate_uploads(self):
        '''
        Calculates files needed to upload to storage before pipeline run.
        '''

        inputs = []
        outputs = []

        for step in self.parsed_yaml['pipelineExecutionOrder']:
            inputs += step['fileInputs']
            outputs += step['fileOutputs']

        return [item for item in inputs if item not in outputs]
