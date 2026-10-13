# Review 2 of `experiments/revision_r1/PREREGISTERED.md` (v2, with §7 power table)

Reviewer role: independent statistician (CV inference, multiple testing) and MIML practitioner; did not write v1, v2, the power script or review 1. Checked against: v2 and `power_table.py`; `PREREG__review_1.md`; the 14 comment files named in the brief; `experiments/miml_pfn/{PREREGISTERED,AMENDMENT}.md`; `run_foundation_baselines.py` (`splits_for`, `tr[:v]`); `miml_clam/data/miml_dataset_cv.py::get_cv_splits`; `experiments/kdis/{mat_to_arff,run_kdis_baselines}.py`; `results/foundation_baselines.json`; `results/provenance_bag_rows_*.csv`; `revision_access_44676/evidence/T01__*`; `tasks/` (holds only `T01-provenance-audit.md`; **no `T10-gpu-arms.md`, no T03**).

Three computations frame the findings. All reproducible from the named files.

**(a) Power-table algebra — verified.** Recomputed independently: single 10-fold, m = 16: t_crit(0.05/16, df 9) = 3.997, factor √(1/10 + 0.1389) = 0.4888, d_z,min = 1.954; power at d_z = 2 via noncentral t with ncp = 2/0.4888 = 0.565. Repeated 5×5, m = 16: t_crit(df 24) = 3.285, factor 0.5937, d_z,min = 1.950. Repeated 5×10: d_z,min = 1.239. Single 5-fold, m = 16: 6.364 × 0.7159 = 4.556. Every spot-checked cell in §7 A1/A2 agrees to the printed precision; `power()` sums both tails correctly; `rho()` matches §1.6. A 40 000-draw Monte Carlo with equicorrelated fold differences whose Var(d̄) equals the corrected variance gives Type-I 0.067 at nominal 0.05 and power 0.52 at d_z = 1 (table: 0.447) — the table is a fair approximation and the test is, as v2 already says, approximate and slightly liberal.

**(b) H2-B is not estimable as written.** From `provenance_bag_rows_*.csv` and the canonical `*_10CV.mat` folds, the fraction of training bags that share at least one source example with at least one test bag is:

| dataset | train bags | leak-purge fraction (mean, min–max over folds) | training bags left |
|---|---|---|---|
| Emotions | 534 | 0.897 (0.873–0.919) | ~55 |
| Yeast | 2176 | 0.906 (0.876–0.921) | ~205 |
| Medical | 881 | 0.969 (0.953–0.978) | ~27 |
| Corel5K | 4386 | 0.987 (0.982–0.993) | ~55 |

All four exceed v2's own 80 % threshold, so every H2-B row is "not estimable", the H2 family is empty, and the H2 decision rule has no inputs. The instance-level variant (remove from each training bag the rows whose source example occurs in any test bag) removes 0.468 / 0.457 / 0.628 / 0.675 of training instance rows and empties only 6.4 / 5.7 / 12.8 / 8.3 % of bags — that version is estimable.

**(c) Global Wilcoxon power.** The eight observed dataset-level mean ΔAP (+0.1265, +0.0744, +0.0620, +0.0115, +0.0097, +0.0093, −0.0571, −0.0562) have mean +0.0225 and SD 0.063 (d ≈ 0.36). Drawing 12 or 16 dataset deltas from that distribution, the two-sided Wilcoxon signed-rank test at α = 0.05 rejects in 18 % / 24 % of draws. The confirmatory global test is underpowered under the heterogeneity already observed, and §7 does not say so.

---

## Part 1 — Were the 26 round-1 findings resolved?

