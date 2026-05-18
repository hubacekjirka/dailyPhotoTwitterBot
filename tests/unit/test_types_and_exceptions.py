import pytest
from core.custom_types import GeoCoordinates, Label
from exceptions import ConfigLoadError, PictureResizeError, S3ConfigError
from handlers.social_handler import SocialHandler


def test_custom_named_tuples_expose_expected_fields() -> None:
    label = Label(name="Forest", confidence=95)
    coordinates = GeoCoordinates(latitude=50.1, longitude=14.2)

    assert label.name == "Forest"
    assert label.confidence == 95
    assert coordinates.latitude == 50.1
    assert coordinates.longitude == 14.2


def test_custom_exceptions_can_be_raised() -> None:
    for exception_type in (ConfigLoadError, S3ConfigError, PictureResizeError):
        with pytest.raises(exception_type):
            raise exception_type("failure")


def test_social_handler_declares_abstract_contract() -> None:
    assert SocialHandler.__annotations__["MAX_PICTURE_SIZE"] is int
    assert SocialHandler.__annotations__["MAX_PICTURE_DIMENSION"] is int
    assert SocialHandler.__abstractmethods__ == {"__init__", "post_picture"}
