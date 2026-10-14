# A1 review 3: tie-neutral ranking metrics (amendment, guard, fail-safe, quarantine)

| | |
|---|---|
| Reviewer | Independent senior referee (multi-label / multi-instance evaluation, ML statistics, research-software rigour). Did not write any of the material and is not the round-1 or round-2 reviewer. |
| Date | 2026-10-13 |
| Inputs | `experiments/revision_r1/AMENDMENT.md` (A1); `git diff 3f09faf d3b6b73 -- experiments/revision_r1 revision_access_44676/DECISIONS.md .gitignore quarantine`; `deposit_check.py`, `h2_common.py`, `library_harness.py`, `t03_checks.py`, `export_library_design.py`, `tabpfn_arms.py`, `run_nested_library.py`; `tests/conftest.py`, `tests/test_failsafe.py`, `tests/test_deposit_check.py`, `tests/test_h2.py`, `tests/test_nested_library.py`; `PREREGISTERED.md` (deposited, DOI 10.5281/zenodo.23341630 on line 8); `reviews/A1__review_1.md`, `reviews/A1__review_2.md`; `evidence/T03__checks/diagnosis/tie_neutral_on_letter_frost_f0.txt` and `diagnosis/reproduced/t03b_reproduced.json`; `quarantine/2026-10-13_accidental_letter_frost_run/README.md` and `MANIFEST.sha256` (no other quarantine file was opened) |
| Commit | `d3b6b73` (diff against `3f09faf`) |
| Scratch | `<scratchpad>/review_A1_r3/` (attack script, mutation plugins, fail-safe probes). No repository file was edited except this report. No real-data entry point was called outside pytest. Every guard-disabling probe ran inside pytest with `conftest._no_real_data` loaded (`-p conftest`), and each probe first asserted that `scipy.io.loadmat` was wrapped. Mutants of `deposit_check` / `h2_common` were applied in memory and run only against `test_deposit_check.py` and the single test `test_h2.py::test_deposit_guard_requires_every_amendment`. No fail-safe mutant was run against a test that could reach real data. |

## Round-2 findings: status

