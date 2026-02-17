# API Costs

## Per-Request Costs

| API | Cost per Request | Free Tier | Billing Required |
|-----|-----------------|-----------|------------------|
| Google Maps Directions | ~$0.005 | $200/month credit (~40,000 requests) | Yes |
| YouTube Data API v3 | 100 units per search | 10,000 units/day (~100 searches) | No |
| Spotify Web API | Free | Unlimited | No |
| Wikipedia REST API | Free | Unlimited | No |

## Cost Per Tour

Each route point requires:
- 0 or 1 Google Maps Directions call (1 call per route, not per point)
- 1 YouTube search (100 quota units)
- 1 Spotify search (free)
- 1-3 Wikipedia requests (free)
- 1 Judge evaluation (local, no API call)

| Route Size | Google Maps | YouTube Units | Estimated Cost |
|------------|-------------|---------------|----------------|
| 10 points | 1 call ($0.005) | 1,000 units | ~$0.005 |
| 25 points | 1 call ($0.005) | 2,500 units | ~$0.005 |
| 50 points | 1 call ($0.005) | 5,000 units | ~$0.005 |

**Key insight**: Google Maps charges per route, not per point. The main cost driver is the number of distinct routes processed, not route length.

## Daily Limits

| API | Daily Limit | Routes per Day (25 pts avg) |
|-----|-------------|---------------------------|
| YouTube Data v3 | 10,000 units | ~4 routes |
| Google Maps | ~40,000 requests/month | ~1,300 routes/month |
| Spotify | 180 requests/minute | Effectively unlimited |
| Wikipedia | No hard limit | Effectively unlimited |

YouTube is the tightest constraint at ~4 routes per day on the free tier.

## LLM Costs

This project does not use any LLM APIs. The JudgeAgent uses deterministic scoring logic (keyword matching, content-type preference, description length). No inference costs.
