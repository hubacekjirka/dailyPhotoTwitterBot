from config import CONFIG
from core.bot import Bot


def main() -> None:

    bot = Bot(CONFIG)
    bot.run()


if __name__ == "__main__":
    main()
