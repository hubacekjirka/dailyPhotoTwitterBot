from pathlib import Path
from typing import Dict, List, Optional

import yaml
from pydantic import BaseModel

# --- App Config ---


class AppConfig(BaseModel):
    throwback_thursday: bool
    camera_mapping: Dict[str, str]


# --- Provider Configs ---


class SentryProvider(BaseModel):
    enabled: Optional[bool] = True
    dsn: str


class AwsProvider(BaseModel):
    region: Optional[str] = "eu-central-1"
    bucket: str
    access_key_id: str
    secret_access_key: str
    backlog_folder: Optional[str] = "backlog"
    archive_folder: Optional[str] = "archive"


class BskyProvider(BaseModel):
    enabled: Optional[bool] = True
    login: str
    bsky_password: str


class TelegramProvider(BaseModel):
    enabled: Optional[bool] = True
    telegram_token: str
    chat_ids: List[int]


class GcpProvider(BaseModel):
    enabled: Optional[bool] = True
    api_token: str


# --- Providers Container ---


class Providers(BaseModel):
    sentry: SentryProvider
    aws: AwsProvider
    bsky: BskyProvider
    telegram: TelegramProvider
    gcp: GcpProvider


# --- Root Config ---


class Config(BaseModel):
    app_config: AppConfig
    providers: Providers


# --- Loader Function ---


def load_config(path: Path) -> Config:
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    return Config(**data)
