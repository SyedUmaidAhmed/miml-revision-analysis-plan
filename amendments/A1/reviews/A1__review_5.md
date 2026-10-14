# A1 review 5: tie-neutral ranking metrics (amendment, guard, fail-safe)

| | |
|---|---|
| Reviewer | Independent senior referee (multi-label / multi-instance evaluation, ML statistics, research-software rigour). Did not write any of the material and is not a previous A1 reviewer. |
| Date | 2026-10-14 |
| Commit | `b75bb17` (diff against `11eb4ee`, which review 4 covered) |
| Inputs | `experiments/revision_r1/AMENDMENT.md`; `deposit_check.py`; `tests/conftest.py`, `tests/test_failsafe.py`, `tests/test_deposit_check.py`, `tests/test_nested_library.py` and `tests/test_tabpfn_arms.py` (diffs); `library_harness.py`, `t03_checks.py`, `run_nested_library.py`, `tabpfn_arms.py` (subprocess, rename and data-dir code only); `PREREGISTERED.md` lines 8, 102, 115, 134, 157, 191, 243, 336, 410, 418, 503, 524, 525, 544, 546, 557, 563; `revision_access_44676/DECISIONS.md` (last rows); `tasks/TNEW-sensitivity-rows.md`; `reviews/A1__review_{1..4}.md`. `tie_neutral_metrics.py`, `library_harness.score/score_prereg` and `tabpfn_arms` `metrics/metrics_prereg` are unchanged since `11eb4ee` (absent from the diff) and were audited in rounds 1-4. |
| Scratch | `<scratchpad>/review_A1_r5/` (`attack5.py`, `mut.py` + `mut/` copies, `probes/test_probe5.py`, `probes/test_probe_env.py`, `realcheck.py`, `realcopy/`, `fake_env/`). I edited no repository file except this report. I called no real-data entry point. Mutants ran only on scratch copies of `deposit_check.py` and `test_deposit_check.py`, with copies of `PREREGISTERED.md` and `AMENDMENT.md`. I disabled no guard and ran no fail-safe mutant. Fail-safe probes ran inside pytest with the real `conftest` loaded (`-p conftest`). The first probe asserted that the hook and the `loadmat` wrappers were active. The only protected file any probe read is `quarantine/…/README.md`, which this review may open. |

## Round-4 findings: status

