# T03 checks a–g: results (PREREGISTERED.md §6.8)

Status: **RESOLVED** (review 4, `reviews/T03CHECKS__review_4.md`: "RESOLVED, 100%"). C-queue step 1, run 2026-10-13 after the deposit (`https://doi.org/10.5281/zenodo.23341630`, commit `9b17f00`). D-T03b was decided 2026-10-13: tie-neutral scoring, `experiments/revision_r1/AMENDMENT.md` A1.

The checks and tolerances are fixed in §6.8; this file only records their outcomes. Raw outputs are in `../evidence/T03__checks/`: `T03-<x>__<dataset>.json`, run logs, `diagnosis/` (scripts, archived inputs and dumps, and `reproduced/`, which the scripts regenerate), and `probe_correction/`.

| check | dataset | outcome | file |
|---|---|---|---|
| T03-a KDIS determinism | Letter Frost, 5×5 r0 f0 | **PASS**: all 7 methods byte-identical over two runs. No KDIS method is repeated; the §1.3 fallback is not triggered | `T03-a__letter_frost.json` |
| T03-b KDIS dump fidelity | same | **REPORT**: differences > 1e-3 on every method. Two causes, both reproduced from archived inputs (below) | `T03-b__letter_frost.json`, `diagnosis/reproduced/t03b_reproduced.json` |
| T03-c MIMLNN scoring agreement | Letter Frost, 5 folds of r0 | **REPORT**: HL, OE and RL agree exactly. Max \|ΔAP\| = 1.7e-4 (fold 4; fold 0 1.2e-4). Coverage differs by 2/29 = 0.069 on fold 0. Cause: the tie convention, reproduced exactly (below) | `T03-c__letter_frost.json`, `diagnosis/reproduced/t03c_reproduced.json` |
| T03-d distance cache | — | not applicable: no cache is used | `T03-d__letter_frost.json` |
| T03-e Octave seed control | Letter Frost | **PASS**: seed 0 run twice is identical, and seed 1 differs | `T03-e__letter_frost.json` |
| T03-f scorer agreement | Letter Frost labels, 1000 uniform matrices | **PASS**: max \|ΔAP\| vs Mulan 5.8e-4, vs LAMDA 0.0 | `T03-f__letter_frost.json` |
| T03-g logreg reproduction | Scene, canonical 10CV | **FAIL** at the 1e-9 tolerance. Folds 0–7 are exact (0.0). Folds 8 and 9 differ, consistent with a single bag each (max 0.005 = 1/200 OneError; fold 8 Hamming 2/1000 cells). Cause below | `T03-g__scene.json` |
| T03-g TabPFN part | Letter Frost, MPS | **pending**: task T04, at the C-queue tail (§6.8) | — |

## T03-b, cause 1: KDIS writes into the bag it is asked to predict, and Mulan's probe passes it the real test bag 0
- **Where the write is.** KDIS `MIMLClassifier.makePrediction` runs `instance.setValue(labelIndices[labelIndices.length - 1], 1);` (`external/MIML/mavenProject/src/main/java/miml/classifiers/miml/MIMLClassifier.java:154`) on every call. The method is `final` in that base class, so every KDIS MIML classifier does it; the T03 reviewer confirmed the same statement in the shipped jar's bytecode.
- **What triggers it.** Mulan 1.5 `Evaluator.evaluate(learner, test, train)` first calls `prepareMeasures`, which calls `learner.makePrediction(mlTestData.getDataSet().instance(0))` on the **uncopied** test bag 0 (`mulan/evaluation/Evaluator.java:210`, in `mulan-1-5-0-sources.jar`). The write therefore lands on the real bag 0 and changes its last label to 1 for the rest of the run. In the main evaluation loop (`Evaluator.java:124-129`), each bag is first copied with its labels set to missing. The write lands on that copy, which is why predictions are unaffected.
- **Proof, for all 7 methods** (`diagnosis/reproduce_t03b.py` → `reproduced/t03b_reproduced.json`, from the archived fold `diagnosis/t03b_fold/`). `ProbeDump.java` is PredictDump plus that one probe call (`--probe 1`).
  - With and without the probe, predictions are byte-identical.
  - With the probe, ProbeDump equals the library's own run (RunAlgorithm + EvaluatorHoldout) on all five metrics, max difference 0.0.
  - Without it, ProbeDump equals PredictDump, 0.0.
  - `TruthProbe.java` shows bag 0 `…0000000` → `…0000001` after one `makePrediction`, with bag 1 unchanged.
