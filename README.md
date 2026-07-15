# Youtube Digest

## Repo Structure

```
yt-scraper/
├── .github/
│   └── workflows/
│       └── scraper.yml
├── src/
│   ├── __init__.py
│   ├── youtube_client.py       # channel lookup, latest videos, comments
│   ├── transcript_client.py    # fetch + auto-translate transcripts
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── base.py             # Provider interface (summarize, sentiment)
│   │   ├── anthropic_provider.py
│   │   ├── openai_provider.py
│   │   ├── gemini_provider.py
│   │   └── ollama_provider.py
│   ├── telegram_client.py      # sendMessage to digest bot / status bot
│   ├── state.py                # load/save state.json, diff logic
│   ├── archive.py              # append + prune 30-day archive.json
│   └── dashboard.py            # renders index.html from metrics+archive
├── main.py                     # orchestrator — wires everything together
├── generate_dashboard.py       # standalone entrypoint (also callable via CLI)
├── config.example.yaml
├── .env.example
├── requirements.txt
├── .gitignore
├── README.md
└── LICENSE
```
