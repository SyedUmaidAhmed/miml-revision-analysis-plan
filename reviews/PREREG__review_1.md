# Review 1 of `experiments/revision_r1/PREREGISTERED.md` (draft of 2026-10-12)

Reviewer role: independent statistician (CV inference, multiple testing) and MIML practitioner, reading as R1/R2/R5/R6 would on resubmission. Everything below was checked against the draft, `experiments/miml_pfn/{PREREGISTERED,AMENDMENT,RESULT}.md`, the 27 named comment files, `experiments/run_foundation_baselines.py` (`splits_for`, the `tr[:v]` inner split, `fit_predict`), `experiments/kdis/run_kdis_baselines.py`, `results/*.json` and `revision_access_44676/evidence/T01__verify_knn_bags_stdout.txt`.

Two numbers I computed from the existing fold vectors, because they frame most of what follows. With the draft's own test (Nadeau-Bengio factor `1/k + n_te/n_tr`, df = k-1, two-sided) applied to the *current* data, before nested selection and before any Holm family larger than one:

| comparison | k | mean dAP | d_z | t_NB | p_NB (raw) |
|---|---|---|---|---|---|
| multiview vs bag-mean, Letter Frost | 5 | +0.081 | 1.85 | 2.75 | 0.051 |
| multiview vs bag-mean, Letter Carroll | 5 | +0.086 | 1.81 | 2.70 | 0.054 |
| multiview vs bag-mean, MSRC v2 | 5 | +0.069 | 3.77 | 5.62 | 0.005 |
| multiview vs best test-selected published, Letter Frost | 5 | +0.074 | 2.62 | 3.91 | 0.017 |
| multiview vs best test-selected published, Letter Carroll | 5 | +0.062 | 2.27 | 3.38 | 0.028 |
| multiview vs best test-selected published, Birdsong (loss) | 10 | -0.056 | -1.27 | -2.77 | 0.022 |

Minimum standardised fold effect `mean(d)/s_d` needed to pass the corrected test at the *first* Holm step with family size m (the step the largest effect must clear):

| k | m = 1 | m = 8 | m = 14 | m = 40 |
|---|---|---|---|---|
| 10 (ratio 1/9) | 1.04 | 1.63 | 1.80 | 2.12 |
| 5 (ratio 1/4) | 1.86 | 3.53 | 4.12 | 5.45 |
| 5x5 repeated (df = 24) | 1.11 | - | 1.74 | - |

So under the draft as written, with a 14-dataset family, a 5-fold dataset needs a Cohen's d_z above 4 to be the first survivor. The three datasets carrying the method's largest effects are all 5-fold. The draft does not say this anywhere. That is the single most important omission.

---

## A. Statistical test and families

**F1. BLOCKER. R1-M04's request for repeated cross-validation is declined without a pre-stated reason, and the corrected test is applied outside the setting it was validated in.**
R1-M04 asks, verbatim, to "rerun the tests with a corrected resampled t-test on repeated cross-validation (for example 10 x 10 or 5 x 2)". The draft's Common protocol says "No new outer partition is drawn for the existing datasets" and applies the Nadeau-Bengio factor to a single k-fold run with df = k-1. That is the Bouckaert and Frank (2004) usage, not Nadeau and Bengio's (2003) own setting (J random train/test resamples). Bouckaert (2003) and Bouckaert and Frank (2004) found that on a *single* 10-fold run the corrected test has acceptable Type I error but poor replicability, which is exactly why they recommend r x k with df = rk-1. R1 will read the draft as having ignored the request. R2-04 and R5-04 list the corrected test as one acceptable option, so they are satisfied; R1-M04 is not.
*Fix.* Split the datasets by whether the partition is canonical. (i) For the `*_10CV.mat` sets, keep the published partition as primary and *state the reason*: it is the partition the published baselines were run on and the one the literature uses, and re-partitioning would cost the same-fold property. (ii) For MSRC v2, Letter Frost and Letter Carroll the seed-42 5-fold split is our own; no comparability argument protects it, and it is where df = 4 bites. Pre-register r x k repeated CV there (5 x 5-fold, seeds fixed in this document, e.g. 43-47), run every arm that enters H1 on it (TabPFN arms are cheap at d = 16-48; KDIS and MIMLNN are lazy learners), and use the Bouckaert-Frank corrected test with df = rk-1 as the confirmatory test on those three datasets. (iii) Add the power table above (or a regenerated one) to the document so that the expected NS verdicts at k = 5 are pre-stated, not discovered.

