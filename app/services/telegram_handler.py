import time

import requests
from config import TelegramProvider
from logger import logger
from services.metadata import Metadata

# from services.social_handler import SocialHandler
from utils import compress_image_to_limit


class TelegramHandler:

    MAX_PICTURE_SIZE = 20 * 1024 * 1024  # 20 MB

    def __init__(self, config: TelegramProvider) -> None:
        self.config = config

    def post_picture(self, picture: bytes, metadata: Metadata) -> None:
        url = f"https://api.telegram.org/bot{self.config.telegram_token}/sendPhoto"
        if len(picture) > self.MAX_PICTURE_SIZE:
            picture = compress_image_to_limit(picture, self.MAX_PICTURE_SIZE)

        hashtags = [
            f"{str(int(tag['Confidence']))}% #{tag['Name']}"
            for tag in metadata.get("content_prediction", [])
            if tag["Confidence"] > 50
        ][:5]
        hashtags_text = ", ".join(hashtags) if hashtags else ""
        camera_model = metadata["camera"]
        text = (
            "#photoOfTheDay bot."
            + (f" Shot on {camera_model}" if camera_model else "")
            + (f", AWS Rekognition sees {hashtags_text}" if hashtags_text else "")
            + " | Sent with ❤️"
        )

        for chat_id in self.config.chat_ids:
            response = requests.post(url, data={"chat_id": chat_id, "caption": text}, files={"photo": picture})
            time.sleep(0.5)  # backoff a bit

            if response.status_code != 200:
                logger.error(f"Failed to send photo to chat_id {chat_id}: {response.text}")
