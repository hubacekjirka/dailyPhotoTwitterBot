import io
from collections.abc import Callable, Mapping
from functools import cached_property
from typing import Any, Optional, Sequence, cast

from config import AwsProvider, GcpProvider
from exceptions import PictureResizeError
from handlers.gcp_handler import GcpHandler
from handlers.rekognition_handler import RekognitionHandler
from logger import logger
from PIL import Image as Image

from core.custom_types import GeoCoordinates, Label

ExifData = Mapping[int, Any]


class Picture:
    def __init__(
        self, picture_bytes: bytes, picture_path: str, aws_config: AwsProvider, gcp_config: GcpProvider
    ) -> None:
        self.picture_bytes = picture_bytes
        self.picture_path = picture_path
        self.aws_config = aws_config
        self.gcp_config = gcp_config

    def _read_exif(self) -> ExifData | None:
        img = Image.open(io.BytesIO(self.picture_bytes))
        get_exif = cast(Callable[[], ExifData | None] | None, getattr(img, "_getexif", None))
        if get_exif is None:
            return None
        return get_exif()

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
    def camera_model(self) -> str | None:
        try:
            exif_data = self._read_exif()
            if not exif_data:
                logger.warning("No camera model or make EXIF data found in the image.")
                return None

            value = exif_data.get(272) or exif_data.get(271)
            return str(value) if value is not None else None

        except AttributeError:
            logger.warning("No camera model or make EXIF data found in the image.")
            return None

        except Exception as e:
            logger.warning(f"Couldn't get camera from exif: {e}")
            return None

    @cached_property
    def _exif_geo_coordinates(self) -> GeoCoordinates | None:
        """
        Extracts GPS coordinates from the picture's EXIF data.
        :return: A tuple of (latitude, longitude) if available, otherwise None.
        """
        try:
            exif_data = self._read_exif()
            if not exif_data:
                return None

            gps_info = exif_data.get(34853)
            if gps_info:
                lat_direction = gps_info.get(1)
                lat_dms = gps_info.get(2)
                lon_direction = gps_info.get(3)
                lon_dms = gps_info.get(4)
                if lat_dms and lon_dms and lat_direction and lon_direction:
                    lat = float(lat_dms[0] + lat_dms[1] / 60 + lat_dms[2] / 3600)
                    lat = -lat if lat_direction == "S" else lat

                    long = float(lon_dms[0] + lon_dms[1] / 60 + lon_dms[2] / 3600)
                    long = -long if lon_direction == "W" else long

                    return GeoCoordinates(lat, long)

        except Exception as e:
            logger.warning(f"Couldn't get GPS coordinates from EXIF data: {e}")

        return None

    @cached_property
    def place(self) -> Optional[str]:
        if not self.gcp_config.enabled or not self._exif_geo_coordinates:
            return None

        gcp_handler = GcpHandler(self.gcp_config.api_token)
        return gcp_handler.get_reverse_geolocation(self._exif_geo_coordinates)

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
