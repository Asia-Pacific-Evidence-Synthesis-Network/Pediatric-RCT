"""
Rebuild of Analysis 2 (drug/ATC landscape + EMLc evidence-gap comparison) against the updated
Trial Bank. Reuses: ATC_Level1 column (already built into the sheet), the static EMLc-medicine ATC
map (emlc_atc_level1_map.py, independent reference data unaffected by trial-bank edits), and the
existing matched/unmatched EMLc crossref (emlc_crossref.json) -- re-validated against the CURRENT
Normalized_Drugs trial counts (a medicine is re-marked unmatched if its only supporting trial(s)
were among the rows removed since the crossref was built; no medicine can gain a new match from
pure row removal).
"""
import pandas as pd
import numpy as np
import json
import sys
sys.path.insert(0, '/Users/leayu/Documents/trend_rct')
from analysis.emlc_atc_level1_map import EMLC_ATC_MAP

SRC = '/Users/leayu/Documents/trend_rct/Trial bank_13269.xlsx'
OUT = '/Users/leayu/Documents/trend_rct/results_v2_20260809'
df = pd.read_excel(SRC, sheet_name='all')
N = len(df)

ATC_LETTERS = list("ABCDGHJLMNPRSV")
ATC_NAMES = {
    'A':'Alimentary tract & metabolism','B':'Blood & blood-forming organs','C':'Cardiovascular system',
    'D':'Dermatologicals','G':'Genitourinary system & sex hormones',
    'H':'Systemic hormonal preparations (excl. sex hormones/insulins)','J':'Antiinfectives for systemic use',
    'L':'Antineoplastic & immunomodulating agents','M':'Musculoskeletal system','N':'Nervous system',
    'P':'Antiparasitic products, insecticides & repellents','R':'Respiratory system','S':'Sensory organs',
    'V':'Various',
}

# ---- overall counts (non-mutually-exclusive) ----
atc_counts = {l: 0 for l in ATC_LETTERS}
for v in df['ATC_Level1'].dropna():
    for l in v.split('+'):
        if l in atc_counts:
            atc_counts[l] += 1
no_drug = int(df['ATC_Level1'].isna().sum())
n_classified = N - no_drug
total_touches = sum(atc_counts.values())
print(f"N={N}, classified={n_classified} ({n_classified/N*100:.1f}%), no drug={no_drug} ({no_drug/N*100:.1f}%)")
print(f"Total group-touches: {total_touches}")
for l in sorted(atc_counts, key=lambda x: -atc_counts[x]):
    print(f"  {l} {ATC_NAMES[l]}: {atc_counts[l]} ({atc_counts[l]/n_classified*100:.1f}% of classified)")

# ---- Gini coefficient across the 14 groups ----
vals = sorted(atc_counts.values())
n = len(vals)
cum = np.cumsum(vals)
total = cum[-1]
lorenz_y = [0.0] + [c/total for c in cum]
lorenz_x = [i/n for i in range(n+1)]
gini = 1 - 2*np.trapz(lorenz_y, lorenz_x)
print(f"\nGini = {gini:.4f}")
sorted_letters = sorted(atc_counts, key=lambda x: atc_counts[x])
print("Sorted ascending:", [(l, atc_counts[l]) for l in sorted_letters])
top1_share = max(atc_counts.values())/total_touches*100
bottom3 = sum(sorted(atc_counts.values())[:3])/total_touches*100
print(f"Largest group share of touches: {top1_share:.1f}%; 3 smallest groups share: {bottom3:.1f}%")

with open(f'{OUT}/atc_level1_gini_v2.json', 'w') as f:
    json.dump({'gini': float(gini), 'counts': atc_counts, 'total_touches': int(total_touches),
               'lorenz': [{'x': x, 'y': y} for x, y in zip(lorenz_x, lorenz_y)]}, f, indent=2)

