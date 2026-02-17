# Configuration

## Environment Variables

Copy `.env.example` to `.env` and fill in your API keys. See [API_SETUP.md](../API_SETUP.md) for how to obtain them.

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GOOGLE_MAPS_API_KEY` | Yes | — | Google Maps Directions API key |
| `YOUTUBE_API_KEY` | No | — | YouTube Data API v3 key (video search disabled without it) |
| `SPOTIFY_CLIENT_ID` | No | — | Spotify app client ID (music search disabled without it) |
| `SPOTIFY_CLIENT_SECRET` | No | — | Spotify app client secret |

Only `GOOGLE_MAPS_API_KEY` is strictly required. If YouTube or Spotify keys are missing, the orchestrator skips those agents and proceeds with the remaining ones.

## CLI Arguments

```
usage: tour_guide.py [-h] [--log-level {DEBUG,INFO,WARNING,ERROR}] [--log-file LOG_FILE]

options:
  --log-level    Logging verbosity (default: INFO)
  --log-file     Path to log file (default: tour_guide.log)
```

## Orchestrator Parameters

Configurable in code when using the programmatic API:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_workers` | 10 | Thread pool size |

```python
orchestrator = Orchestrator(
    run_id="demo",
    youtube_api_key=os.getenv('YOUTUBE_API_KEY'),
    spotify_client_id=os.getenv('SPOTIFY_CLIENT_ID'),
    spotify_client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
    max_workers=10,
)
```

## Logging

All log entries follow the format: `(run_id, agent_name, message)`

Log levels:
- `DEBUG`: Detailed API responses, query strings, scoring breakdowns
- `INFO`: Agent start/completion, API calls, point processing
- `WARNING`: Fallback scenarios, rate limiting, degraded results
- `ERROR`: API failures, exceptions, unrecoverable states

Logs are written to file only (no console output) to keep the interactive CLI clean.
