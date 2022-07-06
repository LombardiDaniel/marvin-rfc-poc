from pprint import pprint
import yaml
import typer

from pipelines import MarvinInstance


app = typer.Typer()


@app.command()
def pipeline(pipeline_path: str):
    '''
    tmp
    '''

    with open(pipeline_path, mode='r', encoding='utf-8') as file:
        pipeline_dict = yaml.load(file, Loader=yaml.FullLoader)

        pprint(pipeline_dict)


@app.command()
def init(name: str, template: str='None', clean: bool = False, tutorial: bool = False):
    '''
    tmp
    '''

    mrvn = MarvinInstance()


if __name__ == '__main__':
    app()
