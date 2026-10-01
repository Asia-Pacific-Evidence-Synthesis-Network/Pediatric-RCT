"""
Figure S2: (A) world choropleth map of trial counts per country, (B) full bar chart of all
countries ranked by trial count.

Split from the original country_map_plots.py: this is the plotting half only. Reads
country_trial_counts.csv, written by country_map_analysis.py, instead of an in-memory variable.
"""
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio

counts = pd.read_csv('/Users/leayu/Documents/trend_rct/analysis/country_trial_counts.csv',
                      index_col=0)['n_trials']

# =====================================================================================
# Panel A: choropleth world map, binned like the reference figure (0, 1-10, 11-100, 101-500, >500)
# =====================================================================================
BIN_EDGES = [-0.5, 0.5, 10.5, 100.5, 500.5, np.inf]
BIN_LABELS = ['0', '1–10', '11–100', '101–500', '>500']
BIN_COLORS = ['#d9d9d6', '#f6ddc8', '#e3a487', '#c96f52', '#9e3a26']  # light->dark warm sequential, gray for 0

# Country-name -> ISO-3 mapping needed for plotly choropleth; use plotly's built-in name matching
# via locationmode='country names', which handles most standard English names directly.
NAME_FIXES = {
    'South Korea':'South Korea', 'North Korea':'North Korea', "Côte d'Ivoire":"Cote d'Ivoire",
    'DR Congo':'Democratic Republic of the Congo', 'Congo':'Republic of Congo',
    'Vietnam':'Vietnam', 'North Macedonia':'North Macedonia', 'Russia':'Russia',
}
plot_countries = counts.rename(index=lambda c: NAME_FIXES.get(c, c))
plot_df = plot_countries.reset_index()
plot_df.columns = ['country', 'n_trials']

def bin_label(n):
    for i in range(len(BIN_EDGES)-1):
        if BIN_EDGES[i] < n <= BIN_EDGES[i+1]:
            return BIN_LABELS[i]
    return BIN_LABELS[-1]
plot_df['bin'] = plot_df['n_trials'].apply(bin_label)

fig = go.Figure()
for label, color in zip(BIN_LABELS, BIN_COLORS):
    sub = plot_df[plot_df['bin'] == label]
    fig.add_trace(go.Choropleth(
        locations=sub['country'], locationmode='country names', z=[1]*len(sub),
        colorscale=[[0, color], [1, color]], showscale=False,
        marker_line_color='#8a8a86', marker_line_width=0.4,
        name=label, hovertext=sub.apply(lambda r: f"{r['country']}: {r['n_trials']} trials", axis=1),
        hoverinfo='text',
    ))
# legend proxies
for label, color in zip(BIN_LABELS, BIN_COLORS):
    fig.add_trace(go.Scattergeo(lon=[None], lat=[None], marker=dict(size=12, color=color, symbol='square'),
                                 name=label, showlegend=True))

fig.update_layout(
    geo=dict(
        showframe=False, showcoastlines=False, projection_type='natural earth',
        landcolor='#d9d9d6', showland=True, showcountries=True,
        countrycolor='#8a8a86',
        bgcolor='#fcfcfb',
    ),
    legend=dict(title='Number of trials', x=0.02, y=0.35, bgcolor='rgba(255,255,255,0.8)',
                font=dict(size=11)),
    paper_bgcolor='#fcfcfb',
    width=1400, height=750,
    margin=dict(l=10, r=10, t=10, b=10),
)
fig.write_image('/Users/leayu/Documents/trend_rct/figures/country_map.png', scale=2)
print("saved country_map.png")

# =====================================================================================
# Panel B: full bar chart of all countries, ranked descending
# =====================================================================================
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

BLUE = '#2a78d6'
TEXT_PRIMARY = '#0b0b0b'
TEXT_SECONDARY = '#52514e'
GRID = '#e4e2dc'
SURFACE = '#fcfcfb'
plt.rcParams.update({
    'font.family': 'sans-serif', 'font.size': 9,
    'axes.edgecolor': GRID, 'axes.labelcolor': TEXT_SECONDARY, 'text.color': TEXT_PRIMARY,
    'xtick.color': TEXT_SECONDARY, 'ytick.color': TEXT_SECONDARY,
    'figure.facecolor': SURFACE, 'axes.facecolor': SURFACE, 'savefig.facecolor': SURFACE,
})

sorted_counts_all = counts.sort_values(ascending=False)
sorted_counts = sorted_counts_all.head(20)
print(f"\nTotal countries: {len(sorted_counts_all)}; shown in bar chart: top {len(sorted_counts)} "
      f"(full ranking still in the CSV)")

fig2, ax = plt.subplots(figsize=(11, 6))
x = range(len(sorted_counts))
ax.bar(x, sorted_counts.values, color=BLUE, width=0.65, zorder=3)
for i, v in enumerate(sorted_counts.values):
    ax.text(i, v + max(sorted_counts.values)*0.015, str(int(v)), ha='center', va='bottom',
            fontsize=9, color=TEXT_PRIMARY)
ax.set_xticks(list(x))
ax.set_xticklabels(sorted_counts.index, rotation=45, ha='right', fontsize=9.5)
ax.set_ylabel('Trials (n)', fontsize=11)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(axis='y', color=GRID, linewidth=0.7, zorder=0)
ax.set_axisbelow(True)
ax.set_xlim(-0.7, len(sorted_counts) - 0.3)
ax.set_ylim(0, max(sorted_counts.values) * 1.1)
plt.tight_layout()
plt.savefig('/Users/leayu/Documents/trend_rct/figures/country_bar_top20.png', dpi=200)
plt.close()
print("saved country_bar_top20.png")
