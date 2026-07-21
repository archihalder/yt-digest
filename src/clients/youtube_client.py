import re
import requests
from urllib.parse import urlsplit, parse_qsl

BASE_URL = "https://www.googleapis.com/youtube/v3/"
CHANNEL_ENDPOINT = BASE_URL + "channels"
PLAYLIST_ITEMS_ENDPOINT = BASE_URL + "playlistItems"


class ChannelInputError(Exception):
    """Raised when the channel url is invalid"""


def extract_single_channel_handle(channel_url: str) -> str:
    try:
        split_url = urlsplit(channel_url)
    except ValueError as error:
        raise ChannelInputError(f"URL is malformed: {channel_url}") from error

    if split_url.scheme != "https":
        raise ChannelInputError(f"URL scheme is not 'https': {channel_url}")

    if split_url.username is not None or split_url.password is not None:
        raise ChannelInputError(f"URL credentials are not allowed: {channel_url}")

    try:
        port = split_url.port
    except ValueError as error:
        raise ChannelInputError(f"URL port is invalid: {channel_url}") from error

    if port is not None:
        raise ChannelInputError(f"URL ports are not allowed: {channel_url}")

    if split_url.hostname not in {"www.youtube.com", "youtube.com"}:
        raise ChannelInputError(f"URL host is not set to YouTube: {channel_url}")

    query_parameters = parse_qsl(split_url.query, keep_blank_values=True)

    if query_parameters:
        if len(query_parameters) != 1:
            raise ChannelInputError(
                f"URL must contain at most one query parameter: {channel_url}"
            )

        name, value = query_parameters[0]

        if name != "si" or not value:
            raise ChannelInputError(
                f"URL query must contain one non-empty 'si' parameter: {channel_url}"
            )

    url_path = split_url.path

    if not url_path:
        raise ChannelInputError(f"URL path is missing: {channel_url}")

    if not re.fullmatch(r"/@[A-Za-z0-9._-]+/?", url_path):
        raise ChannelInputError(f"URL path is invalid: {channel_url}")

    if split_url.fragment:
        raise ChannelInputError(f"URL fragment is not empty: {channel_url}")

    if url_path[-1] == "/":
        url_path = url_path[1:-1]
    else:
        url_path = url_path[1:]

    return url_path


def extract_unique_channel_handles(channel_urls: list[str]) -> list[str]:
    unique_handles = []
    seen_handles = set()

    for url in channel_urls:
        handle = extract_single_channel_handle(url)

        if handle not in seen_handles:
            seen_handles.add(handle)
            unique_handles.append(handle)

    return unique_handles


def fetch_latest_videos(*, channel_handles: list[str], api_key: str) -> list[dict]:
    """
    Fetch the latest video from each channel.

    Args:
        channel_handles: YouTube channel handles to process.
        api_key: YouTube Data API key.

    Returns:
        Metadata for the latest video from each channel.
    """

    youtube_data = []

    for handle in channel_handles:
        # get uploads playlist ID
        channel_response = requests.get(
            CHANNEL_ENDPOINT,
            params={
                "part": "contentDetails",
                "forHandle": handle,
                "key": api_key,
            },
            timeout=10,
        )

        uploads_id = channel_response.json()["items"][0]["contentDetails"][
            "relatedPlaylists"
        ]["uploads"]

        # get latest video
        playlist_response = requests.get(
            PLAYLIST_ITEMS_ENDPOINT,
            params={
                "part": "snippet",
                "playlistId": uploads_id,
                "maxResults": 1,
                "key": api_key,
            },
            timeout=10,
        )

        video = playlist_response.json()["items"][0]["snippet"]

        youtube_data.append(
            {
                "channel_id": video["channelId"],
                "channel_title": video["videoOwnerChannelTitle"],
                "video_id": video["resourceId"]["videoId"],
                "video_title": video["title"],
                "published_at": video["publishedAt"],
            }
        )

    return youtube_data
