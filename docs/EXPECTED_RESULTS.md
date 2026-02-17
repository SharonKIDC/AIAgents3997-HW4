# Expected Results

## Typical Output

For a Rome walking route (Pantheon to Vatican City, ~22 points):

```
======================================================================
AI Tour Guide - Multimedia Content Generator
======================================================================
Enter Google Maps walking route URLs to process.
Type 'stop' to exit the program.
======================================================================

Enter Google Maps URL (or 'stop' to exit): https://maps.app.goo.gl/5A5xc4qnSdL8DcVp6

Got map URL: https://maps.app.goo.gl/5A5xc4qnSdL8DcVp6
Run ID: run_20251214_193220_1
Added 88 tasks for 22 points to orchestrator
Processing...

========================================
TOUR GUIDE SUMMARY
========================================
  Point  1/22: Head west on Piazza della Rotonda  -> TEXT : Piazza della Rotonda
  Point  2/22: Turn right to stay on Piazza ...   -> TEXT : Historic centre of Albano Laziale
  ...
  Point 22/22: 00120, Vatican City                -> TEXT : Index of Vatican City-related articles
========================================
Complete! Processed 22/22 points. Check log file for details.
```

## Agent Behavior

### YouTubeAgent
- Returns a video title, URL, description, thumbnail, and channel name
- Navigation-word filtering removes "turn", "head", "continue", etc. from queries
- Falls back to city-based search when no results found

### SpotifyAgent
- Returns a track name, artist, album, Spotify URL, and preview URL
- Appends "instrumental ambient" to all queries
- Falls back to generic "ambient instrumental" search

### TextAgent
- Returns a Wikipedia article title, extract, and URL
- 3-tier fallback: location-context search -> direct lookup -> search API
- Skips disambiguation pages automatically

### JudgeAgent
- Scores each result 0-100 based on content, title relevance, description, type preference, URL
- Text content has a +10 scoring preference (most informative for tours)
- Generates reasoning string explaining the selection

## Success Criteria

| Metric | Target |
|--------|--------|
| Points processed per route | 100% (all points get a decision) |
| Agent success rate | >95% (at least one agent succeeds per point) |
| Judge selection rate | >95% (judge produces a decision for each point with results) |
| Concurrent routes | At least 4 simultaneous tours without conflicts |
| Processing time per point | <10 seconds (dependent on API latency) |

## Test Results

All 33 tests pass with mocked API responses:
```bash
$ pytest tests/ -v
tests/test_google_maps.py    - Route extraction, URL expansion, parsing
tests/test_youtube_agent.py  - Video search, fallback, error handling
tests/test_spotify_agent.py  - Track search, fallback, error handling
tests/test_text_agent.py     - Wikipedia search, 3-tier fallback, error handling
tests/test_judge_agent.py    - Scoring, selection, edge cases
```
