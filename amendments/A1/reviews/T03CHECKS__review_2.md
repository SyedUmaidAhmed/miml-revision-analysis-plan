# T03 checks a–g: independent review, round 2

| field | value |
|---|---|
| reviewer | independent senior reviewer (ML evaluation software, Java/Weka/Mulan + Python), acting as the R1 reviewer for R1-M08 / R1-M10; not the author, not the round-1 reviewer |
| date | 2026-10-13 |
| under review | `revision_access_44676/tasks/T03-baseline-harness-checks.md` at `d3b6b73`, with emphasis on the new section "Effect on the submitted KDIS numbers" (`:63-92`) |
| inputs | `evidence/T03__checks/` (`diagnosis/`, `probe_correction/`), `reviews/T03CHECKS__review_1.md`, `results/kdis_tuned_baselines.json`, `results/kdis_published_baselines.json`, `results/lamda_baselines.json`, `experiments/kdis/run_kdis_baselines.py`, `paper_ieee_access/make_tables.py`, `paper_ieee_access/main.tex`, `paper_ieee_access/submission/miml_ieee_access_source.zip`, `comments/R1-M10.md`, `evidence/R4-06__claims_audit.md` |
| git HEAD | `d3b6b73` (working tree clean before and after, except this file) |
| scratch | `/private/tmp/claude-501/-Users-umaidahmed-Desktop-Research-Research-Writer-ML-Papers-MIML-NextGen/684ac21e-f977-4d47-9d53-9e4a3befea69/scratchpad/review_T03_r2` (`scripts/rederive.py`, `scripts/defaults.py`, `scripts/qdef.py`, `scripts/mk_fmean.py`, `qdef.log`, `mirror_*`, `ev/`) |

No repo file other than this review was modified. `reproduce_t03b.py` / `reproduce_t03c.py` were run from a copy in scratch (they write into `diagnosis/reproduced/`). `build_corrected.py` was not run; its outputs were rebuilt independently. No forbidden entry point was called, no guard was touched, nothing under `quarantine/` was opened except `README.md`. Every Java process I started has exited (`pgrep java` empty).

## Round-1 findings

| # | round-1 finding | status | evidence |
|---|---|---|---|
| 1 | Cause 1 attributed to Mulan; the write is in KDIS | **FIXED** | `:18-20` cite `MIMLClassifier.java:154`, `final`, Mulan `Evaluator.java:210` probe vs the `:124-129` copy |
| 2 | "every fold" overstated; effect not quantified | **FIXED for `kdis_tuned_baselines.json`**: 90/105 counted, correction run, table and verdict check added. The quantification is incomplete, and three statements in it are wrong (new findings 1, 3, 4, 5) | `count_affected_folds.py` reruns to 90/105; my re-derivation below |
| 3 | `ties.py` did not produce the cited 0.0 | **FIXED**: `ties.py` and `tie_analysis.json` removed; `reproduce_t03b.py` regenerates everything | rerun in scratch: `t03b_reproduced.json` **byte-identical** |
| 4 | WekaSort sentence omits MIMLIBLR | **FIXED** (`:33`) | JSON: MIMLIBLR 29 rows differ, other six 0, `mulan_ranks` vs Java 0 for all |
| 5 | T03-g environment inventory | **FIXED** (`:53-60`) | spot-checked: `pyvenv.cfg` 3.14.6, `python -V` 3.14.8, Cellar 3.14.7 (09-07) / 3.14.8 (10-06), 4 dist-infos dated 10-13 |
| 6 | T03-c numbers and missing evidence | **FIXED**: 1.7e-4; `reproduce_t03c.py` added | rerun in scratch: `t03c_reproduced.json` **byte-identical**; LAMDA convention − authors = 0.0 on folds 0 and 4 |
| 7 | "one bag each"; TabPFN half missing | **FIXED** (`:15-16`) | — |
| 8 | Over-general agreement claim | **FIXED** (`:37`): OE/RL/AP only; Coverage 9.966/9.897/9.931 | matches `tie_neutral_on_letter_frost_f0.txt` |
| 9 | Bias direction; stale "Decision needed" | **FIXED** (`:38`, `:94-95`) | MIMLBRkNN OE 0.1379 vs 0.1724 confirmed |
| 10 | ProbeDump header; only 2 methods proven | **FIXED**: header added; all 7 in `t03b_reproduced.json` | probe-correction `build/ProbeDump.class`: bytecode (`javap -c -p`) identical to a fresh compile of the current `ProbeDump.java` |

