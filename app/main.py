from bot import Bot
from config import CONFIG


def main() -> None:

    bot = Bot(CONFIG)
    print(bot)


if __name__ == "__main__":
    main()
