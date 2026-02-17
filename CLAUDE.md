# CLAUDE.md

Developer guidance for Claude Code when working in this repository.

## Project Overview

AI Tour Guide Orchestration System — a multi-agent system that finds multimedia content for points along a Google Maps walking route. See [PRD.md](PRD.md) for full requirements and architecture.

## Dev Environment

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # Then add API keys (see API_SETUP.md)
```

## Running

```bash
python tour_guide.py                   # Interactive CLI
python tour_guide.py --log-level DEBUG # Verbose
pytest tests/ -v                       # All tests
```

## Logging Requirements

All agents **must** use Python's `logging` module with this format:

```
(run_id, agent_name, message)
```

Log levels:
- `INFO`: Normal operations (agent start, completion, API calls)
- `WARNING`: Degraded performance, fallback scenarios, rate limiting
- `ERROR`: Failures, exceptions, unrecoverable states
- `DEBUG`: Detailed operational data for troubleshooting

Example:
```python
logging.info(f"({run_id}, YouTubeAgent, Searching for videos about {location_name})")
```

## Code Quality

- Use type hints consistently
- Handle API failures gracefully (timeouts, rate limits)
- Never commit `.env` or API keys
