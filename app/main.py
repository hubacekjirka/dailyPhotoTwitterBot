import os
from pathlib import Path

from bot import Bot
from config import load_config

CONFIG_PATH_ENV_VAR = "BOT_CONFIG_PATH"
DEFAULT_CONFIG_FILE_PATH = Path("app", "config.yaml")


def get_config_path() -> Path:
    return Path(os.environ.get(CONFIG_PATH_ENV_VAR, str(DEFAULT_CONFIG_FILE_PATH)))


def main() -> None:

    bot = Bot(load_config(get_config_path()))
    bot.run()


if __name__ == "__main__":
    main()
