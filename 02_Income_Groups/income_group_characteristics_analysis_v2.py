"""
Analysis 6: how pediatric medication RCT characteristics differ by World Bank income group
(Low / Lower-middle / Upper-middle / High-income), among the 7,557 trials with an attributable
single country. Covers: temporal trend of trial share, therapeutic focus (ATC first-level and
research topic), age-band representation, research-transparency indicators, and trial size/power
to detect adverse-event signals.
"""
import pandas as pd
import numpy as np
import json

df = pd.read_excel('/Users/leayu/Documents/trend_rct/Trial bank_13269.xlsx', sheet_name='all')
income = pd.read_csv('/Users/leayu/Documents/trend_rct/results_v2_20260809/trial_country_income_v2.csv')[['PDF_name', 'income_group']]
df = df.merge(income, on='PDF_name', how='left')
N = len(df)
sub = df[df['income_group'].notna()].copy()
n_sub = len(sub)
print(f"N total = {N}, N with income group = {n_sub} ({100*n_sub/N:.1f}%)")

GROUPS = ['Low-income', 'Lower-middle-income', 'Upper-middle-income', 'High-income']
GLABEL = {'Low-income':'LIC', 'Lower-middle-income':'LMIC', 'Upper-middle-income':'UMIC', 'High-income':'HIC'}
print(sub['income_group'].value_counts().reindex(GROUPS))

