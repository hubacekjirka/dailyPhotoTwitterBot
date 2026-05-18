from typing import Any, Iterator, TypedDict, cast

import pytest
from config import BskyProvider, TelegramProvider
from core.custom_types import GeoCoordinates, Label
from core.picture import Picture
from handlers import bsky_handler, gcp_handler, telegram_handler


class TelegramPostCall(TypedDict):
    url: str
    data: dict[str, object]
    files: dict[str, bytes]


class FakeResponse:
    def __init__(self, status_code: int, data: dict[str, Any] | None = None, text: str = "") -> None:
        self.status_code = status_code
        self.data = data or {}
        self.text = text

    def json(self) -> dict[str, Any]:
        return self.data


def test_gcp_reverse_geolocation_returns_locality(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[dict[str, object]] = []

    def fake_get(url: str, params: dict[str, str]) -> FakeResponse:
        calls.append({"url": url, "params": params})
        return FakeResponse(
            200,
            {
                "results": [
                    {"types": ["administrative_area_level_1", "political"], "formatted_address": "State"},
                    {"types": ["locality", "political"], "formatted_address": "City"},
                ]
            },
        )

    monkeypatch.setattr(gcp_handler.requests, "get", fake_get)

    result = gcp_handler.GcpHandler("token").get_reverse_geolocation(GeoCoordinates(50.1, 14.2))

    assert result == "City"
    assert calls == [
        {
            "url": "https://maps.googleapis.com/maps/api/geocode/json",
            "params": {"key": "token", "latlng": "50.1,14.2"},
        }
    ]


def test_gcp_reverse_geolocation_falls_back_to_state(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        gcp_handler.requests,
        "get",
        lambda url, params: FakeResponse(
            200,
            {"results": [{"types": ["administrative_area_level_1", "political"], "formatted_address": "State"}]},
        ),
    )

    result = gcp_handler.GcpHandler("token").get_reverse_geolocation(GeoCoordinates(50.1, 14.2))

    assert result == "State"


def test_gcp_reverse_geolocation_returns_none_without_matching_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        gcp_handler.requests,
        "get",
        lambda url, params: FakeResponse(200, {"results": [{"types": ["country"], "formatted_address": "Country"}]}),
    )

    result = gcp_handler.GcpHandler("token").get_reverse_geolocation(GeoCoordinates(50.1, 14.2))

    assert result is None


def test_gcp_reverse_geolocation_returns_none_on_http_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(gcp_handler.requests, "get", lambda url, params: FakeResponse(500, text="server error"))

    result = gcp_handler.GcpHandler("token").get_reverse_geolocation(GeoCoordinates(50.1, 14.2))

    assert result is None


