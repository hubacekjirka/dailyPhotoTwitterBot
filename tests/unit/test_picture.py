from io import BytesIO
from typing import Any, Callable

import core.picture as picture_module
import pytest
from config import AwsProvider, GcpProvider
from core.custom_types import GeoCoordinates, Label
from exceptions import PictureResizeError
from PIL import Image


def make_picture(
    image_bytes: bytes,
    aws_config: AwsProvider,
    gcp_config: GcpProvider,
    picture_path: str = "backlog/photo.jpg",
) -> picture_module.Picture:
    return picture_module.Picture(
        picture_bytes=image_bytes,
        picture_path=picture_path,
        aws_config=aws_config,
        gcp_config=gcp_config,
    )


def test_content_prediction_uses_rekognition_once(
    monkeypatch: pytest.MonkeyPatch,
    image_bytes_factory: Callable[..., bytes],
    aws_config: AwsProvider,
    gcp_config: GcpProvider,
) -> None:
    labels = [Label(name="Tree", confidence=91)]
    calls: list[bytes] = []

    class FakeRekognitionHandler:
        def __init__(self, config: AwsProvider) -> None:
            assert config is aws_config

        def get_picture_content(self, picture_bytes: bytes) -> list[Label]:
            calls.append(picture_bytes)
            return labels

    monkeypatch.setattr(picture_module, "RekognitionHandler", FakeRekognitionHandler)
    image_bytes = image_bytes_factory()
    picture = make_picture(image_bytes, aws_config, gcp_config)

    assert picture.content_prediction == labels
    assert picture.content_prediction == labels
    assert calls == [image_bytes]


def test_content_prediction_returns_none_on_handler_error(
    monkeypatch: pytest.MonkeyPatch,
    image_bytes_factory: Callable[..., bytes],
    aws_config: AwsProvider,
    gcp_config: GcpProvider,
) -> None:
    class FailingRekognitionHandler:
        def __init__(self, config: AwsProvider) -> None:
            raise RuntimeError("rekognition unavailable")

    monkeypatch.setattr(picture_module, "RekognitionHandler", FailingRekognitionHandler)
    picture = make_picture(image_bytes_factory(), aws_config, gcp_config)

    assert picture.content_prediction is None


def test_camera_model_prefers_model_over_make(
    monkeypatch: pytest.MonkeyPatch,
    image_bytes_factory: Callable[..., bytes],
    aws_config: AwsProvider,
    gcp_config: GcpProvider,
) -> None:
    class FakeImage:
        def _getexif(self) -> dict[int, str]:
            return {271: "Camera Make", 272: "Camera Model"}

    monkeypatch.setattr(picture_module.Image, "open", lambda stream: FakeImage())
    picture = make_picture(image_bytes_factory(), aws_config, gcp_config)

    assert picture.camera_model == "Camera Model"


def test_camera_model_falls_back_to_make(
    monkeypatch: pytest.MonkeyPatch,
    image_bytes_factory: Callable[..., bytes],
    aws_config: AwsProvider,
    gcp_config: GcpProvider,
) -> None:
    class FakeImage:
        def _getexif(self) -> dict[int, str]:
            return {271: "Camera Make"}

    monkeypatch.setattr(picture_module.Image, "open", lambda stream: FakeImage())
    picture = make_picture(image_bytes_factory(), aws_config, gcp_config)

    assert picture.camera_model == "Camera Make"


def test_camera_model_returns_none_when_exif_missing(
    monkeypatch: pytest.MonkeyPatch,
    image_bytes_factory: Callable[..., bytes],
    aws_config: AwsProvider,
    gcp_config: GcpProvider,
) -> None:
    class FakeImage:
        def _getexif(self) -> None:
            return None

    monkeypatch.setattr(picture_module.Image, "open", lambda stream: FakeImage())
    picture = make_picture(image_bytes_factory(), aws_config, gcp_config)

    assert picture.camera_model is None


def test_camera_model_returns_none_when_image_open_fails(
    monkeypatch: pytest.MonkeyPatch,
    image_bytes_factory: Callable[..., bytes],
    aws_config: AwsProvider,
    gcp_config: GcpProvider,
) -> None:
    def raise_error(stream: BytesIO) -> None:
        raise OSError("invalid image")

    monkeypatch.setattr(picture_module.Image, "open", raise_error)
    picture = make_picture(image_bytes_factory(), aws_config, gcp_config)

    assert picture.camera_model is None


def test_exif_geo_coordinates_parse_north_east(
    monkeypatch: pytest.MonkeyPatch,
    image_bytes_factory: Callable[..., bytes],
    aws_config: AwsProvider,
    gcp_config: GcpProvider,
) -> None:
    class FakeImage:
        def _getexif(self) -> dict[int, dict[int, Any]]:
            return {34853: {1: "N", 2: (52, 30, 0), 3: "E", 4: (13, 24, 0)}}

    monkeypatch.setattr(picture_module.Image, "open", lambda stream: FakeImage())
    picture = make_picture(image_bytes_factory(), aws_config, gcp_config)

    assert picture._exif_geo_coordinates == GeoCoordinates(52.5, 13.4)


