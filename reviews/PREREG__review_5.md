# Review 5 of `experiments/revision_r1/PREREGISTERED.md` (v3 after the round-4 fixes; git `d2c1103`, 791 lines, working tree clean)

Reviewer role: independent statistician (CV inference, multiple testing, nested selection, compute budgeting on shared hardware) and MIML practitioner; did not write v1–v3, `power_table.py`, or reviews 1–4. Date: 2026-10-13.

Checked against: the file at `d2c1103`; `git diff b72856e d2c1103` (the only files touched since round 4 are this document, `power_table.py`, `evidence/T05__power_table.txt` and `PREREG__review_4.md`); `PREREG__review_1.md` to `_4.md`; `DECISIONS.md` (every row); §1 of each of `comments/R1-M04, R1-M05, R1-M08, R2-02, R2-03, R2-04, R2-07, R2-08, R5-02, R5-03, R5-04, R6-M03, R6-M05, R6-M08.md`; `results/provenance_bag_rows_{emotions,yeast,medical,corel5k}.csv`; the four `.mat` files and their `*_10CV.mat`; `miml_dataset_cv.py::get_cv_splits`; `verify_knn_bags.py` lines 513–550 (how `centre_row` and `member_rows` are written); the `.venv` interpreter.

## What I re-ran