- **Consequence for our harness:** none. PredictDump never passes an uncopied bag, so the deposited §1.5 design (score from dumped predictions, with the library report as a check only) is correct.
- **Consequence for the submitted manuscript.**
  - Every submitted KDIS number came from the library's own report. `experiments/kdis/run_kdis_baselines.py` runs RunAlgorithm → EvaluatorHoldout (`EvaluatorHoldout.java:129`, the 3-argument `evaluate`), which runs the probe. ProbeDump with the probe reproduces all 2 940 stored per-fold rows of both submitted KDIS files exactly (`probe_correction/`; tuned sweep and shipped defaults).
  - The ground truth changes only in folds where test bag 0's last label is 0. That is **90 of 105 submitted folds**: Scene 7/10, Reuters 8/10, Emotions 4/10, Letter Frost 4/5, Birdsong 9/10, Yeast 10/10, MSRC v2 5/5, Letter Carroll 5/5, Azotobacter 10/10, Geobacter 10/10, Haloarcula 9/10 and Pyrococcus 9/10 (`probe_correction/count_affected_folds.py`). In each affected fold, exactly one bag-label cell is wrong.
  - The size of the effect on every dataset, metric and configuration, and whether any submitted win, loss or best-configuration choice changes, is in **"Effect on the submitted KDIS numbers"** below.

## T03-b, cause 2: tie conventions (same outputs, same truth)
- **Mulan's rule.** `MultiLabelOutput.ranksFromValues` → `weka.core.Utils.stableSort`. Values within `Utils.SMALL = 1e-6` of the **first** value of a run count as tied, and the tie is broken by label index, the later label ranking higher. `tie_neutral_metrics.ranking_four_mulan` implements this rule together with Mulan's bag conventions. On the dumped scores, it reproduces PredictDump's in-process Mulan measures to ≤ 1.1e-16 for **all 7 methods** (`reproduced/t03b_reproduced.json`, `max_abs_mulan_reimpl_minus_inprocess`).
- **Why the 1e-6 tolerance matters, and only for MIMLIBLR.** `WekaSort.java` calls the Mulan function from Java. For MIMLIBLR, all 29 of its score rows contain a near-tie (0 < gap < 1e-6, from saturated logistic outputs), so Weka's ranks differ from an exact stable sort on all 29 rows. For the other six methods, 0 rows differ. `mulan_ranks` agrees with Java on every row of every method.
- **`miml_metrics.py` has no single tie rule.** OneError uses `np.argmax` (the first tied index). Coverage and AP use `np.argsort` (an implementation-defined order). RankingLoss is `sklearn.label_ranking_loss`, which counts every tied relevant–irrelevant pair as a full error.
- **Size** (`diagnosis/tie_neutral_on_letter_frost_f0.txt`, closed forms; columns: deposited | Mulan | tie-neutral A1):
  - MIMLkNN (scores exactly {0, 1}): RankingLoss 0.659 | 0.371 | 0.335.
  - MIMLBagging (5 distinct values): RankingLoss 0.492 | 0.324 | 0.299.
  - DMIMLkNN and MIMLMAPkNN (continuous scores): OE, RL and AP agree to about 1e-3 under all three rules, but Coverage spreads by up to 0.069 (DMIMLkNN 9.966 | 9.897 | 9.931).
