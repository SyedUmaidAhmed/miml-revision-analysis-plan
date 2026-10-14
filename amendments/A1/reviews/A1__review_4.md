# A1 review 4: tie-neutral ranking metrics (amendment, guard, fail-safe)

| | |
|---|---|
| Reviewer | Independent senior referee (multi-label / multi-instance evaluation, ML statistics, research-software rigour). Did not write any of the material and is not a previous A1 reviewer. |
| Date | 2026-10-14 |
| Commit | `11eb4ee` (diff against `d3b6b73`) |
| Inputs | `experiments/revision_r1/AMENDMENT.md`; `deposit_check.py`; `tie_neutral_metrics.py`; `library_harness.py` / `tabpfn_arms.py` scorer and data-dir wiring; `tests/conftest.py`, `tests/test_failsafe.py`, `tests/test_deposit_check.py`, `tests/test_tie_neutral.py`, `tests/test_h2.py` (diff), `tests/test_nested_library.py` (refusal tests); `PREREGISTERED.md` (lines 8, 102, 115, 134, 157, 191, 243, 336, 410, 418, 503, 524, 525, 536-557, 563); `revision_access_44676/DECISIONS.md` (last rows), `LEDGER.md` "Gating tasks", `tasks/TNEW-sensitivity-rows.md`; `evidence/T03__checks/diagnosis/reproduced/t03b_reproduced.json`; `reviews/A1__review_{1,2,3}.md`. No quarantine file was opened except one probe read of `README.md` (below). |
| Scratch | `<scratchpad>/review_A1_r4/` (`attack4.py`, `mut.py` + `mut/` copies, `probes/test_probe_failsafe.py`, fake data dirs). No repository file was edited except this report. No real-data entry point was called. Mutants were applied to scratch copies of `deposit_check.py` + `test_deposit_check.py` (+ copies of `PREREGISTERED.md`, `AMENDMENT.md`) only; no guard was disabled anywhere and no fail-safe mutant was run. Fail-safe probes ran inside pytest with the real `conftest` loaded (`-p conftest`), and the first probe asserted the hook and wrappers were active. |

## Round-3 findings: status

| # | Round-3 finding | Status | Evidence |
|---|---|---|---|
| F1 | A2 can reuse A1's deposit line; deposit may predate the amendment | **Fixed** (residual: heading date not validated, new N2) | `deposit_check.py:214-219`, `SECTION_RE` `:124` (date mandatory). Tests `test_deposit_check.py:208-219` (copied line, copied with case change, deposit before heading). Mutants `no_doi_unique`, `no_hdate`, `doi_unique_case`, `date_optional2` all killed. `doi_unique_case2` survives but is near-equivalent (a case-variant copy still nulls the lowercase section). |
| F2 | Markdown forms fail open; `:8` overstated | **Fixed for every attack string of round 3** (residual forms, new N1) | `HEADING_LIKE_RE` `:127`, `FORBIDDEN_RE` `:130`; tests `:222-240` cover blockquote/list/indented headings, fences, comments, `<pre>`, `<hN>`, nested fences. Mutants `heading_simple` (8), `no_list_marker` (6), `no_forbidden_fence`, `no_forbidden_tilde`, `no_forbidden_comment_close`, `no_forbidden_tag` (3), `no_tag_ignorecase` killed. |
| F3 | Fail-safe narrower than claimed | **Largely fixed** (residuals N3, N4) | Audit hook `conftest.py:77-100` covers `open` (so `np.load`, file objects, every `loadmat` import path) and `subprocess.Popen` argv; roots now include `results/revision_r1`, `quarantine/`, configured data dirs; `MIML_DATA_DIR` hidden and override reset (`:106-118`); a missing `LOADMAT_MODULES` entry now errors (`:120`); `test_every_loadmat_binding_is_wrapped`, per-root test, subprocess test; accident tests now assert `tmp_path` holds no file. Positive probe: with `MIML_DATA_DIR` set before pytest starts, an open under it is refused. Not done: the round-3 item "give `test_nested_library.py:1061-1064` tmp paths" (N4). |
| F4 | Four surviving guard mutants | **Fixed** | `required_never_default` killed by `test_real_plan_applies_required_sections_by_default` (`:285-298`); lone `<!--` and fences now forbidden outright; CR/CRLF tests `:175-181` (`cr_not_normalised` survives only because `open()` already applies universal newlines, so it is an equivalent mutant); `title_twice_ok` survives and is harmless (noted in round 3). |
| F5 | E scope vs plan :525; no content limit; undated E | **Fixed in substance** (wording residuals N1, N6) | `AMENDMENT.md:7` adds §6.5 cap approvals and the :524 reduced grid, states the content limit, requires `## E<n> (YYYY-MM-DD)`; DECISIONS row 2026-10-14 "E sections, scope and content". The Reading note `:10` was not updated (N6); the content limit is not mechanical (N1). |
| F6 | Row-(a) refits unscheduled; gates only in prose | **Fixed** (residual interaction with the continuation rule, N5) | `AMENDMENT.md:51` (after every primary library unit), `:53`; `tasks/TNEW-sensitivity-rows.md` with review gate; LEDGER "Gating tasks" row, OPEN. |
| F7 | Stale DECISIONS row | **Fixed** | Appended row 2026-10-14 "Sensitivity rows (a)-(c)", names the change from "without re-selection", the budget charge and the schedule; decider **user**; row 40 left unedited. |

