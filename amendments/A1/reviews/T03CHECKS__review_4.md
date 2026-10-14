# T03 checks a–g: independent review, round 4

| field | value |
|---|---|
| reviewer | independent senior reviewer (ML evaluation software), acting as the R1 reviewer for R1-M08 / R1-M10; not the author, not a previous reviewer |
| date | 2026-10-14 |
| under review | `revision_access_44676/tasks/T03-baseline-harness-checks.md` at `1dba26b` (HEAD), diff since `11eb4ee` |
| inputs | `git diff 11eb4ee HEAD -- revision_access_44676` (task file `:3`, `:105`, `:160-163`, `:176`; new `probe_correction/defaults_to_tuned_gain.{py,json}`), `reviews/T03CHECKS__review_3.md`, `probe_correction/effect_summary.json`, `probe_correction/tables_diff.txt`, `probe_correction/corrected_kdis_{tuned,published}_baselines.json`, `results/kdis_{tuned,published}_baselines.json`, `paper_ieee_access/main.tex:1180-1196`, `deposit/revision_r1_analysis_plan/original_aug2026/RESULT.md:131-136` |
| scratch | `/private/tmp/claude-501/-Users-umaidahmed-Desktop-Research-Research-Writer-ML-Papers-MIML-NextGen/684ac21e-f977-4d47-9d53-9e4a3befea69/scratchpad/review_T03_r4` (`pc/` = copy of the script + corrected JSONs, `mygain.py`) |

No repo file other than this review was modified (`git status` clean before writing it). No real-data entry point was run, nothing under `quarantine/` was opened, no dataset loaded; every input is a results/evidence JSON.

## Round-3 findings

| # | round-3 finding | status | evidence |
|---|---|---|---|
| 1 | "3 of the paper's comparator cells" should be 4 | **FIXED** (`:105`) | now "4 … (marked *: Letter Carroll RankingLoss and Coverage, Geobacter Coverage, Haloarcula Coverage)". `effect_summary.json` `effect/<ds>/<metric>/paper_best`: exactly 4 arm changes — LC Coverage MIMLDGC→DMIMLkNN AveH, LC RL MIMLDGC→MIMLMAPkNN AveH, Geobacter Coverage MIMLNN→MIMLMAPkNN (default), Haloarcula Coverage MIMLNN→DMIMLkNN (default); matches the four * in the table (`:90,94,96`) |
| 2 | Corrected value for the "+0.027 to +0.034" sentence missing | **FIXED** (`:160-163`, new script) | see R1–R3 below; every quoted number reproduced |
| 3 | Stale status line | **FIXED** (`:3`) | "IN-REVIEW (round 4)"; review log row 3 added (`:176`) |

## What I ran

| # | what | result |
|---|---|---|
| R1 | `defaults_to_tuned_gain.py` from a scratch copy (`R` pointed at the repo `results/`, corrected JSONs copied alongside, output written to scratch) | output JSON **byte-identical** (`cmp`) to the committed `defaults_to_tuned_gain.json` |
| R2 | `mygain.py`: own loader (per-dataset grouping, 21 tuned / 7 default configs per dataset checked for all 12 datasets in both file pairs), own max, prints the winning arms | identical per-dataset values. Submitted: MSRC v2 +0.0319, Letter Frost +0.0276, Letter Carroll +0.0337 (only these three fall in [0.027, 0.034]); min −0.0064 Haloarcula, max +0.0561 Reuters. Corrected: +0.0313 / +0.0281 / +0.0330 ("+0.028 to +0.033"); min −0.0046, max +0.0557. Haloarcula is the only dataset where the best default (DMIMLkNN) beats all 21 tuned configurations, in both sets — as `:161` says |
| R3 | `main.tex` lines | `:1191` "baselines gained $+0.027$ to $+0.034$ average precision" (sentence starts on `:1190`), `:1192` "Every number in this paper is from the tuned sweep." — matches the write-up's citations `main.tex:1190-1191` and `:1192`. `main.tex` unchanged since the as-submitted commit `aceec7b` |
| R4 | Paper-comparator table (`:84-97`) re-read from `effect_summary.json` | all 12 rows × (folds changed, 5 deltas, AP comparator arm) match; folds 7+8+5+4+5+9+4+10+9+9+10+10 = 90 of 105 as at `:29`; counts 41/18/1 and 48/10/2 match `counts_over_60_dataset_metric_pairs`; the 18 unchanged = 11 OE + 4 Reuters non-OE + Haloarcula AP + MSRC v2 RL/Coverage (all MIMLNN), consistent with `:99,101` |
| R5 | Macros vs `tables_diff.txt` | `\reutersKdis`, `\haloKdis`, `\sceneIBLRMax/Ave/Min` old → new exactly as `:152-154` |
| R6 | End-to-end read of the write-up | sections unchanged since `11eb4ee` were fully re-derived in round 3 (margins, Table VI, not-evaluated gaps, neural counts); I re-read them for internal consistency with the new text and found no conflict |

## Considered and not raised

- `:160` "is wrong on two counts. No submitted script regenerates it, and … the range holds only for three datasets": unregenerability is a traceability defect rather than a numerical error, but both statements are true and the bullets that follow give the full and probe-corrected ranges, so the response letter has everything it needs. Not a concrete false statement.
- The archived August note (`deposit/.../original_aug2026/RESULT.md:122`) calls 0.5843 a "tuned KDIS" Haloarcula value; it is a default. That file is a frozen deposit outside the write-up, and the write-up itself states the correct provenance (`:153`, `:160-161`). Out of scope.

## New findings

None.

## Summary
All three round-3 findings are fixed. The new script reruns byte-identically, an independent re-implementation reproduces every number quoted from it (three-dataset submitted and corrected ranges, the 12-dataset ranges, and the Haloarcula default-beats-tuned statement), and `main.tex:1190-1192` says what the write-up says it says. The comparator-change count of 4 and the named cells match `effect_summary.json`. No remaining false, unsupported or internally inconsistent statement found.

VERDICT: RESOLVED, 100%