- **Direction.** RankingLoss under the deposited rule is always at least the tie-neutral value, so tie-heavy baselines are penalised. That favours an untied method such as ours. On OneError, Coverage and AP the deposited value depends on label order, and its direction varies by method; for example, MIMLBRkNN's OneError is 0.138 deposited but 0.172 tie-neutral, which favours the baseline. So the deposited rule is biased mostly in our favour: always for RankingLoss, while for the other three it depends on label order.
- **Superseded:** an earlier `ties.py` and `tie_analysis.json` used an exact stable sort without Weka's 1e-6 tolerance, and a Monte-Carlo estimate for tie-neutral Coverage and AP. Both were removed in round 2. `reproduce_t03b.py` replaces them.

## T03-c
All five folds agree with the authors' own LAMDA scoring on HL, OE and RL. `diagnosis/reproduce_t03c.py` rescores the archived MIMLNN dumps of folds 0 and 4 (`diagnosis/t03c_dumps/`).
- The archive equals the T03-c JSON on all five metrics (0.0).
- Ranking with MATLAB's stable ascending sort, where the later label ranks higher in a tie, reproduces the authors' AP and Coverage exactly (0.0). All 29 test bags of fold 0 and 28 of fold 4 have tied scores.
- The deposited scorer's differences (AP 1.2e-4 and 1.7e-4, Coverage 0.069 on fold 0) are therefore the tie convention.

## T03-g: cause
- **What it is not:**
  - The rerun is deterministic: pinned and unpinned runs are identical (`diagnosis/g_rerun_{pinned,unpinned}.json`).
  - It is not the 2026-10-04 std-clamp change to the shared loader. `diagnosis/legacy.py` restores the old clamp and gives the same folds 8–9 difference (`g_rerun_legacy_std.json`). Today's `miml_dataset_cv.py` was modified on 2026-10-04 and 2026-10-05. The cached `miml_clam/data/__pycache__/miml_dataset_cv.cpython-313.pyc` (2026-07-14, compiled from the March source) has the same functions and names as today's file, and its `normalize_features` differs only in the clamp (T03 review 1, R10).
- **Environment.**
  - Packages: `.venv`'s numpy 2.5.2, scipy 1.18.0, scikit-learn 1.9.0 and torch 2.13.0 were installed on 2026-08-12. Since then, only pytest, iniconfig, pluggy and pygments were added (2026-10-13), none of them imported by the runner.
  - Interpreter: **the interpreter did change.** `.venv/bin/python3.14` is a symlink to Homebrew's `python@3.14`. `pyvenv.cfg` records 3.14.6, but it now runs **3.14.8** (Homebrew: 3.14.7 on 2026-09-07, 3.14.8 on 2026-10-06; the 3.14.6 build is no longer installed). `uv` has no 3.14.6 build for macOS arm64, so the August interpreter cannot be restored to test this.
  - macOS is unchanged since 2026-07-16 (26.5.2).
- **What the timing shows.**
  - The stored row's mean AP is 0.748396. `experiments/miml_pfn/PREREGISTERED.md` (mtime 2026-08-14 18:22:09) already quotes it as 0.7484, while the rerun gives 0.748021.
  - `run_foundation_baselines.py` was last modified at 18:23:03, and the runner skips any `dataset/config` key already in its output file.
  - **The stored row therefore predates the final script.** The most likely cause is that last edit, which cannot be recovered because the project had no version control then. The interpreter change (3.14.6 → 3.14.8) is less plausible but not excluded.
- **§6.8 rule applied:** a fail is reported, and stored rows are labelled by environment: "August run (Python 3.14.6, pre-final script)" vs "recreated (Python 3.14.8)". No stop.

