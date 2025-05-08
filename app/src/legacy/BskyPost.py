from Post import Post
from PhotoWithBenefits import PhotoWithBenefits
from atproto import Client, client_utils
from config import (
    bsky_login,
    bsky_password,
)

import logging

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel("DEBUG")


class BskyPost(Post):
    def __init__(self, photo: PhotoWithBenefits):
        super().__init__(photo)
        self._api = self._get_api()
        
        self._bot_signature = "Bsky bot (Github: http://bit.ly/PotDGithub)"
        self._post_text = (
            f"{self._intro_text} "
            f"{self._exif_section} {self._bot_signature} "
            f"{', '.join(photo._content_prediction_hashtags[:5])}"
        )

    def _get_api(self) -> Client:
        client = Client()
        client.login(bsky_login, bsky_password)
        return client


    def post(self):
        if len(self._post_text) > 250:
            self._post_text = f"{self._post_text[:250]}..."

        kwargs = {}

        if self._post_text is not None:
            kwargs["status"] = self._post_text

        with open(self._photo._file_path, 'rb') as f:
            img_data = f.read()
            self._api.send_image(text=self._post_text, image=img_data, image_alt=self._post_text)
