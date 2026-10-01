"""
Figure 3: ranked log2-ratio bar chart (the "10/90 gap"-style figure) -- RCT-to-burden ratio
across GBD Level-2 causes.

Split from the original burden_perspective1_global.py: this is the plotting half only. Reads
perspective1_global_alignment.csv, written by burden_perspective1_global_analysis.py.
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import math
import os

OUT_DIR = '/Users/leayu/Documents/trend_rct/burden_of_disease_results'
PLOTS_DIR = os.path.join(OUT_DIR, 'plots')

merged = pd.read_csv(os.path.join(OUT_DIR, 'perspective1_global_alignment.csv'), index_col=0)

TEXT_PRIMARY = '#0b0b0b'
TEXT_SECONDARY = '#52514e'
GRID = '#e4e2dc'
SURFACE = '#fcfcfb'
BLUE = '#2a78d6'
ORANGE = '#eb6834'

plt.rcParams.update({
    'font.family': 'sans-serif', 'font.size': 10,
    'axes.edgecolor': GRID, 'axes.labelcolor': TEXT_SECONDARY, 'text.color': TEXT_PRIMARY,
    'xtick.color': TEXT_SECONDARY, 'ytick.color': TEXT_SECONDARY,
    'figure.facecolor': SURFACE, 'axes.facecolor': SURFACE, 'savefig.facecolor': SURFACE,
})

# ---- figure: ranked log2-ratio bar chart (the "10/90 gap"-style figure) ----
plot_ratio = merged['log2_research_to_burden_ratio']

fig, ax = plt.subplots(figsize=(10, 10.5))
y = range(len(merged))
colors = [BLUE if v > 0 else ORANGE for v in plot_ratio]
ax.barh(y, plot_ratio, color=colors, height=0.65, zorder=3)
# label placed just past the tip of each bar (left of tip for negative bars, right of tip for
# positive bars), rather than at a fixed x -- generous x-margins below make room for this on both
# sides so labels never overrun the figure edge or collide with the y-axis category labels
label_offset = 0.06
for i, (v, n) in enumerate(zip(plot_ratio, merged['n_trials'])):
    label = f"{2**v:.2f} (n={int(n)})"
    if v >= 0:
        ax.text(v + label_offset, i, label, va='center', ha='left', fontsize=8, color=TEXT_SECONDARY)
    else:
        ax.text(v - label_offset, i, label, va='center', ha='right', fontsize=8, color=TEXT_SECONDARY)
ax.axvline(0, color=TEXT_SECONDARY, linewidth=1)
ax.set_yticks(list(y))
ax.set_yticklabels(merged.index, fontsize=9)
ax.set_ylabel('GBD Level-2 cause', fontsize=9.5)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(axis='x', color=GRID, linewidth=0.7, zorder=0)
ax.set_axisbelow(True)
ax.margins(x=0.14)
# the BAR LENGTH stays on the log2 scale (so equal over-/under-research is equal bar length), but
# the axis tick LABELS are converted back to plain research-to-burden ratios (2x, 0.5x, etc.) --
# log2 numbers on the axis itself were confusing to read even though the underlying scale is right
xmin, xmax = ax.get_xlim()
tick_positions = [t for t in range(math.floor(xmin), math.ceil(xmax) + 1)]
ax.set_xticks(tick_positions)
ax.set_xticklabels([f"{2**t:.2f}" for t in tick_positions])
ax.set_xlabel('RCT-to-burden ratio, shown on a doubling/halving scale (1.0 = proportional to burden)',
              fontsize=9.5)
# directional cues placed inside the plot area (top corners) instead of cramming them into the
# x-axis title, which was overflowing the figure width
ax.text(0.02, 1.01, '← Under-researched relative to burden', transform=ax.transAxes,
        ha='left', va='bottom', fontsize=8.5, color=ORANGE)
ax.text(0.98, 1.01, 'Over-researched relative to burden →', transform=ax.transAxes,
        ha='right', va='bottom', fontsize=8.5, color=BLUE)
plt.tight_layout()
plt.savefig(os.path.join(PLOTS_DIR, 'perspective1_ranked_ratio.png'), dpi=200, bbox_inches='tight')
plt.close()
print("Saved perspective1_ranked_ratio.png")
