from typing import Any, Dict

from core.exceptions import S3ConfigError
from core.logger import logger
from services.s3_handler import S3_handler


class Bot:

    def __init__(self, config: Dict[str, Any]) -> None:
        logger.info("Bot started")
        self.config = config

        # Load S3 configuration
        try:
            self.s3_config = self.config["providers"]["s3"]["config"]
        except KeyError as e:
            raise S3ConfigError("Missing S3 configuration keys") from e

    def run(self) -> None:

        logger.info("Bot is running")
        # Add your bot logic here

        s3_handler = S3_handler(self.s3_config)
        self.picture = s3_handler.get_random_file_as_binary(
            prefix=self.config["providers"]["s3"]["config"].get("backlog", "backlog")
        )

        print("xxx")
