import os

import yaml
from core.exceptions import ConfigLoadError

try:
    with open(os.path.join(os.path.dirname(__file__), "config.yaml"), "r") as f:
        CONFIG = yaml.safe_load(f)
except Exception as ex:
    raise ConfigLoadError("Failed to load config") from ex
