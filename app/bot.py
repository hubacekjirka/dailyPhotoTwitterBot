from config import Config
from logger import logger, setup_sentry
from services.bsky_handler import Bsky_handler
from services.rekognition_handler import RekognitionHandler
from services.s3_handler import S3Handler
from services.telegram_handler import TelegramHandler
from utils import get_camera_from_exif


class Bot:

    def __init__(self, config: Config) -> None:
        logger.info("Bot started")
        self.config = config

        # Add Sentry handler
        setup_sentry(self.config.providers.sentry)

        self.picture = None
        self.picture_path = None
        self.metadata: dict[str, object] = {}

    def run(self) -> None:

        logger.info("Bot is running")

        s3_handler = S3Handler(self.config.providers.aws)

        logger.info("Retrieving random file from S3")
        self.picture, self.picture_path = s3_handler.get_random_file()

        logger.info("Getting picture content using Rekognition")
        rekognition_handler = RekognitionHandler(self.config.providers.aws)
        self.metadata["picture_content"] = rekognition_handler.get_picture_content(self.picture)

        logger.info("Getting camera model from exif data")
        if camera_model := get_camera_from_exif(self.picture):
            self.metadata["camera_model"] = camera_model

        #### Let's start the posting sharade
        # Bluesky
        if self.config.providers.bsky.enabled:
            logger.info("Posting to Bluesky")
            try:
                bsky_handler = Bsky_handler(self.config.providers.bsky)
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
                s3_handler.move_to_archive(self.picture_path)
            except Exception as e:
                logger.error(f"Failed to move picture to S3 archive: {e}")
        else:
            logger.warning("No providers enabled, skipping moving picture to archive")

        logger.info("Bot run completed successfully")
