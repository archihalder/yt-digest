from src import youtube_client

youtube_data = youtube_client.fetch_latest_videos()

for data in youtube_data:
    print(data)
    print()
