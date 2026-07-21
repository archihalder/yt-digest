from unittest.mock import Mock

import main
from src.config import ConfigurationError, Config
from src.clients.youtube.channel_input import ChannelInputError


def test_configuration_error_returns_one_and_stops_processing(monkeypatch, capsys):
    load_config = Mock(side_effect=ConfigurationError("Test Configuration Failure"))
    extract_handles = Mock()
    fetch_videos = Mock()

    monkeypatch.setattr(main, "load_config", load_config)
    monkeypatch.setattr(main.channel_input, "extract_unique_channel_handles", extract_handles)
    monkeypatch.setattr(main.client, "fetch_latest_videos", fetch_videos)

    result = main.main()
    captured = capsys.readouterr()

    assert result == 1
    assert "Configuration error: Test Configuration Failure" in captured.err
    assert captured.out == ""

    load_config.assert_called_once_with()
    extract_handles.assert_not_called()
    fetch_videos.assert_not_called()


def test_channel_input_error_returns_one_and_skips_fetching(monkeypatch, capsys):
    config = Config(
        youtube_api_key="test-api-key",
        channel_urls=["https://www.youtube.com/@example"],
    )

    load_config = Mock(return_value=config)
    extract_handles = Mock(side_effect=ChannelInputError("Test invalid channel URL"))
    fetch_videos = Mock()

    monkeypatch.setattr(main, "load_config", load_config)
    monkeypatch.setattr(main.channel_input, "extract_unique_channel_handles", extract_handles)
    monkeypatch.setattr(main.client, "fetch_latest_videos", fetch_videos)

    result = main.main()
    captured = capsys.readouterr()

    assert result == 1
    assert "Channel Input Error: Test invalid channel URL" in captured.err
    assert captured.out == ""

    load_config.assert_called_once_with()
    extract_handles.assert_called_once_with(config.channel_urls)
    fetch_videos.assert_not_called()


def test_valid_configuration_passes_handles_and_api_keys_to_fetching_and_returns_zero(
    monkeypatch, capsys
):
    config = Config(
        youtube_api_key="test-api-key",
        channel_urls=["https://www.youtube.com/@testChannel"],
    )

    expected_handles = ["@testChannel"]

    youtube_data = [
        {
            "channel_id": "channel-123",
            "channel_title": "Test Channel",
            "video_id": "video-123",
            "video_title": "Test Video",
            "published_at": "2026-07-22T10:00:00Z",
        }
    ]

    load_config = Mock(return_value=config)
    extract_handles = Mock(return_value=expected_handles)
    fetch_videos = Mock(return_value=youtube_data)

    monkeypatch.setattr(main, "load_config", load_config)
    monkeypatch.setattr(main.channel_input, "extract_unique_channel_handles", extract_handles)
    monkeypatch.setattr(main.client, "fetch_latest_videos", fetch_videos)

    result = main.main()
    captured = capsys.readouterr()

    assert result == 0
    assert captured.err == ""
    assert "Test Channel" in captured.out
    assert "Test Video" in captured.out

    load_config.assert_called_once_with()
    extract_handles.assert_called_once_with(config.channel_urls)
    fetch_videos.assert_called_once_with(
        channel_handles=expected_handles, api_key=config.youtube_api_key
    )
