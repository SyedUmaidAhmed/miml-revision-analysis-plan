# Revision R1: pre-registration of all new analyses (v2)

| | |
|---|---|
| Written | 2026-10-12, before any revision experiment has produced a number |
| v1 | reviewed in `../../revision_access_44676/reviews/PREREG__review_1.md` (26 findings); v2 addresses all of them, finding by finding (see the table at the end) |
| Public timestamp | **PENDING.** Before the first run, this file and `experiments/revision_r1/` are deposited publicly (OSF registration, or a public GitHub repository archived to Zenodo) and the URL/DOI is entered here. Until that happens, the manuscript calls this an "analysis plan", not a pre-registration (F21). |
| Context | IEEE Access Access-2026-44676 decision; per-comment tracking in `../../revision_access_44676/LEDGER.md` |

`../miml_pfn/PREREGISTERED.md` and `../miml_pfn/AMENDMENT.md` stay **as written**. Their primary verdict, "FAILED at 3 of 4 qualifying datasets, as of the 2026-09-04 submission", remains the primary outcome of record of the original study. This document adds analyses and rewrites nothing.

**Labels:**
- **CONFIRMATORY**: hypothesis, test, family and decision rule fixed here, before the data exists.
- **CONFIRMATORY (new protocol; direction previously observed)**: the comparison was seen under the submitted protocol, but the protocol, test and family are new and fixed here (F22).
- **EXPLORATORY**: reported, never used alone to support a headline claim.

---

## 0. Datasets and a-priori grouping (F18, F26)

| dataset | source of split | bag origin, fixed a priori | bag size varies? |
|---|---|---|---|
| Scene | `10CV.mat` | native: image regions (fixed 9 per image) | no |
| Reuters | `10CV.mat` | native: text passages | from T01 |
| MSRC v2 | none shipped → §1.2 | native: image segments | yes |
| Letter Frost | none shipped → §1.2 | native: letters in words | yes |
| Letter Carroll | none shipped → §1.2 | native: letters in words | yes |
| Birds (our `birdsong.mat`, 257 bags, 19 labels; identity in T01) | `birdsong_10CV.mat` | native: audio segments | yes |
| **HJA Birdsong** (`hja_birdsong.mat`, 548 bags, 13 labels; Briggs et al. 2012) | none shipped → §1.2 | native: audio segments | yes |
| Protein ×4 | `*_10CV.mat` | native: per T01 description | from T01 |
| **VOC2012** (`voc2012.mat`, 11,540 bags × 16 patches × 2048-d) | `voc2012_10CV.mat` | native: image patches (our own feature extraction; provenance in T01) | no |
| Emotions, Yeast, Medical, Corel5K | `*_10CV.mat` | **constructed** (k-NN; T01) | no |

- HJA Birdsong is the dataset the literature means by "Birdsong" (R1-REF07, R6-M01).
- VOC2012 is the larger, naturally occurring dataset R2-08 asks for.
- Both are added before any number exists on them.
- "Native" and "constructed" are fixed by this table. "Bag size varies" is taken from T01's measured bag-size SD (> 0), not from results.

## 1. Common protocol

### 1.1 Datasets with a shipped split
- The canonical split is used: the `*_10CV.mat` permutation, cut into 10 contiguous folds by the existing loader.
  - **Reason:** this split ships with the data, so it is comparable with every other user of these files. Single 10-fold is the primary design here.
- **F24:** the loader cuts blocks of size ⌊n/10⌋, so n mod 10 bags are never tested. T01 reports the counts per dataset. They are kept out, as in the submission, so that numbers stay comparable, and the manuscript says so.

### 1.2 Datasets without a shipped split (MSRC v2, Letter Frost, Letter Carroll, HJA Birdsong)
- The primary design is **repeated cross-validation, r = 5 repeats × k folds**: k = 5 for MSRC v2 and the Letter sets (as submitted), k = 10 for HJA Birdsong.
- Permutations come from `numpy.random.default_rng(seed)` with seed ∈ {0, 1, 2, 3, 4}, and every bag is used.
- **Reason:** there is no canonical split to stay comparable with, and a single k = 5 run has very little power (§1.6).
- The submitted seed-42 5-fold results for MSRC v2 and the Letter sets are kept in a supplementary "as submitted" column.

