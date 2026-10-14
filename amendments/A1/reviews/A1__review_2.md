# A1 review 2: tie-neutral ranking metrics (amendment, guard, wiring)

| | |
|---|---|
| Reviewer | Independent senior referee (multi-label / multi-instance evaluation, ML statistics). Did not write any of the material and is not the round-1 reviewer. |
| Date | 2026-10-13 |
| Inputs | `experiments/revision_r1/AMENDMENT.md` (A1); `git diff 51b6763 3f09faf -- experiments/revision_r1` (`deposit_check.py`, `h2_common.py`, `library_harness.py`, `run_tabpfn_arms.py`, `tabpfn_arms.py`, `tie_neutral_metrics.py`, tests); `PREREGISTERED.md` (deposited, DOI 10.5281/zenodo.23341630 on line 8); `revision_access_44676/reviews/A1__review_1.md`; `revision_access_44676/evidence/T03__checks/diagnosis/tie_neutral_on_letter_frost_f0.txt` and `diagnosis/reproduced/t03b_reproduced.json`; `run_nested_library.py`, `t03_checks.py`, `export_library_design.py`, `h2a_rebuild.py`, `h2b_masks.py` |
| Commit | `3f09faf` (diff against `51b6763`) |
| Scratch | `<scratchpad>/review_A1_r2/` (attack scripts, mutation plugin). Mutants were injected in memory through a pytest plugin (`-p mutplug`); no repository source file was edited. **See the incident note under "What I ran", item 9.** |

## Round-1 findings: status

| # | Round-1 finding | Status | Evidence |
|---|---|---|---|
| 1 | The direction of the defect was misstated | **Fixed** (some wording left, see new F4) | `AMENDMENT.md:32-36` is now per metric. I checked every number against `t03b_reproduced.json` at full precision. RankingLoss: deposited ≥ tie-neutral for all 7 methods. All OneError and Coverage directions are correct. One rounding slip and one omission on AP remain (new F4). The "barely" sentence is replaced by a measured, reported quantity (`:36`). |
| 2 | Incomplete "observed" disclosure | **Fixed** (wording, see new F4) | `:60-66` lists the §6.8 outputs, the three-rule table and §7 Part B, with the protocol differences. Alternatives are at `:55-58`. The overclaiming sentence is gone. |
| 3 | Row (a) was not the deposited pipeline | **Fixed in text**; whether it can be carried out is open (new F3) | `:47` (a) now re-selects with the deposited scorer and refits changed winners. `:49` (c) is the hybrid, labelled as such. `:46` states that both sides are covered, gives the test, p and Holm, and that the rows are descriptive. |
| 4 | Superseded binding text was not named | **Fixed** | `:18-24`. Every cited plan line checked against `PREREGISTERED.md`: 102 (§1.3 library procedure), 115 (F4), 134 (§1.5), 157 (fallback), 418 (H5 theory note), 563 (T03-b) all say what A1 quotes. |
| 5 | No mechanical deposit-before-run guard | **Partly fixed** | `deposit_check.amendment_status` / `deposit_recorded` exist, and today every entry point is closed (see "What I ran", item 3). But the guard fails open for any amendment heading that is not literally `## A<n>` at column 0, and when the file is deleted (new F1). The plan's own §6.7 amendments conflict with it (new F2). |
| 6 | Ambiguous plan references | **Fixed** | H5 at `:22`. Reading note at `:7`. Plan lines 336, 503 and 557 checked. |
| 7 | Edge-case conventions | **Fixed** | `tie_neutral_metrics.py:76` returns −1.0, and `_rows` raises for L < 2. `test_edge_cases_follow_miml_metrics` covers both. The two mutants (Coverage edge → 0.0; no L < 2 check) are each killed by 1 test. |
| 8 | Application details | **Fixed** | `:40` (float64/float32), `:41` (after the F4 overwrite), `:44` (H5 thresholds). |
| 9 | The 1e-6 grouping was unpinned | **Fixed** | `test_mulan_tolerance_and_first_element_grouping`. Neighbour-chaining mutant: 1 failure. `small = 0` mutant: 2 failures. |
| 10 | AP-vs-library assertion dropped | **Fixed** | `tests/test_nested_library.py:271` restored. With Java present the test ran (0 skips in the `.venv` run). |
| 11 | No wiring tests | **Fixed** | (a) `test_unit_stores_tie_neutral_primary_and_prereg_separately`; (b) `test_selection_uses_the_tie_neutral_rule`; (c) `AMENDMENT.md:50-53`. The mutants (`lh.score` → `score_prereg`; TabPFN primary = deposited; TabPFN prereg = tie-neutral) are killed with 2, 1 and 1 failures. |
| 12 | The CLI test could become vacuous | **Fixed** | `tests/test_tabpfn_arms.py:680-687` points `ta.DEVICE_LOG` at a tmp path (`tabpfn_arms.py:1225` resolves the global at call time). The line-8-only CLI mutant is killed. |

