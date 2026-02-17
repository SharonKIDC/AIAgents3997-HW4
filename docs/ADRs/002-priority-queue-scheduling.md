# ADR-002: Priority Queue Scheduling

## Status
Accepted

## Context
The orchestrator must coordinate search agents and the judge agent per point. Judge tasks depend on search results being available. A naive approach would process all searches first, then all judges, but this increases end-to-end latency.

## Decision
Use `queue.PriorityQueue` where judge tasks (priority=1) are dequeued before search tasks (priority=2).

## Rationale
- As soon as a point's search agents complete, a judge task is enqueued at higher priority
- Worker threads pick up judge tasks before starting searches for new points
- This reduces the time between search completion and judge execution for each point
- Ties within the same priority level are broken by timestamp (FIFO)

## Consequences
- Points that finish searching early get judged early, freeing memory
- The system does not need an explicit two-phase pipeline
- If the queue is empty, workers block on `get(timeout=1)` and retry
