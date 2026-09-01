"""
Figure 1A. Income-group composition of pediatric medication RCTs, by decade.
Stacked bar chart (LIC/LMIC/UMIC/HIC shares sum to 100% within each decade).

Self-contained: reads income_group_trend_by_decade.csv from this same folder
(a copy of results_v2_20260809/income_group_trend_by_decade_v2.csv, the source
that matches the numbers reported in the manuscript text) and saves the figure
back into this folder.
"""
import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

HERE = os.path.dirname(os.path.abspath(__file__))

BLUE = '#2a78d6'
TEXT_PRIMARY = '#0b0b0b'
TEXT_SECONDARY = '#52514e'
GRID = '#e4e2dc'
SURFACE = '#ffffff'
CAT = {'LIC': '#e34948', 'LMIC': '#eda100', 'UMIC': '#1baf7a', 'HIC': '#2a78d6'}

plt.rcParams.update({
    'font.family': 'sans-serif', 'font.size': 10,
    'axes.edgecolor': GRID, 'axes.labelcolor': TEXT_SECONDARY, 'text.color': TEXT_PRIMARY,
    'xtick.color': TEXT_SECONDARY, 'ytick.color': TEXT_SECONDARY,
    'figure.facecolor': SURFACE, 'axes.facecolor': SURFACE, 'savefig.facecolor': SURFACE,
})

GROUPS = ['LIC', 'LMIC', 'UMIC', 'HIC']

decade_df = pd.read_csv(os.path.join(HERE, 'income_group_trend_by_decade.csv'))
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
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=4, frameon=False, fontsize=9.5)
plt.tight_layout()
plt.savefig(os.path.join(HERE, 'income_group_trend_by_decade.png'), dpi=200, bbox_inches='tight')
plt.close()
print("saved income_group_trend_by_decade.png")
