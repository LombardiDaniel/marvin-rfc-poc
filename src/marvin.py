from renderer import Renderer
from parser import Parser

if __name__ == '__main__':
    import yaml
    import uuid

    y = {}
    with open('../examples/housing_prices_pipeline/pipeline.yaml', 'r', encoding='UTF=8') as f:
        y = yaml.load(f, Loader=yaml.FullLoader)

    p = Parser(project_path='.', user_defined_yaml=y)

    r = Renderer(p.dict, uuid.uuid4())
    r.render('../examples/housing_prices_pipeline/rendered_pipe_from_user_yaml.py', True)


    # tmp:
    # if user_command == 'marvin pipeline upload_dependencies':
    #     COMMAND = 'python pipeline.py --op upload_to_s3 --bucket_name = '
    #
    #     subprocess.run(
    #         ['/bin/sh', '-c', COMMAND]
    #     )
