# T03 checks a–g: independent review, round 1

| field | value |
|---|---|
| reviewer | independent senior reviewer (ML evaluation software, Java/Weka/Mulan + Python), acting as the original R1 reviewer for R1-M08 / R1-M10 |
| date | 2026-10-13 |
| under review | `revision_access_44676/tasks/T03-baseline-harness-checks.md` (outcome table, T03-b Causes 1 and 2, T03-c, T03-g cause) |
| inputs | `experiments/revision_r1/PREREGISTERED.md` §6.8; `revision_access_44676/evidence/T03__checks/` (all 7 JSONs, both logs, `diagnosis/`); `experiments/kdis/run_kdis_baselines.py`; `experiments/revision_r1/{library_harness,t03_checks,tie_neutral_metrics}.py`; `results/kdis_tuned_baselines.json`, `results/foundation_baselines.json`; `external/MIML/` (KDIS source, shipped jar, `mulan-1-5-0-sources.jar`); `experiments/kdis/arff/` |
| git HEAD | `51b67639faa33297d658e5f53ba166a129f4ce53` |
| scratch | `/private/tmp/claude-501/-Users-umaidahmed-Desktop-Research-Research-Writer-ML-Papers-MIML-NextGen/684ac21e-f977-4d47-9d53-9e4a3befea69/scratchpad/review_T03checks` (`scripts/quant.py`, `scripts/summ.py`, `scripts/cause2.py`, `scripts/tc.py`, `quant_letter_frost.json`, `quant_birdsong.json`) |

No repo file other than this review was modified. Every Java and Octave process I started has exited (`pgrep` empty).

## What I ran

| # | what | result |
|---|---|---|
| R1 | `diagnosis/diag.py` (with `set_run_mode(False)`) into scratch, all 7 KDIS methods, Letter Frost 5×5 r0 f0 refit, AveH k=10 | ARFF pair rebuilt. PredictDump's in-process measures and the library run (`run_kdis_baselines.run_one`: RunAlgorithm → EvaluatorHoldout → BaseMIMLReport) match `T03-b__letter_frost.json` for all 7 methods |
| R2 | Compiled `TruthProbe`, `ProbeDump`, `RankDump`, `WekaSort` and `PredictDump` against `external/MIML/dist/miml-1.4-jar-with-dependencies.jar`, then ran TruthProbe on all 7 | bag 0 `…0000000` → `…0000001`, bag 1 unchanged, for all 7. Matches `truth_probe_output.txt` |
| R3 | ProbeDump with `--probe 1` and `--probe 0`, all 7 methods | probe=1 equals the library run's five metrics, max\|Δ\| = 0.0 for all 7. probe=0 equals PredictDump, 0.0. Scores and bipartitions are byte-identical between probe=0, probe=1 and PredictDump for **all 7** (the write-up checked 2) |
| R4 | Located the write in source and in the shipped bytecode (`javap -c -l`) | `miml/classifiers/miml/MIMLClassifier.java:154` `instance.setValue(labelIndices[labelIndices.length - 1], 1);`, which is bytecode line 154 → `Instance.setValue(ID)V` in the shipped jar. `makePrediction` is `final`. All 7 classes inherit it: MIMLkNN and MIMLBagging directly, the other five through `MultiInstanceMultiLabelKNN` |
| R5 | Read Mulan `Evaluator.java` | line 193 `prepareMeasures`; line 210 `learner.makePrediction(mlTestData.getDataSet().instance(0))`, the original instance and not a copy. Lines 124–129: the main loop predicts on a labels-missing **copy**, so the KDIS write lands harmlessly there. The write-up's cited lines 188–210 are correct |
| R6 | `tie_neutral_metrics.ranking_four_mulan` on PredictDump scores vs PredictDump `native_measures`, all 7 | max\|Δ\| ≤ 1.1e-16 on all 7: **Cause 2 confirmed**. `RankDump`: 0 bags with ranking ≠ ranksFromValues(confidences), for all 7. `WekaSort` vs `tn.mulan_ranks`: 0 of 203 rows differ |
| R7 | Ran the cited `diagnosis/ties.py` | It does **not** reproduce MIMLIBLR (max dev 0.793), and it writes `ties_summary.json`, not `tie_analysis.json` (finding 3) |
| R8 | Reran MIMLNN (Octave, seed 0) on folds 0 and 4 of 5×5 r0. Scored with the LAMDA convention (ascending stable sort, later label ranks higher) | Reproduces the authors' Coverage and AP **exactly** on both folds, so the T03-c tie attribution is correct (finding 6) |
| R9 | Submitted-number quantification: ProbeDump probe=1 and probe=0 on the **submitted** ARFF (`experiments/kdis/arff/`), 7 methods × 3 distances × all folds, for Letter Frost (5 folds) and Birdsong (10 folds) | probe=1 reproduces **every** stored per-fold row of `results/kdis_tuned_baselines.json` exactly (315 fold-rows, max\|Δ\| = 0). The corrections are in finding 2 |
| R10 | Counted the submitted folds whose test bag 0 has last label 0, i.e. the folds the bug actually corrupts, over all 12 datasets | 90 of 105 folds (finding 2) |
| R11 | T03-g: mtimes, stored vs rerun means, `.venv` dist-info dates, interpreter, loader pycs | finding 5 |
| R12 | Checked every outcome-table number against the JSONs | findings 6–8 |

