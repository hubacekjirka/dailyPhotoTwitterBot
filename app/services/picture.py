import io
from functools import cached_property
from typing import Optional, Sequence

from config import AwsProvider
from exceptions import PictureResizeError
from logger import logger
from PIL import Image

from services.rekognition_handler import Label, RekognitionHandler


class Picture:
    def __init__(self, picture_bytes: bytes, picture_path: str, aws_config: AwsProvider) -> None:
        self.picture_bytes = picture_bytes
        self.picture_path = picture_path
        self.aws_config = aws_config

    @cached_property
    def content_prediction(self) -> Optional[Sequence["Label"]]:
        """
        Uses AWS Rekognition to analyze the picture and return content predictions.
        :return: A sequence of Label NamedTuples containing label names and confidence scores,
                 or None if the analysis fails.
        """
        try:
            rekognition_handler = RekognitionHandler(self.aws_config)
            if content_prediction := rekognition_handler.get_picture_content(self.picture_bytes):
                return content_prediction
        except Exception as e:
            logger.error(f"Failed to get picture content: {e}")
        return None

    @cached_property
    def camera_model(self) -> Optional[str]:
        try:
            img = Image.open(io.BytesIO(self.picture_bytes))
            exif_data = img._getexif()

            value = exif_data.get(272) or exif_data.get(271)
            return str(value) if value is not None else None

        except AttributeError:
            logger.warning("No camera model or make EXIF data found in the image.")
            return None

        except Exception as e:
            logger.warning(f"Couldn't get camera from exif: {e}")
            return None

    def compress_image(self, max_size_bytes: int, max_dimension: int) -> bytes:
        """
        Compresses an image to fit within a specified size limit.
        :param picture: The binary content of the picture.
        :param max_size_bytes: The maximum size in bytes for the compressed image.
        :return: The compressed image as bytes.
        :raises PictureResizeError: If the image cannot be compressed to fit within the size limit.
        """
        img = Image.open(io.BytesIO(self.picture_bytes))

        if len(self.picture_bytes) <= max_size_bytes and max(img.size) <= max_dimension:
            logger.debug("Image is already within size limit and dimension, no compression  downscaling needed.")
            return self.picture_bytes

        # Downsize if necessary
        if max(img.size) > max_dimension:
            img.thumbnail((max_dimension, max_dimension))

        # Compress by reducing JPEG quality
        quality = 95
        while quality > 10:
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=quality)
            size = buffer.tell()
            if size <= max_size_bytes:
                buffer.seek(0)
                logger.debug(f"Compressed to {size / 1024:.2f} KB at quality {quality}")
                return buffer.read()
            quality -= 5

        raise PictureResizeError(f"Could not compress image to under {max_size_bytes / 1024 / 1024} MB.")
