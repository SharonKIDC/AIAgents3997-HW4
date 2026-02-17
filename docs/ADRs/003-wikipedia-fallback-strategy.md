# ADR-003: Wikipedia 3-Tier Fallback Strategy

## Status
Accepted

## Context
The TextAgent needs to find relevant Wikipedia articles for route points. Location names from Google Maps Directions API are often navigation instructions ("Head west on Via del Corso") rather than proper place names. Direct Wikipedia lookups frequently fail or hit disambiguation pages.

## Decision
Implement a 3-tier fallback strategy:
1. Location-context search (query + city from address)
2. Direct page lookup via REST API
3. Wikipedia search API

## Rationale
- Tier 1 uses the address field to extract a city name, providing geographic specificity (e.g., "Corso Rome" instead of just "Corso")
- Tier 2 catches exact-match articles when the cleaned location name is a real Wikipedia page
- Tier 3 is the broadest search, accepting the best Wikipedia search result
- Disambiguation pages are detected by checking for "may refer to" in the extract

## Consequences
- Higher success rate for finding relevant articles
- Three HTTP calls in the worst case (acceptable given 5-second timeouts)
- Text results tend to score highest in the judge, making this agent's reliability important