## What I ran

| # | What | Result |
|---|---|---|
| 1 | `./.venv/bin/python -m pytest experiments/revision_r1/tests -q` | 323 passed, 8 errors. The 8 errors are the TabPFN tests refusing `.venv`, by design. |
| 2 | `.tabpfn_env/bin/python -m pytest …/test_tabpfn_arms.py …/test_tie_neutral.py …/test_deposit_check.py -q` | 174 passed |
| 3 | Live guard state, real plan and real `AMENDMENT.md` | `deposit_reference()` = (zenodo.23341630, 2026-10-13); `amendment_status()` = `{'A1': None}`; `deposit_recorded()` = False. **All closed:** `lh.guard_dataset("scene", False)`, `lh.guard_write` (real mode), `h2_common.deposit_guard`, `h2_common.guard_real_run("emotions", …)`, CLI `run_nested_library.py --dataset scene`, `t03_checks.py a --dataset letter_frost`, `export_library_design.py --dataset scene`, `h2a_rebuild.py --datasets emotions`, `h2b_masks.py --datasets emotions`, and `run_tabpfn_arms.py --dataset scene` (tabpfn_env). Every one refused before reading data. |
| 4 | Number audit: every figure in `AMENDMENT.md:31-36,48` against both evidence files | All match except kNN AP 0.506 (new F4). Distinct-value counts 2/5/11/115/373/460/613 ✓; Mulan reimplementation within 1.1e-16 ✓. |
| 5 | Plan line audit (8, 102, 115, 134, 157, 336, 418, 503, 557, 563) | All ✓ |
| 6 | Guard attack: 52 synthetic plan + `AMENDMENT.md` pairs (`attack_guard.py`, `attack2.py`) | Closed, correctly: pending, malformed, sandbox, future, same-as-plan DOI, earlier date, duplicate line, duplicate section, `## A10` pending, CRLF pending, CR-only, deposit line before the first section, leading space, bullet, latin-1, UTF-16, directory. **Open, wrongly:** see F1 and F6. |
| 7 | Mutation tests (in-memory, `-p mutplug`) | Killed: `lh_score_prereg` (2), `ta_primary_is_prereg` (1), `ta_prereg_is_neutral` (1), `mulan_neighbour` (1), `mulan_small0` (2), `tn_cov_edge0` (1), `tn_no_L2_check` (1), `dc_ignore_amendments` (13), `dc_no_doi_differs` (1), `dc_no_date_order` (1), `dc_any_line_ok` (1), `dc_unreadable_open` (2), `lh_line8_only` (2), `tabcli_line8_only` (1). **Survived:** `h2_line8_only` (`deposit_guard` ignores amendments): 150 passed, 4 skipped (F7). |
| 8 | `np.argsort` tie order: `.venv` (numpy 2.5.2) vs `.tabpfn_env` (numpy 2.4.6), 6 000 tied rows | Identical on this Mac. Not tested on G (F10). |
| 9 | **Incident.** The mutant `lh_guards_line8_only` replaced `lh.guard_dataset` / `guard_write` in memory with versions that check only line 8. Under it, `test_real_data_refused_before_deposit` (`tests/test_nested_library.py:507-511`) patches `lh.deposit_recorded` (no longer consulted) and calls `rnl.main(["--dataset", "letter_frost"])` with the **default** `--root` and `--workdir`. It therefore **started a real Letter Frost nested-library run**. I killed it after about 40 min. | **This read real data and wrote untracked files:** `results/revision_r1/` (manifest `20261013T141401Z_…_56303_6840d5e2.jsonl`, `library/letter_frost__original__main.json[.lock]`, `predictions/letter_frost/original/*`) and `$TMPDIR/nested_library/letter_frost`, created 19:14:02 to 19:54:09 by pid 56303 (mine). My attempt to delete them was refused by the permission system, so **they are still on disk and must be deleted by the user before any real run.** `run_nested_library.py:280-287` reuses stored unit npz files, so a legitimate run would otherwise pick these up. They are not a valid run: they were produced under a mutated guard while A1 is undeposited. This is my error. It is also the evidence for F8. |

