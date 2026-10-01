"""
Figure S7: overall alignment by income group (trial share vs burden share), same style as
Perspective 2's age-band chart.
Figure S8: heatmap, income group x cause.

Split from the original burden_perspective3_income_group.py: this is the plotting half only.
Reads income_group_overall_alignment.csv, perspective4_income_group_alignment_by_cause.csv, and
perspective1_global_alignment.csv (for cause ordering), all written by
burden_perspective3_income_group_analysis.py (and burden_perspective1_global_analysis.py).
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

# ==================================================================
# Figure S7: overall alignment by income group
# ==================================================================
overall = pd.read_csv(os.path.join(OUT_DIR, 'income_group_overall_alignment.csv'), index_col=0)

fig, ax = plt.subplots(figsize=(8, 5.5))
x = np.arange(len(overall))
w = 0.35
ax.bar(x - w / 2, overall['trial_share_pct'], width=w, color=BLUE, label='Share of pediatric RCTs', zorder=3)
ax.bar(x + w / 2, overall['burden_share_pct'], width=w, color=ORANGE,
       label='Share of pediatric disease burden\n(% of DALYs, average annual 1990-2022, all causes)', zorder=3)
for i, g in enumerate(overall.index):
    ax.text(i - w / 2, overall.loc[g, 'trial_share_pct'] + 0.7, f"{overall.loc[g, 'trial_share_pct']:.1f}%",
            ha='center', fontsize=8, color=TEXT_PRIMARY)
    ax.text(i + w / 2, overall.loc[g, 'burden_share_pct'] + 0.7, f"{overall.loc[g, 'burden_share_pct']:.1f}%",
            ha='center', fontsize=8, color=TEXT_PRIMARY)
ax.set_xticks(x)
ax.set_xticklabels(overall.index, fontsize=10.5)
ax.set_ylabel('Share (%)', fontsize=10)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(axis='y', color=GRID, linewidth=0.7, zorder=0)
ax.set_axisbelow(True)
ax.legend(loc='upper right', frameon=False, fontsize=9)
ax.set_ylim(0, max(overall['trial_share_pct'].max(), overall['burden_share_pct'].max()) * 1.25)
plt.tight_layout()
plt.savefig(os.path.join(PLOTS_DIR, 'perspective4_income_group_alignment.png'), dpi=200, bbox_inches='tight')
plt.close()
print("Saved perspective4_income_group_alignment.png")

# ==================================================================
# Figure S8: heatmap, income group x cause
# ==================================================================
# Reuses per_cause_df computed in the analysis half -- trial_share_pct/burden_share_pct there are
# each already renormalized to 100% WITHIN each income group's own 20-cause profile (the same
# within-group convention as the rest of this perspective, e.g. the index-of-dissimilarity and
# LIC/HIC charts), so each row of this heatmap answers "for this income group, is this cause
# over/under-researched relative to that SAME group's own burden profile" -- not a raw-volume
# comparison across groups.
per_cause_df = pd.read_csv(os.path.join(OUT_DIR, 'perspective4_income_group_alignment_by_cause.csv'))
p1 = pd.read_csv(os.path.join(OUT_DIR, 'perspective1_global_alignment.csv'), index_col=0)
cause_order = p1.sort_values('log2_research_to_burden_ratio').index.tolist()
group_order = ['LIC', 'LMIC', 'UMIC', 'HIC']

n_pivot = per_cause_df.pivot(index='income_group', columns='cause', values='n_trials').reindex(
    index=group_order, columns=cause_order)
ig_log2_ratio = pd.read_csv(os.path.join(OUT_DIR, 'income_group_cause_heatmap_log2_ratio.csv'), index_col=0)
ig_log2_ratio = ig_log2_ratio.reindex(index=group_order, columns=cause_order)

cmap = LinearSegmentedColormap.from_list('orange_white_blue', [ORANGE, SURFACE, BLUE], N=256)
vmax = 5  # log2 units = 32x, same cap as the cause x age-band heatmap for a consistent visual scale
norm = TwoSlopeNorm(vcenter=0, vmin=-vmax, vmax=vmax)

fig, ax = plt.subplots(figsize=(15, 4.4))
im = ax.imshow(ig_log2_ratio.values, cmap=cmap, norm=norm, aspect='auto')
ax.set_xticks(range(len(cause_order)))
ax.set_xticklabels(cause_order, fontsize=8.5)
ax.set_yticks(range(len(group_order)))
ax.set_yticklabels(group_order, fontsize=9.5)
plt.setp(ax.get_xticklabels(), rotation=45, ha='right', rotation_mode='anchor')

for i, g in enumerate(group_order):
    for j, c in enumerate(cause_order):
        v = ig_log2_ratio.loc[g, c]
        n = n_pivot.loc[g, c]
        ratio_txt = f"{2**v:.2f}" if n > 0 else 'no trials'
        text_color = TEXT_PRIMARY if abs(v) < vmax * 0.6 else SURFACE
        alpha = 0.55 if n < 5 else 1.0
        ax.text(j, i - 0.17, ratio_txt, ha='center', va='center', fontsize=7.3, color=text_color, alpha=alpha)
        ax.text(j, i + 0.22, f"n={int(n)}", ha='center', va='center', fontsize=6.0, color=text_color,
                alpha=alpha * 0.85, style='italic')

ax.set_xticks(np.arange(-0.5, len(cause_order), 1), minor=True)
ax.set_yticks(np.arange(-0.5, len(group_order), 1), minor=True)
ax.grid(which='minor', color=SURFACE, linewidth=1.5)
ax.tick_params(which='minor', length=0)
for spine in ax.spines.values():
    spine.set_visible(False)

cbar = fig.colorbar(im, ax=ax, orientation='vertical', fraction=0.02, pad=0.01)
cbar.set_label('RCT-to-burden ratio (log2 scale; 1.0 = proportional to own-group burden)', fontsize=8.5)
cbar_ticks = list(range(-vmax, vmax + 1))
cbar.set_ticks(cbar_ticks)
cbar.set_ticklabels([f"{2**t:.2f}" for t in cbar_ticks])
cbar.ax.tick_params(labelsize=7.5)

plt.tight_layout()
plt.savefig(os.path.join(PLOTS_DIR, 'income_group_cause_heatmap.png'), dpi=200, bbox_inches='tight')
plt.close()
print("Saved income_group_cause_heatmap.png")