def test_gcp_reverse_geolocation_returns_none_on_request_exception(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def raise_request_error(url: str, params: dict[str, str]) -> None:
        raise gcp_handler.requests.exceptions.RequestException("network")

    monkeypatch.setattr(gcp_handler.requests, "get", raise_request_error)

    result = gcp_handler.GcpHandler("token").get_reverse_geolocation(GeoCoordinates(50.1, 14.2))

    assert result is None


def test_bsky_handler_logs_in(monkeypatch: pytest.MonkeyPatch, bsky_config: BskyProvider) -> None:
    class FakeClient:
        def __init__(self) -> None:
            self.login_calls: list[tuple[str, str]] = []

        def login(self, login: str, password: str) -> str:
            self.login_calls.append((login, password))
            return "profile"

    fake_client = FakeClient()
    monkeypatch.setattr(bsky_handler, "Client", lambda: fake_client)

    handler = bsky_handler.BskyHandler(bsky_config)

    assert handler.client is fake_client
    assert handler.profile == "profile"
    assert fake_client.login_calls == [("user.example", "password")]


def test_bsky_handler_wraps_login_errors(monkeypatch: pytest.MonkeyPatch, bsky_config: BskyProvider) -> None:
    class FailingClient:
        def login(self, login: str, password: str) -> None:
            raise ValueError("bad login")

    monkeypatch.setattr(bsky_handler, "Client", FailingClient)

    with pytest.raises(RuntimeError, match="Failed to initialize Bluesky client"):
        bsky_handler.BskyHandler(bsky_config)


def test_bsky_post_picture_sends_compressed_image_with_metadata() -> None:
    class FakeClient:
        def __init__(self) -> None:
            self.sent_images: list[dict[str, object]] = []

        def send_image(self, **kwargs: object) -> None:
            self.sent_images.append(kwargs)

    class FakePicture:
        content_prediction = [
            Label("Blue Sky", 90),
            Label("Too Low", 50),
            Label("Tree", 70),
            Label("Cloud", 65),
            Label("Mountain", 64),
            Label("Lake", 63),
            Label("Ignored Sixth", 62),
        ]
        camera_model = "Camera Model"
        place = "Prague"

        def __init__(self) -> None:
            self.compress_calls: list[dict[str, int]] = []

        def compress_image(self, max_size_bytes: int, max_dimension: int) -> bytes:
            self.compress_calls.append({"max_size_bytes": max_size_bytes, "max_dimension": max_dimension})
            return b"compressed"

    fake_client = FakeClient()
    handler = bsky_handler.BskyHandler.__new__(bsky_handler.BskyHandler)
    handler.client = fake_client
    picture = FakePicture()

    handler.post_picture(cast(Picture, picture))

    assert picture.compress_calls == [{"max_size_bytes": 976 * 1024, "max_dimension": 2000}]
    assert fake_client.sent_images[0]["image"] == b"compressed"
    text = str(fake_client.sent_images[0]["text"])
    assert "#photoOfTheDay shot on Camera Model taken in Prague" in text
    assert "#BlueSky 90%" in text
    assert "#TooLow" not in text
    assert "#IgnoredSixth" not in text
    assert fake_client.sent_images[0]["image_alt"] == fake_client.sent_images[0]["text"]


def test_bsky_post_picture_handles_missing_optional_metadata() -> None:
    class FakeClient:
        def __init__(self) -> None:
            self.sent_images: list[dict[str, object]] = []

        def send_image(self, **kwargs: object) -> None:
            self.sent_images.append(kwargs)

    class FakePicture:
        content_prediction = None
        camera_model = None
        place = None

        def compress_image(self, max_size_bytes: int, max_dimension: int) -> bytes:
            return b"compressed"

    fake_client = FakeClient()
    handler = bsky_handler.BskyHandler.__new__(bsky_handler.BskyHandler)
    handler.client = fake_client

    handler.post_picture(cast(Picture, FakePicture()))

    assert "shot on" not in str(fake_client.sent_images[0]["text"])
    assert "AWS Rekognition sees" not in str(fake_client.sent_images[0]["text"])


def test_telegram_handler_posts_to_each_chat_and_logs_non_200(
    monkeypatch: pytest.MonkeyPatch, telegram_config: TelegramProvider
) -> None:
    responses: Iterator[FakeResponse] = iter([FakeResponse(200, text="ok"), FakeResponse(500, text="failed")])
    post_calls: list[TelegramPostCall] = []
    sleep_calls: list[float] = []

    def fake_post(url: str, data: dict[str, object], files: dict[str, bytes]) -> FakeResponse:
        post_calls.append({"url": url, "data": data, "files": files})
        return next(responses)

    class FakePicture:
        content_prediction = [Label("Forest Trail", 88), Label("Low", 50)]
        camera_model = "Camera"
        place = "Berlin"

        def compress_image(self, max_size_bytes: int, max_dimension: int) -> bytes:
            assert max_size_bytes == 20 * 1024 * 1024
            assert max_dimension == 5000
            return b"telegram-image"

    monkeypatch.setattr(telegram_handler.requests, "post", fake_post)
    monkeypatch.setattr(telegram_handler.time, "sleep", lambda seconds: sleep_calls.append(seconds))
    handler = telegram_handler.TelegramHandler(telegram_config)

    handler.post_picture(cast(Picture, FakePicture()))

    assert [call["url"] for call in post_calls] == [
        "https://api.telegram.org/bottoken/sendPhoto",
        "https://api.telegram.org/bottoken/sendPhoto",
    ]
    assert [call["data"]["chat_id"] for call in post_calls] == [1001, 1002]
    assert "#ForestTrail 88%" in str(post_calls[0]["data"]["caption"])
    assert "#Low" not in str(post_calls[0]["data"]["caption"])
    assert [call["files"] for call in post_calls] == [{"photo": b"telegram-image"}, {"photo": b"telegram-image"}]
    assert sleep_calls == [0.5, 0.5]


def test_telegram_handler_handles_missing_optional_metadata(
    monkeypatch: pytest.MonkeyPatch, telegram_config: TelegramProvider
) -> None:
    post_calls: list[TelegramPostCall] = []

    def fake_post(url: str, data: dict[str, object], files: dict[str, bytes]) -> FakeResponse:
        post_calls.append({"url": url, "data": data, "files": files})
        return FakeResponse(200)

    class FakePicture:
        content_prediction = None
        camera_model = None
        place = None

        def compress_image(self, max_size_bytes: int, max_dimension: int) -> bytes:
            assert max_size_bytes == 20 * 1024 * 1024
            assert max_dimension == 5000
            return b"telegram-image"

    monkeypatch.setattr(telegram_handler.requests, "post", fake_post)
    monkeypatch.setattr(telegram_handler.time, "sleep", lambda seconds: None)
    handler = telegram_handler.TelegramHandler(telegram_config)

    assert handler.url == "https://api.telegram.org/bottoken/sendPhoto"
    handler.post_picture(cast(Picture, FakePicture()))

    captions = [str(call["data"]["caption"]) for call in post_calls]
    assert len(captions) == 2
    assert all(caption.startswith("#photoOfTheDay") for caption in captions)
    assert all("shot on" not in caption for caption in captions)
    assert all("AWS Rekognition sees" not in caption for caption in captions)
