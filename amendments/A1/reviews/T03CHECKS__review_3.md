# T03 checks a–g: independent review, round 3

| field | value |
|---|---|
| reviewer | independent senior reviewer (ML evaluation software, Java/Weka/Mulan + Python), acting as the R1 reviewer for R1-M08 / R1-M10; not the author, not a previous reviewer |
| date | 2026-10-14 |
| under review | `revision_access_44676/tasks/T03-baseline-harness-checks.md` at `11eb4ee`, with emphasis on "Effect on the submitted KDIS numbers" (`:63-163`) |
| inputs | `evidence/T03__checks/probe_correction/` (64 `quant_*.json`, 84 `quantdef_*.json`, `build_corrected.py`, `effect_summary.json`, `corrected_*.json`, `tables_stored/`, `tables_corrected/`, `tables_diff.txt`, `run_def.log`, `jobs_def.txt`, `quant.py`), `results/kdis_tuned_baselines.json`, `results/kdis_published_baselines.json`, `results/lamda_baselines.json`, `results/{foundation_baselines,foundation_coverage,logreg_multiview,samefold_baselines}.json`, `paper_ieee_access/make_tables.py`, `paper_ieee_access/main.tex`, `paper_ieee_access/tables/`, `comments/R1-M10.md`, `evidence/R4-06__claims_audit.md`, `reviews/T03CHECKS__review_{1,2}.md` |
| git HEAD | `11eb4ee` (working tree clean before; only this file added) |
| scratch | `/private/tmp/claude-501/-Users-umaidahmed-Desktop-Research-Research-Writer-ML-Papers-MIML-NextGen/684ac21e-f977-4d47-9d53-9e4a3befea69/scratchpad/review_T03_r3` (`scripts/rederive3.py`, `scripts/gain.py`, `rederive3.log`, `pc/` = copy of `probe_correction/`, `mirrors/`) |

No repo file other than this review was modified. No forbidden entry point was called, no guard touched, nothing under `quarantine/` opened, no real dataset loaded (all inputs are JSON results/quant files). I started no Java process. `diagnosis/` is unchanged since `d3b6b73` (`git diff --stat`), where round 2 reran both reproduce scripts byte-identically, so I did not rerun them.

## Round-2 findings

| # | round-2 finding | status | evidence |
|---|---|---|---|
| 1 | Defaults file (`kdis_published_baselines.json`) uncorrected | **FIXED** | 84 `quantdef_*.json`; my loader: 84 configs, **735 rows**, max \|p1 − stored\| = **0.0**, quant `stored` = results file 0.0, no unused tags; both corrected files swapped into the mirror; Birdsong HL default 0.07389 → 0.07200, Yeast HL default 0.19683 → 0.19653, `\haloKdis` 0.5843 → 0.5934 |
| 2 | "Every number … from the tuned sweep" misstatement not raised | **FIXED** (`:160`) | `main.tex:1192` text confirmed; three reported default-sourced cells (Birdsong HL, Yeast HL, `\haloKdis`) confirmed as the only ones (only AP/HL comparators are reported; `tab_full` never falls back to defaults). See new finding 2 for the companion "+0.027 to +0.034" sentence |
| 3 | "58 of 60" wrong | **FIXED** (`:101-102`) | re-derived: paper comparator **41 / 18 / 1** (worse = Scene OE +0.0005); tuned-only **48 / 10 / 2**; OneError mechanism sentence correct |
| 4 | Size table measured best-of-21, not the paper's comparator | **FIXED** (`:82-99`, `build_corrected.py:26-31`) | every cell of the table re-derived from `best()` over tuned ∪ defaults ∪ LAMDA in `make_tables.py` order; all match (Azotobacter Cov −0.5675000…8 rounds to −0.568). Comparator-change marks: see new finding 1 |
| 5 | Incomplete list of manuscript changes; R1-M10/R4-06 cross-ref | **FIXED** | AP margins, HL margins, Table VI t/p, not-evaluated gaps, macros, neural counts all match `tables_corrected/` and my recomputation; `tables_diff.txt` = `diff -u -r` of the two dirs (only file mtimes differ on regeneration); notes at `R1-M10.md:77`, `R4-06__claims_audit.md:35`: MIMLNN 0.74285 vs corrected 0.74436 → gap 0.0016 confirmed |
| 6 | fmean vs np.mean | **FIXED** (`build_corrected.py:86`) | stored summaries equal `statistics.fmean` of their own per-fold rows exactly (asserted in my script for all 336 configs × 5 metrics) |
| 7 | Quant-file provenance | **FIXED** (`:73-78`) | defaults: `run_def.log` 17:07:30–17:56:13 UTC, file mtimes 22:08–22:56 +0500 = 17:08–17:56 UTC, `jobs_def.txt` 84 jobs |

## What I ran

