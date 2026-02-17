# Architecture

## Overview

The AI Tour Guide is a multi-agent orchestration system that processes Google Maps walking routes and enriches each point with multimedia content. The system uses a thread-pool executor with priority-queue scheduling to coordinate four specialized agents per route point.

## System Diagram

```
Google Maps URL (full or shortened)
    |
    v
GoogleMapsClient
    |  - Expands shortened URLs (maps.app.goo.gl)
    |  - Calls Directions API (mode=walking)
    |  - Extracts Point objects from every step
    v
List[Point]
    |
    v
Orchestrator (ThreadPoolExecutor, max_workers=10)
    |
    |  PriorityQueue scheduling:
    |    priority=2 (search) -> priority=1 (judge)
    |
    +---> YouTubeAgent   ── YouTube Data API v3
    +---> SpotifyAgent   ── Spotify Web API
    +---> TextAgent      ── Wikipedia REST API
    |         |
    |         v
    |    List[AgentResult] per point
    |         |
    +---> JudgeAgent (local scoring, no external API)
              |
              v
         JudgeDecision per point
              |
              v
         Console summary + log file
```

## Module Map

```
tour_guide.py                  # CLI entry point, logging setup, interactive loop
src/
  __init__.py
  orchestrator.py              # ThreadPoolExecutor + PriorityQueue coordination
  api/
    __init__.py
    google_maps.py             # Route extraction via Directions API
  agents/
    __init__.py
    base_agent.py              # ABC with logging helpers and result factory
    youtube_agent.py           # YouTube Data API v3 search
    spotify_agent.py           # Spotify Web API (spotipy) search
    text_agent.py              # Wikipedia REST API with 3-tier fallback
    judge_agent.py             # Deterministic scoring and selection
  models/
    __init__.py
    point.py                   # Point, Coordinates dataclasses
    agent_result.py            # AgentResult, JudgeDecision dataclasses
tests/
  __init__.py
  test_google_maps.py
  test_youtube_agent.py
  test_spotify_agent.py
  test_text_agent.py
  test_judge_agent.py
examples/
  example_route.py             # Route extraction demo
  example_agents.py            # Full agent pipeline demo
```

## Data Flow

### 1. Input Handling

`GoogleMapsClient.extract_route_points_from_url()`:
1. Detects shortened URLs (`maps.app.goo.gl`) and follows redirects
2. Parses `/dir/{origin}/{destination}` from the expanded URL
3. Calls `client.directions(origin, destination, mode="walking")`
4. Iterates every step in every leg, extracting `Point` objects with coordinates, cleaned HTML instructions as location names, and step ordering

### 2. Orchestration

`Orchestrator.process_points()`:
1. Enqueues one search `Task(priority=2)` per point
2. Worker threads pull tasks from `PriorityQueue`
3. Search task runs all three agents sequentially within a single thread (`_execute_search_agents`)
4. On completion, enqueues a judge `Task(priority=1)` for the same point
5. Judge tasks are dequeued before remaining search tasks (lower priority number = higher priority)
6. Results stored in `results_by_point` / `decisions_by_point` dicts protected by `threading.Lock`

### 3. Agent Execution

Each search agent follows the same pattern (via `BaseAgent`):
1. Clean the location name (remove navigation words like "turn", "head", "continue")
2. Call external API with the cleaned query
3. If no results, apply a fallback strategy (city-based search, generic query, search API)
4. Return `AgentResult` with content dict and success flag

Agent-specific strategies:
- **YouTubeAgent**: Filters navigation words; falls back to city extracted from address
- **SpotifyAgent**: Appends "instrumental ambient" to query; falls back to generic ambient
- **TextAgent**: 3-tier fallback: location-context Wikipedia search -> direct page lookup -> search API

### 4. Judging

`JudgeAgent.judge()` scores each successful `AgentResult` on:
- Content existence (30 pts)
- Title presence (20 pts)
- Title-location keyword overlap (up to 20 pts)
- Description presence (15 pts)
- Content type preference: text +10, video +5, music +5
- URL availability (5 pts)

Maximum score: 100. Highest-scoring result wins.

## Concurrency Model

- **Threading**: `ThreadPoolExecutor` with configurable worker count (default 10)
- **Scheduling**: `PriorityQueue` ensures judge tasks run before search tasks
- **Thread safety**: `threading.Lock` protects shared result dictionaries
- **I/O-bound**: All external work is HTTP API calls; GIL is not a bottleneck

## Key Design Decisions

See [ADRs/](ADRs/) for detailed records. Summary:

| Decision | Rationale |
|----------|-----------|
| Multi-threading over multiprocessing | I/O-bound workload; lower overhead |
| PriorityQueue | Judge tasks depend on search results; prioritizing reduces latency |
| Wikipedia 3-tier fallback | Direct lookups often hit disambiguation; location context improves specificity |
| Interactive CLI over web UI | Simpler for educational demo |
| Per-point sequential agents | Simplifies result collection; parallelism comes from processing multiple points simultaneously |

## External Dependencies

| Dependency | Purpose | API |
|------------|---------|-----|
| `googlemaps` | Route extraction | Google Maps Directions API |
| `google-api-python-client` | Video search | YouTube Data API v3 |
| `spotipy` | Music search | Spotify Web API |
| `requests` | Wikipedia queries, URL expansion | Wikipedia REST API |
| `python-dotenv` | Configuration loading | N/A |
