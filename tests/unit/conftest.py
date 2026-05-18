from pathlib import Path
from typing import Callable, TypeVar, cast

import pytest
from config import AwsProvider, BskyProvider, Config, GcpProvider, SentryProvider, TelegramProvider, load_config
from PIL import Image

FixtureFunc = TypeVar("FixtureFunc", bound=Callable[..., object])
fixture = cast(Callable[[FixtureFunc], FixtureFunc], pytest.fixture)


@fixture
def ut_config() -> Config:
    ut_config_path = Path(__file__).parent / "ut_config.yaml"
    return load_config(ut_config_path)


@fixture
def sentry_config() -> SentryProvider:
    return SentryProvider(enabled=True, dsn="dsn")


@fixture
def aws_config() -> AwsProvider:
    return AwsProvider(
        region="eu-west-1",
        bucket="bucket",
        access_key_id="access-key",
        secret_access_key="secret-key",
        backlog_folder="backlog",
        archive_folder="archive",
    )


@fixture
def bsky_config() -> BskyProvider:
    return BskyProvider(enabled=True, login="user.example", bsky_password="password")


@fixture
def telegram_config() -> TelegramProvider:
    return TelegramProvider(enabled=True, telegram_token="token", chat_ids=[1001, 1002])


@fixture
def gcp_config() -> GcpProvider:
    return GcpProvider(enabled=True, api_token="gcp-token")


@fixture
def image_bytes_factory() -> Callable[..., bytes]:
    def make_image_bytes(size: tuple[int, int] = (20, 20), image_format: str = "JPEG") -> bytes:
        from io import BytesIO

        image = Image.new("RGB", size, color=(20, 80, 140))
        buffer = BytesIO()
        image.save(buffer, format=image_format)
        return buffer.getvalue()

    return make_image_bytes