| finding | status | note |
|---|---|---|
| F1 | resolved | §1.2 repeated CV where no canonical split binds, reason stated; power table appended. Reason for 5×5 rather than R1's 10×10 not stated (m7). |
| F2 | resolved | families named; Wilcoxon global test added. Its power and sidedness are new gaps (M2). |
| F3 | resolved | ddof, n₁, d_z named, NS ≠ tie. d_z,corr naming (m1). |
| F4 | resolved | inner 5-fold, degenerate training labels, optimism diagnostic, `tr[:v]` disclosed. (Scoring-side degenerate labels are moot: the four ranking metrics are example-based and `miml_metrics.py` skips bags with no positive label.) |
| F5 | resolved | option (b), declared handicap, n₁ = 0.8× enters ρ. |
| F6 | resolved | 0.5-threshold sensitivity row; "AP involves no selection" stated. |
| F7 | resolved | tie-break order fixed. |
| F8 | resolved | 5 Octave seeds, mean over seeds, KDIS determinism check with fallback. |
| F9 | resolved | grid in file. |
| F10 | **not resolved** | B3: no absolute cap, device not in this file, "did not complete" undefined for Java/Octave arms. |
| F11 | conditional | rebuilt-set arms are "inside the T10 budget" — T10 does not exist (B3). |
| F12 | **not resolved** | H2-A is fine; H2-B as specified yields an empty family (B1). |
| F13 | partial | overlap quantities listed; release of procedure and mapping not committed (m4). |
| F14 | resolved | ties, duplicates. Remainder bags unassigned (M6). |
| F15 | resolved | |
| F16 | partial | cap and wording present; hardware-sensitivity flag and same-device pairing absent (M7). |
| F17 | partial | d′ = 500 fixed; 72 h threshold device-dependent and ordering not committed (B3, m8). |
| F18 | resolved | §0 table. |
| F19 | partial | CI gate present; whether `bagmean_card` is run on constant-size sets, and which CI, unstated (m5). |
| F20 | partial | Smooth-AP decided, family defined; ABMIL/MLP recipe and pairing unit still missing (M1). |
| F21 | partial | PENDING is acceptable; deposit list omits the two original `miml_pfn` files (m3). |
| F22 | resolved | |
| F23 | resolved | |
| F24 | resolved | |
| F25 | resolved | (m12 extends it.) |
| F26 | resolved | VOC2012 + HJA; VOC's definition is incomplete (M5). |

Genuinely resolved: 17. Partial: 7. Not resolved: 2 (F10, F12).

## Part 2 — Findings on v2

### BLOCKERS

