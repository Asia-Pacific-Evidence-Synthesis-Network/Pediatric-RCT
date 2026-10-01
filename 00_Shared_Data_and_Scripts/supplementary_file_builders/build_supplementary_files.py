"""
Builds clean, standalone supplementary files for the paper from the classification
dictionaries currently embedded in the working analysis scripts:
  - DRUG_KEYWORDS / TOPIC_KEYWORDS (rebuild_all_consolidated_v2.py)
  - UNCOVERED_MAP (atc_level1_manual_map.py)
  - EMLC_ATC_MAP (emlc_atc_level1_map.py)

Each is written as both a .csv (human-readable, for the paper's supplementary materials)
and a .py (clean standalone source, for code reproducibility), into supplementary_files/.
"""
import re
import json
import csv
import sys
sys.path.insert(0, '/Users/leayu/Documents/trend_rct')

ANA = '/Users/leayu/Documents/trend_rct/analysis'
OUT = '/Users/leayu/Documents/trend_rct/supplementary_files'

ATC_LABELS = {
    'A': 'Alimentary tract and metabolism', 'B': 'Blood and blood-forming organs',
    'C': 'Cardiovascular system', 'D': 'Dermatologicals',
    'G': 'Genitourinary system and sex hormones',
    'H': 'Systemic hormonal preparations, excluding sex hormones and insulins',
    'J': 'Antiinfectives for systemic use', 'L': 'Antineoplastic and immunomodulating agents',
    'M': 'Musculoskeletal system', 'N': 'Nervous system',
    'P': 'Antiparasitic products, insecticides and repellents', 'R': 'Respiratory system',
    'S': 'Sensory organs', 'V': 'Various',
}

# =====================================================================================
# 1. Extract DRUG_KEYWORDS + the mixed-category split rules from rebuild_all_consolidated_v2.py
# =====================================================================================
rebuild_src = open(f'{ANA}/rebuild_all_consolidated_v2.py').read()
section = rebuild_src.split("DRUG_PATTERNS = {cat: [re.compile(p) for p in pats] for cat, pats in DRUG_KEYWORDS.items()}")[0]
section = section.split("PLACEBO_PAT = re.compile")[1]
section = "PLACEBO_PAT = re.compile" + section
ns = {'re': re}
exec(section, ns)
DRUG_KEYWORDS = ns['DRUG_KEYWORDS']

add_atc_src = open(f'{ANA}/add_atc_level1.py').read()
# extract from "CATEGORY_TO_LETTER = {" through the end of the keyword_letter() function
start = add_atc_src.index("CATEGORY_TO_LETTER = {")
end = add_atc_src.index("# flat keyword -> letter map")
block = add_atc_src[start:end]
ns2 = {}
exec(block, ns2)
CATEGORY_TO_LETTER = ns2['CATEGORY_TO_LETTER']
ANAESTHETICS_M03 = ns2['ANAESTHETICS_M03']
ENDOCRINE_A10 = ns2['ENDOCRINE_A10']
NEONATAL_R07 = ns2['NEONATAL_R07']
keyword_letter = ns2['keyword_letter']

def clean_pattern(p):
    """Strip regex word-boundary markers (\\b) -- implementation detail, not meaningful content."""
    return p.replace(r'\b', '').replace(r'\.', '.')

dictionary_rows = []
for cat, kws in DRUG_KEYWORDS.items():
    for kw in kws:
        letter = keyword_letter(cat, kw)
        dictionary_rows.append({
            'drug_keyword': clean_pattern(kw), 'ATC_first_level_code': letter,
            'ATC_first_level_group': ATC_LABELS[letter],
            'source_pharmacological_class': cat.split(' (ATC')[0],
            'classification_method': 'predefined_dictionary',
        })

# =====================================================================================
# 2. Long-tail individual drug classification (atc_level1_manual_map.py)
# =====================================================================================
from analysis.atc_level1_manual_map import UNCOVERED_MAP
longtail_rows = []
for name, letter in UNCOVERED_MAP.items():
    if letter is None:
        continue
    longtail_rows.append({
        'drug_keyword': name, 'ATC_first_level_code': letter,
        'ATC_first_level_group': ATC_LABELS[letter],
        'source_pharmacological_class': '',
        'classification_method': 'individual_llm_classification',
    })

all_drug_rows = dictionary_rows + longtail_rows
# de-duplicate exact case-insensitive repeats that agree on ATC group (harmless redundancy from
# manual classification passes); KEEP genuine disagreements (e.g. ephedrine: C in one dictionary
# class, N in another, reflecting its real dual pharmacological use as vasopressor vs. cardiac
# stimulant) so the supplementary file documents rather than silently resolves that ambiguity.
seen = set()
deduped = []
for r in all_drug_rows:
    key = (r['drug_keyword'].lower(), r['ATC_first_level_code'])
    if key in seen:
        continue
    seen.add(key)
    deduped.append(r)
all_drug_rows = deduped
all_drug_rows.sort(key=lambda r: (r['ATC_first_level_code'], r['drug_keyword'].lower()))

with open(f'{OUT}/Supplementary_File_S1_ATC_drug_classification.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['drug_keyword', 'ATC_first_level_code', 'ATC_first_level_group',
                                       'source_pharmacological_class', 'classification_method'])
    w.writeheader()
    w.writerows(all_drug_rows)
print(f"S1: {len(all_drug_rows)} drug-name/keyword classifications "
      f"({len(dictionary_rows)} dictionary + {len(longtail_rows)} individually classified)")

