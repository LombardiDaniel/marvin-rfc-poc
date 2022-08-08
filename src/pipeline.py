import yaml

from container_wrapper import ContainerWrapper as Container
from minio_utils import MinioUtils


# Oq precisa fzer:
#   - Gerar nome do bucket
#   - Criar o bucket
#   - Calcular os arquivos q precisam ser upados antes da run
#       > se um container exporta mas nao importa, ele cria, NAO precisa subir
#       > se um container import e o anterior NAO exporta, precisa subir
#   - Sobe os arquivos necessários
#   - cria os containers

# na vdd só leva os do primeiro pq o resto só vai saber se da qnd rodar

class Pipeline:
    '''
    '''

    def __init__(self, yaml_path=None):

        with open(yaml_path, 'r', 'UTF-8') as file:
            self.yaml = yaml.load(file, Loader=yaml.FullLoader)

        self.steps = []

    def parse_steps(self):
        '''
        '''

        for k, v in self.yaml.items():
            if isinstance(v, list):
                for item in v:
                    pass


# olhar o pipeline.yaml, precisa ter algum tipo de variável 'ctx', que é um dict
# com o contexto atual
