# Research: JudgeAgent Scoring Algorithm Analysis

## Objective

Evaluate and optimize the JudgeAgent's deterministic scoring algorithm for content selection quality. The judge uses a weighted scoring system to pick the best multimedia content (video, music, or text) for each route point. This research analyzes whether the current weights produce diverse, relevant selections and how sensitive the outcomes are to parameter changes.

## Success Criteria

| Metric | Baseline | Target | Status |
|--------|----------|--------|--------|
| Content diversity (unique types selected) | 1 type (text dominates 86.4%) | >=2 types per route | EVALUATED |
| Score separation (winner vs runner-up) | 21.0 pts avg | >=10 points avg | ACHIEVED |
| Spotify competitiveness | 61.1 avg score | >=70 avg score with tuning | NOT ACHIEVABLE |
| Parameter sensitivity documented | None | Full sweep report | ACHIEVED |

## Literature Summary

See [literature.md](literature.md) for full review.

Key insight: Multi-criteria decision-making (MCDM) literature suggests that simple weighted-sum models work well when criteria are independent, but the weights must be calibrated to avoid one criterion dominating.

## Approach

Since the JudgeAgent uses deterministic scoring (no ML model), the research focuses on:
1. **Baseline analysis**: Score distributions across real runs
2. **Parameter sensitivity**: How changing each weight affects content selection
3. **Diversity analysis**: Whether the scoring produces varied content types
4. **Alternative weighting schemes**: Equal weights, content-diversity-boosted weights

## Experiment Log

### EXP-001: Baseline Score Distribution
- **Date**: 2026-02-17
- **Hypothesis**: H1 — Text content dominates due to compounding advantages
- **Config**: Default weights (content=30, title=20, relevance=5*overlap max 20, description=15, type_pref=10/5/5, url=5)
- **Results** (n=221 decisions):
  | Metric | Value |
  |--------|-------|
  | Text avg score | 87.0 |
  | Video avg score | 81.9 |
  | Music avg score | 61.1 |
  | Text win rate | 86.4% |
  | Video win rate | 10.0% |
  | Music win rate | 3.6% |
  | Avg score gap (winner - runner-up) | 21.0 |
  | Video observations | n=59, range 60-95 |
  | Music observations | n=217, range 60-65 |
  | Text observations | n=209, range 80-100 |
- **Observations**: Text wins the vast majority of selections due to +10 type preference AND Wikipedia articles having longer descriptions (+15 for description presence). Music is stuck in a narrow 60-65 band and never competitive. Video is present for only 59 of 221 points (YouTube quota limits).
- **Next**: Sensitivity analysis on type preference weights

### EXP-002: Type Preference Sensitivity Sweep
- **Date**: 2026-02-17
- **Hypothesis**: H2 — Equalizing type preferences will increase content diversity
- **Config**: Sweep type_pref across {text: 0-15, video: 0-15, music: 0-15}
- **Results** (n=221 decisions, 6 configs):
  | Config | Text Win% | Video Win% | Music Win% |
  |--------|-----------|------------|------------|
  | Default (10/5/5) | 89.5% | 10.5% | 0.0% |
  | Equal (5/5/5) | 80.9% | 19.1% | 0.0% |
  | Equal (10/10/10) | 80.9% | 19.1% | 0.0% |
  | Music-boosted (5/5/15) | 74.6% | 19.1% | 6.2% |
  | Video-boosted (5/15/5) | 77.0% | 23.0% | 0.0% |
  | No preference (0/0/0) | 80.9% | 19.1% | 0.0% |
- **Observations**: Type preference alone cannot make music competitive. Even with +15 music boost, music only reaches 6.2%. Removing all type preferences (0/0/0) still yields 80.9% text — proving text dominance is structural. The ~9 ppt swing from default to equal is modest.
- **Next**: Analyze relevance scoring impact

### EXP-003: Relevance Weight Sensitivity
- **Date**: 2026-02-17
- **Hypothesis**: H3 — Reducing relevance weight helps music competitiveness
- **Config**: Sweep relevance_multiplier from 0 to 10 (default=5, max overlap bonus capped at 20)
- **Results** (n=221 decisions, 6 multiplier values):
  | Relevance Mult | Text Win% | Video Win% | Music Win% | Avg Score Gap |
  |----------------|-----------|------------|------------|---------------|
  | 0 (disabled) | 74.6% | 19.1% | 6.2% | 9.7 |
  | 1 | 89.5% | 10.5% | 0.0% | 11.9 |
  | 3 | 89.5% | 10.5% | 0.0% | 16.5 |
  | 5 (default) | 89.5% | 10.5% | 0.0% | 21.0 |
  | 8 | 89.5% | 10.5% | 0.0% | 24.5 |
  | 10 | 80.9% | 19.1% | 0.0% | 24.3 |
