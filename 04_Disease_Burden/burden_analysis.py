"""
Pediatric medication RCTs relative to disease burden -- full analysis pipeline, consolidated
into one file (previously six separate scripts: burden_merge_gbd.py, burden_by_gbd_cause.py,
burden_perspective1_global_analysis.py, burden_perspective2_age_band_analysis.py,
burden_cause_age_heatmap_analysis.py, burden_perspective3_income_group_analysis.py).

Runs as one linear pipeline, each step below reusing the in-memory output of the step before it
rather than round-tripping through disk (the original six scripts, run as separate processes,
had to re-read each other's CSV outputs; consolidated into one process, that's no longer
necessary). All the same CSV outputs are still written to disk, since the *_plots.py scripts
for this section are separate files that read them.

The trial bank is read once; each step takes its own copy before applying step-specific
filters/columns, so no step's intermediate columns or filtering leak into another step (matching
the original scripts' behavior exactly, since each ran as an independent process with its own
untouched copy of the data).
"""
import pandas as pd
import numpy as np
import os

TRIAL_BANK = '/Users/leayu/Documents/trend_rct/Trial bank_13269.xlsx'
INCOME_FILE = '/Users/leayu/Documents/trend_rct/results_v2_20260809/trial_country_income_v2.csv'
OUT_DIR = '/Users/leayu/Documents/trend_rct/burden_of_disease_results'
EXCLUDED_CAUSES = ['Transport injuries', 'Self-harm and interpersonal violence']
BAND_ORDER = ['Neonate', 'Infant', 'Young child', 'Child', 'Adolescent']

df_trials_raw = pd.read_excel(TRIAL_BANK, sheet_name='all')

# =====================================================================================
# Step 1: build one tidy long-format table (and one wide-format table, one row per
# location x cause x age x year) from the GBD 2023 pediatric DALY export, restricted to
# 1990-2022, that the rest of the pipeline uses directly.
#
# Source file (all_GBD_data/IHME-GBD_2023_DATA-60e9d74f-1.csv): a single export covering measure =
# DALYs only, metric = Number (raw counts, not GBD's own pre-computed %), sex = Both, the 7 native
# pediatric age bins, all 22 GBD Level-2 causes, 1990-2023 (2023 is dropped below -- see Filters),
# and 10 locations: the 6 WHO regions + the 4 World Bank income levels. Deaths/YLLs/YLDs are not
# part of this export and are not used anywhere in the current analysis.
#
# No 'Global' row is present in this export. It is derived by summing the 6 WHO regions per
# (cause, age, year) -- validated by spot-check against a prior export's true Global row (agreement
# within ~0.1-0.5% across multiple cause/age/year combinations checked), consistent with WHO's own
# regional grouping being an exhaustive partition of all countries.
#
# Filters: restricted to year 1990-2022 (2023 dropped, to match the trial bank's own data window and
# avoid a partial/most-recent-year estimate that is typically less stable than fully-lagged years).
# =====================================================================================
SRC_DIR = '/Users/leayu/Documents/trend_rct/all_GBD_data'
SRC_FILE = 'IHME-GBD_2023_DATA-60e9d74f-1.csv'

WHO_REGIONS = ['African Region', 'Eastern Mediterranean Region', 'European Region',
               'Region of the Americas', 'South-East Asia Region', 'Western Pacific Region']
KEEP_COLS = ['measure_name', 'location_name', 'age_name', 'cause_name', 'metric_name', 'year', 'val']

raw = pd.read_csv(os.path.join(SRC_DIR, SRC_FILE))
assert (raw['measure_name'] == 'DALYs (Disability-Adjusted Life Years)').all(), "expected DALYs only"
assert (raw['metric_name'] == 'Number').all(), "expected metric='Number' throughout"
assert (raw['sex_name'] == 'Both').all(), "expected sex='Both' throughout"

raw = raw[raw['year'] <= 2022]
print(f"Rows after restricting to year <= 2022: {len(raw)} (years: {sorted(raw['year'].unique())})")

raw = raw[KEEP_COLS]
assert raw.duplicated(subset=['location_name', 'age_name', 'cause_name', 'year']).sum() == 0, \
    "unexpected duplicate (location,age,cause,year) rows in source"

