import io
from venv import logger

from exceptions import PictureResizeError
from PIL import Image


def compress_image_to_limit(picture: bytes, max_size_bytes: int = 1_000_000) -> bytes:
    """
    Compresses an image to fit within a specified size limit.
    :param picture: The binary content of the picture.
    :param max_size_bytes: The maximum size in bytes for the compressed image.
    :return: The compressed image as bytes.
    :raises PictureResizeError: If the image cannot be compressed to fit within the size limit.
    """
    img = Image.open(io.BytesIO(picture))

    # Downsize if necessary
    max_dimension = 2000
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

    raise PictureResizeError("Could not compress image to under 1MB.")


def get_camera_from_exif(picture: bytes) -> str | None:
    """
    Extracts the camera model from the EXIF data of a picture.
    Camera model (272) takes precendence over camera make (271).
    If neither is found, returns None.
    :raises Exception: If there is an issue reading the EXIF data.
    :param picture: The binary content of the picture.
    :return: The camera model as a string, or None if not found.
    """
    try:
        img = Image.open(io.BytesIO(picture))
        exif_data = img._getexif()

        value = exif_data.get(272) or exif_data.get(271)
        return str(value) if value is not None else None

    except AttributeError:
        logger.warning("No camera model or make EXIF data found in the image.")
        return None

    except Exception as e:
        logger.warning(f"Couldn't get camera from exif: {e}")
        return None
