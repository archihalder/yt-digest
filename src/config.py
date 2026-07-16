import os
from dataclasses import dataclass
from pathlib import Path

import yaml
from dotenv import load_dotenv


class ConfigurationError(Exception):
    """Raised when the application configuration is invalid."""
    pass


ROOT_DIR = Path(__file__).resolve().parent.parent

load_dotenv(ROOT_DIR / ".env")


@dataclass(frozen=True)
class Config:
    youtube_api_key: str
    channel_urls: list[str]


def load_config() -> Config:
    youtube_api_key = os.getenv("YOUTUBE_API_KEY")

    if not youtube_api_key:
        raise ConfigurationError("YOUTUBE_API_KEY not found in .env")

    with open(ROOT_DIR / "config.yaml", "r") as f:
        config_data = yaml.safe_load(f)

    channel_urls = config_data["channels"]

    return Config(
        youtube_api_key=youtube_api_key,
        channel_urls=channel_urls
    )


config = load_config()