# ---- derive 'Global' as the sum of the 6 WHO regions ----
who_df = raw[raw['location_name'].isin(WHO_REGIONS)]
assert who_df['location_name'].nunique() == 6, "expected all 6 WHO regions present"
global_df = who_df.groupby(['measure_name', 'age_name', 'cause_name', 'metric_name', 'year'],
                            as_index=False)['val'].sum()
global_df['location_name'] = 'Global'
global_df = global_df[KEEP_COLS]
print(f"Derived 'Global' rows (summed from the 6 WHO regions): {len(global_df)}")

# ---- combine: derived Global + the 6 WHO regions + the 4 World Bank income levels ----
long_df = pd.concat([global_df, raw], ignore_index=True)

dupe_check = long_df.duplicated(subset=['measure_name', 'location_name', 'age_name', 'cause_name', 'year'])
print(f"Duplicate (measure,location,age,cause,year) rows: {dupe_check.sum()} (should be 0)")
assert dupe_check.sum() == 0

print(f"\nTotal long-format rows: {len(long_df)}")
print("Locations ({}): {}".format(long_df['location_name'].nunique(), sorted(long_df['location_name'].unique())))
print("Causes ({}): {}".format(long_df['cause_name'].nunique(), sorted(long_df['cause_name'].unique())))
print("Ages:", sorted(long_df['age_name'].unique()))
print("Years:", sorted(long_df['year'].unique()))

long_df.to_csv(os.path.join(OUT_DIR, 'gbd_merged_long.csv'), index=False)
print(f"\nSaved gbd_merged_long.csv ({len(long_df)} rows)")

# ---- wide format: one row per (location, cause, age, year); single 'dalys' column ----
wide_df = long_df.pivot_table(index=['location_name', 'cause_name', 'age_name', 'year'],
                                columns='measure_name', values='val', aggfunc='first').reset_index()
wide_df.columns.name = None
wide_df = wide_df.rename(columns={'DALYs (Disability-Adjusted Life Years)': 'dalys'})
wide_df['dalys'] = wide_df['dalys'].fillna(0.0)

wide_df.to_csv(os.path.join(OUT_DIR, 'gbd_merged_wide.csv'), index=False)
print(f"Saved gbd_merged_wide.csv ({len(wide_df)} rows, columns: {list(wide_df.columns)})")

# =====================================================================================
# Step 2: aggregate GBD's 7 native pediatric age bins into per-cause, per-location totals, at
# GBD's own Level-2 cause granularity (22 causes) -- NO crosswalk to Topic_Category involved.
#
# Every trial in the trial bank has been individually classified into one of these same 22 GBD
# Level-2 causes (column `GBD_Level2_Cause`, see add_gbd_l2_column.py /
# update_gbd_l2_column_recheck.py) using each trial's own disease term and title. Because both
# sides of the comparison speak the same 22-cause vocabulary directly, no lossy many-to-many
# bucketing into the trial bank's 15 coarser Topic_Category groups is needed -- trial-share and
# burden-share can be compared cause-for-cause.
#
# Years: burden is AVERAGED across every year in the source data (1990-2022), not a single year,
# since the trial bank itself spans decades and a single most-recent-year burden snapshot doesn't
# represent the disease landscape the whole trial bank was conducted against. For every metric in
# this analysis, burden is only ever used as a SHARE (%) of the total across causes -- averaging
# vs. summing across years produces IDENTICAL shares (dividing every cause's total by the same
# year count before taking its share of the total cancels out exactly) -- so this is reported as
# an average annual burden (a standard, interpretable quantity), not a 33-year cumulative sum.
#
# Age rebinning is unchanged: GBD's 3 infancy sub-bins are summed into one Infant total; the other
# 4 native bins map 1:1 onto the paper's 5 age bands.
# =====================================================================================
AGE_TO_BAND = {
    '<28 days': 'Neonate',
    '1-5 months': 'Infant', '6-11 months': 'Infant', '12-23 months': 'Infant',
    '2-4 years': 'Young child',
    '5-9 years': 'Child',
    '10-19 years': 'Adolescent',
}

wide = wide_df.copy()
wide['age_band'] = wide['age_name'].map(AGE_TO_BAND)
assert wide['age_band'].notna().all(), "unmapped age_name found"

years = sorted(wide['year'].unique())
print(f"\nAveraging over {len(years)} years: {years}")

# average across years FIRST (per location, cause, native age bin), then roll up ages -- linear
# operations, so this is mathematically identical to averaging after rolling up ages
yearly_avg = wide.groupby(['location_name', 'cause_name', 'age_name', 'age_band'], as_index=False)[
    ['dalys']].mean()

