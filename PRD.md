# Product Requirements Document: AI Tour Guide Orchestration System

## 1. Overview

An AI-powered tour guide system that automatically enriches location-based tours by orchestrating multiple agents to find and select the best multimedia content (videos, music, text) for **every point** along a walking route.

**Important**: The system extracts ALL points along the route path (every turn, street, direction change), not just the start/end waypoints. This provides comprehensive content for the entire journey.

## 2. Goals & Objectives

- **Primary Goal**: Automatically generate enriched tour content for any given route
- **Key Objective**: Demonstrate multi-agent orchestration with concurrent processing
- **Technical Objective**: Implement a scalable queue-based architecture supporting multiple simultaneous tours

## 3. User Stories

- As a tour organizer, I want to provide a Google Maps route and automatically receive the best content recommendations for each stop
- As a system operator, I want to run multiple tours simultaneously without performance degradation
- As a developer, I want comprehensive logging to debug and monitor agent operations

## 4. System Architecture

### 4.1 High-Level Flow

```
Input (Google Maps Route)
    ↓
Google Maps API Integration (extract points)
    ↓
Point Queue Creation
    ↓
Orchestrator (manages agent lifecycle)
    ↓
4 Concurrent Agents per Point:
    - YouTube Search Agent
    - Spotify Search Agent
    - Text Search Agent
    - Judge Agent
    ↓
Result Queue
    ↓
Collector (aggregates judge decisions)
    ↓
Output (best content per point)
```

### 4.2 Component Details

