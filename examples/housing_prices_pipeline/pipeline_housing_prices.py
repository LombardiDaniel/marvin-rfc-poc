"""

This file was generated from the template: $MARVIN_PATH/src/templates/pipeline.py.j2

Interaction is done mainly by marvin commands. However, for debugging purposes,
the CLI usage is as follows:

`$python3 ./pipeline_housing_prices.py OPERATION -h HASH`
    - HASH (str) : Generated by marvin, available in the .marvin file inside
    your project directory. Used for bucket and KFP operations.
    - OPERATION (str) : one of:
        'compile_pipeline': compiles the pipeline
        'create_bucket': creates the bucket
        'prepare_env': prepares the environment in the cloud storage bucket
        'create_run': Creates a run in KFP
        'create_recurring_run': Creates a recurring run in KFP


*** DOCSTRING ***
Pipeline for presentation of famous housing_prices problem
"""
import argparse
from datetime import datetime

import kfp
from kfp import dsl

from marvin.container_wrapper import ContainerWrapper as Container
from marvin.s3_utils import S3Utils


ARG_OPS = [
    "compile_pipeline",
    "create_bucket",
    "prepare_env",
    "create_run",
    "create_recurring_run",
]


# - ***Variables for user project*** - #
PROJECT_NAME = "pipeline_housing_prices"


KFP_ENDPOINT = "kfp_uri"

S3_ACCESS_KEY = "minio_key"

S3_SECRET_KEY = "minhaChaveSecretaaa444aa"

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
        KFP_ENDPOINT="kfp_uri",
        S3_ACCESS_KEY="minio_key",
        S3_SECRET_KEY="minhaChaveSecretaaa444aa",
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
    """
    Acquisitor
    """

    container = create_container(
        image="python:3.8",
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
    """
    Data preparator
    """

    container = create_container(
        image="python:3.7",
    )
    container.name = "data_prep"

    container.file_inputs = [
        "test.csv",
        "train.csv",
        "data_prep.py",
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
    """
    Train the machine learning model
    """

    container = create_container(
        image="python:3.7",
    )
    container.name = "train_model"

    container.file_inputs = [
        "X_train.csv",
        "y_train.csv",
        "X_test.csv",
        "y_test.csv",
        "train_model.py",
        "requirements.txt",
    ]

    container.file_outputs = [
        "regressionTree",
        "regressionLinear",
        "randomForest",
    ]

    return container.run("python train_model.py")


def evaluate_step_func():
    """
    Evaluates the metrics
    """

    container = create_container(
        image="python:3.7",
    )
    container.name = "evaluate"

    container.file_inputs = [
        "X_train.csv",
        "y_train.csv",
        "X_test.csv",
        "y_test.csv",
        "regressionTree",
        "regressionLinear",
        "randomForest",
        "evaluate.py",
        "requirements.txt",
    ]

    container.file_outputs = []

    return container.run("python evaluate.py")


@dsl.pipeline(
    name="pipeline_housing_prices",
    description="Pipeline for presentation of famous housing_prices problem",
)
def pipeline_housing_prices_pipe_func():

    acquisitor_step_pointer_func = acquisitor_step_func()

    data_prep_step_pointer_func = data_prep_step_func()

    data_prep_step_pointer_func.after(acquisitor_step_pointer_func)

    train_model_step_pointer_func = train_model_step_func()

    train_model_step_pointer_func.after(data_prep_step_pointer_func)

    evaluate_step_pointer_func = evaluate_step_func()

    evaluate_step_pointer_func.after(train_model_step_pointer_func)


# falta montar a main certa
if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-h", "--hash", help="UUID for storage_bucket/run.")
    parser.add_argument("op", type=str, choices=ARG_OPS, help="Operation")
    args = parser.parse_args()

    PROJECT_NAME = S3Utils.replace_invalid_bucket_name_chars(PROJECT_NAME)

    uuid_hash = args.hash
    date_str = datetime.now().strftime("%Y-%m-%d")

    bucket_path = f"{PROJECT_NAME}-{date_str}-{uuid_hash}"

    pipeline_file_path = f"{PROJECT_NAME}.yaml"

    client = kfp.Client(host="")

    # OPERATIONS::
    if args.op == "compile_pieline":  # this op requests a new uuid
        kfp.compiler.Compiler().compile(
            pipeline_housing_prices_pipe_func, pipeline_file_path
        )

    if args.op == "create_bucket":
        S3Utils.create_bucket(BUCKET_NAME_VAR)

    exp_obj = None
    if args.op == "prepare_env":
        setup_storage_pipeline_dependencies([])
        exp_obj = client.create_experiment(
            name="pipeline_housing_prices",
            description="Pipeline for presentation of famous housing_prices problem",
        )
        print(f"Bucket Path: '{bucket_path}'")

    if args.op == "create_run":
        client.create_run_from_pipeline_package(
            experiment_name=bucket_path,
            pipeline_file=pipeline_file_path,
            enable_caching=True,
        )

    elif args.op == "create_recurring_run":
        client.create_recurring_run(
            experiment_id=exp_obj.id,
            pipeline_package_path=pipeline_file_path,
            cronExpression="0-59/2 * * * *",
            max_concurrency=2,
            no_catchup=True,
        )
