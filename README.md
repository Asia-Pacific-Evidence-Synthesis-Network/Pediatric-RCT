# Analysis Code Organization — RCT Trend Manuscript

This folder organizes the analysis code and data for "Global Disparities in Pediatric
Medication Trials, 1956-2023" into the four Results sections, plus shared infrastructure.

**Update:** five scripts (`table1_and_characteristics_v2.py`, `country_map_plots.py` was
already fixed earlier, `income_group_characteristics_analysis_v2.py`, `income_group_plots2.py`,
`drug_atc_emlc_v2.py`, `emlc_atc_level1_plots.py`) originally read `Trial bank_13465.xlsx` (an
older, superseded trial bank — the manuscript uses `Trial bank_13269.xlsx`) or stale
intermediate files. **These have been corrected and re-run.** For `income_group_*` and
`table1_and_characteristics_v2.py`, the output was verified byte-identical to the pre-fix
version (the 13465→13269 cleanup didn't change these particular numbers). For
`emlc_atc_level1_plots.py`, the old path pointed to a genuinely stale file and the fixed
version now correctly reproduces the manuscript's EMLc figures (241/359 = 67.1% overall).
Sections `01`-`04` and `00_Shared_Data_and_Scripts/primary_data` now contain **zero** code
referencing `Trial bank_13465.xlsx`.

Historical Trial-Bank-construction scripts (the ones that built the *predecessor* of
`13269`, before it existed, and are not needed to reproduce current results) were moved to
`_legacy_pipeline_history/` — separated from the current, working codebase so "final version"
only means final version. `NEEDS_REVIEW/` scripts (superseded or unused-in-final-manuscript
analyses) still reference the old file; they were left as-is since their outputs aren't part
of the submitted manuscript.

The original `/Users/leayu/Documents/trend_rct/analysis/` folder's five corrected scripts were
edited in place (this was an explicit, later instruction superseding the original
"don't modify" request — everything else in `analysis/` is untouched).

**Analysis/plotting separation, then consolidation to one analysis file per section.** Every
script that originally mixed data computation (writing CSV/JSON) with plotting
(`savefig`/`write_image`) was first split into an `_analysis.py` half and a `_plots.py` half.
That produced multiple analysis files per section (e.g. Section 1 briefly had three: a Table 1
script, a country-map script, and a shared country-cleaning helper — two of which turned out to
contain a near-duplicate, silently-drifted copy of the same country-name-cleaning logic). Each
section's analysis files have since been merged into exactly **one** analysis script per section:

| Section | Analysis file (one per section) | Plot file(s) |
|---|---|---|
| 01 | `characteristics_analysis.py` | `country_map_plots.py` |
| 02 | `income_group_characteristics_analysis_v2.py` (already single-file) | `income_group_plots2.py` |
| 03 | `drug_atc_emlc_v2.py` (already single-file) | `atc_level1_plots.py`, `emlc_atc_level1_plots.py` |
| 04 | `burden_analysis.py` (merged from 6 files) | `burden_perspective1_global_plots.py`, `burden_perspective2_age_band_plots.py`, `burden_cause_age_heatmap_plots.py`, `burden_perspective3_income_group_plots.py` |

Section 1's merge also removed genuine dead code found during consolidation (a `clean_country`
call whose result was never used — the real country list came from a different file) and
eliminated the duplicate cleaning-logic drift. Section 4's merge eliminated redundant disk
round-trips between pipeline steps (the trial bank was being read from disk 4 separate times;
intermediate CSVs were being written then immediately re-read in the same logical pipeline) by
reusing in-memory DataFrames between steps instead — each step still gets its own isolated copy
of the trial bank before applying step-specific filters, so no step's behavior changed. Verified:
every one of Section 4's 14 output CSVs was diffed against its pre-merge version; all matched to
within 1e-9–1e-16 (floating-point summation-order noise from no longer round-tripping through
disk, far below any reported precision), and all 4 of Section 4's plot scripts re-ran
successfully against the consolidated output. Sections 2 and 3 already had one analysis file
each and were not restructured.

**Important — hardcoded paths.** Every script uses absolute, hardcoded file paths (e.g.
`/Users/leayu/Documents/trend_rct/Trial bank_13269.xlsx`), not relative paths. Copying a
script into this folder does **not** change what it reads or writes — running a script from
here still touches the same original absolute locations it always did. The `data/` and
`figures/` subfolders in each section are reference copies of relevant inputs/outputs for
inspection, not a self-contained runnable environment.

## Folder structure