### 1.3 Inner selection
- **Baselines (F4).** Every candidate configuration is scored by **inner 5-fold CV** on the outer training fold.
  - Inner permutation seed = 1000 + outer-fold index (+100 × repeat).
  - The candidate with the best mean inner score is **refit on 100% of the outer training fold** and evaluated once on the outer test fold.
- **Library procedure (F7).** "Tuned published library" is a *validation-selected procedure*. Per outer fold and per metric, it picks the best (method, distance, k) or MIMLNN (ratio, λ) by mean inner score.
  - **Tie-break order:** better inner mean → lower inner SD → method name alphabetical → smaller k.
  - The selected candidate is stored per fold and reported.
  - Each of the 8 published methods is also reported individually, with its own nested tuning.
- **Selection per metric.** Each metric's baseline is tuned on that metric's inner score, which is the most favourable choice for the baselines.
- **Ours (F5, F6), unchanged from the submission.**
  - TabPFN context = the first 80% of the outer training indices (`tr[:v]` is the validation set).
  - **Declared handicap:** our model sees 80% of the training data while baselines are refit on 100%.
  - **Disclosed quirk (F4):** `tr[:v]` gives the same validation bags for outer folds 2..9 on the 10CV sets.
  - Per-label thresholds are tuned for Hamming loss on that validation set.
  - **AP, one-error, coverage and ranking loss for MIML-PFN involve no selection of any kind.** Only Hamming loss uses the tuned thresholds.
  - A fixed-0.5-threshold Hamming-loss row is reported as a sensitivity check.
  - KDIS and MIMLNN produce bipartitions natively. That procedure is documented per method in the manuscript (R1-M08, R6-M05).
- **Degenerate labels (F4).** A label with no positive bag in an inner training split is predicted constant negative for that split. The metric conventions (miml_metrics.py; written into the manuscript per R1-m05) handle it identically for every method.
- **Stochastic baselines (F8).** MIMLNN (k-medoids initialisation) is run with Octave seeds {0, 1, 2, 3, 4} per configuration.
  - Selection uses the inner score averaged over seeds.
  - The outer-test metric is the **mean over the 5 seeds**, not an ensemble of their predictions.
  - Grid, fixed here: ratio ∈ {0.2, 0.4, 0.6} × λ ∈ {0.1, 1, 10} (released defaults 0.4 and 1). KDIS methods are deterministic given the data; T03 verifies this on Letter Frost, and if that fails the same 5-seed rule applies.
- **KDIS grid:** 7 methods × distance {AveH, MaxH, MinH} × k {5, 10, 15, 20}. Methods without a k parameter are swept over distance only.
- **Selection optimism (F4).** For every dataset we report AP(test-fold-selected, as submitted) − AP(nested). This measures how much the submitted selection flattered the baselines.

### 1.4 Shared preprocessing for VOC2012 (2048-d instances)
- Instance features are reduced by PCA to **128 dimensions**, fit on outer-training instances only.
- The reduced features are used **by every method**: KDIS, MIMLNN, logreg, all TabPFN arms.
- **Reason:** this keeps Hausdorff-distance baselines computationally feasible, and every arm gets identical preprocessing.

### 1.5 Metrics
- **Primary:** Average Precision (AP).
- **Secondary:** Hamming loss, one-error, coverage, ranking loss.
- All computed by `../../../MIML_CLAM_Release/miml_clam/metrics/miml_metrics.py`. MIMLNN keeps its authors' own scoring, as in the submission; T03 checks agreement on one dataset by rescoring stored predictions if available.

### 1.6 Statistical test (F1, F2, F3)
**Test statistic.** The corrected repeated k-fold cv test of Bouckaert & Frank (2004), built on the Nadeau & Bengio (2003) variance correction. Over the n = r·k fold differences d_j:

  t = d̄ / sqrt( (1/n + n₂/n₁) · s²_d ),  s²_d with ddof = 1,  df = n − 1,  two-sided.

- For the single 10-fold designs, r = 1.
- n₂/n₁ is the mean outer test size over the **smaller** of the two training sets compared. For MIML-PFN that is 0.8 × the outer training size (F5), which gives the more conservative correction.