## New findings

**F1. MAJOR: the amendment guard fails open on every heading form except literal `## A<n>`, and when the file is deleted.**
`deposit_check.py:101` `SECTION_RE = r"## (A\d+)\b"` with `.match()` recognises a section only when a line begins exactly `## A<digits>` followed by a word boundary. I took a plan with A1 deposited and added a second, undeposited amendment that has no deposit line. The guard **opens** when that amendment is headed any of: `### A2`, `##A2`, ` ## A2` (one leading space, still a heading in Markdown), `## A2a`, `## Amendment A2: …`, `## a2`, `# A2`, `##\tA2`, `## A２` (fullwidth digit), or `## Budget extension 2026-11-01`. It also opens when a BOM precedes `## A1` on line 1 (`{'A1': pending}` → `{}`), when A1's heading is renamed (`## Amendment 1` → `{}`), when `AMENDMENT.md` is empty, and when it is deleted. Only the exact `## A2 …` control closes it. A close-only guard must not depend on the next author spelling a heading one particular way, and `AMENDMENT.md:5` does not even state the heading grammar.
*Fix:*
- Fail closed on unknown structure. After stripping a BOM, treat every ATX heading of level 1–6 (up to 3 leading spaces) after the title line as an amendment section. Each must match `^## A[1-9][0-9]*(?=[ :(]|$)` exactly; any other heading closes the guard.
- Pin `REQUIRED_SECTIONS = {"A1"}` (grown by each committed amendment), so that deletion, renaming or an empty file closes the guard.
- State the heading grammar in `AMENDMENT.md:5`.
- Add one test for each case above.

**F2. MAJOR: the guard conflicts with the plan's own §6.7 amendments, and A1 does not resolve it.**
`PREREGISTERED.md:243` and `:544` require a budget extension to be "requested from the user through a dated `AMENDMENT.md` in `experiments/revision_r1/`", i.e. this file. `:546` (continuation rule) says that units independent of a held unit **keep running**. Under the new guard, an extension written as `## A2 …` without a Zenodo deposit closes every real-data tool, so the independent units stop, contrary to `:546`. If it is headed any other way, it is invisible (F1). Either the guard silently changes a binding execution rule, or the deposit requirement does not cover extensions. A1 names neither choice, and §6.7 is not in its "Deposited text this amendment supersedes" list.
*Fix:* decide, record it in DECISIONS.md, and state it in `AMENDMENT.md:5`. Either (a) §6.7 budget extensions are a separate, recognised section type (say `## E<n>`) that the guard excludes, since they change no analysis rule, or (b) they need deposit too, in which case add §6.7 `:544-546` to A1's superseded list and say that the continuation rule is suspended until the deposit. Implement the choice in `amendment_status` and test it.