| # | Round-2 finding | Status | Evidence |
|---|---|---|---|
| F1 | Guard fails open unless the heading is literally `## A<n>`; also on BOM, rename, empty file, deletion | **Fixed** for every case listed (other residual fail-open forms are new F1/F2 below) | `deposit_check.py:120-218`. `test_unknown_heading_closes` covers all 13 forms from round 2. BOM: `test_unsafe_structure_closes`. Rename, empty, missing: `test_required_sections`. Mutant `unknown_heading_ok` is killed by 13 tests, `missing_file_open` by 1. On a copy of the real `AMENDMENT.md` with `required={"A1"}`: closed as committed (`{'A1': None}`), and closed again when `## A2` pending is appended. |
| F2 | Guard conflicts with §6.7 budget extensions (plan :243, :544, :546) | **Fixed** (scope gap at plan :525, see new F5) | `## E<n>` sections are exempt (`deposit_check.py:116-120,200`), `AMENDMENT.md:7`, DECISIONS.md last row. Test `test_budget_extension_sections_are_exempt`; mutants `E_needs_deposit` and `deposit_in_E_ok` are each killed by 1 test. Judgement below. |
| F3 | Row-(a) refits unbudgeted; H5 per-epoch storage; gate timing | **Fixed in text** (scheduling and tracking left open, see new F6) | `AMENDMENT.md:51-53`. The bound "5 largest measured candidate refit times per method" is a valid upper bound: only 4 ranking metrics can change selection, and Hamming selection is unchanged by A1. The H5 (c) line is 410 ✓. |
| F4 | Number and wording slips | **Fixed** | All checked at full precision against `t03b_reproduced.json`. kNN AP 0.506509 → 0.507 ✓. DMIMLkNN/MAPkNN AP +5.452e-5 → "+5.5e-5" ✓. DGC −1.34e-4 ✓. OneError unchanged for DMIMLkNN/MAPkNN/DGC ✓. RankingLoss moves toward Mulan's value for 6/7 methods, MIMLIBLR 0.3285/0.3425/0.3259 ✓. The Mulan reason is removed from the Alternatives ✓. |
| F5 | Holm wording; confirmatory test not named | **Fixed** | `AMENDMENT.md:49`: Holm is applied per sensitivity row, with the same m as the primary family; primary p-values are never adjusted by it; the §1.6 global Wilcoxon is named at plan line 191 ✓. |
| F6 | Deposit lines in fences or comments count; DOI compared by case | **Fixed** (a residual fence-parsing divergence is new F2) | `_amendment_lines` strips comments and fences, `deposit_recorded` uses `casefold()`. Mutants `no_comment_strip`, `no_casefold` and `unclosed_fence_ok` are each killed by 1 test. |
| F7 | `h2_common.deposit_guard` amendment branch untested | **Fixed** | `test_deposit_guard_requires_every_amendment`. The mutant (`deposit_guard` checks line 8 only, applied after collection) is killed. If it is applied before collection, `test_h2.py` fails to import. |
| F8 | Refusal tests not fail-safe | **Partly fixed** | The refusal tests at `test_nested_library.py:507-516` now use `tmp_path`, and `conftest._no_real_data` blocks `loadmat` under four roots. My probes, with every guard disabled, show that `rnl.main` and `t03_checks.main(["a"])` write nothing (t03 creates only the empty `ev/` dir) before `RealDataRead`. But the fail-safe's scope is narrower than `AMENDMENT.md:73,88` claim, and `test_nested_library.py:1061-1064` still uses default paths (new F3). |
| F9 | Stale refusal messages | **Fixed** | `t03_checks.py:294`, `export_library_design.py:72`, `library_harness.py:150`. Grep finds no remaining "plan not deposited" message. |
| F10 | Deposited scorer is platform-dependent on ties | **Fixed** | `AMENDMENT.md:59`: one machine, from the stored npz, numpy version recorded; §6.9 is also reported tie-neutral. |

## What I ran

