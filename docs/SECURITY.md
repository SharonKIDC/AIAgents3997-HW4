# Security

## Credential Management

All API keys and secrets are loaded from environment variables via `python-dotenv`. No credentials are hardcoded in source code.

### Files

| File | Purpose | Git-tracked |
|------|---------|-------------|
| `.env` | Actual credentials | No (gitignored) |
| `.env.example` | Template with placeholder values | Yes |

### Required Credentials

| Variable | Service | Sensitivity |
|----------|---------|-------------|
| `GOOGLE_MAPS_API_KEY` | Google Maps Directions API | High (billing-enabled) |
| `YOUTUBE_API_KEY` | YouTube Data API v3 | Medium (quota-limited) |
| `SPOTIFY_CLIENT_ID` | Spotify Web API | Low (public identifier) |
| `SPOTIFY_CLIENT_SECRET` | Spotify Web API | High (authentication secret) |

## Gitignore Protections

The `.gitignore` excludes:
- `.env` and `.envrc` (credential files)
- `*.log` (log files may contain API keys in URLs)
- `.venv/` (virtual environment)
- `__pycache__/` (bytecode)

## API Key Handling in Code

- `tour_guide.py`: Loads keys from env vars, passes as constructor parameters
- `GoogleMapsClient`: Receives `api_key` as constructor argument
- `YouTubeAgent`: Receives `api_key` as constructor argument
- `SpotifyAgent`: Receives `client_id` and `client_secret` as constructor arguments
- `TextAgent`: No API key required (Wikipedia is public)

## Network Security

- All API calls use HTTPS
- HTTP timeouts set to 5 seconds to prevent hanging connections
- `User-Agent` header set for Wikipedia requests per their API policy

## Test Security

Test files use placeholder values (`"AIza_test_key"`, `"test_client_id"`, `"test_client_secret"`) with mocked API responses. No real API calls are made during testing.

## Recommendations

1. Restrict Google API keys to specific APIs in Cloud Console
2. Set Spotify redirect URI to `http://localhost:8888/callback` only
3. Rotate credentials if they are ever accidentally committed
4. Monitor API usage dashboards for unexpected spikes