| # | Round-4 finding | Status | Evidence |
|---|---|---|---|
| N1 | Blockquote setext, raw HTML blocks and the E-content limit fail open, and `:8` overstated the guard | **Fixed for every round-4 string.** One residual form remains (new F1). | `HTML_BLOCK_RE` `deposit_check.py:132,194`; `CONTAINER_RE` stripping before `SETEXT_RE` `:128,196-199`; tests `test_deposit_check.py:312-323`. Run 2: blockquote setext h1/h2, `<script>`, `<div hidden>`, `<style>`, `<template>`, tab-indented and nested-list setext all close. Each was rendered with markdown-it-py 3.0.0 (CommonMark) to confirm it is a real heading or a hidden block. `AMENDMENT.md:7` now says "The guard does not check content". `:8-18` is now an explicit list followed by "The guard is not a Markdown renderer". Mutants `no_html_block`, `html_no_bq` and `setext_no_container` are killed. |
| N2 | Heading dates not checked as dates | **Fixed** | `deposit_check.py:203-208` parses each date with `fromisoformat` and checks `MIN_DATE ≤ d ≤ _today()` for A and E headings alike. Tests `:326-333`. Run 2: `0000-00-00`, `2026-02-30`, `2026-10-00`, `9999-99-99`, `2026-10-12` and a future E date all close. Mutants `no_hdate_parse`, `no_hdate_low` and `no_hdate_high` are killed. `AMENDMENT.md:6-7,14` match the code. |
| N3 | Four audit-hook bypasses; data-dir wiring untested | **The four round-4 routes are fixed.** Two neighbouring routes remain, and the text claims to cover them (new F2). | `conftest.py:74-104` (casefolded real paths; roots recomputed at every event from `MIML_DATA_DIR` and `_DATA_DIR_OVERRIDE`), `:133-143,163-173` (Popen `cwd`, `os.system`, `os.posix_spawn`, `os.exec`, `os.spawn`). Run 4: case variant, `cwd` + relative name, `os.system`, `posix_spawn`, `set_data_dir` mid-test and open through a symlink alias are all **refused**. Tests `test_failsafe.py:98-122`. Run 5: a data dir in `MIML_DATA_DIR` before pytest starts is refused, also under `@synthetic_data_dir`. |
| N4 | Refusal test could write into the evidence tree; round-3 item undone | **Fixed** | `test_nested_library.py:1054-1066` now passes `tmp_path` for `--evidence-dir`, `--workdir` and `--out`, and asserts that no file was written. `WRITE_PROTECTED_ROOTS` with `_is_write` (`conftest.py:61,107-110,161-162`) refuses `open(...,'w')` and `os.open(O_WRONLY\|O_CREAT)` under `revision_access_44676/evidence/`. Reads still work (`test_failsafe.py:125-132`). The default evidence dir of `t03_checks` lies under that root, so the `:970` mutant scenario is closed. `git status` is clean after every run. |
| N5 | Row-(a) refits vs the continuation rule | **Fixed** | `AMENDMENT.md:61` ("While any primary library unit is held, or is awaiting a user decision under §6.7, no row-(a) refit starts"); new DECISIONS row 2026-10-14 "Row-(a) refits wait for held primaries"; TNEW item 1. All three state the same rule, and with it the claim "never … hold, delay or reorder a primary unit" holds. |
| N6 | Reading note | **Fixed** | `AMENDMENT.md:20`: lines 336, 503 and 557 use the bare "AMENDMENT.md" and mean `miml_pfn`; line 544 means this file; lines 243 and 525 ("a dated AMENDMENT") mean this file. Checked against the plan text of each line. |

## What I ran

| # | What | Result |
|---|---|---|
| 1 | `./.venv/bin/python -m pytest experiments/revision_r1/tests -q` | 377 passed, 8 errors. The 8 errors are the TabPFN tests, which refuse `.venv` (8.2.0) by design. |
| 2 | `.tabpfn_env/bin/python -m pytest …/test_tabpfn_arms.py …/test_tie_neutral.py …/test_deposit_check.py …/test_failsafe.py -q` | 227 passed |
| 3 | `attack5.py`: 26 bodies, each a synthetic plan with a valid A1 plus one addition. Each was checked with the guard and rendered with markdown-it-py (CommonMark). | Every round-4 string closes (N1, N2). **Opens on a real heading:** `A2 (2026-10-14): new rule` / `-`, and the same inside a blockquote (`> -`) and inside a list item (`  -`). All three render as `<h2>` (F1). Also opens: a deposit line hidden in a multi-line link-reference-definition title (rendered as nothing; see Notes). Controls open as expected: a valid A2, a valid E1, and an empty list item between items. |
| 4 | `probes/test_probe5.py` (real `conftest`, hook asserted on, cwd = project) | Refused: all six round-4 routes. **Not refused:** `subprocess.run(["head","-c","10","quarantine/…/README.md"])` with an implicit cwd (10 bytes read); `os.system("head … quarantine/…/README.md")` with a relative path; a subprocess given a symlink alias of the quarantine dir in argv (10 bytes); a shell command that reaches the path through an environment variable (10 bytes) (F2, Notes). |
| 5 | `probes/test_probe_env.py`, with `MIML_DATA_DIR` set to a fake dir before pytest starts | The open is refused, both with and without `@synthetic_data_dir`. |
| 6 | 10 text mutants of `deposit_check.py` (scratch) against `test_deposit_check.py` | 7 killed. 3 survive. `setext_prev_no_container` is equivalent: `prev` is non-blank either way. `hdate_le_today_strict` closes on a heading dated today, i.e. it fails closed, but no test pins it (Notes). `no_bq_bare` makes `>A2` / `>---` (no space after `>`) fail open; HEAD closes this form correctly, but no test covers it (Notes). |
| 7 | Real file: `FORBIDDEN_RE`, `HTML_BLOCK_RE` and heading-like scan; status at HEAD; copies with A1's line filled (`10.5281/zenodo.23341631 (2026-10-14)`), real UTC clock (2026-10-14), **default** `required` (`dc.PLAN` set to a copy of the real plan) | No forbidden construct, no HTML-block line, no lone `-`/`=` line and no link-reference definition. The heading-like lines are exactly the title and `## A1 (2026-10-13): …`. HEAD: `{'A1': None}`, so the guard is closed. Filled: **opens** with LF, with CRLF, and with a well-formed `## E1 (2026-10-14)` appended. `test_real_amendment_file_opens_once_a1_is_deposited` passes in both suites. |
| 8 | Plan-line audit (the 16 lines listed in Inputs) and an end-to-end read of `AMENDMENT.md` | Every citation says what A1 says. Numbers at `:44-47,90` are unchanged since round 4, which audited them against `t03b_reproduced.json`. |
| 9 | `git status` after all runs | clean |

