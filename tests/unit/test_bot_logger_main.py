from pathlib import Path

import bot as bot_module
import logger as logger_module
import main as main_module
import pytest
from config import Config, SentryProvider


def test_bot_initializes_sentry(monkeypatch: pytest.MonkeyPatch, ut_config: Config) -> None:
    sentry_calls: list[SentryProvider] = []
    monkeypatch.setattr(bot_module, "setup_sentry", lambda config: sentry_calls.append(config))

    bot = bot_module.Bot(ut_config)

    assert bot.config is ut_config
    assert sentry_calls == [ut_config.providers.sentry]


def test_bot_run_posts_to_enabled_providers_and_archives(monkeypatch: pytest.MonkeyPatch, ut_config: Config) -> None:
    events: list[tuple[str, object]] = []

    class FakeS3Handler:
        def __init__(self, config: object) -> None:
            events.append(("s3-init", config))

        def get_random_file(self) -> tuple[bytes, str]:
            events.append(("s3-get", None))
            return b"image", "backlog/photo.jpg"

        def move_to_archive(self, key: str) -> None:
            events.append(("s3-archive", key))

    class FakePicture:
        def __init__(
            self,
            picture_bytes: bytes,
            picture_path: str,
            aws_config: object,
            gcp_config: object,
        ) -> None:
            events.append(("picture", (picture_bytes, picture_path, aws_config, gcp_config)))
            self.picture_path = picture_path

    class FakeBskyHandler:
        def __init__(self, config: object) -> None:
            events.append(("bsky-init", config))

        def post_picture(self, picture: object) -> None:
            events.append(("bsky-post", picture))

    class FakeTelegramHandler:
        def __init__(self, config: object) -> None:
            events.append(("telegram-init", config))

        def post_picture(self, picture: object) -> None:
            events.append(("telegram-post", picture))

    monkeypatch.setattr(bot_module, "setup_sentry", lambda config: None)
    monkeypatch.setattr(bot_module, "S3Handler", FakeS3Handler)
    monkeypatch.setattr(bot_module, "Picture", FakePicture)
    monkeypatch.setattr(bot_module, "BskyHandler", FakeBskyHandler)
    monkeypatch.setattr(bot_module, "TelegramHandler", FakeTelegramHandler)

    bot_module.Bot(ut_config).run()

    assert ("s3-init", ut_config.providers.aws) in events
    assert ("s3-get", None) in events
    assert ("bsky-init", ut_config.providers.bsky) in events
    assert ("telegram-init", ut_config.providers.telegram) in events
    assert ("s3-archive", "backlog/photo.jpg") in events


def test_bot_run_skips_archive_when_no_social_provider_enabled(
    monkeypatch: pytest.MonkeyPatch, ut_config: Config
) -> None:
    config = ut_config.model_copy(deep=True)
    config.providers.bsky.enabled = False
    config.providers.telegram.enabled = False
    archive_calls: list[str] = []

    class FakeS3Handler:
        def __init__(self, config: object) -> None:
            pass

        def get_random_file(self) -> tuple[bytes, str]:
            return b"image", "backlog/photo.jpg"

        def move_to_archive(self, key: str) -> None:
            archive_calls.append(key)

    class FakePicture:
        def __init__(self, picture_bytes: bytes, picture_path: str, aws_config: object, gcp_config: object) -> None:
            self.picture_path = picture_path

    def fail_if_called(config: object) -> None:
        raise AssertionError("disabled provider should not be created")

    monkeypatch.setattr(bot_module, "setup_sentry", lambda config: None)
    monkeypatch.setattr(bot_module, "S3Handler", FakeS3Handler)
    monkeypatch.setattr(bot_module, "Picture", FakePicture)
    monkeypatch.setattr(bot_module, "BskyHandler", fail_if_called)
    monkeypatch.setattr(bot_module, "TelegramHandler", fail_if_called)

    bot_module.Bot(config).run()

    assert archive_calls == []