## What I ran

| # | what | result |
|---|---|---|
| R1 | `scripts/rederive.py`: my own loader for all 64 `quant_*.json` (no shared code with `build_corrected.py`); compared with `results/kdis_tuned_baselines.json`; recomputed summaries with `statistics.fmean`/`pstdev` | 252 configurations, **2 205 rows**, no tag duplicated across files, `p1` − stored (results file) **max 0.0**, `quant.stored` − results file 0.0. Corrected per-fold rows = `p0` exactly. Corrected summaries vs fmean/pstdev ≤ 3.6e-15 |
| R2 | Stored summaries vs recomputation from their own `per_fold` | `run_kdis_baselines.py:200-202` uses **`statistics.fmean` / `statistics.pstdev`**, not `np.mean`/`np.std`; recomputation matches to **0** (exact); 0 failed folds; per-fold keys are exactly the five metrics |
| R3 | Per-dataset effect table re-derived (best of the 21 tuned configurations) | **every cell of `:72-83` reproduced**, including bracketed per-config AP maxima; 90/105 both from the ARFF (`count_affected_folds.py`) and from `p0 ≠ p1` |
| R4 | Direction count over the 60 best-config pairs | **48 improve, 10 unchanged, 2 worse**, not "58 of 60" (finding 3). The 10 unchanged are OneError, Δ = 0 exactly, on every dataset except Scene and Reuters |
| R5 | Best-config choice changes | exactly 2, both Letter Carroll: Coverage MIMLDGC AveH → DMIMLkNN AveH, RankingLoss MIMLDGC AveH → MIMLMAPkNN AveH. **Confirmed** |
| R6 | `scripts/mk_fmean.py` + two mirrors: `make_tables.py` on stored results, and on a corrected file I built myself with fmean/pstdev | stored mirror = committed `paper_ieee_access/tables/*.tex` byte for byte; committed = the submission zip's tables byte for byte. My corrected mirror = `tables_corrected/*.tex` **byte for byte**, and stdout is identical. So the np-vs-fmean difference has no output effect (finding 6 is documentation only) |
| R7 | Diffed `tables_stored/` vs `tables_corrected/` | AP 6/0/2, HL 1/3/4, rule 3 of 4 with 6 qualifying, Holm 7/8 with Emotions failing: **all confirmed unchanged**. All seven AP margins at `:90` are confirmed. Neural 4/0/8 → 3/1/8 and KDIS-only 6–6 → 5–6 are confirmed. Geobacter 0.5817 = neural 0.5817 is confirmed. Changes the write-up does not list: finding 5 |
| R8 | Which results files `make_tables.py` reads | `PUB = tuned ∪ kdis_published_baselines.json ∪ lamda` (`make_tables.py:54-56,126`); `best(PUB, …)` feeds tab_headline, tab_notevaluated, tab_holm and the macros; `kdis_only = {**TUNED, **DEFAULTS}` (`:610-614`) |
| R9 | `scripts/defaults.py`: does an uncorrected default configuration win a paper cell? | **Yes.** In the submitted tables: Birdsong HL (MIMLDGC default), Yeast HL (MIMLBRkNN default), `\haloKdis` (DMIMLkNN default). In `tables_corrected/` the Birdsong HL cell is **still the uncorrected default 0.0739** (finding 1) |
| R10 | `scripts/qdef.py`: ProbeDump `--probe 1/0` on the submitted ARFF for 4 **default** configurations (Java only) | `p1` reproduces the stored `kdis_published_baselines.json` rows **exactly (0.0)** for all 4, so the defaults file carries the same bug. Corrected means: Birdsong MIMLDGC HL 0.07389 → **0.07200**, AP 0.70855 → 0.71023. Yeast MIMLBRkNN HL 0.19683 → **0.19653**. Letter Frost MIMLMAPkNN Coverage 9.529 → 9.471, RL 0.14911 → 0.14763. Pyrococcus MIMLDGC HL 0.05929 → 0.05888 |
| R11 | Provenance of the quant files (mtimes, `jobs.txt`, round-1 scratch) | finding 7 |
| R12 | `count_affected_folds.py` (reads ARFF text only) | 90/105, per-dataset counts as written |

