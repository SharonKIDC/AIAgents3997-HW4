# Results

Output from the JudgeAgent scoring sensitivity analysis.

## Metrics (`metrics/`)

| File | Description |
|------|-------------|
| `baseline_metrics.json` | Score distribution and win rates across 221 judge decisions |
| `type_preference_sensitivity.json` | Win rates under 6 type-preference weight configurations |
| `relevance_sensitivity.json` | Win rates and score gaps under 6 relevance multiplier values |

## Figures (`figures/`)

| Figure | Description |
|--------|-------------|
| `score_distribution.png` | Bar chart of average judge scores by content type |
| `win_rate_pie.png` | Pie chart showing baseline content selection distribution |
| `type_preference_sensitivity.png` | Grouped bar chart of win rates across type-preference configs |
| `relevance_sensitivity.png` | Dual-panel line chart: win rates and judge confidence vs relevance multiplier |

## Key Findings

- **Text wins 86.4%** of selections with avg score 87.0/100
- **Type preference weights** have limited impact (~9 ppts swing)
- **Relevance multiplier** is the most sensitive parameter (15 ppt swing, 9.7-24.5 gap range)
- Default parameters sit in the stable region of parameter space

## Reproduction

```bash
source .venv/bin/activate
python research/experiments/judge_analysis.py
```