```
00_Shared_Data_and_Scripts/   Infrastructure used across multiple/all sections
01_Characteristics_of_RCTs/   Table 1, Figure S2
02_Income_Groups/             Figure 1A/1B, Figure S3, Figure S4
03_Therapeutic_Coverage/      Figure S5, Figure S6, Figure 2
04_Disease_Burden/            Figure 3, Figure 4A/4B, Figure S7, Figure S8
NEEDS_REVIEW/                 Scripts I could not confidently map to a current section
                               (mostly superseded v1 versions or analyses not in the final
                               manuscript) — see table at the bottom of this file.
```

---

## 00_Shared_Data_and_Scripts

Scripts and data used by more than one Results section, or that build the underlying Trial
Bank itself (upstream of all four sections).

| Subfolder | Contents |
|---|---|
| `primary_data/` | `Trial bank_13269.xlsx` (the final trial bank) and `trial_country_income_v2.csv` (country→income-group mapping, used by Sections 1, 2, and 4) |
| `trial_bank_construction/` | Scripts that derive columns in the Trial Bank itself: `add_atc_level1.py`, `add_gbd_l2_column.py`, `update_gbd_l2_column_recheck.py`, `adults_included_parse.py`/`parse2.py`/`finalize.py`, `fill_missing_age_bands.py`, `nonpharm_arms_classify.py`, `rebuild_all_consolidated_v2.py`, `rebuild_clean_final.py` |
| `reference_dictionaries/` | `atc_level1_manual_map.py`, `emlc_atc_level1_map.py` — hand-built drug/medicine → ATC classification lookups, feeding Supplementary Files S1/S2 |
| `supplementary_file_builders/` | `build_supplementary_files.py`, `build_topic_validation_sheet.py`, plus a copy of the `supplementary_files/` output folder (Supplementary Files S1-S4) |

**Flag:** `update_gbd_l2_column_recheck.py` is the one script in the whole codebase that calls
an LLM API directly (title-based recheck of low-confidence GBD cause classifications). You
asked to exclude AI-classification code from an earlier summary of "all analysis code" — it's
included here for completeness/traceability since it's part of the existing codebase, but flagged
so you can exclude it if you only want non-AI descriptive/statistical code.

---

## 01_Characteristics_of_RCTs

**Manuscript section:** "Characteristics of pediatric medication RCTs" — Table 1, trial
counts/design/region/topic/drug-class summary text, Figure S2 (geographic distribution).

| Script | Produces |
|---|---|
| `table1_characteristics_analysis.py` | Table 1 summary statistics (printed + `table1_characteristics_v2.json`) |
| `country_map_analysis.py` | Country-level data for Figure S2 (`country_trial_counts.csv`) |
| `country_map_plots.py` | Figure S2 (country choropleth map + top-20 bar chart), reads the CSV above |
| `country_cleaning.py` | Shared country-name-cleaning helper (`clean_country`, alias dict, exclude list) imported by both scripts above |

`table1_characteristics_analysis.py` and `country_map_analysis.py` each had their own
near-duplicate copy of the country-name cleaning logic, which had quietly drifted apart (only
one recognized "türkiye" as an alias for Turkey). Consolidated into `country_cleaning.py`, now
imported by both. Their *denominators* remain intentionally different, not a bug: Table 1
reports country stats over all 13,269 trials with an identifiable single country (135
countries, 7,464 trials), while Figure S2 restricts to the subset also used in the income-group
analysis (130 countries, 7,454 trials, matching the manuscript text).

**Known issues:**
- `table1_characteristics_analysis.py` reads `Trial bank_13269.xlsx` (fixed from the originally
  stale `13465` reference) — verified, Table 1 numbers reproduce exactly.
- The original `table1_and_characteristics_v2.py` also contained a **second, independent**
  country-map computation bundled into the same file, with its own (different, and wrong)
  country-name cleaning logic — it produced 135 countries / US=1,742 / 78 countries at 1–10
  trials, none of which match the manuscript (130 / 1,749 / 73). That code has been **removed
  entirely**, not split out, since it was a redundant duplicate of Figure S2, not something the
  manuscript actually uses. `country_map_analysis.py` + `country_map_plots.py` (verified against
  the manuscript: 130 countries, US=1,749, 73 countries at 1–10 trials) are the only country-map
  code kept.
- Figure S1 (literature screening flow chart) has no corresponding script anywhere in
  `analysis/` — likely built manually. Not included here; see Needs Review notes below.

---

## 02_Income_Groups

**Manuscript section:** "Pediatric medication RCTs across country income groups" — Figure 1A
(decade trend), Figure 1B (ATC distribution by income group), Figure S3 (topic distribution by
income group), Figure S4 (age-band representation by income group).