**F2. MAJOR. The Holm family for H1 is never defined, and the stated hypothesis is global while the decision rule is per-dataset.**
H1 says "MIML-PFN AP > the nested-tuned published library AP" (one hypothesis) and then reports W/L/NS per dataset after Holm. The draft never says what the family is: datasets only? arms (multiview, bag-mean) x datasets? x 5 metrics? x 9 comparators (library + 8 individual methods)? The family size changes the first-step threshold from 1.80 to above 2.1 even at k = 10 (table above). R2-04 explicitly asks what multiplicity Holm is correcting.
*Fix.* State: primary family = {MIML-PFN multiview vs validation-selected library, AP, one test per dataset in the completed set}; secondary families, each Holm-corrected separately and labelled: bag-mean arm vs library (AP); each of the four secondary metrics; each individual method. Add a Demsar-style Wilcoxon signed-rank test across datasets on the dataset-level mean AP differences as *the* test of the global hypothesis as written; the per-dataset tests then answer "where", not "whether". This also gives the paper a result that can be significant when every per-dataset test at k = 5 is not.

**F3. MAJOR. R2-04's request to "explain why the selected statistical test is valid for five- and ten-fold results" is not addressed; several details of the test are unspecified.**
No justification paragraph exists. Unspecified: `s_d` ddof; whether `n_train` in the ratio is the outer training size or the 80 % TabPFN context (F5); the name of the effect size (`mean d / s_d` is d_z; say so, and say it is *not* corrected for fold dependence); what "not significant" licenses. With the 0.006 band retired there is no smallest effect of interest, so an NS result cannot be read as a tie; the manuscript's Reuters and Yeast language depends on this.
*Fix.* Add a short validity paragraph citing Dietterich (1998), Nadeau and Bengio (2003), Bouckaert and Frank (2004): the correction is a heuristic for the training-set overlap, the ratio approximation `rho = n_te/n_tr`, df = k-1 by convention, calibrated Type I error on single k-fold runs but low power and replicability at k = 5. Fix ddof = 1, `n_train` = outer training-fold size, and state that NS means inconclusive. If any equivalence claim is wanted (Reuters, Yeast, Emotions), pre-register a SESOI and a TOST; otherwise commit to never writing "tie" or "no difference".

## B. Nested selection (H1)

