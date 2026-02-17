# Extensibility Plan

## Adding New Agents

All search agents extend `BaseAgent` (ABC). To add a new agent:

1. Create `src/agents/new_agent.py`:
   ```python
   from src.agents.base_agent import BaseAgent
   from src.models.point import Point
   from src.models.agent_result import AgentResult

   class NewAgent(BaseAgent):
       def __init__(self, run_id: str, ...):
           super().__init__(run_id, "NewAgent")

       def search(self, point: Point) -> AgentResult:
           # Implement search logic
           return self.create_result(point, content_type="...", content={...})
   ```

2. Register in `Orchestrator._execute_search_agents()` alongside YouTube, Spotify, and Text agents

3. Add the new content type to the `JudgeAgent._score_result()` type preferences

4. Add unit tests in `tests/test_new_agent.py`

## Replacing the Judge

The current `JudgeAgent` uses deterministic scoring. To replace it:

- Implement a new class with a `judge(point, results) -> JudgeDecision` method
- Swap it in `Orchestrator._execute_judge_agent()`
- Possible approaches: LLM-based judge, user preference learning, A/B testing framework

## Adding a Web UI

The CLI could be replaced or supplemented with a web interface:

1. Add Flask/FastAPI as a dependency
2. Expose `process_map_url()` as a REST endpoint
3. Return `JudgeDecision` objects as JSON
4. The orchestrator is already thread-safe and supports concurrent runs

## Batch Processing

Support processing multiple routes from a file:

1. Accept a file path via CLI argument
2. Read URLs line by line
3. Process each with a unique `run_id`
4. Output results to CSV or JSON

## Content Caching

Cache API responses to reduce quota usage:

1. Hash the query string as a cache key
2. Store responses in SQLite or Redis
3. Check cache before making API calls
4. Set TTL based on content freshness requirements

## Export Formats

Current output is console text + log file. Future formats:

- JSON export for programmatic consumption
- PDF tour guide with embedded content links
- Audio guide narration via TTS
- GPX file with multimedia annotations