def test_bot_run_swallows_provider_and_archive_errors(monkeypatch: pytest.MonkeyPatch, ut_config: Config) -> None:
    class FakeS3Handler:
        def __init__(self, config: object) -> None:
            pass

        def get_random_file(self) -> tuple[bytes, str]:
            return b"image", "backlog/photo.jpg"

        def move_to_archive(self, key: str) -> None:
            raise RuntimeError("archive failed")

    class FakePicture:
        def __init__(self, picture_bytes: bytes, picture_path: str, aws_config: object, gcp_config: object) -> None:
            self.picture_path = picture_path

    class FailingBskyHandler:
        def __init__(self, config: object) -> None:
            pass

        def post_picture(self, picture: object) -> None:
            raise RuntimeError("bsky failed")

    class FailingTelegramHandler:
        def __init__(self, config: object) -> None:
            pass

        def post_picture(self, picture: object) -> None:
            raise RuntimeError("telegram failed")

    monkeypatch.setattr(bot_module, "setup_sentry", lambda config: None)
    monkeypatch.setattr(bot_module, "S3Handler", FakeS3Handler)
    monkeypatch.setattr(bot_module, "Picture", FakePicture)
    monkeypatch.setattr(bot_module, "BskyHandler", FailingBskyHandler)
    monkeypatch.setattr(bot_module, "TelegramHandler", FailingTelegramHandler)

    bot_module.Bot(ut_config).run()


def test_setup_sentry_skips_disabled_config(monkeypatch: pytest.MonkeyPatch) -> None:
    init_calls: list[dict[str, object]] = []
    monkeypatch.setattr(logger_module.sentry_sdk, "init", lambda **kwargs: init_calls.append(kwargs))

    logger_module.setup_sentry(SentryProvider(enabled=False, dsn="dsn"))

    assert init_calls == []


def test_setup_sentry_initializes_enabled_config(monkeypatch: pytest.MonkeyPatch) -> None:
    init_calls: list[dict[str, object]] = []
    monkeypatch.setattr(logger_module.sentry_sdk, "init", lambda **kwargs: init_calls.append(kwargs))

    logger_module.setup_sentry(SentryProvider(enabled=True, dsn="dsn"))

    assert init_calls == [{"dsn": "dsn", "traces_sample_rate": 1.0, "send_default_pii": True}]


def test_setup_sentry_swallows_init_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    def raise_error(**kwargs: object) -> None:
        raise RuntimeError("sentry failed")

    monkeypatch.setattr(logger_module.sentry_sdk, "init", raise_error)

    logger_module.setup_sentry(SentryProvider(enabled=True, dsn="dsn"))


def test_main_loads_config_and_runs_bot(monkeypatch: pytest.MonkeyPatch, ut_config: Config) -> None:
    calls: list[tuple[str, object]] = []

    def fake_load_config(path: Path) -> Config:
        calls.append(("load", path))
        return ut_config

    class FakeBot:
        def __init__(self, config: Config) -> None:
            calls.append(("bot-init", config))

        def run(self) -> None:
            calls.append(("bot-run", None))

    monkeypatch.setattr(main_module, "load_config", fake_load_config)
    monkeypatch.setattr(main_module, "Bot", FakeBot)
    monkeypatch.delenv("BOT_CONFIG_PATH", raising=False)

    main_module.main()

    assert calls == [("load", Path("app", "config.yaml")), ("bot-init", ut_config), ("bot-run", None)]


def test_main_uses_bot_config_path_env_var(monkeypatch: pytest.MonkeyPatch, ut_config: Config) -> None:
    calls: list[Path] = []

    def fake_load_config(path: Path) -> Config:
        calls.append(path)
        return ut_config

    class FakeBot:
        def __init__(self, config: Config) -> None:
            self.config = config

        def run(self) -> None:
            return None

    monkeypatch.setenv("BOT_CONFIG_PATH", "/run/secrets/photo-bot-config.yaml")
    monkeypatch.setattr(main_module, "load_config", fake_load_config)
    monkeypatch.setattr(main_module, "Bot", FakeBot)

    main_module.main()

    assert calls == [Path("/run/secrets/photo-bot-config.yaml")]