## Effect on the submitted KDIS numbers (T03-b cause 1)
**Scope: both submitted KDIS results files.**
- `results/kdis_tuned_baselines.json`: 12 datasets × 21 configurations, 2 205 per-fold rows.
- `results/kdis_published_baselines.json`: the 7 methods at their shipped defaults, 84 configurations, 735 rows.

The paper's "best published" comparator is the best over **tuned + defaults + LAMDA MIMLNN** (`make_tables.py:54-56`, `best()`). MIMLNN was scored by the authors' own code, so the probe does not affect it.

**Method.**
- ProbeDump ran on the submitted ARFF folds twice per (configuration, fold): with `--probe 1`, which must reproduce the stored row, and with `--probe 0`, which gives the corrected value. Both are scored by the same Mulan measures, so only the corrupted ground truth differs.
- Scripts: `probe_correction/quant.py`, with one output file per concurrent writer: `quant_<ds>[__<algo>].json` for the tuned sweep and `quantdef_<ds>__<algo>.json` for the defaults. Then `build_corrected.py` and `count_affected_folds.py`.
- Provenance of the quant files:
  - Letter Frost and Birdsong (tuned) are the T03 round-1 reviewer's outputs, imported unchanged. They come from an earlier `quant.py` with ProbeDump bytecode identical to `build/ProbeDump.class` except for the class-file version.
  - MSRC v2 and parts of Scene, Reuters and Emotions (tuned) ran serially, 13:43–13:57 UTC.
  - The rest of the tuned sweep ran 13:57–16:30 UTC, 7 jobs in parallel.
  - The defaults ran 17:07–17:56 UTC, 7 in parallel.
  - Every file passes the same p1 = stored check.

**Reproduction.** `--probe 1` equals every stored per-fold row of both files, 2 205 + 735 = **2 940 rows**, on all five metrics, with maximum difference **0.0** (`effect_summary.json`, `tuned` / `defaults`). Every submitted KDIS number is therefore exactly the library's probe-affected value.

**Size against the paper's comparator** (`effect_summary.json` → `paper_best`: corrected minus submitted value of the best published arm; * = the comparator arm changes):

| dataset | folds changed | AP | HL | OE | RL | Coverage | AP comparator |
|---|---|---|---|---|---|---|---|
| Scene | 7/10 | +0.0001 | −0.0007 | +0.0005 | −0.0010 | −0.010 | MIMLIBLR MaxH |
| Reuters | 8/10 | 0 | 0 | 0 | 0 | 0 | MIMLNN (all five metrics) |
| MSRC v2 | 5/5 | +0.0010 | −0.0004 | 0 | 0 | 0 | MIMLIBLR AveH |
| Letter Frost | 4/5 | +0.0013 | −0.0011 | 0 | −0.0015 | −0.057 | MIMLMAPkNN AveH |
| Letter Carroll | 5/5 | +0.0021 | −0.0012 | 0 | −0.0032* | −0.279* | MIMLDGC AveH |
| Birdsong | 9/10 | +0.0044 | −0.0019 | 0 | −0.0046 | −0.140 | MIMLDGC AveH |
| Emotions | 4/10 | +0.0002 | −0.0011 | 0 | −0.0006 | −0.007 | MIMLDGC MaxH |
| Yeast | 10/10 | +0.0003 | −0.0003 | 0 | −0.0008 | −0.031 | MIMLIBLR MaxH |
| Prot. Haloarcula | 9/10 | 0 | −0.0014 | 0 | −0.0108 | −0.333* | MIMLNN |
| Prot. Pyrococcus | 9/10 | +0.0045 | −0.0004 | 0 | −0.0024 | −0.162 | DMIMLkNN MinH |
| Prot. Geobacter | 10/10 | +0.0100 | −0.0010 | 0 | −0.0055 | −0.062* | DMIMLkNN AveH |
| Prot. Azotobacter | 10/10 | +0.0129 | −0.0005 | 0 | −0.0083 | −0.568 | DMIMLkNN AveH |

