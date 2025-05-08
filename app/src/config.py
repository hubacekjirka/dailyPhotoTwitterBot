import pyaml as yaml

from Exceptions import ConfigLoadError

try:
    with open("config.yaml", "r") as f:
        CONFIG = yaml.safe_load(f)
except Exception as ex:
    raise ConfigLoadError("Failed to load config") from ex
