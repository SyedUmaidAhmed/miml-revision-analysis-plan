# PREREG review 12 — round-11 fixes to the pre-deposit addendum (2026-10-13)

Reviewer: independent (statistics / MIML / reproducible-experiment engineering). Did not write the plan, the addendum, the DECISIONS rows, the code or any earlier review.

**Text reviewed.** `experiments/revision_r1/PREREGISTERED.md` at commit `619f844` (HEAD; working tree clean apart from an untracked `data/`). Diff base `589a980` (the text review 11 saw). `revision_access_44676/DECISIONS.md` is unchanged since `589a980`: sixteen rows dated 2026-10-13, of which rows 23–31 are the nine implementation rows the addendum names.

**Method.** (1) Each of review 11's five findings traced to its edit in the plan diff and, for findings 3 and 5, to the code. (2) `h2_acceptance.py` read in full; every hard-coded constant compared by eye with the plan text (H2-A step 4 lists, H2-B table at lines 292–295), and its plan-line citations (274, 275, 282, 287, 292–295) checked against HEAD line numbers. (3) The JSON keys the checker reads (`dropped_rows[].row`, `pool_sizes_after`, `n_dropped_rows_labels_differ`, `vectors_leaving_h2a_lowest_row_in_remainder`, `splits[].overlap_source_rows/overlap_vector_ids`; `folds[].frac_training_rows_removed`, `frac_training_bags_emptied`, `rows_left_per_surviving_bag`, `centre_deleted_rate_surviving_bags`, `centre_deleted_rate_unstratified_uniform_would_give`, `not_estimable`) traced to the writers in `h2a_rebuild.drop_duplicates`/`build_split` and `h2b_masks.fold_stats`/`build_dataset`. (4) Every call site of `split.ids_tr` in `experiments/revision_r1/*.py` enumerated to confirm the refit order. (5) All sixteen 2026-10-13 DECISIONS rows re-traced into the plan. (6) §6.4 widths recomputed (6d + 1: MSRC v2 289, Letter 97, Birds 229, Scene 91). (7) Both test suites run.

## Tests (run by this reviewer, HEAD)

```
./.venv/bin/python -m pytest experiments/revision_r1/tests/test_h2.py experiments/revision_r1/tests/test_nested_library.py -q
66 passed in 78.45s
.tabpfn_env/bin/python -m pytest experiments/revision_r1/tests -q -W ignore::DeprecationWarning
117 passed in 89.40s
```

`test_refit_training_order_ascending` (needs Java and Octave) ran, not skipped: `1 passed, 30 deselected`.

## Review-11 findings

| # | status | evidence |
|---|---|---|
| 1 d′ scope vs table | resolved | §6.4 now states the rule applies to d > 500 only; Birds row annotated "width 229 ≤ 500: `native` regardless"; §1.5 no-op definition "d ≤ 500, or d′ = d for an arm with d > 500". Matches `width_plan` (`d_feat <= PCA_DIM` → `native` before any fold arithmetic). The "Arms with d ≤ 500 are unchanged" bullet is now consistent with the formula. |
| 2 "(or SDs)" | resolved | §1.3: means tied at |Δ| ≤ 1e-12, "Inner SDs are compared exactly". Matches `MEAN_TIE_ABS` / `tie_key` and DECISIONS row 27. |
| 3 acceptance checks in code | resolved | `h2_acceptance.py` holds `H2A_EXPECTED` (Medical dropped 445, 301, 246, 310, 376, 607, 818, 398, 357, 853, 873; Corel5K 2465, 4676; Medical pools 96, 96, 96, 96, 95, 97, 96, 94, 97, 96; Corel5K 487 except pools 4, 5 = 486; Emotions 59 × 10; Yeast 241 × 10) and `H2B_EXPECTED` (the four table rows, bags emptied as a fraction to 3 dp, rows per surviving bag to 2 dp, centre min/max from the bracket). All equal the plan text; `test_expected_constants_are_the_plan_lines` parses the plan and asserts the same. `matches_printed` = half a unit of the last printed digit (+1e-12). `h2a_rebuild.run` and `h2b_masks.run` call `enforce(check_*)` **before** `write_all`, so a mismatch writes nothing (`test_builders_stop_before_writing_on_mismatch`); the CLI re-checks the files (exit 0/1/2). §6.0 step 2 names the script and says it runs before anything reads the constructions. |
| 4 provenance / History | resolved in the History row and the change table (nine rows named; rows (7)–(9) cited). Residue in the Version-control row and §6.0: finding 3 below. | |
| 5 refit training order | resolved | §1.3 sentence added. `library_harness.refit_train_ids` = `np.sort`. Used on every refit path: `Runner.run_split` (ARFF pair `refit` and the refit `unit()` jobs, both `selected` and `all`), `run_pilot` (export and task list; the KDIS pilot unit reads the `refit` ARFF pair, which is sorted), `export_library_design.design` (JSON `refit_train_ids` and the written pair), `t03_checks.check_a_b`, `check_c_e` (three MIMLNN calls). No remaining refit call passes `split.ids_tr` unsorted; the remaining `ids_tr` uses are the inner-permutation draw, counts, and the TabPFN arms (whose §1.3 permutation order is unchanged, as intended). KDIS training-ARFF row order and the MIMLNN row file are asserted ascending by the new test. |

