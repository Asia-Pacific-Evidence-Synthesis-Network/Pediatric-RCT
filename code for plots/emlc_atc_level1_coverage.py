"""
Figure 2. Pediatric RCT evidence coverage of medicines on the WHO Model List of Essential
Medicines for Children (EMLc), by WHO ATC first-level group. Horizontal bar chart, ranked
by descending coverage; each bar labeled with pct and (matched/total). Genitourinary system
& sex hormones (n=0 EMLc medicines) has no bar and is called out in a footnote instead.

Self-contained: reads emlc_atc_level1_coverage.json from this same folder (a copy of
results_v2_20260809/emlc_atc_level1_coverage_v2.json, the source that matches the manuscript
text exactly -- overall 241/359 = 67.1%, anti-infectives 63.6%, etc.) and saves the figure
back into this folder.
"""
import os
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))

BLUE = '#2a78d6'
TEXT_PRIMARY = '#0b0b0b'
TEXT_SECONDARY = '#52514e'
GRID = '#e4e2dc'
SURFACE = '#ffffff'

plt.rcParams.update({
    'font.family': 'sans-serif', 'font.size': 11,
    'axes.edgecolor': GRID, 'axes.labelcolor': TEXT_SECONDARY, 'text.color': TEXT_PRIMARY,
    'xtick.color': TEXT_SECONDARY, 'ytick.color': TEXT_SECONDARY,
    'figure.facecolor': SURFACE, 'axes.facecolor': SURFACE, 'savefig.facecolor': SURFACE,
})

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

with open(os.path.join(HERE, 'emlc_atc_level1_coverage.json')) as f:
    data = json.load(f)

rows = []
for L, g in data['group_coverage'].items():
    if g['n_total'] == 0:
        continue  # Genitourinary -- no EMLc medicines in this group, footnoted instead
    rows.append({'label': ATC_NAMES[L], 'n_total': g['n_total'],
                 'n_matched': g['n_matched'], 'pct': g['pct']})
rows.sort(key=lambda r: r['pct'])  # ascending, since barh plots bottom-to-top

fig, ax = plt.subplots(figsize=(10, 8))
y = range(len(rows))
ax.barh(y, [r['pct'] for r in rows], color=BLUE, height=0.6, zorder=3)
ax.set_yticks(list(y))
ax.set_yticklabels([f"{r['label']}  (n={r['n_total']})" for r in rows], fontsize=10.5)
for i, r in enumerate(rows):
    ax.text(r['pct'] + 1.5, i, f"{r['pct']:.1f}%  ({r['n_matched']}/{r['n_total']})",
            va='center', fontsize=10, color=TEXT_PRIMARY)
ax.set_xlim(0, 110)
ax.set_xticks(range(0, 101, 20))
ax.set_xticklabels([f"{t}%" for t in range(0, 101, 20)])
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.grid(axis='x', color=GRID, linewidth=0.8, zorder=0)
ax.set_axisbelow(True)
ax.tick_params(axis='y', length=0)
ax.set_xlabel('% of EMLc medicines in this group with >=1 supporting pediatric RCT', fontsize=11)

fig.text(0.01, -0.01, 'Genitourinary system & sex hormones has no EMLc medicines in this '
                       'group and is omitted.', fontsize=9.5, color=TEXT_SECONDARY)

plt.tight_layout()
plt.savefig(os.path.join(HERE, 'emlc_atc_level1_coverage.png'), dpi=200, bbox_inches='tight',
            pad_inches=0.3)
plt.close()
print("saved emlc_atc_level1_coverage.png")