| # | What | Result |
|---|---|---|
| 1 | `./.venv/bin/python -m pytest experiments/revision_r1/tests -q` | 355 passed, 8 errors (the 8 TabPFN tests refuse `.venv`, by design) |
| 2 | `.tabpfn_env/bin/python -m pytest …/test_tabpfn_arms.py …/test_tie_neutral.py …/test_deposit_check.py …/test_failsafe.py -q` | 205 passed |
| 3 | Plan-line audit: 8, 102, 115, 134, 157, 191, 243, 336, 410, 418, 500, 503, 525, 544, 546, 547-557, 563 | Every line cited in A1 says what A1 says it does. Line 525 also routes approvals to "a dated AMENDMENT", and A1 does not mention it (F5). |
| 4 | Number audit: every figure in `AMENDMENT.md:34-37,54,74` against `t03b_reproduced.json` (full precision) and the evidence `.txt` | All correct, including the 7 distinct-value counts and the ≤ 1.1e-16 Mulan reimplementation bound |
| 5 | Guard attack (`attack3.py`): synthetic plan with line 8 deposited, valid A1, plus one hostile addition | **Opens, wrongly:** A2 reusing A1's deposit line; A2 deposit dated before A2's own heading date; `> ## A2` (blockquote); `- ## A2` and `1. ## A2` (list items); `<h2>A2</h2>`; an A2 heading between two 4-space- or tab-indented "fences" (which Markdown renders as code lines, not fences); an A2 heading between a code span `` `<!--` `` and a later `` `-->` ``; an example deposit line inside a ```` ```` ```` fence that contains a ```` ``` ```` line; an example deposit line inside `<pre>`; rule text in an `## E1` (F1, F2, F5). **Real file:** a copy of the real `AMENDMENT.md` with A1's line replaced by `**Deposited:** https://doi.org/10.5281/zenodo.23341631 (2026-10-13)` **opens** with `required={"A1"}`, and still opens with an `## E1` appended and with CRLF line endings. It does not fail closed on valid input. |
| 6 | `deposit_check` mutants (in memory, 17) against `test_deposit_check.py` + the h2 test | Killed: `no_required`(1), `no_setext`(2), `unknown_heading_ok`(13), `deposit_in_E_ok`(1), `no_casefold`(1), `no_comment_strip`(1), `unclosed_fence_ok`(1), `dup_ok`(1), `missing_file_open`(1), `no_date_order`(1), `E_needs_deposit`(1), `bom_kept`(1). **Survived:** `required_never_default` (REQUIRED_SECTIONS never applied to the real plan), `unclosed_comment_ok`, `fence_any_char_closes`, `cr_not_normalised`, `title_after_section_ok` (F4). |
| 7 | Fail-safe probes (pytest, `-p conftest`, fail-safe asserted active) | With `ta.set_data_dir(<dir>)` (the `--data-dir` / `MIML_DATA_DIR` route), `loadmat` of `<dir>/scene.mat` is allowed (`_is_real` False). `results/revision_r1/constructions/…npz` and `…/predictions/…npz` are not covered, and `numpy.load` is not wrapped. Fail-safe mutant (restore the original `loadmat` in `miml_dataset_dd`, `flat_knn_dataset`, `h2_common`) run only on `test_failsafe.py::test_loadmat_on_real_data_raises`: **survives** (F3). |
| 8 | Quarantine: `shasum -a 256 -c MANIFEST.sha256` from inside the folder | 2 639 / 2 639 OK, 0 failures. The manifest's path set equals the file set on disk (`find -type f`), with no symlinks. `git check-ignore` confirms that both trees are ignored, and `git log --all` shows that no quarantined file was ever committed. `results/revision_r1/` and `$TMPDIR/nested_library` no longer exist. No data file was opened. |

## Judgement on the E<n> decision (DECISIONS.md last row)
It is sound. Plan :544 names this file as the place where an extension is *requested*. Plan :546 keeps independent units running during a hold. The decision to drop or reduce a unit stays a user decision in DECISIONS.md (:546). A budget-extension request changes no analysis rule, so requiring a Zenodo deposit for it would have suspended :546, a binding execution rule, without saying so. Exempting `## E<n>` keeps the deposited §6.7 text in force, and it is recorded as a method decision. Two gaps remain, and both are in F5: plan :525 also sends cap approvals, **including the pre-fixed VOC2012 reduced grid**, to "a dated AMENDMENT"; and the exemption has no written content limit.

## Judgement on the accident disclosure and quarantine
The disclosure (`AMENDMENT.md:73`, DECISIONS row, README) is accurate and specific. I checked the times (manifest stem `20261013T141401Z`, 14:14–14:54 UTC), the file count (2 639), the cause (an in-memory guard mutant and a default-root refusal test), the user's decision and the no-use rule. The manifest verifies, and nothing quarantined is tracked or was ever committed. One sentence overclaims (F3): "The test suite now blocks any real-data read".

## New findings

