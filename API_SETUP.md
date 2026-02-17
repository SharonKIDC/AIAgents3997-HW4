# API Keys Setup Guide

Three sets of credentials are required. After obtaining them, copy `.env.example` to `.env` and fill in the values.

## 1. Google Maps API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create or select a project
3. Enable **Directions API** (APIs & Services -> Library -> search "Directions API" -> Enable)
4. Optionally enable **Geocoding API** for address lookups
5. Create an API key (Credentials -> Create Credentials -> API key)
6. **Enable billing** (required; $200/month free credit covers typical usage)
7. Recommended: restrict the key to only Directions API

```
GOOGLE_MAPS_API_KEY=AIza...
```

## 2. YouTube Data API v3 Key

1. In the same Google Cloud Console project (or a new one)
2. Enable **YouTube Data API v3** (Library -> search -> Enable)
3. Create an API key (Credentials -> Create Credentials -> API key)
4. Recommended: restrict the key to only YouTube Data API v3

```
YOUTUBE_API_KEY=AIza...
```

## 3. Spotify API Credentials

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
2. Create an app (name: `Tour Guide Agent`, redirect URI: `http://localhost:8888/callback`)
3. In app Settings, copy **Client ID** and **Client Secret**

```
SPOTIFY_CLIENT_ID=...
SPOTIFY_CLIENT_SECRET=...
```

## Costs & Limits

| API | Free Tier | Notes |
|-----|-----------|-------|
| Google Maps Directions | $200/month credit (~40,000 requests) | Billing required |
| YouTube Data v3 | 10,000 units/day (~100 searches) | No billing required |
| Spotify Web API | Unlimited | Rate limit: 180 req/min |

## Verify Setup

```bash
source .venv/bin/activate
python examples/example_route.py     # Tests Google Maps only
python examples/example_agents.py    # Tests all APIs
```

## Troubleshooting

| Error | Fix |
|-------|-----|
| `This API project is not authorized to use this API` | Enable Directions API in Cloud Console |
| `REQUEST_DENIED` | Enable billing for your Google Cloud project |
| `API key not valid` | Verify the key in `.env` matches what's in Cloud Console |
| `quotaExceeded` (YouTube) | Daily 10,000-unit limit reached; wait 24 hours |
| `invalid_client` (Spotify) | Check both Client ID and Client Secret are correct |
| `INVALID_CLIENT: Invalid client secret` | Regenerate secret in Spotify Dashboard -> Settings |
