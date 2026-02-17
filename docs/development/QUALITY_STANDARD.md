# Quality Standard

## Code Standards

### Type Hints
All function signatures must include type hints for parameters and return values.

### Logging Format
All agents must use the structured format: `(run_id, agent_name, message)`

Log levels:
- `INFO`: Normal operations
- `WARNING`: Degraded performance, fallbacks
- `ERROR`: Failures, exceptions
- `DEBUG`: Detailed operational data

### Error Handling
- API calls must have timeouts (5 seconds)
- Agent failures must not crash the orchestrator
- Failed results are logged and skipped; processing continues
- Each agent returns an `AgentResult` with `success=False` on failure

### Testing
- All agents have unit tests with mocked API responses
- No real API calls during testing
- Tests cover success paths, fallback paths, and error paths

## Quality Gates

| Gate | Criteria | Status |
|------|----------|--------|
| no_secrets_in_code | No hardcoded API keys; `.env` gitignored | Pass |
| config_separation | All credentials from env vars via `dotenv` | Pass |
| example_env_present | `.env.example` exists with documented placeholders | Pass |
| tests_present | Unit tests for all agents and API client | Pass |
| edge_cases_covered | Fallback strategies tested; empty/error inputs handled | Pass |
| readme_updated | README reflects current project state | Pass |

## Dependencies

- Pin minimum versions in `requirements.txt`
- No unnecessary dependencies
- Test dependencies (`pytest`, `pytest-mock`) separated conceptually
