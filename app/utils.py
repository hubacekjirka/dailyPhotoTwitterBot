import io

from exceptions import PictureResizeError
from PIL import Image


def compress_image_to_limit(picture: bytes, max_size_bytes: int = 1_000_000) -> bytes:
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
            # logger.info(f"Compressed to {size / 1024:.2f} KB at quality {quality}")
            return buffer.read()
        quality -= 5

    raise PictureResizeError("Could not compress image to under 1MB.")
