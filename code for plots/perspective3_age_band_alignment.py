"""
Figure 4A. RCT share versus disease burden share, by age band. Grouped bar chart: fractionally-
allocated pediatric RCT share (a trial spanning N age bands contributes 1/N to each) vs. global
average-annual 1990-2022 all-cause DALY share, both summing to 100% across the 5 bands.

Self-contained: reads perspective3_age_band_alignment.csv from this same folder (a copy of
burden_of_disease_results/perspective3_age_band_alignment.csv) and saves the figure back into
this folder.

Note: the source script's legend read "Global 2022" -- a leftover from before the burden metric
was switched to an average across 1990-2022 (the computation itself was already correct; only the
label text was stale). Corrected here to match the actual data and the wording used in the sibling
income-group figure.
"""
import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

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

merged = pd.read_csv(os.path.join(HERE, 'perspective3_age_band_alignment.csv'), index_col=0)
merged = merged.reindex(BAND_ORDER)

fig, ax = plt.subplots(figsize=(8, 5.5))
x = np.arange(len(BAND_ORDER))
w = 0.35
ax.bar(x - w/2, merged['trial_share_pct'], width=w, color=BLUE,
       label='Share of pediatric RCTs\n(fractionally allocated)', zorder=3)
ax.bar(x + w/2, merged['burden_share_pct'], width=w, color=ORANGE,
       label='Share of pediatric disease burden\n(% of DALYs, average annual 1990-2022)', zorder=3)
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
plt.savefig(os.path.join(HERE, 'perspective3_age_band_alignment.png'), dpi=200, bbox_inches='tight')
plt.close()
print("saved perspective3_age_band_alignment.png")