**B1. H2-B produces an empty family; the confirmatory leakage test cannot run as written.**
Computation (b) above: the bag-level leak purge removes 90–99 % of training bags on all four constructed sets, so the pre-registered ">80 % = not estimable" clause excludes every row. R2-03's "quantify … and evaluate using groups" and R6-M01's leakage request are then answered only by H2-A, which (as v2 concedes in F12's logic) changes the datasets as well as removing leakage.
*Fix.* Replace the bag-level purge with an instance-level purge, defined on source-example indices (the same unit as the overlap quantification): in each outer fold, delete from every training bag each instance row whose source example occurs in any test bag; a bag left with zero rows is dropped. **Control:** for each training bag, delete the *same number* of rows chosen uniformly at random among that bag's rows (`numpy.random.default_rng(seed)`, seeds {0, 1, 2}); bags emptied by the leak purge are dropped in the control too. This matches bag count, instance count and per-bag cardinality exactly, so the contrast isolates *which* rows were removed. Report the bag-level purge fractions above as the descriptive statistic they are. Keep a not-estimable clause, now on instance rows (e.g. > 80 % of training rows); none of the four trips it. State that n₁ in ρ is the mean post-purge training bag count. Re-word the interpretation: removing the test fold's neighbourhood also removes legitimately similar, distinct examples, so a positive effect is an *upper bound* on leakage inflation, not leakage alone.

**B2. The nested published library is not feasible on VOC2012 (and is unbudgeted everywhere), and "did not complete" is undefined for Java/Octave arms.**
§6's projection method ("3 labels × 2 fits") exists only for TabPFN. KDIS and MIMLNN recompute Hausdorff distances inside every run. On VOC2012 (11 540 bags × 16 instances × 128-d after PCA) one distance pass is ~6.7 × 10⁷ bag pairs × 256 instance pairs; nested selection is 10 outer × 5 inner × 84 configurations = 4 200 KDIS runs plus 10 refits, and MIMLNN adds 9 configs × 5 seeds × 5 inner × 10 outer = 2 250 Octave runs each containing a k-medoids over thousands of bags. That is thousands of device-hours with no rule governing it; the same applies, at smaller scale, to the rebuilt and purged Corel5K/Medical arms. When it stalls, the H1 family size and the VOC row will be decided by judgement after data are seen.
*Fix.* (i) Define a measurement and cap for baseline arms as §6 does for TabPFN: time inner fold 0 of outer fold 0 for each (method, distance, k); projected = per-run time × run count; cap stated in hours. (ii) Fix a reduced VOC grid *now*: inner 3-fold; distance ∈ {AveH, MaxH}; k ∈ {10, 20}; MIMLNN ratio ∈ {0.2, 0.4}, λ = 1, seeds {0, 1}. (iii) If the harness permits precomputing one Hausdorff matrix per (distance, outer fold) and reusing it across k and methods, say so; that is caching, not retuning. (iv) State that a baseline arm that cannot complete under the cap makes the dataset "library did not complete" and that the row is then excluded from F-H1-primary and reported with hours spent, exactly as for TabPFN arms.

**B3. The 72 device-hour PCA rule and the 3× stop rule are not an executable budget.**
(a) `tasks/T10-gpu-arms.md` does not exist and this file does not say which arms run on MPS and which on the GPU; "72 device-hours" trips or does not trip depending on an unrecorded device choice (MPS vs a datacentre GPU differ 5–10×). (b) The only stop rule is relative: 3× the projection. For the proteins (~328 h projected) that is a 984-hour cap; F10 asked for a wall-clock cap per dataset. (c) After a PCA switch that is a no-op (Corel5K bag-mean, d = 499 ≤ 500, projected ≈ 260 h at the measured Reuters rate), nothing happens: the arm simply runs under the 3× rule. (d) Arms are measured one at a time; if bag-mean is measured and run first, a later multiview projection > 72 h retroactively requires rerunning bag-mean under PCA.
*Fix.* Name the GPU (model, memory) in this file now, or list the admissible devices and commit that the projection is measured on the device actually used and both are logged before the run continues. Add an absolute per-(dataset, arm) cap (e.g. 120 device-hours *after* any PCA) above which the arm is "not attempted", recorded before starting, and a total budget for the revision. Measure every arm's projection on a dataset before running any arm on it. State the result for a post-PCA projection above the cap (not attempted; dataset excluded from the family; stated in the manuscript with the projection).

### MAJOR

**M1. H5 is not pre-registered as a training protocol.** The bag-mean MLP and ABMIL-multilabel recipe (architecture widths, optimiser, learning rate, batch size, epochs, early-stopping signal and patience, model selection) is absent; with five surrogates of different scale, per-surrogate tuning after the fact is a forking path, and R1-M08 sub-request 6 asks for exactly these details. The pairing unit of the cross-evaluation test with 3 seeds × k folds is unspecified (F20 asked). Which split MSRC v2 and Letter Frost use in H5 (new 5×5 or submitted seed-42) is unspecified.
*Fix.* Write the recipe once for both models and all surrogates (same optimiser, LR, epochs, early stopping on the surrogate's own validation loss with the `tr[:v]` validation split, patience fixed). Pairing unit = outer fold, with the seed-mean as the fold value (n = k, df = k − 1); never (seed × fold). Use the §1.2 design (5×5) for MSRC v2 and Letter Frost or say why not.

**M2. The global Wilcoxon test — the confirmatory test of the headline — has no power statement, no sidedness, and pseudo-replicated datasets.** Computation (c): power ≈ 0.18–0.24 at n = 12–16 under the heterogeneity already observed. Four protein sets share feature extraction and construction; two Letter sets share a generator; Birds and HJA Birdsong are two files from one source (T01: zero shared instance vectors, so these two are defensibly distinct). Demšar's test assumes independent datasets. Sidedness is not stated. R2-04 asks for CIs and effect sizes; none is specified for this test.
*Fix.* Two-sided. Add to §7: the power of the global test under (i) the observed 8-dataset distribution and (ii) a sign-consistent alternative. Pre-register a sensitivity analysis collapsing each family to its mean difference (proteins → 1, Letters → 1; Birds and HJA kept separate) with n stated. Report the Hodges–Lehmann median ΔAP with its 95 % CI. Pre-write the abstract wording for "global test not significant; Holm wins on X, losses on Y", since that is the likely outcome.

**M3. Baseline preprocessing is not fixed.** `mat_to_arff.py` writes raw features and `export_folds_mat.py` does not standardise; TabPFN and logreg arms z-score on `fit_i`. R6-M05 asks "how the baselines were preprocessed". The choice matters for Hausdorff distances on Medical (1 449-d, sparse) and on the rebuilt sets.
*Fix.* State now: KDIS and MIMLNN receive raw features exactly as their authors' code expects (and that this is the authors' setting), or z-scored on the outer training fold; one sentence, applied identically to the rebuilt, purged and VOC (post-PCA) variants.

**M4. The library procedure selects across two scorers, and no per-bag predictions are stored.** Inner selection picks "best (method, distance, k) or MIMLNN" by inner AP, but KDIS APs come from the Mulan evaluator and MIMLNN's from the authors' MATLAB; `run_kdis_baselines.py` keeps only report CSVs, so §1.5's "rescoring stored predictions if available" cannot happen and R2-08's "raw fold-level predictions" cannot be released for baselines.
*Fix.* Commit to dumping per-bag scores from both harnesses (KDIS: a prediction-writing report or a small wrapper around `EvaluatorHoldout`; Octave: save `Outputs`/`Pre_Labels`), score every inner and outer fold with `miml_metrics.py`, and release them. If dumping is impossible for a harness, pre-state the tolerance (≤ 1e-3 AP on one dataset, T03) under which native scoring is accepted, and that failing it, the library procedure is split per harness.

**M5. VOC2012 is defined by a dangling pointer.** §0 says "our own feature extraction; provenance in T01", but `T01-provenance-audit.md` does not mention VOC. The backbone, patch grid, image set, 20-label set, the sha256 of `voc2012.mat`, and the reason for choosing it over the sibling files `voc2012seg.mat` / `voc2012segml.mat` in the same directory are all unrecorded; a later switch between the three would be a forking path. PCA-128 is fixed but unmotivated, and multiview on PCA-128 is 769 bag-level features, so §6's d′ = 500 rule can trigger a second PCA — say whether that is intended or multiview runs at 769 with `ignore_pretraining_limits`. (Training rows 0.8 × 0.9 × 11 540 ≈ 8 300 are under TabPFN's 10 000-row limit; state it.) Adding VOC2012 and HJA Birdsong *is* legitimate: `results/*.json` contain no entry for either, nor for `tabpfn_bagmax` / `bagmean_card`; T01 already verifies that `hja_birdsong.mat` matches the published 548/13 statistics.
*Fix.* One paragraph: file hash, extractor, patches, labels, which sibling files are excluded and why, why 128, what happens at 769, and a commitment to release the file with checksums.