**Why this is valid at k = 5 and k = 10 (R2-04, F3).**
- The paired t-test treats fold differences as independent. Overlapping training sets make them positively correlated, so the naive variance s²/n is too small (Dietterich 1998; Nadeau & Bengio 2003).
- The n₂/n₁ term inflates the variance by the correlation implied by the training/test overlap.
- Bouckaert & Frank showed that the corrected test has close-to-nominal Type-I error, and better replicability, *when repeated*. That is why §1.2 uses r = 5 wherever no canonical split binds us.
- For the canonical single 10-fold splits the test remains approximate. The manuscript states this, and pairs it with the cross-dataset test below, which does not rely on fold independence.

**Families and Holm (F2).** Holm step-down at α = 0.05 within each family:
- **F-H1-primary:** MIML-PFN (multiview) vs nested library, AP, one test per dataset.
- **F-H1-bagmean:** bag-mean TabPFN vs nested library, AP, per dataset.
- **F-H1-secondary-<metric>:** one family per secondary metric, for each arm.
- H2 and H4 families are defined in their sections.

**Global hypothesis.**
- The Wilcoxon signed-rank test over datasets (Demšar 2006) on the per-dataset mean AP differences, for multiview vs library.
- This is the confirmatory test of "MIML-PFN beats the library across the suite".
- The per-dataset Holm results describe *where*.

**Reporting.**
- For every test: raw p, Holm-adjusted p, mean Δ, 95% CI (corrected variance), d_z = d̄ / s_d (uncorrected standardised mean difference, named as such), and d_z,corr = d̄ / sqrt(n·(1/n + n₂/n₁) · s²_d).
- The uncorrected `ttest_rel` appears only in a supplementary table, labelled.

**Outcomes and wording (F3).**
- A Holm-significant difference is a "win" or a "loss". Anything else is "**not significant**", never "tie" or "equivalent".
- The 0.006 band is retired (it appears only inside the original MIML-PFN rule, H3).
- No equivalence claims are made.

**Power, stated in advance.** An appended power table (computed by T05 from the *submitted* fold vectors before this file is deposited) lists, per dataset and design, the d_z needed for the first Holm survivor at family size m. For example, a single k = 5 run with m ≈ 16 needs d_z > ~4. The manuscript reports this table, and interprets non-significance on underpowered rows as "inconclusive", not "no effect".

### 1.7 Hygiene
- No dataset is dropped post hoc. A technical failure is reported as a failure, with measured compute (§6 defines "did not complete").
- One results file per concurrent writer, under `results/revision_r1/`.
- All seeds are listed above.

---

## H1: MIML-PFN vs published methods under nested selection

**Label:** CONFIRMATORY (new protocol; direction previously observed on 8 datasets).

Addresses R1-M03, R1-M08, R2-01, R2-02, R3-01, R3-02, R5-03, R6-M02, R6-M05.

- **Arms.** `tabpfn_multiview` (MIML-PFN as defined in the manuscript) and `tabpfn_bagmean`. Each gets its **own** record and is **never pooled** into a single count.
- **Family F-H1-primary.** All datasets in §0 on which both MIML-PFN and the library complete under §6. For the four constructed sets, the primary row is the **symmetric-rebuild** version (H2-A). The original version is reported beside it, labelled "leaky".
- **Decision.**
  - The abstract states the Wilcoxon result and the Holm W/L/NS counts for MIML-PFN, exactly as obtained.
  - The bag-mean arm's counts are stated separately.
  - If losses outnumber wins, the abstract says so.
- **Stress test (EXPLORATORY).** The submitted test-selected numbers appear in one supplementary table titled as an optimistic-for-baselines stress test. They are never used for p-values.

## H2: leakage in the k-NN-constructed sets

**Label:** CONFIRMATORY. Addresses R2-03, R6-M01, R1-M02 (F12–F15).

**Overlap quantification, reported for every outer fold** (from T01, R2-03, F13):
- exact instance overlap: the share of test bags with at least one instance vector in training bags, and the share of test instances present in training bags;
- source-example overlap: the share of test-bag centre examples that occur in training bags;
- neighbourhood overlap: the mean Jaccard of test-bag source sets with their most-overlapping training bag.

