"""
Judge Agent Scoring Analysis

Parses real log data and runs sensitivity analysis on the JudgeAgent's
scoring parameters. Generates metrics and visualizations.
"""

import re
import json
from collections import defaultdict
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
LOG_FILE = PROJECT_ROOT / "tour_guide.log"
RESULTS_DIR = PROJECT_ROOT / "results"
METRICS_DIR = RESULTS_DIR / "metrics"
FIGURES_DIR = RESULTS_DIR / "figures"


def parse_log_scores(log_path: Path) -> list[dict]:
    """Parse judge scores from log file.

    Scores come in blocks: 2-3 agent score lines per route point,
    followed by a 'Selected' line. Group them by consecutive blocks.
    """
    scores = []
    current_point: dict = {'agents': {}}

    pattern = re.compile(
        r'\((\w+), JudgeAgent, (\w+Agent) \((\w+)\): score=([0-9.]+)\)'
    )
    selection_pattern = re.compile(
        r'\((\w+), JudgeAgent, Selected (\w+) from (\w+Agent)\)'
    )

    with open(log_path, 'r', encoding='utf-8') as f:
        for line in f:
            match = pattern.search(line)
            if match:
                run_id, agent, content_type, score = match.groups()
                current_point['run_id'] = run_id
                current_point['agents'][agent] = {
                    'content_type': content_type,
                    'score': float(score)
                }
                continue

            sel_match = selection_pattern.search(line)
            if sel_match:
                run_id, selected_type, selected_agent = sel_match.groups()
                current_point['selected_type'] = selected_type
                current_point['selected_agent'] = selected_agent
                scores.append(current_point)
                current_point = {'agents': {}}

    return scores


def analyze_baseline(scores: list[dict]) -> dict:
    """Compute baseline statistics from parsed scores."""
    type_scores = defaultdict(list)
    type_wins = defaultdict(int)
    score_gaps = []
    total = 0

    for entry in scores:
        if 'selected_type' not in entry:
            continue
        total += 1
        type_wins[entry['selected_type']] += 1

        for data in entry['agents'].values():
            type_scores[data['content_type']].append(data['score'])

        # Compute score gap
        agent_scores = [d['score'] for d in entry['agents'].values()]
        if len(agent_scores) >= 2:
            sorted_scores = sorted(agent_scores, reverse=True)
            score_gaps.append(sorted_scores[0] - sorted_scores[1])

    metrics = {
        'total_judgments': total,
        'type_avg_scores': {
            t: round(sum(s) / len(s), 1) if s else 0
            for t, s in type_scores.items()
        },
        'type_win_rates': {
            t: round(count / total * 100, 1) if total else 0
            for t, count in type_wins.items()
        },
        'avg_score_gap': round(sum(score_gaps) / len(score_gaps), 1) if score_gaps else 0,
        'type_score_details': {
            t: {
                'count': len(s),
                'min': min(s) if s else 0,
                'max': max(s) if s else 0,
                'avg': round(sum(s) / len(s), 1) if s else 0,
            }
            for t, s in type_scores.items()
        }
    }

    return metrics


def sensitivity_type_preference(scores: list[dict]) -> list[dict]:
    """Sweep type preference weights and measure selection changes."""
    configs = [
        {'name': 'Default (10/5/5)', 'text': 10, 'video': 5, 'music': 5},
        {'name': 'Equal (5/5/5)', 'text': 5, 'video': 5, 'music': 5},
        {'name': 'Equal (10/10/10)', 'text': 10, 'video': 10, 'music': 10},
        {'name': 'Music-boosted (5/5/15)', 'text': 5, 'video': 5, 'music': 15},
        {'name': 'Video-boosted (5/15/5)', 'text': 5, 'video': 15, 'music': 5},
        {'name': 'No preference (0/0/0)', 'text': 0, 'video': 0, 'music': 0},
    ]

    results = []
    for config in configs:
        wins = defaultdict(int)
        total = 0

        for entry in scores:
            if 'selected_type' not in entry or len(entry['agents']) < 2:
                continue
            total += 1

            # Recalculate with new type preferences
            # Adjust each score by the delta between new and default type pref
            default_prefs = {'text': 10, 'video': 5, 'music': 5}
            best_score = -1
            best_type = None

            for data in entry['agents'].values():
                ct = data['content_type']
                # Remove old type pref, add new
                adjusted = data['score'] - default_prefs.get(ct, 0) + config.get(ct, 0)
                if adjusted > best_score:
                    best_score = adjusted
                    best_type = ct

            if best_type:
                wins[best_type] += 1

        result = {
            'config': config['name'],
            'text_pct': round(wins.get('text', 0) / total * 100, 1) if total else 0,
            'video_pct': round(wins.get('video', 0) / total * 100, 1) if total else 0,
            'music_pct': round(wins.get('music', 0) / total * 100, 1) if total else 0,
        }
        results.append(result)

    return results


