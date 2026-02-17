# ADR-004: Interactive CLI Over Web UI

## Status
Accepted

## Context
The system needs a user interface for submitting Google Maps URLs and viewing results.

## Decision
Use a terminal-based interactive CLI loop (`tour_guide.py`) instead of a web UI.

## Rationale
- Simpler to implement and test for an educational project
- No frontend framework dependencies
- Logs go to file; summaries print to console
- Easy to extend to batch mode (read URLs from file) or web UI later

## Consequences
- No web server, no static assets, no frontend build step
- Testing is straightforward (mock `input()` or use `--help` for argument validation)
- Users must run from a terminal with Python installed