**H2-A: symmetric rebuild.** One construction per dataset, used as the primary rows in H1.
- Source examples are partitioned by the outer fold of their bag centre.
- Every bag, training or test, is rebuilt as centre + its 4 nearest neighbours **within the centre's own outer-fold pool**.
  - Euclidean distance on features z-scored with that pool's own statistics.
  - **Ties:** the lower source index wins (F14).
  - **Duplicates:** duplicate source rows are kept as distinct examples, and the duplicate counts are reported (F14).
- Labels are the centre's labels, as verified in T01.
- Every bag sees a pool of the same size (n/10), so training and test neighbourhoods have the same density, and no source example contributes to both a training and a test bag.
- For repeated designs this would be per-repeat, but the constructed sets all use canonical 10-fold.

**H2-B: purged CV on the original bags.** This isolates leakage from training-set size.
- In each outer fold, every training bag that shares any source example with any test bag is removed ("leak purge").
- **Control:** remove the same number of training bags *at random* ("random purge"), with seeds {0, 1, 2}, and average.
- **Leakage effect** = AP(random purge) − AP(leak purge), paired over folds with the §1.6 test. Positive means leakage inflated the scores.
- The purge fraction is reported. If a purge removes more than 80% of the training bags on a dataset (possible for Corel5K, whose hub instances occur in up to 2902 bags), that dataset's H2-B row is reported as "not estimable" rather than tested.

**H2 methods.** logreg bag-mean, logreg multiview, the nested library, MIMLkNN on its own (the most neighbourhood-sensitive method), MIMLNN, TabPFN bag-mean and TabPFN multiview.

**H2 family.** All estimable (method × dataset) H2-B tests, Holm α = 0.05.

**H2 decision.**
- We report the count of significant positive leakage effects.
- The manuscript wording is fixed per outcome:
  - (i) **≥ 1 significant positive effect:** "leakage measurably inflates scores for [methods] on [datasets]".
  - (ii) **none:** "these splits leak by construction (overlap reported), but the measured effect on scores is not significant".
  - (iii) **significant negative effects:** reported as contradicting the leakage story.
- **Interpretation (F15).** Whichever outcome holds, the constructed sets remain constructed. Their use as a negative control for multi-instance structure rests on T01 (provenance), not on H2.

## H3: the original MIML-PFN rule, completed

**Label:** CONFIRMATORY, as originally registered (F16, F17).

**Primary rule.** The rule in `../miml_pfn/PREREGISTERED.md` is evaluated exactly as written, including the 0.006 band, with Yeast included once its multiview arm completes.
- Inputs:
  - **Yeast** uses its canonical split, i.e. the leaky original version, because that is what the rule was registered on.
  - **Birds** keeps its submitted MPS result and is not rerun.
- Yeast multiview **wall-clock cap:** 3× its measured projection on the T10 GPU. Beyond the cap it is recorded as "did not complete" a second time.
- Pre-written abstract wording:
  - (a) primary, as of submission: "failed its pre-registered rule (3 of 4; one dataset incomplete)";
  - (b) upon completion, if Yeast wins: "the rule's last dataset, completed during revision, met the bar (4 of 4)";
  - (b′) if Yeast does not win: "failed (3 of 4) after completion".
  - Both (a) and (b) or (b′) appear in the abstract.

**R2, from AMENDMENT.md.** Evaluated exactly as amended, on {Reuters, 4 protein sets}.

## H4: what the multi-view gain comes from

**Label:** EXPLORATORY, because the arms were added after results were seen. Addresses R1-M05, R5-02, R6-M03.

- **Arms on every dataset:** `tabpfn_bagmean`, `tabpfn_bagmax` (pre-registered 2026-08-14 but never run), `tabpfn_bagmean_card` (mean + cardinality scalar), `tabpfn_multiview`.
- **Reporting:** AP deltas against bag-mean, with §1.6 tests; family Holm over (arm × dataset).
- **Interpretation rule, applied only where the 95% CI of Δ(multiview) excludes 0 (F19):**
  - "largely cardinality" if Δ(bagmean_card) ≥ 0.5 · Δ(multiview);
  - otherwise "higher-order statistics".
  - On sets with constant bag size (Scene, VOC2012, the constructed four), cardinality is constant and cannot contribute. This is stated a priori.
