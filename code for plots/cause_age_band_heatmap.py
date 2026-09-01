"""
Figure 4B. RCT-to-burden ratio by cause, within each age band. Joint (cause x age-band)
heatmap: recombines Perspective 1 (by cause) and Perspective 2 (by age band) to surface
interactions neither single-dimension view can show. Every cell's trial-share and
burden-share are % of the ENTIRE joint grid (20 causes x 5 age bands together, both summing
to 100% over the whole grid), so cells are directly comparable in both dimensions at once.
Cause order (x-axis) reuses Perspective 1's ranking (most under-researched first, from
perspective1_global_alignment.csv) so this heatmap reads consistently with Figure 3.

Self-contained: reads cause_age_heatmap_log2_ratio.csv (the color/text value for each cell)
and cause_age_heatmap_n_trials.csv (fractional trial counts, used for the "n=" annotation and
the n<5 reliability-flag transparency) from this same folder -- both recomputed from
Trial bank_13269.xlsx + gbd_burden_by_cause_age_band.csv -- and saves the figure back here.
"""
import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm

HERE = os.path.dirname(os.path.abspath(__file__))

TEXT_PRIMARY = '#0b0b0b'
TEXT_SECONDARY = '#52514e'
GRID = '#e4e2dc'
SURFACE = '#ffffff'
BLUE = '#2a78d6'
ORANGE = '#eb6834'
BAND_ORDER = ['Neonate', 'Infant', 'Young child', 'Child', 'Adolescent']

plt.rcParams.update({
    'font.family': 'sans-serif', 'font.size': 10,
    'axes.edgecolor': GRID, 'axes.labelcolor': TEXT_SECONDARY, 'text.color': TEXT_PRIMARY,
    'xtick.color': TEXT_SECONDARY, 'ytick.color': TEXT_SECONDARY,
    'figure.facecolor': SURFACE, 'axes.facecolor': SURFACE, 'savefig.facecolor': SURFACE,
})

log2_ratio = pd.read_csv(os.path.join(HERE, 'cause_age_heatmap_log2_ratio.csv'), index_col=0)
n_trials_grid = pd.read_csv(os.path.join(HERE, 'cause_age_heatmap_n_trials.csv'), index_col=0)
cause_order = log2_ratio.index.tolist()

cmap = LinearSegmentedColormap.from_list('orange_white_blue', [ORANGE, SURFACE, BLUE], N=256)
vmax = 5
norm = TwoSlopeNorm(vcenter=0, vmin=-vmax, vmax=vmax)

log2_ratio_t = log2_ratio.T
n_trials_grid_t = n_trials_grid.T

fig, ax = plt.subplots(figsize=(15, 6))
im = ax.imshow(log2_ratio_t.values, cmap=cmap, norm=norm, aspect='auto')

ax.set_xticks(range(len(cause_order)))
ax.set_xticklabels(cause_order, fontsize=8.5)
ax.set_yticks(range(len(BAND_ORDER)))
ax.set_yticklabels(BAND_ORDER, fontsize=9.5)
plt.setp(ax.get_xticklabels(), rotation=45, ha='right', rotation_mode='anchor')

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
plt.savefig(os.path.join(HERE, 'cause_age_band_heatmap.png'), dpi=200, bbox_inches='tight')
plt.close()
print("saved cause_age_band_heatmap.png")
