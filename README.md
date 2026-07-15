# Youtube Digest

## Data branch structure

```
(root)/
├── state.json        # {channel_id: {last_video_id, last_checked}}
├── metrics.json       # append-only run log
├── archive.json       # last-30-days full video records
└── index.html          # generated dashboard (served via GitHub Pages)
```