Confirmed and needing no change: T03-a (7/7 byte-identical, pass true); T03-d; T03-e (pass, seed 1 differs); T03-f (AP 5.79e-4 vs Mulan, 0.0 vs LAMDA, n_above_1e-3 = 0); T03-b "differences > 1e-3 on every method" (HL alone is 1.33e-3 on all 7); T03-c "one Coverage difference of 0.069 = 2/29 on fold 0" and "HL, OE, RL agree on all five folds"; T03-g "folds 0–7 exact, max 0.005"; the three `g_rerun_*.json` files are byte-identical (same md5); the MIMLkNN figures 0.659/0.371/0.335 and the MIMLBagging figures 0.492/0.324/0.299.

## Findings

**1. MAJOR: Cause 1 is attributed to the wrong library, and the write-up never names the writing method.** `T03-baseline-harness-checks.md:18-19` calls it "a Mulan bug" and says the call "sets the last label … in place". The write happens in KDIS, not Mulan: `external/MIML/mavenProject/src/main/java/miml/classifiers/miml/MIMLClassifier.java:154`, `instance.setValue(labelIndices[labelIndices.length - 1], 1);`. It runs on **every** `makePrediction` call. I confirmed the same statement at line 154 in the shipped jar's bytecode, so the source matches the binary that was run. Mulan's `prepareMeasures` (`Evaluator.java:210`) is only the trigger: it passes the uncopied test instance. In Mulan's main loop (`Evaluator.java:124-129`) the write lands on a labels-missing copy, which is why predictions are unaffected. Because `makePrediction` is `final` in the base class, every KDIS MIML classifier is affected by construction, not just these 7 by observation.
*Fix:* retitle as "KDIS `MIMLClassifier.makePrediction` writes label L into its argument (MIMLClassifier.java:154); Mulan's probe (Evaluator.java:210) passes the real test bag 0". Cite both lines, give the copy-vs-original explanation, and state that it applies to every KDIS MIML classifier. Do the same in the reviewer response and the manuscript.