**M6. H2-A leaves the remainder bags unassigned and invites a mis-reading.** `get_cv_splits` puts the n mod 10 bags (3 / 7 / 8 / 3) in *every* training set; they have no outer fold, so "partitioned by the outer fold of their bag centre" is undefined for them, and pool size is ⌊n/10⌋, not n/10. Separately, rebuilt bags come from pools 10× sparser than the original construction, so rebuilt absolute APs are not comparable with the "leaky" rows and "leaky − rebuilt" must not be presented as a leakage estimate — that is H2-B's job.
*Fix.* Assign remainder centres to the fold-9 pool (or exclude them from all pools and all bags), state it; write the non-comparability sentence into H1 and H2-A.

**M7. H3's Yeast comparison is cross-device as written.** Yeast multiview runs on the GPU while Yeast bag-mean is the stored MPS result; §6 itself says not to compare across devices within a test if the check fails. F16(ii)'s hardware-sensitivity flag (|margin − 0.006| < 1e-3; Birds is 2e-6 short) is absent.
*Fix.* Rerun Yeast `tabpfn_bagmean` on the GPU (140 fits, d = 103) and evaluate the rule on the GPU pair; add the flag rule; Birds is flagged by construction.

**M8. ρ = n₂/n₁ is under-defined outside MIML-PFN-vs-library tests.** H2-B (purged training sets), H4 (both arms at 80 %), H5 (neural models, 80 %) and library-vs-library contrasts need n₁ stated; the power table hard-codes 0.8 and its "applies to" column reads as if it covered every test.
*Fix.* One rule: n₁ = mean training bag count actually used by the arm with the smaller training set (0.8 × outer training for TabPFN/logreg/neural arms; 1.0 × for KDIS/MIMLNN; post-purge counts in H2-B), recomputed per comparison; label §7 as the MIML-PFN-vs-library table.

### MINOR

