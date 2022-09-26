import argparse
import importlib
#from marvin.utils.s3_utils import S3Utils


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--action', '-a', type=str)
    args = parser.parse_args()

    module = importlib.import_module('actions.' + args.action.lower())
    clss = getattr(module, args.action)
    instance = clss()
    instance.entrypoint()
