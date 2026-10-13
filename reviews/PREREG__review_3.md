# Review 3 of `experiments/revision_r1/PREREGISTERED.md` (v3, with `power_table.py` and §7)

Reviewer role: independent statistician (CV inference, Nadeau–Bengio / Bouckaert–Frank, Demšar, nested CV, multiple testing, compute budgeting) and MIML practitioner; did not write v1–v3, the power script, or reviews 1–2. Date: 2026-10-13.

Checked against: v3 (662 lines) and `power_table.py`; `history/PREREGISTERED_v2.md` (line diff); `PREREG__review_1.md`, `PREREG__review_2.md`; `STEP1-R2R5__review_1.md`, `_2.md`; `STEP1-R1__review_1.md` F2; `DECISIONS.md` (all rows, especially the three dated 2026-10-13); section 1 of the 14 named comment files; `evidence/T05__power_table.txt`, `T07__tabpfn_2.2.1_defaults.md`; `tasks/T01-provenance-audit.md` (section headers); `results/provenance.json`; `results/provenance_bag_rows_*.csv`; the canonical `*_10CV.mat` files; `experiments/miml_pfn/{PREREGISTERED,AMENDMENT,RESULT}.md`; `run_foundation_baselines.py`, `run_gradient_conflict.py`, `run_mimlnn.m`, `miml_metrics.py`, `miml_dataset_cv.py::get_cv_splits`, `MIMLClassifier.java`; the git log.

## What I re-ran and re-checked

| check | result |
|---|---|
| §7 A1/A2 cells by hand (independent code): single 10-fold m=16, 5×5 m=16, 5×10 m=10, single 5-fold m=16 | t_crit 3.997 / 3.285 / 2.940 / 6.364; d_z,min 1.954 / 1.950 / 1.172 / 4.556; power(d_z=2, first step) 0.565 / 0.543 / 0.978 / 0.084; last-step power(d_z=1) 0.447 / 0.366 / 0.691 / 0.192. All agree with §7 to printed precision. |
| §7 C cells (H2 library f=0.872, H2 TabPFN f=0.698, H4 m=42, H5 5×5 m=20) | d_z,min 2.086 / 2.227 / 2.276 / 2.004; power(d_z=1) 0.062 / 0.051 / 0.043 / 0.068; power(d_z=2) 0.489 / 0.415 / 0.389 / 0.511. Agree. |
| §7 B: t_corr from the printed d_z and k; Holm at m=8 and m=16 on the printed p_corr | t = 7.52 / 3.66 / 5.38 / 3.68 / −6.51 / −2.60 / 1.10 (Reuters prints 3.67, rounding); Holm m=8 passes Scene, Yeast, MSRC v2, Reuters (4/8); m=16 scenario passes Scene, Yeast, MSRC v2 (3/8). Agree. |
| §7 D Wilcoxon Monte Carlo, independent 3 000-draw rerun | n=16: observed 0.366 (table 0.365), normal 0.245 (0.245), sign p=0.9 0.900 (0.898); n=10: 0.262 / 0.173 / 0.724 (table 0.263 / 0.167 / 0.710). Min attainable p 2/2ⁿ = 3.1e-05, 0.002, 0.016: agree. The mean +0.0225 and SD 0.0633 reproduce. |
| `evidence/T05__power_table.txt` vs §7 text | Identical in every row I compared (A, A1, C, B survivors line, D). |
| Header hashes and dates of the three August files | sha256 of `PREREGISTERED.md`, `AMENDMENT.md`, `RESULT.md` match the header table byte for byte; `stat` birth/modified times match. Git: `aceec7b` first commit, v2 archived in `88d50fc`, `experiments/revision_r1/` untracked: all as the header says. |
| §0.1 hashes and sizes | `hja_birdsong.mat` sha256 starts `cc3a2fef…` (full: `cc3a2feffed3…f4c2`); `voc2012.mat` sha256 `f672df5c…a79b0c`, 1 514 140 560 bytes; `voc2012_patch_gt.npz` `3bbc512d…1359`; `voc2012_10CV.mat` `Indexes` == `RandomState(42).permutation(11540)+1`. All true. |
| §0.1 / §0.2 bag and label counts, n mod 10 | Match `provenance.json` structure for all 14 audited files; 593/2417/978/4873 → 3/7/8/3; 257 → 7; proteins 304/425/379/407 → 4/5/9/7. Correct. |
| H2-B descriptive numbers (recomputed from the CSV mappings and the canonical folds) | Instance rows removed 0.468 / 0.457 / 0.628 / 0.675; bags emptied 6.4 / 5.7 / 12.8 / 8.3 %: exactly as §H2-B states. **See B1 for what the same computation shows about the control.** |
| Reuters duplicate share | `provenance.json` `frac_test_bags_identical_to_a_train_bag` = 0.037: the "3.7 %" in H1 is correct. |
| `TabPFNClassifier` defaults (T07) | n_estimators 8, random_state 0, harness passes only `ignore_pretraining_limits=True`: H4's constructor line is the harness's effective configuration. |
| `MIMLClassifier.makePrediction` at line 145 of the KDIS source | Present, `public final MultiLabelOutput makePrediction(Instance)`: the `PredictDump.java` plan is implementable against the unmodified jar. |
| Dembczyński et al. pinpoints | Identical to the verified pinpoints in `STEP1-R1__review_1.md` F2 (§4.1 eq. 13; §4.2 Theorem 1, eq. 18; eq. 20; §5 Proposition 2; "cannot be extended to the normalized version"). `miml_metrics.RankingLoss` is `sklearn.label_ranking_loss` and `s_ranking` averages over pairs: both normalised, as H5 says. |
| `scipy.stats.wilcoxon(method="exact")` with ties / zeros (scipy 1.18.0 in `.venv`) | Runs without error or fallback. The §1.6 clause "normal approximation with continuity correction if there are ties or zeros" does not describe what the named call does (m2). |
| Leftover v2 terms (`d_z,corr`, `T10`, `symmetric`, `null_perm`, `null_gauss`, "folds in agreement") | None outside the response tables and the ban sentence. |

