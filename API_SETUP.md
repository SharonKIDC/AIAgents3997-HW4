# API Keys Setup Guide

This guide walks you through obtaining all required API keys for the AI Tour Guide system.

## Required APIs

You need three sets of API credentials:
1. **Google Maps API Key** (for route extraction)
2. **YouTube Data API Key** (for video search)
3. **Spotify API Credentials** (for music search)

---

## 1. Google Maps API Key

### Step-by-Step Instructions

#### 1.1 Access Google Cloud Console
- Go to: https://console.cloud.google.com/
- Sign in with your Google account

#### 1.2 Create a Project
1. Click the **project dropdown** at the top (next to "Google Cloud")
2. Click **"NEW PROJECT"**
3. Enter project name: `TourGuideProject` (or your preferred name)
4. Click **"CREATE"**
5. Select your new project from the dropdown

#### 1.3 Enable Required APIs
1. Go to **"APIs & Services"** → **"Library"**
2. Search for and enable **"Directions API"**:
   - Click on "Directions API"
   - Click **"ENABLE"**
3. Search for and enable **"Geocoding API"** (optional, for address lookups):
   - Click on "Geocoding API"
   - Click **"ENABLE"**

#### 1.4 Create API Key
1. Go to **"APIs & Services"** → **"Credentials"**
2. Click **"+ CREATE CREDENTIALS"** → **"API key"**
3. Copy the generated key (starts with `AIza`)
4. Click **"CLOSE"**

#### 1.5 Restrict API Key (Recommended)
1. Click the **edit icon** next to your API key
2. Under **"API restrictions"**:
   - Select **"Restrict key"**
   - Check **"Directions API"**
   - Check **"Geocoding API"** (if enabled)
3. Click **"SAVE"**

#### 1.6 Enable Billing (Required)
- Google Maps APIs require billing to be enabled
- Go to **"Billing"** in the left sidebar
- Link a billing account (you get $200 free credit monthly)
- Most small projects stay within free tier limits

### Add to .env
```bash
GOOGLE_MAPS_API_KEY=AIza...your_key_here
```

---

## 2. YouTube Data API v3 Key

### Step-by-Step Instructions

#### 2.1 Use Same Google Cloud Project
- Stay in the same Google Cloud Console project from Step 1
- OR create a new project following the same steps as 1.2

#### 2.2 Enable YouTube Data API v3
1. Go to **"APIs & Services"** → **"Library"**
2. Search for **"YouTube Data API v3"**
3. Click on **"YouTube Data API v3"**
4. Click **"ENABLE"**

#### 2.3 Create API Key
1. Go to **"APIs & Services"** → **"Credentials"**
2. Click **"+ CREATE CREDENTIALS"** → **"API key"**
3. Copy the generated key (starts with `AIza`)
4. Click **"CLOSE"**

#### 2.4 Restrict API Key (Recommended)
1. Click the **edit icon** next to your API key
2. Under **"API restrictions"**:
   - Select **"Restrict key"**
   - Check **"YouTube Data API v3"**
3. Click **"SAVE"**

### Important Notes
- **Free Quota**: 10,000 units/day
- **Search Cost**: 100 units per search = ~100 searches/day free
- **No Billing Required** (unlike Google Maps)

### Add to .env
```bash
YOUTUBE_API_KEY=AIza...your_key_here
```

---

## 3. Spotify API Credentials

### Step-by-Step Instructions

#### 3.1 Access Spotify Developer Dashboard
- Go to: https://developer.spotify.com/dashboard/
- Sign in with your Spotify account (or create one for free)

#### 3.2 Create an App
1. Click **"Create app"** button
2. Fill in the details:
   - **App name**: `Tour Guide Agent`
   - **App description**: `AI-powered tour guide with music recommendations`
   - **Redirect URI**: `http://localhost:8888/callback` (required, even if not used)
3. Check the **"I understand and agree..."** checkbox
4. Click **"SAVE"**

#### 3.3 Get Your Credentials
1. You'll see your app dashboard
2. Click **"Settings"** button in the top right
3. You'll see two values:
   - **Client ID**: Copy this
   - **Client Secret**: Click **"View client secret"** → Copy this

### Important Notes
- **No Quota Limits** for basic API calls
- **Free Tier**: Sufficient for this project
- **Rate Limits**: 180 requests per minute (very generous)

### Add to .env
```bash
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
```

---

## Final .env File

Your complete `.env` file should look like this:

```bash
# Google Maps API (for route extraction)
GOOGLE_MAPS_API_KEY=AIzaSyD...your_google_maps_key

# YouTube API (for video search)
YOUTUBE_API_KEY=AIzaSyC...your_youtube_key

# Spotify API (for music search)
SPOTIFY_CLIENT_ID=1234567890abcdef1234567890abcdef
SPOTIFY_CLIENT_SECRET=abcdef1234567890abcdef1234567890
```

---

## Testing Your API Keys

After setting up all API keys in your `.env` file:

```bash
# Activate virtual environment
source .venv/bin/activate

# Test Google Maps API (extract route points)
python examples/example_route.py

# Test all agents (requires all API keys)
python examples/example_agents.py
```

---

## Troubleshooting

### Google Maps API

**Error: "This API project is not authorized to use this API"**
- Solution: Enable Directions API in Google Cloud Console (Step 1.3)

**Error: "REQUEST_DENIED"**
- Solution: Enable billing for your Google Cloud project

**Error: "API key not valid"**
- Solution: Check that your API key is correct in `.env` file

### YouTube API

**Error: "API key not valid"**
- Solution: Enable YouTube Data API v3 in Google Cloud Console

**Error: "quotaExceeded"**
- Solution: You've hit the 10,000 units/day limit. Wait 24 hours or request quota increase.

### Spotify API

**Error: "invalid_client"**
- Solution: Check that both Client ID and Client Secret are correct

**Error: "INVALID_CLIENT: Invalid client secret"**
- Solution: Regenerate your client secret in the Spotify Dashboard → Settings

---

## API Usage Costs & Limits

| API | Free Tier | Cost After Free Tier | Notes |
|-----|-----------|---------------------|--------|
| **Google Maps Directions** | $200/month credit | $0.005 per request | ~40,000 free requests/month |
| **YouTube Data v3** | 10,000 units/day | Contact Google for increase | 100 units per search = 100 searches/day |
| **Spotify Web API** | Unlimited | Free | Rate limited to 180 req/min |

For typical usage (a few route extractions per day), you should stay well within free tier limits.

---

## Security Best Practices

1. **Never commit your `.env` file** to version control
   - Already included in `.gitignore`

2. **Restrict your API keys** to only the APIs you need
   - Limits damage if keys are exposed

3. **Use separate API keys** for development and production
   - Easier to rotate and track usage

4. **Monitor your API usage** in respective dashboards
   - Google Cloud Console: APIs & Services → Dashboard
   - Spotify Dashboard: Analytics section

5. **Rotate keys periodically** or if compromised
   - Generate new keys and update `.env`

---

## Quick Reference

### Google Cloud Console
- URL: https://console.cloud.google.com/
- Path: APIs & Services → Credentials

### Spotify Developer Dashboard
- URL: https://developer.spotify.com/dashboard/
- Path: Your App → Settings

### Need Help?
- Google Maps API Docs: https://developers.google.com/maps/documentation
- YouTube API Docs: https://developers.google.com/youtube/v3
- Spotify API Docs: https://developer.spotify.com/documentation/web-api
