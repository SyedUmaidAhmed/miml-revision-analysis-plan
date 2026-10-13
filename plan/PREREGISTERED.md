# Revision R1: pre-registration of all new analyses (v3)

| | |
|---|---|
| Written | 2026-10-12; H1 labelling revised 2026-10-13 by user decision. Before any revision experiment has produced a number; no timing pilot (§6.3) has run either. |
| History | v1 reviewed in `../../revision_access_44676/reviews/PREREG__review_1.md` (26 findings). v2 reviewed in `../../revision_access_44676/reviews/PREREG__review_2.md` (22 findings: B1–B3, M1–M8, m1–m11). v3 also closes 12 gaps found by the fact-checkers (`../../revision_access_44676/comments/R2-*.md` §3), numbered B.1–B.12 below. v3 was reviewed in `../../revision_access_44676/reviews/PREREG__review_3.md` (14 findings: B1, M1–M4, m1–m9), all addressed in place. The round-3 text was reviewed in `PREREG__review_4.md` (10 findings: M1, m1–m9), the round-4 text in `PREREG__review_5.md` (3 findings: m1–m3), the round-5 text in `PREREG__review_6.md` (1 finding), the round-6 text in `PREREG__review_7.md` (1 finding, 4 notes) and the round-7 text in `PREREG__review_8.md` (2 findings, notes); all addressed in place. **Pre-deposit addendum, 2026-10-13:** implementation decisions for T02, T03 and T04/T07 (`DECISIONS.md`, fifteen rows dated 2026-10-13: T03, T02, T04/T07, T04/T07 refinements, T03 part 2, d′ scope, refit-failure consequence, projection approximation, library refit projection bound, review-11 clarifications, KDIS non-determinism fallback, deposit-line format, KDIS fallback labelling, deposit-line grammar tightened, deposit date not in the future) are written into §1.2, §1.3, §1.4, §1.5, §1.6, H2-A, H2-B, H4, §5, §6.3, §6.4, §6.6, §6.7, §6.8 and §1.9, each marked "(pre-deposit addendum, 2026-10-13)"; they are part of the deposited text and binding (table at the end). **Review 9** (`PREREG__review_9.md`) found the round-8 text RESOLVED; that text is tagged `prereg-v3-final` (`62a86a6`). The addendum was reviewed in round 10 at `3c720d8` (`PREREG__review_10.md`, 11 findings) and in round 11 at `589a980` (`PREREG__review_11.md`, 5 findings), all addressed in place; round 12 reviewed `619f844` (`PREREG__review_12.md`, 3 findings, addressed in place). The response tables are at the end of the file. |
| Version control | **None before 2026-10-12.** The project's first git commit is `aceec7b` (2026-10-12 20:15:44 +0500). `experiments/revision_r1/` is tracked: commit `38013d0` holds the v3 draft reviewed in round 3, `b72856e` the text reviewed in round 4, `d2c1103` the text reviewed in round 5, `5e29f54` the text reviewed in round 6, `55105f4` the text reviewed in round 7, `155e4e2` the text reviewed in round 8, `62a86a6` the text RESOLVED in round 9 (tag `prereg-v3-final`), `3c720d8` the pre-deposit addendum reviewed in round 10, `589a980` the text reviewed in round 11, and `619f844` the text reviewed in round 12; the round-12 fixes are committed after this edit. v1 was revised in place and is not versioned (`PREREG__review_1.md` records what it said); v2 is archived, git-committed, at `experiments/revision_r1/history/PREREGISTERED_v2.md`. |
| Public timestamp | **PENDING (user action).** Before step 1 of either queue in §6.0, the deposit listed in §1.8 goes to a public, timestamped archive (an OSF registration, or a public GitHub repository archived to Zenodo), and the URL/DOI is written here. Until then the manuscript calls this an "analysis plan", not a pre-registration (F21). |
| Deposited version | **to be filled at deposit.** The deposited copy itself reads "to be filled" here, because it cannot contain its own hash. A follow-up commit records the deposited copy's git commit hash, sha256 and URL/DOI in this row (§1.8). **Public-timestamp cell, format after deposit (pre-deposit addendum, 2026-10-13):** the orchestrator replaces the PENDING cell of the row above with exactly `https://doi.org/<DOI> (YYYY-MM-DD)` (§1.8). |
| Context | IEEE Access Access-2026-44676 decision; per-comment tracking in `../../revision_access_44676/LEDGER.md`; binding user decisions in `../../revision_access_44676/DECISIONS.md` |

**The August pre-registration cannot be publicly timestamped (B.12, R2-07, m3).** `../miml_pfn/PREREGISTERED.md` and `../miml_pfn/AMENDMENT.md` were local files with no version control and no deposit. A deposit made now proves their content as of October 2026, not August. The deposit therefore includes them byte-for-byte unchanged, with their sha256 and their local filesystem dates, and the manuscript says that those dates rest on local file metadata only:

| file | sha256 | birth time / last modified (local, macOS `stat`) |
|---|---|---|
| `experiments/miml_pfn/PREREGISTERED.md` | `b2176dcf85d83cc8020f6908bab4b02a6a2e93068f38332c5b0e52576e6fb5d8` | 2026-08-14 18:22:09 / 2026-08-14 18:22:09 |
| `experiments/miml_pfn/AMENDMENT.md` | `ca2f1689e44d48c232a0a153002c37dd9fcb138eedd19ff436e0334168f64a20` | 2026-08-15 12:30:47 / 2026-08-15 12:30:47 |
| `experiments/miml_pfn/RESULT.md` (the outcome of record) | `1999f15ec167cdcb4d38171b159d495b527627d92da22cad9bc05fd9b6ad3bfb` | 2026-08-17 20:53:36 / 2026-08-18 12:02:57 |

**User action (optional):** if independent contemporaneous evidence of the August files exists (a Time Machine snapshot, cloud-sync version history, or an email or chat message containing the rule), cite it in the response. If none exists, the manuscript says so.

Both August files stay **as written**. Their primary verdict, "FAILED at 3 of 4 qualifying datasets, as of the 2026-09-04 submission", remains the primary outcome of record of the original study. This document adds analyses and rewrites nothing.

**Labels (B.3, R2-07; user decision 2026-10-13, `DECISIONS.md`):**
- **CONFIRMATORY**: hypothesis, test, family and decision rule fixed here, before any number under this protocol exists.
  - **CONFIRMATORY, direction previously observed**: a confirmatory row whose direction was seen under the submitted protocol (Scene, Reuters, MSRC v2, Letter Frost, Letter Carroll, Birds (MLSP 2013), and Emotions and Yeast, whose leaky versions were seen). The qualifier is printed wherever the row appears.
- **EXPLORATORY**: reported with full tests, never used alone to support a headline claim.
- **POST-HOC**: an analysis whose existence or specification was chosen after results of the same comparison were seen. Reported and labelled as such; never tested inside a confirmatory family.

---

## 0. Datasets, provenance and a-priori grouping (F18, F26, B.9, B.10, M5)

### 0.1 Origin of every file

From the T01 origin table (`../../revision_access_44676/tasks/T01-provenance-audit.md` §C; sha256 values in `../../results/provenance.json` and `../../revision_access_44676/evidence/T01__origin_evidence.txt`). Of the 13 datasets in the submitted paper, **8 files were produced or repackaged by our own converter** (March–April 2026); only Scene, Reuters, MSRC v2 and the two Letter sets are third-party files used as received. Corel5K, HJA Birdsong and VOC2012 are also our files.

| dataset (name used from now on) | file | origin class | who produced the file | label / example filtering | bags | labels | split |
|---|---|---|---|---|---|---|---|
| Scene | `scene.mat` | published, used as distributed | LAMDA MIML distribution; copied | none | 2000 | 5 | `10CV.mat` (2007) |
| Reuters | `reuters_MIML.mat` | published, used as distributed | LAMDA MIML distribution; copied | none | 2000 | 7 | `10CV.mat` (2007) |
| MSRC v2 | `MSCV2.mat` | published, used as distributed | third-party DD-format file (2021); matches the published statistics of the KDD 2012 instance-annotation collection; **not checksum-verified** (source page 404) | none | 591 | 23 | none → §1.2 |
| Letter Frost | `letter_frost.mat` | as MSRC v2 | as MSRC v2 | none; **26 label columns, 24 with at least one positive bag** | 144 | 26 (24) | none → §1.2 |
| Letter Carroll | `letter_carroll.mat` | as MSRC v2 | as MSRC v2 | none; **26 label columns, 24 with at least one positive bag** | 166 | 26 (24) | none → §1.2 |
| **Birds (MLSP 2013)** (formerly "Birdsong") | `birdsong.mat` | published, repackaged by our converter without change | our `convert_birdsong()`, byte-identical to KDIS `miml_birds.arff`; this is the MLSP 2013 bird-challenge set (doi:10.1109/MLSP.2013.6661934; 28 authors verbatim in `../../revision_access_44676/evidence/R1-REF__crossref_checks.txt`), published as an MIML set ("MLSP") by Amelia Zafra and Eva Gibaja, ESWA 232:120876, 2023 | none | 257 | 19 | `birdsong_10CV.mat` |
| **HJA Birdsong** | `hja_birdsong.mat` (sha256 `cc3a2fef…`) | published, repackaged by our script | our `build_hja_birdsong.py` (2026-10-05) from `Birds.mat`, raw features; Forrest Briggs, Balaji Lakshminarayanan, Lawrence Neal, Xiaoli Z. Fern, Raviv Raich, Sarah J. K. Hadley, Adam S. Hadley, Matthew G. Betts, JASA 131(6):4640–4650, 2012 | none | 548 | 13 | none → §1.2 |
| Protein Haloarcula / Pyrococcus / Geobacter / Azotobacter | `protein_*.mat` | published, **label-filtered by us** | our `convert_protein()` from LAMDA `MIMLprotein.zip` (bags byte-identical to the text files) | **labels with ≥ 10 positive bags kept**: 234→21, 321→52, 320→28, 340→46; no bags dropped | 304 / 425 / 379 / 407 | 21 / 52 / 28 / 46 | `protein_*_10CV.mat` |
| **VOC2012** | `voc2012.mat` (sha256 `f672df5c38614fc2c23576cee776998c0f783e65e9570b40ef0c09fda6a79b0c`, 1 514 140 560 bytes) | **built by us** from a public image set; native bags (§0.2) | our `../../../MIML_CLAM_Enhanced/datasets/voc_miml.py` (2026-05-25): every Pascal VOC 2012 `trainval` image (ImageSets/Main/trainval.txt, 11 540 images) → 4×4 grid of equal patches (last row/column absorbs remainder pixels) → frozen torchvision ResNet-50, `IMAGENET1K_V2` weights, standard ImageNet transforms, avgpool output → 2048-d per patch | label = +1 iff at least one **non-difficult** object of that class is annotated (standard VOC multi-label convention); 20 classes; no bag has zero labels | 11 540 | 20 | `voc2012_10CV.mat` = `RandomState(42).permutation(11540)+1` (verified) |
| Emotions, Yeast, Medical, Corel5K | `*.mat` | **constructed by the authors** (DECISIONS.md, 2026-10-12) | our `convert_new_datasets.py`: k-NN bagging of single-instance Mulan/OpenML sets, scaler and neighbour index fitted on all rows (T01 §A) | Corel5K only: labels with ≥ 75 positives (59 of 374), 127 rows with no kept label dropped (5000→4873) | 593 / 2417 / 978 / 4873 | 6 / 14 / 45 / 59 | `*_10CV.mat` = `RandomState(42)` |

**Origin groups, with explicit membership (one count governs every table and the abstract).** Group 1, published MIML sets used as distributed or repackaged without change: Scene, Reuters, MSRC v2, Letter Frost, Letter Carroll, Birds (MLSP 2013), HJA Birdsong (7). Group 2, published but label-filtered by us: the four protein sets (4). Group 3, constructed by the authors by k-NN bagging: Emotions, Yeast, Medical, Corel5K (4). Listed separately: VOC2012, our own feature extraction from a published image set (1). Total 16; the submitted paper's 13 are group 1 without HJA Birdsong (6), group 2 (4), and group 3 without Corel5K (3).

**VOC2012 sibling files, excluded now (M5).** `voc2012seg.mat` (2273 bags) is the subset of `voc2012.mat` rows that have a VOC segmentation mask, and `voc2012segml.mat` (660 bags) is its multi-label-only subset (`build_voc_seg_subset.py`, 2026-08-17). Both were built for instance-attribution work, are subsets of `voc2012.mat`, and are smaller. `voc2012.mat` is the full `trainval` set and the only one that answers R2-08's request for a larger dataset. No switch between the three is permitted.

**VOC2012 dimensions (M5).** Instances are reduced to 128 dimensions by PCA (§1.4). 128 is fixed, not tuned, to make Hausdorff distances affordable at 11 540 bags (one bag pair costs 256 instance pairs × 128 dimensions); whether the library then fits its cap is decided by measurement under §6.5. At 128-d, `tabpfn_multiview` has 6·128 + 1 = **769** bag-level features. It runs at 769 with `ignore_pretraining_limits=True` (already the harness default, `run_foundation_baselines.fit_predict`) unless §6.4's PCA rule triggers, which then reduces it to 500. The TabPFN context is 0.8 × 0.9 × 11 540 ≈ 8 309 rows, under TabPFN v2's 10 000-row limit.

**Released with checksums (M5, m4).** `voc2012.mat`, `voc2012_10CV.mat`, `voc2012_patch_gt.npz` (sha256 `3bbc512ddd0b3449cede0109d032a2e27a5632907398dae4055b7d9e45ae1359`), `voc_miml.py`, or, if the VOC licence forbids redistributing derived features, the scripts plus checksums (release task T11, to be created; the release list is fixed in §1.8).

**The Corel5K and protein label filters** used label counts over all rows. They define the label space of the file and are applied identically to every arm and every version (original, rebuilt, purged); they transfer no per-example label. The manuscript discloses both.

### 0.2 A-priori grouping

A dataset is **native** if every instance is a part of exactly one observed object (an image, a document, a recording, a word, a protein) and no instance is placed in a bag by reference to other bags. It is **constructed** if bags are assembled by the experimenter from neighbourhoods of separately observed examples. By this rule, fixed before any number exists on VOC2012:

