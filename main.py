import sys

from src.clients import youtube_client as yc
from src.clients.youtube_client import ChannelInputError
from src.config import ConfigurationError, load_config


def main() -> int:
    try:
        config = load_config()
    except ConfigurationError as error:
        print(f"Configuration error: {error}", file=sys.stderr)
        return 1

    try:
        channel_handles = yc.extract_unique_channel_handles(config.channel_urls)
    except ChannelInputError as error:
        print(f"Channel Input Error: {error}", file=sys.stderr)
        return 1

    youtube_data = yc.fetch_latest_videos(
        channel_handles=channel_handles, api_key=config.youtube_api_key
    )

    for data in youtube_data:
        print(data)
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