- **Language commitment:** "higher-order bag statistics and cardinality", never "multi-instance structure and nothing else".

## H5: metric alignment

**Label:** EXPLORATORY. Addresses R1-M06, R2-06, R3-04, R4-02, R6-M04 (F20).

**Settings:**
- datasets: Scene, MSRC v2, Letter Frost, Birds
- models: bag-mean MLP (as submitted) and ABMIL-multilabel
- standardisation on training data only
- seeds {0, 1, 2}

**Surrogates, each defined in the manuscript:**
- Hamming → BCE-with-logits
- ranking loss → pairwise softplus
- one-error → softmax cross-entropy over the positive set
- coverage → log-sum-exp soft count of negatives ranked above each positive
- **AP → Smooth-AP** (Brown et al. 2020; sigmoid temperature 0.01). The decision to include it is made now, so the AP claim is tested rather than withdrawn.

**Measurements:**
- (a) Full-batch, mini-batch (batch size 16) and per-label gradient cosines along the BCE trajectory.
- (b) **Cross-evaluation:** train separately on each of the 5 surrogates, then evaluate all 5 metrics on the outer test folds.

**Cross-evaluation family.** Per (dataset, model), all 20 off-diagonal comparisons, "trained on A's surrogate vs trained on B's own surrogate, scored on metric B". Holm within each (dataset, model).

**Reporting:**
- "Conflict observed for (A, B) on [setting]" for each significant degradation.
- "No conflict observed in these settings" only if none are significant.
- The title and abstract will not state metric alignment as a property of the suite.
- We cite Dembczyński et al. (2012), whose result is that Hamming and rank losses have different risk minimisers, as the theory our measurement does not contradict *or* does, whichever holds.

## 5. One-fit TabPFN

**Label:** verification, not a hypothesis.

- Replace the two fits (validation pass, test pass) with one fit that predicts both, **only if** it reproduces all five metrics on every fold of Letter Frost and Scene `tabpfn_bagmean` to |Δ| ≤ 1e-9.
- If it fails, keep two fits and report the cost as measured.

## 6. Compute protocol and the definition of "did not complete"

Addresses F10, F11, F17, F23 and F25.

**Hardware.** Local arms run on Apple M4 Pro (MPS). GPU arms run on the NVIDIA GPU named in `tasks/T10-gpu-arms.md` **before** any GPU result is produced.

**Measured rate.**
- For each (dataset, arm), time the first 3 labels × 2 fits of outer fold 0 on the target device.
- Projected wall-clock = mean fit time × total fits.
- The projection is recorded in T10 before the run continues.

**Budget and PCA rule.** This fixes the PCA budget left open in AMENDMENT.md.
- If the projection exceeds **72 device-hours** for a (dataset, arm), **all TabPFN arms on that dataset** switch to PCA on the bag-level feature matrix, fit on outer-training rows only, with **d′ = 500 components**. 500 is TabPFN v2's pre-training feature limit. If d ≤ 500 the switch is a no-op.
- The switch is decided from the projection only, before any result on that dataset is seen. It applies to bag-mean and multiview alike.

**"Did not complete".** A crash after 2 retries, or a wall-clock above 3× the (post-PCA) projection. It is reported with the hours spent.

**Rebuilt sets (F11).** Every H1 arm, including multiview, also runs on the H2-A rebuilt versions of Emotions, Yeast, Medical and Corel5K. These are inside the T10 budget, under the same rule.

**Cross-device check (F25).** On the GPU, rerun `tabpfn_bagmean` on Letter Frost and Scene. Report the maximum per-fold |ΔAP| against the stored MPS results. If it exceeds 1e-3, the manuscript reports the device for every row and does not compare across devices within a test.

**Cost table (R2-05, F23).** Per method and dataset:
- wall-clock for training plus inference
- peak memory (from `torch.mps`/`torch.cuda` max allocated, or `resource.getrusage` for Java and Octave)
- device

Energy is not measured; the table says so explicitly. Every new results JSON stores per-fit times, device string, library versions and the full constructor arguments. `n_estimators` stays at the default of 8 so that results remain comparable with the submission, and the manuscript states that this is an internal 8-member ensemble.

