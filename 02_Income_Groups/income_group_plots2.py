"""
Figures for Analysis 6: trial characteristics by World Bank income group.
1. Temporal trend of income-group share, stacked bar by decade
2. Therapeutic focus (ATC first-level), heatmap by income group
3. Trial size & power to detect AE signals, by income group
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.colors import LinearSegmentedColormap

BLUE = '#2a78d6'
TEXT_PRIMARY = '#0b0b0b'
TEXT_SECONDARY = '#52514e'
GRID = '#e4e2dc'
SURFACE = '#fcfcfb'
CAT = {'LIC': '#e34948', 'LMIC': '#eda100', 'UMIC': '#1baf7a', 'HIC': '#2a78d6'}
SEQ_BLUE_STEPS = ['#cde2fb', '#b7d3f6', '#9ec5f4', '#86b6ef', '#6da7ec', '#5598e7',
                  '#3987e5', '#2a78d6', '#256abf', '#1c5cab', '#184f95', '#104281', '#0d366b']
SEQ_BLUE = LinearSegmentedColormap.from_list('seq_blue', SEQ_BLUE_STEPS, N=256)

plt.rcParams.update({
    'font.family': 'sans-serif', 'font.size': 10,
    'axes.edgecolor': GRID, 'axes.labelcolor': TEXT_SECONDARY, 'text.color': TEXT_PRIMARY,
    'xtick.color': TEXT_SECONDARY, 'ytick.color': TEXT_SECONDARY,
    'figure.facecolor': SURFACE, 'axes.facecolor': SURFACE, 'savefig.facecolor': SURFACE,
})

FIG = '/Users/leayu/Documents/trend_rct/figures'
ANA = '/Users/leayu/Documents/trend_rct/results_v2_20260809'
GROUPS = ['LIC', 'LMIC', 'UMIC', 'HIC']

# ==================================================================
# 1. Temporal trend, stacked bar by decade
# ==================================================================
decade_df = pd.read_csv(f'{ANA}/income_group_trend_by_decade_v2.csv')
decade_df = decade_df[decade_df['Decade'] != 'Before 1960']

fig, ax = plt.subplots(figsize=(10, 6))
bottom = np.zeros(len(decade_df))
for g in GROUPS:
    vals = decade_df[g].values
    ax.bar(decade_df['Decade'], vals, bottom=bottom, color=CAT[g], width=0.7, label=g,
           edgecolor=SURFACE, linewidth=0.6, zorder=3)
    bottom += vals
ax.set_ylim(0, 100)
ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=100, decimals=0))
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(axis='y', color=GRID, linewidth=0.8, zorder=0)
ax.set_axisbelow(True)
ax.set_ylabel('Share of country-attributable trials (%)', fontsize=10)
ax.set_xlabel('Decade', fontsize=10)
plt.xticks(rotation=30, ha='right')
ax.set_title('Income-group composition of pediatric medication RCTs, by decade',
             fontsize=13, color=TEXT_PRIMARY, loc='left', fontweight='bold', pad=10)
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=4, frameon=False, fontsize=9.5)
plt.tight_layout()
plt.savefig(f'{FIG}/income_group_trend_by_decade.png', dpi=200, bbox_inches='tight')
plt.close()
print("saved income_group_trend_by_decade.png")

# ==================================================================
# 2. ATC first-level distribution, heatmap by income group
# ==================================================================
atc_df = pd.read_csv(f'{ANA}/income_group_atc_distribution_v2.csv')
atc_df = atc_df.set_index('income_group').reindex(GROUPS)
atc_cols = [c for c in atc_df.columns if c != 'n_trials']
mat = atc_df[atc_cols].to_numpy()

fig, ax = plt.subplots(figsize=(10, 4.2))
im = ax.imshow(mat, cmap=SEQ_BLUE, vmin=0, vmax=mat.max(), aspect='auto')
ax.set_xticks(range(len(atc_cols)))
ax.set_xticklabels(atc_cols, fontsize=10)
ax.xaxis.set_ticks_position('top')
ax.set_yticks(range(len(GROUPS)))
ax.set_yticklabels([f"{g}  (n={int(atc_df.loc[g,'n_trials'])})" for g in GROUPS], fontsize=10)
ax.tick_params(axis='both', which='major', length=0)
for spine in ax.spines.values():
    spine.set_visible(False)
ax.set_xticks(np.arange(-0.5, len(atc_cols), 1), minor=True)
ax.set_yticks(np.arange(-0.5, len(GROUPS), 1), minor=True)
ax.grid(which='minor', color=SURFACE, linewidth=2.5)
ax.tick_params(which='minor', length=0)
for i in range(len(GROUPS)):
    for j in range(len(atc_cols)):
        v = mat[i, j]
        txt_color = 'white' if v > mat.max()*0.55 else TEXT_PRIMARY
        ax.text(j, i, f"{v:.0f}", ha='center', va='center', fontsize=9, color=txt_color)
ax.set_title('WHO ATC first-level group (% of classified trials), by income group',
             fontsize=13, color=TEXT_PRIMARY, loc='left', fontweight='bold', pad=45)
plt.tight_layout()
plt.savefig(f'{FIG}/income_group_atc_heatmap.png', dpi=200, bbox_inches='tight')
plt.close()
print("saved income_group_atc_heatmap.png")

# ==================================================================
# 3. Trial size & power, by income group
# ==================================================================
power_df = pd.read_csv(f'{ANA}/income_group_power_v2.csv')
power_df = power_df.set_index('income_group').reindex(GROUPS).reset_index()

fig, axes = plt.subplots(1, 2, figsize=(11, 5))
ax = axes[0]
colors = [CAT[g] for g in GROUPS]
ax.bar(power_df['income_group'], power_df['median_n'], color=colors, width=0.6, zorder=3)
for i, v in enumerate(power_df['median_n']):
    ax.text(i, v + 5, f"{v:.0f}", ha='center', fontsize=10, fontweight='bold', color=TEXT_PRIMARY)
ax.set_ylabel('Median sample size (N)', fontsize=10)
ax.set_title('A   Trial size', fontsize=12, color=TEXT_PRIMARY, loc='left', fontweight='bold')
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
ax.grid(axis='y', color=GRID, linewidth=0.8, zorder=0); ax.set_axisbelow(True)

ax = axes[1]
ax.bar(power_df['income_group'], power_df['median_mde_5pct'], color=colors, width=0.6, zorder=3)
for i, v in enumerate(power_df['median_mde_5pct']):
    ax.text(i, v + 0.3, f"{v:.1f}", ha='center', fontsize=10, fontweight='bold', color=TEXT_PRIMARY)
ax.set_ylabel('Median min. detectable AE risk\nincrease, pct-points (baseline=5%)', fontsize=9.5)
ax.set_title('B   Safety-detection power', fontsize=12, color=TEXT_PRIMARY, loc='left', fontweight='bold')
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
ax.grid(axis='y', color=GRID, linewidth=0.8, zorder=0); ax.set_axisbelow(True)

fig.suptitle('Trial size and statistical power to detect adverse-event signals, by income group',
             fontsize=13, color=TEXT_PRIMARY, x=0.02, y=1.02, ha='left', fontweight='bold')
plt.tight_layout()
plt.savefig(f'{FIG}/income_group_power.png', dpi=200, bbox_inches='tight')
plt.close()
print("saved income_group_power.png")
