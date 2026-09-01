"""
Figure 1B. Drug classes (WHO ATC Level-1 anatomical group, % of each income group's
classified trials -- non-exclusive, a multi-drug trial counts in every class it involves),
by income group. Heatmap: rows = income group, columns = ATC first-level group, in standard
ATC letter-code order (A,B,C,D,G,H,J,L,M,N,P,R,S,V).

Self-contained: reads income_group_atc_distribution.csv from this same folder (recomputed
from Trial bank_13269.xlsx + trial_country_income_v2.csv, verified to match
results_v2_20260809/plots/income_group_atc_heatmap.png exactly) and saves the figure back
into this folder.
"""
import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

HERE = os.path.dirname(os.path.abspath(__file__))

TEXT_PRIMARY = '#0b0b0b'
TEXT_SECONDARY = '#52514e'
GRID = '#e4e2dc'
SURFACE = '#ffffff'
SEQ_BLUE_STEPS = ['#cde2fb', '#b7d3f6', '#9ec5f4', '#86b6ef', '#6da7ec', '#5598e7',
                  '#3987e5', '#2a78d6', '#256abf', '#1c5cab', '#184f95', '#104281', '#0d366b']
SEQ_BLUE = LinearSegmentedColormap.from_list('seq_blue', SEQ_BLUE_STEPS, N=256)

plt.rcParams.update({
    'font.family': 'sans-serif', 'font.size': 10,
    'axes.edgecolor': GRID, 'axes.labelcolor': TEXT_SECONDARY, 'text.color': TEXT_PRIMARY,
    'xtick.color': TEXT_SECONDARY, 'ytick.color': TEXT_SECONDARY,
    'figure.facecolor': SURFACE, 'axes.facecolor': SURFACE, 'savefig.facecolor': SURFACE,
})

GROUPS = ['LIC', 'LMIC', 'UMIC', 'HIC']
ATC_LETTERS = list('ABCDGHJLMNPRSV')
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

atc_df = pd.read_csv(os.path.join(HERE, 'income_group_atc_distribution.csv'))
atc_df = atc_df.set_index('income_group').reindex(GROUPS)
mat = atc_df[ATC_LETTERS].to_numpy()
col_labels = [ATC_NAMES[L] for L in ATC_LETTERS]
row_labels = [f"{g} (n={int(atc_df.loc[g, 'n_trials'])})" for g in GROUPS]

fig, ax = plt.subplots(figsize=(13.6, 4.8))
im = ax.imshow(mat, cmap=SEQ_BLUE, vmin=0, vmax=mat.max(), aspect='auto')
ax.set_xticks(range(len(col_labels)))
ax.set_xticklabels(col_labels, fontsize=8.5)
plt.setp(ax.get_xticklabels(), rotation=45, ha='right', rotation_mode='anchor')
ax.set_yticks(range(len(GROUPS)))
ax.set_yticklabels(row_labels, fontsize=10)
ax.tick_params(axis='both', which='major', length=0)
for spine in ax.spines.values():
    spine.set_visible(False)
ax.set_xticks(np.arange(-0.5, len(col_labels), 1), minor=True)
ax.set_yticks(np.arange(-0.5, len(GROUPS), 1), minor=True)
ax.grid(which='minor', color=SURFACE, linewidth=2.5)
ax.tick_params(which='minor', length=0)
for i in range(len(GROUPS)):
    for j in range(len(col_labels)):
        v = mat[i, j]
        txt_color = 'white' if v > mat.max()*0.55 else TEXT_PRIMARY
        ax.text(j, i, f"{v:.1f}%", ha='center', va='center', fontsize=8.5, color=txt_color)

cbar = fig.colorbar(im, ax=ax, orientation='vertical', fraction=0.025, pad=0.01)
cbar.set_label("% of income group's classified trials", fontsize=9.5)
cbar.ax.tick_params(labelsize=8.5)

plt.tight_layout()
fig.canvas.draw()
plt.savefig(os.path.join(HERE, 'income_group_atc_heatmap.png'), dpi=200, bbox_inches='tight', pad_inches=0.35)
plt.close()
print("saved income_group_atc_heatmap.png")