Where MIMLNN or an unaffected arm is the comparator, the paper-level effect is 0. That covers Reuters on every metric, Haloarcula AP, and MSRC v2 RL and Coverage. `effect_summary.json` also holds the best-of-21-tuned view (`tuned_best`) for reference.

- **Direction.** Against the paper's comparator, the best published value improves on **41** of 60 dataset-metric pairs, is **unchanged on 18** (all of OneError except Scene, plus the MIMLNN cells above), and is **worse on 1** (OneError on Scene, +0.0005). Of the 21 tuned configurations alone: 48 improve, 10 are unchanged and 2 are worse.
  - **Why OneError behaves differently.** The probe only ever turns a 0 label into a 1. That can make the top-ranked label relevant, but never irrelevant, so under the bug OneError could only stay the same or look better.
  - **The other four metrics.** For AP, HL, RL and Coverage, the bug made the published baselines look worse, and it therefore favoured our method. The paper-level AP effect is up to 0.013 on Azotobacter and 0.010 on Geobacter, 0.0045 on Pyrococcus, 0 on Haloarcula, and 0–0.0044 on the eight evaluated datasets.
  - For individual configurations the change goes both ways (e.g. MIMLkNN on Letter Frost, AP −0.0047).
- **Best-configuration choice** changes in 2 of 60 tuned-only cases (Letter Carroll, Coverage and RankingLoss) and in 4 of the paper's comparator cells (marked *: Letter Carroll RankingLoss and Coverage, Geobacter Coverage, Haloarcula Coverage).

**Effect on the submitted manuscript.**
- **How this was computed.** `build_corrected.py` runs `paper_ieee_access/make_tables.py` in two copies of the project. In the second copy, **both** corrected files are swapped in. The first copy, on the stored results, reproduces every committed table byte for byte. Outputs: `tables_stored/`, `tables_corrected/`. The full diff is in `tables_diff.txt` (every changed table cell and macro).
- **Unchanged:**
  - AP vs best published: 6 win / 0 tie / 2 loss.
  - HL: 1 / 3 / 4.
  - The pre-registered rule: 3 of 4 credited, 6 qualifying.
  - Table VI: the same 7 of 8 pass Holm, and Emotions still fails.
  - Reuters' AP margin, +0.0097, because MIMLNN is the comparator.
- **AP margins** (ours − best published):

  | dataset | submitted | corrected |
  |---|---|---|
  | MSRC v2 | +0.1265 | +0.1255 |
  | Letter Frost | +0.0744 | +0.0732 |
  | Letter Carroll | +0.0620 | +0.0599 |
  | Yeast | +0.0115 | +0.0112 |
  | Emotions | +0.0093 | +0.0091 |
  | Scene | −0.0571 | −0.0572 |
  | Birdsong | −0.0562 | −0.0606 |

- **HL margins:**

  | dataset | submitted | corrected | note |
  |---|---|---|---|
  | MSRC v2 | +0.0181 | +0.0177 | |
  | Letter Frost | −0.0093 | −0.0104 | |
  | Letter Carroll | −0.0103 | −0.0114 | |
  | Yeast | +0.0043 | +0.0040 | tie; comparator is the default MIMLBRkNN, 0.1968 → 0.1965 |
  | Emotions | −0.0020 | −0.0031 | tie |
  | Scene | −0.0252 | −0.0259 | |
  | Birdsong | −0.0192 | −0.0211 | comparator is the default MIMLDGC, 0.0739 → 0.0720 |

- **Table VI:**
  - Emotions: t +1.71 → +1.66, p 0.122 → 0.132 (`\tEmoAP`, `\pEmoAP`).
  - Birdsong: t −4.02 → −4.59.
  - MSRC v2: t +12.04 → +12.65.
  - Letter Frost: t +5.86 → +5.89.
  - Letter Carroll: t +5.07 → +4.86.
  - Yeast: t +8.33 → +8.16.
  - Scene: t −10.07 → −10.28.
