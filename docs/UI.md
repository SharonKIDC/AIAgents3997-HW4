# UI Documentation

The AI Tour Guide is a terminal-based CLI application. All user interaction happens through `tour_guide.py`.

## Command Syntax

```
python tour_guide.py [--log-level {DEBUG,INFO,WARNING,ERROR}] [--log-file LOG_FILE]
```

### Help Output

```
$ python tour_guide.py --help
usage: tour_guide.py [-h] [--log-level {DEBUG,INFO,WARNING,ERROR}]
                     [--log-file LOG_FILE]

AI Tour Guide - Generate multimedia content for walking routes

options:
  -h, --help            show this help message and exit
  --log-level {DEBUG,INFO,WARNING,ERROR}
                        Set logging level (default: INFO)
  --log-file LOG_FILE   Log file path (default: tour_guide.log)
```

### Options

| Flag | Values | Default | Description |
|------|--------|---------|-------------|
| `--log-level` | `DEBUG`, `INFO`, `WARNING`, `ERROR` | `INFO` | Controls verbosity of log file output |
| `--log-file` | Any file path | `tour_guide.log` | Where agent logs are written |

## Interactive Loop

On startup, the CLI enters an interactive loop accepting Google Maps URLs until the user types `stop`.

### State Diagram

```
┌─────────┐
│  Start  │
└────┬────┘
     │
     ▼
┌──────────────────────┐
│  Print welcome banner │
└──────────┬───────────┘
           │
           ▼
     ┌───────────┐
     │  Prompt:   │◄──────────────────────┐
     │  Enter URL │                       │
     └─────┬─────┘                       │
           │                              │
     ┌─────▼──────┐                      │
     │  "stop"?   │── yes ──► Exit       │
     └─────┬──────┘                      │
           │ no                           │
     ┌─────▼──────┐                      │
     │  Valid URL? │── no ──► Error msg ──┘
     └─────┬──────┘
           │ yes
     ┌─────▼────────────────────┐
     │  Extract route points    │
     │  (Google Maps API)       │
     └─────┬────────────────────┘
           │
     ┌─────▼────────────────────┐
     │  Run agents per point    │
     │  (YouTube, Spotify, Text)│
     │  + Judge scoring         │
     └─────┬────────────────────┘
           │
     ┌─────▼────────────────────┐
     │  Print summary table     │
     └─────────┬────────────────┘
               │
               └──────────────────────────┘
```

## Terminal Examples

### Example 1: Standard Run

```
$ python tour_guide.py
======================================================================
AI Tour Guide - Multimedia Content Generator
======================================================================
Enter Google Maps walking route URLs to process.
Type 'stop' to exit the program.
======================================================================

Enter Google Maps URL (or 'stop' to exit): https://maps.app.goo.gl/FpTzPfHX6F1HPt7T8

Got map URL: https://maps.app.goo.gl/FpTzPfHX6F1HPt7T8
Run ID: run_20251214_193220_1
Added 88 tasks for 22 points to orchestrator
Processing...

========================================================================================================================
TOUR GUIDE SUMMARY
========================================================================================================================
  Point  1/22: Head west on Piazza della Rotonda                    -> TEXT : Piazza della Rotonda
  Point  2/22: Turn right to stay on Piazza della Rotonda           -> TEXT : Historic centre of Albano Laziale
  Point  3/22: Turn left to stay on Piazza della Rotonda            -> TEXT : Historic centre of Albano Laziale
  Point  4/22: Slight right onto Via della Rosetta                  -> TEXT : Rosetta (spacecraft)
  Point  5/22: Turn left onto Via del Pozzo delle Cornacchie        -> TEXT : Baths of Nero
  Point  6/22: Continue onto Largo Giuseppe Toniolo                 -> TEXT : Università Cattolica del Sacro Cuore
  Point  7/22: Continue onto Via di S. Giovanna d'Arco              -> TEXT : Giovanna d'Arco
  Point  8/22: Turn right onto Piazza delle Cinque Lune             -> TEXT : Five Moons Square
  Point  9/22: Continue onto Piazza di Tor Sanguigna                -> TEXT : Tor Sanguigna
  Point 10/22: Continue onto V. dei Coronari                        -> TEXT : Via dei Coronari
  Point 11/22: Turn right onto Via di Panico                        -> MUSIC: Approaching the Cosmic Horizon
  Point 12/22: Turn left onto Piazza di Ponte S. Angelo             -> TEXT : Castel Sant'Angelo
  Point 13/22: Continue onto Lungotevere degli Altoviti             -> TEXT : Lungotevere degli Altoviti
  Point 14/22: Turn right onto Ponte Vittorio Emanuele II           -> TEXT : Ponte Vittorio Emanuele II
  Point 15/22: Continue onto Via San Pio X                          -> TEXT : Borgo Santo Spirito
  Point 16/22: Turn left onto Borgo Santo Spirito                   -> TEXT : Borgo Santo Spirito
  Point 17/22: Borgo Santo Spirito → Via Paolo VI (Vatican City)    -> TEXT : Via Paolo VI
  Point 18/22: Slight right onto Border Path                        -> TEXT : Road
  Point 19/22: Continue onto P.za Santa Marta                       -> TEXT : History of Croatia
  Point 20/22: Slight right toward P.za Santa Marta                 -> TEXT : History of Croatia
  Point 21/22: Slight right onto Via delle Fondamenta               -> TEXT : Via delle Fondamenta
  Point 22/22: 00120, Vatican City                                  -> TEXT : Index of Vatican City-related articles
========================================================================================================================
Complete! Processed 22/22 points. Check log file for details.

Enter Google Maps URL (or 'stop' to exit): stop

Stopping tour guide...

Goodbye!
```

