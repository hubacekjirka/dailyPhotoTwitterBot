import logging

import sentry_sdk
from config import CONFIG

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

sentry_provider = CONFIG["providers"].get("sentry")
if sentry_provider.get("enabled"):
    sentry_sdk.init(sentry_provider.get("api_key"), traces_sample_rate=1.0)
    logging.info("Sentry logging started")
else:
    logging.warning("Sentry logging not started")

logger.addHandler(console_handler)