# age-band level (all pediatric ages kept separate) -- used where age-band granularity matters
band_agg = yearly_avg.groupby(['location_name', 'cause_name', 'age_band'], as_index=False)[
    ['dalys']].sum()

# cause level (all pediatric ages 0-19 summed) -- used for Perspectives 1/2/3
cause_agg = yearly_avg.groupby(['location_name', 'cause_name'], as_index=False)[
    ['dalys']].sum()

band_agg.to_csv(os.path.join(OUT_DIR, 'gbd_burden_by_cause_age_band.csv'), index=False)
cause_agg.to_csv(os.path.join(OUT_DIR, 'gbd_burden_by_cause.csv'), index=False)

print(f"Saved gbd_burden_by_cause_age_band.csv ({len(band_agg)} rows)")
print(f"Saved gbd_burden_by_cause.csv ({len(cause_agg)} rows)")
print(f"\n{cause_agg['cause_name'].nunique()} GBD Level-2 causes, "
      f"{cause_agg['location_name'].nunique()} locations")

# =====================================================================================
# Perspective 1: overall global alignment between pediatric medication RCT research effort
# (trial-share by GBD Level-2 cause) and pediatric disease burden (DALY-share by the same GBD
# Level-2 cause).
#
# Denominator discipline: both shares are computed OVER THE SAME set of trials/burden that have a
# usable GBD Level-2 cause -- i.e. excluding trials classified "Not applicable" (procedures,
# sedation/anesthesia, generic symptoms with no attributable disease, placeholders). Two further
# causes (Transport injuries, Self-harm and interpersonal violence) are excluded from BOTH sides
# entirely -- medication RCTs are not a meaningful study design for injury/violence prevention or
# treatment, so these causes are structurally unresearchable by the trial bank's own scope (0 and
# 1 trials respectively) rather than genuinely under-researched.
#
# Metrics: log2(research-to-burden ratio) = log2(trial_share / burden_share). >0 = over-researched
# relative to burden; <0 = under-researched. Symmetric on the log scale, so a cause at 2x and a
# cause at 0.5x are equally far from parity. absolute gap = trial_share_pct - burden_share_pct.
# =====================================================================================
df1 = df_trials_raw.copy()
cause_counts_all = df1['GBD_Level2_Cause'].value_counts()
trial_counts = cause_counts_all.drop(['Not applicable'] + EXCLUDED_CAUSES, errors='ignore')
n_mapped_trials = trial_counts.sum()
trial_share = (trial_counts / n_mapped_trials * 100).rename('trial_share_pct')
print(f"\nTrials with a usable GBD Level-2 cause: {n_mapped_trials} / {len(df1)} total "
      f"({n_mapped_trials/len(df1)*100:.1f}%)")

burden_global = cause_agg[cause_agg['location_name'] == 'Global'].set_index('cause_name')
burden_global = burden_global.drop(EXCLUDED_CAUSES, errors='ignore')
total_dalys = burden_global['dalys'].sum()
burden_share = (burden_global['dalys'] / total_dalys * 100).rename('burden_share_pct')
print(f"Total pediatric DALYs (Global, average annual 1990-2022, across the 20 included GBD Level-2 causes): {total_dalys:,.0f}")

all_causes = burden_share.index
trial_share = trial_share.reindex(all_causes, fill_value=0.0)
trial_counts = trial_counts.reindex(all_causes, fill_value=0)

p1_merged = pd.concat([trial_share, burden_share], axis=1)
assert p1_merged.isna().sum().sum() == 0, f"unmatched causes:\n{p1_merged[p1_merged.isna().any(axis=1)]}"

with np.errstate(divide='ignore'):
    p1_merged['log2_research_to_burden_ratio'] = np.log2(p1_merged['trial_share_pct'] / p1_merged['burden_share_pct'])
p1_merged['absolute_gap_pp'] = p1_merged['trial_share_pct'] - p1_merged['burden_share_pct']
p1_merged['n_trials'] = trial_counts
p1_merged = p1_merged.sort_values('log2_research_to_burden_ratio', ascending=False)

p1_merged.to_csv(os.path.join(OUT_DIR, 'perspective1_global_alignment.csv'))
print("\n=== Perspective 1: global alignment, ranked by log2(research/burden) ratio ===")
pd.set_option('display.width', 140)
print(p1_merged.round(2).to_string())