## New findings

**1. MAJOR: the correction leaves the second KDIS results file uncorrected, so the "corrected" tables are still partly probe-affected.** `T03-baseline-harness-checks.md:66,88` and `build_corrected.py:13-23` treat `results/kdis_tuned_baselines.json` as the only KDIS input. But `make_tables.py:54-56` puts `results/kdis_published_baselines.json` (7 methods at shipped defaults × 12 datasets, 84 configurations, 735 per-fold rows) into the `PUB` pool, and `:610-614` uses it in `kdis_only`. That file was produced by the same `run_kdis_baselines.run_one` → `EvaluatorHoldout` path. I ran ProbeDump on 4 of its configurations (R10): `--probe 1` reproduces the stored rows exactly, and `--probe 0` changes them. Default configurations are the paper's comparator in these cells:
- **Birdsong HL, headline table.** Best published is `MIMLDGC` (default) at 0.0739 in **both** `tables_stored/tab_headline.tex` and `tables_corrected/tab_headline.tex`. Its corrected value is 0.0720, so the margin is −0.0211, not −0.0192.
- **Yeast HL, headline table.** `tables_corrected` switches the comparator to MIMLBRkNN MinH (0.1967) only because the default it beats is uncorrected. The fully corrected best is the default, 0.1965, giving a margin of +0.0040 (tie), not +0.0042.
- **`\haloKdis`** was a default (DMIMLkNN, 0.5843) in the submitted paper. Its corrected value was not measured.
- **The neural-context counts** (`:91`): Geobacter's new tie sits exactly at the published 0.5817. Defaults within reach of a protein-sized correction (≤ 0.023 AP per configuration, `:83`): Geobacter MIMLMAPkNN 0.5686 and DMIMLkNN 0.5626, Pyrococcus MIMLMAPkNN 0.5222. Until they are corrected, 3/1/8 and 5–6 are not certified.
- **`main.tex:1191`** ("+0.027 to +0.034" gain from defaults to tuned) compares two probe-affected sets.
No headline AP or HL *verdict* can flip from what I measured (Birdsong HL stays a loss, Yeast HL stays a tie). But "Every submitted KDIS number is therefore exactly the library's probe-affected value", and the claim that the corrected copy shows the corrected manuscript, are only established for one of the two files.
*Fix:* run `quant.py` over `kdis_published_baselines.json` (84 configurations; `classifier_block(algo)` with no distance or k, one output file per writer). Extend `build_corrected.py` to write `corrected_kdis_published_baselines.json`, swap **both** files into the corrected mirror, and regenerate `tables_corrected/`, `effect_summary.json` and `:68-91`. Then state the 735-row reproduction alongside the 2 205-row one. Alternatively, if the revision drops defaults from `PUB`, say so explicitly. Even then, the submitted-manuscript effect still needs the corrected defaults, because the submitted Birdsong and Yeast HL cells used them.

