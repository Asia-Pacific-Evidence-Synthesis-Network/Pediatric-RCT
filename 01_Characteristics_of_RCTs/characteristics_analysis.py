"""
"Characteristics of pediatric medication RCTs" -- Table 1 and Figure S2 data.

Consolidated from three previously separate files (table1_characteristics_analysis.py,
country_map_analysis.py, country_cleaning.py), which had split one section's analysis across
multiple scripts, including two near-duplicate copies of the same country-name-cleaning logic
that had quietly drifted apart (only one recognized "türkiye" as an alias for Turkey). All
analysis for this section now lives in this single file; country_map_plots.py (Figure S2) and
any future plotting script for this section read this file's CSV/JSON outputs.
"""
import pandas as pd
import numpy as np
import json
import re

SRC = '/Users/leayu/Documents/trend_rct/Trial bank_13269.xlsx'
OUT = '/Users/leayu/Documents/trend_rct/results_v2_20260809'
df = pd.read_excel(SRC, sheet_name='all')
N = len(df)
print(f"N = {N}")

def pct(n, denom=N):
    return n, round(n/denom*100, 1)

results = {'N': N}

# ---- Publication year (decade bins) ----
# Decade column bins strictly by calendar decade (e.g. "2020-2029"); displayed as "2020-2023" since
# the search/data-collection cutoff (mid-2023) makes the most recent bin a partial decade.
decade_order = ['Before 1960','1960-1969','1970-1979','1980-1989','1990-1999',
                 '2000-2009','2010-2019','2020-2029']
decade_display = {'2020-2029': '2020-2023'}
decade_counts = df['Decade'].value_counts()
results['decade'] = {decade_display.get(d, d): pct(int(decade_counts.get(d,0))) for d in decade_order}
since_2000 = df['Decade'].isin(['2000-2009','2010-2019','2020-2029']).sum()
results['since_2000'] = pct(int(since_2000))

# ---- Geographic region (WHO_Region, non-mutually-exclusive multi-label) ----
region_labels = ['African','Americas','South-East Asia','European','Eastern Mediterranean','Western Pacific']
region_counts = {r: 0 for r in region_labels}
multi_regional = 0
not_classifiable = 0
no_country = df['WHO_Region'].isna().sum()
for v in df['WHO_Region'].dropna():
    if v == 'Multi-regional':
        multi_regional += 1
    elif v == 'Not classifiable':
        not_classifiable += 1
    else:
        for r in v.split('+'):
            if r in region_counts:
                region_counts[r] += 1
results['region'] = {r: pct(c) for r, c in region_counts.items()}
results['region']['Multi-regional'] = pct(multi_regional)
results['region']['Not classifiable'] = pct(not_classifiable)
results['region']['No country reported'] = pct(int(no_country))

# ---- Study design ----
design_map = df['Study Design'].value_counts(dropna=False)
results['design'] = {str(k): pct(int(v)) for k, v in design_map.items()}

# ---- Centre (normalize case) ----
center_norm = df['Center'].astype(str).str.strip().str.lower().replace({'nan': np.nan})
center_norm = center_norm.map({'single':'Single','multi':'Multi'})
center_counts = center_norm.value_counts(dropna=False)
results['center'] = {
    'Single-centre': pct(int(center_counts.get('Single', 0))),
    'Multi-centre': pct(int(center_counts.get('Multi', 0))),
    'Not reported': pct(int(center_norm.isna().sum())),
}

# ---- Funding source ----
FUND_MAP = {
    'Non-profit': 'Non-profit/academic',
    'Industry/Industry-employmer': 'Industry',
    'Industry + Non-profit': 'Industry + non-profit',
    'No funding': 'No funding',
    'Not report': 'Not reported',
}
fund_clean = df['Funding_type'].map(FUND_MAP)
fund_counts = fund_clean.value_counts(dropna=False)
results['funding'] = {v: pct(int(fund_counts.get(v, 0))) for v in
                       ['Non-profit/academic','Industry','Industry + non-profit','No funding','Not reported']}
results['funding_unavailable'] = pct(int(df['Funding_type'].isna().sum() + (df['Funding_type']=='Not report').sum()))
funded_known = df[~df['Funding_type'].isin(['Not report']) & df['Funding_type'].notna()]
results['funding_among_reported'] = {
    'Non-profit/academic': pct(int((funded_known['Funding_type']=='Non-profit').sum()), len(funded_known)),
    'Industry': pct(int((funded_known['Funding_type']=='Industry/Industry-employmer').sum()), len(funded_known)),
    'Industry + non-profit': pct(int((funded_known['Funding_type']=='Industry + Non-profit').sum()), len(funded_known)),
}