cause_order = p1_merged.sort_values('log2_research_to_burden_ratio').index.tolist()  # most under-researched first

# =====================================================================================
# Perspective 2: is neonatal underrepresentation in pediatric medication RCTs proportionate to
# neonates' share of pediatric disease burden, or disproportionate?
#
# Methodological note on why this can't just reuse Table 1's Age_Band_WHO percentages directly:
# those are NON-mutually-exclusive (built from each trial's full enrolment range, so a trial
# spanning 3-17 years counts toward 3 different bands simultaneously -- they sum to >100%). GBD's
# age-band burden shares are mutually exclusive by construction (every DALY belongs to exactly one
# age bin, summing to 100%). Fix: fractional allocation -- split each trial's weight evenly across
# every band its range touches -- which produces a trial-share series that legitimately sums to
# 100% and is directly comparable to GBD's.
# =====================================================================================
df2 = df_trials_raw.copy()


def band_set(v):
    return [] if pd.isna(v) else [b for b in v.split('+') if b in BAND_ORDER]


df2['_bands'] = df2['Age_Band_WHO'].apply(band_set)
weights = {b: 0.0 for b in BAND_ORDER}
n_unclassified = 0
for bands in df2['_bands']:
    if not bands:
        n_unclassified += 1
        continue
    w = 1.0 / len(bands)
    for b in bands:
        weights[b] += w
n_classified = len(df2) - n_unclassified
age_trial_share = pd.Series({b: weights[b] / n_classified * 100 for b in BAND_ORDER}, name='trial_share_pct')
print(f"\nTrials with a usable age band: {n_classified} / {len(df2)}")
print("\nFractional trial-share by age band (sums to 100%):")
print(age_trial_share.round(2))

# burden-share by age band, Global, average annual 1990-2022, ALL causes (not just the 20
# cause-mapped ones -- age-band totals should reflect the FULL pediatric burden, independent of
# cause-classification quality, for consistency with how Table 1's own age-band % is computed
# over all trials)
AGE_TO_BAND_P2 = AGE_TO_BAND  # identical mapping, reused
dalys_g = long_df[(long_df['location_name'] == 'Global') &
                   (long_df['measure_name'] == 'DALYs (Disability-Adjusted Life Years)')].copy()
dalys_g['age_band'] = dalys_g['age_name'].map(AGE_TO_BAND_P2)
by_age_year = dalys_g.groupby(['age_name', 'age_band', 'year'])['val'].sum().reset_index()
by_age_avg = by_age_year.groupby(['age_name', 'age_band'])['val'].mean().reset_index()
burden_by_band = by_age_avg.groupby('age_band')['val'].sum()
age_burden_share = (burden_by_band / burden_by_band.sum() * 100).reindex(BAND_ORDER).rename('burden_share_pct')
print("\nBurden-share by age band (Global, average annual 1990-2022, all-cause DALYs, sums to 100%):")
print(age_burden_share.round(2))

p2_merged = pd.concat([age_trial_share, age_burden_share], axis=1)
p2_merged['log2_ratio'] = np.log2(p2_merged['trial_share_pct'] / p2_merged['burden_share_pct'])
p2_merged['absolute_gap_pp'] = p2_merged['trial_share_pct'] - p2_merged['burden_share_pct']
p2_merged.to_csv(os.path.join(OUT_DIR, 'perspective3_age_band_alignment.csv'))
print("\n=== Perspective 2: age-band alignment ===")
print(p2_merged.round(2).to_string())

neo = p2_merged.loc['Neonate']
print(f"\nHeadline: neonates carry {neo['burden_share_pct']:.1f}% of pediatric DALY burden but "
      f"only {neo['trial_share_pct']:.1f}% of (fractionally-allocated) trial representation "
      f"-- a {neo['burden_share_pct']/neo['trial_share_pct']:.1f}-fold gap.")

# =====================================================================================
# Supplementary: research-to-burden ratio broken out jointly by GBD Level-2 cause AND age band --
# not a numbered perspective in its own right, since it recombines Perspectives 1 and 2 rather
# than adding a new independent dimension.
#
# Denominator discipline: EVERY cell's trial-share and burden-share are expressed as a % of the
# ENTIRE joint grid (all 20 included causes x 5 age bands together, both summing to 100% over the
# whole grid) -- so cells are directly comparable to each other in both dimensions at once.
#
# Trial side: fractional age-band allocation, the same method used in Perspective 2.
# GBD_Level2_Cause is NOT fractionally split (each trial has exactly one cause).
# =====================================================================================
df3 = df_trials_raw.copy()
df3 = df3[(df3['GBD_Level2_Cause'] != 'Not applicable') & (~df3['GBD_Level2_Cause'].isin(EXCLUDED_CAUSES))
          & df3['GBD_Level2_Cause'].notna()]