## New findings

**F1. MINOR: a single-dash setext heading still opens the guard, contrary to `AMENDMENT.md:12`.**
`AMENDMENT.md:12` says the guard closes on "a setext heading, also inside a blockquote or list item". At `deposit_check.py:198`, the clause `inner.strip() not in ("-", "*", "+")` exempts a lone `-` underline.

In CommonMark, an empty list item cannot interrupt a paragraph, so `text` followed by `-` is a setext h2. Run 3 confirms this with markdown-it-py. The following all render as `<h2>A2 (2026-10-14): new rule</h2>` and leave the guard **open** with an undeposited A2:
- `A2 (2026-10-14): new rule` followed by `-`;
- `> A2 …` followed by `> -`;
- `- A2 …` followed by `  -`.

(`*` and `+` are not setext characters, so their part of the exemption does nothing.)

*Fix:*
- Delete the exemption, so the condition is `SETEXT_RE.fullmatch(inner) and prev_inner.strip()`. This also closes on an empty list item directly under a non-blank line (`- one` / `-`). That is harmless: the real file has no line consisting only of `-` (run 7).
- Add the three strings above to `test_review4_hidden_structure_closes`.

**F2. MINOR: `AMENDMENT.md:83` ("any subprocess, `os.system` or exec call whose arguments or working directory name a path, under the protected locations") is not true for relative paths with the implicit working directory, nor for symlink aliases.**
Run 4 found two routes:
- `subprocess.run(["head","-c","10","quarantine/2026-10-13_…/README.md"])`, started from the project root (pytest's cwd) without `cwd=`, read the file. So did `os.system` with the same relative path. In `conftest.py:139`, a relative token is resolved only when `cwd` is passed explicitly. The `os.system` / `os.posix_spawn` / exec branch (`:170-173`) never resolves relative tokens.
- An absolute argv token that reaches a root through a symlink was not refused either. `_names_protected` (`:133-143`) does a casefolded substring test on the raw text and never takes `realpath` of the token, whereas the `open` branch does and refuses the same alias.

No current code path hits either route. The harness, `t03_checks` and `run_nested_library` pass absolute paths. But the sentence claims to cover them, and this is the same mechanism round 4 asked to fix for an explicit `cwd`.

*Fix:*
- In the `subprocess.Popen` branch, use `cwd or os.getcwd()`. In the `os.system` / spawn / exec branch, pass `os.getcwd()` as `cwd`.
- In `_names_protected`, also test `_under(t if os.path.isabs(t) else os.path.join(cwd, t), roots)` for every token. `_under` already takes `realpath`, so this catches aliases.
- Add tests for a relative argv, a relative `os.system` path and a symlink-alias argv.
- Alternatively, reword `:83` to say what is checked: "whose arguments contain the spelling of a protected path, or whose explicit working directory lies under one".

## Notes (no change required)

- **Link-reference-definition titles.** A multi-line title (`[x]: /u "` … `"`) can hold a `**Deposited:**` line that a reader never sees, and the guard counts it (run 3). This is the same class as the round-4 `<script>` case, but `AMENDMENT.md:18` no longer claims that nothing can be hidden. It says the guard "is not a Markdown renderer" and checks only the listed structure, and the real file has no link-reference definition. Also, a hidden deposit line is no stronger an attack than a visible fake DOI, which no offline check can detect. If you want it closed anyway, treat any line matching `^\s{0,3}\[[^\]]+\]:` as an HTML-block-like construct.
- **Child processes are outside the hook.** An audit hook does not propagate into children. A test that reached `t03_checks` check `g` with guards disabled would start `run_foundation_baselines.py --datasets scene` (`t03_checks.py:258-265`). That child reads real data through its own config paths, and its argv names no protected path. No test calls check `g`, and `:83` describes the argv/cwd mechanism precisely. `conftest.py:42` ("covers … Java/Octave children") and `:89` ("protects these locations against the test suite") read slightly wider than that. If you want to close it, have `lh.child_env()` set `MIML_DATA_DIR` to an empty sentinel directory while `conftest._HOOK["on"]`.
- **Renames and deletions in the evidence tree.** `os.rename` / `os.replace` / `os.remove` / `shutil.rmtree` into or under the evidence tree are not refused. Only write-mode opens are refused, which is exactly what `AMENDMENT.md:85` says. No code path renames into that tree: `run_nested_library.py:150` writes its tmp file next to the target, so the open is caught first. Git recovers anything lost.
- **Test gaps (the code is correct).**
  - No test dates a heading exactly "today" (mutant `hdate_le_today_strict` survives; it fails closed).
  - No test covers the `>A2` / `>---` form without a space after `>` (mutant `no_bq_bare` survives; HEAD closes it).
  - The setup-time capture of a pre-set `MIML_DATA_DIR` / override (`conftest.py:183-194`) works (run 5), but no test exercises it. Round 4 N3(d) asked for that path in particular; the new test covers the event-time path.
- **Stale docstrings.** The docstrings at `deposit_check.py:45-54` and `conftest.py:37-42` do not yet list the HTML-block, heading-date, `cwd`/`os.system` and write-protect rules. They are incomplete, not false.

## Summary
All six round-4 findings are fixed:
- the guard now closes on blockquote setext headings, on raw HTML blocks and on impossible or out-of-range heading dates;
- the text no longer claims that the guard checks E-section content;
- the audit hook refuses case variants, an explicit `cwd`, `os.system` and spawn calls, and data dirs configured mid-test;
- the evidence tree is write-protected and the remaining refusal test uses `tmp_path`;
- row-(a) refits wait for held primaries, in the amendment, DECISIONS.md and TNEW alike;
- the Reading note matches plan lines 243, 336, 503, 525, 544 and 557.

Both suites pass (377 + 8 by-design errors; 227). The real `AMENDMENT.md` has no forbidden construct, is closed at HEAD, and opens once A1's deposit line is filled, under the default `required` and the real clock, with LF, with CRLF and with a valid E section appended. Every plan citation checks out.

Two MINOR findings remain. In each, a sentence of the amendment claims slightly more than the code does:
- the lone-`-` setext underline (F1);
- relative and aliased paths given to subprocesses (F2).

Both have two-line fixes, and neither affects the science or any current code path.

VERDICT: NOT RESOLVED — 2 findings
