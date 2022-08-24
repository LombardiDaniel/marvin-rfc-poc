"""
Jinja template for pipeline creation.
"""

from datetime import datetime

import kfp
from kfp import dsl

from container_wrapper import ContainerWrapper as Container
from s3_utils import S3Utils


# - ***Variables for user project*** - #
PROJECT_NAME = "pipeline_housing_prices"


S3_ACCESS_KEY = "minio_key"

S3_SECRET_KEY = "$MINIO_SECRET_KEY"

S3_ENDPOINT = "minio_uri"


BUCKET_NAME_VAR = S3Utils.replace_invalid_bucket_name_chars("housing_prices")
BUCKET_PATH = ""


def create_container(**kwargs):
    """
    Wraps container with env vars, forwards env vars with kwargs.
    """

    return Container(
        setup_command="pip install -r requirements.txt",
        verbose=True,
        S3_ACCESS_KEY="minio_key",
        S3_SECRET_KEY="$MINIO_SECRET_KEY",
        S3_ENDPOINT="minio_uri",
        BUCKET_NAME=BUCKET_NAME_VAR,
        BUCKET_PATH=BUCKET_PATH,
        **kwargs,
    )


# TODO: Currentrly this uses only S3, must be adapted for later use with various types (create a masterClass)
def setup_storage_pipeline_dependencies(files=[]):
    """
    Manually sets up the s3 objects for the first container.
    """

    local_files = [file["key"] for file in files if file["value"] == "local"]

    s3 = S3Utils(
        S3_ENDPOINT,
        S3_ACCESS_KEY,
        S3_SECRET_KEY,
        bucket_name=BUCKET_NAME_VAR,
        bucket_path=BUCKET_PATH,
    )

    s3.upload(local_files)

    # TODO: still needs to treat other file sources -> can even be user defined


# - ***USER DEFINED PIPELINE*** - #

# Generate funcions


def acquisitor_step_func():
    container = create_container(
        MY_ENV_VAR="test_specific_env",
    )
    container.name = "acquisitor"

    container.file_inputs = [
        "test.csv",
        "train.csv",
        "requirements.txt",
    ]

    container.file_outputs = []

    return container.run("python acquisitor.py")


def data_prep_step_func():
    container = create_container()
    container.name = "data_prep"

    container.file_inputs = [
        "test.csv",
        "train.csv",
        "requirements.txt",
    ]

    container.file_outputs = [
        "X_train.csv",
        "y_train.csv",
        "X_test.csv",
        "y_test.csv",
    ]

    return container.run("python data_prep.py")


def train_model_step_func():
    container = create_container()
    container.name = "train_model"

    container.file_inputs = [
        "X_train.csv",
        "y_train.csv",
        "X_test.csv",
        "y_test.csv",
        "requirements.txt",
    ]

    container.file_outputs = [
        "regressionTree",
        "regressionLinear",
        "randomForest",
    ]

    return container.run("python train_model.py")


def evaluate_step_func():
    container = create_container()
    container.name = "evaluate"

    container.file_inputs = [
        "X_train.csv",
        "y_train.csv",
        "X_test.csv",
        "y_test.csv",
        "regressionTree",
        "regressionLinear",
        "randomForest",
        "requirements.txt",
    ]

    container.file_outputs = []

    return container.run("python evaluate.py")


@dsl.pipeline(
    name="pipeline_housing_prices",
    description="Pipeline for presentation of famous housing_prices problem",
)
def pipeline_housing_prices_step_func():

    acquisitor_step_func = acquisitor_step_func()

    data_prep_step_func = data_prep_step_func()

    data_prep_step_func.after(acquisitor_step_func)

    train_model_step_func = train_model_step_func()

    train_model_step_func.after(data_prep_step_func)

    evaluate_step_func = evaluate_step_func()

    evaluate_step_func.after(train_model_step_func)


# falta montar a main certa
if __name__ == "__main__":
    # TODO: colocar algum tipo de if aqui, q usa sys.args, e a gnt passa na hr de compilar, se entrar no if, sobe os arquivos e o pipe, cria a run e bora

    PROJECT_NAME = S3Utils.replace_invalid_bucket_name_chars(PROJECT_NAME)

    # hash = uuid.uuid4()  # o proprio marvin passa o hash pro arquivo final -> template recebe o hash
    # TODO: só entra aqui SE tiver especificado que vai criar run?
    global HASH_
    HASH_ = "6acee885-996f-4673-9c5f-45f38967f695"
    date_str = datetime.now().strftime("%Y-%m-%d")

    global BUCKET_PATH_
    BUCKET_PATH_ = f"{PROJECT_NAME}-{date_str}-{HASH_}"

    pipeline_file_path = f"{PROJECT_NAME}.yaml"

    kfp.compiler.Compiler().compile(
        pipeline_housing_prices_step_func, pipeline_file_path
    )
    print(BUCKET_PATH_)