| # | what | result |
|---|---|---|
| R1 | `scripts/rederive3.py`: my own loader for all `quant*.json` (regex on filename, cross-file consistency check), own corrected stores (p0 rows, fmean/pstdev), own `best()` with `make_tables.py`'s pool order and first-wins ties, own `ours()`, Holm, notevaluated, neural and macro logic. No code shared with `build_corrected.py` | tuned 252 configs / 2 205 rows and defaults 84 / 735 rows, max \|p1 − stored\| 0.0 both; changed folds from `p0 ≠ p1`: 7+8+5+4+5+9+4+10+9+9+10+10 = **90**, per dataset as at `:29` |
| R2 | Paper-comparator table (`:84-97`) | every value and AP comparator arm reproduced. Comparator arm changes: **4** cells (Letter Carroll RL and Coverage, Geobacter Coverage MIMLNN → MIMLMAPkNN default, Haloarcula Coverage MIMLNN → DMIMLkNN default); `effect_summary.json` agrees (4) |
| R3 | Counts | paper 41/18/1, tuned 48/10/2, both as written |
| R4 | AP margins (`:117-125`), HL margins (`:129-137`), verdicts | all 7 AP and 7 HL margins as written; AP 6/0/2 and HL 1/3/4 unchanged; Reuters AP +0.0097 and HL +0.0052 unchanged (MIMLNN) |
| R5 | Table VI (`:139-146`) via `scipy.stats.ttest_rel` | all t values as written; Emotions p 0.1224 → 0.1319; same 7/8 pass Holm, Emotions fails, in both |
| R6 | Not-evaluated (`:147-150`), macros (`:151-155`), neural counts (`:156-159`) | Geobacter −0.0304 → −0.0405, Azotobacter −0.0153 → −0.0281, Pyrococcus −0.0177 → −0.0222; `\reutersKdis` 0.8941 → 0.8946, `\haloKdis` 0.5843 → 0.5934, `\sceneIBLR*` as written; neural 4/0/8 → 3/1/8, KDIS-only 6–6 → 5–6; Geobacter pub 0.581703 vs neural 0.581701 |
| R7 | `build_corrected.py` run from a copy (`pc/`, `PROJECT` pointed at the repo, outputs to the copy) | `effect_summary.json`, both `corrected_*.json`, `tables_stored/`, `tables_corrected/` **byte-identical** to the committed ones; `tables_diff.txt` differs only in the two header timestamps per file; stored mirror = committed `paper_ieee_access/tables/*.tex` (also checked directly with `cmp`, 8/8) |
| R8 | `scripts/gain.py`: best tuned − best default AP per dataset, submitted and corrected | finding 2 |

## New findings

**1. MINOR: the number of comparator changes is wrong.** `T03-baseline-harness-checks.md:105` says the best-configuration choice changes "in 3 of the paper's comparator cells (marked *)". The table at `:90,94,96` marks **four** cells (Letter Carroll RL\*, Letter Carroll Coverage\*, Haloarcula Coverage\*, Geobacter Coverage\*), and both my re-derivation and `effect_summary.json` (`paper_best.submitted[0] ≠ corrected[0]`) give 4. This is a count bound for the response letter.
*Fix:* "and in 4 of the paper's comparator cells (marked *)". Optionally name them, since two of them (Geobacter and Haloarcula Coverage) are switches from MIMLNN to a corrected default configuration.

**2. MINOR: the "+0.027 to +0.034" sentence is flagged but its corrected value is not given.** `:160` says the defaults→tuned gain at `main.tex:1191` "compares two probe-affected sets" and that the response to R1-M08 states this, but gives no corrected figure, so the response letter has nothing to report. No script or results file regenerates the submitted range. The only reading I can reproduce is best-tuned − best-default AP per dataset on MSRC v2, Letter Frost and Letter Carroll: submitted +0.0319 / +0.0276 / +0.0337 (= "+0.027 to +0.034"), corrected **+0.0313 / +0.0281 / +0.0330** ("+0.028 to +0.033"). Over all 12 datasets the corrected gain ranges from −0.0046 (Haloarcula, where a default beats every tuned configuration, which is why `\haloKdis` is a default) to +0.0557 (Reuters), so the manuscript's range was never the full picture.
*Fix:* add one sentence with the corrected values and the scope they cover (a small script in `probe_correction/` that prints them), or state that the sentence is withdrawn in the revision and why.

**3. MINOR: stale status line.** `:3` reads "Status: **IN-REVIEW** (round 2)", while the review log (`:172`) records the round-3 changes.
*Fix:* "IN-REVIEW (round 3)" (or the post-review status).

## Summary
All seven round-2 findings are fixed. Independent re-derivation from `quant_*.json` + `quantdef_*.json` + `results/lamda_baselines.json` reproduces: the 2 205 + 735 = 2 940-row reproduction at 0.0; 90/105 affected folds; every cell and comparator arm of the paper-comparator table; 41/18/1 and 48/10/2; every AP and HL margin, every Table VI t and p, the not-evaluated gaps, the macros and the neural counts; and `build_corrected.py` regenerates the committed outputs byte for byte. What remains is one wrong count (3 vs 4 comparator changes), a missing corrected figure for the "+0.027 to +0.034" sentence the write-up itself raises, and a stale status line. No verdict is affected.

VERDICT: NOT RESOLVED — 3 findings