df3['_bands'] = df3['Age_Band_WHO'].apply(band_set)
df3 = df3[df3['_bands'].apply(len) > 0]  # also need a usable age band to enter the joint grid

trial_weight = pd.DataFrame(0.0, index=cause_order, columns=BAND_ORDER)
for cause, bands in zip(df3['GBD_Level2_Cause'], df3['_bands']):
    w = 1.0 / len(bands)
    for b in bands:
        trial_weight.loc[cause, b] += w
n_total_trials = trial_weight.values.sum()
heatmap_trial_share = trial_weight / n_total_trials * 100
print(f"\nTrials in the joint (cause x age-band) grid: {n_total_trials:.0f} "
      f"(of {len(df3)} with both a usable cause and a usable age band)")

burden_ca = band_agg[(band_agg['location_name'] == 'Global') & (~band_agg['cause_name'].isin(EXCLUDED_CAUSES))]
burden_grid = burden_ca.pivot_table(index='cause_name', columns='age_band', values='dalys', aggfunc='sum')
burden_grid = burden_grid.reindex(index=cause_order, columns=BAND_ORDER)
heatmap_burden_share = burden_grid / burden_grid.values.sum() * 100

floor = 1e-4  # % -- small relative to any real cell, just keeps log2 finite for true 0-trial cells
with np.errstate(divide='ignore'):
    log2_ratio = np.log2(heatmap_trial_share.clip(lower=floor) / heatmap_burden_share.clip(lower=floor))

n_trials_grid = trial_weight.round(1)  # fractional but close to integer counts; keep 1dp for display
log2_ratio.to_csv(os.path.join(OUT_DIR, 'cause_age_heatmap_log2_ratio.csv'))
heatmap_trial_share.to_csv(os.path.join(OUT_DIR, 'cause_age_heatmap_trial_share.csv'))
heatmap_burden_share.to_csv(os.path.join(OUT_DIR, 'cause_age_heatmap_burden_share.csv'))
n_trials_grid.to_csv(os.path.join(OUT_DIR, 'cause_age_heatmap_n_trials.csv'))
print("\n=== log2(research-to-burden ratio), by cause x age band ===")
pd.set_option('display.width', 160)
print(log2_ratio.round(2).to_string())

# =====================================================================================
# Perspective 3: does research-to-burden alignment itself differ by country income level? LIC's
# absolute trial volume can remain far smaller while its PROPORTIONAL alignment is simultaneously
# better (or worse) -- this perspective is designed to tell those two things apart.
#
# Summary metric: the index of dissimilarity (ID) = 0.5 x sum(|trial_share_i - burden_share_i|)
# across causes i, a standard demographic-style summary (bounded 0-100): "the % of trials that
# would need to move to a different cause for that income group's research profile to exactly
# mirror its own burden profile." Lower ID = better aligned.
#
# Denominator discipline: within EACH income group separately, trial-share and burden-share are
# each renormalized to 100% over the 20 included GBD Level-2 causes (comparing each income
# group's own internal profile, not comparing income groups' raw volumes to each other).
# =====================================================================================
GROUPS = ['Low-income', 'Lower-middle-income', 'Upper-middle-income', 'High-income']
GLABEL = {'Low-income': 'LIC', 'Lower-middle-income': 'LMIC', 'Upper-middle-income': 'UMIC', 'High-income': 'HIC'}
GBD_LOCATION = {'Low-income': 'World Bank Low Income', 'Lower-middle-income': 'World Bank Lower Middle Income',
                'Upper-middle-income': 'World Bank Upper Middle Income', 'High-income': 'World Bank High Income'}

df4 = df_trials_raw.copy()
income = pd.read_csv(INCOME_FILE)[['PDF_name', 'income_group']]
df4 = df4.merge(income, on='PDF_name', how='left')

burden_avg = cause_agg[~cause_agg['cause_name'].isin(EXCLUDED_CAUSES)]
all_causes_p3 = sorted(burden_avg['cause_name'].unique())