---

## Response to `PREREG__review_1.md`

| finding | where addressed |
|---|---|
| F1 repeated CV, power | §1.2, §1.6 (power table appended by T05 before deposit) |
| F2 families, global test | §1.6 |
| F3 validity, ddof, d_z, NS ≠ tie | §1.6 |
| F4 inner 5-fold, degenerate labels, optimism, `tr[:v]` quirk | §1.3 |
| F5 80% vs 100% asymmetry, n₂/n₁ | §1.3, §1.6 |
| F6 thresholding, 0.5 sensitivity, AP involves no selection | §1.3 |
| F7 procedure name, tie-break | §1.3 |
| F8 MIMLNN seeds | §1.3 |
| F9 MIMLNN grid fixed now | §1.3 |
| F10, F11, F17 budget, stop rule, PCA d′, hardware | §6 |
| F12 symmetric rebuild + purge control | H2-A, H2-B |
| F13 overlap quantification | H2 |
| F14 ties and duplicates | H2-A |
| F15 meaning of a null | H2 decision |
| F16 Yeast cap, device, wording | H3 |
| F18 a-priori groups | §0 |
| F19 ratio rule only where CI excludes 0 | H4 |
| F20 Smooth-AP decided, cross-evaluation family | H5 |
| F21 public timestamp | header (PENDING, user deposit) |
| F22 label wording | H1 |
| F23 memory and energy | §6 |
| F24 remainder bags | §1.1 |
| F25 cross-device | §6 |
| F26 larger natural dataset | §0 (VOC2012, plus HJA Birdsong) |


---

## 7. Power table (computed 2026-10-12 from submitted fold vectors)

Generated by `experiments/revision_r1/power_table.py` (deterministic, one command; full output also in `../../revision_access_44676/evidence/T05__power_table.txt`). Test and ratio exactly as §1.6: n₂/n₁ = (1/k)/((1−1/k)·0.8), df = rk−1, α = 0.05, two-sided.

**Planned family size.** §0 lists 16 F-H1-primary rows: Scene, Reuters, MSRC v2, Letter Frost, Letter Carroll, Birds, HJA Birdsong, 4 protein sets, VOC2012 (12 native) plus Emotions, Yeast, Medical, Corel5K counted once each in their rebuilt version (4). **m = 16 is the planned family if every dataset completes**; m = 14 corresponds to two "did not complete" exclusions under §6, and m = 18 is a margin for comparison. The single 5-fold row is the *submitted* design, shown for reference only; no confirmatory test uses it.

**Power approximation.** T ~ noncentral t with df = n−1 and ncp = d_z/√(1/n + n₂/n₁), i.e. assuming the corrected variance is the true variance of d̄, which is the assumption the test itself makes. d_z here is the population standardised mean of the per-fold differences; under repeated CV, s_d also absorbs between-repeat variation, so a d_z observed on a single k-fold run is not guaranteed to carry over.

### A. Design-level power (corrected test of §1.6, alpha = 0.05)

rho = n2/n1 = (1/k)/((1-1/k)*0.8); n = r*k; df = n-1. d_z,min = t_crit * sqrt(1/n + rho).

| design | n | df | rho | factor sqrt(1/n+rho) | applies to |
|---|---|---|---|---|---|
| single 10-fold (r=1,k=10) | 10 | 9 | 0.1389 | 0.4888 | Scene, Reuters, Birds, Protein x4, VOC2012, constructed x4 |
| repeated 5x5 (r=5,k=5) | 25 | 24 | 0.3125 | 0.5937 | MSRC v2, Letter Frost, Letter Carroll |
| repeated 5x10 (r=5,k=10) | 50 | 49 | 0.1389 | 0.3986 | HJA Birdsong |
| single 5-fold (r=1,k=5) | 5 | 4 | 0.3125 | 0.7159 | REFERENCE ONLY: submitted design for MSRC v2 / Letters |

#### A1. Critical |t| and minimum d_z