| check | result |
|---|---|
| **H2-B table on vector ids, recomputed independently.** Vector ids built from the stacked centre instances of the `.mat` bags (T01's identity mapping), not from the CSV; every instance position of every bag mapped to its id; CSV cross-check: `member_rows` equal my ids at positions 1–4 for all 4 sets, and `centre_row` is the raw bag index for every bag. Folds from `get_cv_splits` (training = permutation minus the test block, remainder bags included). S_f = ids occurring in any test bag; k per training bag; centre = position 0. | Duplicate source rows **0 / 0 / 11 / 2** (Emotions / Yeast / Medical / Corel5K). Rows removed **0.468 / 0.457 / 0.629 / 0.675**; bags emptied **6.4 / 5.7 / 13.6 / 8.3 %**; rows left per surviving bag **2.84 / 2.88 / 2.14 / 1.77**; centre deleted by the leak purge **0.238 [0.193–0.275] / 0.255 [0.230–0.267] / 0.076 [0.051–0.097] / 0.054 [0.050–0.058]**; unstratified uniform control **0.432 / 0.424 / 0.571 / 0.645**. **Every cell agrees with the document to the printed digit.** Surviving leak-purge training bags containing a test instance vector: **0 in every fold of all four sets**, so the new zero-overlap check passes by construction. |
| Raw-index (round-3) definition, for the sentence under the table | Medical 0.628 / 12.8 % / 0.073 [0.050–0.095], and surviving bags with a test vector per fold **9, 9, 10, 7, 8, 9, 7, 6, 8, 9** (document: "6–10"); Corel5K 2, 1, 1, 1, 0, 1, 1, 1, 2, 1. The sentence is correct. |
| Control feasibility and the 80 % clause | k = 5 implies the centre position is deleted, so k − 1{centre} ≤ 4 always; the stratified draw is well-defined in every bag of every fold. Maximum fraction of training rows removed in any single fold: 0.489 / 0.479 / 0.657 / 0.684, so "not estimable" never triggers. |
| `e = 0.136` | Post-purge training bags / outer training bags, mean over folds: 0.936 / 0.943 / **0.864** / 0.917. e = 1 − 0.864 = 0.136 (Medical, the worst case) is correct and conservative for the other three. |
| §7 C thresholds | Independent formula: f = 0.864 → ρ = 0.1286, d_z,min = t_{0.05/56, 9}·√(0.1 + ρ) = **2.091**; f = 0.691 → ρ = 0.1608, **2.234**. Both match. `power_table.py` imported and Parts A and C regenerated in memory: **byte-identical** to the first 60 lines of `evidence/T05__power_table.txt`. The `|` rows of §7 in the document are byte-identical to the evidence file (diff empty). The round-4→5 diff of the script is the `E_PURGE` constant and its comment only; Parts B and D are untouched and were verified in round 4. |
| Header hashes | sha256 of the three August files match the header byte for byte. Git: `38013d0` = round-3 text, `b72856e` = round-4 text, `d2c1103` = this text; the header's statements are current. |
| Reviewer requirements (§1 of the 14 comment files) | Each sub-request maps to a section that exists and is unchanged since the round where it was verified: nested selection evaluated once per outer fold (§1.3; R2-02, R5-03, R6-M05 item 1), corrected test with CIs and effect sizes and a stated validity argument (§1.6; R1-M04, R2-04, R5-04, R6-M08), repeated CV (§1.2, §1.9), per-fold SDs (§1.6 Reporting; R6-M08 item 2), 0.006 band retired (§1.6), small Reuters/Yeast effects worded by δ_ds (§1.6; R2-04 item 6, R5-04 item 3), cardinality and bag-max arms with a width control and a language ceiling (H4; R1-M05, R5-02, R6-M03), native/constructed defined a priori (§0.2), overlap quantified and bags rebuilt per split with the mapping released (H2, §1.8; R2-03), labels and public deposit (Labels, header, §1.8; R2-07), release list including raw fold-level predictions and a larger natural dataset (§1.5, §1.8, §0.1; R2-08), baseline thresholding and preprocessing stated (§1.3, §1.4; R1-M08, R6-M05), neural recipe (H5; R1-M08 item 6). |

## Part 1 — Round-4 findings: genuinely resolved?

| finding | status | note |
|---|---|---|
| **M1** one global sequence over two devices | **resolved** | §6.0 is now two queues with step 0 = deposit. Dependency graph: C1–C7 depend on nothing in G; C8 (MPS tail) depends on G4 for the multiview PCA decision only; G3/G7 on rebuilt and purged rows depend on C2; G8 depends on C8 (T03-g TabPFN part). **Acyclic.** With G absent, C1–C7 run to completion, and in C8 the T03-g TabPFN part, the §1.9 bag-mean arms and the §1.9 multiview arms on datasets whose multiview width is ≤ 500 (Scene 91, Birds 229; §6.4 "no-op") can run; only §1.9 multiview on Reuters, the proteins and VOC2012 waits. Nothing blocks starting, and the DECISIONS row "all local work first" is met. One residual wording gap at the §6.1 fallback switch (m3 below). |
| **m1** S_f on raw indices | **resolved** | Vector-id identity for centres and members, centre as an instance position, zero-overlap check for the leak arm, table regenerated and reproduced here to every digit, duplicate counts correct, e = 0.136 propagated to §7 C and the script. |
| **m2** §1.9 self-executing gates | resolved | Routed through the stop rule; the "not run" wording now carries "by user decision [date]". Consistent with `DECISIONS.md` 2026-10-13. |
| **m3** heaps vs 24 GiB | resolved | `-Xmx2g` default, `-Xmx8g` for VOC2012 and Corel5K; N = min(8, ⌊16 GiB / Xmx⌋) gives 8 and 2 as stated; N recorded; OOM retry rule; no MPS TabPFN process during a timed C batch. |
| **m4** load-independence | resolved | Claim softened; E-core caveat stated; Octave pinned; load-average > 10 re-time rule. |
| **m5** §1.9 cross-device juxtaposition | resolved | Sixth run on the canonical split on MPS; "on the same device" in the Reported bullet. |
| **m6** environment vs device | resolved | T03-g with the two tolerances, before §6.9; fail → rows labelled by environment. |
| **m7** broken sentence | resolved | Object clause restored. |
| **m8** header/deposit | resolved | Tracked commits named; deposit precedes step 1 of either queue (and §1.8 says so); reviews 1–4 listed; "any later review files are added the same way". |
| **m9** `tr` order on H2-B; storage keys | resolved for `tr`; **storage keys only partly** | `tr` order on H2-B stated. The path now carries version, arm, config and condition, but the condition set is flat and cannot express an H2-B condition and an Octave seed at once (m1 below). |

Genuinely resolved: 9 of 10 fully, 1 (m9) with a residual gap. No fix introduced a statistical change; the only numerical change (e = 0.128 → 0.136) is correct.

## Part 2 — Regressions against rounds 1–3

The diff `b72856e..d2c1103` touches exactly the sections the round-4 response table names (header, §1.3, §1.5, §1.6 global test, §1.8, §1.9, H2-B, §5, §6.0, §6.1, §6.3, §6.8, §6.9, §7 C, response table). I re-read the round-3 fixes in their current form: stratified control (H2-B), seven-step order now per queue (§6.0), timing rules (§6.1–§6.2, §6.6), H4 gate = CI above 0 with the fixed sentence, Fieller beside the delta method and the "both intervals" rule, §1.9 multiview under the gate, Wilcoxon call with `zero_method="wilcox"` and the tie clause, F-H1-newdata name and abstract qualifier, pilot fit count from §5, refit multiplier, T03/T11 "to be created", stop rule replacing the drop order, "Deposited version" row. All present. Round-1/2 items were walked in review 4 and the sections they live in are untouched by this diff. **No regression.**

## Part 3 — Consistency with `DECISIONS.md`

| row | consistent? |
|---|---|
| 2026-10-12 rebuild leak-free, rerun every arm | yes (H2-A; H1/H4 on rebuilt rows; H2-B on purged originals) |
| 2026-10-12 run all missing arms, nothing descoped | yes; the §1.9 gates now go through the stop rule too |
| 2026-10-12 Corel5K through every arm | yes for H1, H2, H4, library, logreg; H5 is a fixed four-dataset metric-alignment analysis, not an arm (note N1) |
| 2026-10-12 GPU arms wait; all local work first | **yes now** (§6.0 C queue starts at the deposit; G queue independent) |
| 2026-10-12 release bundle prepared by Claude, uploaded by user | yes (§1.8 release list; T11) |
| 2026-10-12 no second foundation model | yes |
| 2026-10-12 process: independent reviewer must say RESOLVED, 100 % | this review |
| 2026-10-12 contribution 1 reframed; four sets "constructed by the authors"; no "field's suite" claims | yes (§0.1 table and groups; H2 preamble; no "suite" claim in the plan) |
| 2026-10-12 H1 labelling (orchestrator) | superseded; the plan follows the 2026-10-13 user row |
| 2026-10-13 all CONFIRMATORY, eight "direction previously observed", sensitivity on new data | yes (Labels; §1.6 m = 16 / m = 10; the eight are Scene, Reuters, MSRC v2, Letter Frost, Letter Carroll, Birds, Emotions, Yeast) |
| 2026-10-13 clarification (rebuilt four in both families; leaky originals in no family) | yes |
| 2026-10-13 no unit dropped without a user decision; priority list = execution order only | yes (§1.9, §6.5–§6.7, H3) |
| [row redacted from the public copy: a decision about a different manuscript, outside the scope of this plan] | — |

## Part 4 — Findings

No MAJOR finding. Three MINOR findings, each a text fix; none requires a new analysis or changes a number.

**m1. §1.5's `<condition>` key cannot express an H2-B condition and an MIMLNN Octave seed at the same time, so the no-overwrite rule refuses the second seed of every H2-B MIMLNN unit.**
The path is `<dataset>/<version>/<arm>/<config>/<condition>/r<repeat>_f<fold>[_i<inner>].npz` with `<condition>` drawn from one flat set {main, leak, control-s0..2, padded-s0..2, sub-…, seed-s0..s4}. MIMLNN is an H2 method ("MIMLNN (nested)") and runs with Octave seeds {0..4} per configuration (§1.3), under the H2-B conditions leak and control-s0..2. A unit such as (purged, MIMLNN, ratio 0.4 λ 1, control-s1, Octave seed 3) has no path: choosing `control-s1` makes the five seeds collide, choosing `seed-s3` makes leak and the three controls collide. Because "a writer refuses to overwrite an existing file", the run stops at the second seed rather than silently losing data, but it stops. The same ambiguity applies to the H5 models (seed {0, 1, 2} × five surrogates), whose key is not enumerated at all although §1.5 covers "every method".
*Fix.* Make `<condition>` a `+`-joined list of the applicable tokens in a fixed order, e.g. `control-s1+seed-s3`, `leak+seed-s0`, `main+seed-s2`; and state the H5 key: `<arm>` = model (bagmean_mlp, abmil_ml), `<config>` = training surrogate, `<condition>` = `seed-s<k>`.

**m2. The deposit step is self-referential as written: the deposited file cannot contain its own commit hash and sha256.**
Header: "Deposited version: to be filled at deposit: git commit hash and sha256 of this file as deposited". §1.8: "its commit hash and sha256 are written into the header ... at deposit, before the URL/DOI". Writing either value into the file changes both values. A doer either deposits a copy whose header reads "to be filled" (then the header of the later file names a hash that does not match the file a reader downloads from the archive) or edits before depositing (then the recorded hash is wrong). A reviewer who checks the sha256 in the header against the deposited file will find a mismatch either way unless the text says which copy is which.
*Fix.* One sentence in §1.8 and the header row: "The deposited copy carries 'to be filled' in this row. After deposit, one follow-up commit writes the deposited copy's commit hash, its sha256 and the archive URL/DOI here; the archive's own checksum of the deposited copy is the binding one." (The URL/DOI is already a post-deposit edit, so this adds no new edit, only names it.)

**m3. §6.1's device table and fallback clause are out of step with the new C-queue tail.**
(i) Row 1 assigns "every TabPFN fit in this revision ... except §1.9" to G, while row 3 of the same table and §6.0 C-queue step 8 put T03-g's TabPFN part on MPS: an internal contradiction in the device assignment. (ii) The fallback switch must be recorded "before any TabPFN revision fit". Under §6.0 the C tail (T03-g's TabPFN part, the §1.9 bag-mean arms, and §1.9 multiview on Scene and Birds) can legitimately run on MPS before the credits arrive, after which the switch's precondition can no longer be met by the letter, although the switch is exactly what is needed if the credits never come. (iii) Under the fallback, the "no MPS TabPFN process during a timed C batch" rule makes the two queues strictly serial on one machine (1 500 MPS device-hours plus the C work); the plan calls them independent and does not say which goes first in that case.
*Fix.* Row 1: "except §1.9 and T03-g's TabPFN part". Fallback: "recorded before the first G-queue fit (G-queue step 2)"; C-tail MPS fits made before that do not bar the switch, and are kept (they are MPS results compared only with MPS results). Add: "Under the fallback the two queues share the machine and run serially, C queue first (DECISIONS.md 2026-10-12)".