def test_exif_geo_coordinates_parse_south_west(
    monkeypatch: pytest.MonkeyPatch,
    image_bytes_factory: Callable[..., bytes],
    aws_config: AwsProvider,
    gcp_config: GcpProvider,
) -> None:
    class FakeImage:
        def _getexif(self) -> dict[int, dict[int, Any]]:
            return {34853: {1: "S", 2: (10, 15, 0), 3: "W", 4: (20, 30, 0)}}

    monkeypatch.setattr(picture_module.Image, "open", lambda stream: FakeImage())
    picture = make_picture(image_bytes_factory(), aws_config, gcp_config)

    assert picture._exif_geo_coordinates == GeoCoordinates(-10.25, -20.5)


def test_exif_geo_coordinates_returns_none_when_gps_missing(
    monkeypatch: pytest.MonkeyPatch,
    image_bytes_factory: Callable[..., bytes],
    aws_config: AwsProvider,
    gcp_config: GcpProvider,
) -> None:
    class FakeImage:
        def _getexif(self) -> dict[int, dict[int, Any]]:
            return {}

    monkeypatch.setattr(picture_module.Image, "open", lambda stream: FakeImage())
    picture = make_picture(image_bytes_factory(), aws_config, gcp_config)

    assert picture._exif_geo_coordinates is None


def test_exif_geo_coordinates_returns_none_on_error(
    monkeypatch: pytest.MonkeyPatch,
    image_bytes_factory: Callable[..., bytes],
    aws_config: AwsProvider,
    gcp_config: GcpProvider,
) -> None:
    def raise_error(stream: BytesIO) -> None:
        raise OSError("invalid image")

    monkeypatch.setattr(picture_module.Image, "open", raise_error)
    picture = make_picture(image_bytes_factory(), aws_config, gcp_config)

    assert picture._exif_geo_coordinates is None


def test_place_returns_none_when_gcp_disabled(
    monkeypatch: pytest.MonkeyPatch,
    image_bytes_factory: Callable[..., bytes],
    aws_config: AwsProvider,
) -> None:
    disabled_gcp_config = GcpProvider(enabled=False, api_token="gcp-token")
    picture = make_picture(image_bytes_factory(), aws_config, disabled_gcp_config)
    picture.__dict__["_exif_geo_coordinates"] = GeoCoordinates(1.0, 2.0)

    def fail_if_called(api_token: str) -> None:
        raise AssertionError("GcpHandler should not be instantiated")

    monkeypatch.setattr(picture_module, "GcpHandler", fail_if_called)

    assert picture.place is None


def test_place_returns_none_without_coordinates(
    monkeypatch: pytest.MonkeyPatch,
    image_bytes_factory: Callable[..., bytes],
    aws_config: AwsProvider,
    gcp_config: GcpProvider,
) -> None:
    class FakeImage:
        def _getexif(self) -> dict[int, dict[int, Any]]:
            return {}

    monkeypatch.setattr(picture_module.Image, "open", lambda stream: FakeImage())
    picture = make_picture(image_bytes_factory(), aws_config, gcp_config)

    assert picture.place is None


def test_place_uses_reverse_geolocation(
    monkeypatch: pytest.MonkeyPatch,
    image_bytes_factory: Callable[..., bytes],
    aws_config: AwsProvider,
    gcp_config: GcpProvider,
) -> None:
    coordinates = GeoCoordinates(50.0, 14.0)
    received_coordinates: list[GeoCoordinates] = []

    class FakeGcpHandler:
        def __init__(self, api_token: str) -> None:
            assert api_token == gcp_config.api_token

        def get_reverse_geolocation(self, coords: GeoCoordinates) -> str:
            received_coordinates.append(coords)
            return "Prague, Czechia"

    monkeypatch.setattr(picture_module, "GcpHandler", FakeGcpHandler)
    picture = make_picture(image_bytes_factory(), aws_config, gcp_config)
    picture.__dict__["_exif_geo_coordinates"] = coordinates

    assert picture.place == "Prague, Czechia"
    assert received_coordinates == [coordinates]


def test_compress_image_returns_original_when_within_limits(
    image_bytes_factory: Callable[..., bytes],
    aws_config: AwsProvider,
    gcp_config: GcpProvider,
) -> None:
    image_bytes = image_bytes_factory((20, 20), "JPEG")
    picture = make_picture(image_bytes, aws_config, gcp_config)

    assert picture.compress_image(max_size_bytes=len(image_bytes) + 1, max_dimension=100) == image_bytes


def test_compress_image_downscales_when_dimensions_are_too_large(
    image_bytes_factory: Callable[..., bytes],
    aws_config: AwsProvider,
    gcp_config: GcpProvider,
) -> None:
    image_bytes = image_bytes_factory((100, 60), "JPEG")
    picture = make_picture(image_bytes, aws_config, gcp_config)

    compressed = picture.compress_image(max_size_bytes=1_000_000, max_dimension=10)

    with Image.open(BytesIO(compressed)) as image:
        assert max(image.size) <= 10


def test_compress_image_raises_when_quality_reduction_cannot_meet_limit(
    monkeypatch: pytest.MonkeyPatch,
    aws_config: AwsProvider,
    gcp_config: GcpProvider,
) -> None:
    class NeverSmallEnoughImage:
        size = (100, 100)

        def thumbnail(self, size: tuple[int, int]) -> None:
            self.size = size

        def save(self, buffer: BytesIO, format: str, quality: int) -> None:
            buffer.write(b"x" * 100)

    monkeypatch.setattr(picture_module.Image, "open", lambda stream: NeverSmallEnoughImage())
    picture = make_picture(b"too-large", aws_config, gcp_config)

    with pytest.raises(PictureResizeError, match="Could not compress image"):
        picture.compress_image(max_size_bytes=1, max_dimension=10)
