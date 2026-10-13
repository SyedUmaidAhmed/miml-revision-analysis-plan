# PREREG review 10 — pre-deposit addendum (2026-10-13)

Reviewer: independent (statistics / MIML / reproducible-experiment engineering). Did not write the plan, the addendum, the DECISIONS rows or any earlier review.

**Text reviewed.** `experiments/revision_r1/PREREGISTERED.md` in the **working tree**, which is commit `3c720d8` plus one uncommitted edit (§6.3: "The number of non-constant labels is measured on outer fold 0's `fit_i` …" and the matching addendum-table cell). Baseline: tag `prereg-v3-final` = `62a86a6`. `DECISIONS.md` in the working tree is `3c720d8` plus **two uncommitted rows** dated 2026-10-13 ("T03 decisions, part 2", "d′ scope"), i.e. six rows carrying the date, not the four the addendum names.

**Method.** (1) Every "(pre-deposit addendum, 2026-10-13)" insertion in `git diff prereg-v3-final HEAD` was matched to its DECISIONS row and to the lead-decision sections of `tasks/T02-leakfree-rebuild.md`, `T04-mechanism-arms.md` and `T07-tabpfn-config-cost.md`. (2) Every item in the four cited rows was traced into the plan. (3) Counts were recomputed independently from the `.mat` files with the harness's own `get_cv_splits` (counts only; no bag, mask or metric was produced). (4) Cross-section consistency and executability were checked against §1.1–1.9, H2, H4, §5, §6 and the code in `experiments/revision_r1/`.

## Independent recomputation (all match the addendum)

| quantity | addendum | recomputed |
|---|---|---|
| Medical duplicate rows / groups / remainder | 11 of 978; 3 same-feature-different-label groups incl. Corel5K; remainder 8 | 11 rows, 7 groups (2 with differing labels), remainder 8, no group touches the remainder |
| Medical rows dropped per pool 0..9 | 1,1,1,1,2,0,1,3,0,1 | 1,1,1,1,2,0,1,3,0,1 |
| Medical pool sizes after rule B | 96,96,96,96,95,97,96,94,97,96 of 97 | identical |
| Corel5K | 2 of 4873; pools 4 and 5 → 486 of 487; 1 group with differing labels; remainder 3 | identical |
| Emotions / Yeast duplicates | 0 / 0 | 0 / 0 |
| Protein `fit_i` (canonical folds; v = ⌊0.2·|tr|⌋) | "220–307" | azotobacter 294, geobacter 274, haloarcula 220, pyrococcus 307 (all folds equal within a set) |
| Protein d (instance) / multiview width | — | 216 / 1297 |
| d′ for protein multiview, plan text read as "H1 canonical folds" | e.g. `pca219` | 293 / 273 / **219** / 306 |
| smallest `fit_i` on the §1.9 rcv10 folds (`array_split`, every bag used) | — | 293 / 273 / **219** / 306 — equal to the d′ above, so n_components = n_samples on those folds |
| d′ under the uncommitted "d′ scope" row (H1 ∪ rcv10 folds) | "Haloarcula gets pca218" | 292 / 272 / **218** / 305 |
| protein bag-mean (d = 216 ≤ 218) | `native` | no-op confirmed |
| Medical / Corel5K / Yeast / VOC2012 d′ if triggered | 500 | 500 (min `fit_i` 705 / 3509 / 1741 / 8309); purged Medical ≈ 0.8 × 881 × (1 − 0.136) ≈ 609 > 500, so the "d′ scope" assert cannot fire on any realistic trigger |

The evidence file's (row, pool) pairs reproduce exactly with `get_cv_splits` pool numbering. The refit bound in §6.3 is a valid upper bound: within one method the library tie-break (mean → SD → k → distance → ratio → λ) equals the per-method order, so the library's per-metric choice is always that method's per-metric choice, and ≤ 5 refits per method per outer fold follow.

## Findings

