# A1 review 6: tie-neutral ranking metrics (amendment, guard, fail-safe)

| | |
|---|---|
| Reviewer | Independent senior referee (multi-label / multi-instance evaluation, ML statistics, research-software rigour). Did not write any of the material and is not a previous A1 reviewer. |
| Date | 2026-10-14 |
| Commit | `cbb0a60` (diff against `b75bb17`, which review 5 covered) |
| Inputs | `experiments/revision_r1/AMENDMENT.md` (whole file, read end to end); `deposit_check.py` (whole file); `tests/conftest.py` (whole file); `tests/test_deposit_check.py` and `tests/test_failsafe.py` (diffs and fixtures); subprocess call sites in `library_harness.py:580-602` and `t03_checks.py:195-265`; guard call sites (`grep deposit_recorded\|deposit_guard`); `loadmat` bindings (`grep`); `reviews/A1__review_5.md`. |
| Scratch | `<scratchpad>/review_A1_r6/`: `attack6.py` (35 strings, rendered with markdown-it-py 3.0.0 in CommonMark mode), `mut_dc.py` + `mutdc/` (copies of `deposit_check.py`, `PREREGISTERED.md`, `AMENDMENT.md`, `test_deposit_check.py`), `mut_failsafe.py` + `mut/` (pure-function mutants of `conftest._names_protected`, called directly, so no process is started), `probes/test_probe6.py` (run inside pytest with the real `conftest` loaded via `-p conftest`; the first probe asserts that the hook is on), `realcheck.py` + `realcopy/`. I edited no repository file except this report. I called no real-data entry point. I disabled no guard. I ran no hook mutant inside pytest or against a real process. The only protected file any probe read is `quarantine/…/README.md`, which this review may open. |

## Round-5 findings: status

| # | Round-5 finding | Status | Evidence |
|---|---|---|---|
| F1 | Single-dash setext underline opened the guard | **Fixed for every round-5 string.** One neighbouring form remains: a lone `-` followed by trailing whitespace (new F3). | `deposit_check.py:200` dropped the `("-","*","+")` exemption. Run 3: `A2…`/`-`, `> A2…`/`> -`, `- A2…`/`  -`, the same with 1-3 leading spaces, `--`, `=`, ordered, `*`/`+`, nested, compact `>`/`>-`, list-in-quote, quote-in-list, multi-line paragraph, CR-only and CRLF all **close**. Each renders as `<h1>`/`<h2>` in CommonMark. Run 4: the mutant that restores the exemption, and the mutant that requires `-{2,}`, are both **killed** by `test_single_dash_and_compact_setext_close` (`test_deposit_check.py:349`). Review 5's two test gaps are closed: `no_bq_bare` is killed (`>A2`/`>---`), and `hdate_strict_today` is killed by `test_heading_dated_today_is_accepted` (`:353`). |
| F2 | Relative command paths without `cwd`, and symlink aliases, were not refused | **The code is fixed. The new tests do not kill the mutant that brings the bug back** (new F4). | `conftest.py:140-155`: `base = cwd or os.getcwd()`, and each whitespace token is resolved against `base` through `_under`, which applies `realpath`. `os.system`/spawn/exec now go through the same path (`:182-185`). Run 5, inside pytest with the real `conftest`, cwd = project root, no `cwd=`: review 5's `subprocess.run(["head","-c","10","quarantine/…/README.md"])` and `os.system` with the same relative path are both **refused**. So are `sh -c`, `shell=True`, `./…`, `experiments/../…`, `cd quarantine/…;head …`, a relative `cwd=` and a protected `cwd` with no path argument. Symlink-alias argv is refused too (pure-function run 6). `AMENDMENT.md:83` and `conftest.py:38-47` now describe this mechanism and say plainly that the hook does not follow into child processes. |

## What I ran