# =====================================================================================
# 3. EMLc medicine ATC classification, with matched/unmatched RCT-evidence status
# =====================================================================================
from analysis.emlc_atc_level1_map import EMLC_ATC_MAP
crossref = json.load(open(f'{ANA}/emlc_crossref.json'))
matched_names = set(m[0] for m in crossref['matched'])
matched_ncounts = {m[0]: m[2] for m in crossref['matched']}

emlc_rows = []
for name, letter in EMLC_ATC_MAP.items():
    is_matched = name in matched_names
    emlc_rows.append({
        'emlc_medicine_name': name, 'ATC_first_level_code': letter,
        'ATC_first_level_group': ATC_LABELS[letter],
        'has_supporting_pediatric_RCT': 'Yes' if is_matched else 'No',
        'n_supporting_trials': matched_ncounts.get(name, 0),
    })
emlc_rows.sort(key=lambda r: (r['ATC_first_level_code'], r['emlc_medicine_name']))

with open(f'{OUT}/Supplementary_File_S2_EMLc_ATC_classification.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['emlc_medicine_name', 'ATC_first_level_code', 'ATC_first_level_group',
                                       'has_supporting_pediatric_RCT', 'n_supporting_trials'])
    w.writeheader()
    w.writerows(emlc_rows)
print(f"S2: {len(emlc_rows)} EMLc medicines classified")

# =====================================================================================
# 4. Research topic keyword dictionary (TOPIC_KEYWORDS)
# =====================================================================================
section2 = rebuild_src.split("TOPIC_PATTERNS = {cat: [re.compile(p) for p in pats] for cat, pats in TOPIC_KEYWORDS.items()}")[0]
section2 = section2.split("TOPIC_KEYWORDS = {")[1]
section2 = "TOPIC_KEYWORDS = {" + section2
ns4 = {'re': re}
exec(section2, ns4)
TOPIC_KEYWORDS = ns4['TOPIC_KEYWORDS']

topic_rows = []
for cat, pats in TOPIC_KEYWORDS.items():
    for p in pats:
        topic_rows.append({'topic_category': cat, 'keyword_pattern': clean_pattern(p)})
topic_rows.sort(key=lambda r: (r['topic_category'], r['keyword_pattern']))

with open(f'{OUT}/Supplementary_File_S3_topic_keyword_dictionary.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['topic_category', 'keyword_pattern'])
    w.writeheader()
    w.writerows(topic_rows)
print(f"S3: {len(topic_rows)} topic keyword patterns across {len(TOPIC_KEYWORDS)} categories")

# =====================================================================================
# 5. Clean standalone .py sources (code reproducibility, alongside the .csv tables above)
# =====================================================================================
import shutil
shutil.copy(f'{ANA}/atc_level1_manual_map.py', f'{OUT}/Supplementary_File_S1b_ATC_individual_drug_classification_source.py')
shutil.copy(f'{ANA}/emlc_atc_level1_map.py', f'{OUT}/Supplementary_File_S2b_EMLc_ATC_classification_source.py')

with open(f'{OUT}/Supplementary_File_S1a_ATC_predefined_drug_dictionary_source.py', 'w') as f:
    f.write('"""\nPredefined keyword dictionary mapping commonly used drug names to WHO ATC first-level\n'
            'groups (Supplementary File S1, dictionary-classified rows). Extracted from\n'
            'analysis/rebuild_all_consolidated_v2.py (DRUG_KEYWORDS) and analysis/add_atc_level1.py\n'
            '(CATEGORY_TO_LETTER + the 3 mixed-category keyword-level splits).\n"""\n\n')
    f.write('DRUG_KEYWORDS = {\n')
    for cat, kws in DRUG_KEYWORDS.items():
        f.write(f'    {cat!r}: {kws!r},\n')
    f.write('}\n\n')
    f.write('CATEGORY_TO_LETTER = {\n')
    for cat, letter in CATEGORY_TO_LETTER.items():
        f.write(f'    {cat!r}: {letter!r},\n')
    f.write('}\n\n')
    f.write('# 3 categories above mix two ATC first-level groups; split at the individual-keyword level:\n')
    f.write(f'ANAESTHETICS_M03 = {ANAESTHETICS_M03!r}  # -> M (muscle relaxants); rest of category -> N\n')
    f.write(f'ENDOCRINE_A10 = {ENDOCRINE_A10!r}  # -> A (antidiabetics); rest of category -> H\n')
    f.write(f'NEONATAL_R07 = {NEONATAL_R07!r}  # -> R (surfactant); rest of category -> N\n')
print("S1a/S1b/S2b: standalone .py sources written")

with open(f'{OUT}/Supplementary_File_S3b_topic_keyword_dictionary_source.py', 'w') as f:
    f.write('"""\nKeyword dictionary mapping research-topic categories (anchored to ICD-10 disease\n'
            'chapters, plus 1 procedure-context category) to the disease/condition-text keyword\n'
            'patterns used to classify each trial. Extracted from\n'
            'analysis/rebuild_all_consolidated_v2.py (TOPIC_KEYWORDS).\n"""\n\n')
    f.write('TOPIC_KEYWORDS = {\n')
    for cat, pats in TOPIC_KEYWORDS.items():
        f.write(f'    {cat!r}: {pats!r},\n')
    f.write('}\n')
print("S3b: standalone .py source written")