- **Not-evaluated table:**
  - Geobacter: −0.0304 → −0.0405.
  - Azotobacter: −0.0153 → −0.0281.
  - Pyrococcus: −0.0177 → −0.0222.
- **Macros:**
  - `\reutersKdis`: 0.8941 → 0.8946.
  - `\haloKdis` (a default, DMIMLkNN): 0.5843 → 0.5934.
  - `\sceneIBLRMax/Ave/Min`: 0.8782/0.8770/0.8772 → 0.8784/0.8774/0.8776.
  - Every KDIS row of `tab_full`.
- **Changed counts (neural context only, not a claim about the paper's method):**
  - Neural models vs published: 4 win / 0 tie / 8 loss → 3 / 1 / 8.
  - Neural models vs KDIS only: 6–6 → 5–6.
  - Cause: Geobacter's best published rises to 0.5817, equal to the neural value within the tie band. The relevant defaults are now corrected, so these counts are final for the submitted protocol.
- **A misstatement in the submitted manuscript (R1-M08).** `main.tex:1192` says "Every number in this paper is from the tuned sweep". That is false. The best-published pool also includes the shipped-default runs, and three reported cells came from them: Birdsong HL (MIMLDGC), Yeast HL (MIMLBRkNN) and `\haloKdis` (DMIMLkNN). The "+0.027 to +0.034" AP gain from defaults to tuned (`main.tex:1190-1191`) is wrong on two counts. No submitted script regenerates it, and `probe_correction/defaults_to_tuned_gain.py` (→ `defaults_to_tuned_gain.json`; best tuned minus best default, KDIS only) shows the range holds only for three datasets: MSRC v2 +0.0319, Letter Frost +0.0276 and Letter Carroll +0.0337.
  - Across all 12 datasets, the submitted gain runs from **−0.0064** (Haloarcula, where the best default beats every tuned configuration) to **+0.0561** (Reuters).
  - Probe-corrected, those three become +0.0313, +0.0281 and +0.0330 ("+0.028 to +0.033"), and the full range becomes −0.0046 to +0.0557.
  - The revision states the full per-dataset range, not the three-dataset one. The response to R1-M08 states both points, and the revision's description of the baseline pool is explicit about them.
- **Cross-references updated:**
  - The planned R1-M10 / R4-06 C11 sentence used the KDIS MSRC v2 value 0.7434, which is 0.7444 corrected. A note was added to `comments/R1-M10.md` and `evidence/R4-06__claims_audit.md`.
- **Consequence for the revision:** every KDIS number in the revision comes from the harness (PredictDump, no probe) and is unaffected. The response to R1-M08/R1-M10 reports the bug, the 90/105 affected folds, the 2 940-row reproduction, this table, and that no headline verdict changes.

## Decision D-T03b (user, 2026-10-13): how ranking metrics treat tied scores
**Decided: tie-neutral**, the recommended option (DECISIONS.md row "A1 tie-neutral ranking metrics"; `experiments/revision_r1/AMENDMENT.md` A1, which lists the alternatives considered and what had been observed).

## Review log
| round | reviewer file | verdict |
|---|---|---|
| 1 | `reviews/T03CHECKS__review_1.md` | NOT RESOLVED — 10 findings (4 major, 6 minor); all addressed in round 2 |
| 2 | `reviews/T03CHECKS__review_2.md` | NOT RESOLVED — 7 findings (3 major, 4 minor); all addressed in round 3 (defaults corrected, paper-comparator table, counts, full diff) |
| 3 | `reviews/T03CHECKS__review_3.md` | NOT RESOLVED — 3 minor findings; addressed in round 4 (comparator-cell count 4, defaults-to-tuned gain recomputed over all 12 datasets, status line) |
| 4 | `reviews/T03CHECKS__review_4.md` | **RESOLVED, 100%** |
