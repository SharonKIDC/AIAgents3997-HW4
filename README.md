# AI Tour Guide Orchestration System

An AI-powered multi-agent system that automatically enriches walking tours by finding and selecting the best multimedia content (videos, music, text) for **every point** along a Google Maps route.

## Overview

Given a Google Maps walking route (including shortened URLs), this system:
1. Extracts **ALL points** along the route (every turn, street, direction change)
2. For each point, launches 4 concurrent agents:
   - **YouTube Agent**: Finds relevant videos
   - **Spotify Agent**: Finds relevant music
   - **Text Agent**: Finds descriptions
   - **Judge Agent**: Selects the best content
3. Collects and aggregates results for the entire tour

## Implementation Status

✅ **Completed**:
- Google Maps Directions API integration
- Shortened URL support (maps.app.goo.gl)
- Complete route extraction (all points, not just waypoints)
- Point data model with step-by-step instructions
- All 4 agent implementations (YouTube, Spotify, Text, Judge)
- Multi-threaded orchestrator with priority queue
- Thread-safe logging and result collection
- Interactive command-line interface
- Comprehensive test suite (33 tests, 100% passing)
- Example usage demonstrations

## Quick Start

### 1. Activate Virtual Environment

The virtual environment is already set up at `.venv/` with all dependencies installed.

```bash
# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

**Note**: If you need to recreate the virtual environment:
```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Setup API Keys

You need three sets of API credentials:
- **Google Maps API Key** (Directions API)
- **YouTube Data API Key**
- **Spotify API Credentials** (Client ID + Secret)

**Follow the detailed setup guide**: [API_SETUP.md](API_SETUP.md)

This guide provides step-by-step instructions for obtaining all required API keys.

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env and add all your API keys (see API_SETUP.md for details)
```

Your `.env` file should contain:
```bash
GOOGLE_MAPS_API_KEY=your_google_maps_key
YOUTUBE_API_KEY=your_youtube_key
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
```

### 4. Run the Tour Guide

```bash
# Activate virtual environment (if not already activated)
source .venv/bin/activate

# Run the interactive tour guide (default: INFO logging)
python tour_guide.py

# Run with DEBUG logging for detailed output
python tour_guide.py --log-level DEBUG

# Run with custom log file
python tour_guide.py --log-file my_tour.log
```

The tour guide will:
- Prompt for Google Maps URLs continuously
- Process each URL using multi-threaded agents
- Display judge decisions for each point
- Type 'stop' to exit

### 5. Run Examples (Optional)

```bash
# Test route extraction (requires only Google Maps API key)
python examples/example_route.py

# Test all agents working together (requires all API keys)
python examples/example_agents.py
```

### 6. Run Tests

```bash
# Activate virtual environment (if not already activated)
source .venv/bin/activate

# Run all tests (33 tests)
pytest tests/ -v

# Run specific test files
pytest tests/test_google_maps.py -v
pytest tests/test_youtube_agent.py -v
pytest tests/test_spotify_agent.py -v
pytest tests/test_text_agent.py -v
pytest tests/test_judge_agent.py -v
```

## Usage

### Interactive Tour Guide (Recommended)

```bash
python tour_guide.py
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

========================================================================================================================
TOUR GUIDE SUMMARY
========================================================================================================================
  Point  1/22: Head west on Piazza della Rotonda                  -> TEXT : Piazza della Rotonda
  Point  2/22: Turn right to stay on Piazza della Rotonda         -> TEXT : Historic centre of Albano Laziale
  Point  3/22: Turn left to stay on Piazza della Rotonda          -> TEXT : Historic centre of Albano Laziale
  Point  4/22: Slight right onto Via della Rosetta                -> TEXT : Rosetta (spacecraft)
  Point  5/22: Turn left onto Via del Pozzo delle Cornacchie      -> TEXT : Baths of Nero
  [... 17 more points ...]
  Point 22/22: 00120, Vatican City                                -> TEXT : Index of Vatican City–related articles
========================================================================================================================
Complete! Processed 22/22 points. Check log file for details.

Enter Google Maps URL (or 'stop' to exit): stop

Stopping tour guide...
Goodbye!
```

**All detailed information (reasoning, scores, timestamps) is logged to `tour_guide.log`**

### Command Line Options

```bash
# Run with DEBUG logging
python tour_guide.py --log-level DEBUG

# Custom log file
python tour_guide.py --log-file my_tour.log

# Show help
python tour_guide.py --help
```

## Example Usage

### Extract Route Points (Programmatic)

```python
import os
from dotenv import load_dotenv
from src.api.google_maps import GoogleMapsClient

# Load API key from .env
load_dotenv()
api_key = os.getenv('GOOGLE_MAPS_API_KEY')