## DECISIONS rows (check 5)

Rows 16–22 (H1 labelling, m = 16 / m = 10 families, budget overruns, [a different manuscript, redacted], no multiview−N_i arm, origin counts, deposit route) and rows 23–31 (the nine implementation rows) are all still encoded where review 11 found them; the diff since `589a980` removes no rule. One divergence from a row's literal text is finding 2.

## Findings

**1. (m) The H2-B acceptance tolerance is glossed as "3 decimals" but one table column is printed to 2.** H2-B: "must reproduce the table below **at the table's printed precision** (3 decimals; 0.1 % for bags emptied)". The "rows left per surviving bag" column is printed to 2 decimals (2.84, 2.88, 2.14, 1.77). `h2_acceptance.H2B_EXPECTED` follows the printed precision (`rows_left` at 2 dp, i.e. ±0.005), which is the right reading of the bold clause, but the parenthetical says ±0.0005. A binding stop condition should have one reading. Fix: "(3 decimals; 2 for rows per surviving bag; 0.1 % for bags emptied)".

**2. (m) Three rules added in rounds 11–12 have no DECISIONS row, and one of them departs from the literal text of a row the plan cites as its source.** The change-table source line says the addendum's rules come from the nine rows (23–31). (a) The d′ scope now excludes arms with d ≤ 500. DECISIONS row 28 reads d′ = min(500, d, min n_fit − 1) with no such exclusion, and the change-table rows "PCA components (as refined)" and "d′ scope" still print the unrestricted formula (for Birds multiview the row gives 184, the plan now gives `native`). The restriction is correct and matches the code, but a reader comparing plan and log finds a different formula. (b) The refit training order (ascending canonical index) is a new binding rule with no row. (c) H2-A step 7's "canonical block order" is one reading of row 24's "test-bag order is canonical"; the choice (lead decision, "option (a)") is recorded only in `tasks/T02-leakfree-rebuild.md`, which the plan says is not needed to read it. Fix: one orchestrator row dated 2026-10-13 ("addendum review 11: d′ rule applies to d > 500 only; library refit order = ascending canonical index; H2-A test bags in `get_cv_splits` block order"), cited from the change table, and the source line updated to ten rows; or, if no row is wanted, the source line should say these three are review-11 clarifications outside the DECISIONS log.

**3. (m) Two stale provenance statements remain in the deposited text.** (a) The Version-control row (line 7) ends at "`3c720d8` the pre-deposit addendum reviewed in round 10; the round-10 fixes are committed after this edit", while the History row (line 6) already names `589a980` as the round-11 text; the row should list `589a980` (round 11) and say the round-11 fixes are committed after this edit (or name `619f844` once the deposit commit is known). (b) §6.0 step 2 says `h2_acceptance.py` is "(being written by T02)"; it is committed at HEAD, called by both builders and covered by seven tests. Delete the parenthetical.

## Notes (not findings)

- `check_h2a` enforces more than step 4's sentence: the differing-label counts (Medical 2, Corel5K 1), an empty remainder-leaving list, and zero row/vector overlap in every split. All are statements of H2-A step 3–4 (verified by review 11 against `evidence/T02__duplicate_pool_check.txt`), so the extra stops are plan-consistent; they are mentioned so nobody is surprised when one fires.
- `check_h2b` fails on `not_estimable = True`, and the builder then writes nothing, whereas the T02 row says not-estimable masks are still written and flagged. For the four real sets this cannot bite: a fold mean above 0.80 would already fail the rows-removed comparison (0.468–0.675). The "still written" rule stays meaningful only for datasets without an expected table.
- The H2-B constants have an independent recomputation on record (`PREREG__review_5.md`, vector-id definition), so the stop is unlikely to fire for a table error.
- `library_harness.inner_folds`' grouped-rule docstring still says "inner training order = outer training order with the inner test bags removed"; the code sorts (plan and test agree). Not deposited text.
- The line numbers cited inside `h2_acceptance.py`'s comments are correct at HEAD; they will drift if lines are inserted above 275 before deposit. The constants are tested against the plan's content, not its line numbers, so nothing breaks.
- `results/revision_r1/` still does not exist; no construction, T03, §5 or pilot output predates the deposit.

VERDICT: NOT RESOLVED — 3 findings
