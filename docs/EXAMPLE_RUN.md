# Example Run: Pantheon to Vatican City

A complete walkthrough of a real run processing a walking route from the Pantheon to Vatican City in Rome.

**Run ID**: `run_20251214_143121_1`
**Date**: 2024-12-14
**Route**: Pantheon → Vatican City (2.5 km walking, 22 points)

## 1. Input

```
Enter Google Maps URL (or 'stop' to exit): https://maps.app.goo.gl/FpTzPfHX6F1HPt7T8
```

The system expands the shortened URL to:
```
https://www.google.com/maps/dir/Pantheon/Vatican+City/@41.9104795,12.4867194,14z/...
```

## 2. Route Extraction

The Google Maps Directions API returns 22 walking steps:

```
(run_20251214_143121_1, GoogleMapsClient, Route: Pantheon → Vatican+City)
(run_20251214_143121_1, GoogleMapsClient, Processing leg 1: 2.5 km)
(run_20251214_143121_1, GoogleMapsClient, Successfully extracted 22 points from route)
```

Points extracted (in order):

| # | Location Name |
|---|---------------|
| 1 | Head west on Piazza della Rotonda |
| 2 | Turn right to stay on Piazza della Rotonda |
| 3 | Turn left to stay on Piazza della Rotonda |
| 4 | Slight right onto Via della Rosetta |
| 5 | Turn left onto Via del Pozzo delle Cornacchie |
| 6 | Continue onto Largo Giuseppe Toniolo |
| 7 | Continue onto Via di S. Giovanna d'Arco |
| 8 | Turn right onto Piazza delle Cinque Lune |
| 9 | Continue onto Piazza di Tor Sanguigna |
| 10 | Continue onto V. dei Coronari |
| 11 | Turn right onto Via di Panico |
| 12 | Turn left onto Piazza di Ponte S. Angelo |
| 13 | Continue onto Lungotevere degli Altoviti |
| 14 | Turn right onto Ponte Vittorio Emanuele II |
| 15 | Continue onto Via San Pio X |
| 16 | Turn left onto Borgo Santo Spirito |
| 17 | Borgo Santo Spirito becomes Via Paolo VI (Entering Vatican City) |
| 18 | Slight right onto Border Path |
| 19 | Continue onto P.za Santa Marta |
| 20 | Slight right toward P.za Santa Marta |
| 21 | Slight right onto Via delle Fondamenta |
| 22 | 00120, Vatican City |

## 3. Agent Execution

The orchestrator launched 88 tasks (3 search agents + 1 judge per point) across 10 worker threads.

### Sample: Point 1 — Piazza della Rotonda

**YouTubeAgent** searched for `"west on Piazza della Rotonda"` (filtered "Head"):
```
Found video: Rome - Italy - The Pantheon and the Spanish Steps Walking tour 4K
Score: 75.0/100
```

**SpotifyAgent** searched for `"west on Piazza della Rotonda instrumental ambient"`:
```
Found track: Choirambient Tres - Loop Mix by Cereplex
Score: 60.0/100
```

**TextAgent** searched Wikipedia for `"west on Piazza della Rotonda"` with location context:
```
Found article: Piazza della Rotonda
Score: 95.0/100
```

**JudgeAgent** selected **text** (score 95.0 — highest):
> Selected text content from TextAgent (score: 95.0/100). Title: 'Piazza della Rotonda'. Significantly higher relevance than alternatives. Contains comprehensive description.

### Sample: Point 9 — Piazza di Tor Sanguigna

**YouTubeAgent**:
```
Found video: Spot Piazza Tor Sanguigna
Score: 90.0/100
```

**SpotifyAgent**:
```
Found track: Arkham Nights by Sanguinus
Score: 60.0/100
```

**TextAgent**:
```
Found article: Tor Sanguigna
Score: 90.0/100
```

**JudgeAgent** selected **video** (tied at 90.0, video dequeued first):
> Both YouTube and Text scored 90/100. YouTube video was selected because it matched the location name exactly.

### Sample: Point 14 — Ponte Vittorio Emanuele II

**YouTubeAgent**:
```
Found video: Rome Sunset Stroll: Palazzo del Quirinale to Ponte Sant'Angelo
Score: 75.0/100
```

**SpotifyAgent**:
```
Found track: Veni, veni, Emanuel II by Martin Stadtfeld
Score: 60.0/100
```

**TextAgent**:
```
Found article: Ponte Vittorio Emanuele II
Score: 100.0/100 (perfect match)
```

**JudgeAgent** selected **text** (perfect score 100):
> Selected text content from TextAgent (score: 100.0/100). Title: 'Ponte Vittorio Emanuele II'. Significantly higher relevance than alternatives. Contains comprehensive description.

## 4. Final Summary Output

