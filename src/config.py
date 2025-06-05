import os

import yaml


def load_config():
    config_path = os.getenv("CONFIG_PATH", "../config.yaml")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)