**2. MINOR (response-letter accuracy): the submitted manuscript says every number is from the tuned sweep, and it is not.** `paper_ieee_access/main.tex:1191-1192`: "Every number in this paper is from the tuned sweep." `make_tables.py` takes the best over tuned ∪ defaults ∪ LAMDA. So the submitted headline Birdsong HL comparator (`\algo{MIMLDGC}`, no distance suffix) and Yeast HL comparator (`\algo{MIMLBRkNN}`) are default-configuration rows, and so is `\haloKdis`. This bears directly on R1-M08 (baseline fidelity). The T03 write-up is where it surfaced, and it does not mention it.
*Fix:* add one bullet under "Effect on the submitted manuscript": "the submitted best-published pool included the shipped-default runs; three reported cells came from them (Birdsong HL, Yeast HL, `\haloKdis`), contrary to main.tex:1192". Carry it into the response to R1-M08 and into the revision's description of the baseline pool.

**3. MAJOR: "improves on 58 of 60 dataset-metric pairs" is wrong.** `T03-baseline-harness-checks.md:85`. Re-derived from the quant files (R4): the best configuration improves on **48**, is **unchanged on 10** (OneError, Δ = 0 exactly, on MSRC v2, both Letters, Birdsong, Emotions, Yeast and all four proteins), and worsens on 2 (OneError, Scene and Reuters, +0.0005). The table at `:72-83` shows those zeros itself, so the sentence contradicts its own table. That matters because this count goes to the reviewer. The mechanism also deserves one clause: the probe only ever turns a 0 label into a 1. That cannot make a top-ranked label irrelevant, so for the best configuration OneError can only stay equal or look better under the bug, never worse.
*Fix:* "improves on 48 of 60, is unchanged on 10 (all OneError), and is worse on 2 (OneError on Scene and Reuters, +0.0005 each)". Keep "made the baselines look worse" for AP, HL, RL and Coverage, and say OneError was unaffected or slightly favourable to the baselines.

**4. MAJOR: the size table measures the best of the 21 tuned configurations, which is not the paper's comparator, yet it is presented as what the paper compares against.** `:68` and `:85` ("the best configuration, which is what the paper compares against"), and `build_corrected.py:25` ("the paper's 'best tuned published'"). The paper compares against `best(PUB)` = tuned ∪ defaults ∪ LAMDA MIMLNN. Consequences:
- Reuters AP (+0.0004) and Haloarcula AP (+0.0109) have **zero** effect on the paper, because MIMLNN (0.9677; 0.606) is the comparator. Accordingly `tab_holm` Reuters and `tab_notevaluated` Haloarcula are unchanged in `tables_corrected/`.
- "favoured our method … by up to 0.013 AP on the protein sets" (`:85`) therefore overstates Haloarcula. The paper-level AP effects on the proteins are Geobacter +0.0100, Azotobacter +0.0128, Pyrococcus +0.0045, Haloarcula 0.
- Birdsong HL, Birdsong RL, Letter Frost Coverage and Pyrococcus HL have a default configuration as the paper's best (R9), so the table's HL/RL/Coverage cells for them are not the paper-level effect.
*Fix:* add a column (or a second table) "paper's best published (tuned ∪ defaults ∪ MIMLNN), submitted → corrected" for at least AP and HL. Reword `:85` so that "up to 0.013" refers to that column. Correct the `build_corrected.py` docstring and the `effect_summary.json` key description.

