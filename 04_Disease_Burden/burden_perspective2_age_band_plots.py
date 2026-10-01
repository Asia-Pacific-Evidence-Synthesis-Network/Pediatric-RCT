"""
Figure 4A: grouped bar chart, trial share vs burden share, by age band.

Split from the original burden_perspective2_age_band.py: this is the plotting half only. Reads
perspective3_age_band_alignment.csv, written by burden_perspective2_age_band_analysis.py.

Note: the legend label below was corrected from the original script's "Global 2022" to "average
annual 1990-2022" -- the underlying computation always used the 1990-2022 average (see the
analysis half), the original label text just hadn't been updated to match. Same correction
already applied in /Users/leayu/Documents/trend_rct/code for plots/perspective3_age_band_alignment.py.
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
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

merged = pd.read_csv(os.path.join(OUT_DIR, 'perspective3_age_band_alignment.csv'), index_col=0)
merged = merged.reindex(BAND_ORDER)

# ---- figure: grouped bar, trial share vs burden share, by age band ----
fig, ax = plt.subplots(figsize=(8, 5.5))
x = np.arange(len(BAND_ORDER))
w = 0.35
ax.bar(x - w/2, merged['trial_share_pct'], width=w, color=BLUE, label='Share of pediatric RCTs\n(fractionally allocated)', zorder=3)
ax.bar(x + w/2, merged['burden_share_pct'], width=w, color=ORANGE, label='Share of pediatric disease burden\n(% of DALYs, average annual 1990-2022)', zorder=3)
for i, band in enumerate(BAND_ORDER):
    ax.text(i - w/2, merged.loc[band, 'trial_share_pct'] + 0.7, f"{merged.loc[band, 'trial_share_pct']:.1f}%",
            ha='center', fontsize=8, color=TEXT_PRIMARY)
    ax.text(i + w/2, merged.loc[band, 'burden_share_pct'] + 0.7, f"{merged.loc[band, 'burden_share_pct']:.1f}%",
            ha='center', fontsize=8, color=TEXT_PRIMARY)
ax.set_xticks(x)
ax.set_xticklabels(BAND_ORDER, fontsize=10)
ax.set_ylabel('Share (%)', fontsize=10)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(axis='y', color=GRID, linewidth=0.7, zorder=0)
ax.set_axisbelow(True)
ax.legend(loc='upper right', frameon=False, fontsize=9)
ax.set_ylim(0, max(merged['trial_share_pct'].max(), merged['burden_share_pct'].max()) * 1.25)
plt.tight_layout()
plt.savefig(os.path.join(PLOTS_DIR, 'perspective3_age_band_alignment.png'), dpi=200, bbox_inches='tight')
plt.close()
print("\nSaved perspective3_age_band_alignment.png")