| Script | Produces |
|---|---|
| `income_group_characteristics_analysis_v2.py` | All underlying data: decade trend, ATC distribution, topic crosstab, age-band distribution, transparency, and power/sample-size summaries, each by income group (6 CSVs in `data/`) |
| `income_group_plots2.py` | Figure 1A and 1B as PNGs, plus an income-group power figure (unused — power/AE analysis was removed from the manuscript) |

**Known issues (important):**
- Both scripts read `Trial bank_13465.xlsx` (does not exist) and, for the trend figure,
  `income_group_plots2.py` reads `analysis/income_group_trend_by_decade.csv` — an **older,
  non-"_v2" file** with slightly different numbers than what's in the manuscript, not the
  `_v2` CSV this same script's sibling analysis produces.
- **Figure S3's PNG** (`income_group_topic_heatmap.png`, copied here) has **no generating
  script anywhere** in `analysis/` — only the underlying CSV (`income_group_topic_crosstab_v2.csv`)
  is produced; nothing turns it into the plot.
- **Figure S4's PNG** (`income_group_age_band.png`, copied here) has **no generating script
  anywhere** either, for the same reason.
- During this project, verified/corrected replacement scripts for Figure 1A, 1B, and S3 (using
  the correct `_v2` CSVs, matching the manuscript numbers exactly) were separately built in
  `/Users/leayu/Documents/trend_rct/code for plots/` (`income_group_trend_by_decade.py`,
  `income_group_atc_heatmap.py`, `income_group_topic_heatmap.py`). Those are **not** part of
  the original `analysis/` codebase and are not copied into this folder, per your instruction
  not to introduce new analysis code here — but if you need a version that actually runs and
  reproduces the manuscript's exact numbers, that's where it is. Figure S4 has no such
  replacement yet; nothing currently reproduces it.

---

## 03_Therapeutic_Coverage

**Manuscript section:** "Therapeutic coverage of pediatric medication RCTs" — Figure S5 (ATC
frequency), Figure S6 (ATC trend over time), Figure 2 (EMLc coverage).

| Script | Produces |
|---|---|
| `atc_level1_plots.py` | Figure S5 (`atc_level1_frequency.png`) and Figure S6 (`atc_level1_trend_by_decade.png`) |
| `drug_atc_emlc_v2.py` | A `_v2` version of the ATC-trend-by-decade data (`atc_level1_trend_by_decade_v2.csv`) — relationship to Figure S6 unclear, see below |
| `emlc_atc_level1_plots.py` | Figure 2 (EMLc coverage bar chart) |

**Known issues:**
- `atc_level1_plots.py` reads `analysis/atc_level1_trend_by_decade.csv`, but **no script
  anywhere writes this file** — its provenance is untraceable from the current codebase.
- `drug_atc_emlc_v2.py` reads the stale `Trial bank_13465.xlsx` and produces a differently-named
  `_v2` CSV that no plotting script reads. Unclear whether this script's output is actually used
  in the final Figure S6, superseded it, or is an abandoned parallel attempt.
- **`emlc_atc_level1_plots.py` reads `analysis/emlc_atc_level1_coverage.json`, which is STALE**
  (produces an overall EMLc coverage of 243/359 = 67.7%, Antiparasitic group 32/40 = 80.0%).
  The manuscript's actual numbers (241/359 = 67.1%, Antiparasitic/P-group 30/40 = 75.0%) come
  from `results_v2_20260809/emlc_atc_level1_coverage_v2.json` — copied here as
  `emlc_atc_level1_coverage_v2.json` alongside the stale one (renamed
  `emlc_atc_level1_coverage_STALE.json`) so both are visible for comparison. If you re-run
  `emlc_atc_level1_plots.py` as-is, Figure 2 will not match the manuscript.
- A corrected, verified version of this script is in `/Users/leayu/Documents/trend_rct/code for
  plots/emlc_atc_level1_coverage.py` (not copied here, same reasoning as above).
- `drug_landscape_plots.py` was **not** placed here — it analyzes therapeutic coverage using an
  older free-text 24-class drug dictionary (`Intervention_Drug_Class`) rather than the WHO ATC
  classification the manuscript actually reports, and appears to be an earlier/superseded
  approach. See Needs Review.

---

## 04_Disease_Burden

**Manuscript section:** "Pediatric medication RCTs relative to disease burden" — Figure 3
(cause-level ratio), Figure 4A (age-band alignment), Figure 4B (cause × age-band heatmap),
Figure S7 (income-group volume), Figure S8 (income-group × cause heatmap).