**5. MINOR: the list of manuscript changes is incomplete for a response letter.** `:89-91` give only the AP margins and the neural counts. `diff tables_stored tables_corrected` also changes the following:
- HL margins (Table headline): MSRC v2 +0.0181 → +0.0177, Letter Frost −0.0093 → −0.0104, Letter Carroll −0.0103 → −0.0114, Emotions −0.0020 → −0.0031, Scene −0.0252 → −0.0259. Yeast +0.0043 → +0.0042, with the comparator label changing from MIMLBRkNN to MIMLBRkNN MinH (see finding 1).
- Not-evaluated table: Geobacter −0.0304 → −0.0405, Azotobacter −0.0153 → −0.0281, Pyrococcus −0.0177 → −0.0222.
- Table VI t and p: Emotions p 0.122 → 0.132 (`\pEmoAP`, `\tEmoAP` in prose); Birdsong t −4.02 → −4.59.
- `tab_full`: every KDIS row.
- Macros: `\sceneIBLRMax/Ave/Min`, `\reutersKdis` 0.8941 → 0.8946, `\haloKdis` 0.5843 → 0.5888 (still incomplete per finding 1).
- The write-up should say that Reuters' AP margin (+0.0097) is unchanged because MIMLNN is the comparator.
- It should also cross-reference the planned R1-M10 / R4-06 C11 replacement sentence. That sentence ("LAMDA MIMLNN 0.74285 vs KDIS MIMLIBLR_AveH 0.7434", `comments/R1-M10.md:49`, `evidence/R4-06__claims_audit.md` C11) uses a probe-affected value. Corrected, it is 0.7444, so the gap is 0.0016, not 0.0006.
*Fix:* append the full diff as a list, or commit `diff -u tables_stored tables_corrected` as `probe_correction/tables_diff.txt` and cite it. Add a note to R1-M10 / R4-06 C11 to use the corrected MSRC v2 value.

**6. MINOR: `build_corrected.py` misstates how the submitted summaries were computed.** `build_corrected.py:15-16` says "recomputed as the submitted file computes it (np.mean, np.std with ddof 0)". The submitted file used `statistics.fmean` and `statistics.pstdev` (`experiments/kdis/run_kdis_baselines.py:200-202`). Recomputing the stored summaries that way matches them exactly, while `np.mean` differs from them by up to 3.6e-15. I checked that this changes no output: my fmean-based corrected file produces byte-identical tables and stdout (R6).
*Fix:* use `statistics.fmean` / `statistics.pstdev` at `build_corrected.py:80`, or correct the docstring to say "np.mean / np.std (ddof 0), equal to the submitted fmean/pstdev within 4e-15; tables verified byte-identical".

**7. MINOR: the provenance of the quant files is not as stated.** `:64` says the outputs come from `quant.py`, run 13:57–16:30 UTC with 7 parallel jobs. In fact:
- `quant_letter_frost.json` and `quant_birdsong.json` are **byte-identical** to the round-1 reviewer's scratch outputs (`scratchpad/review_T03checks/`). They were written by that reviewer's predecessor `quant.py`, with a ProbeDump compiled without `--release 11`. Its bytecode instructions are identical to `build/ProbeDump.class`; only the class-file version differs.
- `quant_{scene,reuters,mscv2,emotions}.json` were written 13:43–13:56 UTC, before the parallel run.
- `jobs.txt` covers 9 datasets.
The results are unaffected (`p1` = stored on all 2 205 rows), but the method paragraph should be exact.
*Fix:* one sentence: "Letter Frost and Birdsong were run by the round-1 reviewer (identical ProbeDump bytecode) and imported; MSRC v2 and parts of Scene, Reuters and Emotions were run serially before the parallel batch; all files pass the same p1 = stored check."

## Summary
All ten round-1 findings are fixed. The core reproduction claims hold under independent re-derivation:
- `p1` = stored on all 2 205 tuned rows (0.0), and 90/105 affected folds.
- Every cell of the per-dataset table, and the two Letter Carroll best-config changes.
- All headline verdicts (AP 6/0/2, HL 1/3/4, rule 3/4, Holm 7/8).
- Both diagnosis scripts rerun byte-identically.
- `tables_corrected/` is reproduced byte for byte by an independent build.

What does not hold is the scope of the correction. The second KDIS file the paper draws on (`kdis_published_baselines.json`) carries the same bug, verified on 4 configurations, was not corrected, and still supplies a headline cell (Birdsong HL) in the "corrected" tables. Three write-up statements bound for the response letter are also wrong or mis-scoped: "58 of 60" (it is 48 improved / 10 unchanged / 2 worse); "best of 21 is what the paper compares against" (the paper's pool also has defaults and MIMLNN, which zeroes the Reuters and Haloarcula effects); and an incomplete list of changed manuscript numbers. No verdict I could measure flips.

VERDICT: NOT RESOLVED — 7 findings