id_results = []
per_cause_rows = []
for g in GROUPS:
    gsub = df4[(df4['income_group'] == g) & (~df4['GBD_Level2_Cause'].isin(['Not applicable'] + EXCLUDED_CAUSES))
               & df4['GBD_Level2_Cause'].notna()]
    n_g = len(gsub)
    trial_count_g = gsub['GBD_Level2_Cause'].value_counts().reindex(all_causes_p3, fill_value=0)
    trial_share_g = (trial_count_g / n_g * 100).reindex(all_causes_p3, fill_value=0.0)

    burden_g = burden_avg[burden_avg['location_name'] == GBD_LOCATION[g]].set_index('cause_name')['dalys']
    burden_share_g = (burden_g / burden_g.sum() * 100).reindex(all_causes_p3, fill_value=0.0)

    ID = 0.5 * np.abs(trial_share_g - burden_share_g).sum()
    id_results.append({'income_group': GLABEL[g], 'n_trials': n_g, 'index_of_dissimilarity': ID})

    for c in all_causes_p3:
        per_cause_rows.append({'income_group': GLABEL[g], 'cause': c, 'n_trials': int(trial_count_g[c]),
                                'trial_share_pct': trial_share_g[c], 'burden_share_pct': burden_share_g[c]})
    print(f"{GLABEL[g]}: n={n_g} trials, index of dissimilarity = {ID:.1f}")

id_df = pd.DataFrame(id_results).set_index('income_group').reindex(['LIC', 'LMIC', 'UMIC', 'HIC'])
per_cause_df = pd.DataFrame(per_cause_rows)
id_df.to_csv(os.path.join(OUT_DIR, 'perspective4_income_group_alignment_summary.csv'))
per_cause_df.to_csv(os.path.join(OUT_DIR, 'perspective4_income_group_alignment_by_cause.csv'), index=False)

print("\n=== Perspective 3: index of dissimilarity by income group (lower = better aligned) ===")
print(id_df.round(1).to_string())

# ---- overall alignment by income group (trial share vs burden share), all trials / all-cause
# burden (not just the 20 included causes) -- matches how Table 1's own income-group percentages
# are computed, and is a genuine "research volume vs burden" comparison independent of
# cause-classification quality ----
all_cause_by_loc_year = wide_df.groupby(['location_name', 'year'], as_index=False)['dalys'].sum()
all_cause_burden_avg = all_cause_by_loc_year.groupby('location_name', as_index=False)['dalys'].mean()

overall_trial_counts = df4[df4['income_group'].isin(GROUPS)]['income_group'].value_counts().reindex(GROUPS, fill_value=0)
overall_trial_counts.index = [GLABEL[g] for g in overall_trial_counts.index]
n_overall = overall_trial_counts.sum()
overall_trial_share = overall_trial_counts / n_overall * 100

overall_burden = pd.Series({GLABEL[g]: all_cause_burden_avg.loc[
    all_cause_burden_avg['location_name'] == GBD_LOCATION[g], 'dalys'].sum() for g in GROUPS})
overall_burden_share = overall_burden / overall_burden.sum() * 100

overall = pd.DataFrame({'trial_share_pct': overall_trial_share, 'burden_share_pct': overall_burden_share,
                         'n_trials': overall_trial_counts}).reindex(['LIC', 'LMIC', 'UMIC', 'HIC'])
overall.to_csv(os.path.join(OUT_DIR, 'income_group_overall_alignment.csv'))
print("\n=== Overall alignment by income group (all trials, all-cause pediatric burden) ===")
print(overall.round(2).to_string())

# ---- income group x cause log2-ratio grid (feeds Figure S8's heatmap) ----
group_order = ['LIC', 'LMIC', 'UMIC', 'HIC']
trial_pivot = per_cause_df.pivot(index='income_group', columns='cause', values='trial_share_pct').reindex(
    index=group_order, columns=cause_order)
burden_pivot = per_cause_df.pivot(index='income_group', columns='cause', values='burden_share_pct').reindex(
    index=group_order, columns=cause_order)

floor_ig = 0.02
with np.errstate(divide='ignore'):
    ig_log2_ratio = np.log2(trial_pivot.clip(lower=floor_ig) / burden_pivot.clip(lower=floor_ig))
ig_log2_ratio.to_csv(os.path.join(OUT_DIR, 'income_group_cause_heatmap_log2_ratio.csv'))
print("\nSaved income_group_cause_heatmap_log2_ratio.csv")
