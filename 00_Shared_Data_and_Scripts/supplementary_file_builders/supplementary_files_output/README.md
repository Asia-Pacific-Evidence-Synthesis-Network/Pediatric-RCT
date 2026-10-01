# Supplementary classification files

These files document the classification methodology described in the paper's Data Analysis
section — specifically, how intervention drug names were assigned to WHO ATC first-level
anatomical groups, how EMLc medicines were classified for the evidence-coverage comparison, and
how research topics were classified to ICD-10-anchored categories. Each classification task used
a two-tier approach: a **predefined keyword dictionary** for common/well-established terms, and
**individual classification** (performed with LLM assistance and reviewed for accuracy) for
terms not captured by the dictionary. Every file below has a `.csv` (the classification table
itself) and, where applicable, a `.py` (clean standalone source code for reproducibility).

| File | Contents | Rows |
|---|---|---|
| `Supplementary_File_S1_ATC_drug_classification.csv` | Every drug name/keyword classified to its WHO ATC first-level group (A–V), with the method used (`predefined_dictionary` or `individual_llm_classification`) and, for dictionary entries, the source pharmacological class | 1,669 |
| `Supplementary_File_S1a_ATC_predefined_drug_dictionary_source.py` | The predefined dictionary itself (`DRUG_KEYWORDS`, 24 pharmacological classes) plus the category→ATC-letter mapping and the 3 keyword-level splits for classes that mix two ATC groups (anaesthetics/muscle relaxants, endocrine/antidiabetics, neonatal surfactant/caffeine) | — |
| `Supplementary_File_S1b_ATC_individual_drug_classification_source.py` | The individual classification lookup (`UNCOVERED_MAP`) for drug names not captured by the predefined dictionary | 1,092 names |
| `Supplementary_File_S2_EMLc_ATC_classification.csv` | Every WHO EMLc (9th edition, 2023) medicine classified to its ATC first-level group, with matched/unmatched pediatric-RCT evidence status and supporting-trial count | 359 |
| `Supplementary_File_S2b_EMLc_ATC_classification_source.py` | The EMLc classification lookup (`EMLC_ATC_MAP`) | 359 |
| `Supplementary_File_S3_topic_keyword_dictionary.csv` | Every keyword pattern used to classify trials into the 15 research-topic categories (14 ICD-10-chapter-anchored + 1 procedure-context category) | 232 |
| `Supplementary_File_S3b_topic_keyword_dictionary_source.py` | The topic keyword dictionary itself (`TOPIC_KEYWORDS`) | — |
| `Supplementary_File_S4_topic_classification_validation.xlsx` | Manual accuracy validation of the topic classification: 150 trials (10 per category, stratified random sample), each independently re-classified by blind review of the disease/condition text (i.e. without seeing the originally assigned category first), compared against the original assignment, with a reviewer note on every disagreement or borderline case | 150 |

## Notes on interpreting the drug classification table (S1)

- `classification_method = predefined_dictionary` rows were matched by keyword/substring search
  against each trial's canonical drug name; `individual_llm_classification` rows were assigned
  one-by-one using pharmacological reasoning for drug names the dictionary did not cover
  (predominantly uncommon, herbal, or investigational agents).
- Regex word-boundary markers used in the underlying matching code have been stripped from the
  `drug_keyword` / `keyword_pattern` columns for readability; a small number of dictionary entries
  are intentional partial-word stems (e.g. `allerg` matches allergy/allergic/allergen) rather than
  complete words.
- One documented ambiguity: **ephedrine** appears twice in the predefined dictionary, classified
  as both **C** (Cardiovascular system) and **N** (Nervous system) — reflecting its genuine dual
  pharmacological use as a vasopressor in anaesthesia and as a cardiac/decongestant stimulant. Both
  entries are retained rather than arbitrarily resolved to one.
- Coverage achieved: the drug classification (S1) reached 95.0% of trials (12,786/13,465); the
  topic classification (S3) reached 83.5% of trials (11,240/13,465), with the remainder falling
  into the "Other/unclassifiable" residual category, consistent with the figures reported in the
  paper.

## Notes on the topic classification validation (S4)

- Agreement was 136/150 (90.7%) on a strict standard (any case a reviewer would call differently
  counts as a disagreement) and 144/150 (96.0%) on a lenient standard (genuinely dual-topic
  diseases, where the assigned category is a defensible reading, counted as agreement rather than
  error).
- All 6 strict disagreements shared the same identified mechanism: the classification pipeline
  checks the abbreviated `Disease_clean` field first and only falls back to the fuller `Disease`
  field if `Disease_clean` yields no match at all. In each case `Disease_clean` retained a generic
  term (e.g. "colitis," "Fever," "Hypotension") that matched a broader category, while the fuller
  `Disease` text contained a clinically decisive modifier (e.g. "necrotizing," "Mediterranean,"
  "in extremely low birth weight infants") that would have pointed to the correct, more specific
  category — but was never consulted because a match had already been found.
- One case (PDF 6278) reflects a source-data inconsistency (the `Disease` and `Disease_clean`
  fields disagree with each other), not a classification-logic error.

## Source data

All files were generated from the working analysis repository by
`analysis/build_supplementary_files.py`, which extracts the dictionaries/lookups directly from
the scripts that performed the actual classification (`rebuild_all_consolidated_v2.py`,
`add_atc_level1.py`, `atc_level1_manual_map.py`, `emlc_atc_level1_map.py`) — nothing here is
independently re-derived, so the tables are guaranteed to match what was actually run.
