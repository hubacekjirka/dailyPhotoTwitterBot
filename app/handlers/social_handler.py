from abc import ABC, abstractmethod

from config import BskyProvider, TelegramProvider
from core.picture import Picture


class SocialHandler(ABC):
    MAX_PICTURE_SIZE: int  # Should be set by subclasses
    MAX_PICTURE_DIMENSION: int  # Should be set by subclasses

    @abstractmethod
    def __init__(self, config: BskyProvider | TelegramProvider) -> None:
        pass

    @abstractmethod
    def post_picture(self, picture: Picture) -> None:
        pass