# ---- Trial registration ----
is_registered = df['Registry'] == 'Y'
results['registered'] = pct(int(is_registered.sum()))
results['not_registered'] = pct(int((~is_registered).sum()))
reg = df[is_registered]
n_reg = len(reg)
reg_status_map = {'Pro':'Prospective','Retro':'Retrospective','Pro_Retro':'Mixed','Retro_Pro':'Mixed',
                   'Missing data':'Missing/unclear'}
reg_status_clean = reg['Reg_status'].map(reg_status_map)
reg_status_clean = reg_status_clean.fillna('Missing/unclear')
rs_counts = reg_status_clean.value_counts()
results['reg_status'] = {k: pct(int(rs_counts.get(k,0)), n_reg) for k in
                          ['Prospective','Retrospective','Mixed','Missing/unclear']}
results['n_registered'] = n_reg

# ---- Data sharing statement (publication-level) ----
ds = df['Data sharing statement']
results['data_sharing_available'] = pct(int((ds == 'Y').sum()))

# ---- Research topic ----
topic_counts = df['Topic_Category'].value_counts(dropna=False)
results['topic'] = {(str(k) if pd.notna(k) else 'Not classifiable (no usable disease text)'): pct(int(v))
                     for k, v in topic_counts.items()}

# ---- Age group (WHO band, non-mutually-exclusive) ----
age_labels = ['Neonate','Infant','Young child','Child','Adolescent']
age_counts = {a: 0 for a in age_labels}
age_not_classifiable = df['Age_Band_WHO'].isna().sum()
for v in df['Age_Band_WHO'].dropna():
    for a in v.split('+'):
        if a in age_counts:
            age_counts[a] += 1
results['age_band'] = {a: pct(c) for a, c in age_counts.items()}
results['age_band']['Not classifiable'] = pct(int(age_not_classifiable))

# ---- Drug classes (ATC Level 1, non-mutually-exclusive) ----
ATC_LETTERS = list("ABCDGHJLMNPRSV")
ATC_NAMES = {
    'A':'Alimentary tract & metabolism','B':'Blood & blood-forming organs','C':'Cardiovascular system',
    'D':'Dermatologicals','G':'Genitourinary system & sex hormones',
    'H':'Systemic hormonal preparations (excl. sex hormones/insulins)','J':'Antiinfectives for systemic use',
    'L':'Antineoplastic & immunomodulating agents','M':'Musculoskeletal system','N':'Nervous system',
    'P':'Antiparasitic products, insecticides & repellents','R':'Respiratory system','S':'Sensory organs',
    'V':'Various',
}
atc_counts = {l: 0 for l in ATC_LETTERS}
no_drug = df['ATC_Level1'].isna().sum()
for v in df['ATC_Level1'].dropna():
    for l in v.split('+'):
        if l in atc_counts:
            atc_counts[l] += 1
results['atc'] = {f"{l} — {ATC_NAMES[l]}": pct(c) for l, c in atc_counts.items()}
results['atc_no_drug'] = pct(int(no_drug))
results['atc_classified'] = pct(N - int(no_drug))

# ---- Sample size (mean, SD, median, IQR) ----
ss = df['Sample size'].dropna()
results['sample_size'] = {
    'n_with_data': len(ss),
    'mean': round(ss.mean(), 1),
    'sd': round(ss.std(), 1),
    'median': round(ss.median(), 1),
    'q1': round(ss.quantile(0.25), 1),
    'q3': round(ss.quantile(0.75), 1),
    'min': int(ss.min()),
    'max': int(ss.max()),
}