| # | What | Result |
|---|---|---|
| 1 | `./.venv/bin/python -m pytest experiments/revision_r1/tests -q` | 384 passed, 8 errors. The 8 errors are the TabPFN tests, which refuse `.venv` by design. |
| 2 | `.tabpfn_env/bin/python -m pytest …/test_tabpfn_arms.py …/test_tie_neutral.py …/test_deposit_check.py …/test_failsafe.py -q` | 234 passed |
| 3 | `attack6.py` at HEAD: 35 bodies, each a synthetic plan with a valid A1 plus one addition. Each was checked with the guard and rendered in CommonMark. A row is flagged when the guard opens and the render shows an unexpected heading or a hidden deposit line. | **5 fail open.** All are a single `-` underline followed by whitespace: `A2…`/`-   `, `A2…`/`-\t`, `A2…`/`- \t `, `> A2…`/`> - ` and `- A2…`/`  - `. Each renders as `<h2>A2 (2026-10-14): new rule</h2>` (F3). Everything else closes. The controls open as expected: a thematic break after a blank line, lists, a valid A2 and a valid E1. List-item HTML blocks with an indented deposit line close. |
| 4 | `mut_dc.py`: 5 mutants of `deposit_check.py` on scratch copies, run against `test_deposit_check.py` | 4 of 4 behavioural mutants are **killed**: `F1_exemption_back`, `setext_two_dash_min`, `no_bq_bare`, `hdate_strict_today`. The candidate fix for F3 (`fix_rstrip`, below) passes all 142 tests, and `attack6.py` against it reports **0 fail-open**. |
| 5 | `probes/test_probe6.py`: 12 command probes inside pytest with the real `conftest` (hook asserted on), cwd = project root | 9 are refused (listed under F2). 3 are not refused, each reading 10 bytes of the README: the shell redirect `head -c 10 <quarantine/…`, the glob `quaranti*/…` and `dd if=quarantine/…` (see Notes). |
| 6 | `mut_failsafe.py`: 5 mutants of `_names_protected`, evaluated as pure functions on the inputs of the F2 tests and of the review-5 scenario | `no_getcwd_fallback`, `no_realpath_tokens` and `no_split` are killed by the current tests. **`abs_tokens_only` survives.** This mutant drops relative-token resolution, which is the F2 bug. It also misses the review-5 scenario (relative path, unprotected cwd). **`no_cwd_check` survives** too (F4). With the tests proposed in F4, both are killed. |
| 7 | Real file (`realcheck.py`), real UTC clock (2026-10-14), **default** `required` (copies with `dc.PLAN` set to a copy of the real plan) | At HEAD: `{'A1': None}`, `deposit_recorded() == False`, so the guard is closed. There is no forbidden construct, no HTML-block line, no link-reference definition and no line with trailing whitespace. The only lone-dash line is the thematic break at `:22`, which follows a blank line. The heading-like lines are exactly the title and `## A1 (2026-10-13): …`. With A1's line filled (`10.5281/zenodo.23341631 (2026-10-14)`) the guard **opens** with LF, with CRLF, and with a valid `## E1 (2026-10-14)` appended. `test_real_amendment_file_opens_once_a1_is_deposited` passes in both suites, and under the F3 fix. |
| 8 | End-to-end read of `AMENDMENT.md`. Every guard and fail-safe sentence (`:5-18, :83-89, :97, :103-104`) was checked against the code. | `:6` matches the code: `SECTION_RE`, the deposit grammar, distinct DOIs, the date bounds. So do `:9-11` (`FORBIDDEN_RE`, `HTML_BLOCK_RE`, `HEADING_LIKE_RE`), `:13-16`, `:18`, `:83-88` (the hook events, `WRITE_PROTECTED_ROOTS`, casefold, `LOADMAT_MODULES`, which covers every `from scipy.io import loadmat` in the tree, and `synthetic_data_dir`) and `:97` (every entry point calls `deposit_recorded` directly or through `h2_common.deposit_guard`). **`:12` is false for F3.** Everything else in the file is unchanged since round 5 apart from `:83`, and round 5 audited it. |
| 9 | `git status` after all runs | clean, apart from the untracked review files |

## New findings

**F3. MINOR: a single-dash setext underline followed by whitespace still opens the guard, contrary to `AMENDMENT.md:12` and `deposit_check.py:53`.**

`AMENDMENT.md:12` says the guard closes on "a setext heading, also inside a blockquote or list item". The docstring at `deposit_check.py:53` says "any "=" or "-" underline". At `deposit_check.py:198`, however, `CONTAINER_RE` consumes `-` + whitespace as a list marker, so `inner` becomes empty and `SETEXT_RE` (`:200`) never sees the underline.

CommonMark allows trailing whitespace on a setext underline, and an empty list item cannot interrupt a paragraph. All five strings below render as `<h2>A2 (2026-10-14): new rule</h2>` and leave the guard **open** with an undeposited A2 (run 3):
- `A2 (2026-10-14): new rule` followed by `- ` (a trailing space, invisible in most editors);
- the same followed by `-\t`, or by `- \t `;
- `> A2 …` followed by `> - `;
- `- A2 …` followed by `  - `.

This is the round-5 F1 attack plus one trailing space. No code path writes such a file, and the real file has no line with trailing whitespace. But `:12` claims to cover it.

