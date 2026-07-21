import sys

from src.clients.youtube import channel_input, client
from src.config import ConfigurationError, load_config


def main() -> int:
    try:
        config = load_config()
    except ConfigurationError as error:
        print(f"Configuration error: {error}", file=sys.stderr)
        return 1

    try:
        handles = channel_input.extract_unique_channel_handles(config.channel_urls)
    except channel_input.ChannelInputError as error:
        print(f"Channel Input Error: {error}", file=sys.stderr)
        return 1

    youtube_data = client.fetch_latest_videos(
        channel_handles=handles, api_key=config.youtube_api_key
    )

    for data in youtube_data:
        print(data)
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
