"""
Figure 4B: cause x age-band heatmap of the RCT-to-burden ratio.

Split from the original burden_cause_age_heatmap.py: this is the plotting half only. Reads
cause_age_heatmap_log2_ratio.csv and cause_age_heatmap_n_trials.csv, written by
burden_cause_age_heatmap_analysis.py (the trial-count grid is a newly-added CSV export so this
half doesn't need the in-memory trial_weight variable from the analysis half).
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
import os

OUT_DIR = '/Users/leayu/Documents/trend_rct/burden_of_disease_results'
PLOTS_DIR = os.path.join(OUT_DIR, 'plots')
BAND_ORDER = ['Neonate', 'Infant', 'Young child', 'Child', 'Adolescent']

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

log2_ratio = pd.read_csv(os.path.join(OUT_DIR, 'cause_age_heatmap_log2_ratio.csv'), index_col=0)
n_trials_grid = pd.read_csv(os.path.join(OUT_DIR, 'cause_age_heatmap_n_trials.csv'), index_col=0)
cause_order = log2_ratio.index.tolist()

# ---- figure: heatmap ----
# The true range of log2 ratios spans roughly -3.8 to +8.7 (416x, Sense organ diseases x Neonate --
# a real, if extreme, signal from that cause's near-zero neonatal burden, not a data bug). Coloring
# on the FULL range washes out the typical -3..+3 cells into near-white, since a handful of extreme
# cells stretch the scale. Saturate color at a fixed, round cap instead -- extreme cells still read
# as "fully saturated" rather than being hidden, and their true (uncapped) ratio is still the number
# printed in the cell -- while the bulk of the grid gets real color contrast.
cmap = LinearSegmentedColormap.from_list('orange_white_blue', [ORANGE, SURFACE, BLUE], N=256)
vmax = 5  # log2 units = 32x; integer bound avoids off-range colorbar ticks too
norm = TwoSlopeNorm(vcenter=0, vmin=-vmax, vmax=vmax)

# transposed (horizontal) layout: causes along the x-axis, age bands along the y-axis
log2_ratio_t = log2_ratio.T  # index=BAND_ORDER, columns=cause_order
n_trials_grid_t = n_trials_grid.T

fig, ax = plt.subplots(figsize=(15, 5.5))
im = ax.imshow(log2_ratio_t.values, cmap=cmap, norm=norm, aspect='auto')

ax.set_xticks(range(len(cause_order)))
ax.set_xticklabels(cause_order, fontsize=8.5)
ax.set_yticks(range(len(BAND_ORDER)))
ax.set_yticklabels(BAND_ORDER, fontsize=9.5)
plt.setp(ax.get_xticklabels(), rotation=45, ha='right', rotation_mode='anchor')

# annotate each cell with the plain ratio and the (fractional) trial count; very sparse cells
# (n < 5) get a lighter/italic annotation as a light-touch reliability flag, not hidden or hatched
for i, band in enumerate(BAND_ORDER):
    for j, cause in enumerate(cause_order):
        v = log2_ratio_t.loc[band, cause]
        n = n_trials_grid_t.loc[band, cause]
        ratio_txt = f"{2**v:.2f}" if n > 0 else 'no trials'
        text_color = TEXT_PRIMARY if abs(v) < vmax * 0.6 else SURFACE
        alpha = 0.55 if n < 5 else 1.0
        ax.text(j, i - 0.17, ratio_txt, ha='center', va='center', fontsize=7.3,
                 color=text_color, alpha=alpha)
        ax.text(j, i + 0.22, f"n={n:.0f}", ha='center', va='center', fontsize=6.0,
                 color=text_color, alpha=alpha * 0.85, style='italic')

ax.set_xticks(np.arange(-0.5, len(cause_order), 1), minor=True)
ax.set_yticks(np.arange(-0.5, len(BAND_ORDER), 1), minor=True)
ax.grid(which='minor', color=SURFACE, linewidth=1.5)
ax.tick_params(which='minor', length=0)
for spine in ax.spines.values():
    spine.set_visible(False)

cbar = fig.colorbar(im, ax=ax, orientation='vertical', fraction=0.02, pad=0.01)
cbar.set_label('RCT-to-burden ratio (log2 scale; 1.0 = proportional to burden)', fontsize=8.5)
cbar_ticks = [t for t in range(-int(np.ceil(vmax)), int(np.ceil(vmax)) + 1)]
cbar.set_ticks(cbar_ticks)
cbar.set_ticklabels([f"{2**t:.2f}" for t in cbar_ticks])
cbar.ax.tick_params(labelsize=7.5)

plt.tight_layout()
plt.savefig(os.path.join(PLOTS_DIR, 'cause_age_band_heatmap.png'), dpi=200, bbox_inches='tight')
plt.close()
print("\nSaved cause_age_band_heatmap.png")
