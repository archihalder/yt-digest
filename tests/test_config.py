import os
import pytest
import src.config as config_module
from src.config import Config, load_config, ConfigurationError


def test_loads_api_key_from_environment_without_dotenv(tmp_path, monkeypatch):
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        "channels:\n  - https://www.youtube.com/@gugul\n", encoding="utf-8"
    )

    missing_env_path = tmp_path / ".env"

    monkeypatch.setenv("YOUTUBE_API_KEY", "test-api-key")

    config = load_config(config_path=config_path, env_path=missing_env_path)

    assert config == Config(
        youtube_api_key="test-api-key", channel_urls=["https://www.youtube.com/@gugul"]
    )


def test_loads_api_key_from_dotenv_without_environment(tmp_path, monkeypatch):
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        "channels:\n  - https://www.youtube.com/@example\n", encoding="utf-8"
    )

    env_path = tmp_path / ".env"
    env_path.write_text("YOUTUBE_API_KEY=dotenv-api-key\n", encoding="utf-8")

    monkeypatch.delenv("YOUTUBE_API_KEY", raising=False)

    try:
        config = load_config(config_path=config_path, env_path=env_path)
    finally:
        os.environ.pop("YOUTUBE_API_KEY", None)

    assert config == Config(
        youtube_api_key="dotenv-api-key",
        channel_urls=["https://www.youtube.com/@example"],
    )


def test_environment_key_takes_precedence_over_dotenv(tmp_path, monkeypatch):
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        "channels:\n  - https://www.youtube.com/@example\n", encoding="utf-8"
    )

    env_path = tmp_path / ".env"
    env_path.write_text("YOUTUBE_API_KEY=dotenv-api-key\n", encoding="utf-8")

    monkeypatch.setenv("YOUTUBE_API_KEY", "environment-api-key")

    config = load_config(config_path=config_path, env_path=env_path)

    assert config.youtube_api_key == "environment-api-key"


def test_reports_unreadable_configuration_file(tmp_path, monkeypatch):

    def raise_permission_error(*args, **kwargs):
        raise PermissionError("permission denied")

    monkeypatch.setattr(config_module, "open", raise_permission_error, raising=False)

    monkeypatch.setenv("YOUTUBE_API_KEY", "test-api-key")

    with pytest.raises(
        ConfigurationError,
        match="Could not read configuration file",
    ):
        config_module.load_config(
            config_path=tmp_path / "config.yaml",
            env_path=tmp_path / ".env",
        )


@pytest.mark.parametrize("api_key", [None, "", " "])
def test_invalid_api_key_is_rejected(api_key, tmp_path, monkeypatch):
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        "channels:\n  - https://www.youtube.com/@testExample\n", encoding="utf-8"
    )

    if api_key is None:
        monkeypatch.delenv("YOUTUBE_API_KEY", raising=False)
    else:
        monkeypatch.setenv("YOUTUBE_API_KEY", api_key)

    with pytest.raises(ConfigurationError, match="YOUTUBE_API_KEY is missing or blank"):
        load_config(config_path=config_path, env_path=tmp_path / ".env")


def test_surrounding_whitespace_is_removed_from_api_key(tmp_path, monkeypatch):
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        "channels:\n  - https://www.youtube.com/@example\n", encoding="utf-8"
    )

    monkeypatch.setenv("YOUTUBE_API_KEY", "   test-api-key   ")

    config = load_config(config_path=config_path, env_path=tmp_path / ".env")

    assert config == Config(
        youtube_api_key="test-api-key",
        channel_urls=["https://www.youtube.com/@example"],
    )


def test_missing_config_file_is_rejected(tmp_path, monkeypatch):
    config_path = tmp_path / "new_config.yaml"
    monkeypatch.setenv("YOUTUBE_API_KEY", "test-api-key")

    with pytest.raises(ConfigurationError, match="Configuration file not found"):
        load_config(config_path=config_path, env_path=tmp_path / ".env")


