import pytest
from src.clients import youtube_client
from src.clients.youtube_client import ChannelInputError


@pytest.mark.parametrize(
    "url, expected_url",
    [
        ("https://www.youtube.com/@t3dotgg", "@t3dotgg"),
        ("https://www.youtube.com/@t3dotgg/", "@t3dotgg"),
        ("https://www.youtube.com/@t3dotgg?si=YelJuOp1r-cww6tZ", "@t3dotgg"),
        ("https://www.youtube.com/@t3dotgg/?si=YelJuOp1r-cww6tZ", "@t3dotgg"),
        ("https://youtube.com/@measureofdoubt?si=YelJuOp1r-cww6tZ", "@measureofdoubt"),
        ("https://youtube.com/@measureofdoubt/?si=YelJuOp1r-cww6tZ", "@measureofdoubt"),
        ("https://youtube.com/@measureofdoubt", "@measureofdoubt"),
        ("https://youtube.com/@measureofdoubt/", "@measureofdoubt"),
        (
            "https://www.youtube.com/@test.handle_123-name",
            "@test.handle_123-name",
        ),
    ],
)
def test_canonical_url_returns_complete_handle(url, expected_url):
    channel_url = youtube_client.extract_single_channel_handle(url)
    assert channel_url == expected_url


def test_malformed_url_is_rejected():
    url = "https://www.[youtube.com/"
    with pytest.raises(ChannelInputError, match="URL is malformed"):
        youtube_client.extract_single_channel_handle(url)


@pytest.mark.parametrize(
    "invalid_url, expected_error",
    [
        ("https://user:pass@youtube.com", "URL credentials are not allowed"),
        ("https://youtube.com:443", "URL ports are not allowed"),
        ("https://www.youtube.com:abc", "URL port is invalid"),
    ],
)
def test_url_credentials_and_ports_are_rejected(invalid_url, expected_error):
    with pytest.raises(ChannelInputError, match=expected_error):
        youtube_client.extract_single_channel_handle(invalid_url)


@pytest.mark.parametrize(
    "invalid_url",
    [
        "www.youtube.com",
        "http://www.youtube.com/@abc/",
        "http://youtube.com/@abc?si=hello",
    ],
)
def test_url_with_missing_https_scheme_is_rejected(invalid_url):
    with pytest.raises(ChannelInputError, match="URL scheme is not 'https'"):
        youtube_client.extract_single_channel_handle(invalid_url)


@pytest.mark.parametrize(
    "invalid_url",
    [
        "https://youtube.com.example.com/@abc",
        "https://www.youtube.com.example.com/@abc",
        "https://notyoutube.com/@abc",
    ],
)
def test_url_hostname_other_than_youtube_is_rejected(invalid_url):
    with pytest.raises(ChannelInputError, match="URL host is not set to YouTube"):
        youtube_client.extract_single_channel_handle(invalid_url)


@pytest.mark.parametrize(
    "invalid_url, expected_error",
    [
        (
            "https://www.youtube.com/@t3dotgg?si=abc&si=123",
            "URL must contain at most one query parameter",
        ),
        (
            "https://www.youtube.com/@t3dotgg?si=abc&tk=123",
            "URL must contain at most one query parameter",
        ),
        (
            "https://www.youtube.com/@t3dotgg?si=",
            "URL query must contain one non-empty 'si' parameter",
        ),
        (
            "https://www.youtube.com/@t3dotgg?abc=token",
            "URL query must contain one non-empty 'si' parameter",
        ),
    ],
)
def test_url_with_invalid_query_parameter_is_rejected(invalid_url, expected_error):
    with pytest.raises(ChannelInputError, match=expected_error):
        youtube_client.extract_single_channel_handle(invalid_url)


@pytest.mark.parametrize(
    "invalid_url, expected_error",
    [
        # Missing path
        ("https://www.youtube.com", "URL path is missing"),
        ("https://youtube.com?si=token", "URL path is missing"),
        # Missing @handle
        ("https://www.youtube.com/", "URL path is invalid"),
        ("https://www.youtube.com/@", "URL path is invalid"),
        ("https://www.youtube.com/abc", "URL path is invalid"),
        # Unsupported path shapes
        ("https://www.youtube.com/@abc/videos", "URL path is invalid"),
        ("https://www.youtube.com/@abc//", "URL path is invalid"),
        ("https://www.youtube.com//@abc", "URL path is invalid"),
        ("https://www.youtube.com/channel/UC123", "URL path is invalid"),
        ("https://www.youtube.com/user/example", "URL path is invalid"),
        ("https://www.youtube.com/c/example", "URL path is invalid"),
        # Characters rejected by your regex
        ("https://www.youtube.com/$abc", "URL path is invalid"),
        ("https://www.youtube.com/@@abc", "URL path is invalid"),
        ("https://www.youtube.com/@abc!", "URL path is invalid"),
        ("https://www.youtube.com/@abc%20def", "URL path is invalid"),
    ],
)
def test_url_with_invalid_path_is_rejected(invalid_url, expected_error):
    with pytest.raises(ChannelInputError, match=expected_error):
        youtube_client.extract_single_channel_handle(invalid_url)


def test_url_with_fragment_is_rejected():
    url = "https://www.youtube.com/@test#test-fragment"
    with pytest.raises(ChannelInputError, match="URL fragment is not empty"):
        youtube_client.extract_single_channel_handle(url)


def test_duplicate_handles_are_removed_and_order_is_preserved():
    channel_urls = [
        "https://www.youtube.com/@Same",
        "https://www.youtube.com/@Same/",
        "https://youtube.com/@Same",
        "https://youtube.com/@Same?si=token",
        "https://www.youtube.com/@same",
    ]

    expected_handles = ["@Same", "@same"]

    unique_handles = youtube_client.extract_unique_channel_handles(channel_urls)
    assert unique_handles == expected_handles