**F1. MAJOR: an amendment's deposit line is not bound to that amendment, so copying A1's line into a new A2 opens the guard.**
`deposit_check.py:209-235` checks each A section's line only against the plan: valid grammar, a DOI different from the plan's, and a date no earlier than the plan's. Nothing ties the line to its own amendment. In attack 5, `## A2 (2026-11-01): new rule` carrying a verbatim copy of A1's `**Deposited:** https://doi.org/10.5281/zenodo.17345699 (2026-10-13)` gives `deposit_recorded() = True`. So does an A2 whose deposit is dated before its own heading date. The most likely way to write A2 is to copy the A1 section as a template, which makes this the most likely fail-open in practice. `AMENDMENT.md:5` already states the rule that would prevent it ("as a new version of the same Zenodo record **with its own DOI**"), but the code does not enforce it. This is the same class of defect as round-2 F1: the guard depends on the next author's care.
*Fix:*
- Require pairwise-distinct DOIs (casefolded) across all A sections. Any repeat closes the guard.
- Make the heading date mandatory (`## A<n> (YYYY-MM-DD)…`). Close the guard when a section's deposit date is earlier than its heading date.
- State both rules in `AMENDMENT.md:6`, and add a test for each (copied line; deposit dated before the heading; a heading without a date).

**F2. MINOR: other Markdown forms still fail open, and `AMENDMENT.md:8` overstates the coverage.**
`HEADING_LIKE_RE = r"[ \t]*#"` (`deposit_check.py:122`) recognises only headings that begin a line. `FENCE_RE` (`:124`) treats any indented ```` ``` ```` or `~~~` as a fence, and closes a fence on any run of the same character. Attack 5 opens the guard on each of these:
- an undeposited A2 headed `> ## A2` (blockquote), `- ## A2` or `1. ## A2` (list item), or `<h2>A2</h2>`, all of which render as headings;
- an `## A2` heading placed between two 4-space- or tab-indented ```` ``` ````/`~~~` lines (Markdown renders these as indented code, not fences, so the heading is visible; the guard hides it);
- an `## A2` heading between a code span `` `<!--` `` on one line and `` `-->` `` on a later line (`:152` strips across the gap);
- an example deposit line inside a 4-backtick fence that contains a 3-backtick line, or inside `<pre>`, which counts as A2's deposit.

`AMENDMENT.md:8` says that "another heading form after the title" closes the guard. That is not true of these forms.
*Fix:*
- Close the guard on any line whose first non-container content (after stripping up to 3 spaces and any run of `>`, `-`, `*`, `+` or `\d+[.)]` markers) starts with `#`.
- Close it on any `<h[1-6]` or `<pre` tag.
- Treat a fence as open only with at most 3 leading spaces (no tab), and close it only with a run of the same character of at least the opening length.
- Run the comment strip after removing fenced blocks and code spans, or simply close the guard on any `<!--` or `-->` outside a fence.
- Add the attack strings above as tests, and reword `:8` to say what is actually covered.

**F3. MAJOR: the suite-wide fail-safe is narrower than A1 claims, and it has a hole on the GPU machine.**
`AMENDMENT.md:73` ("The test suite now blocks any real-data read") and `:88` ("no test can read real data") are public, to-be-deposited claims. `conftest._no_real_data` (`tests/conftest.py:38-78`) wraps only `loadmat`, in five named modules, for four fixed path roots. Gaps:
- (a) **Configured data directory.** `tabpfn_arms.data_path` reads by basename from `MIML_DATA_DIR` or `--data-dir` (`tabpfn_arms.py:65-76`, `run_tabpfn_arms.py:102,118`). This is the portability route for G, where the TabPFN tests run. `REAL_DATA_ROOTS` ignores it. Probe 7: `loadmat` of `<data-dir>/scene.mat` passes. Any copy of the data outside `../VIT_MIL/Code/MIML-SELFVIT` (on G, a backup, `~/Downloads`) is unprotected.
- (b) **Stored real outputs.** `numpy.load` and `open` are not wrapped, and `results/revision_r1/` is not a root. Once T02/C-queue production exists, these become real-data reads that nothing blocks: `load_rebuilt`/`load_purged`/`dataset_train_sizes` (`tabpfn_arms.py:328,370,715`, default `CONSTRUCTIONS_ROOT`), the stored-unit reuse in `run_nested_library.py:283`, and `h2a_rebuild.py:328`/`h2b_masks.py:185`.
- (c) **Fragility.** `_is_real` lets every file object through (`conftest.py:55-56`: "synthetic by construction" is an assumption, not a check). A module that fails to import is skipped silently (`:66-67`). `scipy.io.matlab.loadmat`, or any new module's own `from scipy.io import loadmat`, is not covered.
- (d) **The fail-safe's own test checks 2 of its 5 wrappers.** `test_loadmat_on_real_data_raises` checks `scipy.io` and `miml_dataset_cv` only. The mutant that leaves `miml_dataset_dd`, `flat_knn_dataset` and `h2_common` unwrapped survives it. That mutant would be caught only by `test_accident_scenario_*` **after** real Letter Frost (DD format) data had been read into memory, i.e. by repeating the accident.
- (e) **Writes are not covered.** `test_nested_library.py:1061-1064` still calls `t03_checks.main(["a"])` and `eld.main(...)` with default `--evidence-dir`/`--workdir`/`/tmp` paths. That is harmless today (probe: only `makedirs` of the existing evidence dir before the first read), but it is the letter of round-2 F8's fix. `test_failsafe.py`'s docstring promises "write nothing" but asserts only that no `.npz` exists.

