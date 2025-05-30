import logging

import sentry_sdk
from config import Config

# Set up standard logging
logger = logging.getLogger("Bot")
logger.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter("[%(levelname)s] %(asctime)s - %(message)s")
console_handler.setFormatter(formatter)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger.addHandler(console_handler)


def setup_sentry(config: Config) -> None:
    try:
        sentry_sdk.init(
            dsn=config.providers.sentry.dsn,
            traces_sample_rate=1.0,
            send_default_pii=True,
        )
        logger.info("Sentry initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Sentry: {e}")