**F3. MAJOR: the row-(a) refits are unbudgeted real-data runs, and H5 storage for the rows is unspecified.**
The stored data do support re-selection. For every candidate and inner fold, the inner npz holds the post-F4 `scores`/`bip`, the raw output and `test_idx` (`run_nested_library.py:312-317`), and Y comes from the split. TabPFN/logreg npz hold `scores`, `y_test`, `thresholds`. No TabPFN step selects on a ranking metric (thresholds are Hamming-only), so `metrics_prereg` and the stored scores suffice there. What is missing:
- (i) Row (a)'s conditional refits are new library runs on real data. They are not in the §6.3 projection (`PREREGISTERED.md:500`: "Only selected candidates are refit"), nor in the §6.7 caps (300 process-hours per unit, 3 000 total). A1 does not say whether they count, whether the stop rule applies to them, or how row (a) is reported if one is held or fails. Under the deposited rule up to 5 more winners per procedure and fold are possible, so the refit term can double.
- (ii) No runner path selects with `score_prereg`. `AMENDMENT.md:80` defers this, which is acceptable only if the deferral is gated (see the fix).
- (iii) H5 measurement (c) (`PREREGISTERED.md:409`) scores the exact metric at **every epoch**. Recomputing the rows "from the stored predictions" (`:46`) therefore needs per-epoch test score matrices, and the unwritten H5 runner is not told to store them.

*Fix:*
- State that the row-(a) refits are charged to the library budget, appear as a separate term in `PROJECTIONS.md`, and fall under the §6.7 stop rule. A held refit is reported as "row (a): selection differs, refit held [h]".
- Require the H5 runner to store per-epoch outer-test score matrices, or exempt H5 (c) from the rows explicitly.
- Make the row-(a) analysis code a C-queue gate (reviewed before the first library unit), not merely "before the first analysis that reports it". Selection-differs bookkeeping is cheap only if it is designed in before the units exist.

**F4. MINOR: number and wording slips in the defect and observed sections.**
- (a) `AMENDMENT.md:34`: MIMLkNN AP tie-neutral is 0.506509, which rounds to **0.507**, not 0.506.
- (b) `:34` lists AP "better on MIMLkNN and MIMLIBLR" and includes MIMLDGC's −1.3e-4 as "marginally" worse. It omits DMIMLkNN and MIMLMAPkNN, which are marginally **better** (+5.4e-5 each). A reader checking for selective reporting will notice. Also state that OneError is unchanged for DMIMLkNN, MIMLMAPkNN and MIMLDGC.
- (c) `:66` "moves the primary RankingLoss rule … toward values close to Mulan's". This is false for MIMLIBLR: deposited 0.3285, Mulan 0.3425, tie-neutral 0.3259, so it moves *away*. Say "for 6 of the 7 methods".
- (d) `:57` rejects Mulan's rule because it "does not apply naturally to non-KDIS methods". Item 4(b) (`:48`) applies `ranking_four_mulan` to every arm, so the reason contradicts the amendment. Keep only the index-dependence reason.

*Fix:* correct the four sentences.

**F5. MINOR: the Holm wording in item 4 is ambiguous, and the confirmatory test is not named.**
`:46`: "the Holm-adjusted p within the same family as the primary row" can be read as pooling the sensitivity p-values into the primary family, which changes m and so the primary verdicts. The §1.6 confirmatory global Wilcoxon (`PREREGISTERED.md:191`, on AP) takes library AP values that A1 changes for tie-heavy candidates, yet it is not named among what each row reports.
*Fix:* "Holm is applied over each sensitivity row's own p-values, family by family, with the same m as the primary family. Primary p-values are never adjusted by them. Each row also reports the §1.6 confirmatory global Wilcoxon."

**F6. MINOR: the deposit-line parsing accepts non-content lines and compares DOIs by case.**
- A section's only `**Deposited:** https://…` line inside a ``` fence or an HTML comment opens the guard (an example line counts as a deposit).
- `https://doi.org/10.5281/ZENODO.23341630` passes the "differs from the plan's DOI" check. DOIs are case-insensitive, so this is the plan DOI.

*Fix:* skip fenced and comment regions when scanning, compare DOIs with `casefold()`, and add tests for both cases.