*Fix* (verified on a scratch copy: 142/142 tests pass, 0 of 35 attack strings fail open, the real file still opens once filled). At `deposit_check.py:198`:
```python
        stripped = line.rstrip()
        inner = stripped[CONTAINER_RE.match(stripped).end():]
```
Then add `"A2 (2026-10-14): new rule\n- "`, `"…\n-\t"`, `"> A2\n> - "` and `"- A2\n  - "` to `test_single_dash_and_compact_setext_close`.

**F4. MINOR: the F2 tests do not kill the mutant that reintroduces F2, and the protected-`cwd` rule is untested.**

`test_relative_path_without_cwd_is_resolved` (`test_failsafe.py:136`) first does `monkeypatch.chdir(STATIC_ROOTS[0])`, so the working directory itself is protected. Both calls are then refused by the final `_under(base, roots)` check (`conftest.py:153`), whatever happens to relative tokens. Two mutants survive the whole suite (run 6):
- `abs_tokens_only` resolves only absolute tokens. That is exactly the F2 defect: review 5's `quarantine/…` from the project root would again go through.
- `no_cwd_check` deletes `conftest.py:153-154`. The existing `cwd=` test is still refused, because the token `scene.mat` resolves under the protected `cwd`. So `AMENDMENT.md:83` "whose working directory is there" is pinned by no test (HEAD is correct: probe `cwd_only_no_path` is refused).

*Fix* (both proposed checks kill both mutants in run 6 and pass at HEAD; they name a file that does not exist, so even a broken hook reads nothing):
```python
def test_relative_path_from_an_unprotected_cwd_is_resolved(monkeypatch):
    monkeypatch.chdir(conftest.PROJECT)
    rel = "../VIT_MIL/Code/MIML-SELFVIT/never_exists.mat"   # relative: contains no root as text
    with pytest.raises(conftest.RealDataRead):
        subprocess.run(["cat", rel], capture_output=True)
    with pytest.raises(conftest.RealDataRead):
        os.system(f"cat {rel} > /dev/null")

def test_protected_cwd_alone_is_refused():
    with pytest.raises(conftest.RealDataRead):
        subprocess.run(["/usr/bin/true"], cwd=conftest.STATIC_ROOTS[0])
```
The `rel` path must be spelled relative to `PROJECT`. A `relpath` taken from `tmp_path` climbs to `/` and then contains the absolute root as text, so it would not test resolution.

## Notes (no change required)

- **Shell syntax around a relative path (run 5).** A command reached a protected file in three cases:
  - a redirect (`head -c 10 <quarantine/…`);
  - a glob (`quaranti*/…`);
  - a `key=path` argument (`dd if=quarantine/…`).

  `AMENDMENT.md:83` promises a check of arguments "read as text or resolved against the working directory". None of these forms contains the absolute root as text, and none resolves to it as a whole token, so the sentence holds as written. Every real call site passes absolute paths, which the text check catches: `library_harness.py:600`, `t03_checks.py:202,210,265`. If you want the gap closed anyway, split tokens on `[\s<>=;|&()'"]+` rather than on whitespace alone. Globs cannot be closed without a shell parser.
- **Carried over from round 5, unchanged and still accurately described:** link-reference-definition titles can hold a deposit line that does not render (`:18` claims only structure); the hook does not reach into child processes (`:83` now says so); renames and deletes in the evidence tree are not refused (`:85` claims only write-mode opens).
- `_strings` would raise `TypeError` on an `os.spawn` audit event whose mode is a nonzero int, which still stops the call. On POSIX, `os.spawn*` is implemented through fork and exec, so that event is not raised. Nothing to fix.

## Summary

Round-5 F1 and F2 are fixed for every string and route that round 5 reported. Both suites pass (384 + 8 by-design errors; 234). The real `AMENDMENT.md` has no forbidden construct, is closed at HEAD, and opens once A1's deposit line is filled, under the real clock and the default `required`, with LF, with CRLF and with an E section appended. Every other statement about the guard and the fail-safe matches the code.

Two MINOR findings remain:
- **F3:** a lone `-` underline with trailing whitespace still renders a heading the guard misses, so `:12` overstates the guard. The fix is one line plus four test strings.
- **F4:** the new fail-safe tests pass for the wrong reason (a protected cwd). The mutant that restores F2 survives, and so does the one that drops the cwd rule. The fix is two short tests.

Neither finding affects the science or any current code path.

VERDICT: NOT RESOLVED — 2 findings
