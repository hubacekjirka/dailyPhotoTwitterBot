from config import Config
from logger import logger, setup_sentry


class Bot:

    def __init__(self, config: Config) -> None:
        logger.info("Bot started")
        self.config = config

        # Add Sentry handler if configured
        setup_sentry(self.config) if self.config.providers.sentry.enabled else None

    def run(self) -> None:

        logger.info("Bot is running")
        # Add your bot logic here

        # s3_handler = S3_handler(self.s3_config)
        # self.picture = s3_handler.get_random_file_as_binary(
        #     prefix=self.config["providers"]["s3"]["config"].get("backlog", "backlog")
        # )

        print("xxx")
