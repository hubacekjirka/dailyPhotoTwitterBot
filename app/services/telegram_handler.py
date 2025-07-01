import time

import requests
from config import TelegramProvider
from logger import logger

from services.picture import Picture
from services.social_handler import SocialHandler


class TelegramHandler(SocialHandler):

    MAX_PICTURE_SIZE = 20 * 1024 * 1024  # 20 MB
    MAX_PICTURE_DIMENSION = 5000  # 5000 pixels

    def __init__(self, config: TelegramProvider) -> None:
        self.config = config
        self.url = f"https://api.telegram.org/bot{self.config.telegram_token}/sendPhoto"

    def post_picture(self, picture: Picture) -> None:
        hashtags = None
        if picture.content_prediction:
            hashtags = [
                f"#{tag.name.replace(' ', '')} {tag.confidence}%"
                for tag in picture.content_prediction
                if tag.confidence > 50
            ][:5]
        hashtags_text = ", ".join(hashtags) if hashtags else ""

        text = (
            "#photoOfTheDay bot."
            + (f" Shot on {picture.camera_model}" if picture.camera_model else "")
            + (f", AWS Rekognition sees {hashtags_text}" if hashtags_text else "")
            + " | Sent with ❤️"
        )

        for chat_id in self.config.chat_ids:
            response = requests.post(
                self.url,
                data={"chat_id": chat_id, "caption": text},
                files={
                    "photo": picture.compress_image(
                        max_size_bytes=self.MAX_PICTURE_SIZE, max_dimension=self.MAX_PICTURE_DIMENSION
                    )
                },
            )
            time.sleep(0.5)  # backoff a bit

            if response.status_code != 200:
                logger.error(f"Failed to send photo to chat_id {chat_id}: {response.text}")
