from abc import ABC, abstractmethod

from config import BskyProvider, TelegramProvider
from services.metadata import Metadata


class SocialHandler(ABC):
    MAX_PICTURE_SIZE: int  # Should be set by subclasses

    @abstractmethod
    def __init__(self, config: BskyProvider | TelegramProvider) -> None:
        pass

    @abstractmethod
    def post_picture(self, picture: bytes, metadata: Metadata) -> None:
        pass