*Fix:*
- Replace the per-module wrap with one `sys.addaudithook` installed in `conftest.py` (gated by a flag that the autouse fixture sets). Refuse the `open` event for any realpath under: the four roots, `results/revision_r1/`, `quarantine/`, `os.environ.get("MIML_DATA_DIR")` and `tabpfn_arms._DATA_DIR_OVERRIDE["dir"]`. Refuse a `subprocess.Popen` event whose argv names any of them. This covers `np.load`, `open`, every `loadmat` import path and file objects.
- In the autouse fixture, `monkeypatch.delenv("MIML_DATA_DIR")` and reset `ta.set_data_dir(None)`.
- Make a missing `LOADMAT_MODULES` entry fail rather than `continue`.
- Add a test that asserts, without any read, that every listed module's `loadmat` carries `_no_real_data`, and that a path under each root (including a set data dir and `results/revision_r1`) is refused.
- Give `test_nested_library.py:1061-1064` tmp paths, and make `test_failsafe` assert that `tmp_path` holds no files at all.
- Until then, reword `AMENDMENT.md:73,88` to say "blocks `.mat` reads from the project's data directories".

**F4. MINOR: four surviving `deposit_check` mutants, one of them on the wiring that round-2 F1 required.**
- `required_never_default`: `amendment_status` never applies `REQUIRED_SECTIONS` to the real plan (`deposit_check.py:178-179`). This mutant passes the whole file. `test_real_plan_requires_a1` checks only that the constant contains "A1". Under this mutant, deleting or renaming A1 in the real `AMENDMENT.md` opens every real-data tool, and no test fails.
- `unclosed_comment_ok`: the test case `<!-- unclosed comment\n## A2 x` is closed by the A2 heading anyway, so it does not isolate the check.
- `fence_any_char_closes` and `cr_not_normalised`: no test covers ```` ``` ```` closing a `~~~` fence, or CR-only/CRLF amendment files.
- `title_after_section_ok`: harmless today; noted only.

*Fix:* monkeypatch `dc.PLAN` to a tmp plan and assert that `deposit_recorded(p)` (default `required`) is False when `AMENDMENT.md` is missing, empty, or has A1 renamed. Add a lone `<!--` case with nothing else after it, a `~~~` fence containing a ```` ``` ```` line and a hidden `## A2`, and CR-only and CRLF variants of a pending A1 and a pending A2.

