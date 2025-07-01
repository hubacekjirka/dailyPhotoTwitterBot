from atproto import Client
from config import BskyProvider

from services.picture import Picture
from services.social_handler import SocialHandler


class BskyHandler(SocialHandler):
    MAX_PICTURE_SIZE = 976 * 1024  # 976 KB
    MAX_PICTURE_DIMENSION = 2000  # 2000 pixels

    def __init__(self, bsky_config: BskyProvider) -> None:
        try:
            self.client = Client()
            self.profile = self.client.login(bsky_config.login, bsky_config.bsky_password)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Bluesky client: {e}") from e

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

        self.client.send_image(
            text=text,
            image=picture.compress_image(
                max_size_bytes=self.MAX_PICTURE_SIZE, max_dimension=self.MAX_PICTURE_DIMENSION
            ),
            image_alt=text,
        )