**F4. MAJOR. A single 80/20 inner holdout is too small to select among ~90 configurations on the datasets that matter, and the result will be read as handicapping the baselines exactly where the margins are largest (R6-M05).**
Letter Frost: 144 bags, 5-fold, ~115 training bags, so `v = 23` validation bags for 26 labels, several with zero positives in the fold (CLAUDE.md, dataset integrity). Choosing the best of 7 methods x 3 distances x 4 k values (plus MIMLNN's grid) per metric on 23 bags is selection on noise. The nested library will come out well below the test-selected library, and R6 will attribute part of our margin to that. Per-metric selection on an undefined-AP label set is also undefined as written.
*Fix.* (i) Use inner k-fold CV (5-fold) on the outer training fold for the baseline grid; the KDIS methods and MIMLNN are cheap enough that this costs hours, not days. The symmetry argument ("same inner split for everyone") is weaker than selection reliability, and TabPFN has no hyperparameters to select anyway (thresholds only; see F6). (ii) Write the degenerate-label rule for inner scores now (labels with no positive or no negative in the inner validation part are excluded from that fold's selection score, matching the metric conventions promised under R1-m05). (iii) Pre-state a diagnostic: per dataset, report `AP(test-selected library) - AP(nested library)` as a measured upper bound on selection optimism; this turns the stress-test table into a quantity rather than a footnote.
Also note for transparency: with the `tr[:v]` rule, `tr` is the permutation with the test block removed, so for outer folds 2..9 the validation set is *exactly* permutation folds 0 and 1, identical across eight outer folds. It is not a fresh random 20 % per fold. This does not invalidate anything (each outer test fold is untouched by its own selection) but the manuscript must not call it "random inner split", and it is one more reason to move to inner k-fold.

**F5. BLOCKER. Protocol asymmetry inside H1: baselines are refit on the full outer training fold, MIML-PFN is not.**
H1: "The candidate with the best inner-validation score is refit on the full outer training fold." The TabPFN code (`run_foundation_baselines.py` lines 152-157) fits on `fit_i` (80 % of the outer training fold) and predicts the test fold from that same 80 % context; the "one-fit" verification section confirms this is the intended design. So in H1 the library sees 100 % of the training data and MIML-PFN sees 80 %. It is a disadvantage to us, but it is an undeclared asymmetry in a document whose purpose is to fix the protocol, and R5 will find it in the released code.
*Fix.* Decide now and write it: either (a) MIML-PFN also refits on 100 % of the outer training fold for test prediction, thresholds carried over from the 80 % validation fit (standard practice; changes every submitted TabPFN number, so say so and keep the old ones as the "as submitted" column), or (b) stay at 80 % and state it as a deliberate handicap with the size of the context difference per dataset. Either way, state which `n_train` enters the correction factor (F3).

**F6. MAJOR. Thresholding is asymmetric and undocumented (R1-M08 asked directly).**
Ours: per-label thresholds grid-searched on the inner validation set for Hamming loss. KDIS methods: the library's own bipartition. MIMLNN: its own. The Hamming-loss comparison therefore pits a Hamming-tuned threshold against untuned ones. The draft says nothing about how baselines are thresholded.
*Fix.* Document each method's bipartition source; report our Hamming loss at a fixed 0.5 threshold as a sensitivity row; note that the four ranking metrics are threshold-free, so for AP the MIML-PFN arm involves *no selection at all*, which is worth saying explicitly because it is the strongest answer to R2-02 and R5-03.

**F7. MINOR. The "library procedure" answers R1-M08 only if it is named and reported as a procedure.**
Selecting across methods per fold by inner validation is a legitimate single learning procedure (a validation-selected portfolio), and reporting the chosen (method, configuration) per fold plus each method's own nested result, as the draft does, is the right structure. But per-metric selection produces five different comparators, and the manuscript must say "validation-selected library" and never "the best published method". Also pre-state what happens on ties in inner score (first in a fixed order, written here).

**F8. MAJOR. MIMLNN is stochastic and has no seed or repetition policy.**
RESULT.md §6: two Letter Frost runs gave 0.5875 and 0.6004, a spread of 0.013 larger than the submitted Reuters margin (+0.0097) that is *against* MIMLNN. Under nested selection its grid search and its fold values both inherit that noise.
*Fix.* Fix Octave seeds (e.g. 3 seeds, written here), define the fold value as the mean over seeds, report the sd, and apply the same policy to MIMLBagging if it is stochastic.

**F9. MINOR. The LAMDA MIMLNN grid is deferred to a "T03 addendum" that does not exist** (`revision_access_44676/tasks/` is empty). A pre-registration that points to a future document for part of its design is not complete. Put the grid (ratio, lambda values) in this file.

## C. Feasibility and family definition

**F10. BLOCKER. The H1 family is "all datasets on which both arms complete", but no compute budget or stop rule is stated for H1 arms, and the 14-dataset target is not reachable on the measured rates.**
Measured: 401 s per fit at d = 243 (RESULT §7, MPS). Yeast multiview was abandoned at 68 h. Corel5K in our file is 4873 bags x 59 labels x 499 features: bag-mean alone is 1180 fits, ~130 h at the Reuters rate, multiview (2995 features) far more. Medical: ~100 h (R6-M06's own arithmetic). Proteins: ~328 h. The only feasibility rule in the draft (72 GPU-hours, PCA fallback) is written under H3 for R2 only. Without a budget stated for *every* arm before launch, "did not complete" becomes a discretionary exclusion, and the Holm family size becomes a post hoc quantity. R2-07 is precisely about this.
*Fix.* One feasibility section applying to every TabPFN arm in H1-H4: hardware named; the measurement protocol (time the first N fits of fold 0 at full width, extrapolate linearly in fit count, record in the results JSON before continuing); a wall-clock cap per dataset after which the dataset is recorded as not completed; the fallback (PCA) and its fixed budget d' (never specified, not in AMENDMENT either), fitted on the outer training fold only; and the statement that the family is whatever completes under those rules, with the attempted set listed. The reader must be able to see that completion could not have been steered by the result.

**F11. MAJOR. Primary rows for constructed sets require rebuilt-data runs of every arm, including multiview on rebuilt Yeast, Medical and Corel5K.** H1 says the leakage-free rebuilt version is the primary row for Emotions, Yeast, Medical and Corel5K. That is a second full run of every baseline and both TabPFN arms on those datasets, and multiview on Yeast alone cost 68 h without finishing. Reconcile with F10, or pre-state that the primary row for Medical and Corel5K is baselines-plus-bag-mean only.

## D. H2, leakage

**F12. MAJOR. The rebuild design confounds leakage with neighbourhood density, the draft admits it, and the decision rule still phrases the outcome as a leakage claim.**
Test bags built from a pool one-ninth the size have systematically looser neighbourhoods; a drop after rebuilding is expected from density alone. The decision text "the standard folds leak in a way that materially inflates reported scores" is not licensed by the design, and the "at least half of the pairs" threshold is arbitrary.
*Fix, two parts.* (a) Make density symmetric: build every bag within its *own outer fold's* pool (fold f's bags from fold f's centres only, for all ten folds); training set = union of the nine within-fold-built folds. Leakage-free (no source example crosses folds), identical pool size for every bag, one construction per dataset instead of one per outer fold. (b) Add the clean leakage-only contrast on the *original* bags: purged CV, where every training bag sharing any source example with the test fold is removed, versus a size-matched random purge as control. T01 shows 88-97 % of test instances appear in training bags, so the purge will be large; the random-purge control is what separates the leakage effect from the training-set-size effect. Report `AP(random purge) - AP(overlap purge)` per method and dataset with the corrected test. Replace "half of pairs" with per-dataset pooled effect and CI, plus the control contrast.

**F13. MAJOR. R2-03's explicit request to quantify exact instance and neighbourhood overlap is not in the pre-registration's reporting list.**
T01 already measures it (`frac_test_bags_sharing_any_vector` = 1.0 on all four sets; `mean_frac_test_instances_in_train` 0.88-0.97; `frac_test_bags_fully_contained_in_train` 0.41-0.84). None of this appears in H2. Add a descriptive block: per dataset and fold, those four quantities plus neighbourhood-set Jaccard between test bags and their nearest training bag, and the mapping release (R2-03's last sentence; R6-M01 asks for metric and label assignment, which T01 settles: Euclidean on z-scored features, self as first neighbour, label = centre's source label).

**F14. MINOR. Rebuild rule lacks tie and duplicate handling.** T01: Medical has 11 duplicate source rows and 117 bags with within-bag duplicates; Corel5K has a vector with multiplicity 2902 (a hub) and 71 within-bag duplicates; Medical's replay is 99.9 % not 100 % byte-identical. Pre-state the tie-break (stable sort by source index), whether duplicates of the centre may be neighbours, and the fallback if T01's reproduction is below 100 % on a dataset.

**F15. MINOR. Falsification clause is one-sided.** "A significant increase after rebuilding for most pairs would contradict the leakage story" is fine; also pre-state what a *null* under the symmetric design means for the "negative control" framing in the manuscript (R2-03: "would materially affect the interpretation of these datasets as negative controls").

## E. H3, completing the original rule

**F16. MINOR (legitimacy). Evaluating the original rule once Yeast completes is defensible, not a forking path**, because the rule, the threshold and the qualifying set were fixed on 2026-08-14 with Yeast inside it, and this document commits to reporting both (a) and (b) before the run. Keep that. Three additions are needed to make it unattackable: (i) a wall-clock cap for the Yeast run written here (else "ran until it passed"); (ii) the hardware will change from MPS to CUDA; pre-state a cross-device tolerance (the project has MPS vs CPU agreement to 1e-4 AP) and that any dataset whose margin lies within 1e-3 of the 0.006 band is flagged as hardware-sensitive (Birdsong is 2e-6 short of it); (iii) the abstract wording for each (a)/(b) combination, written now.

**F17. MAJOR. The 72 GPU-hour threshold is under-specified and the PCA fallback has no budget.** "GPU-hours" on which GPU; MPS and an A100 differ by 5-10x. "Measured per-fit rate" from how many fits, extrapolated how. If all four proteins trip the rule, R2 is decided on PCA'd arms for four of five datasets, with d' unspecified (AMENDMENT says "fixed-budget PCA" and never fixes the budget). Also fix the order of operations: the protein feasibility decisions and `T10` must be recorded before the Reuters multiview number is looked at, otherwise the held-out set is partly seen when the protocol for the rest is chosen.

## F. H4 and H5

**F18. MAJOR. The native/constructed grouping that the mechanism claim depends on is not pre-defined.** R1-M05 and R6-M03 both ask for a definition and the actual count per side. The draft's H4 has an interpretation rule but no group assignment. Reuters (text segments, 2-26 instances, 4.6 % cross-bag vector sharing), the proteins and our Birdsong file need an a priori label. Write the two lists now, with the criterion (bags present in the source data vs bags constructed by a k-NN procedure over single-instance data, as verified by T01), so the mechanism table cannot be arranged after the fact.

**F19. MINOR. H4's interpretation rule is unstable when the multiview gain is near zero** (Scene +0.011, Birdsong +0.006, Emotions +0.001). `Delta(card) >= 0.5 * Delta(multiview)` with a denominator inside the noise is uninformative. Apply the rule only where the multiview-vs-bag-mean CI excludes zero; otherwise report "no gain to decompose". Also state that on constant-cardinality datasets the `bagmean_card` arm is numerically identical to bag-mean after z-scoring (constant column maps to zero), so it need not be run there.

**F20. MINOR. H5 leaves a decision open and a family undefined.** "A smooth-AP surrogate (or the AP claim is withdrawn)" must be decided now; otherwise the choice can be made after seeing which one looks better. Define the family for the cross-evaluation "significantly worse" rule (4 datasets x 5 training surrogates x 4 other metrics is 80 tests; say how Holm is applied and what the pairing unit is with 3 seeds x k folds). Name the ABMIL training recipe (R1-M08 complained about missing neural training details).

## G. Labelling, record, reporting

**F21. MAJOR. "Committed to git before the first run" is not a public timestamp, and the project is not under git (CLAUDE.md, gap 3).** R2-07 asks for "a permanent, timestamped public record of the original preregistration and amendment"; R6-M07 says internal paths cannot timestamp a plan. *Fix.* Before the first run: deposit this file plus `miml_pfn/PREREGISTERED.md` and `AMENDMENT.md` (with their original dates and the honest note that those two were local files until now) on OSF or Zenodo, or push a public repository, and write the DOI/commit URL into this document's header. Without it the word "pre-registration" should become "analysis plan" in the manuscript, as R6 suggests.

**F22. MINOR. Confirmatory/exploratory labels are mostly right; two adjustments.** H1 is honestly confirmatory in design but it is a re-test, after seeing the test-selected results, of a comparison whose direction is known on 8 of 14 datasets; label it "confirmatory under the new protocol; the direction was known on eight datasets from the submitted analysis" so R2-07 cannot say the 6-2 narrative was re-badged. H2's hypothesis is confirmatory but its decision rule needs F12 before it can be. H3(b) is correctly a completion of a confirmatory test. H4 and H5 as exploratory is right; the verification section is correctly not a hypothesis.

**F23. MINOR. Compute reporting is incomplete for R2-05.** It asks for memory and energy as well as time, and for the trained baselines' cost too. Add peak memory and (where measurable) energy or at least device power x time for TabPFN arms, and wall-clock for every KDIS and LAMDA nested run; the cost table needs both sides. Pre-commit the manuscript wording on `n_estimators = 8` (R6-M06: "single-model on both sides needs qualifying").

**F24. MINOR. Partition facts to state once.** The 5-fold splits drop the remainder bags from every fold (Letter Frost 144 - 5x28 = 4 bags never tested; MSRC v2 and Letter Carroll one each); T01 shows 3/8/7/3 never-tested bags on the 10CV constructed sets. Harmless, but R5 will find it in the code, so say it.

**F25. MINOR. One-fit verification is sound; add a cross-device check.** The 1e-9 rule with fallback to two fits is fine. Since the long arms will move to CUDA, add one explicit cross-device reproduction (Letter Frost and Scene bag-mean, CUDA vs the stored MPS values, tolerance stated) so that submitted and new numbers are known to be comparable, and keep the submitted two-fit numbers untouched.

**F26. MINOR. R2-08's request for one larger natural MIML dataset is not mentioned.** State the decision (declined with reason, or which dataset) so the response letter does not have to invent it later.

---

## What a hostile reviewer (R5) still attacks after the above

1. "Your corrected tests leave nothing significant at k = 5, so the three large wins are now anecdotes." Answer only exists if F1 (repeated CV on the three native 5-fold sets) and F2 (global Wilcoxon) are adopted.
2. "The nested library is weaker than the test-selected one by X; your margin grew by X." Answer only exists if F4's diagnostic and inner k-fold are adopted.
3. "The method sees 80 % of the training data and the baselines 100 %, and you call that a fixed protocol." F5.
4. "Rebuilt test bags are looser by construction; the drop is density, not leakage." F12(b) is the only clean answer.
5. "The pre-registration lives on your laptop." F21.

## Summary of severities

BLOCKER: F1, F5, F10. MAJOR: F2, F3, F4, F6, F8, F11, F12, F13, F17, F18, F21. MINOR: F7, F9, F14, F15, F16, F19, F20, F22, F23, F24, F25, F26.

The document is a serious and mostly well-aimed plan; the labelling discipline, the retention of the failed primary verdict, the retirement of the tie band and the separate arm records are exactly what R1, R2, R3 and R6 asked for. It is not yet a plan that survives R1-M04, R2-04, R2-07, R5-03 and R6-M05 together, because it declines repeated CV without saying why, never states the family or the power, fixes the baselines' protocol while leaving its own at 80 %, and has no feasibility rule for most of the compute it promises.

VERDICT: NOT RESOLVED — 26 findings