| design | m | t_crit first step (alpha/m) | d_z,min first step | t_crit last step (alpha) | d_z,min last step |
|---|---|---|---|---|---|
| single 10-fold (r=1,k=10) | 14 | 3.909 | 1.910 | 2.262 | 1.106 |
| single 10-fold (r=1,k=10) | 16 (planned) | 3.997 | 1.954 | 2.262 | 1.106 |
| single 10-fold (r=1,k=10) | 18 | 4.075 | 1.992 | 2.262 | 1.106 |
| repeated 5x5 (r=5,k=5) | 14 | 3.230 | 1.918 | 2.064 | 1.225 |
| repeated 5x5 (r=5,k=5) | 16 (planned) | 3.285 | 1.950 | 2.064 | 1.225 |
| repeated 5x5 (r=5,k=5) | 18 | 3.333 | 1.979 | 2.064 | 1.225 |
| repeated 5x10 (r=5,k=10) | 14 | 3.061 | 1.220 | 2.010 | 0.801 |
| repeated 5x10 (r=5,k=10) | 16 (planned) | 3.109 | 1.239 | 2.010 | 0.801 |
| repeated 5x10 (r=5,k=10) | 18 | 3.150 | 1.256 | 2.010 | 0.801 |
| single 5-fold (r=1,k=5) | 14 | 6.138 | 4.394 | 2.776 | 1.988 |
| single 5-fold (r=1,k=5) | 16 (planned) | 6.364 | 4.556 | 2.776 | 1.988 |
| single 5-fold (r=1,k=5) | 18 | 6.570 | 4.703 | 2.776 | 1.988 |

#### A2. Approximate power at the first Holm step (alpha/m) and the last (alpha)

Noncentral t, df = n-1, ncp = d_z/sqrt(1/n+rho).

| design | step | d_z=0.5 | d_z=1 | d_z=2 | d_z=3 |
|---|---|---|---|---|---|
| single 10-fold (r=1,k=10) | first, m=14 | 0.018 | 0.095 | 0.590 | 0.956 |
| single 10-fold (r=1,k=10) | first, m=16 | 0.016 | 0.087 | 0.565 | 0.948 |
| single 10-fold (r=1,k=10) | first, m=18 | 0.014 | 0.080 | 0.542 | 0.941 |
| single 10-fold (r=1,k=10) | last (alpha) | 0.151 | 0.447 | 0.952 | 1.000 |
| repeated 5x5 (r=5,k=5) | first, m=14 | 0.016 | 0.085 | 0.563 | 0.954 |
| repeated 5x5 (r=5,k=5) | first, m=16 | 0.015 | 0.078 | 0.543 | 0.948 |
| repeated 5x5 (r=5,k=5) | first, m=18 | 0.013 | 0.072 | 0.526 | 0.943 |
| repeated 5x5 (r=5,k=5) | last (alpha) | 0.128 | 0.366 | 0.898 | 0.998 |
| repeated 5x10 (r=5,k=10) | first, m=14 | 0.043 | 0.304 | 0.970 | 1.000 |
| repeated 5x10 (r=5,k=10) | first, m=16 | 0.040 | 0.289 | 0.967 | 1.000 |
| repeated 5x10 (r=5,k=10) | first, m=18 | 0.036 | 0.276 | 0.964 | 1.000 |
| repeated 5x10 (r=5,k=10) | last (alpha) | 0.233 | 0.691 | 0.998 | 1.000 |
| single 5-fold (r=1,k=5) | first, m=14 | 0.007 | 0.019 | 0.093 | 0.259 |
| single 5-fold (r=1,k=5) | first, m=16 | 0.006 | 0.017 | 0.084 | 0.236 |
| single 5-fold (r=1,k=5) | first, m=18 | 0.005 | 0.015 | 0.076 | 0.217 |
| single 5-fold (r=1,k=5) | last (alpha) | 0.085 | 0.192 | 0.562 | 0.873 |

### B. Observed effects (descriptive, submitted protocol; not a result of this pre-registration)

Ours = make_tables.ours() arm (multiview where it completed, else bag-mean); published = make_tables.best(PUB, ds, AP), selected on test. d = ours - published per fold. d_z = mean(d)/sd(d, ddof=1), uncorrected. t_corr/p_corr = §1.6 test with r=1, k = folds actually used, rho = (1/k)/((1-1/k)*0.8). p_naive = ttest_rel (as in the submitted paper). Holm at m=8 (the 8 tests) and m=16 (planned F-H1-primary size; the 8 untested rows assumed to rank last, which is the most favourable case).

