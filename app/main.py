import os
from pathlib import Path

from bot import Bot
from config import load_config

CONFIG_PATH_ENV_VAR = "BOT_CONFIG_PATH"
DEFAULT_CONFIG_FILE_PATH = Path(__file__).resolve().parent / "config.yaml"


def get_config_path() -> Path:
    config_path = os.environ.get(CONFIG_PATH_ENV_VAR)
    if config_path:
        return Path(config_path).expanduser()

    cwd_config_path = Path(DEFAULT_CONFIG_FILE_PATH.name)
    if cwd_config_path.exists():
        return cwd_config_path.resolve()

    return DEFAULT_CONFIG_FILE_PATH


def main() -> None:

    bot = Bot(load_config(get_config_path()))
    bot.run()


if __name__ == "__main__":
    main()