**F5. MINOR: the E-section rule does not cover plan line 525, and E sections have no content limit.**
Plan :525 (§6.5) lets the user "approve the extra hours **or the VOC2012 reduced grid** for that dataset version, by a dated AMENDMENT". This is a third route into this file. The reduced grid is pre-fixed at :524, so choosing it executes a pre-registered contingency and changes no rule. That makes it an E, but `AMENDMENT.md:7`, the Reading note (`:10`) and the DECISIONS row define E only as "§6.7 budget extensions" (243, 544). An approval under :525 therefore has no defined section type: as an A it would need a deposit and halt all real work, contrary to :546. Also, `## E1 … also RankingLoss now uses Mulan` opens the guard (attack 5), because the exemption rests on `:7`'s descriptive "They change no analysis rule". That is not a stated prohibition. Finally, the plan says "dated", but the E heading grammar does not require a date.
*Fix:*
- Extend E to "§6.5/§6.7 cap and budget decisions (plan :243, :525, :544), including selecting a pre-registered option such as the VOC2012 reduced grid of :524". Update `:10` and the DECISIONS row to match.
- State that an E section may contain only the unit, its projection, the hours used, the requested hours or pre-registered option, and the DECISIONS.md reference; anything else is an A and needs a deposit.
- Require `## E<n> (YYYY-MM-DD)`.

**F6. MINOR: the row-(a) refits can crowd out primary units, and the row-(a) gates exist only in prose.**
`AMENDMENT.md:51` charges the refits to the 3 000-h library budget under the stop rule, but does not schedule them. If they run interleaved with primary units, a descriptive sensitivity row can exhaust the budget and **hold a primary unit** (:541-546). The gate at `:53` (row-(a) code reviewed before the first library unit) and the H5 per-epoch storage requirement at `:52` are not in `revision_access_44676/LEDGER.md` or any `tasks/` file. Grep finds "row (a)" only in `AMENDMENT.md`. Nothing in `run_nested_library.py` enforces them.
*Fix:*
- State that row-(a) refits run after every primary library unit of the C queue (after position 9 of :547-556), and that a hold on them never holds or reorders a primary unit.
- Add a task file and a LEDGER line for the row-(a) analysis code and the H5 storage requirement, each with its own review gate.
- Optionally, have `run_nested_library.py` in real mode refuse unless a reviewed-marker file for the row-(a) module exists.

**F7. MINOR: the A1 row in DECISIONS.md is stale and contradicts the amendment.**
`DECISIONS.md:40` still says "The deposited scorer and Mulan's convention are reported as sensitivity rows, **without re-selection**". A1 item 4(a) now re-selects and refits (real compute charged to the library budget), and adds a hybrid row (c). The user decided the version in that row. The later changes (row (a) re-selection after review A1-1 F3, and the budget charge after A1-2 F3) have no decision row saying who approved them. The budget charge matters given the user's "nothing descoped" decision (§6.7).
*Fix:* append a dated DECISIONS row (do not edit row 40) recording the change of the sensitivity design, rows (a)-(c) as now in A1 item 4. The row should state that the refits are charged to the library budget, and should name the decider: the user, or the orchestrator with user confirmation.

## Summary
All 10 round-2 findings were addressed. Nine are verified fixed: every number and plan line cited in A1 checks out at full precision, and every round-2 mutant is now killed. F8 is partly fixed: the refusal tests and the new `loadmat` fail-safe stop the accident scenario before any write, but the fail-safe is narrower than A1 states. The rewritten guard behaves correctly on the real file: closed now, and open on a copy given a valid A1 line, also with an `## E1` appended or CRLF endings. The quarantine verifies (2 639/2 639) and is disclosed accurately. Two MAJOR findings remain. A new amendment can reuse A1's deposit line and open the guard (F1). The suite-wide fail-safe misses the configured data directory used on G, stored real outputs, `np.load` and file objects, and its own unit test checks 2 of its 5 wrappers (F3). Five MINOR findings remain: Markdown forms that fail open (F2), test gaps including the untested real-plan `REQUIRED_SECTIONS` wiring (F4), E-section scope against plan :525 and its content limit (F5), row-(a) scheduling and tracking (F6), and a stale DECISIONS row (F7).

VERDICT: NOT RESOLVED — 7 findings
