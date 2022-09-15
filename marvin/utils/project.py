import os
import tarfile
from cookiecutter.main import cookiecutter
from .misc import filter_tar

def generate_project(name, version, output_dir):
    template_ctx = {
        'project_name': name,
        'version': version
    }
    template_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "templates/project"
        )
    cookiecutter(
        template_path,
        extra_context=template_ctx,
        #TODO: replace with MARVIN_HOME
        output_dir=os.getcwd(),
        no_input=True
    )

def make_tarball(project_name, project_path):
    output_filename = os.path.join(project_path,
                                   project_name + '.tar.gz')

    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(project_path,
                arcname=os.path.basename(os.path.sep),
                filter=filter_tar)