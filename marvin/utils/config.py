import os
import yaml

class Config:
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = os.environ['MARVIN_CONFIG']
        with open(config_path, 'r') as f:
            parsed_yaml = yaml.safe_load(f)
        
        self.kfp_url = parsed_yaml['backend']['kfp_url']
        self.s3_url = parsed_yaml['storage']['s3_url']
        self.s3_access_key = parsed_yaml['storage']['s3_access_key']
        self.s3_secret_key = parsed_yaml['storage']['s3_secret_key']