**2. MAJOR: the consequence for the submitted manuscript is overstated in one respect and unquantified in another.** `:22` says every KDIS number "carries this one-bag error in every fold".
(a) The first half is correct. ProbeDump with the probe reproduces all 315 stored per-fold rows of `results/kdis_tuned_baselines.json` that I tested (Letter Frost and Birdsong, 21 configurations each) to 0.0. `run_kdis_baselines.run_one` goes RunAlgorithm → EvaluatorHoldout (`EvaluatorHoldout.java:129`, the 3-arg `evaluate`) → the probe.
(b) "Every fold" is false. The truth changes only when test bag 0's last label is 0. In the submitted ARFF, 90 of 105 folds are affected: Scene 7/10, Reuters 8/10, Emotions 4/10, Letter Frost 4/5, Birdsong 9/10, Yeast 10/10, MSRC v2 5/5, Letter Carroll 5/5, and the protein sets 10, 10, 9, 9 of 10.
(c) The size is not negligible against the paper's own margins, and its sign varies by method, so it neither uniformly favours nor uniformly harms the baselines. Corrected minus submitted mean AP for the best configuration per algorithm:
- Letter Frost: MIMLkNN −0.0047, MIMLIBLR −0.0027, MIMLBagging −0.0003, DMIMLkNN +0.0014, MIMLMAPkNN +0.0013, MIMLDGC +0.0010, MIMLBRkNN +0.0004.
- Birdsong: MIMLkNN −0.0068, MIMLBagging −0.0035, DMIMLkNN +0.0046, MIMLMAPkNN +0.0049, MIMLIBLR +0.0048, MIMLDGC +0.0044, MIMLBRkNN +0.0041.
- The largest per-fold OneError shift is 1/28 = 0.036.
These are the same order as the corrected-significant Reuters (+0.0097) and Yeast (+0.0115) effects that the project's own notes call "practically negligible". A reviewer will ask whether any win or loss flips.
*Fix:* (i) Replace "in every fold" with the per-dataset affected-fold counts. (ii) Run the cheap exact correction (ProbeDump probe=0 vs probe=1, or PredictDump, on `experiments/kdis/arff/`, all 12 datasets × 21 configurations; Letter Frost took about 2 min, Birdsong about 8 min). Write it to a new evidence JSON, not `results/`. (iii) Add a table of submitted vs corrected values per dataset and metric, plus a statement of whether any submitted win, loss or best-configuration choice changes (regenerate the `make_tables.py` win counts as a sensitivity run). That table is what goes to R1-M08/M10.

**3. MAJOR: the cited evidence for Cause 2 does not produce the cited result.** `:25` cites `diagnosis/ties.py` and `tie_analysis.json` for "0.0 on all 7 methods". But `ties.py` writes `ties_summary.json` with different keys (`max_dev_mulan_reimpl_vs_inprocess` vs `mulan_reimpl_max_dev`), and it implements Mulan ranks with an **exact** stable sort and no `Utils.SMALL`. Run on the same dumps, it gives max dev **0.793 on MIMLIBLR** (R7). The 0.0 claim is true: I reproduced it with `tie_neutral_metrics.ranking_four_mulan` (R6). But the archived script is not what produced it. In addition, `tie_analysis.json`'s `tie_neutral` block is a Monte-Carlo estimate, not the A1 closed form: Coverage differs from `tn.ranking_four` by up to 0.0137 (MIMLBagging) and 0.0026 (MIMLDGC). It therefore disagrees with `tie_neutral_on_letter_frost_f0.txt`, which is closed-form. `ties.py` also contains a dead placeholder function `expected()`.
*Fix:* archive the script that actually wrote `tie_analysis.json`, or regenerate the file from `tn.ranking_four_mulan` and `tn.ranking_four` with a script committed under `diagnosis/`. Delete or mark `ties.py` as superseded and remove `expected()`. Either relabel the MC numbers or drop them.

**4. MINOR: the WekaSort sentence leaves out the method.** `:25` "0 of 29 rows differ under the 1e-6 rule, 29 of 29 under exact stable sort" describes **MIMLIBLR only**: every one of its rows has a near-tie (0 < gap < 1e-6). For the other six methods, 0 rows differ under either rule (R6, 203 rows).
*Fix:* name MIMLIBLR, and say that this is why the SMALL rule matters and why `ties.py` (finding 3) fails.

