from atproto import Client
from config import BskyProvider
from services.metadata import Metadata
from utils import compress_image_to_limit

from app.services.social_handler import SocialHandler


class Bsky_handler(SocialHandler):
    MAX_PICTURE_SIZE = 976 * 1024  # 976 KB

    def __init__(self, bsky_config: BskyProvider) -> None:
        try:
            self.client = Client()
            self.profile = self.client.login(bsky_config.login, bsky_config.bsky_password)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Bluesky client: {e}") from e

    def post_picture(self, picture: bytes, metadata: Metadata) -> None:
        if len(picture) > self.MAX_PICTURE_SIZE:
            picture = compress_image_to_limit(picture, self.MAX_PICTURE_SIZE)

        hashtags = [
            f"{str(int(tag['Confidence']))}% #{tag['Name']}"
            for tag in metadata.get("content_prediction", [])
            if tag["Confidence"] > 50
        ][:5]
        hashtags_text = ", ".join(hashtags) if hashtags else ""
        camera_model = metadata.get("camera")
        text = (
            "#photoOfTheDay bot."
            + (f" Shot on {camera_model}" if camera_model else "")
            + (f", AWS Rekognition sees {hashtags_text}" if hashtags_text else "")
            + " | Sent with ❤️"
        )

        self.client.send_image(text=text, image=picture, image_alt=text)