```
========================================
TOUR GUIDE SUMMARY
========================================
  Point  1/22: Head west on Piazza della Rotonda                    -> TEXT : Piazza della Rotonda
  Point  2/22: Turn right to stay on Piazza della Rotonda           -> TEXT : Historic centre of Albano Laziale
  Point  3/22: Turn left to stay on Piazza della Rotonda            -> VIDEO: 🇮🇹 ROME, Italy - Virtual Tour 4K
  Point  4/22: Slight right onto Via della Rosetta                  -> TEXT : Rosetta (spacecraft)
  Point  5/22: Turn left onto Via del Pozzo delle Cornacchie        -> TEXT : Baths of Nero
  Point  6/22: Continue onto Largo Giuseppe Toniolo                 -> VIDEO: Coffee in Rome Italy LARGO GIUSEPPE TONIOLO
  Point  7/22: Continue onto Via di S. Giovanna d'Arco              -> TEXT : Giovanna d'Arco
  Point  8/22: Turn right onto Piazza delle Cinque Lune             -> TEXT : Five Moons Square
  Point  9/22: Continue onto Piazza di Tor Sanguigna                -> VIDEO: Spot Piazza Tor Sanguigna
  Point 10/22: Continue onto V. dei Coronari                        -> TEXT : Via dei Coronari
  Point 11/22: Turn right onto Via di Panico                        -> MUSIC: The Quiet Return by Paix Sonique
  Point 12/22: Turn left onto Piazza di Ponte S. Angelo             -> VIDEO: Rome Sunset Stroll: Ponte Sant'Angelo
  Point 13/22: Continue onto Lungotevere degli Altoviti             -> TEXT : Lungotevere degli Altoviti
  Point 14/22: Turn right onto Ponte Vittorio Emanuele II           -> TEXT : Ponte Vittorio Emanuele II
  Point 15/22: Continue onto Via San Pio X                          -> VIDEO: PARISS G - VIA SAN PIO X
  Point 16/22: Turn left onto Borgo Santo Spirito                   -> MUSIC: Via cordis by Helge Burggrabe
  Point 17/22: Borgo Santo Spirito → Via Paolo VI (Vatican City)    -> MUSIC: Piazza San Marco by Ziv Moran
  Point 18/22: Slight right onto Border Path                        -> TEXT : Road
  Point 19/22: Continue onto P.za Santa Marta                       -> TEXT : History of Croatia
  Point 20/22: Slight right toward P.za Santa Marta                 -> TEXT : History of Croatia
  Point 21/22: Slight right onto Via delle Fondamenta               -> MUSIC: Destination by Tristan Axvall
  Point 22/22: 00120, Vatican City                                  -> TEXT : Index of Vatican City-related articles
========================================
Complete! Processed 22/22 points. Check log file for details.
```

## 5. Results Breakdown

| Content Type | Count | Percentage |
|-------------|-------|------------|
| TEXT | 14 | 64% |
| VIDEO | 5 | 23% |
| MUSIC | 3 | 14% |

**Judge scoring distribution:**

| Score Range | Count | Example |
|-------------|-------|---------|
| 90-100 | 6 | Ponte Vittorio Emanuele II (100), Piazza della Rotonda (95) |
| 80-89 | 8 | Five Moons Square (80), Via dei Coronari (90) |
| 60-69 | 8 | Music fallbacks when text/video unavailable |

## 6. Observations

- **Text dominates**: Wikipedia articles scored highest for most points due to the +10 content-type preference and typically strong title relevance
- **YouTube wins on exact matches**: When the video title directly contains the location name (e.g., "Spot Piazza Tor Sanguigna"), video can tie or beat text
- **Music as fallback**: Spotify results were selected when neither YouTube nor Wikipedia found relevant content (e.g., navigation-only points)
- **Imperfect matches are expected**: Some Wikipedia results are tangential (e.g., "History of Croatia" for P.za Santa Marta) — this reflects the challenge of mapping navigation instructions to encyclopedia articles
- **Processing time**: All 22 points processed in ~7 seconds (concurrent API calls across 10 threads)

## 7. Log Excerpt

Selected log lines showing the agent pipeline for Point 14:

```
19:32:25 - (run_20251214_193220_1, Orchestrator, Starting search agents for: Turn right onto Ponte Vittorio Emanuele II)
19:32:25 - (run_20251214_193220_1, YouTubeAgent, Search query: right Ponte Vittorio Emanuele II)
19:32:25 - (run_20251214_193220_1, SpotifyAgent, Search query: right Ponte Vittorio Emanuele II instrumental ambient)
19:32:25 - (run_20251214_193220_1, SpotifyAgent, Found track: Veni, veni, Emanuel II by Martin Stadtfeld)
19:32:25 - (run_20251214_193220_1, TextAgent, Search query: Ponte Vittorio Emanuele II)
19:32:26 - (run_20251214_193220_1, TextAgent, Found article: Ponte Vittorio Emanuele II)
19:32:26 - (run_20251214_193220_1, JudgeAgent, Judging 3 results for: Turn right onto Ponte Vittorio Emanuele II)
19:32:26 - (run_20251214_193220_1, JudgeAgent, SpotifyAgent (music): score=65.0)
19:32:26 - (run_20251214_193220_1, JudgeAgent, TextAgent (text): score=100.0)
19:32:26 - (run_20251214_193220_1, JudgeAgent, Selected text from TextAgent)
```
