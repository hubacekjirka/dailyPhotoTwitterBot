from bot import Bot
from config import CONFIG


def main():

    bot = Bot(CONFIG)
    bot.process_images()


if __name__ == "__main__":
    main()
