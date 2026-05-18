from typing import Any

import pytest
from config import AwsProvider
from core.custom_types import Label
from handlers import rekognition_handler, s3_handler


class FakeBody:
    def __init__(self, data: bytes) -> None:
        self.data = data

    def read(self) -> bytes:
        return self.data


def make_s3_handler(config: AwsProvider, client: object) -> s3_handler.S3Handler:
    handler = s3_handler.S3Handler.__new__(s3_handler.S3Handler)
    handler.config = config
    handler.s3_client = client
    return handler


def test_s3_handler_initializes_boto_client(monkeypatch: pytest.MonkeyPatch, aws_config: AwsProvider) -> None:
    captured: dict[str, Any] = {}
    fake_client = object()

    def fake_boto_client(service_name: str, **kwargs: str) -> object:
        captured["service_name"] = service_name
        captured["kwargs"] = kwargs
        return fake_client

    monkeypatch.setattr(s3_handler.boto3, "client", fake_boto_client)

    handler = s3_handler.S3Handler(aws_config)

    assert handler.config is aws_config
    assert handler.s3_client is fake_client
    assert captured == {
        "service_name": "s3",
        "kwargs": {
            "aws_access_key_id": "access-key",
            "aws_secret_access_key": "secret-key",
            "region_name": "eu-west-1",
        },
    }


def test_s3_handler_wraps_boto_client_errors(monkeypatch: pytest.MonkeyPatch, aws_config: AwsProvider) -> None:
    def raise_error(*args: object, **kwargs: object) -> None:
        raise ValueError("bad credentials")

    monkeypatch.setattr(s3_handler.boto3, "client", raise_error)

    with pytest.raises(RuntimeError, match="Failed to initialize S3 client"):
        s3_handler.S3Handler(aws_config)


def test_get_random_file_filters_images_and_reads_selected_object(
    monkeypatch: pytest.MonkeyPatch, aws_config: AwsProvider
) -> None:
    class FakeS3Client:
        def __init__(self) -> None:
            self.list_calls: list[dict[str, str]] = []
            self.get_calls: list[dict[str, str]] = []

        def list_objects_v2(self, **kwargs: str) -> dict[str, list[dict[str, str]]]:
            self.list_calls.append(kwargs)
            return {
                "Contents": [
                    {"Key": "backlog/"},
                    {"Key": "backlog/readme.txt"},
                    {"Key": "backlog/photo.JPG"},
                    {"Key": "backlog/nested.png"},
                ]
            }

        def get_object(self, **kwargs: str) -> dict[str, FakeBody]:
            self.get_calls.append(kwargs)
            return {"Body": FakeBody(b"image-bytes")}

    fake_client = FakeS3Client()

    def choose(files: list[str]) -> str:
        assert files == ["backlog/photo.JPG", "backlog/nested.png"]
        return "backlog/nested.png"

    monkeypatch.setattr(s3_handler.random, "choice", choose)
    handler = make_s3_handler(aws_config, fake_client)

    data, key = handler.get_random_file()

    assert data == b"image-bytes"
    assert key == "backlog/nested.png"
    assert fake_client.list_calls == [{"Bucket": "bucket", "Prefix": "backlog"}]
    assert fake_client.get_calls == [{"Bucket": "bucket", "Key": "backlog/nested.png"}]


def test_get_random_file_raises_when_no_contents(aws_config: AwsProvider) -> None:
    class FakeS3Client:
        def __init__(self, response: dict[str, object]) -> None:
            self.response = response

        def list_objects_v2(self, **kwargs: str) -> dict[str, object]:
            return self.response

    responses: tuple[dict[str, object], ...] = ({}, {"Contents": []})
    for response in responses:
        handler = make_s3_handler(aws_config, FakeS3Client(response))

        with pytest.raises(FileNotFoundError, match="No files found"):
            handler.get_random_file()


def test_get_random_file_raises_when_no_image_keys(aws_config: AwsProvider) -> None:
    class FakeS3Client:
        def list_objects_v2(self, **kwargs: str) -> dict[str, list[dict[str, str]]]:
            return {"Contents": [{"Key": "backlog/"}, {"Key": "backlog/document.txt"}]}

    handler = make_s3_handler(aws_config, FakeS3Client())

    with pytest.raises(FileNotFoundError, match="No files found under prefix"):
        handler.get_random_file()


def test_move_to_archive_copies_then_deletes_original_key(aws_config: AwsProvider) -> None:
    class FakeS3Client:
        def __init__(self) -> None:
            self.copy_calls: list[dict[str, object]] = []
            self.delete_calls: list[dict[str, str]] = []

        def copy_object(self, **kwargs: object) -> None:
            self.copy_calls.append(kwargs)

        def delete_object(self, **kwargs: str) -> None:
            self.delete_calls.append(kwargs)

    fake_client = FakeS3Client()
    handler = make_s3_handler(aws_config, fake_client)

    handler.move_to_archive("backlog/photo.jpg")

    assert fake_client.copy_calls == [
        {
            "CopySource": {"Bucket": "bucket", "Key": "backlog/photo.jpg"},
            "Bucket": "bucket",
            "Key": "archive/backlog/photo.jpg",
        }
    ]
    assert fake_client.delete_calls == [{"Bucket": "bucket", "Key": "backlog/photo.jpg"}]


def test_rekognition_handler_initializes_boto_client(monkeypatch: pytest.MonkeyPatch, aws_config: AwsProvider) -> None:
    captured: dict[str, Any] = {}
    fake_client = object()

    def fake_boto_client(service_name: str, **kwargs: str) -> object:
        captured["service_name"] = service_name
        captured["kwargs"] = kwargs
        return fake_client

    monkeypatch.setattr(rekognition_handler.boto3, "client", fake_boto_client)

    handler = rekognition_handler.RekognitionHandler(aws_config)

    assert handler.client is fake_client
    assert captured == {
        "service_name": "rekognition",
        "kwargs": {
            "aws_access_key_id": "access-key",
            "aws_secret_access_key": "secret-key",
            "region_name": "eu-west-1",
        },
    }


def test_rekognition_handler_wraps_boto_client_errors(monkeypatch: pytest.MonkeyPatch, aws_config: AwsProvider) -> None:
    def raise_error(*args: object, **kwargs: object) -> None:
        raise ValueError("bad credentials")

    monkeypatch.setattr(rekognition_handler.boto3, "client", raise_error)

    with pytest.raises(RuntimeError, match="Failed to initialize Rekognition client"):
        rekognition_handler.RekognitionHandler(aws_config)


def test_get_picture_content_maps_rekognition_labels(aws_config: AwsProvider) -> None:
    class FakeRekognitionClient:
        def __init__(self) -> None:
            self.detect_calls: list[dict[str, object]] = []

        def detect_labels(self, **kwargs: object) -> dict[str, list[dict[str, object]]]:
            self.detect_calls.append(kwargs)
            return {
                "Labels": [
                    {"Name": "Forest", "Confidence": 99.9},
                    {"Name": "Mountain", "Confidence": 75.1},
                ]
            }

    fake_client = FakeRekognitionClient()
    handler = rekognition_handler.RekognitionHandler.__new__(rekognition_handler.RekognitionHandler)
    handler.client = fake_client

    labels = handler.get_picture_content(b"image", max_labels=3, min_confidence=70.0)

    assert labels == [Label(name="Forest", confidence=99), Label(name="Mountain", confidence=75)]
    assert fake_client.detect_calls == [{"Image": {"Bytes": b"image"}, "MaxLabels": 3, "MinConfidence": 70.0}]