def _adjust_relevance_score(base_score: float, content_type: str,
                            mult: int, default_mult: int) -> float:
    """Adjust a score by swapping relevance multiplier."""
    relevance_estimate = {'text': 15, 'video': 10, 'music': 0}.get(content_type, 0)
    old_relevance = min(relevance_estimate, 20)
    new_relevance = min(relevance_estimate * mult / default_mult, 20) if default_mult > 0 else 0
    return base_score - old_relevance + new_relevance


def _run_relevance_sweep(scores: list[dict], mult: int, default_mult: int) -> dict:
    """Run a single relevance multiplier sweep iteration."""
    wins = defaultdict(int)
    total = 0
    gaps = []

    for entry in scores:
        if 'selected_type' not in entry or len(entry['agents']) < 2:
            continue
        total += 1

        best_score = -1
        best_type = None
        all_adjusted = []

        for data in entry['agents'].values():
            ct = data['content_type']
            adjusted = _adjust_relevance_score(data['score'], ct, mult, default_mult)
            all_adjusted.append(adjusted)
            if adjusted > best_score:
                best_score = adjusted
                best_type = ct

        if best_type:
            wins[best_type] += 1
            sorted_adj = sorted(all_adjusted, reverse=True)
            if len(sorted_adj) >= 2:
                gaps.append(sorted_adj[0] - sorted_adj[1])

    return {
        'multiplier': mult,
        'text_pct': round(wins.get('text', 0) / total * 100, 1) if total else 0,
        'video_pct': round(wins.get('video', 0) / total * 100, 1) if total else 0,
        'music_pct': round(wins.get('music', 0) / total * 100, 1) if total else 0,
        'avg_gap': round(sum(gaps) / len(gaps), 1) if gaps else 0,
    }


def sensitivity_relevance_weight(scores: list[dict]) -> list[dict]:
    """Sweep relevance multiplier and measure selection changes."""
    default_mult = 5
    return [
        _run_relevance_sweep(scores, mult, default_mult)
        for mult in [0, 1, 3, 5, 8, 10]
    ]


def save_metrics(baseline: dict, type_sens: list, rel_sens: list):
    """Save metrics to JSON files."""
    METRICS_DIR.mkdir(parents=True, exist_ok=True)

    with open(METRICS_DIR / "baseline_metrics.json", 'w', encoding='utf-8') as f:
        json.dump(baseline, f, indent=2)

    with open(METRICS_DIR / "type_preference_sensitivity.json", 'w', encoding='utf-8') as f:
        json.dump(type_sens, f, indent=2)

    with open(METRICS_DIR / "relevance_sensitivity.json", 'w', encoding='utf-8') as f:
        json.dump(rel_sens, f, indent=2)

    print(f"Metrics saved to {METRICS_DIR}")


def _plot_score_distribution(plt, baseline: dict, colors: dict):
    """Plot average judge scores by content type."""
    _, ax = plt.subplots(figsize=(8, 5))
    types = list(baseline['type_avg_scores'].keys())
    avg_scores = [baseline['type_avg_scores'][t] for t in types]
    bar_colors = [colors.get(t, '#9E9E9E') for t in types]

    bars = ax.bar(types, avg_scores, color=bar_colors, edgecolor='white', linewidth=1.5)
    ax.set_ylabel('Average Score', fontsize=12)
    ax.set_xlabel('Content Type', fontsize=12)
    ax.set_title('Baseline: Average Judge Score by Content Type', fontsize=14)
    ax.set_ylim(0, 105)
    ax.grid(axis='y', alpha=0.3)

    for rect, score in zip(bars, avg_scores):
        ax.text(rect.get_x() + rect.get_width() / 2., rect.get_height() + 1,
                f'{score}', ha='center', va='bottom', fontsize=11, fontweight='bold')

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "score_distribution.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {FIGURES_DIR / 'score_distribution.png'}")


def _plot_win_rate_pie(plt, baseline: dict, colors: dict):
    """Plot content selection distribution pie chart."""
    _, ax = plt.subplots(figsize=(7, 7))
    win_types = list(baseline['type_win_rates'].keys())
    win_pcts = [baseline['type_win_rates'][t] for t in win_types]
    pie_colors = [colors.get(t, '#9E9E9E') for t in win_types]

    ax.pie(
        win_pcts, labels=[f"{t.capitalize()}\n{p}%" for t, p in zip(win_types, win_pcts)],
        colors=pie_colors, autopct='', startangle=90,
        textprops={'fontsize': 13, 'fontweight': 'bold'}
    )
    ax.set_title('Baseline: Content Selection Distribution', fontsize=14)

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "win_rate_pie.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {FIGURES_DIR / 'win_rate_pie.png'}")


