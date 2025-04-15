import yaml
import os

def load_config(config_file):
    """Load configuration from a YAML file."""
    config_path=os.path.join("configs", config_file)
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config