# =====================================================================================
# 1. Temporal trend: income-group share of trials, by decade
# =====================================================================================
def decade_bin(y):
    if pd.isna(y):
        return np.nan
    y = int(y)
    if y < 1960:
        return 'Before 1960'
    if y >= 2010:
        return '2010-2023'  # trial bank search cutoff Feb 2023 means 2020-2023 alone is a partial,
                              # under-counted window (publication/indexing lag); merged with the
                              # complete 2010-2019 decade rather than shown as a misleading standalone bar
    lo = (y // 10) * 10
    return f"{lo}-{lo+9}"
sub['Decade'] = sub['Year'].apply(decade_bin)
decade_order = ['1960-1969','1970-1979','1980-1989','1990-1999','2000-2009','2010-2023']

decade_rows = []
for d in decade_order:
    dsub = sub[sub['Decade'] == d]
    n_d = len(dsub)
    row = {'Decade': d, 'n_trials': n_d}
    for g in GROUPS:
        row[GLABEL[g]] = round(100 * (dsub['income_group']==g).sum() / n_d, 1) if n_d else None
    decade_rows.append(row)
decade_df = pd.DataFrame(decade_rows)
print("\n=== Income-group share by decade ===")
print(decade_df.to_string(index=False))
decade_df.to_csv('/Users/leayu/Documents/trend_rct/results_v2_20260809/income_group_trend_by_decade_v2.csv', index=False)

# =====================================================================================
# 2. Therapeutic focus: ATC first-level group, by income group (non-exclusive)
# =====================================================================================
sub['_atc'] = sub['ATC_Level1'].apply(lambda v: [] if pd.isna(v) else v.split('+'))
atc_rows = []
for g in GROUPS:
    gsub = sub[sub['income_group']==g]
    n_g = len(gsub)
    n_atc_g = gsub['ATC_Level1'].notna().sum()
    row = {'income_group': GLABEL[g], 'n_trials': n_g}
    for L in "ABCDGHJLMNPRSV":
        n = gsub['_atc'].apply(lambda ls: L in ls).sum()
        row[L] = round(100*n/n_atc_g, 1) if n_atc_g else None
    atc_rows.append(row)
atc_df = pd.DataFrame(atc_rows)
print("\n=== ATC first-level group %, by income group ===")
print(atc_df.to_string(index=False))
atc_df.to_csv('/Users/leayu/Documents/trend_rct/results_v2_20260809/income_group_atc_distribution_v2.csv', index=False)

# =====================================================================================
# 3. Research topic, by income group (non-exclusive at Other level -- using real categories only)
# =====================================================================================
topic_valid = sub[sub['Topic_Category'].notna() & (sub['Topic_Category'] != 'Other/unclassified')]
topic_rows = []
for g in GROUPS:
    gsub = topic_valid[topic_valid['income_group']==g]
    n_g = len(gsub)
    vc = gsub['Topic_Category'].value_counts()
    top3 = vc.head(3)
    topic_rows.append({'income_group': GLABEL[g], 'n_trials_classified': n_g,
                        'top3_topics': '; '.join(f"{t} ({100*c/n_g:.1f}%)" for t,c in top3.items())})
topic_df = pd.DataFrame(topic_rows)
print("\n=== Top 3 topics by income group ===")
print(topic_df.to_string(index=False))

# full topic x income crosstab (for figure)
topic_full = pd.crosstab(topic_valid['Topic_Category'], topic_valid['income_group'], normalize='columns') * 100
topic_full = topic_full.reindex(columns=GROUPS)
topic_full.to_csv('/Users/leayu/Documents/trend_rct/results_v2_20260809/income_group_topic_crosstab_v2.csv')

# =====================================================================================
# 4. Age-band representation (non-exclusive), by income group
# =====================================================================================
BAND_ORDER = ['Neonate', 'Infant', 'Young child', 'Child', 'Adolescent']
sub['_bands'] = sub['Age_Band_WHO'].apply(lambda v: [] if pd.isna(v) else v.split('+'))
age_rows = []
for g in GROUPS:
    gsub = sub[sub['income_group']==g]
    n_g = len(gsub)
    row = {'income_group': GLABEL[g], 'n_trials': n_g}
    for b in BAND_ORDER:
        n = gsub['_bands'].apply(lambda bl: b in bl).sum()
        row[b] = round(100*n/n_g, 1) if n_g else None
    age_rows.append(row)
age_df = pd.DataFrame(age_rows)
print("\n=== Age-band %, by income group ===")
print(age_df.to_string(index=False))
age_df.to_csv('/Users/leayu/Documents/trend_rct/results_v2_20260809/income_group_age_band_v2.csv', index=False)

# =====================================================================================
# 5. Transparency indicators, by income group
# =====================================================================================
sub['is_registered'] = sub['Registry'] == 'Y'
sub['funding_reported'] = ~sub['Funding_type'].isin(['Not report']) & sub['Funding_type'].notna()
sub['data_sharing_stmt'] = sub['Data sharing statement'] == 'Y'
sub['ipd_available'] = sub['IPD available in Registry'] == 'Y'

trans_rows = []
for g in GROUPS:
    gsub = sub[sub['income_group']==g]
    n_g = len(gsub)
    reg_sub = gsub[gsub['is_registered']]
    trans_rows.append({
        'income_group': GLABEL[g], 'n_trials': n_g,
        'pct_registered': round(100*gsub['is_registered'].mean(),1),
        'pct_funding_reported': round(100*gsub['funding_reported'].mean(),1),
        'pct_data_sharing_stmt': round(100*gsub['data_sharing_stmt'].mean(),1),
        'n_registered': len(reg_sub),
        'pct_ipd_of_registered': round(100*reg_sub['ipd_available'].mean(),1) if len(reg_sub) else None,
    })
trans_df = pd.DataFrame(trans_rows)
print("\n=== Transparency indicators, by income group ===")
print(trans_df.to_string(index=False))
trans_df.to_csv('/Users/leayu/Documents/trend_rct/results_v2_20260809/income_group_transparency_v2.csv', index=False)

# =====================================================================================
# 6. Trial size and power to detect AE signals, by income group
# =====================================================================================
from scipy.stats import norm
Z_A2, Z_B = norm.ppf(1-0.05/2), norm.ppf(0.80)
CONST = 2*(Z_A2+Z_B)
sub['ss'] = pd.to_numeric(sub['Sample size'], errors='coerce')
sub['mde_5pct'] = CONST * np.sqrt(0.05*0.95/sub['ss']) * 100

power_rows = []
for g in GROUPS:
    gsub = sub[(sub['income_group']==g) & sub['ss'].notna()]
    power_rows.append({
        'income_group': GLABEL[g], 'n_trials': len(gsub),
        'median_n': gsub['ss'].median(), 'iqr_n_low': gsub['ss'].quantile(0.25), 'iqr_n_high': gsub['ss'].quantile(0.75),
        'median_mde_5pct': round(gsub['mde_5pct'].median(),1),
    })
power_df = pd.DataFrame(power_rows)
print("\n=== Trial size & power (5% baseline), by income group ===")
print(power_df.to_string(index=False))
power_df.to_csv('/Users/leayu/Documents/trend_rct/results_v2_20260809/income_group_power_v2.csv', index=False)

print("\nAll income-group-characteristics CSVs saved to analysis/")
