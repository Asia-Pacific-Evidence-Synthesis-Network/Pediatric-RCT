"""
Burden-of-disease analysis, supplementary: formal statistical test of the association between
trial volume and disease burden, modeled on the method used in a published pediatric-trials/GBD
study (Spearman's rho between trial counts and burden, globally and by income group; a generalized
gamma regression with a log link on log-transformed burden to estimate "expected" trial counts).

This complements the descriptive ratio-based Perspectives 1-3 above with an inferential answer to
a related but different question: those perspectives ask "is research volume PROPORTIONAL to
burden, cause by cause" (a ratio against an implicit 1:1 target); this analysis asks "is there a
statistically detectable MONOTONIC association between the two at all, and how much of the
cause-to-cause variation in trial counts does burden explain." A cause can score badly on the
ratio metric (way off proportional) while the two variables are still strongly correlated overall
(more-burdensome causes still reliably attract more trials, just not 1:1) -- these are genuinely
different questions, which is why both are reported rather than one replacing the other.

Uses the same trial-level GBD_Level2_Cause classification and the same 20 included causes
(excluding Transport injuries / Self-harm and interpersonal violence -- see Perspective 1) as the
rest of this analysis, RAW counts/DALYs rather than percentage shares (Spearman's rho is rank-based
so this makes no difference to it, but the regression is not scale-invariant and "expected number
of trials" is only a meaningful quantity in raw-count terms).
"""
import pandas as pd
import numpy as np
from scipy.stats import spearmanr
import statsmodels.api as sm
import os

TRIAL_BANK = '/Users/leayu/Documents/trend_rct/Trial bank_13269.xlsx'
INCOME_FILE = '/Users/leayu/Documents/trend_rct/results_v2_20260809/trial_country_income_v2.csv'
OUT_DIR = '/Users/leayu/Documents/trend_rct/burden_of_disease_results'
EXCLUDED_CAUSES = ['Transport injuries', 'Self-harm and interpersonal violence']

GROUPS = ['Low-income', 'Lower-middle-income', 'Upper-middle-income', 'High-income']
GLABEL = {'Low-income': 'LIC', 'Lower-middle-income': 'LMIC', 'Upper-middle-income': 'UMIC', 'High-income': 'HIC'}
GBD_LOCATION = {'Low-income': 'World Bank Low Income', 'Lower-middle-income': 'World Bank Lower Middle Income',
                'Upper-middle-income': 'World Bank Upper Middle Income', 'High-income': 'World Bank High Income'}

df = pd.read_excel(TRIAL_BANK, sheet_name='all')
df = df[(df['GBD_Level2_Cause'] != 'Not applicable') & (~df['GBD_Level2_Cause'].isin(EXCLUDED_CAUSES))
        & df['GBD_Level2_Cause'].notna()]

burden = pd.read_csv(os.path.join(OUT_DIR, 'gbd_burden_by_cause.csv'))
burden_avg = burden[~burden['cause_name'].isin(EXCLUDED_CAUSES)]

# ==== 1. Global-level Spearman's rho: trial count vs DALY burden, across the 20 causes ====
trial_counts_global = df['GBD_Level2_Cause'].value_counts()
burden_global = burden_avg[burden_avg['location_name'] == 'Global'].set_index('cause_name')['dalys']
cause_order = sorted(burden_global.index)
trial_counts_global = trial_counts_global.reindex(cause_order, fill_value=0)
burden_global = burden_global.reindex(cause_order)

rho_global, p_global = spearmanr(trial_counts_global, burden_global)
print(f"=== Global Spearman correlation: trial count vs. DALY burden, across {len(cause_order)} causes ===")
print(f"rho = {rho_global:.3f}, p = {p_global:.4f}, n = {len(cause_order)} causes")

# ==== 2. Spearman's rho within each income group ====
income = pd.read_csv(INCOME_FILE)[['PDF_name', 'income_group']]
df_inc = df.merge(income, on='PDF_name', how='left')

rho_results = [{'group': 'Global', 'rho': rho_global, 'p_value': p_global, 'n_causes': len(cause_order)}]
for g in GROUPS:
    gsub = df_inc[df_inc['income_group'] == g]
    tc = gsub['GBD_Level2_Cause'].value_counts().reindex(cause_order, fill_value=0)
    bd = burden_avg[burden_avg['location_name'] == GBD_LOCATION[g]].set_index('cause_name')['dalys'].reindex(cause_order)
    rho, p = spearmanr(tc, bd)
    rho_results.append({'group': GLABEL[g], 'rho': rho, 'p_value': p, 'n_causes': len(cause_order)})
    print(f"{GLABEL[g]}: rho = {rho:.3f}, p = {p:.4f}")

rho_df = pd.DataFrame(rho_results).set_index('group').reindex(['Global', 'LIC', 'LMIC', 'UMIC', 'HIC'])
rho_df.to_csv(os.path.join(OUT_DIR, 'correlation_spearman_by_group.csv'))
print("\n" + rho_df.round(4).to_string())

# ==== 3. LIC-specific sub-analysis: infectious/parasitic causes only (mirrors the reference
# paper's separate analysis of the 16 infectious causes for low-income countries, where infectious
# disease dominates total burden) ====
INFECTIOUS_CAUSES = ['Enteric infections', 'HIV/AIDS and sexually transmitted infections',
                      'Neglected tropical diseases and malaria', 'Other infectious diseases',
                      'Respiratory infections and tuberculosis']
lic = df_inc[df_inc['income_group'] == 'Low-income']
tc_lic_inf = lic['GBD_Level2_Cause'].value_counts().reindex(INFECTIOUS_CAUSES, fill_value=0)
bd_lic_inf = burden_avg[burden_avg['location_name'] == GBD_LOCATION['Low-income']].set_index(
    'cause_name')['dalys'].reindex(INFECTIOUS_CAUSES)
rho_lic_inf, p_lic_inf = spearmanr(tc_lic_inf, bd_lic_inf)
print(f"\nLIC, infectious/parasitic causes only (n={len(INFECTIOUS_CAUSES)}): "
      f"rho = {rho_lic_inf:.3f}, p = {p_lic_inf:.4f}")

# ==== 4. Generalized gamma regression (log link) of trial count on log(burden), global level ====
X = sm.add_constant(np.log(burden_global.values))
model = sm.GLM(trial_counts_global.values, X, family=sm.families.Gamma(link=sm.families.links.Log()))
result = model.fit()
print("\n=== Generalized gamma regression (log link): trial count ~ log(DALY burden), global ===")
print(result.summary())

expected = result.predict(X)
reg_df = pd.DataFrame({
    'cause': cause_order,
    'observed_trials': trial_counts_global.values,
    'burden_dalys': burden_global.values,
    'expected_trials': expected,
}, index=cause_order)
reg_df['observed_to_expected_ratio'] = reg_df['observed_trials'] / reg_df['expected_trials']
reg_df = reg_df.sort_values('observed_to_expected_ratio', ascending=False)
reg_df.to_csv(os.path.join(OUT_DIR, 'correlation_gamma_regression_fit.csv'), index=False)
print("\n=== Observed vs. expected trial counts (from the fitted regression), ranked ===")
pd.set_option('display.width', 140)
print(reg_df.round(2).to_string(index=False))
