# Literature Review: Content Scoring and Multi-Criteria Decision Making

## Research Question

How should a deterministic agent score and rank heterogeneous multimedia content (video, music, text) for relevance to a geographic location?

## Key Areas

### 1. Multi-Criteria Decision Making (MCDM)

The JudgeAgent's scoring is a weighted-sum model (WSM), the simplest MCDM method.

- **Weighted Sum Model (WSM)**: Score = Σ(wᵢ × cᵢ) where wᵢ are weights and cᵢ are criteria scores. Works well when criteria are independent and measured on a common scale.
  - *Fishburn, P.C. (1967). "Additive utilities with incomplete product sets"*

- **TOPSIS**: Ranks alternatives by distance to ideal and anti-ideal solutions. More robust than WSM when criteria have different scales.
  - *Hwang, C.L. & Yoon, K. (1981). "Multiple Attribute Decision Making"*

- **AHP (Analytic Hierarchy Process)**: Uses pairwise comparisons to derive weights. Useful when domain experts need to calibrate preferences.
  - *Saaty, T.L. (1980). "The Analytic Hierarchy Process"*

**Relevance to project**: The JudgeAgent uses WSM with 6 criteria (content existence, title presence, title relevance, description length, content type, URL presence). This is appropriate given all criteria are scored on a 0-100 scale.

### 2. Information Retrieval Scoring

Search engines score document relevance using TF-IDF, BM25, or neural retrieval models.

- **BM25**: Probabilistic ranking function based on term frequency and document length normalization. The JudgeAgent's keyword-overlap scoring is a simplified version of this.
  - *Robertson, S.E. & Zaragoza, H. (2009). "The Probabilistic Relevance Framework: BM25 and Beyond"*

- **Neural Retrieval**: Dense passage retrieval (DPR) and cross-encoders provide semantic similarity beyond keyword matching.
  - *Karpukhin et al. (2020). "Dense Passage Retrieval for Open-Domain Question Answering"*

**Relevance to project**: The current keyword-overlap scoring is BM25-like but without term frequency weighting or document length normalization. An improvement would be to use embedding-based similarity for semantic matching.

### 3. Recommendation Diversity

Content recommendation systems balance relevance and diversity.

- **Maximal Marginal Relevance (MMR)**: Re-ranks results by penalizing items similar to already-selected ones. Increases diversity.
  - *Carbonell, J. & Goldstein, J. (1998). "The Use of MMR for Diversity-Based Reranking"*

- **Calibrated Recommendations**: Match the distribution of recommended items to user interest distribution.
  - *Steck, H. (2018). "Calibrated Recommendations"*

**Relevance to project**: The JudgeAgent selects one content type per point independently. Cross-point diversity (ensuring a mix of text/video/music across the route) is not currently considered. MMR could be applied at the orchestrator level.

### 4. Location-Based Content Matching

Geographic information retrieval matches content to places.

- **Geoparsing**: Extracting place names from text and resolving them to coordinates.
  - *Gritta et al. (2018). "What's missing in geographical parsing?"*

- **Place-based search**: Searching for content about a specific geographic location, handling ambiguity (e.g., "Corso" could be many streets).
  - *Purves et al. (2018). "Geographic Information Retrieval"*

**Relevance to project**: The agents' query-cleaning step (removing navigation words) is a form of geoparsing. The TextAgent's 3-tier fallback with location context addresses place name ambiguity.

## Summary

| Technique | Current Implementation | Potential Improvement |
|-----------|----------------------|----------------------|
| WSM scoring | 6-criteria weighted sum | TOPSIS or AHP for weight calibration |
| Keyword matching | Simple set intersection | BM25 or embedding similarity |
| Type preference | Fixed +10/+5/+5 bonus | User-adaptive preferences |
| Diversity | Per-point independent | MMR across full route |
| Place matching | Navigation word filtering | Full geoparsing pipeline |

## Open Challenges

1. **Semantic gap**: Keyword overlap misses semantically related content (a video about "Roman architecture" is relevant to "Piazza della Rotonda" but shares no keywords)
2. **Music relevance**: Ambient music is inherently not "about" a location — scoring frameworks designed for informational content disadvantage it
3. **Route-level coherence**: Current scoring is per-point; a tour-level judge could ensure variety across the full route