| Script | Produces |
|---|---|
| `burden_merge_gbd.py` | Merges trial-level GBD cause classifications with raw GBD burden data |
| `burden_by_gbd_cause.py` | Aggregated burden-by-cause and burden-by-cause-by-age-band tables (averaged DALYs, 1990-2022) |
| `burden_perspective1_global.py` | **Figure 3** |
| `burden_perspective2_age_band.py` | **Figure 4A** (output files are internally named `perspective3_...` — a leftover naming inconsistency from earlier renumbering; not fixed here per "preserve original code") |
| `burden_cause_age_heatmap.py` | **Figure 4B** |
| `burden_perspective3_income_group.py` | **Figure S7 and Figure S8** (output files are internally named `perspective4_...`, same naming-inconsistency note as above) |
| `burden_correlation_analysis.py` | Spearman/gamma-regression correlation analysis — **not used in the final manuscript** (explicitly removed from Results during this project); kept here for reference only |

This section's scripts were rebuilt late in the project against the current
`Trial bank_13269.xlsx` and are, to the best of my verification this session, internally
consistent and reproducible as-is (no stale-path issues found here, unlike Sections 1-3).
`data/all_GBD_data/` contains the raw GBD 2023 source extract; `data/*.csv` contains all
intermediate and final burden-comparison tables from `burden_of_disease_results/`.

---

## NEEDS_REVIEW

Scripts I could not confidently assign to a current manuscript section — mostly superseded
non-"_v2" predecessors of scripts already placed above, or analyses (age-band×topic, trial
transparency trends, adverse-event/power detection) that don't appear to correspond to any
figure or table in the current manuscript. I have **not** deleted or altered any of these —
they remain in `analysis/` untouched; these are copies for your review.

| Script | Why it's flagged |
|---|---|
| `age_band_plots.py`, `age_band_plots_v2.py` | Produce `age_band_stacked_area.png`, `neonate_trend.png` — not matched to any current Figure/Figure S caption |
| `age_band_topic_analysis.py`, `age_band_topic_analysis_v2.py`, `age_band_topic_heatmap.py`, `age_band_topic_heatmap_v2.py` | Age-band × topic crosstab/heatmap — distinct from Figure S3/S4 (which are topic/age-band *by income group*, not by each other); not matched to a current caption |
| `drug_landscape_plots.py` | Earlier therapeutic-coverage analysis using a free-text drug dictionary rather than WHO ATC; likely superseded by Section 3's scripts |
| `income_group_analysis.py`, `income_group_analysis_v2.py`, `income_group_characteristics_analysis.py`, `income_group_plots.py` | Non-"_v2" or earlier predecessors of the scripts placed in `02_Income_Groups/` |
| `power_analysis.py`, `power_analysis_v2.py`, `power_plots.py`, `power_plots_v2.py` | Adverse-event detectable-risk/power analysis — this entire analysis was removed from the manuscript (harm-detection section deleted) |
| `transparency_analysis.py`, `transparency_plots.py`, `transparency_region_analysis.py`, `transparency_region_plots.py` | Trial registration/funding/data-sharing *trend-over-time and by-region* figures — Table 1 already reports registration/funding/data-sharing as simple proportions; these more detailed trend figures don't appear to be cited by any current Figure/Figure S caption |

If any of these actually do correspond to a figure, table, or in-text statistic I missed, let
me know which one and I'll re-file it into the correct section.

---

## Summary: what's confirmed vs. what needs attention

**Confirmed working as-is:** all of Section 4 (Disease Burden).

**Stale/broken if re-run today** (all reference `Trial bank_13465.xlsx`, which has been
superseded by `Trial bank_13269.xlsx`): `table1_and_characteristics_v2.py`,
`income_group_characteristics_analysis_v2.py`, `income_group_plots2.py`, `drug_atc_emlc_v2.py`,
and several `NEEDS_REVIEW` scripts. Their **existing output files** (the CSVs/PNGs copied into
each section's `data/`/`figures/`) were generated before this path broke and, where I
independently verified them against the manuscript this session (Section 2's CSVs, Figure S2),
matched correctly — but the scripts themselves cannot be re-run without a path fix, which I
have not made here per your instruction to preserve the original code unmodified.

**No source script found at all:** Figure S1 (flow chart), Figure S3's PNG, Figure S4's PNG,
and `atc_level1_plots.py`'s input CSV.

**Confirmed stale data, not just a broken path:** `emlc_atc_level1_plots.py`'s Figure 2 input
JSON — would currently reproduce a different number (67.7%) than the manuscript (67.1%).
