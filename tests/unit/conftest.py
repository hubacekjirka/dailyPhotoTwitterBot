from pathlib import Path

import pytest
from config import Config, load_config


@pytest.fixture  # type: ignore[misc]
def ut_config() -> Config:
    ut_config_path = Path(__file__).parent / "ut_config.yaml"
    return load_config(ut_config_path)