#### 4.2.1 Input Handler (Google Maps Integration)
- Accepts Google Maps URLs including shortened URLs (e.g., https://maps.app.goo.gl/...)
- Automatically expands shortened URLs to full URLs
- Extracts origin and destination from URL
- Uses Google Maps **Directions API** to get complete walking route
- **Scope**: Extracts ALL points along the route (every step, turn, direction change)
- Returns list of Point objects with:
  - Step-by-step instructions (e.g., "Turn left onto Via della Rosetta")
  - Coordinates for each point
  - Street names and addresses
  - Order in the route

#### 4.2.2 Orchestrator (Implemented)
- **Multi-threaded execution**: Uses ThreadPoolExecutor for concurrent agent processing
- **Priority-based task queue**: PriorityQueue with judge tasks at higher priority than search tasks
- **Thread-safe operations**: Thread-safe queues, logging, and result collection
- Launches 3 search agents + 1 judge agent per point
- Manages agent lifecycle and coordination
- Handles agent failures and errors gracefully
- Collects and aggregates results by point_id

#### 4.2.4 Agent Types

**Agent 1: YouTube Search Agent**
- Searches YouTube API for videos relevant to the location point
- Returns top video recommendation with metadata (title, URL, duration, description)

**Agent 2: Spotify Search Agent**
- Searches Spotify API for songs/playlists relevant to the location point
- Returns top song recommendation with metadata (title, artist, URL)

**Agent 3: Text Search Agent**
- Searches for textual descriptions of the location
- Sources could include: Wikipedia API, travel guides, or web scraping
- Returns formatted text description

**Agent 4: Judge Agent**
- Evaluates outputs from Agents 1-3
- Selects the best content based on relevance, quality, and user experience
- Outputs decision with reasoning

#### 4.2.5 Main Entry Point (tour_guide.py)
- **Interactive CLI**: Continuous operation mode accepting multiple URLs
- Accepts Google Maps URLs from user input
- Processes each URL through the orchestrator
- Displays formatted judge decisions for each point to console
- Supports configurable log levels (DEBUG, INFO, WARNING, ERROR)
- Thread-safe logging to shared log file
- Graceful shutdown on 'stop' command

## 5. Functional Requirements

### 5.1 Core Functionality

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | System shall integrate with Google Maps API to extract route points | P0 |
| FR-2 | System shall create a queue of points from each route | P0 |
| FR-3 | Orchestrator shall launch 4 agents per point | P0 |
| FR-4 | YouTube agent shall search and return relevant video | P0 |
| FR-5 | Spotify agent shall search and return relevant song | P0 |
| FR-6 | Text agent shall search and return relevant description | P0 |
| FR-7 | Judge agent shall select best content from 3 options | P0 |
| FR-8 | All agents shall write operations to queue | P0 |
| FR-9 | Collector shall aggregate judge results per map | P0 |
| FR-10 | System shall support multiple concurrent map processing | P0 |

### 5.2 Logging Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| LG-1 | All agents must use Python logging package | P0 |
| LG-2 | Log format: `(run_id, agent_name, message)` | P0 |
| LG-3 | Use appropriate log levels: INFO, WARNING, ERROR, DEBUG | P0 |
| LG-4 | INFO: Normal operations (agent start, completion, API calls) | P0 |
| LG-5 | WARNING: Degraded performance, fallback scenarios | P0 |
| LG-6 | ERROR: Failures, exceptions, unrecoverable states | P0 |
| LG-7 | DEBUG: Detailed operational data for troubleshooting | P1 |

## 6. Technical Requirements

### 6.1 APIs & Integrations

- **Google Maps API**:
  - **Directions API** (primary) for getting complete walking routes with all steps
  - Supports shortened URLs (maps.app.goo.gl) with automatic expansion
  - Extracts every point, turn, and direction change along the route
- **YouTube Data API v3**: Search endpoint for video discovery
- **Spotify Web API**: Search endpoint for music discovery
- **Text Sources**: Wikipedia API, or alternative text content sources

### 6.2 Technology Stack

- **Language**: Python 3.12+
- **Queue System**: Python `queue.Queue` or similar thread-safe queue implementation
- **Logging**: Python standard `logging` module
- **Concurrency**: Threading or asyncio for agent orchestration
- **API Clients**: `requests` or specialized client libraries (google-api-python-client, spotipy, etc.)

### 6.3 Data Structures

**Point Object**:
```python
{
    "run_id": str,
    "point_id": str,
    "location_name": str,
    "coordinates": {"lat": float, "lng": float},
    "order": int
}
```

**Agent Result Object**:
```python
{
    "run_id": str,
    "point_id": str,
    "agent_name": str,
    "content_type": str,  # "video", "music", "text"
    "content": {
        "title": str,
        "url": str,
        "description": str,
        # additional metadata
    },
    "timestamp": datetime
}
```

**Judge Decision Object**:
```python
{
    "run_id": str,
    "point_id": str,
    "selected_content_type": str,
    "selected_content": dict,
    "reasoning": str,
    "timestamp": datetime
}
```

## 7. Non-Functional Requirements

### 7.1 Performance

- Support at least 4 concurrent map processing runs
- Agent execution should be parallelized where possible
- API calls should have appropriate timeouts and retry logic

### 7.2 Reliability

- Graceful handling of API failures (rate limits, timeouts, invalid responses)
- Agent failures should not crash the entire system
- Failed points should be logged and skipped or retried

### 7.3 Observability

- Comprehensive logging at all stages
- Each run identifiable by unique `run_id`
- Clear error messages for debugging

## 8. Success Metrics

- System successfully processes routes with 5-10 points
- All 4 agents execute for each point
- Judge makes selection for >95% of points
- Collector produces complete output for each map
- Multiple maps can run concurrently without conflicts
- Logs provide clear audit trail of all operations

## 9. Out of Scope (for initial version)

- User interface (web/mobile app)
- Real-time location tracking
- User preferences or personalization
- Content caching or storage
- Multi-language support
- Audio playback or video streaming integration
- Route optimization or modification

## 10. Assumptions & Dependencies

- Valid Google Maps API key available (with **Directions API** enabled)
- Valid YouTube API key available
- Valid Spotify API credentials available
- Internet connectivity for API calls
- Routes are walking routes (mode=walking)
- API rate limits are sufficient for expected usage
- URLs can be shortened (maps.app.goo.gl) or full Google Maps URLs

## 10.1 How to Get Google Maps API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - **Directions API** (required) - for getting walking routes
   - Geocoding API (optional, for reverse geocoding)
4. Go to "Credentials" and click "Create Credentials" → "API Key"
5. Copy the API key and add it to your `.env` file as `GOOGLE_MAPS_API_KEY`
6. (Recommended) Restrict the API key to only the required APIs for security

## 11. Future Enhancements

- Machine learning-based judge agent using preference learning
- Content caching to reduce API calls
- User feedback loop to improve judge decisions
- Web interface for route submission and result viewing
- Export results to various formats (PDF, audio guide, mobile app)
- Real-time updates as user progresses through tour
