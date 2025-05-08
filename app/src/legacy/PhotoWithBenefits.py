from PIL import Image
from PIL.ExifTags import TAGS
import os
import PIL.Image

# from classify_image import classifyImage
import logging
import boto3
from config import aws_access_key, aws_key_id

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel("DEBUG")


class PhotoWithBenefits:
    """
    Photo class
    """

    def __init__(self, photo_path, **kwargs):
        LOGGER.info(f"Picked file: {photo_path}")
        self._file_path = photo_path
        self._file_name = os.path.basename(photo_path)
        self._resize()
        self._exif = self._get_exif()
        self._content_prediction_hashtags = self._get_content_hashtags()
        self._throwback_thursday = kwargs.get("throwback_thursday", False)
        self._throwback_everyday = kwargs.get("throwback_everyday", False)

    def _get_exif(self):
        img = PIL.Image.open(self._file_path)
        if img._getexif() is None:
            LOGGER.debug("No exif data found")
            return {}

        LOGGER.debug(f"Raw exif tags: {img._getexif().items()}")

        exif = {TAGS[k]: v for k, v in img._getexif().items() if k in PIL.ExifTags.TAGS}
        LOGGER.debug(f"Exif tags: {exif}")

        return exif

    def _get_exif_hashtags(self):
        hashtags = []
        hashtags.append("")

        if self._exif.get("Model"):
            hashtags.append(f"#{self._exif.get('Model').replace(' ','')}")

        exif_hashtags = f"{' '.join(hashtags)}"
        return exif_hashtags

    def _resize(self):
        # keep resizing until the file is smaller than 3MB and 8192px
        #     => Twitter's API limit
        #       also x+y must be less than 10000 for Telegram
        while (
            os.path.getsize(self._file_path) >= 1 * 1024 * 1024
            or Image.open(self._file_path).size[0] > 8192
            or Image.open(self._file_path).size[1] > 8192
            or Image.open(self._file_path).size[0] + Image.open(self._file_path).size[1]
            > 10000
        ):

            img = Image.open(self._file_path)
            LOGGER.debug(
                f"Resizing to {img.size[0] * 0.75} x {round(img.size[1] * 0.75)}"
            )
            resizedImg = img.resize(
                (round(img.size[0] * 0.75), round(img.size[1] * 0.75)),
                resample=PIL.Image.LANCZOS,
            )
            resizedImg.save(self._file_path, exif=img.info["exif"])

    def _get_content_hashtags(self) -> list:
        """
        Call AWS Rekognition service to retrieve image content prediction
        """
        output = "AWS #rekognition sees: "

        try:
            client = boto3.client(
                "rekognition",
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_key_id,
                region_name="us-east-1",
            )

            with open(self._file_path, "rb") as photo:
                photo_bytes = photo.read()

            response = client.detect_labels(Image={"Bytes": photo_bytes})
            tags = [
                f"{round(t['Confidence'],0):.0f}% #{t['Name'].replace(' ', '')}"
                for t in response["Labels"]
            ]
            LOGGER.debug(f"Rekognition detected the following labels: {tags}")

            return tags

        except Exception as e:
            LOGGER.error(f"Something went wrong during running Rekognition: {e}")