| dataset | group | bag origin | bag size varies? (T01 SD > 0) | n mod 10 (never tested on canonical splits) |
|---|---|---|---|---|
| Scene | native | image regions (9 per image) | no | 0 |
| Reuters | native | text passages | yes (2–26) | 0 |
| MSRC v2 | native | image segments | yes | (no canonical split) |
| Letter Frost / Letter Carroll | native | letters in words | yes | (no canonical split) |
| Birds (MLSP 2013) | native | spectrogram segments | yes (2–36) | 7 |
| HJA Birdsong | native | spectrogram segments | yes | (no canonical split) |
| Protein ×4 | native | protein domains | yes | 4 / 5 / 9 / 7 |
| VOC2012 | native | 16 patches of one observed image (fixed grid, like Scene's fixed regions) | no | 0 |
| Emotions, Yeast, Medical, Corel5K | **constructed** | centre example + its 4 nearest neighbours | no | 3 / 7 / 8 / 3 |

- HJA Birdsong is the dataset the literature means by "Bird Song" (R1-REF07, R6-M01). Birds (MLSP 2013) and HJA Birdsong are different datasets: no instance vector is shared (T01 §6).
- VOC2012 is native by the rule above for the same reason Scene is: a bag is one image and its instances are parts of that image. Its patch grid and features are ours, and the manuscript says so. Patch-level ground truth (`voc2012_patch_gt.npz`: `patch_bbox`, and `patch_seg` for the 2273 masked images) confirms that labels are carried by specific instances; it is not used by any test here.
- Both VOC2012 and HJA Birdsong are added before any number exists on them: `results/*.json` contain no entry for either.

## 1. Common protocol

### 1.1 Datasets with a shipped split
- The canonical split is used: the `*_10CV.mat` permutation, cut into 10 contiguous blocks of ⌊n/10⌋ by `get_cv_splits`.
  - **Reason:** the split ships with the file, so the result is comparable with every other use of the file. Single 10-fold is the primary design here.
- **F24:** the n mod 10 bags (table in §0.2) are in every training set and never tested. They are kept that way, as in the submission, so numbers stay comparable; the manuscript says so. H2-A treats them differently (§H2-A, step 1).
- **Limitation, stated with §7's numbers:** on these single 10-fold rows the corrected test of §1.6 is approximate, and first-step power at d_z = 1 is 9–12 % (§7 A2, m = 10–16). §1.9 adds a repeated-10-fold sensitivity on the cheap arms.

### 1.2 Datasets without a shipped split (MSRC v2, Letter Frost, Letter Carroll, HJA Birdsong)
- Primary design: **repeated cross-validation, r = 5 repeats × k folds**; k = 5 for MSRC v2 and the Letter sets (as submitted), k = 10 for HJA Birdsong.
- Permutations from `numpy.random.default_rng(seed)`, seed ∈ {0, 1, 2, 3, 4}; every bag is used; fold j of repeat s = the j-th of k contiguous blocks of the permutation, sizes differing by at most 1. **Block rule (pre-deposit addendum, 2026-10-13):** blocks are `np.array_split(perm, k)`, so larger blocks come first; the same rule applies to the §1.9 outer blocks and to every ordinary inner split (§1.3); H2-A rows use the grouped inner rule of H2-A step 5.
- **Reason:** there is no canonical split to stay comparable with, and a single k = 5 run has very little power (§7).
- **Why 5×5 and not R1-M04's 10×10 (m7):** the nested library costs (outer folds) × (inner folds) × (candidates). 5×5 is 25 outer folds × 5 inner × 84 KDIS configurations; 10×10 would be 100 outer folds, 4× the cost, on top of the H2 and H4 arms. 5×5 already moves the first-step threshold from d_z 4.56 to 1.95 (§7 A1, m = 16).
- The submitted seed-42 5-fold results for MSRC v2 and the Letter sets are kept in a supplementary "as submitted" column.

### 1.3 Inner selection
- **Baselines (F4).** Every candidate configuration is scored by **inner 5-fold CV** on the outer training fold (inner 3-fold on VOC2012, §6.5).
  - Inner permutation seed = 1000 + outer-fold index + 100 × repeat; inner folds are contiguous blocks of that permutation. **(pre-deposit addendum, 2026-10-13)** Exactly: `np.random.default_rng(1000 + f + 100·r).permutation(tr)`, then `np.array_split(·, 5)` (3 on VOC2012), larger blocks first. The inner SD used in the tie-break has ddof = 1. **Inner training order (pre-deposit addendum, 2026-10-13):** within each inner training set, bags are passed to the library in ascending canonical bag index (this fixes MIMLNN's k-medoids path). The same applies to the H2-A grouped inner folds. **Refit training order (pre-deposit addendum, 2026-10-13):** the 100 % refit on the outer training fold also passes the outer-training bags in ascending canonical bag index, on every version and design (canonical, `rcv10`, §1.2, `submitted5`, rebuilt, purged). Purged (H2-B) versions use this ordinary inner rule; only H2-A rows use the grouped rule of H2-A step 5.
  - The candidate with the best mean inner score is **refit on 100 % of the outer training fold** and evaluated once on the outer test fold.
  - A candidate that crashes or times out (§6.6) in any inner fold of an outer fold is excluded from selection in that outer fold; exclusions are reported. **(pre-deposit addendum, 2026-10-13)** For MIMLNN, a crash in any (inner fold, seed) excludes that candidate for that outer fold. **Complex outputs (pre-deposit addendum, 2026-10-13):** if MIMLNN returns complex scores, the real part is used, the maximum |imag| is logged, and a unit with max |imag| > 1e-8 is flagged in the results.
  - **Refit failure (pre-deposit addendum, 2026-10-13).** Only selected candidates are refit: for the library procedure and for each of the 8 per-method nested selections, at most one per metric per outer fold; one refit serves every selection that chose the same candidate. If its refit fails, that (outer fold, metric) is recorded as failed and routed through the §6.7 stop rule; there is **no fallback to the runner-up**. **Consequence (pre-deposit addendum, 2026-10-13), orchestrator decision:** if the failure persists after the stop rule (no fix approved), the (dataset, metric, selection) row "did not complete". It is excluded from the Holm family for that metric and reported with the reason, and nothing is imputed. If a primary-family (F-H1) row is affected, that family's m is reduced and the reduction is stated.
- **Library procedure (F7).** "Tuned published library" is a *validation-selected procedure*. Per outer fold and per metric, it picks the best (method, distance, k) or MIMLNN (ratio, λ) by mean inner score, **all candidates scored by `miml_metrics.py` on dumped predictions** (§1.5, M4).
  - **Tie-break order:** better inner mean → lower inner SD → method name alphabetical → smaller k → **distance name alphabetical; for MIMLNN, smaller ratio → smaller λ** (pre-deposit addendum, 2026-10-13). **Tie tolerance (pre-deposit addendum, 2026-10-13):** two inner **means** are tied when |Δ| ≤ 1e-12 (absolute); the next criterion then decides. Inner SDs are compared exactly.
  - The selected candidate is stored per fold and **reported per fold in a supplementary table (dataset × metric × outer fold)**, so the stability of selection is visible (R5-03).
  - Each of the 8 published methods is also reported individually, with its own nested tuning. The response states that the comparator changed meaning (a per-fold validation-selected procedure, not a per-dataset test-selected maximum) and shows the per-method rows.
- **Selection per metric.** Each metric's baseline is tuned on that metric's inner score, the most favourable choice for the baselines.
- **Ours (F5, F6), unchanged from the submission.**
  - TabPFN context = `fit_i = tr[v:]`, v = max(1, ⌊0.2·|tr|⌋); `val_i = tr[:v]` is the validation set.
  - **Order of `tr` (round 3 m1):** on the canonical 10CV sets, as `get_cv_splits` returns it (the permutation with the test block removed, in permutation order). On the §1.2 and §1.9 repeated designs, the same rule: that repeat's permutation with the test block removed, in permutation order. On H2-A rows, the rebuilt training bags in ascending canonical bag index. On H2-B rows, the canonical `get_cv_splits` order with emptied bags removed.
  - **Declared handicap:** our model sees 80 % of the training bags while baselines are refit on 100 %.
  - **Disclosed quirk (F4):** `tr[:v]` gives the same validation bags for outer folds 2..9 on the 10CV sets.
  - Per-label thresholds are tuned for Hamming loss on `val_i`.
  - **MIML-PFN's only tuned quantity is the per-label Hamming-loss threshold, selected on `val_i` inside the outer training fold.** AP, one-error, coverage and ranking loss for MIML-PFN involve no selection of any kind. A fixed-0.5-threshold Hamming row is reported as a sensitivity check. The manuscript states this sentence (R5-03).
  - KDIS and MIMLNN produce bipartitions natively; that procedure is documented per method in the manuscript (R1-M08, R6-M05).
- **Degenerate labels (F4).** A label with no positive bag in a training split is predicted constant negative for that split (this is what the harness already does). **(pre-deposit addendum, 2026-10-13)** The same rule is applied identically to library (KDIS and MIMLNN) outputs: such a label's scores and bipartition are overwritten with constant negative before scoring. **Score value (pre-deposit addendum, 2026-10-13):** the constant-negative score is 0.0 for KDIS and −1.0 for MIMLNN, with the bipartition set to negative. For TabPFN and logreg, a label constant in `fit_i` is not fitted (its constant value is predicted), and timing projections count non-constant labels only (§6.3). The metric conventions of `miml_metrics.py` (written into the manuscript per R1-m05) apply identically to every method.
- **Stochastic baselines (F8).** MIMLNN (k-medoids initialisation) runs with Octave seeds {0, 1, 2, 3, 4} per configuration ({0, 1} on VOC2012). **Meaning of "seed" (pre-deposit addendum, 2026-10-13):** the authors' files are not modified; seeding goes through a `clock.m` shim on the Octave path. The authors' `MIML_cluster.m` reseeds itself internally with `rand('state', sum(100*clock))`, which would overwrite any state set before the call. The shim (`experiments/lamda/seed_shim/clock.m`, ours) returns `[s 0 0 0 0 0]/100` while it is on the path, so that internal call becomes `rand('state', s)`. "Seed s" means exactly that; with no seed set, the shim raises an error (no silent fallback to the clock). Selection uses the inner score averaged over seeds; the outer-test metric is the **mean over seeds**, not an ensemble of their predictions. Grid: ratio ∈ {0.2, 0.4, 0.6} × λ ∈ {0.1, 1, 10} (released defaults 0.4 and 1). KDIS methods are deterministic given the data; T03-a (§6.8) checks this. ~~If it fails the same seed rule applies to KDIS.~~ **KDIS non-determinism fallback (pre-deposit addendum, 2026-10-13):** if T03-a finds a KDIS method non-deterministic on Letter Frost, **that method** is run 5 independent times per (candidate, fold), and its metrics are averaged before selection, the same treatment as MIMLNN's seeds. KDIS exposes no seed, except MIMLBagging's own `<seed>`. The other methods' repetitions are therefore uncontrolled; this is disclosed, and the across-run SD is reported. **MIMLBagging labelling (pre-deposit addendum, 2026-10-13), DECISIONS row (13):** `seed-sK` (with `<seed>` fixed to 0–4) is used only where `<seed>` demonstrably controls MIMLBagging's randomness, i.e. its runs are byte-identical under one fixed seed. If T03-a finds MIMLBagging non-identical despite its shipped fixed `<seed>`, the seed does not control its randomness, and its 5 repetitions are labelled uncontrolled (`rep-r0..r4`, `uncontrolled: true`), like the other methods'. In repetition k its `<seed>` is still set to k (k = 0..4), so its five configurations are not nominally identical; the runs nevertheless remain labelled uncontrolled (pre-deposit addendum, 2026-10-13). Because the fallback is triggered for a method only by non-identical runs, a MIMLBagging fallback will in practice use `rep-r0..r4`. The repetition harness is added and code-reviewed before any KDIS production run. Selection rules are unchanged. **Tokens and switch (pre-deposit addendum, 2026-10-13):** repetitions are stored as separate units under the §1.5 condition tokens `seed-s0..s4` (MIMLBagging, only as stated above) and `rep-r0..r4` (every other case), joined with `+` to any other token. Whether a method is repeated is decided **only** by the T03-a result file, never by hand or by any result on a production dataset.
- **KDIS grid:** 7 methods (MIMLkNN, DMIMLkNN, MIMLBRkNN, MIMLMAPkNN, MIMLIBLR, MIMLDGC, MIMLBagging) × distance {AveH, MaxH, MinH} × k {5, 10, 15, 20} = 84 configurations. All seven have a neighbourhood parameter in their shipped config (`numOfNeighbours`, or `nReferences` = `nCiters` = k for MIMLkNN and MIMLBagging's base learner). Every other line of each `<classifier>` block is the shipped one, verbatim.
- **Selection optimism (F4).** For every dataset: AP(test-fold-selected, as submitted) − AP(nested).

### 1.4 Preprocessing (M3)
- **KDIS and MIMLNN receive raw instance features**, exactly as their authors' released code expects and as in the submission; no standardisation is applied for them. This holds for the original, rebuilt (H2-A), purged (H2-B) and de-duplicated versions alike. The manuscript states it (R6-M05).
- **VOC2012 only:** every method, KDIS and MIMLNN included, receives instance features reduced by PCA to 128 dimensions. PCA (centred, unscaled, `sklearn.decomposition.PCA(n_components=128, svd_solver="randomized", random_state=0)`) is fit on the instances of the outer training fold only and applied to that fold's training and test bags. Inner folds reuse the outer fit (label-free; disclosed). **(pre-deposit addendum, 2026-10-13)** The instance PCA-128 is fitted per outer split **before** any H4 subsampling, and subsampling then draws from the projected instances.
- **TabPFN, logreg and the H5 neural models** z-score bag-level features with mean and SD of `fit_i` only (as in the submission; H5 previously used all rows and is corrected here).
- **Precision (pre-deposit addendum, 2026-10-13):** TabPFN arms use float32 throughout¹; H2-A rebuilt bags (materialised as float64) are cast to float32 so rebuilt and original rows share one precision. KDIS and MIMLNN inputs are written as **lossless float64** (the submitted ARFF export used `%.6g`); the revision's library rows are therefore not byte-comparable with the submitted ones, and the manuscript says so.
  - ¹ **Precision footnote (pre-deposit addendum, 2026-10-13):** instance features are float32 as loaded. The bag-level matrix is float32 for `tabpfn_bagmean` and `tabpfn_bagmax`. Arms that append the cardinality column are promoted to **float64**: `tabpfn_multiview`, including its H4 subsampled versions, `tabpfn_padded`, whose permuted columns come from the multiview matrix, and `tabpfn_bagmean_card`. This is exactly as in the submitted runner (`experiments/run_foundation_baselines.py`, where concatenating the integer cardinality promotes the row), and it is kept for byte-identical reproduction. Each unit's sidecar records the feature dtype.
- **Library I/O (pre-deposit addendum, 2026-10-13):**
  - Each KDIS unit reads a training ARFF and a test ARFF, as in the submission.
  - Every file of an outer fold declares the same nominal bag-id set: that fold's bag universe, which is the whole dataset for `original`, `rcv10` and `submitted5`, as in the submission's converter. On H2-B rows, training bags emptied by the mask are not in the universe and are left out of the id header.
  - **Disclosed:** MIMLIBLR uses the bag-id attribute as an input, so its output depends on the declared id set. This is a property of the library implementation and is reported as such.
  - The LAMDA MIMLNN code's removal of bags positive on every label is moot here: T01 found no all-positive bags.

### 1.5 Metrics and stored predictions (M4, B.6)
- **Primary:** Average Precision (AP). **Secondary:** Hamming loss, one-error, coverage, ranking loss.
- **Every number is computed by `../../../MIML_CLAM_Release/miml_clam/metrics/miml_metrics.py` from stored per-bag predictions**, for every method including KDIS and MIMLNN. Native library scoring is recorded beside it as a check only.
- **What is stored, for every method × dataset version × repeat × outer fold (and every inner fold of every candidate):** the test bag indices, the per-bag score matrix (n_test × L, float64), the binary prediction matrix (n_test × L), and for MIML-PFN also the validation scores and the tuned thresholds. One `.npz` per unit under `results/revision_r1/predictions/<dataset>/<version>/<arm>/<config>/<condition>/r<repeat>_f<fold>[_i<inner>].npz`, with a sha256 manifest:
  - `<version>` ∈ {original, rebuilt, purged, dedup, rcv10 (§1.9), submitted5 (the submitted seed-42 single 5-fold splits, `r0_f0..4`, used by T03-g and §6.9 on Letter Frost; Scene keeps `original`)};
  - `<arm>` is the method or TabPFN arm;
  - `<config>` is the candidate for library arms (method, distance, k / ratio, λ). For TabPFN arms it is the **width token**, `native` or `pca<d′>` (§6.4; e.g. `pca500`, `pca218`; per-dataset d′ (pre-deposit addendum, 2026-10-13)), so the manifest shows width as it shows device; an arm for which the PCA switch is a no-op, **defined as d ≤ 500, or d′ = d for an arm with d > 500 (§6.4)** (pre-deposit addendum, 2026-10-13), carries `native`. For logreg arms `<config>` is `default` (`LogisticRegression(max_iter=1000)`, no tuned quantity). For H5 it is the surrogate (below);
  - `<condition>` ∈ {main, leak, control-s0, control-s1, control-s2 (H2-B), padded-s0..s2, sub-f0.25-s0 … sub-single-s2 (H4), seed-s0..s4 (MIMLNN Octave seeds; H5 training seeds s0..s2; MIMLBagging under the KDIS fallback only where its `<seed>` demonstrably controls its randomness, §1.3 (pre-deposit addendum, 2026-10-13)), rep-r0..r4 (uncontrolled repetitions under the KDIS fallback of any KDIS method, MIMLBagging included when its `<seed>` does not control it (pre-deposit addendum, 2026-10-13))}. Tokens are joined with `+` when a unit has more than one, e.g. `control-s1+seed-s3` (MIMLNN under the H2-B control).
  - **Device token (round 6):** every TabPFN unit ends its `<condition>` with `+g` or `+mps` (`main+g`, `main+mps`, `leak+g`, `padded-s1+g`, …); CPU arms carry none. So the §1.9 MPS canonical run and the H1 G run of the same arm, and the T03-g (MPS) and §6.9 (G) runs, never share a path, and the released manifest shows the device of every TabPFN prediction.
  - **H5 key:** `<arm>` = the model (`mlp_bagmean`, `abmil`), `<config>` = the training surrogate (`bce`, `ranking`, `oneerror`, `coverage`, `smoothap`), `<condition>` = `seed-s0..s2`.

  - **One stored unit per seed token (pre-deposit addendum, 2026-10-13):** every `padded-sK`, `sub-…-sK`, `control-sK` and `seed-sK` condition is its own stored unit; "mean over seeds" is always an analysis step on stored predictions, never a stored quantity. **(pre-deposit addendum, 2026-10-13)** The same holds for each `rep-rK` repetition. Its sidecar records the repetition index, `uncontrolled: true` and, for MIMLBagging, the `<seed>` value used; MIMLBagging `seed-sK` sidecars record the seed.

  No two units share a path, and a writer refuses to overwrite an existing file (lesson 9). **Where two procedures name the same unit, the unit is fitted once and reused; the manifest lists every procedure that uses it.** The reuses fixed now (round 7):
  - **Device token in these bullets.** `<dev>` = `g`, or `mps` under the §6.1 MPS fallback.
  - **H1 leaky-column Yeast vs H3 Yeast pair.** When the widths coincide, the H1 leaky-column Yeast rows are the H3 units, i.e. `yeast/original/tabpfn_{multiview,bagmean}/native/main+<dev>` (no §6.4 trigger on Yeast, or bag-mean at d = 103 in any case). When the Yeast trigger fires, the leaky-column multiview row is a separate unit at `pca<d′>` and the H3 unit stays at `native`.
  - **§1.9 sixth run under the MPS fallback.** The H1 units are then `main+mps` on the canonical split, and the §1.9 sixth run reuses them.
  - **§6.9 on Scene.** The `tabpfn_bagmean` Scene run of §6.9 is the H1 Scene bag-mean unit (`scene/original/tabpfn_bagmean/<width>/main+<dev>`), reused.
  - **§6.9 on Letter Frost under the MPS fallback.** §6.9's Letter Frost `tabpfn_bagmean` unit is then `letter_frost/submitted5/tabpfn_bagmean/native/main+mps`, which **is the T03-g unit**, reused. In that branch §6.9 is reported as a **same-device environment check, not a cross-device check**.
  - **§5 outputs.** The two-fit and one-fit predictions of the §5 check are written under the dedicated condition tokens `verify-2fit` and `verify-1fit`, each with the device token of §6.1, on `scene/original` and `letter_frost/submitted5`. They are kept, never reused as H1 units, and deposited with the check's result.

  All stored predictions are released (R2-08 item 9).
- **KDIS cannot dump predictions as shipped.** `EvaluatorHoldout.runExperiment` passes the classifier straight to Mulan's `Evaluator` and `BaseMIMLReport` writes only aggregate measures. Each classifier does expose `MultiLabelOutput makePrediction(Instance)` (`external/MIML/mavenProject/src/main/java/miml/classifiers/miml/MIMLClassifier.java:145`), which carries confidences and a bipartition. We will therefore add a small Java wrapper, `experiments/kdis/PredictDump.java` (to be written before T03), compiled against the **unmodified** `miml-1.4-jar-with-dependencies.jar`: it configures the classifier from the same `<classifier>` block, calls `build` on the training ARFF, calls `makePrediction` on every test bag, and writes confidences and bipartitions. The library itself is not modified.
- **Construction artefacts (pre-deposit addendum, 2026-10-13):** H2-A and H2-B constructions are written to `results/revision_r1/constructions/<dataset>/rebuilt/r0_f<f>.npz` and `results/revision_r1/constructions/<dataset>/purged/<condition>/r0_f<f>.npz` (`<condition>` ∈ {leak, control-s0, control-s1, control-s2}), with `construction.json` / `masks.json` and a `MANIFEST.sha256` per directory.
- **MIMLNN:** our Octave driver (`experiments/lamda/run_mimlnn.m`, ours, not the authors' code) will be extended to request and save the function's score and label outputs. The authors' `MIMLNN.m` is not on disk at the time of writing and must be re-obtained from the LAMDA distribution (sha256 recorded) before T03-c.
- **Fallback, pre-stated.** If a harness cannot produce per-bag scores, its native scoring is accepted only if T03-f (§6.8) shows that the harness's own scoring code and `miml_metrics.py` agree to |ΔAP| ≤ 1e-3 on the same score matrices. If that check fails or cannot be run, the library procedure is split per harness (KDIS-library and MIMLNN reported as two comparators), never mixed across scorers.

### 1.6 Statistical test (F1, F2, F3)
**Test statistic.** The corrected repeated k-fold cv test (Remco R. Bouckaert and Eibe Frank, PAKDD 2004), built on the variance correction of Claude Nadeau and Yoshua Bengio (Machine Learning 52:239–281, 2003). Over the n = r·k fold differences d_j:

  t = d̄ / sqrt( (1/n + n₂/n₁) · s²_d ),  s²_d with ddof = 1,  df = n − 1,  two-sided.

For the single 10-fold designs, r = 1.

**n₁ and n₂, one rule for every comparison (M8).**
- n₂ = mean outer test-fold size actually used.
- n₁ = mean number of training bags actually used to fit **the arm with the smaller training set** in that comparison:
  - TabPFN, logreg and H5 neural arms: |`fit_i`| = 0.8 × outer training;
  - KDIS and MIMLNN: 1.0 × outer training;
  - H2-B: post-purge training bags (bags not emptied), times 0.8 for TabPFN/logreg arms;
  - H2-A: the rebuilt training set (remainder rows excluded), times 0.8 for TabPFN/logreg arms.
- Recomputed per comparison from the stored fold indices. §7 Part A is the MIML-PFN-vs-library table; Part C gives the other families.

**Why this is valid at k = 5 and k = 10 (R2-04, F3).**
- The paired t-test treats fold differences as independent. Overlapping training sets make them positively correlated, so the naive variance s²/n is too small (Thomas G. Dietterich, Neural Computation 10(7):1895–1923, 1998; Nadeau and Bengio 2003).
- The n₂/n₁ term inflates the variance by the correlation implied by the training/test overlap.
- Bouckaert and Frank showed close-to-nominal Type-I error and better replicability *when repeated*; hence §1.2. On the canonical single 10-fold splits the test is approximate (a Monte Carlo in PREREG__review_2 gave Type-I 0.067 at nominal 0.05); the manuscript states this beside §7's power numbers.

**Families and Holm (F2, B.3).** Holm step-down at α = 0.05 within each family:
- **F-H1 (primary, CONFIRMATORY), planned m = 16:** MIML-PFN (multiview) vs nested library, AP, one test per dataset, over **all** H1 rows: Scene, Reuters, MSRC v2, Letter Frost, Letter Carroll, Birds (MLSP 2013), HJA Birdsong, VOC2012, Protein ×4, and the H2-A rebuilt Emotions, Yeast, Medical and Corel5K. Eight rows carry "direction previously observed" (Labels).
- **F-H1-newdata (pre-specified sensitivity), planned m = 10, "no prior number on this data version":** the same tests, with Holm recomputed within the 10 rows that had no foundation-model number on that data version: HJA Birdsong, VOC2012, Protein ×4, and the rebuilt Emotions, Yeast, Medical and Corel5K (the rebuilt sets are new data, as listed in `DECISIONS.md` 2026-10-13, although the leaky Emotions and Yeast direction was seen; the qualifier stays on those two rows). Reported alongside the primary family, never instead of it.
- **F-H1-bagmean (and -newdata):** bag-mean TabPFN vs nested library, AP, same row sets.
- **F-H1-secondary-<metric>-<arm> (and -newdata):** one family per secondary metric × arm.
- H2, H4 and H5 families are defined in their sections.
- A dataset whose arm "did not complete" or was "not run, by user decision" (§6.6, §6.7) leaves its family; m shrinks accordingly and the exclusion is reported with hours spent or projected. A persistent refit failure removes only the affected (dataset, metric, selection) row from that metric's family (§1.3) (pre-deposit addendum, 2026-10-13).
- The leaky originals of the four constructed sets are in no H1 family (reported beside the rebuilt rows, EXPLORATORY).
- **Power consequence of the 16-row family:** first-step d_z,min rises from 1.80 (m = 10) to 1.95 (m = 16) on single 10-fold rows (§7 A1).

**Global hypothesis (M2).**
- **Confirmatory global test:** Wilcoxon signed-rank test (Janez Demšar, JMLR 7:1–30, 2006), **two-sided**, on the per-dataset mean AP differences (multiview − library) of **all F-H1 rows** (n = 16 if all complete), computed by `scipy.stats.wilcoxon(d, alternative="two-sided", method="exact", zero_method="wilcox")` in scipy 1.18.0 (the `.venv` version, recorded with the results). Zero differences are dropped and n is reduced, as `zero_method="wilcox"` does. With continuous AP differences, ties are not expected; if they occur, the call is run as written and the tie count is reported.
- **Sensitivity global test:** the same test on the F-H1-newdata rows (n = 10), reported alongside.
- **Location estimate with CI:** the Hodges–Lehmann median of the Walsh averages (Joseph L. Hodges Jr. and Erich L. Lehmann, Ann. Math. Statist. 34(2):598–611, 1963), with its exact 95 % CI from the Wilcoxon critical value.
- **Effect size:** the matched-pairs rank-biserial correlation r = (T⁺ − T⁻) / (T⁺ + T⁻), from the signed-rank sums.
- **Pseudo-replication sensitivity (pre-registered, reported beside the primary):** the four protein sets share feature extraction and construction, and the two Letter sets share a generator, so each family is collapsed to its mean difference: proteins → 1 and Letters → 1 for the primary test (n = 12); proteins → 1 for the new-data test (n = 7). Birds (MLSP 2013) and HJA Birdsong are kept separate (no shared instance vectors, T01 §6).
- **Power, stated now (§7 D):** under the heterogeneity already observed, the primary global test (n = 16) has power ≈ 0.25–0.37 and the new-data test (n = 10) ≈ 0.17–0.26; a non-significant result is the likely outcome and is pre-worded below.
- Per-dataset Holm results describe *where*.

**Reporting.**
- For every test: raw p, Holm-adjusted p, mean Δ, 95 % CI (corrected variance, unadjusted), d_z = d̄ / s_d (named "uncorrected standardised mean difference"), and t. (The v2 quantity "d_z,corr" was algebraically t/√n and is dropped, m1.)
- **Per-fold SD of every arm in every results table** (m10, R6-M08).
- The uncorrected `ttest_rel` appears only in a supplementary table, labelled.
- **No "folds in agreement" count** (the submitted Table VI column, and phrases such as "better in 10 folds of 10") appears in any revision table or sentence, as evidence or as description (R5-04, R2-04).

**Outcomes and wording (F3, B.7).**
- A Holm-significant difference is a "win" or a "loss". Anything else is "**not significant**", never "tie" or "equivalent". No equivalence claims.
- **Practical threshold, per dataset and metric:** δ_ds = SD (ddof 1) over outer folds of the **comparator arm's** score on that dataset version under this protocol. The comparator is the nested library in H1, the random control in H2-B, bag-mean in H4, and the model trained on B's own surrogate in H5. A Holm-significant difference with |d̄| < δ_ds is worded "**statistically detectable, practically small (|Δ| below one fold-SD of the comparator)**", and is never counted with differences of |d̄| ≥ δ_ds in any sentence without that qualifier.
- Rows with practically small effects (whatever their p) are never summed with native-set wins in any count without that qualifier.
- The 0.006 band is retired; it appears only inside the original MIML-PFN rule (H3).
- Non-significance on rows that §7 marks underpowered is "**inconclusive**", not "no effect".

**Pre-written abstract sentences for the global test (M2).** Exactly one of G1–G3, filled with the obtained numbers, followed in every case by the F-H1 Holm counts (with the number of "direction previously observed" rows among the wins and losses), then one sentence giving the sensitivity result on the datasets "with no prior number on this data version (two of which, rebuilt Emotions and Yeast, had a previously observed direction on their leaky versions)" (global p, HL median and CI, Holm counts):
- **G1** (p ≤ 0.05, HL > 0): "Across all [n] datasets, MIML-PFN's average precision exceeded the nested, validation-selected published library (two-sided Wilcoxon p = …; Hodges–Lehmann median ΔAP = … [95 % CI …]; rank-biserial r = …)."
- **G2** (p ≤ 0.05, HL < 0): the same sentence with "fell below".
- **G3** (p > 0.05): "Across all [n] datasets, the global test was not significant (two-sided Wilcoxon p = …; Hodges–Lehmann median ΔAP = … [95 % CI …]; rank-biserial r = …); per-dataset Holm tests found X wins, Y losses and Z non-significant differences."
- If losses outnumber wins in either family, the abstract says so.

### 1.7 Hygiene
- No dataset is dropped post hoc. A technical failure is reported as a failure, with measured compute (§6).
- One results file per concurrent writer, under `results/revision_r1/`.
- All seeds are listed in this file.

### 1.8 Deposit and release
**Deposited before step 1 of either queue (§6.0)**, and therefore before any T03, §5 or pilot output exists, with sha256 of each file. The deposited v3 is a **git-committed** file. The deposited copy reads "to be filled" in its own "Deposited version" row. A follow-up commit then records that copy's commit hash, sha256 and the archive URL/DOI. **The checksum of the copy held by the public archive is binding**: if any later local text differs from it, the archived copy governs.

**Public-timestamp cell and real-data guard (pre-deposit addendum, 2026-10-13), DECISIONS row (12).** After the deposit, the orchestrator writes the Public-timestamp cell of the header (currently "PENDING") in exactly this form: `https://doi.org/<DOI> (YYYY-MM-DD)`. `<DOI>` is the DOI of the **published** (not draft) record and matches `10\.\d{4,9}/[A-Za-z0-9._;()/:-]+`; the date is the record's publication date. Every tool (T02, T03, T04/T07) uses one shared function, `experiments/revision_r1/deposit_check.py::deposit_recorded()` (committed, `933b185`). It accepts only a whole-cell full match of that grammar. **Tightened (pre-deposit addendum, 2026-10-13), DECISIONS row (14), which can only close the guard:** matching is ASCII-only (`re.ASCII`); the DOI suffix must end in a letter or digit (`[A-Za-z0-9]`), so a trailing `.`, `;`, `)`, `-` or `/` closes the guard; and the date must be on or after 2026-10-13, the earliest possible deposit date. **(pre-deposit addendum, 2026-10-13), DECISIONS row (15), close-only:** the date must also be no later than the current UTC date at the time the check runs. **Further close-only rules enforced by `deposit_check.py` (pre-deposit addendum, 2026-10-13):** the DOI must not look like a placeholder (a run of three or more `N` or `X`, case-insensitive, or `...`), must not use the DataCite test prefix `10.5072/` (issued by the Zenodo sandbox), and must not contain "sandbox". Anything else (free text, a draft, a placeholder, another host) keeps the real-data guard closed, and no tool touches real data. `__pycache__` and other generated files are excluded:
- this file (v3), `experiments/revision_r1/power_table.py`, its output `revision_access_44676/evidence/T05__power_table.txt`;
- `experiments/miml_pfn/PREREGISTERED.md`, `AMENDMENT.md` and `RESULT.md`, unchanged, with the local dates in the header table and the statement that they were local, unversioned files until 2026-10-12;
- `experiments/revision_r1/history/PREREGISTERED_v2.md`, and `../../revision_access_44676/reviews/PREREG__review_1.md` to `PREREG__review_4.md` (review 1 is the only record of v1). Any later review files are added the same way.
- `../../revision_access_44676/evidence/T02__duplicate_pool_check.txt`, the source of the H2-A rule-B counts (pre-deposit addendum).

**Released with the revision (release task T11, to be created; m4, R2-03, R2-08):** the converter `../../../MIML_CLAM_Enhanced/convert_new_datasets.py` (functions `convert_birdsong`, `convert_protein`, `convert_yeast`, `convert_emotions`, `convert_medical`, `convert_corel5k`) and source checksums; `../../../MIML_CLAM_Enhanced/datasets/build_hja_birdsong.py`, `voc_miml.py`, `build_voc_patch_gt.py`, `build_voc_seg_subset.py`; the observation-to-bag mappings `results/provenance_bag_rows_{emotions,medical,yeast,corel5k}.csv`; the H2-A construction script and its per-split bag→source-row mapping; the H2-B purge masks and control masks; all stored predictions (§1.5); every results JSON; the VOC2012 files listed in §0.1. Third-party data whose licence forbids redistribution are replaced by scripts plus checksums.


### 1.9 Repeated-10-fold sensitivity on the canonical-split datasets (R5-04, R2-04)
**Label:** EXPLORATORY. Purpose: show whether the single-run verdicts of §1.1, including the multiview headline rows, survive repetition, for the arms that fit the gates below.
- **Datasets:** the native canonical-split datasets: Scene, Reuters, Birds (MLSP 2013), Protein ×4, VOC2012. (The constructed sets are excluded: H2-A is tied to the canonical folds.)
- **Design:** r = 5 repeats × 10 folds, permutations from `numpy.random.default_rng(seed)`, seed ∈ {10, 11, 12, 13, 14} (disjoint from §1.2's seeds), every bag used, contiguous blocks.
- **Arms, cheap ones only:**
  - logreg bag-mean and logreg multiview: always;
  - TabPFN bag-mean **and TabPFN multiview** on the **local MPS backend** (one of the two MPS exceptions in §6.1, with T03-g; compared only with MPS results). Each arm is planned within 72 MPS-hours per dataset; **(pre-deposit addendum, 2026-10-13)** the gate includes the sixth (canonical) MPS run (conservative). Multiview uses the PCA decision of §6.4 for that dataset;
  - nested library: planned within 300 process-hours per dataset for this design.
- **Gates go through the stop rule (round 4 m2):** an arm whose projection exceeds its gate is held. Projections are recorded, and an extension is requested through a dated AMENDMENT (§6.7). The arm is dropped only by a user decision recorded in `DECISIONS.md`, and is then reported as "not run, by user decision [date], projection [h]".
- **Same-device comparison (round 4 m5):** each §1.9 TabPFN arm also runs once on the **canonical** split on MPS (a sixth run). The repeated-CV results are compared with that MPS canonical run, never with the G canonical run. The library and logreg arms are device-independent (CPU).
- **Contrasts:** each available arm vs the nested library (where run), §1.6 test at r = 5, k = 10.
- **Reported:** the repeated-CV t, p, mean Δ and CI beside the canonical single-run values for the same contrast **on the same device**; whether the sign and the unadjusted p < 0.05 verdict agree. No Holm family; no headline use.
- Budget: execution position 8 (§6.7).

---

## H1: MIML-PFN vs published methods under nested selection

**Labels:** F-H1 **CONFIRMATORY** on all rows, eight of them "direction previously observed"; F-H1-newdata is a pre-specified sensitivity analysis (user decision 2026-10-13). The submitted test-selected comparison is **POST-HOC** (B.3, R2-07). Addresses R1-M03, R1-M08, R2-01, R2-02, R3-01, R3-02, R5-03, R6-M02, R6-M05.

- **Arms.** `tabpfn_multiview` (MIML-PFN as defined in the manuscript) and `tabpfn_bagmean`. Each gets its **own** record and is **never pooled** into a single count.
- **Rows.** As listed in §1.6. For the four constructed sets the H1 row is the **H2-A rebuilt** version. The leaky original is reported beside it, labelled "leaky (constructed by the authors)", EXPLORATORY, in no family.
- **Non-comparability (M6).** Rebuilt bags come from pools one tenth the size of the original construction, so their neighbourhoods are sparser. Rebuilt absolute APs are not comparable with the leaky rows, and "leaky − rebuilt" is never presented as a leakage estimate; that is H2-B's job. This sentence goes into the manuscript.
- **Decision.**
  - The abstract states one of G1–G3 (§1.6), then the F-H1 Holm W/L/NS counts for MIML-PFN, then the new-data sensitivity result, exactly as obtained.
  - The bag-mean arm's counts are stated separately and never summed with the multiview counts.
  - If losses outnumber wins, the abstract says so.
- **Reuters de-duplicated sensitivity (EXPLORATORY; B.2, R2-03 flag b).** 3.7 % of Reuters test bags are identical to a training bag (T01 §5, same definition as `results/provenance.json` `leakage`). For every H1 arm and the library, Reuters is also scored with those test bags removed from each outer test fold (rescoring stored predictions; no refit), and tested with §1.6. The native-set overlap table (exact-duplicate overlap for Reuters, MSRC v2, the Letters and the proteins, T01 §5) is reported in the manuscript beside the constructed-set table.
- **Stress test (POST-HOC).** The submitted test-selected numbers appear in one supplementary table titled as an optimistic-for-baselines stress test. They are never used for p-values.

## H2: leakage in the constructed sets

**Label:** CONFIRMATORY (H2-B family). Addresses R2-03, R6-M01, R1-M02 (F12–F15).

The four constructed sets were built by us and leak by construction (DECISIONS.md, 2026-10-12; T01 §A, §5). H2 measures how much that leakage changes scores, and provides the leakage-free version used in H1.

**Overlap quantification, reported for every outer fold** (from `verify_knn_bags.py`; R2-03, F13): share of test bags with at least one instance vector in training bags; share of test instances present in training bags; share of test-bag centres inside training bags; mean max Jaccard of a test bag's source set with a training bag; share of test bags identical to a training bag. The same quantities are reported for the H2-A rebuilt versions, where every source-example overlap must be 0; a non-zero value stops the run as a construction bug.

### H2-A: per-split grouped rebuild (B.1, M6, R2-03 flag a)
One construction **per outer split f = 0..9** of each constructed set, on the canonical `*_10CV.mat` folds:
1. **Pools.** Source rows are identified by the identity mapping (bag i is centred on source row i, T01 §3). Pool P_g = the source rows of canonical fold block g. **The n mod 10 remainder rows (3 / 7 / 8 / 3) are excluded from every pool and every bag**, so no row sits in a training pool for one split and nowhere for another. The rebuilt training set for split f = the bags centred on ∪_{g≠f} P_g; the test set = the bags centred on P_f.
2. **Scaler.** `StandardScaler` with the original recipe's convention (population SD, ddof 0; zero-variance columns unscaled), **fit on the source rows of ∪_{g≠f} P_g only** (outer-training rows of split f) and applied to every row. No test-fold statistic enters any bag.
3. **Bags.** Bag of row i ∈ P_g = row i + its 4 nearest neighbours among P_g \ {i}, Euclidean distance on the scaled features (direct differences, not the expansion |a|²+|b|²−2ab). Ties at equal distance: lower source index wins (F14); **(pre-deposit addendum, 2026-10-13)** distances are computed with `math.fsum`, and distances equal within relative tolerance 1e-9 form a tie group, lower index first. ~~Duplicate source rows are kept as distinct examples~~ **Duplicates, rule B (pre-deposit addendum, 2026-10-13):** H2 uses vector-id identity throughout. Before pooling, every source row whose vector duplicates a lower-indexed row is dropped (the lowest index of each group is kept, regardless of labels). It is removed from the bags, the neighbour candidates, the scaler fit and the test pools. That is Medical 11 of 978 rows and Corel5K 2 of 4873 (`../../revision_access_44676/evidence/T02__duplicate_pool_check.txt`). If a group's lowest row is a remainder row, the vector leaves H2-A entirely (no such group exists). Three groups have the same features but different labels (Medical 2, Corel5K 1). In the original files and in H2-B, where both rows remain, they are irreducible error, not leakage, and are disclosed. In H2-A, rule B leaves no duplicate, so only the lowest-indexed row's labels survive (label-agnostic, as stated). Stored instance features are **raw**, as in the original files; labels = the centre's labels (T01 §3).
4. **Consequence.** Within split f, no source example contributes to both a training and a test bag, and test bags are built from test rows only (R2-03's grouped design, not the inductive `FlatKNNBagDataset` design; the manuscript names which). ~~Every pool has the same size ⌊n/10⌋.~~ **Pool sizes (pre-deposit addendum, 2026-10-13):** after rule B, pools are ⌊n/10⌋ minus the dropped duplicates in that block. Emotions and Yeast are unchanged. Medical: pools 0, 1, 2, 3, 6 and 9 lose 1 row, pool 4 loses 2 and pool 7 loses 3, so test folds 0, 1, 2, 3, 4, 6, 7 and 9 lose bags and pools 5 and 8 lose none (sizes 96, 96, 96, 96, 95, 97, 96, 94, 97, 96 of ⌊978/10⌋ = 97). Corel5K: pools 4 and 5 lose 1 row each (486 of 487). Pool sizes are reported per split. **H2-A acceptance check (pre-deposit addendum, 2026-10-13):** `construction.json["duplicates"]` must list exactly the dropped rows of this step (Medical 445, 301, 246, 310, 376, 607, 818, 398, 357, 853, 873; Corel5K 2465, 4676), and the pool sizes must equal those above; a mismatch stops the construction (correctness only). **Overlap is checked at vector level**, and any non-zero vector overlap between training and test bags is a hard stop.
5. **Inner selection on H2-A rows.** Library inner CV is grouped by pool: the 9 training pools of split f are ranked by fold index and pool of rank ρ goes to inner fold ρ mod 5, giving inner folds of 2, 2, 2, 2 and 1 pools. MIML-PFN keeps `tr[:v]` (§1.3) over the rebuilt training bags in ascending canonical bag index; its validation and context bags can share pool rows, which affects Hamming thresholds only and is disclosed.
6. These rows are the H1 rows for the four sets (§H1).
7. **Test-bag order (pre-deposit addendum, 2026-10-13):** test bags in each rebuilt file are stored in canonical block order, i.e. fold f exactly as `get_cv_splits` returns it (no metric depends on this order).

### H2-B: instance-level purge on the original bags (B1)
This isolates the effect of *which* training rows are present, at matched bag count, instance count, per-bag cardinality **and centre survival** (round 3 B1).
- **Source identity = vector id (round 4 m1).** In H2, a source example is identified by its **vector id**: a source row byte-identical to a lower-indexed source row is identified with that row, for centres as for members. This is the map `verify_knn_bags.py` uses for `member_rows`; it is applied to `centre_row` too. Medical has 11 such duplicate rows and Corel5K 2; Emotions and Yeast have none.
- **Centre row, as an instance position.** The centre row of bag i is the first instance of the bag that equals source row i. Any further identical instance in the bag is a non-centre row.
- **Leak purge.** In each outer fold f of the original file, let S_f = the set of vector ids (from `results/provenance_bag_rows_<dataset>.csv`, centres mapped to vector ids) occurring in any test bag. From every training bag, delete each instance row whose source index is in S_f. A bag left with zero rows is dropped. Test bags are unchanged. (A training bag whose centre row is deleted keeps its centre's labels.) **Check:** in every fold, the share of test instance vectors present in surviving leak-purge training bags must be exactly 0; a non-zero value stops the run as a construction bug.
- **Size- and centre-matched random control (stratified on centre status).** For every training bag, let k = the number of its rows the leak purge deleted. The control deletes the bag's **centre row if and only if the leak purge deleted it**, then deletes the remaining k − 1{centre deleted} rows uniformly at random among that bag's **non-centre** rows, with `numpy.random.default_rng(seed)`, seed ∈ {0, 1, 2}. Bags emptied by the leak purge (k = 5) are therefore emptied in the control too. Metrics are averaged over the 3 seeds per fold before testing.
  - **RNG draw order (pre-deposit addendum, 2026-10-13):** a fresh `numpy.random.default_rng(seed)` per (dataset, fold). Training bags are visited in canonical `get_cv_splits` order; for each bag with m = k − 1{centre deleted} > 0 the control calls `rng.choice(non_centre_positions, size=m, replace=False)`; bags with m = 0 draw nothing.
  - **Acceptance check (pre-deposit addendum, 2026-10-13):** the fold means written to each `purged/masks.json` must reproduce the table below **at the printed precision of each column** (rows left per surviving bag to 2 decimals, i.e. ±0.005; every other column as printed, to 3 decimals, i.e. ±0.0005; bags emptied as a fraction to 0.1 %, i.e. 3 decimals of the fraction), which is what `h2_acceptance.py` checks; a mismatch stops the H2-B runs (correctness only; decides nothing about outcomes).
  - **Why stratified.** The leak purge deletes neighbours far more often than centres: S_f holds every test row plus the training rows adjacent to one, and a training bag's centre is deleted only in the second case. A uniform draw of the same count would delete the label-carrying centre with probability k/5. Recomputed on vector ids from `results/provenance_bag_rows_*.csv` on the canonical folds (mean over folds; surviving training bags):

    | dataset | training rows removed | bags emptied | rows left per surviving bag | centre deleted, leak purge [min–max over folds] | centre deleted, an unstratified uniform control would give |
    |---|---|---|---|---|---|
    | Emotions (0 duplicate rows) | 0.468 | 6.4 % | 2.84 | 0.238 [0.193–0.275] | 0.432 |
    | Yeast (0) | 0.457 | 5.7 % | 2.88 | 0.255 [0.230–0.267] | 0.424 |
    | Medical (11) | 0.629 | 13.6 % | 2.14 | 0.076 [0.051–0.097] | 0.571 |
    | Corel5K (2) | 0.675 | 8.3 % | 1.77 | 0.054 [0.050–0.058] | 0.645 |

    Under the raw-index definition of the round-3 draft, Medical gave 0.628 / 12.8 % / 0.073 and left 6–10 surviving training bags per fold containing a test vector; on vector ids, that overlap is 0.

    An unstratified control would add label noise to the control arm alone (bags whose labels belong to a deleted row) and bias the effect downward. The stratified control has, by construction, exactly the leak purge's centre-deletion rate in every fold.
- **Leakage effect** = AP(random control) − AP(leak purge), paired over folds, §1.6 test with n₁ = post-purge training bags (× 0.8 for TabPFN/logreg arms). Positive means the removed rows inflated scores.
- **Descriptive statistics reported, per fold:** the table above (rows removed, bags emptied, rows left per bag, centre-deletion rate); and the bag-level purge fractions (≈ 0.90 / 0.91 / 0.97 / 0.99), which make a bag-level purge infeasible and are why it is not used (PREREG__review_2 computation (b)).
- **Not estimable:** if the leak purge removes more than 80 % of training instance rows in any fold of a dataset, that dataset's H2-B rows are reported "not estimable" and leave the family. **(pre-deposit addendum, 2026-10-13)** Masks are still written for such a dataset and flagged `not_estimable: true` in `masks.json`.
- **Interpretation (upper bound).** With bag count, cardinality and centre survival matched, the arms differ only in *which* neighbour rows were removed. The purged neighbours lie, by construction, near test rows, so the leak purge also removes legitimately similar, distinct examples that a leakage-free training set would contain. That residual difference biases the effect upward only. A positive effect is therefore an **upper bound** on leakage inflation, never "leakage alone", and is worded so.
- **Label carriage, disclosed.** In both arms a bag whose centre is deleted keeps labels that no remaining instance carries. Its rate is the centre-deletion column above (5–26 % of surviving bags), identical in both arms.
- **Representation, disclosed (round 3 m7).** After the purge the mean surviving bag has 1.8–2.9 rows, so the multiview statistics (SD, quantiles, max, min) are degenerate for many bags in both arms. The H2-B multiview rows measure leakage on a representation that has largely collapsed toward bag-mean; the manuscript says so. Single-row bags have SD = 0 and every quantile equal to the row; no special handling is applied.

### H2 methods, family and decision
- **Methods (7):** logreg bag-mean, logreg multiview, the nested library, MIMLkNN on its own (nested over its own 12 configurations; the most neighbourhood-sensitive method), MIMLNN (nested), TabPFN bag-mean, TabPFN multiview. TabPFN arms run at execution position 5 (§6.7).
- **Family:** all estimable (method × dataset) H2-B tests, planned m = 28, Holm α = 0.05.
- **Decision wording, fixed per outcome:**
  - (i) **≥ 1 significant positive effect:** "removing the test folds' neighbourhoods from training lowered scores for [methods] on [datasets], an upper bound on leakage inflation of [Δ]".
  - (ii) **none:** "these files leak by construction (overlap reported), but the measured upper bound on its effect is not significant" (with §7 C's power: inconclusive, not "no effect").
  - (iii) **significant negative effects:** reported as contradicting the leakage story.
- **Interpretation (F15).** Whatever the outcome, the four sets remain constructed by us; their use as labelled negative controls rests on T01 (provenance), not on H2.

## H3: the original MIML-PFN rule, completed

**Label:** CONFIRMATORY, as originally registered (F16, F17).

**Primary rule.** The rule in `../miml_pfn/PREREGISTERED.md` is evaluated exactly as written, including the 0.006 band, with Yeast included once its multiview arm completes.
- **Yeast** uses its canonical split and the leaky original file, because that is what the rule was registered on, at native width d = 6·103 + 1 = 619 (no PCA: the registered rule had none).
- **Same device (M7).** Yeast `tabpfn_bagmean` (140 fits, d = 103) is rerun on the TabPFN device of §6.1 and the rule is evaluated on that same-device pair. The stored MPS bag-mean result is reported beside it.
- **Birds (MLSP 2013)** keeps its submitted MPS pair and is not rerun.
- **Hardware-sensitivity flag (F16 ii, M7).** Any dataset whose rule margin satisfies |margin − 0.006| < 1e-3 is flagged "hardware-sensitive" in the manuscript. Birds (margin 0.005998) is flagged by construction.
- **Budget.** Yeast multiview is subject to §6's per-unit cap and stop rule. If its projection exceeds the cap, execution stops before it and an extension is requested (§6.7). If the user declines, or the run hits §6.6's limit and no extension is granted, it is recorded as "did not complete" a second time.
- **Pre-written abstract wording:**
  - (a) primary, as of submission: "failed its pre-registered rule (3 of 4; one dataset incomplete)";
  - (b) upon completion, if Yeast wins: "the rule's last dataset, completed during revision, met the bar (4 of 4)";
  - (b′) if Yeast does not win: "failed (3 of 4) after completion";
  - (b″) if not run or not completed: "the rule's last dataset again did not complete within the pre-registered budget".
  - (a) and exactly one of (b), (b′), (b″) appear in the abstract.

**R2, from AMENDMENT.md.** Evaluated exactly as amended, on {Reuters, 4 protein sets}; §6.4 fixes the PCA budget AMENDMENT.md left open.

## H4: what the multi-view gain comes from

**Labels:** `tabpfn_bagmax` **EXPLORATORY** (registered 2026-08-14, never run); `tabpfn_bagmean_card`, the width-matched control and the instance-subsampling curve **POST-HOC** (chosen after multiview results were seen). Addresses R1-M05, R5-02, R6-M03 (TNEW-dim-control).

**Rows:** the 16 H1 rows (rebuilt versions for the constructed sets).

**Classifier, identical for every H4 arm:** TabPFN only, `TabPFNClassifier(device=G, n_estimators=8, random_state=0, ignore_pretraining_limits=True)` (the harness's settings; T07 confirms 8 and 0 are the v2.2.1 defaults), same `fit_i` z-scoring, same per-label binary relevance, and, where §6.4 triggers on that dataset, the same PCA to d′ (`pca<d′>`, §6.4) (pre-deposit addendum, 2026-10-13). No logreg or library arm enters H4.

**Arms:**
- `tabpfn_bagmean`, `tabpfn_bagmax`, `tabpfn_multiview`;
- `tabpfn_bagmean_card` (bag-mean + bag cardinality as one scalar), **run only on the 10 rows with variable bag size**. On Scene, VOC2012 and the four rebuilt sets cardinality is constant, so `bagmean_card` is **not run**; its row reuses the bag-mean result, labelled "= bag-mean (constant cardinality)" (m5);
- **`tabpfn_padded`, the width-matched control (B.8, R5-02).** Exactly the multiview width 6d + 1, built from **real columns permuted within column**, never from noise: the multiview matrix with its d bag-mean columns kept, and each of the other 5d + 1 columns (max, min, SD, q25, q75 blocks, and **the +1 column, which is the cardinality column**) independently permuted across bags **within the outer training fold** and, separately, **within the outer test fold**, so no value moves between folds. Every padded column therefore has the same marginal distribution as the multiview column it replaces, but no association with its bag. Permutation seeds {0, 1, 2} (`numpy.random.default_rng(seed)`, one permutation per column per fold); the fold metric is the mean over the three seeds, taken at analysis from the three stored per-seed units (§1.5). **Draw order (pre-deposit addendum, 2026-10-13):** a fresh `default_rng(seed)` per outer fold. It first calls `rng.permutation(n_train)` once per padded column, for the columns j = d, …, 6d (0-based; the 5d + 1 non-mean columns) in ascending order, over all outer-training rows (`val_i` and `fit_i` together). It then calls `rng.permutation(n_test)` once per padded column, in the same column order. z-scoring on `fit_i` follows.
- **Instance-subsampling curve.** `tabpfn_multiview` and `tabpfn_bagmean` recomputed from a random subset of each bag's instances, in training and test bags alike: fraction f ∈ {0.25, 0.5, 0.75} of each bag's n_i instances, keeping ⌈f · n_i⌉ (at least 1), plus a **single-instance** row (1 instance per bag); f = 1.0 is the full arm. Subset drawn by `default_rng(seed)`, seeds {0, 1, 2}, averaged per fold at analysis from the stored per-seed units (§1.5). **Draw order (pre-deposit addendum, 2026-10-13):** a **fresh** `default_rng(seed)` per (dataset version, fraction token, seed), and for rebuilt versions per split file. It visits bags in ascending bag id over every bag of that version (or split file). For each bag with n_i instances it calls `rng.choice(n_i, size=m_i, replace=False)` with m_i = ⌈f · n_i⌉ (at least 1; m_i = 1 for the single-instance token), and the positions are sorted. Each bag therefore gets the same subset in every fold and in both the multiview and bag-mean arms. Fractions are drawn independently, not nested. The single-instance multiview row is itself a second width-matched control with degenerate columns (SD = 0, max = min = q25 = q75 = mean), and is reported as such.

**Families (both Holm α = 0.05):**
- **F-H4:** {bagmax, bagmean_card (10 rows), multiview} − bagmean, planned m = 16 + 10 + 16 = 42.
- **F-H4-padded:** multiview − padded, planned m = 16.

**Gate for every share and for Δ_inst (round 3 M3):** computed only where the 95 % CI of Δ(multiview − bagmean), corrected variance, lies **above 0**. Where it lies below 0, only the raw deltas are reported, with the sentence "multi-view did not improve on bag-mean here; no share is computed". Where it includes 0, nothing is computed. **Conditioning disclosed:** the gate selects rows using the same fold vector that forms the denominator of s and c and the g(1.0) term of Δ_inst. Gated rows therefore over-estimate the multiview gain, which biases s and c downward and Δ_inst away from zero. These statistics are descriptive, and the manuscript says so.

**Width share (pre-stated; F19).**
- s = Δ(padded − bagmean) / Δ(multiview − bagmean), from the fold means.
- **95 % CI of s, two forms, both reported:**
  - **Delta method:** with a_j = padded_j − bagmean_j and b_j = multiview_j − bagmean_j per fold, Var(ā), Var(b̄) and Cov(ā, b̄) are the sample (co)variances times (1/n + n₂/n₁). SE(s) = √(Var(ā) − 2s·Cov + s²·Var(b̄)) / |b̄|, and CI = s ± t_{0.975, n−1} · SE(s).
  - **Fieller:** the set of σ with (ā − σ b̄)² ≤ t²_{0.975, n−1} · (Var(ā) − 2σ·Cov + σ²·Var(b̄)), same inputs. If b̄² ≤ t²·Var(b̄), the Fieller set is unbounded and is reported as such.
  - Thresholds below use an interval's bounds only when **both** intervals satisfy them (an unbounded Fieller set satisfies no bound).
- **Outcomes, each reported where it holds (more than one can hold):**
  - (W1) upper CI bound of s < 0.5: "**width-insufficient**: at most a minor share of the gain is reproducible by feature width alone";
  - (W2) the CI of Δ(padded − bagmean) lies above 0: "width alone reproduces [s] of the gain";
  - (W3) the CI of Δ(padded − bagmean) lies below 0: "width hurts; the multi-view gain is obtained despite it";
  - (W0) none of W1–W3: "inconclusive about width".
- Never "width ruled out".

**Cardinality share, same construction and gate:** c = Δ(bagmean_card − bagmean) / Δ(multiview − bagmean), with both CIs as above; "largely cardinality" only if the lower bound of c is ≥ 0.5 under both intervals. On constant-size rows cardinality cannot contribute (stated a priori).

**Instance-subsampling rule (pre-stated).** Per fold, g(f) = AP(multiview_f) − AP(bagmean_f). Statistic: Δ_inst = g(1.0) − g(0.25), §1.6 test, on gated rows only. Subsampling is applied to test bags as well, so it changes the prediction task as well as the representation; the manuscript says so.
- CI of Δ_inst above 0: "the multi-view gain grows with the number of instances used per bag".
- CI below 0: "the multi-view gain shrinks as more instances are used".
- Otherwise: "no dependence on the number of instances detected".
- g(single instance) is reported beside it as the degenerate control. The full curve g(f) is plotted per dataset; only Δ_inst is tested (EXPLORATORY, outside both families).

**Language commitment:** the strongest permitted conclusion is "**higher-order bag statistics and/or cardinality, not width**", and only on rows where W1 holds. Never "multi-instance structure", never "and nothing else".

## H5: metric alignment

**Label:** EXPLORATORY. The dataset choice is partly **POST-HOC**: MSRC v2 and Letter Frost were added to the submitted conflict analysis after Scene had been run. Addresses R1-M06, R1-M08 (item 6), R2-06, R3-04, R4-02, R6-M04 (F20).

**Settings:**
- datasets and designs: Scene and Birds (MLSP 2013) on their canonical 10-fold splits; MSRC v2 and Letter Frost on the §1.2 5×5 design (M1);
- models: bag-mean MLP and ABMIL-multilabel;
- seeds {0, 1, 2}; CPU, float32, `torch.manual_seed(seed)`, `numpy.random.default_rng(seed)` for batch order.

**Surrogates** (as in `experiments/pareto_conflict/run_gradient_conflict.py`, plus Smooth-AP), each defined in the manuscript:
- Hamming → BCE-with-logits;
- ranking loss → pairwise softplus over (positive, negative) label pairs;
- one-error → softmax cross-entropy over the positive set;
- coverage → log-sum-exp of the soft count of negatives ranked above each positive;
- **AP → Smooth-AP** (Andrew Brown, Weidi Xie, Vicky Kalogeiton, Andrew Zisserman, ECCV 2020), computed per bag over labels, sigmoid temperature 0.01.

**Training recipe, identical for both models and all five surrogates (M1):**
- **Bag-mean MLP** (as submitted): Linear(d, 64) → ReLU → Linear(64, L), on bag-mean features.
- **ABMIL-multilabel:** instance encoder Linear(d, 64) → ReLU; one gated-attention pooling branch (Maximilian Ilse, Jakub M. Tomczak, Max Welling, ICML 2018) with attention dimension 32, a_i ∝ exp(wᵀ(tanh(V h_i) ⊙ sigmoid(U h_i))); bag embedding Σ a_i h_i (64-d) → Linear(64, L).
- Inputs z-scored with mean and SD of `fit_i` only (instance level for ABMIL, bag-mean level for the MLP).
- Optimiser Adam, learning rate 1e-3, no weight decay, default betas; mini-batches of 16 bags, reshuffled each epoch; maximum 200 epochs.
- Split: `val_i = tr[:v]`, `fit_i = tr[v:]` as in §1.3.
- **Early stopping** on the training surrogate's own value on `val_i`, patience 20 epochs; the checkpoint with the lowest validation surrogate is the model.
- Hamming loss for every H5 model uses per-label thresholds tuned on `val_i` with the same `optimize_thresholds` as MIML-PFN; the four ranking metrics use raw scores.
- No per-surrogate or per-dataset tuning of any of the above.

**Measurements:**
- (a) Full-batch, mini-batch (16 bags) and per-label gradient cosines along the BCE training trajectory, on `fit_i`.
- (b) **Cross-evaluation:** train separately on each of the 5 surrogates, evaluate all 5 metrics on the outer test folds.
- (c) **Surrogate faithfulness (B.5, R2-06 flag a):** for each (dataset, model, seed, outer fold, surrogate), at every epoch checkpoint up to the last epoch trained, the surrogate value and its paired exact metric on the **outer test fold** (held out from training and from early stopping), both oriented lower-is-better (AP → 1 − AP; Hamming at a fixed 0.5 threshold on sigmoid outputs for this measurement only). Faithfulness = Spearman correlation across checkpoints. Reported per (dataset, model, surrogate) as the median and range over seeds × folds, in the surrogate-definition table. Descriptive; no test.

**Cross-evaluation family.** Per (dataset, model), the 20 off-diagonal comparisons "trained on A's surrogate vs trained on B's own surrogate, scored on metric B". **Pairing unit = outer fold** (repeat × fold for the 5×5 designs); the fold value is the mean over the 3 seeds; n = r·k, df = n − 1; never (seed × fold). §1.6 test with n₁ = 0.8 × outer training. Holm within each (dataset, model), m = 20.

**Reporting:**
- "Conflict observed for (A, B) on [setting]" for each significant degradation.
- "No conflict observed in these settings" only if none are significant.
- The title and abstract do not state metric alignment as a property of the suite, and the title phrase "Non-Conflicting Metrics" is removed regardless of outcome.
- **Theory cited (B.11), checked against the paper:** Krzysztof Dembczyński, Willem Waegeman, Weiwei Cheng, Eyke Hüllermeier, "On label dependence and loss minimization in multi-label classification", *Machine Learning* 88:5–45, 2012, doi:10.1007/s10994-012-5285-8 (open access), §4.1 eq. (13), §4.2 Theorem 1 and eqs. (18), (20), §5 Proposition 2. **What it shows:** the Hamming-loss risk minimiser is the vector of marginal modes (eq. 13); the risk minimiser of the (unnormalised) rank loss sorts labels by their marginal probabilities P(Y_i = 1 | x) (Theorem 1, eq. 18); the subset 0/1 loss is minimised by the joint mode (eq. 20), which coincides with the marginal modes only under conditions such as conditional independence (§5, Proposition 2). So Hamming and the unnormalised rank loss can both be minimised from the marginals alone; the paper does **not** say that Hamming and rank losses have different minimisers in general. The authors add that this result "cannot be extended to the normalized version of the rank loss", for which the marginals are not enough. **Consequence for us:** our ranking-loss metric (`sklearn.metrics.label_ranking_loss`) and our pairwise-softplus surrogate (a mean over the bag's positive–negative pairs) are both normalised, so the theorem does not predict alignment for them. The v2 paraphrase ("Hamming and rank losses have different risk minimisers") was wrong and is withdrawn. The manuscript states the result as above and reports whether our measurements are consistent with it.

## 5. One-fit TabPFN

**Label:** verification, not a hypothesis.

- **(pre-deposit addendum, 2026-10-13)** "One fit" means one `.fit` per label followed by two separate `predict_proba` calls, on `val_i` and on the test fold, never concatenated into one call.
- Replace the two fits (validation pass, test pass) with one fit that predicts both, **only if** it reproduces all five metrics on every fold of Letter Frost (the submitted seed-42 5-fold split, `submitted5`) and Scene (canonical split) `tabpfn_bagmean` to |Δ| ≤ 1e-9, on the TabPFN device of §6.1.
- If it fails, keep two fits and report the cost as measured.
- This is a **fixed-cost pre-projection item** (§6.0, G-queue step 2). It runs before the G timing pilots, because it sets the production fit count every pilot uses. It is outside the budgets and the execution order, and its hours are logged.

## 6. Compute protocol, budget and "did not complete"

Addresses F10, F11, F16, F17, F23, F25, B2, B3, B.4, M7, m8, m9, m11; round 3 M1, M2, m4, m5, m8; user decision 2026-10-12 ("nothing descoped").

### 6.0 Order of execution: two device queues (round 3 M1, round 4 M1)
Work runs in **two independent queues, one per device**, so C work starts before the GPU credits arrive (DECISIONS.md 2026-10-12: "GPU arms wait for NVIDIA Inception credits; all local work first"). Each queue writes its own section of `experiments/revision_r1/PROJECTIONS.md` (to be created), and that section is committed before the queue's first non-pilot run. **Step 0 of both queues is the deposit of §1.8**; nothing in either queue runs before it.

**C queue** (Apple M4 Pro CPU, plus its MPS backend for the items marked):
1. T03 checks a–f (§6.8), and T03-g's logreg part. Fixed cost, outside the budgets; hours logged.
2. H2-A construction (all four sets, all 10 splits) and the H2-B leak and control masks (all four sets, all folds, seeds {0, 1, 2}), each with its overlap check (§H2). A non-zero overlap stops the queue. **(pre-deposit addendum, 2026-10-13)** The H2-A and H2-B acceptance checks then run as `experiments/revision_r1/h2_acceptance.py` (committed; called by both construction builders). It holds the expected constants listed in this plan: the 13 dropped rows and the Medical and Corel5K pool sizes (H2-A step 4), and the H2-B table at its printed precision. It runs before anything reads the constructions, and any mismatch stops the queue.
3. C timing pilots (§6.3): library, logreg, H5.
4. Library caps (§6.5).
5. C caps and C budgets (§6.7), stop rule included.
6. C section of `PROJECTIONS.md` committed.
7. C runs, in the §6.7 execution order restricted to C units.
8. Tail, on MPS, only while no timed C batch is running (§6.1): T03-g's TabPFN part, then the §1.9 TabPFN arms. Their PCA decision comes from the G queue (dependency 3 below). Under the global MPS fallback (§6.1), these items move to the G queue, which then runs on MPS.

**G queue** (the NVIDIA GPU; under the fallback, the MPS backend):
1. `DEVICE_LOG.md` written.
2. §5 one-fit check. Fixed cost, outside the budgets; hours logged.
3. G timing pilots (§6.3), using the production fit count fixed by step 2.
4. PCA trigger (§6.4), from the H1 arms only.
5. G caps and G budgets (§6.7), stop rule included.
6. G section of `PROJECTIONS.md` committed.
7. G runs, in the §6.7 execution order restricted to G units.
8. Cross-device check (§6.9), after T03-g has passed or been reported.

**Cross-queue dependencies, named:**
1. G pilots and runs on the H2-A rebuilt rows (H1, H4) and on the H2-B rows wait for C-queue step 2 (rebuilt files and masks).
2. §6.9 waits for both parts of T03-g.
3. The §1.9 TabPFN multiview arm on MPS uses the §6.4 PCA decision for its dataset, so it waits for G-queue step 4.
4. The H1, H2 and H3 comparisons are analyses of stored predictions from both queues. They are computed only when both sides of a comparison exist.

Within each queue the §6.7 execution order applies. Pilot hours are logged but not counted against the totals of §6.7.

### 6.1 Devices and concurrency, fixed per arm now (B3a, round 3 M2)
| arm | device |
|---|---|
| every TabPFN fit in this revision (all datasets, versions and arms; H3; H4; cross-device check; §5), except §1.9 and T03-g | **G** = one NVIDIA GPU, a single card with ≥ 24 GB memory, obtained under the NVIDIA Inception credits (DECISIONS.md: GPU arms wait for them). Its exact model, memory, driver, CUDA and torch versions are written to `experiments/revision_r1/DEVICE_LOG.md` (to be created) **before the first GPU fit**. |
| KDIS (Java), MIMLNN (Octave), logreg, H2 constructions, H5 neural models | **C** = the Apple M4 Pro (14 cores), CPU |
| §1.9 TabPFN arms, T03-g TabPFN part | the M4 Pro MPS backend (one of the two MPS exceptions, with T03-g; those results are compared only with MPS results) |

- **Concurrency and memory, fixed per dataset version, identical in pilot and run (round 4 m3, m4):**
  - On G and on MPS: **one TabPFN process per device at a time**.
  - On C: JVM heap `-Xmx2g` by default, and `-Xmx8g` for VOC2012 and every Corel5K version. Concurrency N = min(8, ⌊16 GiB / Xmx⌋), i.e. N = 8 at 2g and N = 2 at 8g, so N × Xmx ≤ 16 GiB on this 24 GiB machine. N = 8 is at most the 10 performance cores. Octave and Python runs use N = 8. The N used is recorded per dataset version in `PROJECTIONS.md` and the cost table.
  - An `OutOfMemoryError` is a crash (§6.6). The retry uses doubled Xmx and halved N, recorded; this is not a descoping.
  - Thread pools are pinned in every process: `OMP_NUM_THREADS=1` and `OPENBLAS_NUM_THREADS=1` in the environment of every Python, Java and Octave process (Octave included), `torch.set_num_threads(1)`, and JVM `-XX:+UseSerialGC`.
  - During any timed pilot or run on C, no other CPU-bound process runs on the machine. This includes the §5, §6.9 and §1.9 drivers and any MPS TabPFN process, which draw from the same 24 GiB of unified memory. A timed run whose 1-minute load average exceeded 10 is re-timed.
- **Device-hour (G, MPS):** one hour of wall clock with the device used by that one process.
- **Process-hour (C):** one hour of **CPU time** (user + sys, from `getrusage(RUSAGE_CHILDREN)` of the child process for Java and Octave, `RUSAGE_SELF` for Python). CPU time is far less sensitive to machine load than wall clock, but not insensitive: a process scheduled on an efficiency core accrues CPU seconds more slowly per unit of work. Hence the conditions above, and the 3× margin of §6.6.
- Every timing record (pilots, runs, cost table) also logs the 1-minute load average and the number of concurrent runs.
- **Fallback, one global switch:** if the user records in `DEVICE_LOG.md`, before the first G-queue fit, that G will not be available, then **every** G arm runs on the M4 Pro MPS backend, under the same hour caps measured in MPS device-hours. G and MPS are never mixed within a comparison; the stored submission results are labelled. Under the fallback the two queues share one machine, so they **serialise, C queue first**: G-queue items run on MPS only after the C queue's runs are complete, which also keeps MPS work out of timed C batches.

### 6.2 Cost measurement and table (R2-05, F23, B.4)
For every method × dataset version × outer fold, stored in the results JSON:
- **fit time and predict time, separately:**
  - TabPFN and logreg: `.fit` and `.predict_proba` per label, summed, plus feature construction and standardisation as a third "preprocessing" time;
  - KDIS: `build` and the `makePrediction` loop, timed separately inside `PredictDump.java` (`System.nanoTime`, plus thread CPU time);
  - MIMLNN: training and testing phases separately if the released function's structure allows a split in our driver, otherwise their sum, labelled "fit + predict, not separable";
  - H5: training and inference.
- **memory:** peak process RSS for every method as the common measure (`resource.getrusage`, `RUSAGE_SELF` for Python, `RUSAGE_CHILDREN` of a fresh child per Java/Octave run), plus device peak where applicable (`torch.cuda.max_memory_allocated` on G; `torch.mps.driver_allocated_memory` sampled on MPS), labelled as different quantities. **Definitions (pre-deposit addendum, 2026-10-13):** `ru_maxrss` is a process-lifetime peak and is reported as such; the device peak is per outer fold (CUDA counter reset with `torch.cuda.reset_peak_memory_stats()` at the start of each fold; MPS driver memory sampled during the fold, maximum taken).
- **energy:**
  - on G, the NVML total-energy counter (`nvmlDeviceGetTotalEnergyConsumption`) differenced **per outer fold** (pre-deposit addendum, 2026-10-13);
  - on macOS, `powermetrics --samplers cpu_power,gpu_power -i 1000`, integrated over the run. **`powermetrics` needs sudo: user action.**
  - With N = 8 concurrent runs on C, CPU energy is attributed to the batch and divided by CPU time; it is labelled "shared-machine estimate". Wherever a counter is unavailable, the table says "**not measured**".
- device string, load average, concurrency, library versions, full constructor arguments, per-fit times.
- `n_estimators` stays at TabPFN's default of 8 (comparability with the submission); the manuscript states that this is an internal 8-member ensemble.

### 6.3 Timing pilots (B2i, B3d, m8, round 3 m4, m5)
Within each queue of §6.0, before any of that queue's units runs beyond its pilot, on **every** dataset version and arm of that queue:
- **TabPFN arms:** time the first 3 labels of outer fold 0 (repeat 0) on the assigned device at native width, with the **production fit count** fixed by §5 (one fit predicting validation and test if §5 passed, two fits otherwise). ~~Projected device-hours = mean per-label time × labels × outer folds × repeats × conditions.~~ **(pre-deposit addendum, 2026-10-13)** Labels that are constant in `fit_i` are not fitted. The pilot mean is taken over the fitted labels among the first 3; if any of the first 3 are constant, the pilot extends to the first 3 non-constant labels. Projected hours = mean per-fit time × the number of non-constant labels (× folds × repeats × conditions as above). The number of non-constant labels is measured on outer fold 0's `fit_i` and applied to every fold. This approximation is used for projections only; actual runs fit every label that is non-constant in that fold's `fit_i`. Conditions: H2-B 1 leak + 3 control seeds; H4 padded 3 permutation seeds; H4 subsampling 4 subset sizes × 3 seeds, for multiview and bag-mean each.
- **Library arms:** for every (method, distance, k) and every MIMLNN (ratio, λ, seed), time inner fold 0 of outer fold 0 **and the refit on the full outer training fold 0**, in process-hours. Projected process-hours = Σ over candidates of inner time × (inner folds × outer folds × repeats) + refit time × outer folds × repeats. **(pre-deposit addendum, 2026-10-13)** Only selected candidates are refit (§1.3). Refits occur for the library procedure **and** for each of the 8 per-method nested selections, per metric (5 metrics); the library's selections are a subset of the per-method ones. The refit term per outer fold is therefore bounded by Σ over the 8 methods of the sum of that method's **5 largest measured candidate refit times** (a MIMLNN candidate's refit time covers all its Octave seeds). Projected refit hours = that bound × outer folds × repeats. It is an upper bound, since several metrics may select the same candidate and one refit then serves them all. The refit time is measured, not modelled; Hausdorff distance matrices scale as n², so the refit costs about (5/4)² ≈ 1.56 × an inner 5-fold run, and (3/2)² = 2.25 × an inner 3-fold run.
- **H5:** time epoch 1 of seed 0, outer fold 0, per (dataset, model, surrogate); projected = time × 200 epochs × seeds × folds.
- Timing pilots write times only; their predictions are discarded unscored.
- All projections of a queue, and every decision of §6.4–§6.7 they imply, are written to that queue's section of `PROJECTIONS.md` **before** any non-pilot run of the queue starts, and before any R2 (AMENDMENT.md) multiview result exists.

### 6.4 PCA rule for TabPFN arms (F17, B3c–d, round 3 M1)
- **Trigger, computed from H1 arms only:** if the native-width projection of `tabpfn_multiview` or `tabpfn_bagmean` on any H1 version of a dataset exceeds **72 device-hours**, all TabPFN arms on all versions of that dataset use PCA on the bag-level feature matrix to **d′ = 500** (TabPFN v2's pre-training feature limit), fit on `fit_i` rows only. **(pre-deposit addendum, 2026-10-13)** Exactly: **the d′ rule applies only to arms with bag-level width d > 500; an arm with d ≤ 500 stays `native` whatever its fold sizes (the switch is a no-op, as below).** For d > 500, d′ is fixed **per dataset** (and per arm width d), **d′ = min(500, d, min over the folds of the dataset's H1 version and of its §1.9 `rcv10` version, including the canonical sixth MPS run, of n_rows(`fit_i`) − 1)**. It is computed from fold sizes only, before any fit. The same d′ is used on every version of the dataset: H1, leaky original, rebuilt, purged, `rcv10`, `submitted5`. Every fold asserts n_rows(`fit_i`) − 1 ≥ d′ (on rebuilt and purged versions too) and stops if it is violated. Since PCA needs n_components ≤ n_samples − 1 after centring, this keeps every fit full-rank. Worked values for the multiview width, where the rows bind (H1 `fit_i` / smallest `rcv10` `fit_i` → d′):

  | dataset | H1 `fit_i` | smallest `rcv10` `fit_i` | d′ (multiview) |
  |---|---|---|---|
  | Protein Haloarcula | 220 | 219 | **218** |
  | Protein Pyrococcus | 307 | 306 | 305 |
  | Protein Geobacter | 274 | 273 | 272 |
  | Protein Azotobacter | 294 | 293 | 292 |
  | Birds (MLSP 2013) | 186 | 185 | — (multiview width 229 ≤ 500: `native` regardless) |
  | Reuters, VOC2012 | ≥ 1440 | ≥ 1440 | 500 |

  Protein bag-mean (d = 216 ≤ 500) stays `native`, as do every §1.2 set's arms (MSRC v2 multiview 289, Letter sets 97). The `rcv10` test blocks are `np.array_split` blocks (larger first), so the smallest `rcv10` `fit_i` comes from the largest test block, ⌈n/10⌉. This makes the rule feasible on the protein sets, whose `fit_i` has 220–307 rows. Pipeline: z-score with `fit_i` statistics, then `PCA(n_components=d′, svd_solver="full", random_state=0)` fitted on `fit_i` (the full solver is deterministic), with no re-scaling afterwards. The width token is `pca<d′>` (e.g. `pca500`, `pca218`); where d ≤ 500, or d′ = d, the switch is a no-op and the token is `native`. **TabPFN version guard {T}:** every TabPFN path requires `tabpfn==2.2.1` in the separate TabPFN environment and refuses to run otherwise (the main `.venv` holds a licence-gated tabpfn 8.2.0). "H1 versions" are the 16 primary rows: the rebuilt versions for the constructed four. The leaky originals inherit the decision; H3's Yeast pair stays native. POST-HOC and other non-H1 arms (H2-B, H4, §1.9) can never trigger PCA. They inherit the decision.
- Arms with d ≤ 500 are unchanged (no-op), and this is reported.
- **Exception:** H3's registered Yeast pair on the leaky file stays at native width.
- After a switch, all affected arms are re-projected (pilot rerun at the dataset's d′, §6.4 (pre-deposit addendum, 2026-10-13)), and the post-PCA projection replaces the native one.
- Decided from projections only, before any result on that dataset exists.

### 6.5 Library caps and the VOC2012 grid (B2)
- **VOC2012 reduced grid, fixed now (B2ii):** inner **3-fold**; distance ∈ {AveH, MaxH}; k ∈ {10, 20}; MIMLNN ratio ∈ {0.2, 0.4}, λ = 1, Octave seeds {0, 1}. All 7 KDIS methods are kept. This is VOC2012's configuration, not a fallback.
- **Per-(dataset version, library arm) cap: 300 process-hours.** If a projection exceeds it, the unit is **held** under §6.7's stop rule. The user may approve the extra hours or the VOC2012 reduced grid for that dataset version, by a dated AMENDMENT. Without that decision the unit does not run, and it is reported as "library not run: projection [h] above the pre-registered cap; extension not approved".
- **Distance caching (B2iii).** KDIS has no distance cache: Hausdorff distances are recomputed inside every run (`MIMLkNN.calculateDatasetDistances` builds the full matrix during `buildInternal`).
  - Caching is allowed only as an implementation of identical arithmetic: one precomputed bag-distance matrix per (dataset version, distance, outer fold), exposed to the unmodified library through a custom `IDistance` class on the classpath that looks bags up by their id attribute.
  - It may be used only if T03-d (§6.8) shows byte-identical predictions with and without it on every Letter Frost candidate in outer fold 0.
  - Projections are measured with the implementation that will actually be used.
  - Caching is not retuning: grids, folds and configurations are unchanged.

### 6.6 "Did not complete" (F10, B2iv, round 3 M2)
- **TabPFN unit:** a crash after 2 retries, or device-hours above **min(3 × post-PCA projection, 180)**.
- **Single library run:** a Java or Octave run that exceeds **max(7 200 s, 3 × its pilot) of CPU time** (process-hours, §6.1, not wall clock), or crashes twice, is a failed candidate for that fold (§1.3). **Wall guard (pre-deposit addendum, 2026-10-13):** a run is also killed, and counted as a failed candidate, if its wall clock exceeds 4 × that CPU-time limit (this catches a hung, CPU-idle child).
- **Library unit:** total process-hours above **min(3 × projection, 450)**.
- On reaching a limit, the unit **pauses** and an extension is requested under §6.7's stop rule. If the user declines, the unit "did not complete" and is reported with hours spent. A dataset whose MIML-PFN or library arm did not complete leaves the families that need it.

### 6.7 Budgets, stop rule and execution order (B3b; user decision 2026-10-12, "nothing descoped")
- **Per-unit cap (TabPFN, dataset version × arm × condition):** post-PCA projection ≤ **120 device-hours**.
- **Total budgets for the revision:** TabPFN **1 500 device-hours** on G (the same number in MPS device-hours under the fallback); library **3 000 process-hours** on C; H5 **100 process-hours** on C.
- **Stop rule, replacing any drop rule.** No unit is descoped by this document. When a unit's projection exceeds its cap, or when adding a unit would exceed a total budget:
  1. execution **stops before that unit**;
  2. all projections are recorded in `PROJECTIONS.md`;
  3. a budget extension is requested from the user through a dated `AMENDMENT.md` in `experiments/revision_r1/`, stating the unit, its projection and the hours already used.

  A unit is dropped or reduced only by a user decision recorded in `../../revision_access_44676/DECISIONS.md`. It is then reported as "not run, by user decision [date], projection [h]". The units still within budget continue meanwhile, in the order below. **Continuation rule (pre-deposit addendum, 2026-10-13):** after a budget hold, later units that are independent of the held unit and fit within the remaining budget continue to run; only units that depend on the held unit wait.
- **Execution order** (an order of running, not of dropping):
  1. F-H1 new-data rows: multiview, bag-mean and library;
  2. H3: Yeast multiview and bag-mean on G;
  3. F-H1 "direction previously observed" native rows: multiview, bag-mean and library;
  4. H2-B: library, MIMLkNN, MIMLNN and logreg arms;
  5. H2-B: TabPFN bag-mean, then TabPFN multiview;
  6. H4: padded, bagmax, bagmean_card, then the instance-subsampling curve;
  7. leaky-original rows of the constructed sets (H1 "leaky" column);
  8. §1.9 repeated-10-fold sensitivity;
  9. cross-device check (§6.9).
- R2 (AMENDMENT.md) uses the Reuters and protein multiview runs of positions 1 and 3; it adds no units.

### 6.8 T03 checks, listed here (m9)
Run as C-queue step 1 of §6.0 (T03-g's TabPFN part at the C-queue tail, on MPS, run by task T04).
- **Splits for these checks (pre-deposit addendum, 2026-10-13):** a check that compares with a stored submitted number runs on `submitted5` (the submitted seed-42 5-fold split) for Letter Frost, or on the canonical split for Scene. Every other check ("Letter Frost outer fold 0" below) runs on the §1.2 5×5 design, repeat 0, fold 0, version `original`. Results are recorded in `../../revision_access_44676/tasks/T03-baseline-harness-checks.md` (to be created; the checks and tolerances are fixed here, not there) and summarised in the manuscript.
- **T03-a KDIS determinism:** each of the 7 methods at AveH, k = 10, run twice on Letter Frost outer fold 0: predictions must be byte-identical. ~~If not, KDIS uses the 5-seed rule of §1.3.~~ If not, the KDIS non-determinism fallback of §1.3 applies to that method (pre-deposit addendum, 2026-10-13).
- **T03-b KDIS dump fidelity:** for the same runs, `miml_metrics.py` on the **raw** `PredictDump` output (before the F4 overwrite of §1.3) (pre-deposit addendum, 2026-10-13) vs the library's own report, all 5 metrics; every difference above 1e-3 is reported with its cause (convention differences, e.g. ties, are expected). Primary scoring stays `miml_metrics.py` on the dumped predictions; this check documents, it does not select.
- **T03-c MIMLNN scoring agreement:** the same comparison for MIMLNN (ratio 0.4, λ = 1, seed 0) on Letter Frost, all 5 folds, with the same reporting rule.
- **T03-d distance cache:** only if caching is to be used; byte-identical predictions on every Letter Frost candidate, outer fold 0.
- **T03-e Octave seed control:** the same seed twice gives identical outputs.
- **T03-f scorer agreement without a harness run** (only needed for §1.5's fallback): 1 000 random score matrices (`default_rng(3)`, uniform) paired with Letter Frost's label matrix are scored by `miml_metrics.py` and by the harness's own scoring code called directly (Mulan's measures for KDIS; the LAMDA `.m` scoring functions for MIMLNN); tolerance 1e-3 AP on every matrix.

- **T03-g same-device reproduction with pinned settings (round 4 m6), run before §6.9:**
  - `logreg_bagmean` on Scene in `.venv` on C, with the §6.1 thread pinning, must reproduce the stored result to ≤ 1e-9 on all five metrics on every fold.
  - `tabpfn_bagmean` on Letter Frost on MPS, in the recreated `tabpfn_env`, with the pinned settings, must reproduce the stored result to ≤ 1e-3 AP on every fold.
  - A pass makes §6.9 attributable to the device. A fail is reported, and stored rows are then labelled by environment (August venv vs recreated venv) as well as by device.

### 6.9 Cross-device check (F25, m11)
After T03-g, on G: `tabpfn_bagmean` on Letter Frost and Scene, and `tabpfn_multiview` on Letter Frost, against the stored MPS results. Report the maximum per-fold |ΔAP|. If it exceeds 1e-3, the manuscript reports the device of every row and no test compares arms across devices (H3 and H4 already use one device per comparison).

### 6.10 Rebuilt and purged sets (F11)
Every H1 arm, including multiview, runs on the H2-A rebuilt versions of Emotions, Yeast, Medical and Corel5K; H2-B arms run on the purged originals. Both are units in §6.7 like any other; there is no separate budget.

---

## 7. Power table (recomputed 2026-10-12 for the v3 families)

Generated by `experiments/revision_r1/power_table.py` (one command; the only randomness, Part D, uses `default_rng(20261012)`; full output in `../../revision_access_44676/evidence/T05__power_table.txt`). Test and ratio exactly as §1.6, α = 0.05, two-sided. v3 fixes the H1 families by the user decision of 2026-10-13 (primary F-H1 over all rows, planned m = 16; new-data sensitivity F-H1-newdata, m = 10), so Parts A and B were recomputed; Parts C (other families, m6) and D (global test, M2) are new. Part D's draws are seeded, so its numbers reproduce exactly.

**Planned family sizes.** Primary F-H1: all 16 rows (Scene, Reuters, Birds (MLSP 2013), VOC2012, Protein ×4 and the four rebuilt sets on single 10-fold; MSRC v2 and the Letters on 5×5; HJA Birdsong on 5×10) = 16. Sensitivity F-H1-newdata: HJA Birdsong, VOC2012, Protein ×4, rebuilt Emotions, Yeast, Medical, Corel5K = 10. m = 12 and 14 are margins for exclusions under §6. The single 5-fold row is the *submitted* design, for reference only.

**Power approximation.** T ~ noncentral t, df = n − 1, ncp = d_z / √(1/n + n₂/n₁), i.e. assuming the corrected variance is the true variance of d̄, which is the assumption the test makes. d_z is the population standardised mean of the per-fold differences; under repeated CV s_d also absorbs between-repeat variation, so a d_z observed on a single k-fold run need not carry over. A 40 000-draw Monte Carlo in PREREG__review_2 found the single 10-fold test slightly liberal (Type-I 0.067) and power at d_z = 1 of 0.52 against the table's 0.447: the table is a fair approximation.

### A. Design-level power, H1 families (corrected test of §1.6, alpha = 0.05; MIML-PFN vs library, n1 = 0.8 x outer training)

rho = n2/n1 = (1/k)/((1-1/k)*0.8); n = r*k; df = n-1. d_z,min = t_crit * sqrt(1/n + rho). Planned: primary F-H1 m = 16; sensitivity F-H1-newdata m = 10.

| design | n | df | rho | factor sqrt(1/n+rho) | applies to |
|---|---|---|---|---|---|
| single 10-fold (r=1,k=10) | 10 | 9 | 0.1389 | 0.4888 | Scene, Reuters, Birds (MLSP 2013), VOC2012, Protein x4, Emotions-R, Yeast-R, Medical-R, Corel5K-R |
| repeated 5x5 (r=5,k=5) | 25 | 24 | 0.3125 | 0.5937 | MSRC v2, Letter Frost, Letter Carroll |
| repeated 5x10 (r=5,k=10) | 50 | 49 | 0.1389 | 0.3986 | HJA Birdsong |
| single 5-fold (r=1,k=5) | 5 | 4 | 0.3125 | 0.7159 | REFERENCE ONLY: submitted design for MSRC v2 / Letters |

#### A1. Critical |t| and minimum d_z

| design | m | t_crit first step (alpha/m) | d_z,min first step | t_crit last step (alpha) | d_z,min last step |
|---|---|---|---|---|---|
| single 10-fold (r=1,k=10) | 10 (new-data sensitivity) | 3.690 | 1.803 | 2.262 | 1.106 |
| single 10-fold (r=1,k=10) | 12 | 3.808 | 1.861 | 2.262 | 1.106 |
| single 10-fold (r=1,k=10) | 14 | 3.909 | 1.910 | 2.262 | 1.106 |
| single 10-fold (r=1,k=10) | 16 (primary, planned) | 3.997 | 1.954 | 2.262 | 1.106 |
| repeated 5x5 (r=5,k=5) | 10 (new-data sensitivity) | 3.091 | 1.835 | 2.064 | 1.225 |
| repeated 5x5 (r=5,k=5) | 12 | 3.166 | 1.880 | 2.064 | 1.225 |
| repeated 5x5 (r=5,k=5) | 14 | 3.230 | 1.918 | 2.064 | 1.225 |
| repeated 5x5 (r=5,k=5) | 16 (primary, planned) | 3.285 | 1.950 | 2.064 | 1.225 |
| repeated 5x10 (r=5,k=10) | 10 (new-data sensitivity) | 2.940 | 1.172 | 2.010 | 0.801 |
| repeated 5x10 (r=5,k=10) | 12 | 3.006 | 1.198 | 2.010 | 0.801 |
| repeated 5x10 (r=5,k=10) | 14 | 3.061 | 1.220 | 2.010 | 0.801 |
| repeated 5x10 (r=5,k=10) | 16 (primary, planned) | 3.109 | 1.239 | 2.010 | 0.801 |
| single 5-fold (r=1,k=5) | 10 (new-data sensitivity) | 5.598 | 4.007 | 2.776 | 1.988 |
| single 5-fold (r=1,k=5) | 12 | 5.885 | 4.213 | 2.776 | 1.988 |
| single 5-fold (r=1,k=5) | 14 | 6.138 | 4.394 | 2.776 | 1.988 |
| single 5-fold (r=1,k=5) | 16 (primary, planned) | 6.364 | 4.556 | 2.776 | 1.988 |

#### A2. Approximate power at the first Holm step (alpha/m) and the last (alpha)

Noncentral t, df = n-1, ncp = d_z/sqrt(1/n+rho).

| design | step | d_z=0.5 | d_z=1 | d_z=2 | d_z=3 |
|---|---|---|---|---|---|
| single 10-fold (r=1,k=10) | first, m=10 | 0.024 | 0.120 | 0.652 | 0.972 |
| single 10-fold (r=1,k=10) | first, m=12 | 0.020 | 0.106 | 0.619 | 0.964 |
| single 10-fold (r=1,k=10) | first, m=14 | 0.018 | 0.095 | 0.590 | 0.956 |
| single 10-fold (r=1,k=10) | first, m=16 | 0.016 | 0.087 | 0.565 | 0.948 |
| single 10-fold (r=1,k=10) | last (alpha) | 0.151 | 0.447 | 0.952 | 1.000 |
| repeated 5x5 (r=5,k=5) | first, m=10 | 0.021 | 0.104 | 0.612 | 0.966 |
| repeated 5x5 (r=5,k=5) | first, m=12 | 0.018 | 0.093 | 0.585 | 0.959 |
| repeated 5x5 (r=5,k=5) | first, m=14 | 0.016 | 0.085 | 0.563 | 0.954 |
| repeated 5x5 (r=5,k=5) | first, m=16 | 0.015 | 0.078 | 0.543 | 0.948 |
| repeated 5x5 (r=5,k=5) | last (alpha) | 0.128 | 0.366 | 0.898 | 0.998 |
| repeated 5x10 (r=5,k=10) | first, m=10 | 0.055 | 0.345 | 0.978 | 1.000 |
| repeated 5x10 (r=5,k=10) | first, m=12 | 0.048 | 0.322 | 0.974 | 1.000 |
| repeated 5x10 (r=5,k=10) | first, m=14 | 0.043 | 0.304 | 0.970 | 1.000 |
| repeated 5x10 (r=5,k=10) | first, m=16 | 0.040 | 0.289 | 0.967 | 1.000 |
| repeated 5x10 (r=5,k=10) | last (alpha) | 0.233 | 0.691 | 0.998 | 1.000 |
| single 5-fold (r=1,k=5) | first, m=10 | 0.010 | 0.026 | 0.123 | 0.325 |
| single 5-fold (r=1,k=5) | first, m=12 | 0.008 | 0.022 | 0.106 | 0.288 |
| single 5-fold (r=1,k=5) | first, m=14 | 0.007 | 0.019 | 0.093 | 0.259 |
| single 5-fold (r=1,k=5) | first, m=16 | 0.006 | 0.017 | 0.084 | 0.236 |
| single 5-fold (r=1,k=5) | last (alpha) | 0.085 | 0.192 | 0.562 | 0.873 |

### C. Other families: first Holm step (alpha/m), each with its own n1

f = n1 / outer training size; rho = (1/k)/((1-1/k)*f). H2 uses e = 0.136 (largest mean fraction of training bags emptied by the instance purge, Medical).

| family | m | design | f | rho | d_z,min first step | power d_z=1 | power d_z=2 | power d_z=3 | note |
|---|---|---|---|---|---|---|---|---|---|
| H2 (7 methods x 4 sets), library arms | 28 | r=1,k=10 | 0.864 | 0.1286 | 2.091 | 0.062 | 0.486 | 0.920 | n1 = post-purge training bags |
| H2 (7 methods x 4 sets), TabPFN/logreg arms | 28 | r=1,k=10 | 0.691 | 0.1608 | 2.234 | 0.051 | 0.412 | 0.871 | n1 = 0.8 x post-purge training bags |
| H4 (bagmax 16 + card 10 + multiview 16) | 42 | r=1,k=10 | 0.800 | 0.1389 | 2.276 | 0.043 | 0.389 | 0.862 |  |
| H4 (same), 5x5 rows | 42 | r=5,k=5 | 0.800 | 0.3125 | 2.182 | 0.042 | 0.407 | 0.894 |  |
| H4-padded (multiview vs width-matched padded, 16) | 16 | r=1,k=10 | 0.800 | 0.1389 | 1.954 | 0.087 | 0.565 | 0.948 |  |
| H4-padded (same), 5x5 rows | 16 | r=5,k=5 | 0.800 | 0.3125 | 1.950 | 0.078 | 0.543 | 0.948 |  |
| H5 per (dataset, model), 20 off-diagonal | 20 | r=1,k=10 | 0.800 | 0.1389 | 2.026 | 0.074 | 0.523 | 0.933 | Scene, Birds |
| H5 per (dataset, model), 20 off-diagonal | 20 | r=5,k=5 | 0.800 | 0.3125 | 2.004 | 0.068 | 0.511 | 0.938 | MSRC v2, Letter Frost |

### B. Observed effects (descriptive, submitted protocol; not a result of this pre-registration)

Ours = make_tables.ours() arm (multiview where it completed, else bag-mean); published = make_tables.best(PUB, ds, AP), selected on test. d = ours - published per fold. d_z = mean(d)/sd(d, ddof=1), uncorrected. t_corr/p_corr = §1.6 test with r=1, k = folds actually used, rho = (1/k)/((1-1/k)*0.8). p_naive = ttest_rel (as in the submitted paper). Holm at m=8 (the 8 tests together) and at m=16 (planned primary size). The m=16 column is a scenario: the 8 untested rows are placed after every observed row, which gives the observed rows the strictest thresholds that do not depend on the untested rows; it is not a bound in either direction. Yeast and Emotions here are the leaky originals; their primary rows in v3 are the rebuilt versions.

| dataset | ours | best published | k | mean dAP | d_z | t_corr | p_corr | p_naive | Holm m=8 | Holm m=16 (scenario) | d_z,min first step m=16, this k |
|---|---|---|---|---|---|---|---|---|---|---|---|
| MSRC v2 | multi-view | MIMLIBLR_AveH(10) | 5 | +0.1265 | +5.38 | +7.52 | 0.00167 | 0.00027 | pass | pass | 4.56 |
| Letter Frost | multi-view | MIMLMAPkNN_AveH(10) | 5 | +0.0744 | +2.62 | +3.66 | 0.0215 | 0.0042 | fail | fail | 4.56 |
| Letter Carroll | multi-view | MIMLDGC_AveH(10) | 5 | +0.0620 | +2.27 | +3.17 | 0.034 | 0.0071 | fail | fail | 4.56 |
| Yeast | bag-mean | MIMLIBLR_MaxH(10) | 10 | +0.0115 | +2.63 | +5.39 | 0.000438 | 1.6e-05 | pass | pass | 1.95 |
| Reuters | bag-mean | MIMLNN | 10 | +0.0097 | +1.80 | +3.67 | 0.00512 | 0.0003 | pass | fail | 1.95 |
| Emotions | multi-view | MIMLDGC_MaxH(10) | 10 | +0.0093 | +0.54 | +1.10 | 0.299 | 0.12 | fail | fail | 1.95 |
| Scene | multi-view | MIMLIBLR_MaxH(10) | 10 | -0.0571 | -3.18 | -6.51 | 0.00011 | 3.4e-06 | pass | pass | 1.95 |
| Birdsong | multi-view | MIMLDGC_AveH(10) | 10 | -0.0562 | -1.27 | -2.60 | 0.0287 | 0.003 | fail | fail | 1.95 |

Survivors: 4/8 at m=8; 3/8 at m=16 (scenario).

### D. Global Wilcoxon signed-rank test over datasets: Monte Carlo power

Two-sided, alpha = 0.05, exact null; 20000 draws per cell; numpy default_rng(20261012). Observed submitted-protocol dataset deltas (Part B): mean +0.0225, SD 0.0633. Every draw adds N(0, 0.005^2) jitter so |d| has no ties.

(i) 'observed' = resample the 8 observed deltas with replacement. (i') 'normal' = N(observed mean, observed SD), the form used in PREREG__review_2.md computation (c). (ii) 'sign p' = resample the 8 observed |delta| and give each a positive sign with probability p (sign-consistent alternative).

| test | n | min attainable p | (i) observed | (i') normal | (ii) sign p=0.6 | (ii) sign p=0.75 | (ii) sign p=0.9 |
|---|---|---|---|---|---|---|---|
| primary: all 16 H1 rows | 16 | 3.1e-05 | 0.365 | 0.245 | 0.099 | 0.419 | 0.898 |
| primary, collapsed (proteins -> 1, Letters -> 1) | 12 | 0.00049 | 0.285 | 0.175 | 0.080 | 0.331 | 0.790 |
| sensitivity: 10 new-data rows | 10 | 0.002 | 0.263 | 0.167 | 0.086 | 0.291 | 0.710 |
| sensitivity, collapsed (proteins -> 1) | 7 | 0.016 | 0.158 | 0.118 | 0.071 | 0.220 | 0.593 |

### Interpretation

- **Single 5-fold was hopeless at the first Holm step:** at m = 16 it needs d_z > 4.56 and has 24 % power at d_z = 3. Under 5×5 repeated CV (§1.2) the threshold is 1.95 and power at d_z = 2 is 54 %.
- **Primary F-H1 (m = 16).** Single 10-fold rows need d_z > 1.95 at the first step and > 1.11 at the last; power at d_z = 1 is 9 % (first step) to 45 % (last). 5×5 rows need 1.95; HJA Birdsong (5×10) needs 1.24 and is the best-powered row. True effects with d_z ≤ 1 will mostly come out "not significant", which §1.6 reads as **inconclusive**, not "no effect". Enlarging the family from 10 to 16 raises the single 10-fold first-step threshold from 1.80 to 1.95.
- **New-data sensitivity (m = 10).** Single 10-fold rows need d_z > 1.80; HJA Birdsong 1.17.
- **Submitted state (Part B, descriptive).** With the §1.6 correction and the test-selected comparator, MSRC v2 (d_z = 5.38), Yeast (2.63, leaky, bag-mean arm) and Scene (−3.18) survive in the m = 16 scenario; Reuters (1.80) survives at m = 8 only; Letter Frost (2.62) and Letter Carroll (2.27) fail only because single 5-fold puts their threshold at 4.56, and would clear 1.95 under 5×5 if their d_z holds; Emotions (0.54) and Birds (−1.27) fail. These numbers come from a protocol this file replaces.
- **Other families (Part C).** The H2 (m = 28), H4 (m = 42), H4-padded (m = 16) and H5 (m = 20) families need d_z ≈ 1.95–2.3 at the first step, with power ≤ 9 % at d_z = 1. Their nulls are expected to be largely inconclusive, and the manuscript says so in advance. H2's library arms are slightly better powered than its TabPFN arms because their n₁ is larger.
- **Global test (Part D, M2).** Drawing dataset deltas like the 8 observed ones (mean +0.0225, SD 0.063), the primary two-sided Wilcoxon over 16 datasets rejects in 25 % (normal draws; PREREG__review_2's form gave 24 %) to 37 % (resampling the observed values) of draws, and in 18–29 % after collapsing proteins and Letters (n = 12). The new-data test (n = 10) rejects in 17–26 %. The primary test reaches 90 % only if 9 in 10 datasets favour MIML-PFN with the observed magnitudes. **"Global test not significant; Holm wins on X, losses on Y" is the likely outcome**, and G3 (§1.6) is pre-worded for it.

---

## Response to `PREREG__review_2.md` (round 2)

| finding | where addressed in v3 |
|---|---|
| **B1** H2-B empty family; instance-level purge with size-matched control, upper bound | H2-B (leak purge on source-example indices; per-bag size-matched random-row control, seeds {0,1,2}; not-estimable clause on instance rows; n₁ = post-purge bags; upper-bound wording); §1.6 n₁ rule; §7 C |
| **B2** library infeasible on VOC; no cap; "did not complete" undefined for Java/Octave | §6.3 (library pilot and projection), §6.5 (300 process-hour cap; reduced grid fixed now: inner 3-fold, {AveH, MaxH}, k {10, 20}, MIMLNN ratio {0.2, 0.4}, λ = 1, seeds {0, 1}; caching via a custom `IDistance` only if T03-d is byte-identical), §6.6, §6.7 |
| **B3** device, absolute cap, post-PCA no-op, sequential trigger | §6.1 (device per arm fixed; GPU logged before first fit; one global MPS fallback), §6.0 (execution order), §6.4 (trigger from H1 arms, inherited by all others), §6.6, §6.7 (120 device-hour cap per unit after PCA; total budgets; stop-and-request rule; execution order), as revised in round 3 |
| **M1** H5 recipe, pairing unit, split for MSRC/LF | H5 (recipe; pairing unit = outer fold, seed-mean; 5×5 for MSRC v2 and Letter Frost) |
| **M2** global test: power, sidedness, pseudo-replication, CI, wording | §1.6 Global hypothesis (two-sided, HL median + CI, collapsed sensitivity, G1–G3); §7 D |
| **M3** baseline preprocessing | §1.4 |
| **M4** cross-scorer selection; no stored predictions | §1.3 (all candidates scored by `miml_metrics.py`), §1.5 (`PredictDump.java`, Octave driver, fallback rule), §6.8 T03-b/c/f |
| **M5** VOC2012 definition | §0.1 (hash, extractor, grid, image set, labels, sibling files excluded, why 128, 769 features, 10 000-row limit, release) |
| **M6** remainder bags; non-comparability | H2-A step 1 (remainder rows excluded from all pools and bags); H1 and H2-A non-comparability sentence |
| **M7** H3 cross-device | H3 (Yeast bag-mean rerun on the same device; hardware-sensitivity flag; Birds flagged) |
| **M8** n₁ rule | §1.6 "n₁ and n₂, one rule"; §7 A labelled MIML-PFN vs library, §7 C per family |
| **m1** d_z,corr | §1.6 Reporting (dropped; t reported) |
| **m2** "most favourable case" mislabel | §7 B: the m = 16 column is now described as "a scenario … not a bound in either direction" |
| **m3** deposit the original August files | header table; §1.8 |
| **m4** release construction procedure and mapping | §1.8 |
| **m5** `bagmean_card` on constant-size sets; which CI | H4 (not run; bag-mean reused and labelled; unadjusted 95 % CI with corrected variance) |
| **m6** H4 and H5 families in the power table | §7 C |
| **m7** why 5×5 not 10×10 | §1.2 |
| **m8** projections for all R2 datasets before any R2 result | §6.3 |
| **m9** T03 checks listed | §6.8 |
| **m10** per-fold SDs | §1.6 Reporting |
| **m11** multiview in the cross-device check | §6.9 |
| Part 3 (reviewer requests R1-M04 … R6-M08) | each "after the fixes" cell is met by the rows above: R1-M08 by M1; R2-03 by B1, m4, B.1, B.2; R2-04 by M2, B.7; R2-08 by M4, M5, B.6, B.9; R6-M01 by B1, B.10; R6-M05 by M3; R6-M08 by m10 |
| Part 4 (executability) | device (§6.1), stalls (§6.5–§6.7), empty H2-B (H2-B), neural recipe (H5), preprocessing (§1.4), remainder bags (H2-A), n₁ (§1.6), `bagmean_card` on Scene (H4): each now fixed in the text |

## Response to the fact-checkers' gaps (B.1–B.12)

| item | where addressed in v3 |
|---|---|
| **B.1** H2-A must not z-score test pools with test statistics | H2-A steps 1–4 (construction per outer split; scaler on outer-training rows only; bags within own-fold pools; remainder rows excluded); step 5 (grouped inner CV) |
| **B.2** native duplicates; de-duplicated Reuters | H1 "Reuters de-duplicated sensitivity" and native-set overlap table |
| **B.3** labels; POST-HOC label | Superseded by the user decision of 2026-10-13: all rows CONFIRMATORY, eight "direction previously observed", new-data sensitivity family; POST-HOC kept. Labels (header); §1.6 families; H1, H4, H5 labels |
| **B.4** fit vs predict time; energy | §6.2 (separate times; NVML on G; `powermetrics` with sudo as user action; otherwise "not measured"; peak RSS as common memory measure) |
| **B.5** surrogate faithfulness; neural recipe; pairing unit | H5 measurement (c); training recipe; cross-evaluation pairing |
| **B.6** save per-bag scores and binary predictions; KDIS harness | §1.5 (what, where; `PredictDump.java` against the unmodified jar via `MIMLClassifier.makePrediction`; MIMLNN driver; fallback) |
| **B.7** wording for significant-but-small effects | §1.6 Outcomes and wording (δ_ds = one fold-SD of the library's AP) |
| **B.8** width-matched null | H4 `tabpfn_padded` (permuted real columns within fold, seeds {0,1,2}, +1 = cardinality column), F-H4-padded, width share s with outcomes W0–W3, instance-subsampling curve and rule |
| **B.9** VOC2012 "naturally occurring" | §0.1 (provenance), §0.2 (native rule; patch-level ground truth) |
| **B.10** T01 dataset facts | §0.1 (8 of 13 files ours; protein filters 234→21, 321→52, 320→28, 340→46; Birds (MLSP 2013); Letters 26 columns, 24 ever positive; four sets "constructed by the authors") |
| **B.11** Dembczyński et al. paraphrase | H5 "Theory cited" (checked against the open-access *Machine Learning* text, §4.1 eq. (13), §4.2 Theorem 1; v2 paraphrase withdrawn) |
| **B.12** August pre-registrations cannot be publicly timestamped | header (no version control before 2026-10-12; sha256 and local dates; user action), §1.8 |

## Response to `PREREG__review_1.md` (round 1; pointers updated to v3)

| finding | where addressed |
|---|---|
| F1 repeated CV, power | §1.2, §7 |
| F2 families, global test | §1.6 |
| F3 validity, ddof, d_z, NS ≠ tie | §1.6 |
| F4 inner CV, degenerate labels, optimism, `tr[:v]` quirk | §1.3 |
| F5 80 % vs 100 % asymmetry, n₂/n₁ | §1.3, §1.6 |
| F6 thresholding, 0.5 sensitivity, AP involves no selection | §1.3 |
| F7 procedure name, tie-break | §1.3 |
| F8 MIMLNN seeds | §1.3 |
| F9 MIMLNN grid fixed now | §1.3 |
| F10, F11, F17 budget, stop rule, PCA d′, hardware | §6 |
| F12 leakage-free rebuild + purge control | H2-A, H2-B |
| F13 overlap quantification, release | H2, §1.8 |
| F14 ties and duplicates | H2-A step 3 |
| F15 meaning of a null | H2 decision |
| F16 Yeast cap, device, wording | H3, §6.1 |
| F18 a-priori groups | §0.2 |
| F19 ratio rule only where CI excludes 0 | H4 |
| F20 Smooth-AP, cross-evaluation family | H5 |
| F21 public timestamp | header, §1.8 |
| F22 label wording | Labels (header) |
| F23 memory and energy | §6.2 |
| F24 remainder bags | §1.1, H2-A |
| F25 cross-device | §6.9 |
| F26 larger natural dataset | §0 (VOC2012, HJA Birdsong) |

## Change table: inputs from the STEP1 fact-check reviews (`STEP1-R2R5__review_1.md`, `STEP1-R2R5__review_2.md`, `STEP1-R1__review_1.md` F2)

| input | change in v3 | where |
|---|---|---|
| **H1 labelling** | **USER decision 2026-10-13 (overrides orchestrator recommendation)**, `DECISIONS.md` 2026-10-13 row (amends the orchestrator's 2026-10-12 row, which made seen datasets EXPLORATORY; that earlier split, drafted in v3 in response to R2-07, is withdrawn). All 16 H1 rows are CONFIRMATORY under the new protocol; Scene, Reuters, MSRC v2, Letter Frost, Letter Carroll, Birds (MLSP 2013), Emotions and Yeast carry "direction previously observed". The primary Holm family (m = 16) and the primary global Wilcoxon run over all rows. A pre-specified sensitivity analysis repeats Holm and the global test on the 10 new-data rows (HJA Birdsong, VOC2012, Protein ×4, rebuilt Emotions, Yeast, Medical, Corel5K) and is reported alongside, answering R2-07's request for separation. The leaky originals of the four constructed sets stay EXPLORATORY, in no family. §7 recomputed for m = 16 and m = 10. | Labels (header); §1.6 families and global hypothesis; H1; §6.7; §7 |
| POST-HOC label | Added | Labels (header); H1, H4, H5 |
| R5-02 width control: permuted real columns, not noise; TabPFN only with fixed constructor; three outcomes; seeds {0,1,2}; +1 column stated; width share s with corrected CI, only where Δ(multiview) CI excludes 0; "width-insufficient" only if upper CI of s < 0.5 | `tabpfn_padded` replaces v3-draft `null_perm`/`null_gauss` (Gaussian fill dropped); permutation within outer training fold and within test fold separately; +1 = cardinality column, permuted; outcomes W0–W3 | H4 |
| Instance-subsampling curve with a pre-stated rule | f ∈ {0.25, 0.5, 0.75, 1.0} plus single-instance (degenerate width-matched control), seeds {0,1,2}; Δ_inst = g(1.0) − g(0.25) with three worded outcomes | H4 |
| Wording ceiling | "higher-order bag statistics and/or cardinality, not width", only where W1 holds; never "multi-instance structure" | H4 |
| Global Wilcoxon: sidedness, Hodges–Lehmann CI, effect size | two-sided (already); HL median with exact CI; matched-pairs rank-biserial r added to G1–G3 | §1.6 |
| Table VI "folds in agreement" | Banned from every revision table and sentence | §1.6 Reporting |
| MIML-PFN's only tuned quantity; per-fold selected baseline configs | Stated as a manuscript sentence; per-fold selection table | §1.3 |
| Repeated-10-fold sensitivity on canonical-split datasets (R5-04) | r = 5 × k = 10, seeds {10..14}; logreg always, TabPFN bag-mean on local MPS where ≤ 72 MPS-hours, nested library where ≤ 300 process-hours | §1.9; §6.1 exception; §6.7 level 8 |
| Dembczyński et al. 2012 wording (STEP1-R1 F2) | Eq. 13 / Thm 1, eq. 18 / eq. 20, §5 Prop. 2 cited; "does not say Hamming and rank losses have different minimisers in general"; our metric and surrogate are normalised | H5 "Theory cited" |
| Dataset-group arithmetic (STEP1-R2R5 review 2, finding 5) | Explicit membership: 7 + 4 + 4 + VOC2012 = 16; the submitted 13 = 6 + 4 + 3 | §0.1 |
| Remaining checklist items (instance-level purge with upper-bound reading; H2-A scaler on outer-training rows; Reuters de-dup row; B2 Java/Octave caps and reduced VOC grid; energy and fit/predict split; surrogate faithfulness and H5 recipe; per-bag predictions; small-effect wording) | Already in v3; unchanged | H2-B; H2-A; H1; §6.5–§6.6; §6.2; H5; §1.5; §1.6 |

## Response to `PREREG__review_3.md` (round 3)

| finding | change | where |
|---|---|---|
| **B1** H2-B control not matched on centre deletion | Control stratified on centre status: it deletes the centre iff the leak purge did, and the rest among non-centre rows. Centre-deletion rates recomputed from the CSVs (leak 0.238 / 0.255 / 0.073 / 0.054; an unstratified control would give 0.432 / 0.424 / 0.573 / 0.645), reproducing the reviewer's table. The upper-bound argument is restated for the matched design; label carriage is disclosed | H2-B |
| **M1** order of §6.3–§6.7; PCA trigger set; §5 contradiction | §6.0 seven-step order; PCA trigger from H1 arms only, inherited by H2-B/H3/H4/§1.9; §5 and T03 are fixed-cost pre-projection items outside budgets and order; pilot hours not counted | §6.0, §6.4, §5, §6.8 |
| **M2** concurrency-gameable timing | One TabPFN process per device; N = 8 concurrent runs on C, identical in pilot and run; threads pinned; process-hours = CPU time (user + sys); per-run timeout in CPU time; load average and concurrency logged with every timing | §6.1, §6.2, §6.6 |
| **M3** H4 gate and sign; winner's curse; ratio CI | Gate = CI of Δ(multiview − bagmean) above 0; fixed sentence for CI below 0; conditioning bias disclosed; Fieller interval beside the delta method, thresholds require both; test-bag subsampling changes the task (stated) | H4 |
| **M4** §1.9 misses the multiview headline arm | `tabpfn_multiview` added on MPS under the same 72 MPS-hour gate; purpose reworded | §1.9 |
| **m1** `tr` ordering | Stated for canonical, repeated (§1.2, §1.9) and H2-A designs; H2-A inner folds of 2, 2, 2, 2, 1 pools | §1.3, H2-A step 5 |
| **m2** Wilcoxon tie clause | scipy 1.18.0, `method="exact"`, `zero_method="wilcox"`; ties reported, no fallback claimed | §1.6 |
| **m3** "never-run" name | Renamed F-H1-newdata, "no prior number on this data version"; abstract sensitivity sentence carries the qualifier for rebuilt Emotions and Yeast | §1.6, H1 |
| **m4** pilot fit count | Pilot uses the production fit count fixed by §5 | §6.3 |
| **m5** refit multiplier | Refit time measured in the pilot; ≈ 1.56× (5-fold) and 2.25× (3-fold) stated as the n² expectation | §6.3 |
| **m6** dangling references | T03 and T11 marked "to be created", with content fixed here; converter paths in `../MIML_CLAM_Enhanced/` given exactly; `PredictDump.java`, `run_mimlnn.m` extension, `DEVICE_LOG.md`, `PROJECTIONS.md` described as to be written | §1.5, §1.8, §6.0, §6.1, §6.8, §0.1 |
| **m7** H2-B multiview on ~2-row bags | Disclosed; degenerate statistics need no special handling | H2-B |
| **m8** "nothing descoped" vs drops | Drop order removed. Stop before the exceeding unit, record projections, request an extension by a dated AMENDMENT; a unit is dropped only by a user decision in `DECISIONS.md` (user decision 2026-10-12); priority list kept as execution order only. The library cap and §6.6 limits follow the same rule | §6.5, §6.6, §6.7, H3 |
| **m9** deposit hygiene | "Deposited version" header row for commit hash and sha256, filled at deposit; `__pycache__` excluded | header, §1.8 |

## Response to `PREREG__review_4.md` (round 4)

| finding | change | where |
|---|---|---|
| **M1** one global sequence over two devices | §6.0 rewritten as two queues. C queue: T03 → H2-A construction and H2-B masks (with overlap checks) → C pilots → §6.5 caps → C caps and budgets → C section of `PROJECTIONS.md` → C runs → MPS tail. G queue: `DEVICE_LOG.md` → §5 → G pilots → §6.4 PCA trigger → G caps and budgets → G section → G runs → §6.9. Four cross-queue dependencies named. The §6.7 execution order applies within each queue, and C work starts before the GPU credits | §6.0, §6.3, §5, §6.8 |
| **m1** S_f on raw indices | Source identity = vector id for centres and members; centre row defined as an instance position; zero-overlap check for the leak arm; H2-B table regenerated on vector ids (Medical 0.629 / 13.6 % / 0.076 [0.051–0.097] / 0.571; the other three unchanged); duplicate counts (11 / 2) reported; §7 C recomputed with e = 0.136 | H2-B; §7 C |
| **m2** §1.9 gates self-executing | Routed through the stop rule: hold, record, AMENDMENT; drop only by user decision | §1.9 |
| **m3** JVM heaps vs 24 GiB | `-Xmx2g` default, `-Xmx8g` for VOC2012 and Corel5K; N = min(8, ⌊16 GiB / Xmx⌋); N recorded; OOM retry at doubled Xmx and halved N; no MPS TabPFN during a timed C batch | §6.1, §6.0 C-queue step 8 |
| **m4** load-independence over-claimed | N ≤ 10 performance cores; no other CPU-bound process during timing; Octave threads pinned; re-time if load average > 10; claim softened | §6.1 |
| **m5** §1.9 cross-device juxtaposition | Sixth run on the canonical split on MPS; comparisons within device only | §1.9 |
| **m6** environment vs device | T03-g: pinned-thread reproduction of stored `logreg_bagmean` Scene (≤ 1e-9) and `tabpfn_bagmean` Letter Frost on MPS (≤ 1e-3), before §6.9 | §6.8, §6.9 |
| **m7** broken sentence | Global-test bullet repaired | §1.6 |
| **m8** header and deposit | `experiments/revision_r1/` tracked (`38013d0`, `b72856e`); deposit precedes step 1 of either queue; reviews 1–4 in the deposit list | header, §1.8 |
| **m9** `tr` order on H2-B; prediction-path collisions | H2-B order stated; path carries dataset version, arm, config, condition and seed; no-overwrite rule | §1.3, §1.5 |

## Response to `PREREG__review_5.md` (round 5)

| finding | change | where |
|---|---|---|
| **m1** condition tokens; H5 key | Tokens joinable with `+` (e.g. `control-s1+seed-s3`); H5 key stated: arm = model, config = surrogate, condition = seed | §1.5 |
| **m2** self-referential hash | The deposited copy reads "to be filled"; a follow-up commit records its hash, sha256 and URL/DOI; the archive checksum is binding | header, §1.8 |
| **m3** device table, fallback deadline, serialisation | Row 1 "except §1.9 and T03-g"; fallback recorded before the first G-queue fit; under the fallback the queues serialise, C first | §6.1 |

## Response to `PREREG__review_6.md` (round 6)

| finding | change | where |
|---|---|---|
| **1** G and MPS canonical-split runs, and T03-g / §6.9 on Letter Frost, share a path | Device token `+g` / `+mps` on every TabPFN `<condition>`; version `submitted5` for runs on the submitted seed-42 5-fold splits | §1.5 |
| N1 "the one stated exception" | Now "one of the two MPS exceptions in §6.1, with T03-g" | §1.9 |
| N2 history rows stop at review 4 | History and Version-control rows extended through review 6 and commits `d2c1103`, `5e29f54` | header |

## Response to `PREREG__review_7.md` (round 7)

| finding | change | where |
|---|---|---|
| **1** `<config>` undefined for TabPFN; H3 vs H1 leaky Yeast share a path when widths differ | `<config>` for TabPFN = width token `native` / `pca500`; the H1 leaky-column Yeast rows are the H3 units when widths coincide, a separate `pca500` unit otherwise | §1.5 |
| N1 §1.9 sixth run under the MPS fallback | Reuses the H1 `main+mps` unit | §1.5 |
| N2 §6.9 Scene | The H1 Scene bag-mean unit, reused | §1.5 |
| N3 §5 predictions | Written under `verify-2fit` / `verify-1fit` plus the §6.1 device token (wording generalised in round 8), kept and deposited, never reused as H1 units; splits named | §1.5, §5 |
| N4 §6.1 row 3 wording | "one of the two MPS exceptions, with T03-g" | §6.1 |
| general | "Where two procedures name the same unit, the unit is fitted once and reused; the manifest lists every procedure that uses it." | §1.5 |

## Response to `PREREG__review_8.md` (round 8)

| finding | change | where |
|---|---|---|
| **F1** §6.9 and T03-g under the MPS fallback; literal `+g` in reuse bullets | Reuse bullet added: under the fallback, §6.9's Letter Frost `tabpfn_bagmean` is the T03-g unit, and §6.9 is reported as a same-device environment check. Reuse bullets use `<dev>`; the `verify-*` tokens take "the device token of §6.1" | §1.5 |
| **F2** `<config>` for logreg | `default` (`LogisticRegression(max_iter=1000)`, no tuned quantity) | §1.5 |
| N1 width token of a PCA no-op | `native` | §1.5 |
| N2 header history | History and Version-control rows extended through review 8 and commit `155e4e2` | header |

## Addendum change table (pre-deposit addendum, 2026-10-13)

Source: the fifteen `DECISIONS.md` rows dated 2026-10-13 that carry implementation decisions, all orchestrator rows: (1) T03; (2) T02; (3) T04/T07; (4) T04/T07 refinements, which supersede the matching parts of row 3; (5) T03 decisions part 2; (6) d′ scope, which refines row 4; (7) refit-failure consequence; (8) projection approximation (fold-0 non-constant label count); (9) library refit projection bound; (10) review-11 clarifications: the d′ rule applies only to arms with d > 500; the library refit order is ascending canonical index; H2-A test bags are stored in `get_cv_splits` block order; (11) KDIS non-determinism fallback; (12) deposit-line format and the single shared deposit check; (13) KDIS fallback labelling (MIMLBagging `seed-sK` vs `rep-rK`); (14) deposit-line grammar tightened; (15) deposit date no later than the current UTC date. Also the deposited evidence file `evidence/T02__duplicate_pool_check.txt`. Every rule is written out in full in the section named, so the deposited text is self-contained. Task files are working notes and are not needed to read it. No experiment had run when these were written.

| DECISIONS item | rule written | section |
|---|---|---|
| **T03** inner folds | `default_rng(1000 + f + 100r).permutation(tr)`, then `np.array_split`, larger blocks first; same block rule for §1.2 / §1.9 outer blocks | §1.3, §1.2 |
| T03 tie-break after k | distance alphabetical; MIMLNN smaller ratio, then smaller λ | §1.3 |
| T03 inner SD | ddof = 1 | §1.3 |
| T03 MIMLNN seeding | `clock.m` shim, authors' files unmodified; "seed s" = `rand('state', s)` | §1.3 |
| T03 crash | a crash in any (inner fold, seed) excludes the candidate for that outer fold | §1.3 |
| T03 refit failure | (fold, metric) recorded failed, stop rule, no runner-up fallback; only selected candidates are refit | §1.3 |
| DECISIONS row (9), library refit projection bound | bound per outer fold = Σ over the 8 methods of each method's 5 largest measured candidate refit times (library selections are a subset of the per-method ones) | §6.3 |
| T03 F4 on library outputs | the degenerate-label rule applied identically to KDIS and MIMLNN outputs | §1.3 |
| T03 features | lossless float64 for library inputs (submitted export used `%.6g`) | §1.4 |
| T03 purged versions | ordinary §1.3 inner rule | §1.3 |
| **T02** artefact paths | `results/revision_r1/constructions/<ds>/{rebuilt, purged/<condition>}/r0_f<f>.npz`, `MANIFEST.sha256` | §1.5 |
| T02 control RNG | fresh `default_rng(seed)` per (dataset, fold); canonical bag order; draw only when m > 0 | H2-B |
| T02 ties | rtol 1e-9 on `math.fsum` distances; lower index wins | H2-A step 3 |
| T02 not estimable | masks still written and flagged | H2-B |
| T02 test-bag order (DECISIONS row (10)) | canonical block order (fold f as `get_cv_splits` returns it; no metric depends on it) | H2-A step 7 |
| DECISIONS row (11): KDIS non-determinism fallback | a method found non-deterministic by T03-a runs 5 independent times per (candidate, fold), metrics averaged before selection; MIMLBagging `<seed>` 0–4; other repetitions uncontrolled, disclosed, across-run SD reported; harness code-reviewed before any KDIS production run; replaces "the same seed rule applies to KDIS" | §1.3, §6.8 |
| DECISIONS row (11): KDIS fallback storage tokens | `seed-s0..s4` for MIMLBagging (`<seed>` 0–4) and `rep-r0..r4` for other KDIS methods, each repetition a separate stored unit with `uncontrolled: true` in its sidecar; the repeat switch is driven only by the T03-a result file | §1.5, §1.3 |
| DECISIONS row (12): deposit-line format | after deposit, the Public-timestamp cell reads exactly `https://doi.org/<DOI> (YYYY-MM-DD)` (published record's DOI and publication date); `deposit_check.py::deposit_recorded()` accepts only a whole-cell full match; anything else keeps the real-data guard closed | §1.8, header (Deposited version row) |
| DECISIONS row (13): KDIS fallback labelling | MIMLBagging uses `seed-sK` only where `<seed>` demonstrably controls its randomness (byte-identical runs under one seed); if T03-a finds it non-identical, its repetitions are `rep-r0..r4` with `uncontrolled: true`, like the other methods | §1.3, §1.5 |
| DECISIONS row (14): deposit-line grammar tightened | ASCII-only matching (`re.ASCII`); the DOI suffix ends in `[A-Za-z0-9]`; the date is ≥ 2026-10-13; close-only | §1.8 |
| DECISIONS row (15): deposit date not in the future | the date must also be ≤ the current UTC date when checked; close-only | §1.8 |
| review 14 (F1 and notes) | MIMLBagging `rep-rK` runs still set `<seed>` = k, recorded in the sidecar, and stay labelled uncontrolled; the further close-only `deposit_check.py` rules (placeholder DOIs, prefix 10.5072, "sandbox") are named; `deposit_check.py` committed at `933b185` | §1.3, §1.5, §1.8 |
| DECISIONS row (10): refit training order | library refit trains on outer-training bags in ascending canonical index, on every version and design | §1.3 |
| T02 acceptance check | `masks.json` must reproduce the H2-B table | H2-B |
| T02 duplicates, rule B | vector-id identity; non-lowest duplicates dropped before pooling (Medical 11 / 978, Corel5K 2 / 4873); remainder-row rule; 3 same-feature different-label groups disclosed as irreducible error; vector-level overlap is a hard stop | H2-A steps 3–4 |
| T02 pool sizes | no longer exactly ⌊n/10⌋: Medical test folds 0, 1, 2, 3, 4, 6, 7, 9 lose bags (pools 5, 8 none); Corel5K pools 4, 5; reported per split | H2-A step 4 |
| **T04/T07** PCA components (as refined; restricted to d > 500 by DECISIONS row (10)) | d′ fixed per dataset = min(500, min over folds of n_rows(`fit_i`) − 1, d); width token `pca<d′>` added to the §1.5 token list; `native` when d′ = d | §6.4, §1.5 |
| T04/T07 one fit (as refined) | one `.fit` per label, then two separate `predict_proba` calls (`val_i`, test), never concatenated | §5 |
| T04/T07 PCA pipeline | z-score on `fit_i`, then `PCA(svd_solver="full", random_state=0)` (deterministic), no re-scaling | §6.4 |
| T04/T07 VOC instance PCA | PCA-128 fitted per outer split before subsampling | §1.4 |
| T04/T07 precision | float32 instance features; bag-mean/bag-max matrices float32; arms with the cardinality column (multiview incl. subsampled, padded, bagmean_card) float64 as in the submitted runner (footnote ¹, from CODE-T04T07 review 1, finding 6); rebuilt bags cast to float32 | §1.4 |
| T04/T07 padded and subsampling RNG | draw calls and generator scope written out in full (`rng.permutation(n_train)` / `rng.permutation(n_test)` per column j = d…6d; a fresh `default_rng(seed)` per version, split file, fraction and seed with `rng.choice(n_i, size=m_i, replace=False)`) | H4 text, above |
| T04/T07 constant labels; pilot mean (as refined); fold-0 label count (DECISIONS row (8), projection approximation) | not fitted; pilot mean over fitted labels among the first 3, extended to the first 3 non-constant if needed; hours = per-fit × non-constant labels, counted on outer fold 0's `fit_i` and applied to every fold (projection only) | §1.3, §6.3 |
| T04/T07 PCA trigger set | H1 primary arms, rebuilt versions for the constructed four; leaky originals inherit; H3 Yeast native | §6.4 |
| T04/T07 §1.9 gate | includes the canonical MPS sixth run (conservative) | §1.9 |
| T04/T07 refinements: seed units | one stored unit per seed token; seed means at analysis | §1.5, H4 |
| T04/T07 refinements: memory and energy | `ru_maxrss` process-lifetime; device peak per fold (CUDA reset per fold; MPS sampled); NVML energy per fold | §6.2 |
| T04/T07 budget hold | independent later units continue within the remaining budget | §6.7 |
| **d′ scope** (with DECISIONS row (10): only arms with d > 500; d ≤ 500 stays `native`, e.g. Birds multiview 229) | one d′ per dataset across versions = min(500, d, min over H1 and `rcv10` folds incl. the sixth run of n_rows(`fit_i`) − 1); assert in every fold; Haloarcula `pca218`; TabPFN 2.2.1 guard | §6.4, §1.5 |
| **T03 part 2** checks' splits | `submitted5` when compared with a stored submitted number; otherwise 5×5 repeat 0 | §6.8 |
| T03 part 2 tie | |Δ| ≤ 1e-12 absolute | §1.3 |
| T03 part 2 constant-negative score | 0.0 KDIS, −1.0 MIMLNN | §1.3 |
| T03 part 2 ARFF id header; MIMLIBLR | whole-universe convention; emptied purged bags left out; MIMLIBLR id dependence disclosed | §1.4 |
| T03 part 2 wall guard | 4 × the CPU limit | §6.6 |
| T03 part 2 inner training order | ascending canonical index | §1.3 |
| T03 part 2 T03-b | scores raw output | §6.8 |
| T03 part 2 MIMLNN complex outputs | real part; max \|imag\| logged; flagged above 1e-8 | §1.3 |
| T03 part 2 T03-g | TabPFN part run by task T04 | §6.8 |
| T03 part 2 all-positive bags | LAMDA drop moot (none exist) | §1.4 |
| T03 part 2 library I/O | train/test ARFF pairs as submitted | §1.4 |
| DECISIONS row (7), refit-failure consequence | (dataset, metric, selection) row "did not complete", excluded from that metric's Holm family, no imputation, m reduced and stated | §1.3, §1.6 |

## Response to `PREREG__review_10.md` (round 10)

| finding | change | where |
|---|---|---|
| **1** d′ scope row missing; `pca219` | d′ = min(500, d, min over H1 and `rcv10` folds incl. the sixth run of n_rows(`fit_i`) − 1), same d′ on every version, an assert in every fold; worked table (Haloarcula `pca218`, Pyrococcus 305, Geobacter 272, Azotobacter 292, Birds 184); examples changed to `pca218`; TabPFN 2.2.1 guard | §6.4, §1.5 |
| **2** T03 part 2 missing | tie 1e-12; constant-negative 0.0 / −1.0; inner order canonical; check splits (`submitted5` vs 5×5 r0); 4× wall guard; id header and MIMLIBLR disclosure; complex outputs; T03-b raw; T03-g by T04; train/test pairs; all-positive drop moot | §1.3, §1.4, §6.6, §6.8 |
| **3** commit and header | History row records review 9 RESOLVED at `prereg-v3-final` (`62a86a6`) and the addendum reviewed in rounds 10–11; Version-control row adds `62a86a6`, `3c720d8`; the round-10 text is committed by the orchestrator after this edit | header |
| **4** refit-failure consequence | Orchestrator decision: the (dataset, metric, selection) row did not complete, is excluded from that metric's Holm family, no imputation, m reduced and stated | §1.3, §1.6 |
| **5** §1.2 vs H2-A inner rule | "every ordinary inner split (§1.3); H2-A rows use the grouped rule" | §1.2 |
| **6** two no-op definitions | One definition: d′ = d | §1.5 |
| **7** superseded §6.3 formula | Struck through | §6.3 |
| **8** H4 draw calls and generator scope | `rng.permutation(n_train)` / `rng.permutation(n_test)` per column j = d…6d; a fresh generator per (version, split file, fraction, seed); `rng.choice(n_i, size=m_i, replace=False)`, positions sorted | H4 |
| **9** wording | "Irreducible error" is placed in the original files and H2-B; the `clock.m` mechanism is described as it works | H2-A step 3, §1.3 |
| **10** acceptance checks | H2-B at the table's printed precision; an H2-A counterpart with the dropped-row lists and pool sizes | H2-B, H2-A step 4 |
| **11** provenance | Source line names the six DECISIONS rows and the team-lead instructions; each rule written out in full; task-file pointers removed from the change table. The two DECISIONS lines that review 10 asks for (refit projection, fold-0 count) are for the orchestrator to add; this file does not edit `DECISIONS.md` | addendum change table |

## Response to `PREREG__review_11.md` (round 11)

| finding | change | where |
|---|---|---|
| **1** d′ formula vs "d ≤ 500" vs table | The d′ rule applies only to arms with d > 500; arms with d ≤ 500 stay `native`. Birds row annotated (width 229: `native`); §1.5 no-op definition extended | §6.4, §1.5 |
| **2** "(or SDs)" | Deleted; the 1e-12 tie applies to inner means only, SDs compared exactly | §1.3 |
| **3** acceptance checks not in code | Named: `experiments/revision_r1/h2_acceptance.py` (T02) with the plan's expected constants, run at C-queue step 2 before any read; a mismatch stops the queue | §6.0 |
| **4** provenance and History | Source line names all nine 2026-10-13 DECISIONS rows; the change-table rows cite rows (7)–(9); History records round 10 at `3c720d8`, round 11 at `589a980`, round 12 at the next commit | addendum change table, header |
| **5** refit training order | Library refit passes outer-training bags in ascending canonical index on every version and design; the inner order rule also covers the H2-A grouped folds | §1.3 |

## Response to `PREREG__review_12.md` (round 12)

| finding | change | where |
|---|---|---|
| **1** H2-B acceptance precision | Per-column precision stated as `h2_acceptance.py` checks it: rows per surviving bag to 2 decimals (±0.005), the other columns to 3 decimals (±0.0005), bags emptied as a fraction to 0.1 % | H2-B |
| **2** rules without a DECISIONS row | Source line names ten rows, including (10) review-11 clarifications; it is cited from the change-table rows for PCA components, d′ scope, refit training order and test-bag order | addendum change table |
| **3** stale provenance | Version-control row lists `62a86a6`, `3c720d8`, `589a980`, `619f844` and says round 12 reviewed `619f844` and the round-12 fixes are committed after this edit; §6.0 step 2 says `h2_acceptance.py` is committed | header, §6.0 |

