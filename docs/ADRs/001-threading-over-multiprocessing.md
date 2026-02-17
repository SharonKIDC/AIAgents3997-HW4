# ADR-001: Threading Over Multiprocessing

## Status
Accepted

## Context
The orchestrator needs to run multiple agents concurrently for each route point. Python offers `threading`, `multiprocessing`, and `asyncio` as concurrency models.

## Decision
Use `concurrent.futures.ThreadPoolExecutor` with `queue.PriorityQueue`.

## Rationale
- All agent work is I/O-bound (HTTP API calls to YouTube, Spotify, Wikipedia, Google Maps)
- The GIL does not block I/O operations, so threads achieve true concurrency for this workload
- Threads share memory, making it simple to collect results into shared dictionaries with a `threading.Lock`
- `multiprocessing` would add IPC overhead and serialization cost for no benefit on I/O-bound work
- `asyncio` would require async HTTP libraries and rewriting all agent code; the synchronous `googlemaps`, `spotipy`, and `google-api-python-client` SDKs would need wrappers

## Consequences
- Simple, well-understood concurrency model
- `PriorityQueue` scheduling works naturally with threads
- Thread count is configurable (default 10 workers)
- If CPU-bound work is added later (e.g., ML-based judge), multiprocessing may need to be reconsidered