| dataset | ours | best published | k | mean dAP | d_z | t_corr | p_corr | p_naive | Holm m=8 | Holm m=16 | d_z,min first step m=16, this k |
|---|---|---|---|---|---|---|---|---|---|---|---|
| MSRC v2 | multi-view | MIMLIBLR_AveH(10) | 5 | +0.1265 | +5.38 | +7.52 | 0.00167 | 0.00027 | pass | pass | 4.56 |
| Letter Frost | multi-view | MIMLMAPkNN_AveH(10) | 5 | +0.0744 | +2.62 | +3.66 | 0.0215 | 0.0042 | fail | fail | 4.56 |
| Letter Carroll | multi-view | MIMLDGC_AveH(10) | 5 | +0.0620 | +2.27 | +3.17 | 0.034 | 0.0071 | fail | fail | 4.56 |
| Yeast | bag-mean | MIMLIBLR_MaxH(10) | 10 | +0.0115 | +2.63 | +5.39 | 0.000438 | 1.6e-05 | pass | pass | 1.95 |
| Reuters | bag-mean | MIMLNN | 10 | +0.0097 | +1.80 | +3.67 | 0.00512 | 0.0003 | pass | fail | 1.95 |
| Emotions | multi-view | MIMLDGC_MaxH(10) | 10 | +0.0093 | +0.54 | +1.10 | 0.299 | 0.12 | fail | fail | 1.95 |
| Scene | multi-view | MIMLIBLR_MaxH(10) | 10 | -0.0571 | -3.18 | -6.51 | 0.00011 | 3.4e-06 | pass | pass | 1.95 |
| Birdsong | multi-view | MIMLDGC_AveH(10) | 10 | -0.0562 | -1.27 | -2.60 | 0.0287 | 0.003 | fail | fail | 1.95 |

Survivors: 4/8 at m=8, 3/8 at m=16.

### Interpretation

- **Single 5-fold was hopeless for the first Holm step**: at m = 16 it needs d_z > 4.56, and even d_z = 3 has 24% power. Moving MSRC v2 and the Letter sets to 5×5 repeated CV (§1.2) lowers the first-step threshold to d_z > 1.95 and raises power at d_z = 2 from 8% to 54%; this is the main payoff of F1's fix.
- **Single 10-fold (Scene, Reuters, Birds, proteins, VOC2012, the four constructed sets)** needs d_z > 1.95 at the first step and d_z > 1.11 at the last; power at d_z = 1 is 9% (first step) to 45% (last step). Any true effect with d_z ≤ 1 on these rows is likely to come out "not significant", which §1.6 already commits to reading as **inconclusive**, not "no effect". HJA Birdsong (5×10) is the best-powered row (first-step d_z,min = 1.24).
- **Submitted state (descriptive only).** With the §1.6 correction, test-selected best published comparator, and m = 16 assuming the eight untested rows all rank last: MSRC v2 (win, d_z = 5.38), Yeast (bag-mean win, d_z = 2.63) and Scene (loss, d_z = −3.18) survive; Reuters (d_z = 1.80) survives at m = 8 but not at m = 16; Letter Frost (d_z = 2.62) and Letter Carroll (d_z = 2.27) fail only because k = 5 single-run makes their threshold 4.56; Emotions (d_z = 0.54) and the Birds loss (d_z = −1.27) fail at any m. Under the submitted protocol, 4 of 8 survive at m = 8 and 3 of 8 at m = 16, against 7 of 8 with the uncorrected `ttest_rel` reported in the submission.
- **Which rows are underpowered.** If the Letter-set effects persist at roughly their observed d_z (≈ 2.3–2.6) under 5×5 repeated CV, they clear the 1.95 threshold; if they shrink toward d_z ≈ 1, they will be inconclusive. Effects of the size seen on Reuters, Emotions and Birds (|d_z| ≤ 1.8) are below the first-step threshold of every planned design except 5×10, so their verdicts depend on where they fall in the Holm order rather than on their own size.