def _plot_type_sensitivity(plt, type_sens: list):
    """Plot type preference sensitivity grouped bar chart."""
    _, ax = plt.subplots(figsize=(10, 6))
    config_names = [r['config'] for r in type_sens]
    x = range(len(config_names))
    width = 0.25

    ax.bar([i - width for i in x], [r['text_pct'] for r in type_sens],
           width, label='Text', color='#2196F3')
    ax.bar(list(x), [r['video_pct'] for r in type_sens],
           width, label='Video', color='#FF5722')
    ax.bar([i + width for i in x], [r['music_pct'] for r in type_sens],
           width, label='Music', color='#4CAF50')

    ax.set_ylabel('Win Rate (%)', fontsize=12)
    ax.set_xlabel('Type Preference Config', fontsize=12)
    ax.set_title('Sensitivity: Content Selection vs Type Preference Weights', fontsize=14)
    ax.set_xticks(list(x))
    ax.set_xticklabels(config_names, rotation=30, ha='right', fontsize=9)
    ax.legend(fontsize=11)
    ax.grid(axis='y', alpha=0.3)
    ax.set_ylim(0, 100)

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "type_preference_sensitivity.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {FIGURES_DIR / 'type_preference_sensitivity.png'}")


def _plot_relevance_sensitivity(plt, rel_sens: list):
    """Plot relevance multiplier sensitivity dual-panel chart."""
    _, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    mults = [r['multiplier'] for r in rel_sens]
    ax1.plot(mults, [r['text_pct'] for r in rel_sens], 'o-', color='#2196F3', label='Text', linewidth=2)
    ax1.plot(mults, [r['video_pct'] for r in rel_sens], 's-', color='#FF5722', label='Video', linewidth=2)
    ax1.plot(mults, [r['music_pct'] for r in rel_sens], '^-', color='#4CAF50', label='Music', linewidth=2)
    ax1.axvline(x=5, color='gray', linestyle='--', alpha=0.5, label='Default (5)')
    ax1.set_xlabel('Relevance Multiplier', fontsize=12)
    ax1.set_ylabel('Win Rate (%)', fontsize=12)
    ax1.set_title('Win Rate vs Relevance Weight', fontsize=13)
    ax1.legend(fontsize=10)
    ax1.grid(alpha=0.3)
    ax1.set_ylim(0, 100)

    ax2.plot(mults, [r['avg_gap'] for r in rel_sens], 'D-', color='#9C27B0', linewidth=2)
    ax2.axvline(x=5, color='gray', linestyle='--', alpha=0.5, label='Default (5)')
    ax2.set_xlabel('Relevance Multiplier', fontsize=12)
    ax2.set_ylabel('Avg Score Gap (Winner - Runner-up)', fontsize=12)
    ax2.set_title('Judge Confidence vs Relevance Weight', fontsize=13)
    ax2.legend(fontsize=10)
    ax2.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "relevance_sensitivity.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {FIGURES_DIR / 'relevance_sensitivity.png'}")


def generate_visualizations(baseline: dict, type_sens: list, rel_sens: list):
    """Generate matplotlib visualizations."""
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt  # pylint: disable=import-outside-toplevel
    except ImportError:
        print("matplotlib not available, skipping visualizations")
        return

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    colors = {'text': '#2196F3', 'video': '#FF5722', 'music': '#4CAF50'}

    _plot_score_distribution(plt, baseline, colors)
    _plot_win_rate_pie(plt, baseline, colors)
    _plot_type_sensitivity(plt, type_sens)
    _plot_relevance_sensitivity(plt, rel_sens)


def main():
    """Run full analysis pipeline."""
    print("=" * 60)
    print("JudgeAgent Scoring Analysis")
    print("=" * 60)

    # Parse logs
    print("\n1. Parsing log data...")
    if not LOG_FILE.exists():
        print(f"   ERROR: Log file not found: {LOG_FILE}")
        return

    scores = parse_log_scores(LOG_FILE)
    print(f"   Parsed {len(scores)} judge decisions")

    # Baseline analysis
    print("\n2. Computing baseline metrics...")
    baseline = analyze_baseline(scores)
    print(f"   Total judgments: {baseline['total_judgments']}")
    print(f"   Avg scores: {baseline['type_avg_scores']}")
    print(f"   Win rates: {baseline['type_win_rates']}")
    print(f"   Avg score gap: {baseline['avg_score_gap']}")

    # Sensitivity: type preferences
    print("\n3. Running type preference sensitivity...")
    type_sens = sensitivity_type_preference(scores)
    for r in type_sens:
        print(f"   {r['config']:30s}  text={r['text_pct']:5.1f}%  "
              f"video={r['video_pct']:5.1f}%  music={r['music_pct']:5.1f}%")

    # Sensitivity: relevance weight
    print("\n4. Running relevance weight sensitivity...")
    rel_sens = sensitivity_relevance_weight(scores)
    for r in rel_sens:
        print(f"   mult={r['multiplier']:2d}  text={r['text_pct']:5.1f}%  "
              f"video={r['video_pct']:5.1f}%  music={r['music_pct']:5.1f}%  "
              f"gap={r['avg_gap']:5.1f}")

    # Save metrics
    print("\n5. Saving metrics...")
    save_metrics(baseline, type_sens, rel_sens)

    # Generate visualizations
    print("\n6. Generating visualizations...")
    generate_visualizations(baseline, type_sens, rel_sens)

    print("\n" + "=" * 60)
    print("Analysis complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
