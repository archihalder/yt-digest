import sys

from src.clients import youtube_client
from src.config import ConfigurationError, load_config


def main() -> int:
    try:
        config = load_config()
    except ConfigurationError as error:
        print(f"Configuration error: {error}", file=sys.stderr)
        return 1

    youtube_data = youtube_client.fetch_latest_videos(
        channel_urls=config.channel_urls, api_key=config.youtube_api_key
    )

    for data in youtube_data:
        print(data)
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