# Initialize client
client = GoogleMapsClient(api_key=api_key, run_id="tour_001")

# Extract ALL points from walking route (supports shortened URLs)
shortened_url = "https://maps.app.goo.gl/5A5xc4qnSdL8DcVp6"
points = client.extract_route_points_from_url(shortened_url)

# Process each point
for point in points:
    print(f"{point.order + 1}. {point.location_name}")
    print(f"   Coordinates: {point.coordinates}")
```

### Use Content Agents

```python
import os
from dotenv import load_dotenv
from src.models.point import Point, Coordinates
from src.agents.youtube_agent import YouTubeAgent
from src.agents.spotify_agent import SpotifyAgent
from src.agents.text_agent import TextAgent
from src.agents.judge_agent import JudgeAgent

# Load environment
load_dotenv()

# Create a point
point = Point(
    run_id="demo",
    point_id="point_1",
    location_name="Pantheon",
    coordinates=Coordinates(lat=41.8986108, lng=12.4768729),
    order=0,
    place_id="ChIJ123",
    address="Piazza della Rotonda, Rome"
)

# Search with all agents
youtube = YouTubeAgent(run_id="demo", api_key=os.getenv('YOUTUBE_API_KEY'))
spotify = SpotifyAgent(run_id="demo",
                       client_id=os.getenv('SPOTIFY_CLIENT_ID'),
                       client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'))
text = TextAgent(run_id="demo")

video_result = youtube.search(point)
music_result = spotify.search(point)
text_result = text.search(point)

# Let judge select best content
judge = JudgeAgent(run_id="demo")
decision = judge.judge(point, [video_result, music_result, text_result])

print(f"Selected: {decision.selected_content_type}")
print(f"Reasoning: {decision.reasoning}")
```

See [examples/](examples/) directory for complete working examples.

## Documentation

- **[API_SETUP.md](API_SETUP.md)**: Step-by-step guide to obtain all required API keys
- **[PRD.md](PRD.md)**: Complete product requirements and technical specifications
- **[CLAUDE.md](CLAUDE.md)**: Developer guidance for working in this repository

## Key Design Principles

1. **Multi-threaded architecture**: Thread pool executor with priority queue for efficient processing
2. **Priority-based task scheduling**: Judge tasks have higher priority than search tasks
3. **Thread-safe operations**: Thread-safe queues, logging, and result collection
4. **Complete route coverage**: Extracts ALL points along the route, not just start/end
5. **Walking-focused**: Optimized for walking tours with turn-by-turn points
6. **Multi-agent orchestration**: 3 search agents + 1 judge per point working concurrently
7. **Comprehensive logging**: All operations logged with `(run_id, agent_name, message)` format to shared log file
8. **Interactive CLI**: Continuous operation mode with ability to process multiple routes

## Project Structure

```
/
├── .venv/                        # Virtual environment (gitignored)
├── src/
│   ├── models/
│   │   ├── point.py              # Point and Coordinates data models ✅
│   │   └── agent_result.py       # AgentResult and JudgeDecision models ✅
│   ├── api/
│   │   └── google_maps.py        # Google Maps integration ✅
│   ├── agents/
│   │   ├── base_agent.py         # Abstract base agent ✅
│   │   ├── youtube_agent.py      # YouTube search agent ✅
│   │   ├── spotify_agent.py      # Spotify search agent ✅
│   │   ├── text_agent.py         # Wikipedia search agent ✅
│   │   └── judge_agent.py        # Content selection judge ✅
│   └── orchestrator.py           # Multi-threaded orchestrator ✅
├── tests/
│   ├── test_google_maps.py       # Google Maps tests (6 tests) ✅
│   ├── test_youtube_agent.py     # YouTube agent tests (6 tests) ✅
│   ├── test_spotify_agent.py     # Spotify agent tests (6 tests) ✅
│   ├── test_text_agent.py        # Text agent tests (8 tests) ✅
│   └── test_judge_agent.py       # Judge agent tests (8 tests) ✅
├── examples/
│   ├── example_route.py          # Route extraction demo ✅
│   └── example_agents.py         # All agents working together ✅
├── tour_guide.py                 # Main CLI entry point ✅
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment variables template
├── .env                          # Your API keys (gitignored)
├── API_SETUP.md                  # API keys setup guide ✅
├── PRD.md                        # Product requirements
├── CLAUDE.md                     # Developer guide
└── README.md                     # This file
```

## Requirements

- Python 3.12+
- **Google Maps API key** (Directions API enabled - requires billing)
- **YouTube Data API v3 key** (10,000 units/day free tier)
- **Spotify API credentials** (Client ID + Secret, unlimited free tier)

See [API_SETUP.md](API_SETUP.md) for detailed setup instructions.

## License

Educational project for AI Agents course (HW4)