## What I ran

| # | What | Result |
|---|---|---|
| 1 | `./.venv/bin/python -m pytest experiments/revision_r1/tests -q` | 358 passed, 8 errors (the 8 TabPFN tests refuse `.venv`, by design) |
| 2 | `.tabpfn_env/bin/python -m pytest …/test_tabpfn_arms.py …/test_tie_neutral.py …/test_deposit_check.py …/test_failsafe.py -q` | 208 passed |
| 3 | Real file: `FORBIDDEN_RE` search on the real `AMENDMENT.md`; list of heading-like lines; status at HEAD; copies with A1's line filled (`10.5281/zenodo.23341631 (2026-10-14)`), real clock, **default** `required` (`dc.PLAN` pointed at a copy of the real plan) | No forbidden construct; heading-like lines are exactly the title and `## A1 (2026-10-13): …`; HEAD: `{'A1': None}`, closed. Filled: **opens**; also with CRLF, and with a well-formed `## E1 (2026-10-14)` appended. `test_real_amendment_file_opens_once_a1_is_deposited` passes. |
| 4 | `attack4.py` (synthetic plan, valid A1, one hostile addition) | **Opens:** undeposited A2 as a blockquote setext heading (`> A2 (2026-10-14): new rule` / `> ---`, and `> A2` / `> ===`); A2 whose only deposit line sits inside `<script>…</script>`; A2 headed `(0000-00-00)`, `(2026-02-30)`, `(2026-10-00)`; `## E1 (9999-99-99)`; an E1 containing "Also RankingLoss now uses Mulan." Closed (correct): list-item setext, A2 headed with a later date than its deposit. Rendering checked with markdown-it-py 3.0.0 (CommonMark, scratch install): the blockquote forms render as `<h2>`/`<h1>`; `<script>` and `<div hidden>` hide their contents. |
| 5 | 25 text mutants of `deposit_check.py` on scratch copies, against `test_deposit_check.py` | 20 killed; survivors `doi_unique_case2` (near-equivalent), `cr_not_normalised` (equivalent), `title_twice_ok` (harmless), `E_leading_zero` (cosmetic), and a malformed `date_optional` (superseded by `date_optional2`, killed). |
| 6 | Fail-safe probes (`probes/test_probe_failsafe.py`, `-p conftest`, hook asserted on; control: exact-case open of the quarantine README is refused) | **Not refused:** (i) `open(PROJECT/QUARANTINE/2026-10-13_…/readme.md)` read 10 bytes (APFS is case-insensitive; `realpath` keeps the given case); `_is_real` is also False for `…/VIT_MIL/Code/miml-selfvit/scene.mat`, which exists (stat only, not read); (ii) `subprocess.run(["head","-c","10","README.md"], cwd=<quarantine run dir>)` read 10 bytes; (iii) `os.system("head -c 10 <quarantine README>")` succeeded; (iv) a data dir set with `ta.set_data_dir()` during a test is not protected. **Refused:** a dir given in `MIML_DATA_DIR` before pytest starts. The only protected file actually read was `quarantine/…/README.md`, which this review may open. |
| 7 | Number audit: every figure in `AMENDMENT.md:34-37,54,74` against `t03b_reproduced.json` | All correct (unchanged lines since round 3; re-checked: distinct counts 2/5/11/115/373/460/613, RL 0.659/0.371/0.335, MIMLIBLR 0.3285/0.3425/0.3259, AP ±5.45e-5, DGC −1.34e-4, Mulan reimplementation ≤ 1.1e-16). |
| 8 | Plan-line audit for every line A1 cites, plus 536-557 | All say what A1 says, except the Reading note (N6). |
| 9 | `git status` after all runs | clean (nothing written into the repo by the suites or probes) |

