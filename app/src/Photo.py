from PIL import Image
from PIL.ExifTags import TAGS
import os
import PIL.Image

# from classify_image import classifyImage
import logging
import boto3
from config import awsAccessKey, awsKeyId

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel("DEBUG")


class Photo:
    """
    Photo class
    """

    def __init__(self, photoPath):
        LOGGER.debug(f"Picked file: {photoPath}")
        self.photoPath = photoPath
        self.fileName = os.path.basename(photoPath)
        self.resize()
        self.exifData = self.getExif()
        # self.exifHashtags = self.getExifHashtags()
        self.tensorFlowHashtags = self.get_content_hash_tag_prediction()

    def getExif(self):
        img = PIL.Image.open(self.photoPath)
        if img._getexif() is None:
            LOGGER.debug("No exif data found")
            return {}

        LOGGER.debug(f"Raw exif tags: {img._getexif().items()}")

        exif = {TAGS[k]: v for k, v in img._getexif().items() if k in PIL.ExifTags.TAGS}
        LOGGER.debug(f"Exif tags: {exif}")

        return exif

    def getExifHashtags(self):
        hashtags = []
        hashtags.append("")

        if self.exifData.get("Model"):
            hashtags.append(f"#{self.exifData.get('Model').replace(' ','')}")

        exifHashtags = f"{' '.join(hashtags)}"
        return exifHashtags

    def resize(self):
        # keep resizing until the file is smaller than 3MB and 8192px
        #     => Twitter's API limit
        while (
            os.path.getsize(self.photoPath) >= 3 * 1024 * 1024
            or Image.open(self.photoPath).size[0] > 8192
            or Image.open(self.photoPath).size[1] > 8192
        ):

            img = Image.open(self.photoPath)
            LOGGER.debug(
                f"Resizing to {img.size[0] * 0.75} x {round(img.size[1] * 0.75)}"
            )
            resizedImg = img.resize(
                (round(img.size[0] * 0.75), round(img.size[1] * 0.75)),
                resample=PIL.Image.LANCZOS,
            )
            resizedImg.save(self.photoPath, exif=img.info["exif"])

    def get_content_hash_tag_prediction(self):
        """
        Call AWS Rekognition service to retrieve image content prediction
        """
        output = "AWS #rekognition sees: "

        try:
            client = boto3.client(
                "rekognition",
                aws_access_key_id=awsAccessKey,
                aws_secret_access_key=awsKeyId,
                region_name="us-east-1",
            )

            with open(self.photoPath, "rb") as photo:
                photo_bytes = photo.read()

            response = client.detect_labels(
                Image={"Bytes": photo_bytes}, MinConfidence=90
            )
            tags = [f"#{t['Name'].lower()}" for t in response["Labels"]]
            LOGGER.debug(f"Rekognition detected the following labels: {tags}")

            return output + f"{' '.join(tags)}"

        except Exception as e:
            LOGGER.error(f"Something went wrong during running Rekognition: {e}")