## Part 1 — Round-2 findings (B1–B3, M1–M8, m1–m11): genuinely resolved?

| finding | status | note |
|---|---|---|
| B1 | **partially** | The instance-level purge with a size-matched random control, the not-estimable clause on instance rows, n₁ = post-purge bags and the upper-bound wording are all in H2-B. But the control is not matched on the one covariate that matters (whether the label-carrying centre row survives), and once that is computed the "upper bound" reading is wrong. New BLOCKER B1 below. |
| B2 | resolved | §6.3 library pilot and projection; §6.5 300 process-hour cap, reduced VOC grid fixed verbatim as review 2 proposed, `IDistance` cache gated on T03-d; §6.6 run- and arm-level "did not complete"; §6.7. |
| B3 | resolved as a document, with one hole | Device per arm fixed (§6.1), one global MPS fallback, 120 device-hour per-unit cap after PCA, total budgets, priority list, simultaneous PCA trigger. The hole is the **order** in which §6.3–§6.7 are applied and **which arms** feed the §6.4 trigger (M1 below). |
| M1 | resolved | H5 recipe is complete: architectures, Adam 1e-3, batch 16, 200 epochs, early stopping on the surrogate's own validation value with patience 20, checkpoint rule, z-scoring on `fit_i`, pairing unit = outer fold with the seed mean, 5×5 for MSRC v2 and Letter Frost. |
| M2 | resolved | Two-sided; HL median with exact CI; rank-biserial r; collapsed sensitivity (n = 12 and 7, arithmetic correct); §7 D power; G1–G3 pre-worded; "if losses outnumber wins, the abstract says so". |
| M3 | resolved | §1.4: raw features for KDIS and MIMLNN on every version; PCA-128 on VOC for all; z-scoring on `fit_i` for TabPFN/logreg/H5 (H5's all-rows z-scoring corrected). |
| M4 | resolved | §1.3 "all candidates scored by `miml_metrics.py` on dumped predictions"; §1.5 what/where/format; `PredictDump.java` against the unmodified jar; Octave driver extended; fallback with T03-f tolerance and per-harness split. |
| M5 | resolved | §0.1 VOC paragraph: hash, size, extractor, grid, image set, label rule, sibling files excluded by name, why 128, 769 features with `ignore_pretraining_limits`, 8 309-row context, release list. |
| M6 | resolved | H2-A step 1 excludes the remainder rows from every pool and bag; non-comparability sentence in H1 and H2-A. |
| M7 | resolved | Yeast bag-mean rerun on G; |margin − 0.006| < 1e-3 flag; Birds flagged (RESULT.md margin +0.0060, short by 2e-6: confirmed). |
| M8 | resolved | §1.6 one n₁ rule with four cases; §7 A labelled; §7 C per family with its own f. |
| m1 | resolved | d_z,corr dropped; t reported. |
| m2 | resolved | §7 B wording "a scenario … not a bound in either direction". |
| m3 | resolved | Header table with sha256 and local dates; §1.8 deposit list includes the three August files and the two reviews. |
| m4 | resolved | §1.8 release list. |
| m5 | resolved | H4: `bagmean_card` not run on the 6 constant-cardinality rows; unadjusted 95 % CI with corrected variance. |
| m6 | resolved | §7 C. |
| m7 | resolved | §1.2. |
| m8 | resolved | §6.3 last bullet. |
| m9 | resolved | §6.8 T03-a…f with tolerances. "Recorded in T03's task file" still points at a file that does not exist (m6 below). |
| m10 | resolved | §1.6 Reporting. |
| m11 | resolved | §6.9. |

Genuinely resolved: 20. Partially: 1 (B1). Resolved with a residual hole: 1 (B3 → M1).

## Part 2 — Are the end-of-file tables true?

Every cell of the three response tables and the change table was followed to the section it names; each change is present where it claims. Two cells over-state slightly: the B1 row says "upper-bound wording" as if the reading were established (see B1); the "Remaining checklist items … Already in v3; unchanged" row is correct. The fact-checkers' B.1–B.12 are all implemented as described. The change table's H1-labelling row matches both 2026-10-13 rows of `DECISIONS.md` (all 16 rows CONFIRMATORY; eight "direction previously observed"; never-run m = 10 with the four rebuilt sets; leaky originals EXPLORATORY in no family; primary Holm and global test over all rows). §7, `power_table.py` (`M_PRIMARY = 16`, `M_NEVERRUN = 10`) and §1.6 agree with it.

## Part 3 — Findings on v3

### BLOCKER

**B1. The H2-B random-row control is not matched on centre deletion, and the "upper bound" reading is therefore unjustified; the H2 decision wording (i)–(iii) would misread the result.**

Recomputed from `results/provenance_bag_rows_*.csv` and the canonical folds, exactly as H2-B defines S_f (every source row occurring in any test bag), among training bags that survive the purge:

| dataset | rows removed | bags emptied | rows left per surviving bag | **centre row deleted: leak purge** | **centre row deleted: size-matched uniform control (expected)** |
|---|---|---|---|---|---|
| Emotions | 0.468 | 6.4 % | 2.84 | **0.238** | **0.432** |
| Yeast | 0.457 | 5.7 % | 2.88 | **0.255** | **0.424** |
| Medical | 0.628 | 12.8 % | 2.14 | **0.073** | **0.573** |
| Corel5K | 0.675 | 8.3 % | 1.77 | **0.054** | **0.645** |

Why the rates differ: S_f contains every test row (all test bags' centres) plus the training rows that are neighbours of a test row. A training bag's *neighbour* is deleted when it is a test row or a neighbour of one; its *centre* is deleted only in the second case. So the leak purge removes neighbours far more often than centres, while a uniform draw of the same count removes the centre with probability k/5. The bag's labels are the centre's labels (T01 §3; H2-B keeps them after deletion). Under the control, 43–65 % of surviving training bags therefore become bags whose features are neighbours only and whose labels belong to a row no longer present; under the leak purge, 5–26 %. That is a large, systematic label-noise handicap on the **control** arm, and it is largest exactly on Medical and Corel5K.

Consequence: AP(random control) is biased **downward** relative to a label-preserving removal of the same count, so the "leakage effect" = AP(control) − AP(leak purge) is biased **downward**. The document's argument for "upper bound" (the purge also removes legitimately similar rows, biasing the effect upward) is correct but is one of two opposite biases; nothing in the design says which dominates. As written, outcome (ii) "the measured upper bound on its effect is not significant" could be reported when the control's handicap cancelled a real leakage effect, and outcome (iii) "contradicting the leakage story" could be reported for a pure artefact of the control. This is the only CONFIRMATORY leakage test in the plan (R2-03 item 3, R6-M01), so it blocks.

*Fix (cheap, before deposit).* Stratify the control on centre status: for each surviving training bag, the control deletes the centre row **iff** the leak purge deleted it, and then deletes the remaining k − 1{centre} rows uniformly at random among that bag's non-centre rows (`default_rng(seed)`, seeds {0, 1, 2}). This matches bag count, instance count, per-bag cardinality **and** centre survival exactly, leaving "which neighbours" as the only difference; the remaining asymmetry (purged neighbours are, by construction, near test rows) then biases the effect upward only, and the upper-bound reading becomes defensible. Report the table above (centre-deletion rates per fold) as a descriptive statistic beside the existing ones. State in the interpretation that a bag whose centre is deleted keeps labels no instance carries, for both arms, and give its rate. No change to §7 C is needed (n₁ is unchanged).

### MAJOR

**M1. The order of the §6.3–§6.7 decisions is undefined and the §6.4 trigger set is too wide; together they let exploratory projections change the primary arm's preprocessing, and §5 is scheduled both before and after the projections.**
(a) §6.4 triggers PCA-500 for **all** TabPFN arms on a dataset if **any** TabPFN arm's native projection on any version exceeds 72 device-hours. The H4 instance-subsampling curve alone is 4 subset sizes × 3 seeds × 2 arms = 24 conditions, and H4-padded is 3; on Corel5K-R (59 labels) or the proteins their projection will exceed 72 h on any device even when the H1 multiview arm would not. The primary F-H1 row's preprocessing is then decided by a POST-HOC arm's cost. (b) §6.7 drops units when totals are exceeded; whether §6.4 is evaluated over the units **before** or **after** §6.7 drops is not stated, and the two are circular (PCA changes projections; drops change the trigger set). A doer could, in good faith, obtain either answer. (c) §5 (one-fit check) "is logged before the projection phase, because it halves or does not halve every projection", yet §6.7 lists "§5" at priority level 9, the first to be dropped after the projections exist; the same holds for the timing pilots and T03, whose GPU/CPU hours are in no budget.
*Fix.* Write the order once: (1) T03 checks and §5 on C/G as **fixed-cost pre-projection items**, outside the budgets and the priority list, their hours logged; (2) timing pilots on every unit at native width; (3) §6.5 library caps; (4) §6.4 PCA trigger evaluated **only over the H1 arms (multiview and bag-mean) of the dataset's versions**, with H2-B, H3 and H4 arms inheriting the decision (and re-projected); (5) §6.7 per-unit cap and budget drops; (6) `PROJECTIONS.md` written; (7) runs. Remove "§5" from level 9 (keep the cross-device check there). State that pilot hours are logged but not counted against the 1 500 / 3 000 / 100.

**M2. Three timing rules are gameable through concurrency, and one systematically excludes slow-but-strong baselines.**
§6.1 defines process-hours as wall clock per process and explicitly allows unlimited concurrent processes on C; §6.6 fails a single Java/Octave run at max(7 200 s, 3 × pilot) wall clock; §6.4/§6.7 compare device-hours against 72/120/180 h. Under heavy concurrency every wall clock inflates: a fully loaded M4 Pro can push MIMLBagging (84-configuration grid, bagged base learners) or MIMLNN at Corel5K-R size past 7 200 s and have them "excluded from selection in that outer fold" (§1.3), which removes the baselines most likely to compete; conversely a pilot run on an idle machine under-projects and a later loaded run trips "did not complete". On G, nothing says the device is used by one process at a time, so the PCA trigger depends on scheduling.
*Fix.* (i) Per-run timeouts in **CPU time** (user + sys, `getrusage` of the child), not wall clock; or fix the concurrency level N once, now, and run the pilot and the production run at the same N. (ii) Device-hours on G: one TabPFN process per device at a time, stated; or measure with CUDA event time inside the process. (iii) Log the load average / concurrent-process count with every timing record in `PROJECTIONS.md` and the cost table.

**M3. The H4 ratio and subsampling statistics are gated on the same data they are computed from, and the gate admits negative gains for which W1–W3 and the Δ_inst wording change sign.**
s, c and Δ_inst are computed only where the 95 % CI of Δ(multiview − bagmean) excludes 0. Conditioning on that CI, using the same fold vector that forms the denominator of s and the g(1.0) term of Δ_inst, biases |Δ(multiview − bagmean)| upward (the rows that pass are the lucky ones at 9 % first-step power), hence s and c downward and Δ_inst away from zero. Separately, "excludes 0" includes CI entirely below 0; there "width-insufficient: at most a minor share of the **gain**" and "the multi-view gain grows" are meaningless. With n = 10 and b̄ near the gate, the delta-method CI for a ratio is also poorly calibrated.
*Fix.* (i) Gate on "CI of Δ(multiview − bagmean) **above** 0" for s, c and Δ_inst; for rows with CI below 0 report only the raw deltas and the pre-worded sentence "multi-view did not improve on bag-mean here; no share is computed". (ii) Add one sentence: "s, c and Δ_inst are conditional on the gate and are biased in the directions stated; they are descriptive." (iii) Report a Fieller interval beside the delta-method CI for s and c (same inputs; one line of code). The W1 threshold 0.5 on the upper CI bound is fine once (i) holds.

**M4. §1.9's stated purpose ("whether the single-run verdicts of §1.1 survive repetition") is not met by its arms.** The single-run verdicts R1-M04, R2-04, R5-04 and R6-M08 attack are the multiview-vs-library headline rows. §1.9 repeats only logreg and TabPFN bag-mean (plus the library where cheap). Reviewers will read the gap. On Scene (5 labels) and Birds (19 labels) a multiview MPS run is a few device-hours.
*Fix.* Add `tabpfn_multiview` on the local MPS backend to §1.9 under the same 72 MPS-hour gate as bag-mean (it will run on Scene, Birds, and probably Reuters at PCA-500 and the smaller proteins), and reword the purpose to "for the arms that fit the gate". Keep it EXPLORATORY.

### MINOR

**m1. `tr` ordering for `tr[:v]` is undefined on the new designs.** The 80/20 context/validation split (§1.3) and the TabPFN z-scoring depend on the order of the outer-training index array. On the canonical 10CV sets the harness defines it; on the §1.2 and §1.9 repeated designs ("contiguous blocks of the permutation") and the H2-A rows ("canonical order") it does not. State: `tr` = the permutation with the test block removed, in permutation order; for H2-A, the rebuilt bags in canonical bag-index order. Also note that the grouped inner CV of H2-A step 5 gives inner folds of 2, 2, 2, 2, 1 pools.

**m2. The Wilcoxon tie clause does not match the named call.** With scipy 1.18.0 (`.venv`), `wilcoxon(method="exact")` runs on ties and zeros without falling back. State the scipy version, `zero_method="wilcox"` (the default: zeros dropped, n reduced), and that with continuous AP differences ties are not expected; drop "normal approximation … if there are ties".

**m3. The "never-run" sensitivity family contains two rows whose direction was seen.** Rebuilt Emotions and Yeast carry "direction previously observed" and sit in F-H1-neverrun. `DECISIONS.md` permits this (rebuilt sets are new data), and the text discloses it, but the family's name promises R2 the opposite. Rename it "no prior number on this data version" in the manuscript, and print the qualifier in the sensitivity sentence of the abstract, which currently lists only "global p, HL median and CI, Holm counts".

**m4. §6.3 TabPFN pilot formula should name the fit count.** "fit + validation predict + test predict" is one fit if §5 passes and two if it fails; §6.3 says §5 is decided first but the projection formula does not say the pilot runs the production fit count. One clause.

**m5. Refit multiplier 1.25× understates Hausdorff cost.** Inner training folds are 4/5 of the outer training fold; distance matrices scale as n², so the refit is ≈ 1.56× an inner run, not 1.25×. Use the measured refit time on Letter Frost outer fold 0 (one extra run per method) or 1.56×; otherwise the 300-hour cap is tested against an under-projection.

**m6. Dangling references.** §6.8 "recorded in T03's task file" and §0.1/§1.8 "(T11)": neither `tasks/T03-*.md` nor `T11-*.md` exists (only `T01-provenance-audit.md`). `convert_new_datasets.py`, `build_hja_birdsong.py` and `build_voc_seg_subset.py` are in `../MIML_CLAM_Enhanced/` (root and `datasets/`), not in this project; give the paths as §0.1 does for `voc_miml.py`, since the deposit must be able to find them. `PredictDump.java`, the extended `run_mimlnn.m`, `DEVICE_LOG.md` and `PROJECTIONS.md` are correctly described as to-be-written; say so in §1.5 ("will be added") rather than present tense.

**m7. H2-B multiview arms run on near-single-instance bags.** After the purge the mean surviving bag has 2.8 / 2.9 / 2.1 / 1.8 rows (table in B1), so SD, quantiles and max/min are degenerate for most bags in both arms. Validity is unaffected (both arms are matched), but the manuscript should say that the H2-B multiview rows measure leakage on a representation that has collapsed towards bag-mean.

**m8. `DECISIONS.md` 2026-10-12 "nothing descoped" vs §6.7 drops.** §6.7 can drop primary F-H1 rows (level 3) and the H3 Yeast pair (level 2) by budget. A pre-registered contingency is the right instrument, but the user's row says nothing is descoped; add a `DECISIONS.md` row acknowledging that §6.7's priority list is the only permitted descoping and is applied mechanically from `PROJECTIONS.md`.

**m9. Deposit hygiene.** v3 is untracked; §1.8 should say the deposited v3 is a committed file and record its commit hash and sha256 in the header before deposit (as the header already does for the August files). Exclude `__pycache__`.

## Part 4 — Statistical pieces introduced in v3

- **Instance-level purge + random-row control:** matched on count, cardinality and emptied bags; **not** matched on centre survival (B1). Upper-bound reading: not justified as written; justified after the stratified control.
- **Width share s with delta-method CI:** the formula SE(s) = √(Var(ā) − 2s·Cov + s²·Var(b̄)) / |b̄| is the correct first-order expansion of ā/b̄, and applying the (1/n + n₂/n₁) factor to the covariance is consistent with the test. Issues are the gate and the sign (M3).
- **Instance-subsampling rule:** Δ_inst = g(1.0) − g(0.25) paired per fold is well defined (⌈f·nᵢ⌉ ≥ 1 handles the Letter and MSRC v2 bags of size 1); subsampling test bags changes the task as well as the representation, which the plan should say; gate/sign issue as M3.
- **Hodges–Lehmann and rank-biserial:** HL as the median of Walsh averages with the exact CI from the Wilcoxon critical value is correct; r = (T⁺ − T⁻)/(T⁺ + T⁻) is Kerby's matched-pairs form and is correct.
- **Collapsed sensitivities:** n = 12 and n = 7 are arithmetically right; collapsing to the family mean is the standard remedy; §7 D reports its power.
- **§1.9 repeated 10-fold:** design and test are right; arm coverage is the issue (M4).
- **§7:** every cell I recomputed agrees; the noncentral-t approximation and its stated liberal bias (Type-I 0.067) are correctly carried over; the Monte Carlo is seeded and reproduces.

## Part 5 — Executability

A doer following v3 can run H1, H3, H5, §1.9, the T03 checks and the cost table without judgement. They would have to decide by judgement: the order of §6.3–§6.7 and which arms trigger PCA (M1); how many processes to run concurrently and hence which baselines time out (M2); what to do on an H4 row whose gain CI lies below 0 (M3); the index order behind `tr[:v]` on the new designs (m1); where T03's results go (m6). The H2-B contrast can be run as written, but its interpretation would be wrong (B1).

## Part 6 — Would R1, R2, R5 and R6 accept this analysis plan?

| comment | after v3 as written | after the fixes above |
|---|---|---|
| R1-M04 (corrected test on repeated CV; revise 7/8; band) | yes: §1.2, §1.6, §1.9; band retired, δ_ds per dataset; 5×5 instead of 10×10 justified (§1.2) | yes |
| R1-M05 (bag-max, bag-mean+card, native/constructed counts) | yes: H4 arms, §0.2 groups with counts | yes |
| R1-M08 (selection granularity, like-for-like, "best", neural details, thresholding) | yes: §1.3 per-fold selection table and "procedure" naming, H5 recipe, native bipartitions | yes |
| R2-02 (nested selection, rerun tests) | yes; VOC/Corel5K-R feasibility now capped (§6.5) | yes |
| R2-03 (quantify overlap; rebuild or group; release mapping) | overlap, H2-A, release: yes; H2-B measurement: **no**, the control is mis-matched (B1) | yes with B1 |
| R2-04 (dependence-aware test, CI, effect sizes, validity, selection, Reuters/Yeast care) | yes: §1.6, δ_ds wording, HL/CI/r | yes |
| R2-07 (labels, public record, bag-max, failed rule primary, same-fold separate) | yes: Labels, header deposit, H3 primary, never-run sensitivity, POST-HOC on the submitted comparison; m3 wording | yes |
| R2-08 (release everything; larger natural dataset; restrict claims) | yes: §1.5, §1.8, §0.1 VOC2012; claims are a manuscript matter | yes |
| R5-02 (ablation does not isolate structure; width confound) | yes in design: padded control with permuted real columns, three outcomes, no accept-the-null; gate/sign defect (M3) | yes with M3 |
| R5-03 (selection inside training data; evaluate once) | yes: §1.3; "MIML-PFN's only tuned quantity" sentence | yes |
| R5-04 (corrected test; repeated CV; Reuters/Yeast) | per-dataset yes; the repeated-CV check does not cover the headline arm (M4) | yes with M4 |
| R6-M03 (define native/constructed; arms) | yes: §0.2 rule and table, H4 | yes |
| R6-M05 (tune k; preprocessing; thresholding) | yes: §1.3 grid, §1.4, native bipartitions | yes |
| R6-M08 (corrected test; SDs) | yes: §1.6 Reporting | yes |

## Summary

v3 is a large step: every round-2 finding except B1 is genuinely closed, the fact-checkers' twelve gaps are implemented where the tables say, the document agrees with the three 2026-10-13 rows of `DECISIONS.md`, and every number in §7 that I recomputed, including the seeded Wilcoxon Monte Carlo, reproduces. One thing stops it from being deposited: the H2-B control deletes the label-carrying centre row two to twelve times more often than the leak purge does (0.43–0.65 vs 0.05–0.26 of surviving training bags), so the contrast is confounded with label noise on the control side and the pre-written "upper bound" reading, and outcomes (ii) and (iii), are unsafe. The fix is a one-line stratification of the control. Four further items (decision order and PCA trigger set, concurrency-dependent timing rules, the H4 gate/sign, and the arm coverage of §1.9) are needed before a doer can run the budget and mechanism sections without judgement.

BLOCKER: B1. MAJOR: M1–M4. MINOR: m1–m9.

VERDICT: NOT RESOLVED — 14 findings
