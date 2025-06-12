from atproto import Client
from config import BskyProvider
from utils import compress_image_to_limit


class Bsky_handler:
    MAX_PICTURE_SIZE = 976 * 1024  # 976 KB

    def __init__(self, bsky_config: BskyProvider) -> None:
        try:
            self.client = Client()
            self.profile = self.client.login(bsky_config.login, bsky_config.bsky_password)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Bluesky client: {e}") from e

    def post_picture(self, picture: bytes) -> None:
        if len(picture) > self.MAX_PICTURE_SIZE:
            picture = compress_image_to_limit(picture, self.MAX_PICTURE_SIZE)

        self.client.send_image(text="Oops", image=picture, image_alt="Right?")