## Judgement on the specific questions

- **Guard opens on the real file once deposited:** yes, under the default `required`, the real clock, LF and CRLF, and with a well-formed E section appended (run 3). The real file contains no forbidden construct. The allowlist did not make the guard unusable.
- **Audit-hook fail-safe, can a test still read a protected path:** yes, by four routes (run 6 and N3). None is reached by any current test, and the realistic accident path (a guard mutant plus a refusal test reaching `loadmat` / `np.load` on a correctly spelled data path) is closed. **Could it break legitimate tests or pytest:** no evidence of that. The hook is inert outside the fixture window, pytest's own cache and `tmp_path` lie outside every root, both suites pass, and the repo is clean afterwards. Under `--import-mode=importlib`, `import conftest` in `test_failsafe.py` would create a second module and those tests would fail loudly (not pass silently); acceptable.
- **Text claims about the fail-safe:** `AMENDMENT.md:73` and `conftest.py:34-41` are accurate for correctly spelled absolute paths and argv, but "refuses any file open … under the protected locations" and "covers … Java/Octave children" are stronger than the code (N3).

## New findings

**N1. MINOR: `AMENDMENT.md:8` still says more than the guard does.**
`AMENDMENT.md:8` says the guard closes on "a setext heading" and that it "accepts only the narrow structure above, and closes on anything else". Run 4 shows that it does not:
- a setext heading inside a blockquote (`> A2 …` followed by `> ---` or `> ===`) renders as `<h2>`/`<h1>` but opens the guard. `SETEXT_RE` (`deposit_check.py:128`) does not strip container markers;
- raw HTML blocks other than `<pre>` (`<script>`, `<style>`, `<div hidden>`, `<template>`) hide their content from a reader, but a `**Deposited:**` line inside one is counted (`FORBIDDEN_RE`, `:130`);
- the E-section content limit (`:7`, "may contain only …") is not checked by code, but `:5` says "This is enforced mechanically" just before the list of rules. An E1 containing a rule change opens the guard.

*Fix:*
- Strip leading container markers (`>`, list markers) from both the line and `prev` before applying `SETEXT_RE`, so a blockquote setext heading is caught.
- Add to `FORBIDDEN_RE` any line whose first non-space, non-container character is `<` followed by a letter or `/`, i.e. any HTML block start. The real file has none.
- Add the four strings from run 4 as tests.
- Reword `:8`'s last sentence to "closes on every construct listed here", and say in `:7` that the E content limit is checked at review, not by `deposit_check`.

**N2. MINOR: heading dates are not checked as dates.**
`SECTION_RE` (`deposit_check.py:124`) accepts any `\d{4}-\d{2}-\d{2}`, and `:218` compares the dates as strings. `## A2 (0000-00-00)`, `(2026-02-30)` and `(2026-10-00)` open the guard when a valid deposit line is present, and `## E1 (9999-99-99)` opens it too (run 4). This defeats the round-3 F1 rule "deposit not earlier than the heading date". It also contradicts `AMENDMENT.md:6` ("the date is the day the amendment was written and is mandatory") and the "dated AMENDMENT" required by plan :243/:525/:544.
*Fix:* parse each heading date with `datetime.date.fromisoformat`, and close the guard unless `MIN_DATE ≤ date ≤ _today()`, for A and E sections alike. Add one test each for an impossible date, a date before 2026-10-13 and a future date.

**N3. MINOR: the audit hook has four bypasses, and its configured-data-dir wiring is untested.**
`AMENDMENT.md:73` says the hook "refuses any file open, and any subprocess whose arguments name a path, under the protected locations". Probes (run 6) found four routes around it:
- **(a) Case variants.** `_is_real` (`conftest.py:68-74`) compares paths by exact-case prefix after `realpath`, which keeps the given case on case-insensitive APFS. `QUARANTINE/…/readme.md` was read.
- **(b) Subprocess `cwd`.** The `subprocess.Popen` branch (`:87-97`) checks argv only. A child started with `cwd` under a root and given a relative file name read it. `os.system`, `os.posix_spawn` and `os.exec*` events are not handled at all.
- **(c) Data dir configured mid-test.** Roots are fixed at fixture setup (`:106-118`), so a data dir configured during the test (`ta.set_data_dir(d)`, `run_tabpfn_arms.main([... "--data-dir", d])`, `monkeypatch.setenv`) is not protected.
- **(d) The wiring itself is untested.** `test_configured_data_dir_is_protected` (`test_failsafe.py:46-56`) adds the root to `REAL_DATA_ROOTS` by hand. It never exercises the `env_dd` / `_DATA_DIR_OVERRIDE` capture, so deleting `:115-117` would not fail it.