@pytest.mark.parametrize(
    "config_body, expected_error",
    [
        (
            "channels: ['apple', 'banana'",  # missing closing brackets
            "Configuration file contains invalid YAML",
        ),
        (
            "channels:\n  - apple\n- banana",  # invalid indentations
            "Configuration file contains invalid YAML",
        ),
        (
            "channels: {name: apple",  # missing closing braces
            "Configuration file contains invalid YAML",
        ),
        ("", "Configuration file is empty"),
        ("good_morning", "Configuration must contain a YAML mapping at its root"),
    ],
)
def test_invalid_config_file_is_rejected(
    config_body, expected_error, tmp_path, monkeypatch
):
    config_path = tmp_path / ".config.yaml"
    config_path.write_text(config_body, encoding="utf-8")

    monkeypatch.setenv("YOUTUBE_API_KEY", "sample-api-key")

    with pytest.raises(ConfigurationError, match=expected_error):
        load_config(config_path=config_path, env_path=tmp_path / ".env")


@pytest.mark.parametrize(
    "config_body, expected_error",
    [
        (
            "fruits:\n  - 'apple'\n  - 'banana'",
            "Configuration is missing the required 'channels' setting",
        ),
        ("channels: 'mr.beast'", "'channels' must be a list"),
    ],
)
def test_invalid_channels_setting_is_rejected(
    config_body, expected_error, tmp_path, monkeypatch
):
    config_path = tmp_path / ".config.yaml"
    config_path.write_text(config_body, encoding="utf-8")

    monkeypatch.setenv("YOUTUBE_API_KEY", "sample-api-key")

    with pytest.raises(ConfigurationError, match=expected_error):
        load_config(config_path=config_path, env_path=tmp_path / ".env")


@pytest.mark.parametrize(
    "config_body, expected_error",
    [
        ("channels:\n  - 124\n  - 5834", "Channel url must be a string"),
        ("channels:\n  - ''", "Channel url must not be blank"),
        ("channels:\n  - '     '", "Channel url must not be blank"),
        ("channels: []", "'channels' must contain at least one channel"),
    ],
)
def test_invalid_channels_entry_is_rejected(
    config_body, expected_error, tmp_path, monkeypatch
):
    config_path = tmp_path / ".config.yaml"
    config_path.write_text(config_body, encoding="utf-8")

    monkeypatch.setenv("YOUTUBE_API_KEY", "sample-api-key")

    with pytest.raises(ConfigurationError, match=expected_error):
        load_config(config_path=config_path, env_path=tmp_path / ".env")


def test_surrounding_whitespace_is_removed_from_channel_strings(tmp_path, monkeypatch):
    config_path = tmp_path / "config.yaml"
    config_path.write_text("channels:\n - '  test-channel-url   '", encoding="utf-8")

    monkeypatch.setenv("YOUTUBE_API_KEY", "test-api-key")

    config = load_config(config_path=config_path, env_path=tmp_path / ".env")

    assert config == Config(
        youtube_api_key="test-api-key", channel_urls=["test-channel-url"]
    )


def test_channel_order_is_preserved(tmp_path, monkeypatch):
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        "channels:\n - 'channel-z'\n - 'channel-a'\n - 'channel-u'", encoding="utf-8"
    )

    expected_channels = ["channel-z", "channel-a", "channel-u"]

    monkeypatch.setenv("YOUTUBE_API_KEY", "test-api-key")

    config = load_config(config_path=config_path, env_path=tmp_path / ".env")

    assert config == Config(
        youtube_api_key="test-api-key", channel_urls=expected_channels
    )


def test_unknown_settings_are_ignored(tmp_path, monkeypatch):
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        "channels:\n - 'channel-z'\n\nsummary:\n  word_limit: 50\n\nmax_channels: 10",
        encoding="utf-8",
    )

    monkeypatch.setenv("YOUTUBE_API_KEY", "test-api-key")

    config = load_config(config_path=config_path, env_path=tmp_path / ".env")

    assert config == Config(youtube_api_key="test-api-key", channel_urls=["channel-z"])
