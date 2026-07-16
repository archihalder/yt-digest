import requests
from src.config import config

BASE_URL = "https://www.googleapis.com/youtube/v3/"
CHANNEL_ENDPOINT = BASE_URL + "channels"
PLAYLIST_ITEMS_ENDPOINT = BASE_URL + "playlistItems"


def extract_channel_handles(channel_urls: list[str]) -> list[str]:
    handles = []

    for url in channel_urls:
        handle = url.rstrip("/").split("/")[-1]
        handles.append(handle)

    return handles


def fetch_latest_videos(channel_urls: list[str] | None = None) -> list[dict]:
    """
    Fetch the latest video from each configured YouTube channel.

    Args:
        channel_urls: Optional list of YouTube channel URLs. If None,
        the channels from the application configuration are used.

    Returns:
        A list of dictionaries containing the latest video metadata.
    """

    if channel_urls is None:
        channel_urls = config.channel_urls

    channel_handles = extract_channel_handles(channel_urls)

    youtube_data = []

    for handle in channel_handles:

        # get uploads playlist ID
        channel_response = requests.get(
            CHANNEL_ENDPOINT,
            params={
                "part": "contentDetails",
                "forHandle": handle,
                "key": config.youtube_api_key
            },
            timeout=10
        )

        uploads_id = channel_response.json()["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

        # get latest video
        playlist_response = requests.get(
            PLAYLIST_ITEMS_ENDPOINT,
            params={
                "part": "snippet",
                "playlistId": uploads_id,
                "maxResults": 1,
                "key": config.youtube_api_key
            },
            timeout=10
        )

        video = playlist_response.json()["items"][0]["snippet"]

        youtube_data.append({
            "channel_id": video["channelId"],
            "channel_title": video["videoOwnerChannelTitle"],
            "video_id": video["resourceId"]["videoId"],
            "video_title": video["title"],
            "published_at": video["publishedAt"]
        })
    
    return youtube_data
    