**1. (B) Two DECISIONS rows dated 2026-10-13 are not in the plan, and one contradicts it.** `DECISIONS.md` now carries a "d′ scope" row (d′ = min(500, d, min over the folds of the H1 version **and the §1.9 rcv10 version, including its canonical sixth run**, of n_rows(`fit_i`) − 1); same d′ for rebuilt and purged; an assert n_fit − 1 ≥ d′ in every fold that stops the run; "Haloarcula gets pca218 everywhere") and `tabpfn_arms.py::width_plan` implements exactly that. The plan's §6.4 says only "min over that dataset's outer folds", and §1.5 / §6.4 / the addendum table give `pca219` as the example. Under the plan's wording read as H1 folds, the smallest rcv10 `fit_i` on all four protein sets equals d′ (table above): `PCA(svd_solver="full")` accepts n_components = n_samples, but the last component is a null-space direction after centring, which defeats the "− 1", and the code's own assert would stop the run. The two texts therefore disagree on the stored path token (`pca218` vs `pca219`) for every protein unit on the most likely trigger branch. Fix: write the d′-scope definition into §6.4 verbatim (fold set = H1 version ∪ rcv10 folds, computed before any fit; assert and stop), change the example to `pca218`, and update the addendum table and the History row ("four rows" → the actual count).

**2. (B) "T03 decisions, part 2" is not in the plan, and several of its items change selection or scoring.** Missing from the deposited text: (a) inner-mean tie = |Δ| ≤ 1e-12 absolute (§1.3 tie-break currently has no tolerance, so "better inner mean" is float-equality by default); (b) the score written for a constant-negative label: 0.0 for KDIS, −1.0 for MIMLNN (this is what `miml_metrics.py` ranks; §1.3 F4 says only "constant negative"); (c) inner training order = ascending canonical index (affects MIMLNN's k-medoids path); (d) which Letter Frost split the §6.8 checks run on — submitted5 when compared with a stored submitted number, otherwise 5×5 repeat 0 — §6.8 currently says "Letter Frost outer fold 0" with no version, which is not executable as written; (e) the 4× wall guard beside §6.6's CPU limit; (f) emptied purged bags left out of the ARFF id header; MIMLIBLR's use of the bag-id attribute disclosed; (g) complex MIMLNN outputs → real part, flagged above 1e-8 |imag|. Each is a rule an implementer would otherwise choose after seeing data. Encode (a)–(g) in §1.3, §1.5, §6.6 and §6.8 with the addendum marker.

**3. (M) The text under review is not a commit.** `PREREGISTERED.md` and `DECISIONS.md` both differ from HEAD. §1.8 makes the deposited copy a git-committed file, so the round-10 text must be committed before deposit and the header must say which commit was reviewed. Also: the History row stops at review 8 and does not record that review 9 RESOLVED the text at tag `prereg-v3-final` (`62a86a6`); the Version-control row lists commits only through `155e4e2`. Add `62a86a6` (round-9 text, tag) and the addendum commit(s).

**4. (M) Refit failure has no family consequence.** §1.3 records a failed (outer fold, metric) and routes it through §6.7, with no runner-up. §1.6 and §6.6 define what happens when an *arm* "did not complete" (the dataset leaves the family), but not what a single failed (fold, metric) does if the user grants no fix: is the fold dropped (n shrinks), is the (dataset, metric) library row "did not complete", or does the dataset leave F-H1? Any choice made after the failure is post-data. State one now; the §6.6 convention ("the arm did not complete for that metric; the dataset leaves the families needing that arm × metric") is the conservative one.

**5. (m) §1.2 block rule says "every inner split"; H2-A step 5 assigns pools to inner folds by rank mod 5, not by `array_split`.** §1.3 resolves it ("only H2-A rows use the grouped rule"), but §1.2 should say "every ordinary inner split (§1.3)".

**6. (m) Two definitions of a PCA no-op.** §1.5: "no-op (d ≤ 500) carries `native`"; §6.4: "where d′ = d … `native`". Under the new rule these differ whenever min n_fit − 1 < d ≤ 500. Verified equal on all 16 datasets today (closest case: protein bag-mean, d = 216 vs 218), but one definition should stand; use d′ = d.

**7. (m) §6.3 TabPFN bullet keeps the superseded formula.** "Projected device-hours = mean per-label time × labels × …" still precedes the addendum's "mean per-fit time × non-constant labels". H2-A strikes superseded text; do the same here so the deposited bullet has one formula.

**8. (m) H4 draw rules are less exact than H2-B's.** (a) Subsampling: "one generator per (dataset version, fraction, seed) … (each split file's bags for rebuilt versions)" can be read as one stream consumed across the ten rebuilt split files in order; the code (`apply_subsample`) creates a fresh generator per call, i.e. per split file. Say "a fresh `default_rng(seed)` per (version, split file for rebuilt, fraction token)". (b) Neither H4 rule names its call. H2-B names `rng.choice(non_centre_positions, size=m, replace=False)`; H4 should name `rng.choice(n_i, size=m, replace=False)` (positions sorted) and `rng.permutation(n_train)` / `rng.permutation(n_test)` per column, j = d … 6d. `permutation(n)[:m]` would give different units.

