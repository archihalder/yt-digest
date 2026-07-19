import os
from dataclasses import dataclass
from pathlib import Path

import yaml
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT_DIR / "config.yaml"
ENV_PATH = ROOT_DIR / ".env"


class ConfigurationError(Exception):
    """Raised when application configuration is missing or invalid."""


@dataclass(frozen=True)
class Config:
    youtube_api_key: str
    channel_urls: list[str]


def load_config(config_path: Path = CONFIG_PATH, env_path: Path = ENV_PATH) -> Config:

    load_dotenv(dotenv_path=env_path, override=False)

    youtube_api_key = os.getenv("YOUTUBE_API_KEY")

    if youtube_api_key is None or not youtube_api_key.strip():
        raise ConfigurationError(
            "YOUTUBE_API_KEY is missing or blank in the environment"
        )

    youtube_api_key = youtube_api_key.strip()

    try:
        with open(config_path, "r", encoding="utf-8") as config_file:
            config_data = yaml.safe_load(config_file)

        if config_data is None:
            raise ConfigurationError(
                "Configuration file is empty or contains no configuration"
            )

    except FileNotFoundError as error:
        raise ConfigurationError(
            f"Configuration file not found: {config_path}"
        ) from error

    except OSError as error:
        raise ConfigurationError(
            f"Could not read configuration file: {config_path}"
        ) from error

    except yaml.YAMLError as error:
        raise ConfigurationError(
            f"Configuration file contains invalid YAML: {config_path}"
        ) from error

    if not isinstance(config_data, dict):
        raise ConfigurationError(
            "Configuration must contain a YAML mapping at its root"
        )

    if "channels" not in config_data:
        raise ConfigurationError(
            "Configuration is missing the required 'channels' setting"
        )

    channel_urls = config_data["channels"]

    if not isinstance(channel_urls, list):
        raise ConfigurationError("'channels' must be a list")

    if not channel_urls:
        raise ConfigurationError("'channels' must contain at least one channel")

    normalized_channel_urls = []

    for channel_url in channel_urls:
        if not isinstance(channel_url, str):
            raise ConfigurationError("Channel url must be a string")

        channel_url = channel_url.strip()

        if not channel_url:
            raise ConfigurationError("Channel url must not be blank")

        normalized_channel_urls.append(channel_url)

    return Config(
        youtube_api_key=youtube_api_key,
        channel_urls=normalized_channel_urls,
    )