with open(f'{OUT}/atc_level1_table1_v2.json', 'w') as f:
    json.dump({'N': N, 'n_classified': n_classified, 'no_drug': no_drug,
               'counts': atc_counts,
               'pct_of_classified': {l: round(atc_counts[l]/n_classified*100,1) for l in ATC_LETTERS},
               'pct_of_N': {l: round(atc_counts[l]/N*100,1) for l in ATC_LETTERS}}, f, indent=2)

# ---- EMLc coverage, re-validated against current Normalized_Drugs ----
from collections import Counter
drug_counts = Counter()
for v in df['Normalized_Drugs'].dropna():
    for d in set(x.strip().lower() for x in v.split('+')):
        drug_counts[d] += 1

crossref = json.load(open('/Users/leayu/Documents/trend_rct/analysis/emlc_crossref.json'))
matched_v2 = []
unmatched_v2 = list(crossref['unmatched'])
for emlc_name, drug_name, old_n in crossref['matched']:
    new_n = drug_counts.get(drug_name.lower(), 0)
    if new_n == 0:
        unmatched_v2.append(emlc_name)
    else:
        matched_v2.append([emlc_name, drug_name, new_n])

print(f"\nEMLc coverage (re-validated): matched={len(matched_v2)}, unmatched={len(unmatched_v2)}, "
      f"total={len(matched_v2)+len(unmatched_v2)}")
print(f"Overall coverage: {len(matched_v2)}/{len(matched_v2)+len(unmatched_v2)} "
      f"({len(matched_v2)/(len(matched_v2)+len(unmatched_v2))*100:.1f}%)")

matched_names = set(m[0] for m in matched_v2)
group_cov = {}
for l in ATC_LETTERS:
    names_in_group = [name for name, letter in EMLC_ATC_MAP.items() if letter == l]
    n_total_g = len(names_in_group)
    n_matched_g = sum(1 for name in names_in_group if name in matched_names)
    group_cov[l] = {'n_total': n_total_g, 'n_matched': n_matched_g,
                     'pct': round(n_matched_g/n_total_g*100,1) if n_total_g else None}
print("\n=== EMLc coverage by ATC group ===")
for l in ATC_LETTERS:
    g = group_cov[l]
    print(f"  {l} {ATC_NAMES[l]}: {g['n_matched']}/{g['n_total']} ({g['pct']}%)")

with open(f'{OUT}/emlc_atc_level1_coverage_v2.json', 'w') as f:
    json.dump({'matched': matched_v2, 'unmatched': unmatched_v2, 'group_coverage': group_cov,
               'overall_matched': len(matched_v2), 'overall_total': len(matched_v2)+len(unmatched_v2)},
              f, indent=2)

# ---- Temporal trend, top 8 ATC groups by decade ----
def decade_bin(y):
    if pd.isna(y):
        return np.nan
    y = int(y)
    if y < 1960:
        return 'Before 1960'
    lo = (y // 10) * 10
    if lo >= 2020:
        return '2020-2023'
    return f"{lo}-{lo+9}"
df['_decade'] = df['Year'].apply(decade_bin)
decade_order = ['1960-1969','1970-1979','1980-1989','1990-1999','2000-2009','2010-2019','2020-2023']
top8 = sorted(atc_counts, key=lambda x: -atc_counts[x])[:8]

trend_rows = []
for d in decade_order:
    dsub = df[df['_decade'] == d]
    n_d = len(dsub)
    row = {'Decade': d, 'n_trials': n_d}
    for l in top8:
        n_l = dsub['ATC_Level1'].dropna().apply(lambda v: l in v.split('+')).sum()
        row[l] = round(n_l/n_d*100, 1) if n_d else None
    trend_rows.append(row)
trend_df = pd.DataFrame(trend_rows)
print("\n=== Top 8 ATC groups by decade (%) ===")
print(trend_df.to_string(index=False))
trend_df.to_csv(f'{OUT}/atc_level1_trend_by_decade_v2.csv', index=False)

print("\nSaved atc_level1_gini_v2.json, atc_level1_table1_v2.json, emlc_atc_level1_coverage_v2.json, "
      "atc_level1_trend_by_decade_v2.csv")