**m1.** d_z,corr = d̄ / √(n(1/n + ρ)s²) is algebraically t/√n. Call it that or drop it; it is not a standardised mean difference.
**m2.** §7 B: "the 8 untested rows assumed to rank last, which is the most favourable case" is mislabelled. Ranking last gives the observed rows the *strictest* thresholds that do not depend on untested results; an untested test ranking earlier and failing would stop Holm sooner, so it is neither bound. Write "a scenario; the strictest thresholds not depending on the untested rows".
**m3.** F21: the deposit must include `experiments/miml_pfn/PREREGISTERED.md` and `AMENDMENT.md` with their 2026-08-14/15 dates and the note that they were local files until now; R2-07 asks for the *original* record. The header lists only this file and `experiments/revision_r1/`.
**m4.** R2-03's last sentence (release the construction procedure, source files and observation-to-bag mapping) is not committed anywhere in H2; the `provenance_bag_rows_*.csv` files already exist. Add one line.
**m5.** H4: state that `bagmean_card` is *not run* on constant-size sets and the bag-mean row is reused and labelled (running it is not numerically guaranteed identical through TabPFN's own preprocessing), and that the CI in the interpretation gate is the unadjusted 95 % CI with corrected variance.
**m6.** Add the H4 family (3 arms × 16 ≈ 48) and the H5 per-(dataset, model) families (20) to the power table: at single 10-fold the first-step d_z,min for m = 48 is ≈ 2.3.
**m7.** State why 5×5 rather than R1-M04's 10×10 (nested library cost: 25 vs 100 outer folds × 5 inner × 84 configurations); one sentence pre-empts the obvious reply.
**m8.** F17's ordering: commit that projections and PCA decisions for *all five* R2 datasets are logged before any R2 multiview result is looked at.
**m9.** T03 (determinism of KDIS, MIMLNN scoring agreement) is referenced four times and does not exist; list its checks and tolerances in this file (F9 principle).
**m10.** R6-M08 asks for per-fold SDs in Tables V and VII; add "per-fold SD in every results table" to §1.6 Reporting so it is not forgotten.
**m11.** §6 cross-device check covers bag-mean only; H3 turns on multiview. Add `tabpfn_multiview` on Letter Frost (cheap) to the check.

## Part 3 — Will the named reviewer requests be satisfied?

| comment | after v2 as written | after the fixes above |
|---|---|---|
| R1-M04 (corrected test on repeated CV; revise 7/8; band) | yes where repeated CV is possible; canonical sets justified; band retired | yes |
| R1-M05 (bag-max, bag-mean+card, groups, counts) | yes | yes |
| R1-M08 (selection granularity, like-for-like, "best", neural details, thresholding) | 6 of 7; neural training details missing | yes with M1 |
| R2-02 (nested selection, rerun tests) | yes | yes |
| R2-03 (quantify overlap; rebuild/group; release mapping) | overlap yes; grouped evaluation yes (H2-A); purge contrast dead (B1); release missing (m4) | yes with B1, m4 |
| R2-04 (dependence-aware test, CI, effect sizes, validity, selection) | yes for per-dataset tests; global test lacks CI/effect size | yes with M2 |
| R2-07 (labels, public record, bag-max, failed rule primary) | yes, pending deposit (m3) | yes |
| R2-08 (release everything; larger natural dataset; restrict claims) | dataset yes; predictions for baselines cannot be released (M4); VOC undefined (M5) | yes with M4, M5 |
| R5-03 (selection inside training data) | yes | yes |
| R5-04 (corrected test; Reuters/Yeast care) | yes | yes |
| R6-M01 (leakage; Corel5K analysed; metric; labels) | leakage via H2-A only; Corel5K H2-B not estimable | yes with B1 |
| R6-M03 (define native/constructed; arms) | yes | yes |
| R6-M05 (tune k; preprocessing; thresholding) | k and thresholding yes; preprocessing no (M3) | yes |
| R6-M08 (corrected test; SDs) | test yes; SDs not in reporting list (m10) | yes |

## Part 4 — Executability

A doer following v2 would have to decide by judgement, after seeing data: which device each arm runs on and hence whether PCA applies (B3); what to do when the library stalls on VOC2012 or Corel5K (B2); what to do when every H2-B row is excluded (B1); the neural training recipe and test pairing unit (M1); whether baselines are standardised (M3); where the remainder bags go (M6); n₁ for purged and baseline-only tests (M8); whether to run `bagmean_card` on Scene (m5). Everything else is executable as written.

## Summary

The statistical core of v2 is sound: the corrected test is specified and its power table is numerically correct; the families are named; nested selection, the declared 80 % handicap, the seed policy, the a-priori grouping, the labelling and the H3 completion are what the reviewers asked for. Three things stop it from being a pre-registration one can hand to a doer: the H2-B contrast is empty under its own exclusion rule (confirmed numerically), the compute rules do not bind the arms that will actually run out of time, and the budget depends on a device assignment that is not in the document.

BLOCKER: B1, B2, B3. MAJOR: M1–M8. MINOR: m1–m11.

VERDICT: NOT RESOLVED — 22 findings