### Notes (no action required)

- **N1.** H5 does not include Corel5K; it is a metric-alignment analysis on a dataset set fixed before this revision (Scene, Birds, MSRC v2, Letter Frost), not an arm, so it does not conflict with "Corel5K goes through every arm". Review 4 suggested saying so in one clause; it was not added. Harmless.
- **N2.** Budget forecast, not a defect: 16 H1 library rows at up to 300 process-hours each, plus the H2-B library arms and the §1.9 library arm, exceed the 3 000 process-hour library total on paper, so the stop rule of §6.7 will almost certainly fire at least once and produce an AMENDMENT. The plan is designed for that; the user should expect it.
- **N3.** §1.9's "planned within 72 MPS-hours per dataset" does not say whether the sixth (canonical) run is inside that figure. Either reading is executable because an overrun goes through the stop rule; the AMENDMENT, if any, simply comes 20 % earlier or later.
- **N4.** The new H2-B zero-overlap check is a tautology under vector ids (the purge deletes every row whose id occurs in a test bag). It is still worth keeping as a guard against an implementation that computes ids differently from the released masks.

## Part 5 — Executability sweep

With this file alone a doer can run, without any judgement after seeing data: the deposit (once m2 is clarified), T03 a–g, the H2-A rebuild and the H2-B masks (both definitions now verified to be leakage-free in every fold), the C pilots and caps, every C run in §6.7 order, and, on G when it exists, §5, the G pilots, the §6.4 trigger, every G run, and §6.9. The two queues are acyclic and the C queue is complete without G. The statistics of §1.6, §1.9, H2, H4 and H5 are fully specified (test, families, n₁/n₂ rule, Holm, global Wilcoxon with HL and rank-biserial, pre-worded outcomes, practical-threshold wording). The only step that stops is the second Octave seed of an H2-B MIMLNN unit (m1), and the only wording that a reviewer can catch as contradictory is the §6.1 table/fallback pair (m3) and the self-hash (m2). None of the three can change a result; all three are one- or two-sentence edits.

## Part 6 — Would R1, R2, R5 and R6 accept this plan?

Yes on every requirement listed in the task (R1-M04/M05/M08, R2-02/03/04/07/08, R5-02/03/04, R6-M03/M05/M08), as mapped in the table above; nothing in the round-4 fixes weakened any of them, and R2-03's leakage measurement is now defined on vector ids and reproduces from the released mapping on every fold.

## Summary

The round-4 fixes are real: the queues are acyclic and executable with the GPU absent, the H2-B table on vector ids reproduces to every digit from the `.mat` files and canonical folds, the raw-index overlap sentence is exact, e = 0.136 is correct and propagated, §7 Parts A and C regenerate byte-identical to the evidence file, no earlier fix regressed, and every `DECISIONS.md` row is honoured. Three minor text gaps remain: a storage-key collision for H2-B MIMLNN seeds, a self-referential deposit hash, and a device-table/fallback wording that lags the two-queue design. Fix those and this is ready to deposit.

MAJOR: none. MINOR: m1–m3.

VERDICT: NOT RESOLVED — 3 findings
