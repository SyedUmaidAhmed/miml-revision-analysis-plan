# PREREG review 13 — round-12 fixes to the pre-deposit addendum (2026-10-13)

Reviewer: independent (statistics / MIML / reproducible-experiment engineering). Did not write the plan, the addendum, the DECISIONS rows, the code or any earlier review.

**Text reviewed.** `experiments/revision_r1/PREREGISTERED.md` and `revision_access_44676/DECISIONS.md` at commit `b85fc6d` (HEAD; working tree clean apart from the untracked `data/`). Diff base `619f844` (the text review 12 saw). `git diff 619f844 HEAD --stat` touches exactly three files: `PREREGISTERED.md` (+17/−8, 25 lines), `DECISIONS.md` (+1) and the new `reviews/PREREG__review_12.md`. No code changed.

**Method.** (1) Each of review 12's three findings traced to its edit in the diff. (2) The new H2-B acceptance sentence compared clause by clause with `h2_acceptance.H2B_EXPECTED` and `matches_printed`. (3) The new DECISIONS row read in full and compared with the plan text it claims to encode (§1.3, §1.5, §6.4 lines 511–515, H2-A step 7) and with the change-table rows that cite it. (4) Header rows 6–8 and §6.0 step 2 read at HEAD; line-number citations inside `h2_acceptance.py` re-checked against HEAD (275, 287, 292–295 still correct: every edit either replaced a line in place or lies below line 860). (5) The plan-parsing tests re-run.

## Tests (run by this reviewer, HEAD)

```
./.venv/bin/python -m pytest experiments/revision_r1/tests/test_h2.py -q -k "plan or expected or acceptance or mismatch"
5 passed, 30 deselected in 2.69s
```

`test_expected_constants_are_the_plan_lines` still parses the edited H2-B passage; the rewritten acceptance sentence did not move the table.

## Review-12 findings

| # | status | evidence |
|---|---|---|
| 1 H2-B acceptance precision | resolved | H2-B (line 287) now reads "at the printed precision of each column (rows left per surviving bag to 2 decimals, i.e. ±0.005; every other column as printed, to 3 decimals, i.e. ±0.0005; bags emptied as a fraction to 0.1 %, i.e. 3 decimals of the fraction), which is what `h2_acceptance.py` checks". Code: `rows_left` carries `decimals = 2`, every other key `3`, `bags_emptied` stored as a fraction at 3 dp; `matches_printed` accepts `|value − printed| ≤ 0.5·10^−decimals + 1e-12`, i.e. ±0.005 and ±0.0005. The centre bracket is checked as two 3-dp values (min, max), which is "every other column as printed". One reading only. |
| 2 rules without a DECISIONS row | resolved | `DECISIONS.md` gains one orchestrator row dated 2026-10-13, "Review-11 clarifications (row 10 of the addendum source list)", source "PREREG reviews 11–12", with (a) d′ rule only for d > 500, naming Birds, protein bag-mean, MSRC v2 and the Letter sets as staying native; (b) library refit on outer-training bags in ascending canonical index; (c) H2-A test bags in `get_cv_splits` block order. (a) matches §6.4 lines 511–515 (Birds 229, protein bag-mean 216, MSRC v2 289, Letter 97, all `native`) and §1.5; (b) matches §1.3; (c) matches H2-A step 7. The source line now says "ten `DECISIONS.md` rows dated 2026-10-13 that carry implementation decisions" and lists (10) with its three clauses; the History row says "ten rows". Row (10) is cited from four change-table rows: PCA components, d′ scope, refit training order (new row, §1.3) and T02 test-bag order. The DECISIONS file now has 17 rows dated 2026-10-13, of which the last ten are the implementation rows the addendum names. |
| 3 stale provenance | resolved | Version-control row (line 7) now lists `62a86a6` (round 9, tag), `3c720d8` (round 10), `589a980` (round 11), `619f844` (round 12) and says "the round-12 fixes are committed after this edit", which is true of `b85fc6d`. History row (line 6): "round 12 reviewed `619f844` (`PREREG__review_12.md`, 3 findings, addressed in place)"; the phrase "round 12 reviews the next commit" is gone. §6.0 step 2 now says `h2_acceptance.py` "(committed; called by both construction builders)"; `h2a_rebuild.py:371` and `h2b_masks.py:236` call `acc.enforce(acc.check_*)` before writing. |

## Unchanged, as required

- Line 8, Public timestamp: `**PENDING (user action).**` with the §1.8 / §6.0 / F21 wording, byte-identical to `619f844` (it appears only as diff context).
- Line 9, Deposited version: "to be filled at deposit", unchanged.
- The addendum change-table rows other than the four that now cite row (10) are unchanged; the round-11 response table is unchanged (its "names all nine" entry at line 938 describes the round-11 fix as it was made and is a historical record, not a current claim).
- No rule in the plan body changed except the H2-B acceptance sentence; no threshold, seed, family size or decision rule moved.

## Notes (not findings)

- "ten rows dated 2026-10-13" in the History row is shorthand for the source line's precise phrase ("that carry implementation decisions"); the source line disambiguates it. Same construction review 12 accepted for "nine".
- Review 12's notes on `check_h2b` failing on `not_estimable` and on the `inner_folds` docstring stand; neither is deposited text and neither was raised as a finding.

VERDICT: RESOLVED, 100%
