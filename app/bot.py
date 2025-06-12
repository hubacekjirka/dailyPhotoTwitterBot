from config import Config
from logger import logger, setup_sentry
from services.bsky_handler import Bsky_handler
from services.rekognition_handler import RekognitionHandler
from services.s3_handler import S3Handler
from services.telegram_handler import TelegramHandler


class Bot:

    def __init__(self, config: Config) -> None:
        logger.info("Bot started")
        self.config = config

        # Add Sentry handler
        setup_sentry(self.config.providers.sentry)

        self.picture = None
        self.picture_path = None

    def run(self) -> None:

        logger.info("Bot is running")

        s3_handler = S3Handler(self.config.providers.aws)

        logger.info("Retrieving random file from S3")
        self.picture, self.picture_path = s3_handler.get_random_file()

        logger.info("Getting hashtags for the picture")
        rekognition_handler = RekognitionHandler(self.config.providers.aws)
        _ = rekognition_handler.get_picture_content(self.picture)

        # Let's start the posting sharade
        if self.config.providers.bsky.enabled:
            logger.info("Posting to Bluesky")
            try:
                bsky_handler = Bsky_handler(self.config.providers.bsky)
                bsky_handler.post_picture(self.picture)
            except Exception as e:
                logger.error(f"Failed to post to Bluesky: {e}")
        else:
            logger.info("Bluesky provider is disabled, skipping posting")

        if self.config.providers.telegram.enabled:
            logger.info("Posting to Telegram")
            try:
                telegram_handler = TelegramHandler(self.config.providers.telegram)
                telegram_handler.post_picture(self.picture)
            except Exception as e:
                logger.error(f"Failed to post to Telegram: {e}")
