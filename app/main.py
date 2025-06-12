from pathlib import Path

from bot import Bot
from config import load_config

CONFIG_FILE_PATH = Path("app", "config.yaml")


def main() -> None:

    bot = Bot(load_config(CONFIG_FILE_PATH))
    bot.run()


if __name__ == "__main__":
    main()
