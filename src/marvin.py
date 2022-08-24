from renderer import Renderer
from parser import Parser

if __name__ == '__main__':
    import yaml
    import uuid

    y = {}
    with open('../examples/housing_prices_pipeline/pipeline.yaml', 'r', encoding='UTF=8') as f:
        y = yaml.load(f, Loader=yaml.FullLoader)

    p = Parser(project_path='.', user_defined_yaml=y)

    r = Renderer(p.json, uuid.uuid4())
    r.render('../examples/housing_prices_pipeline/rendered_pipe_from_user_yaml.py', True)
