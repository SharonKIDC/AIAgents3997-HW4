# AI Tour Guide Orchestration System

A multi-agent system that enriches walking tours with multimedia content. Given a Google Maps route, it extracts every point along the path and concurrently searches for the best video, music, or text to accompany each stop.

For detailed requirements see [docs/PRD.md](docs/PRD.md). For architecture see [docs/Architecture.md](docs/Architecture.md).

## Quick Start

```bash
# 1. Setup environment
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Configure API keys (see API_SETUP.md for how to obtain them)
cp .env.example .env
# Edit .env with your keys

# 3. Run
python tour_guide.py
```

## Usage

### Interactive CLI

```bash
python tour_guide.py                        # Default (INFO logging)
python tour_guide.py --log-level DEBUG      # Verbose logging
python tour_guide.py --log-file my.log      # Custom log file
```

Example session:

```
======================================================================
AI Tour Guide - Multimedia Content Generator
======================================================================
Enter Google Maps walking route URLs to process.
Type 'stop' to exit the program.
======================================================================

Enter Google Maps URL (or 'stop' to exit): https://maps.app.goo.gl/5A5xc4qnSdL8DcVp6

Got map URL: https://maps.app.goo.gl/5A5xc4qnSdL8DcVp6
Run ID: run_20251214_193220_1
Added 88 tasks for 22 points to orchestrator
Processing...

========================================
TOUR GUIDE SUMMARY
========================================
  Point  1/22: Head west on Piazza della Rotonda  -> TEXT : Piazza della Rotonda
  Point  2/22: Turn right to stay on Piazza ...   -> TEXT : Historic centre of Albano Laziale
  ...
  Point 22/22: 00120, Vatican City                -> TEXT : Index of Vatican City-related articles
========================================
Complete! Processed 22/22 points. Check log file for details.
```

### Programmatic Usage

```python
from dotenv import load_dotenv
from src.api.google_maps import GoogleMapsClient
from src.orchestrator import Orchestrator
import os

load_dotenv()
client = GoogleMapsClient(api_key=os.getenv('GOOGLE_MAPS_API_KEY'), run_id="demo")
points = client.extract_route_points_from_url("https://maps.app.goo.gl/...")

orchestrator = Orchestrator(
    run_id="demo",
    youtube_api_key=os.getenv('YOUTUBE_API_KEY'),
    spotify_client_id=os.getenv('SPOTIFY_CLIENT_ID'),
    spotify_client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
)
decisions = orchestrator.process_points(points)
```

See [examples/](examples/) for complete working demos.

### Running Tests

```bash
pytest tests/ -v          # All 33 tests
pytest tests/test_google_maps.py -v   # Single module
```

## Project Structure

```
src/
  models/
    point.py              # Point and Coordinates dataclasses
    agent_result.py       # AgentResult and JudgeDecision dataclasses
  api/
    google_maps.py        # Route extraction via Directions API
  agents/
    base_agent.py         # Abstract base with logging helpers
    youtube_agent.py      # YouTube Data API v3 search
    spotify_agent.py      # Spotify Web API search
    text_agent.py         # Wikipedia REST API search
    judge_agent.py        # Scores and selects best content
  orchestrator.py         # ThreadPoolExecutor + PriorityQueue coordination
tests/                    # Unit tests (mocked API calls)
examples/
  example_route.py        # Route extraction demo
  example_agents.py       # All agents working together demo
tour_guide.py             # Interactive CLI entry point
```

## Requirements

- Python 3.12+
- API keys: Google Maps (Directions API), YouTube Data v3, Spotify Web API
- See [API_SETUP.md](API_SETUP.md) for setup instructions and cost details

## License

Educational project for AI Agents course (HW4).