**5. MAJOR: the T03-g environment inventory is inaccurate, and the causal step is an inference.** `:35`.
(a) "No package in `.venv` has changed since 2026-08-12 except pytest" is wrong in two ways. First, iniconfig, pluggy and pygments were also installed on 2026-10-13. Second, `.venv/bin/python3.14` is a symlink to `/opt/homebrew/opt/python@3.14/bin/python3.14`. `pyvenv.cfg` records 3.14.6, but the interpreter now runs **3.14.8** (Cellar: 3.14.7 on 2026-09-07, 3.14.8 on 2026-10-06). The "August venv" is therefore not intact, which matters for §6.8's environment labelling.
(b) The mtime argument checks out, and it is stronger than written. The stored mean AP is 0.748396 (quoted as 0.7484 in `experiments/miml_pfn/PREREGISTERED.md:14`, mtime 18:22:09), while the rerun gives 0.748021. The quote therefore reflects the stored row, which existed before `run_foundation_baselines.py`'s last edit at 18:23:03, and the runner skips cached keys.
(c) That the final edit is *what* changed folds 8 and 9 remains unproven. The interpreter upgrade is a low-plausibility alternative, and so is the loader edit of 2026-10-05: `miml_dataset_cv.py` was modified on 10-04 *and* 10-05, while `legacy.py` reverts only the clamp. I found supporting evidence the write-up could add: `miml_clam/data/__pycache__/miml_dataset_cv.cpython-313.pyc`, compiled from the 2026-03-16 source, has the same functions and names as today's file, with `normalize_features` differing only in the clamp.
*Fix:* list all four packages and the interpreter change (3.14.6 → 3.14.8). Add the stored-0.7484 vs rerun-0.7480 comparison and the March pyc as evidence. Phrase the cause as "the stored row predates the final script; the most likely cause is that last edit, which cannot be recovered; the interpreter changed 3.14.6 → 3.14.8 and is not excluded". Label the stored rows accordingly.

**6. MINOR: T03-c numbers are misreported, and the cause was asserted without evidence.** `:10` "max |ΔAP| 2.0e-4" and `:32` "2e-4 (fold 4)": the JSON value is **1.65e-4** (fold 4; fold 0 is 1.20e-4). "2.0e-4" claims a precision the number does not have. The tie attribution is correct (R8: the LAMDA convention reproduces the authors' AP and Coverage exactly on folds 0 and 4), but no evidence for it is archived.
*Fix:* write 1.7e-4. Add a small script under `diagnosis/` that rescores the MIMLNN dumps with the LAMDA convention and shows 0.0.

**7. MINOR: T03-g "each differ by one bag", and the missing TabPFN half.** `:14`. Fold 8's HL Δ is 0.002 = 2 of 1000 label cells. That is consistent with one bag, but nothing per-bag was dumped to show it. §6.8 T03-g also has a TabPFN part, which is not mentioned.
*Fix:* say "consistent with a single bag" or dump per-bag predictions for folds 8 and 9. Add a row or note: "T03-g TabPFN part: pending, task T04".

**8. MINOR: an over-general agreement claim.** `:27` "Methods with continuous scores (DMIMLkNN, MIMLMAPkNN) agree to about 1e-3 under all three rules". This holds for OE, RL and AP, but Coverage differs by 0.069 (= 2/29: 9.9655 / 9.8966 / 9.9310).
*Fix:* restrict the claim to OE, RL and AP, and give the Coverage spread.

**9. MINOR: the bias direction is overstated, and one line is stale.** `:28` "biased in favour of our method". This is uniformly true for RankingLoss (sklearn counts a tied pair as a full error). It is not uniform for OneError, where `argmax` takes the first index: MIMLBRkNN OE is 0.138 under the preregistered scorer vs 0.172 tie-neutral, which favours the baseline. `:29` "Decision needed: D-T03b, below" is stale, because the decision is recorded at `:39`.
*Fix:* "biased, mostly in our favour (always for RankingLoss; OneError, Coverage and AP depend on label order)". Change `:29` to "Decided: D-T03b, below".

**10. MINOR: ProbeDump hygiene, and the proof's coverage.** `diagnosis/ProbeDump.java:1-35`: the header comment is PredictDump's verbatim and does not mention the `--probe` option. `:20` checks byte-identical predictions for 2 methods only. I extended the check to all 7 (R3).
*Fix:* add a two-line header describing `--probe 1`, and state "all 7" with evidence (the p0/p1 meta files for the remaining 5).

## Summary
The two technical diagnoses hold up under independent reproduction. The probe reproduces the library run to 0.0 for all 7 methods. Mulan-rank rescoring reproduces Mulan in-process to ≤ 1.1e-16. The T03-c tie cause holds, and the T03-g mtime argument holds. But Cause 1 is attributed to Mulan when the write is in KDIS (`MIMLClassifier.java:154`). The manuscript consequence claims "every fold" when the count is 90/105 folds, and gives no quantification even though corrections reach about ±0.005–0.007 AP per method on Letter Frost and Birdsong. The cited `ties.py` does not produce the cited 0.0. The `.venv` inventory omits an interpreter upgrade.

VERDICT: NOT RESOLVED — 10 findings