# ---- Country-level (single-country trials), Table 1's own stat ----
# Base: all N=13,269 trials with an identifiable single country, regardless of whether that
# country maps to a World Bank income group (a different, larger denominator than Figure S2
# below, intentionally -- Table 1 reports the full trial bank's country spread).
MULTI_SEP_RE = re.compile(r'[,;、，]|\band\b|\bversus\b', re.IGNORECASE)
COUNTRY_ALIASES = {
    'usa':'United States','u.s.':'United States','u.s.a':'United States','u.s.a.':'United States',
    'united states':'United States','united stated':'United States','united sates':'United States',
    'america':'United States','american':'United States',
    'uk':'United Kingdom','u.k.':'United Kingdom','united kingdom':'United Kingdom',
    'england':'United Kingdom','scotland':'United Kingdom','northern ireland':'United Kingdom',
    'great britain':'United Kingdom','britain':'United Kingdom',
    'korea':'South Korea','south korea':'South Korea','korean':'South Korea',
    "democratic people's republic of korea":'North Korea','north korea':'North Korea',
    'ehypt':'Egypt','egypt':'Egypt',
    'mexio':'Mexico','méxico':'Mexico','mexico':'Mexico',
    'janpan':'Japan','japan.':'Japan','japan':'Japan',
    'germnay':'Germany','germany':'Germany',
    'netherland':'Netherlands','netherlands':'Netherlands','the netherlands':'Netherlands',
    'brasil':'Brazil','brazil':'Brazil',
    'belgique':'Belgium','belgium':'Belgium',
    'swissland':'Switzerland','switzerland':'Switzerland',
    'danmark':'Denmark','denmark':'Denmark',
    "côte d'ivoire":"Côte d'Ivoire",'côte d’ivoire':"Côte d'Ivoire",'ivory coast':"Côte d'Ivoire",
    'new zealand':'New Zealand','new zeland':'New Zealand',
    'gabonese\xa0republic':'Gabon','gabon':'Gabon',
    'republic of macedonia':'North Macedonia','north macedonia':'North Macedonia',
    'south african':'South Africa','south africa':'South Africa',
    'democratic republic of congo':'DR Congo','dr congo':'DR Congo','congo':'Congo',
    'the gambia':'Gambia','gambia':'Gambia',
    'lao':'Laos','laos':'Laos',
    'malaysian\xa0':'Malaysia','malaysia':'Malaysia',
    'swedish':'Sweden','sweden\xa0':'Sweden','sweden':'Sweden',
    'u.s.a':'United States',
    'guatemalan':'Guatemala','guatemala':'Guatemala',
    'thailand':'Thailand','malaysian':'Malaysia','turkey':'Turkey','türkiye':'Turkey','turkiye':'Turkey',
    'india':'India','china':'China','iran':'Iran',
}
EXCLUDE_TERMS = {
    'not report','not reported','international','multinational','global','europe','asia',
    'north america','north american','european','american','nordic countries','mid-european',
    'north european','west indies','yugoslavia','thai-burmese border','thai-cambodian border',
    'rhodesia','n/a','ni','united states canada','usa canada','us.chile','hajar',
    'congo uganda','gabon malawi','burkina faso ghana mali nigeria',
    'europe (eortc children leukemia group)','north europe','latin america','multi-center',
    'multi-centre',
}
def clean_country(raw):
    if pd.isna(raw):
        return np.nan
    s = str(raw).strip()
    s = re.sub(r'\(.*?\)', '', s).strip()
    s = s.strip('.').strip()
    s = re.sub(r'\s+', ' ', s)
    if not s:
        return np.nan
    if MULTI_SEP_RE.search(s):
        return np.nan
    key = s.lower().strip()
    if key in EXCLUDE_TERMS:
        return np.nan
    if key in COUNTRY_ALIASES:
        return COUNTRY_ALIASES[key]
    return s.title()

df['country_clean'] = df['Region_country'].apply(clean_country)
country_counts = df['country_clean'].value_counts()
n_countries = len(country_counts)
n_single_country_trials = int(country_counts.sum())
results['country'] = {
    'n_countries': n_countries,
    'n_single_country_trials': n_single_country_trials,
    'pct_single_country_trials': round(n_single_country_trials/N*100, 1),
    'top3': country_counts.head(3).to_dict(),
    'n_101_500': int(((country_counts > 100) & (country_counts <= 500)).sum()),
    'n_1_10': int((country_counts <= 10).sum()),
    'pct_1_10': round(((country_counts <= 10).sum()) / n_countries * 100, 1),
}
country_counts.to_csv(f'{OUT}/country_trial_counts_v2.csv', header=['n_trials'])

with open(f'{OUT}/table1_characteristics_v2.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)

print(json.dumps(results, indent=2, default=str))

# ---- Figure S2 data: per-country trial counts, restricted to trials with both an identifiable
# single country AND a mappable World Bank income group (the same 7,454-trial denominator used
# for the income-group-by-decade analysis, Figure 1A) ----
# Reuses trial_country_income_v2.csv's own pre-computed country_clean column (built with this
# same cleaning logic) rather than recomputing from Region_country here, so this count is
# guaranteed consistent with the income-group analysis that shares that denominator.
income = pd.read_csv('/Users/leayu/Documents/trend_rct/results_v2_20260809/trial_country_income_v2.csv')
income = income[income['income_group'].notna()]
counts = income['country_clean'].value_counts()
print(f"\nFigure S2: distinct clean countries: {len(counts)}")
print(f"Trials with an attributable single country and income group: {counts.sum()} / {N} ({counts.sum()/N*100:.1f}%)")
print(counts.head(20))
counts.to_csv('/Users/leayu/Documents/trend_rct/analysis/country_trial_counts.csv', header=['n_trials'])