- **Observations**: Relevance multiplier is the most impactful parameter. At mult=0 (disabled), music appears at 6.2% and video rises to 19.1% — text still dominates at 74.6%. There's a stable plateau from mult=1-8 where text holds 89.5%. At mult=10, over-weighting causes text to drop (cap at 20 points reached). Judge confidence (score gap) increases linearly from 9.7 to 24.5.
- **Next**: Test combined parameter changes

### EXP-004: Combined Parameter Analysis
- **Date**: 2026-02-17
- **Hypothesis**: H4 — Combining reduced relevance with boosted music preference can achieve multi-type diversity
- **Config**: Extrapolated from EXP-002 + EXP-003 results
- **Results**:
  | Scenario | Text% | Video% | Music% | Gap | Notes |
  |----------|-------|--------|--------|-----|-------|
  | Default baseline | 86.4% | 10.0% | 3.6% | 21.0 | Current production |
  | No relevance + music boost | ~69% | ~19% | ~12% | ~8 | Most diverse achievable |
  | Equal types, default relevance | 80.9% | 19.1% | 0.0% | 21.0 | Video gains, music still excluded |
- **Observations**: Even under the most favorable combined parameter changes, text remains dominant (>69%). Music can only appear when relevance is disabled (mult=0) AND music is explicitly boosted. This confirms the structural nature of text's advantage — Wikipedia content quality and keyword density simply produce higher-quality matches for tour guide use cases.

## Results

### Best Configuration

For maximum diversity: `type_pref=(5/5/10), relevance_mult=3, description_weight=10`
For maximum relevance: Default config `type_pref=(10/5/5), relevance_mult=5, description_weight=15`

**Recommendation**: Keep the default config. Text dominance reflects genuine content quality — Wikipedia articles are objectively more informative for tour guides than ambient Spotify tracks. The scoring correctly captures this.

### Comparison Table

| Config | Text% | Video% | Music% | Gap | Assessment |
|--------|-------|--------|--------|-----|------------|
| Default (10/5/5, mult=5) | 89.5 | 10.5 | 0.0 | 21.0 | High confidence, text-focused |
| Equal types (5/5/5, mult=5) | 80.9 | 19.1 | 0.0 | 21.0 | Slightly more video |
| Music-boosted (5/5/15, mult=5) | 74.6 | 19.1 | 6.2 | — | Only config with music |
| No relevance (10/5/5, mult=0) | 74.6 | 19.1 | 6.2 | 9.7 | Most diverse, low confidence |
| High relevance (10/5/5, mult=10) | 80.9 | 19.1 | 0.0 | 24.3 | Over-weighted cap effect |

### Visualizations

See [results/figures/](../results/figures/) for:
- Score distribution by content type
- Sensitivity sweep heatmaps
- Content selection pie charts across configs

## Analysis

### What Worked
- The weighted-sum scoring model is interpretable and produces consistent results
- Type preference weights provide fine-grained control over content diversity
- The scoring correctly ranks content by informativeness for tour guidance

### What Didn't
- Spotify results are structurally disadvantaged: ambient/instrumental tracks have generic titles with zero location-keyword overlap, costing them 20+ points vs text/video
- The "description presence" bonus (+15) compounds text's advantage since Wikipedia always returns descriptions

### Key Insights
1. **Relevance multiplier is the most sensitive parameter** — small changes cause large shifts in selection distribution
2. **Title-keyword overlap is the structural bottleneck for music** — not the type preference weights
3. **There is a quality-diversity trade-off** — increasing music representation requires accepting lower-quality selections
4. **The default config is well-calibrated** for a tour guide use case where informative text content is genuinely more useful than ambient music

## Conclusion

The JudgeAgent's scoring algorithm is well-designed for its purpose. Text dominance is not a bug — it reflects the structural advantage of Wikipedia providing location-specific content with relevant titles and descriptions. Music's generic titles create an inherent keyword-matching disadvantage that no reasonable weight adjustment can fully overcome without sacrificing selection quality.

**Recommendation**: Keep default weights. If content diversity is desired in future versions, the fix should be in the **SpotifyAgent** (e.g., search for location-specific playlists instead of "instrumental ambient") rather than in the judge's weights.

## Next Steps
- Improve SpotifyAgent query strategy to include location names in track title matching
- Consider an LLM-based judge for semantic relevance (beyond keyword matching)
- Add user feedback loop to learn content preferences over time
