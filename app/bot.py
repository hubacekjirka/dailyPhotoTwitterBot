from typing import Dict

from logger import logger


class Bot:
    def __init__(self, config: Dict[str, str]):
        logger.info("Bot started")
        self.config = config

    def run(self) -> None:
        pass
