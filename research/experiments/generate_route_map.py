"""Generate a route map visualization for the Pantheon-to-Vatican example."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # pylint: disable=wrong-import-position
import matplotlib.patches as mpatches  # pylint: disable=wrong-import-position
from pathlib import Path  # pylint: disable=wrong-import-position

# Key waypoints along the Pantheon → Vatican walking route (approximate)
WAYPOINTS = [
    (41.8986, 12.4769, "Pantheon"),
    (41.8990, 12.4755, "Piazza della Rotonda"),
    (41.8996, 12.4738, "Via dei Cestari"),
    (41.9003, 12.4720, "Largo di Torre Argentina"),
    (41.9008, 12.4705, "Via di Torre Argentina"),
    (41.9015, 12.4690, "Piazza Navona area"),
    (41.9020, 12.4672, "Via dei Coronari"),
    (41.9025, 12.4655, "Via di Panico"),
    (41.9030, 12.4640, "Ponte Sant'Angelo"),
    (41.9035, 12.4625, "Castel Sant'Angelo"),
    (41.9040, 12.4610, "Lungotevere"),
    (41.9035, 12.4595, "Ponte Vittorio Emanuele II"),
    (41.9030, 12.4580, "Via della Conciliazione"),
    (41.9028, 12.4570, "Borgo Santo Spirito"),
    (41.9025, 12.4558, "Via Paolo VI"),
    (41.9022, 12.4545, "Piazza San Pietro"),
    (41.9022, 12.4536, "Vatican City"),
]

FIGURES_DIR = Path(__file__).parent.parent.parent / "docs" / "images"


def generate_route_map():
    """Generate route map PNG."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    lats = [w[0] for w in WAYPOINTS]
    lngs = [w[1] for w in WAYPOINTS]

    _, ax = plt.subplots(figsize=(10, 6))

    # Plot route line
    ax.plot(lngs, lats, '-', color='#4285F4', linewidth=3, alpha=0.8, zorder=2)

    # Plot waypoints
    ax.scatter(lngs[1:-1], lats[1:-1], c='#4285F4', s=30, zorder=3, alpha=0.7)

    # Start marker (green)
    ax.scatter([lngs[0]], [lats[0]], c='#0F9D58', s=150, zorder=4,
               marker='o', edgecolors='white', linewidths=2)
    ax.annotate('  Pantheon', (lngs[0], lats[0]), fontsize=11,
                fontweight='bold', color='#0F9D58', va='center')

    # End marker (red)
    ax.scatter([lngs[-1]], [lats[-1]], c='#DB4437', s=150, zorder=4,
               marker='o', edgecolors='white', linewidths=2)
    ax.annotate('Vatican City  ', (lngs[-1], lats[-1]), fontsize=11,
                fontweight='bold', color='#DB4437', va='center', ha='right')

    # Key landmarks
    landmarks = {
        "Castel\nSant'Angelo": 9,
        "Ponte Vittorio\nEmanuele II": 11,
        "Piazza\nSan Pietro": 15,
    }
    for label, idx in landmarks.items():
        ax.annotate(label, (lngs[idx], lats[idx]),
                    textcoords="offset points", xytext=(0, 14),
                    fontsize=8, ha='center', color='#555555',
                    arrowprops={'arrowstyle': '->', 'color': '#999999', 'lw': 0.8})

    # Format axes to show full coordinates
    ax.ticklabel_format(useOffset=False, style='plain')
    ax.set_xlabel('Longitude', fontsize=10)
    ax.set_ylabel('Latitude', fontsize=10)
    ax.set_title('Example Route: Pantheon → Vatican City (22 points, 2.5 km)',
                 fontsize=14, fontweight='bold')

    # Legend
    start_patch = mpatches.Patch(color='#0F9D58', label='Start: Pantheon')
    end_patch = mpatches.Patch(color='#DB4437', label='End: Vatican City')
    route_patch = mpatches.Patch(color='#4285F4', label='Walking route (22 points)')
    ax.legend(handles=[start_patch, route_patch, end_patch], loc='lower left', fontsize=9)

    ax.grid(alpha=0.2)
    ax.set_aspect('equal')

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "route_example.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {FIGURES_DIR / 'route_example.png'}")


if __name__ == "__main__":
    generate_route_map()
