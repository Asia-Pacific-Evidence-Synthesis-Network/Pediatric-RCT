"""
EMLc RCT-evidence coverage by WHO ATC first-level group.
"""
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

BLUE = '#2a78d6'
TEXT_PRIMARY = '#0b0b0b'
TEXT_SECONDARY = '#52514e'
GRID = '#e4e2dc'
SURFACE = '#fcfcfb'

plt.rcParams.update({
    'font.family': 'sans-serif', 'font.size': 10,
    'axes.edgecolor': GRID, 'axes.labelcolor': TEXT_SECONDARY, 'text.color': TEXT_PRIMARY,
    'xtick.color': TEXT_SECONDARY, 'ytick.color': TEXT_SECONDARY,
    'figure.facecolor': SURFACE, 'axes.facecolor': SURFACE, 'savefig.facecolor': SURFACE,
})

FIG = '/Users/leayu/Documents/trend_rct/figures'
ANA = '/Users/leayu/Documents/trend_rct/analysis'

ATC_NAMES = {
    'A': 'Alimentary tract & metabolism', 'B': 'Blood & blood-forming organs',
    'C': 'Cardiovascular system', 'D': 'Dermatologicals',
    'G': 'Genitourinary system & sex hormones',
    'H': 'Systemic hormonal preparations (excl. sex hormones/insulins)',
    'J': 'Antiinfectives for systemic use',
    'L': 'Antineoplastic & immunomodulating agents', 'M': 'Musculoskeletal system',
    'N': 'Nervous system', 'P': 'Antiparasitic products, insecticides & repellents',
    'R': 'Respiratory system', 'S': 'Sensory organs', 'V': 'Various',
}

with open('/Users/leayu/Documents/trend_rct/results_v2_20260809/emlc_atc_level1_coverage_v2.json') as f:
    data = json.load(f)
# the _v2 coverage file is keyed by ATC letter (group_coverage dict), not the flat list-of-dicts
# format this script originally expected -- converted here to the shape the rest of the script uses
rows = [{'group': letter, 'label': ATC_NAMES[letter], 'n_total': g['n_total'],
         'n_matched': g['n_matched'], 'pct_matched': g['pct']}
        for letter, g in data['group_coverage'].items()]
rows = [r for r in rows if r['n_total'] > 0]  # G has zero EMLc medicines mapped -- excluded, noted in text
rows.sort(key=lambda r: r['pct_matched'])

def style(ax):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_axisbelow(True)
    ax.grid(axis='x', color=GRID, linewidth=0.8, zorder=0)
    ax.xaxis.set_major_formatter(mticker.PercentFormatter(xmax=100, decimals=0))

fig, ax = plt.subplots(figsize=(9, 6.5))
labels = [f"{r['group']} — {r['label']}  (n={r['n_total']})" for r in rows]
vals = [r['pct_matched'] for r in rows]
y = range(len(rows))
ax.barh(y, vals, color=BLUE, height=0.6, zorder=3)
for i, r in zip(y, rows):
    ax.text(r['pct_matched'] + 1.5, i, f"{r['pct_matched']:.0f}%  ({r['n_matched']}/{r['n_total']})",
            va='center', fontsize=8.5, color=TEXT_SECONDARY)
ax.set_yticks(list(y))
ax.set_yticklabels(labels, fontsize=9)
style(ax)
ax.set_xlim(0, 115)
ax.set_xlabel('% of EMLc medicines in this group with ≥1 supporting pediatric RCT', fontsize=9.5)
ax.set_title('WHO Essential Medicines for Children: RCT evidence coverage\nby ATC first-level group',
             fontsize=13, color=TEXT_PRIMARY, loc='left', fontweight='bold', pad=12)
fig.text(0.02, -0.02, "Genitourinary system & sex hormones (G) has no EMLc medicines in this group and is omitted.",
          fontsize=8, color=TEXT_SECONDARY)
plt.tight_layout()
plt.savefig(f'{FIG}/emlc_atc_level1_coverage.png', dpi=200, bbox_inches='tight')
plt.close()
print("saved emlc_atc_level1_coverage.png")
