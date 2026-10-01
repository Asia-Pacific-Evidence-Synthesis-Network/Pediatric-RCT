"""
Figures for the new ATC_Level1 (WHO ATC first-level anatomical group) classification:
1. Overall distribution, all 14 groups, ranked bar chart
2. Temporal trend, top 8 groups by decade
"""
import json
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

BLUE = '#2a78d6'
TEXT_PRIMARY = '#0b0b0b'
TEXT_SECONDARY = '#52514e'
GRID = '#e4e2dc'
SURFACE = '#fcfcfb'
CAT8 = ['#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4', '#008300', '#4a3aa7', '#e34948']

plt.rcParams.update({
    'font.family': 'sans-serif', 'font.size': 10,
    'axes.edgecolor': GRID, 'axes.labelcolor': TEXT_SECONDARY, 'text.color': TEXT_PRIMARY,
    'xtick.color': TEXT_SECONDARY, 'ytick.color': TEXT_SECONDARY,
    'figure.facecolor': SURFACE, 'axes.facecolor': SURFACE, 'savefig.facecolor': SURFACE,
})

FIG = '/Users/leayu/Documents/trend_rct/figures'
ANA = '/Users/leayu/Documents/trend_rct/analysis'

def style(ax):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_axisbelow(True)
    ax.grid(axis='y', color=GRID, linewidth=0.8, zorder=0)

# ==================================================================
# 1. Overall distribution, all 14 groups
# ==================================================================
with open(f'{ANA}/atc_level1_table1.json') as f:
    data = json.load(f)
rows = sorted(data['rows'], key=lambda r: r[2])
labels = [f"{r[0]} — {r[1]}" for r in rows]
vals = [r[2] for r in rows]
pcts = [r[3] for r in rows]

fig, ax = plt.subplots(figsize=(9.5, 7))
y = range(len(labels))
ax.barh(y, vals, color=BLUE, height=0.65, zorder=3)
for i, v, p in zip(y, vals, pcts):
    ax.text(v + max(vals)*0.012, i, f"{v} ({p}%)", va='center', fontsize=8.5, color=TEXT_PRIMARY)
ax.set_yticks(list(y))
ax.set_yticklabels(labels, fontsize=9)
style(ax)
ax.set_xlabel('Trials (n, non-mutually-exclusive)', fontsize=10)
ax.set_title('Trials by WHO ATC first-level anatomical group', fontsize=13, color=TEXT_PRIMARY,
             loc='left', fontweight='bold', pad=10)
ax.set_xlim(0, max(vals)*1.22)
plt.tight_layout()
plt.savefig(f'{FIG}/atc_level1_frequency.png', dpi=200, bbox_inches='tight')
plt.close()
print("saved atc_level1_frequency.png")

# ==================================================================
# 2. Temporal trend, top 8 groups by decade
# ==================================================================
decade_df = pd.read_csv(f'{ANA}/atc_level1_trend_by_decade.csv')
decade_df = decade_df[decade_df['Decade'] != 'Before 1960']
top8 = [r[0] for r in sorted(data['rows'], key=lambda r: -r[2])[:8]]
group_labels = {r[0]: r[1] for r in data['rows']}

fig, ax = plt.subplots(figsize=(13.5, 6.5))
for i, col in enumerate(top8):
    ax.plot(decade_df['Decade'], decade_df[col], color=CAT8[i % 8], linewidth=2, marker='o',
            markersize=5, label=f"{col} — {group_labels[col]}", zorder=3)
style(ax)
ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=100, decimals=0))
ax.set_ylabel('Share of trials (%)', fontsize=10)
ax.set_xlabel('Decade', fontsize=10)
ax.set_title('Trial-share trends for the 8 largest ATC first-level groups, by decade',
             fontsize=13, color=TEXT_PRIMARY, loc='left', fontweight='bold', pad=10)
plt.xticks(rotation=30, ha='right')
ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1), frameon=False, fontsize=9,
          title='ATC group', title_fontsize=9)
plt.tight_layout()
plt.savefig(f'{FIG}/atc_level1_trend_by_decade.png', dpi=200, bbox_inches='tight')
plt.close()
print("saved atc_level1_trend_by_decade.png")
