import requests


BASE_URL = "https://www.googleapis.com/youtube/v3/"
CHANNEL_ENDPOINT = BASE_URL + "channels"
PLAYLIST_ITEMS_ENDPOINT = BASE_URL + "playlistItems"


def fetch_latest_videos(*, channel_handles: list[str], api_key: str) -> list[dict]:
    """
    Fetch the latest video from each YouTube channel.

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
