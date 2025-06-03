from config import Config
from logger import logger, setup_sentry

from app.services.s3_handler import S3_handler


class Bot:

    def __init__(self, config: Config) -> None:
        logger.info("Bot started")
        self.config = config

        # Add Sentry handler
        setup_sentry(self.config.providers.sentry)

    def run(self) -> None:

        logger.info("Bot is running")

        s3_handler = S3_handler(self.config.providers.s3)
        print(s3_handler)
        # self.picture = s3_handler.get_random_file_as_binary(
        #     prefix=self.config["providers"]["s3"]["config"].get("backlog", "backlog")
        # )

        print("xxx")
