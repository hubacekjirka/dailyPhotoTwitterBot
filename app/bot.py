from config import Config
from logger import logger, setup_sentry
from services.bsky_handler import BskyHandler
from services.picture import Picture
from services.s3_handler import S3Handler
from services.telegram_handler import TelegramHandler


class Bot:

    def __init__(self, config: Config) -> None:
        logger.info("Bot started")
        self.config = config

        # Add Sentry handler
        setup_sentry(self.config.providers.sentry)

    def run(self) -> None:
        logger.info("Bot is running")

        self.s3_handler = S3Handler(self.config.providers.aws)

        logger.info("Retrieving random file from S3")
        picture_bytes, picture_path = self.s3_handler.get_random_file()
        self.picture = Picture(
            picture_bytes=picture_bytes, picture_path=picture_path, aws_config=self.config.providers.aws
        )

        #### Let's start the posting sharade
        # Bluesky
        if self.config.providers.bsky.enabled:
            logger.info("Posting to Bluesky")
            try:
                bsky_handler = BskyHandler(self.config.providers.bsky)
                bsky_handler.post_picture(self.picture)
            except Exception as e:
                logger.error(f"Failed to post to Bluesky: {e}")
        else:
            logger.warning("Bluesky provider is disabled, skipping posting")

        # Telegram
        if self.config.providers.telegram.enabled:
            logger.info("Posting to Telegram")
            try:
                telegram_handler = TelegramHandler(self.config.providers.telegram)
                telegram_handler.post_picture(self.picture)
            except Exception as e:
                logger.warning(f"Failed to post to Telegram: {e}")

        # Move picture to S3 archive folder
        if self.config.providers.bsky.enabled or self.config.providers.telegram.enabled:
            logger.info("Moving picture to S3 archive folder")
            try:
                self.s3_handler.move_to_archive(self.picture.picture_path)
            except Exception as e:
                logger.error(f"Failed to move picture to S3 archive: {e}")
        else:
            logger.warning("No providers enabled, skipping moving picture to archive")

        logger.info("Bot run completed successfully")