### Example 2: Debug Mode

```
$ python tour_guide.py --log-level DEBUG --log-file debug.log
======================================================================
AI Tour Guide - Multimedia Content Generator
======================================================================
Enter Google Maps walking route URLs to process.
Type 'stop' to exit the program.
======================================================================

Enter Google Maps URL (or 'stop' to exit): https://maps.app.goo.gl/FpTzPfHX6F1HPt7T8
...
```

Debug log file (`debug.log`) contains detailed agent execution:
```
2025-12-14 19:32:22 - (run_20251214_193220_1, Orchestrator, Initialized with 10 workers)
2025-12-14 19:32:22 - (run_20251214_193220_1, Orchestrator, Processing 22 points)
2025-12-14 19:32:22 - (run_20251214_193220_1, YouTubeAgent, Search query: west on Piazza della Rotonda)
2025-12-14 19:32:23 - (run_20251214_193220_1, SpotifyAgent, Found track: Glaciara by Sangenjaya)
2025-12-14 19:32:24 - (run_20251214_193220_1, TextAgent, Found article: Piazza della Rotonda)
2025-12-14 19:32:26 - (run_20251214_193220_1, JudgeAgent, TextAgent (text): score=95.0)
2025-12-14 19:32:26 - (run_20251214_193220_1, JudgeAgent, Selected text from TextAgent)
```

### Example 3: Missing API Key

```
$ python tour_guide.py
ERROR: GOOGLE_MAPS_API_KEY not found in environment variables
Please set it in your .env file
```

### Example 4: Invalid URL Input

```
Enter Google Maps URL (or 'stop' to exit): not-a-url
ERROR: Input doesn't look like a URL. Please enter a Google Maps URL.
```

### Example 5: Failed Route Extraction

```
Enter Google Maps URL (or 'stop' to exit): https://maps.google.com/maps/dir/InvalidPlace/NowhereCity

Got map URL: https://maps.google.com/maps/dir/InvalidPlace/NowhereCity
ERROR: Failed to extract route points: Could not extract origin and destination from URL
```

### Example 6: Keyboard Interrupt

```
Enter Google Maps URL (or 'stop' to exit): https://maps.app.goo.gl/FpTzPfHX6F1HPt7T8
Processing...

^C

Interrupted by user. Stopping...

Goodbye!
```

### Example 7: Programmatic Usage

```python
from dotenv import load_dotenv
from src.api.google_maps import GoogleMapsClient
from src.orchestrator import Orchestrator
import os

load_dotenv()
client = GoogleMapsClient(api_key=os.getenv('GOOGLE_MAPS_API_KEY'), run_id="demo")
points = client.extract_route_points_from_url("https://maps.app.goo.gl/FpTzPfHX6F1HPt7T8")

orchestrator = Orchestrator(
    run_id="demo",
    youtube_api_key=os.getenv('YOUTUBE_API_KEY'),
    spotify_client_id=os.getenv('SPOTIFY_CLIENT_ID'),
    spotify_client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
)
decisions = orchestrator.process_points(points)

for point in points:
    decision = decisions.get(point.point_id)
    if decision:
        print(f"{point.location_name}: {decision.selected_content_type} - {decision.selected_content.get('title')}")

orchestrator.shutdown()
```

## Sequence Diagram: Per-Point Processing

```
User          CLI          GoogleMaps       Orchestrator     YouTube   Spotify   Text     Judge
 │             │               │                │              │         │        │         │
 │──URL──────►│               │                │              │         │        │         │
 │             │──expand URL──►│                │              │         │        │         │
 │             │◄─full URL────│                │              │         │        │         │
 │             │──directions──►│                │              │         │        │         │
 │             │◄─List[Point]─│                │              │         │        │         │
 │             │               │──points───────►│              │         │        │         │
 │             │               │                │──search(p)──►│         │        │         │
 │             │               │                │──search(p)──►│─────────►        │         │
 │             │               │                │──search(p)──►│─────────│────────►         │
 │             │               │                │◄─AgentResult─┤         │        │         │
 │             │               │                │◄─AgentResult─┤─────────┤        │         │
 │             │               │                │◄─AgentResult─┤─────────┤────────┤         │
 │             │               │                │──judge(results)──────────────────────────►│
 │             │               │                │◄─JudgeDecision───────────────────────────┤
 │             │◄──summary─────│────────────────┤              │         │        │         │
 │◄─table──────┤               │                │              │         │        │         │
```

## Configuration

### Environment Variables (.env)

```bash
# Required - route extraction
GOOGLE_MAPS_API_KEY=your_api_key_here

# Optional - video search (skipped if missing)
YOUTUBE_API_KEY=your_api_key_here

# Optional - music search (skipped if missing)
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
```

See [API_SETUP.md](../API_SETUP.md) for how to obtain these keys.

## Output Channels

| Channel | Content | Destination |
|---------|---------|-------------|
| Console (stdout) | Welcome banner, progress, summary table, errors | Terminal |
| Log file | All agent activity in structured format | `tour_guide.log` (default) |

The console is kept minimal — only task counts, the summary table, and errors. All detailed agent execution (queries, scores, reasoning) goes to the log file.

## Accessibility Notes

- No color or ANSI codes are used — output works on all terminals
- Summary table uses fixed-width formatting for alignment
- Error messages are prefixed with `ERROR:` for screen reader clarity
- The interactive loop accepts `stop` (case-insensitive) to exit
- Ctrl+C is handled gracefully with a clean shutdown message
