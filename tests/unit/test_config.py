from pathlib import Path
from textwrap import dedent

import pytest
from config import Config, load_config
from pydantic import ValidationError


def test_unit_config_fixture_loads_expected_sections(ut_config: Config) -> None:
    assert ut_config.app_config.throwback_thursday is True
    assert ut_config.app_config.camera_mapping["GM1913"] == "Oneplus 7 Pro"
    assert ut_config.providers.aws.bucket == "UT"
    assert ut_config.providers.gcp.api_token == "UT"


def test_provider_defaults_are_applied() -> None:
    config = Config.model_validate(
        {
            "app_config": {"throwback_thursday": False, "camera_mapping": {}},
            "providers": {
                "sentry": {"dsn": "dsn"},
                "aws": {
                    "bucket": "bucket",
                    "access_key_id": "access",
                    "secret_access_key": "secret",
                },
                "bsky": {"login": "user", "bsky_password": "password"},
                "telegram": {"telegram_token": "token", "chat_ids": [1]},
                "gcp": {"api_token": "gcp-token"},
            },
        }
    )

    assert config.providers.sentry.enabled is True
    assert config.providers.aws.region == "eu-central-1"
    assert config.providers.aws.backlog_folder == "backlog"
    assert config.providers.aws.archive_folder == "archive"
    assert config.providers.bsky.enabled is True
    assert config.providers.telegram.enabled is True
    assert config.providers.gcp.enabled is True


def test_load_config_reads_yaml_file(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        dedent(
            """
            app_config:
              throwback_thursday: false
              camera_mapping:
                CameraA: "Camera A"
            providers:
              sentry:
                enabled: false
                dsn: "dsn"
              aws:
                region: "test-region"
                bucket: "bucket"
                access_key_id: "access"
                secret_access_key: "secret"
              bsky:
                enabled: false
                login: "user"
                bsky_password: "password"
              telegram:
                enabled: false
                telegram_token: "token"
                chat_ids:
                  - 123
              gcp:
                enabled: false
                api_token: "gcp-token"
            """
        ),
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config.app_config.camera_mapping == {"CameraA": "Camera A"}
    assert config.providers.aws.region == "test-region"
    assert config.providers.telegram.chat_ids == [123]


def test_load_config_missing_file_mentions_config_env_var(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="BOT_CONFIG_PATH"):
        load_config(tmp_path / "missing.yaml")


def test_missing_provider_block_raises_validation_error(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        dedent(
            """
            app_config:
              throwback_thursday: true
              camera_mapping: {}
            providers:
              sentry:
                dsn: "dsn"
              bsky:
                login: "user"
                bsky_password: "password"
              telegram:
                telegram_token: "token"
                chat_ids:
                  - 123
              gcp:
                api_token: "gcp-token"
            """
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValidationError, match="providers.aws"):
        load_config(config_path)