**9. (m) Two wording errors that misdescribe the mechanism.** (a) H2-A step 3: "after the drop they are irreducible error, not leakage" — after rule B no duplicate remains in H2-A; the irreducible-error statement is about the original files and H2-B, where both rows stay, and in H2-A only the lowest-indexed row's labels survive (label-agnostic, as stated). (b) §1.3: "'seed s' means `rand('state', s)` set before the call" — `experiments/lamda/seed_shim/clock.m` shows the opposite mechanism: the authors' `MIML_cluster.m` reseeds internally with `rand('state', sum(100*clock))`, which would overwrite any state set before the call; the shim makes that internal call evaluate to `rand('state', s)`. The DECISIONS row carries the same phrasing; T03-e verifies the outcome either way, but the deposited description should be the true one.

**10. (m) Acceptance checks.** (a) H2-B: "must reproduce the table below" has no tolerance; the table is printed to 3 d.p. and 0.1 %. Say "at the table's printed precision". (b) H2-A: the dropped-row counts and pool sizes are now deposited text, and T02 added a check that `construction.json["duplicates"]` lists exactly the dropped rows, but the plan has no H2-A counterpart to the H2-B check ("pool sizes are reported per split" only). One clause: a mismatch with the counts in step 4 stops the construction (correctness only).

**11. (m) Provenance of the addendum.** (a) The addendum table row "T03 / lead correction: refit projection" and the uncommitted §6.3 fold-0 sentence have no DECISIONS row; add one line each so the addendum's stated source ("the four rows … and the task files") is complete. (b) The table points to "T04 decisions 4–5" and to three task files that are not in the §1.8 deposit list; either deposit them or make the pointer "H4 text, above" (the H4 text is self-contained once finding 8 is fixed).

## Notes (not findings)

- §6.7 continuation rule: "independent of the held unit" is not defined. Suggest: dependent = named in §6.0's dependency list, or sharing a comparison with the held unit (H2 pairs, H4 denominators). Budget bookkeeping only; no outcome depends on it.
- `tasks/T04-mechanism-arms.md` A1 still says "d′ per fold" and "token stays `pca500`", superseded by the refinements and d′-scope rows; mark it superseded so it is not read as current. The code already follows the newer rows.
- The authors' `MIMLNN.m` is now on disk (`data/third_party/lamda_mimlnn/extracted/MIMLNN/`); §1.5 asks for its sha256 to be recorded before T03-c.
- `results/revision_r1/` does not exist: no T03, §5, pilot or construction output predates the deposit, as §1.8 requires.
- The uncommitted §6.3 sentence (non-constant label count measured on outer fold 0's `fit_i`, applied to every fold, projections only) is correct as a rule and closes the ambiguity HEAD left ("the number of non-constant labels" in which fold). It is a projection-only convention: for purged and rebuilt versions, other folds may fit one or two labels more or fewer than fold 0, which cannot move a projection across a cap. Its only defects are the bookkeeping ones in findings 3 and 11(a): commit it, and give it a DECISIONS line so the addendum's stated source is complete.

VERDICT: NOT RESOLVED — 11 findings