**F7. MINOR: `h2_common.deposit_guard`'s amendment branch is untested.**
The mutant that drops it (`deposit_guard` checks line 8 only) survives `test_h2.py` and `test_deposit_check.py`: 150 passed, 4 skipped. The four real-data refusal tests do not catch it because their `skipif(_plan_deposited())` uses the same mutated guard, so they skip silently. `test_deposit_guard_follows_the_shared_rule` (`tests/test_h2.py:1060`) varies only line 8.
*Fix:* add a test with a tmp plan carrying the canonical line 8 and an `AMENDMENT.md` with `## A1` / `**Deposited:** pending`, and assert `NotDeposited`. With a valid amendment line, assert that the returned string contains `A1 https://doi.org/…`.

**F8. MINOR: the refusal tests are not fail-safe; a guard regression turns them into real production runs.**
`tests/test_nested_library.py:507-511` calls `rnl.main(["--dataset", "letter_frost"])` with the default `--root` (the project's `results/revision_r1`) and the default `--workdir`. Its only protection is the guard under test. If `guard_dataset` stops consulting `lh.deposit_recorded` (for example by calling `deposit_check` directly, a plausible refactor), the test runs the full real pipeline and writes into `results/`. This happened in this review (item 9). The same pattern appears in `t03_checks.main(["a"])` (`:511`) and `:1292-1299`.
*Fix:* in every refusal test, pass `--root`/`--workdir`/`--evidence-dir` under `tmp_path`, and monkeypatch `rnl.load_version`, `lh.export_split` and `lh.run_kdis_unit` to raise `AssertionError("guard leaked")`. A regression then fails in milliseconds and reads nothing.

**F9. MINOR: the refusal messages are stale now that line 8 is deposited.**
`t03_checks.py:294` ("plan not deposited: real-data checks refused"), `export_library_design.py:72` ("plan not deposited: real-data export refused") and `library_harness.py:150` (`guard_write`: "plan not deposited (§6.0 step 0)") are all printed today because A1 is pending, not because the plan is undeposited. A log reader is misled.
*Fix:* say "plan or an amendment (AMENDMENT.md) not deposited", as `guard_dataset` and `run_tabpfn_arms.py` already do.

**F10. MINOR: the deposited scorer is platform-dependent on ties, and item 5 relies on it across machines.**
`miml_metrics.py:49,80` uses `np.argsort` with the default (unstable, SIMD-dispatched) kind. Tie order can differ between numpy builds and CPUs; x86 AVX2/AVX-512 builds dispatch to vectorised sorts. Item 5 (`:52`) makes the §6.9 cross-device check compare `metrics_prereg` computed on **G** with stored MPS numbers computed on the Mac. Where TabPFN outputs tie (labels held constant under F4), a difference can come from the numpy build rather than the device. I confirmed agreement only for the two Mac environments.
*Fix:* for §6.9 and for rows (a)/(c), recompute both sides with the deposited scorer on one machine from the stored npz, and record the numpy version. Alternatively, also report §6.9 on the tie-neutral metrics, which do not depend on order.

## Assessment of the remaining text (B4)
- `**Deposited:** pending (Zenodo version v1.1 of record 23341630)` (`:13`) is accurate: the guard reads it as undeposited, and it is.
- The Reading note (`:7`) is correct for lines 336/503/557. It should also say that `:243` and `:544` refer to **this** file (see F2).
- The Alternatives section (`:55-58`) is adequate apart from F4(d).
- The Observed section (`:60-66`) is honest and specific. Its one factual error is F4(c).

## Summary
All 12 round-1 findings are addressed. Eleven are fixed and verified: every number and every plan line cited checks out (with the exceptions in F4), and every wiring and Mulan mutant is killed. Finding 5 is only partly fixed. The new amendment guard is closed today at every real-data entry point, but it fails open on any heading spelling other than literal `## A<n>`, on deletion and on a BOM (F1). It also silently overrides the plan's §6.7 continuation rule for budget-extension amendments (F2). Row (a)'s refits are real-data compute that no budget accounts for (F3). The remaining findings are wording, test-coverage and fail-safety issues (F4–F10). Separately, the user must delete the artefacts of the accidental real run described in "What I ran", item 9, before any production run.

VERDICT: NOT RESOLVED — 10 findings
