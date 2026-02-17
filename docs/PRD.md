# Product Requirements Document: AI Tour Guide Orchestration System

## 1. Goals

- **Primary**: Automatically generate enriched multimedia tour content for any Google Maps walking route
- **Technical**: Demonstrate multi-agent orchestration with concurrent processing and queue-based coordination
- **Scalability**: Support multiple simultaneous tours via thread-safe architecture

## 2. User Stories

- As a tour organizer, I provide a Google Maps route and receive the best content recommendation for each stop
- As a system operator, I run multiple tours simultaneously without performance degradation
- As a developer, I use structured logging to debug and monitor agent operations

## 3. System Architecture

```
Google Maps URL
    |
    v
Google Maps Directions API --> List[Point]
    |
    v
Orchestrator (ThreadPoolExecutor + PriorityQueue)
    |
    +---> YouTubeAgent  --\
    +---> SpotifyAgent  ---+--> JudgeAgent --> JudgeDecision
    +---> TextAgent     --/
    |
    v
Collected results per point --> Console summary + log file
```

### 3.1 Input Handler (GoogleMapsClient)

- Accepts full or shortened (`maps.app.goo.gl`) Google Maps URLs
- Uses Directions API (mode=walking) to get the complete route
- Extracts **every step** along the path (turns, streets, direction changes) as `Point` objects

### 3.2 Orchestrator

- `ThreadPoolExecutor` with configurable worker count (default: 10)
- `PriorityQueue` where judge tasks (priority=1) run before search tasks (priority=2)
- Thread-safe result storage via `threading.Lock`
- Workflow per point: 3 search agents run -> results collected -> judge evaluates -> decision stored

### 3.3 Agents

| Agent | API | Strategy |
|-------|-----|----------|
| **YouTubeAgent** | YouTube Data API v3 | Filters navigation words from query; falls back to city-based search |
| **SpotifyAgent** | Spotify Web API | Appends "instrumental ambient" to queries; falls back to generic ambient |
| **TextAgent** | Wikipedia REST API | 3-tier fallback: location-context search -> direct lookup -> search API |
| **JudgeAgent** | None (local scoring) | Scores on: content existence, title relevance, description length, content type preference (text > video > music), URL availability |

### 3.4 CLI Entry Point (tour_guide.py)

- Interactive loop accepting URLs until user types `stop`
- Logs detailed reasoning to file; prints point summaries to console
- Configurable log level and log file path via CLI args

## 4. Data Structures

### Point

```python
@dataclass
class Point:
    run_id: str
    point_id: str
    location_name: str
    coordinates: Coordinates  # lat: float, lng: float
    order: int
    place_id: Optional[str]
    address: Optional[str]
```

### AgentResult

```python
@dataclass
class AgentResult:
    run_id: str
    point_id: str
    agent_name: str
    content_type: Literal["video", "music", "text"]
    content: dict       # Keys vary by agent (title, url, description, ...)
    timestamp: datetime
    success: bool
    error_message: Optional[str]
```

### JudgeDecision

```python
@dataclass
class JudgeDecision:
    run_id: str
    point_id: str
    selected_content_type: Literal["video", "music", "text"]
    selected_content: dict
    reasoning: str
    timestamp: datetime
    all_results: list[AgentResult]
```

## 5. Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | Extract route points from Google Maps URL (including shortened URLs) | P0 |
| FR-2 | Launch 3 search agents + 1 judge agent per point | P0 |
| FR-3 | YouTube agent returns top relevant video | P0 |
| FR-4 | Spotify agent returns top relevant track | P0 |
| FR-5 | Text agent returns Wikipedia summary | P0 |
| FR-6 | Judge agent selects best content with reasoning | P0 |
| FR-7 | Orchestrator coordinates concurrent execution via priority queue | P0 |
| FR-8 | Interactive CLI accepts multiple URLs in a session | P0 |
| FR-9 | All operations logged in `(run_id, agent_name, message)` format | P0 |

## 6. Non-Functional Requirements

### Performance
- At least 4 concurrent map processing runs supported
- Agent execution parallelized via thread pool
- API calls have 5-second timeouts

### Reliability
- Agent failures do not crash the system; failed points are logged and skipped
- Graceful handling of API rate limits and invalid responses

### Observability
- Each run identified by unique `run_id`
- Log levels: DEBUG (detailed data), INFO (operations), WARNING (degraded/fallback), ERROR (failures)

## 7. Design Decisions

| Decision | Rationale |
|----------|-----------|
| Multi-threading over multiprocessing | I/O-bound workload (API calls); lower overhead; GIL not a bottleneck |
| PriorityQueue for tasks | Judge tasks depend on search results; prioritizing them reduces end-to-end latency |
| Wikipedia 3-tier fallback | Direct lookups often fail or hit disambiguation pages; location context improves specificity |
| Interactive CLI over web UI | Simpler for educational demo; easy to extend later |

## 8. Success Metrics

- Processes routes with 5-50+ points
- All 4 agents execute for each point
- Judge selects content for >95% of points
- Multiple maps run concurrently without conflicts
- Logs provide clear audit trail

## 9. Out of Scope

- Web/mobile UI
- Real-time location tracking
- User preferences or personalization
- Content caching or persistent storage
- Multi-language support
- Audio playback or video streaming

## 10. Future Enhancements

- ML-based judge using preference learning
- Content caching to reduce API quota usage
- User feedback loop for judge improvement
- Web interface for route submission
- Export to PDF / audio guide format
- Batch processing from file input