None of these is reached by a current test.

*Fix:*
- In `_is_real`, compare `os.path.normcase(p).casefold()` against casefolded roots when `sys.platform == "darwin"`, or walk the path's ancestors with `os.path.samefile`.
- In the Popen branch, also check `args[2]` (cwd) and resolve relative argv items against it. Refuse the `os.system` / `os.posix_spawn` / `os.exec` events when their command names a root.
- Compute the configured roots inside `_audit`, at event time, from `os.environ` and `tabpfn_arms._DATA_DIR_OVERRIDE`. Keep the setup-time capture as well.
- Replace the hand-appended test with one that sets the override and then opens a file under it.
- Until then, word `:73` as "refuses opens and subprocess arguments that resolve, with the same spelling, under a protected root".

**N4. MINOR: a refusal test can still write synthetic output into the tracked evidence tree, and one round-3 F3 item was not done.**
Round-3 F3(e) asked for tmp paths at `test_nested_library.py:1061-1064`. They still use the default `--evidence-dir`, `--workdir` and `/tmp`. More concretely, `test_guard_cli_refuses_synthetic_into_real_root` (`test_nested_library.py:970`) runs `t03_checks.main(["d", "--synthetic", "60"])` against the default evidence dir `revision_access_44676/evidence/T03__checks` (`t03_checks.py:61,285`). That tree is not a protected root. With an in-memory `guard_write` mutant (the round-2 accident pattern), this test would overwrite tracked T03 evidence with synthetic output, and the hook would not stop it. The damage is recoverable from git, so this is MINOR.
*Fix:*
- Give `:1061` and `:1064` `tmp_path` arguments (the round-3 item).
- In `_audit`, refuse write-mode opens (mode containing `w`/`a`/`x`/`+`, or flags with `O_WRONLY|O_RDWR|O_CREAT`) under `revision_access_44676/evidence/`. Reads stay allowed. `:970` keeps passing, because its refusal fires first.

**N5. MINOR: "can never hold, delay or reorder a primary unit" (`AMENDMENT.md:51`) does not hold under the plan's continuation rule.**
Plan :546 lets later units that are independent of a held unit run during a hold if they fit the remaining budget. Row-(a) refits are later units. While a primary library unit is held at the 3 000-h total (:541-543), the refits can therefore start and spend the remaining library budget. That enlarges the extension the held primary unit needs, which can delay it or tip the user's decision against it. The same gap exists in the DECISIONS row of 2026-10-14 and in TNEW scope item 1.
*Fix:* state in `:51` (and in a new DECISIONS row and in TNEW item 1) that row-(a) refits count as dependent on every primary library unit: they do not start while any primary library unit is held or awaiting a user decision. Then the claim is true.

**N6. MINOR: the Reading note (`AMENDMENT.md:10`) was not updated for plan :525 and mis-describes :243.**
The note says that the bare "`AMENDMENT.md`" at lines 243 and 544 means this file. Line 243 actually says "a dated AMENDMENT (§6.7)" (not "AMENDMENT.md"). Line 544 names the file with its directory. Line 525 ("by a dated AMENDMENT"), which `:7` now routes here, is not mentioned. Round-3 F5's fix asked for `:10` to be updated to match.
*Fix:* reword the second sentence: "The 'dated AMENDMENT' of lines 243, 525 and 544 is this file (as `## E<n>` sections)."

## Summary
All seven round-3 findings were addressed, and six are fully fixed. The guard now refuses a copied or back-dated deposit line, rejects every Markdown attack string from round 3, applies `REQUIRED_SECTIONS` to the real plan by default, and still opens on the real `AMENDMENT.md` once A1's line is filled (default `required`, real clock, LF/CRLF, with an E section). The real file contains no forbidden construct. The audit-hook fail-safe closes the accident path and the configured-data-dir gap of round 3. It breaks no legitimate test, and both suites pass (358 + 8 by-design errors; 208). Every number and plan citation in A1 checks out. Six MINOR findings remain, and none blocks the science:
- two residual fail-open forms and an overclaiming sentence in the guard text (N1);
- unchecked heading dates (N2);
- four bypasses of the audit hook and an untested wiring path (N3);
- an unprotected evidence tree, plus an undone round-3 item (N4);
- the row-(a) refits against the continuation rule (N5);
- a stale Reading note (N6).

VERDICT: NOT RESOLVED — 6 findings
