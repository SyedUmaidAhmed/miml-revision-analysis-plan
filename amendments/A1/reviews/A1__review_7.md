# A1 review 7: AMENDMENT.md (A1), guard and test-suite fail-safe

- **Commit reviewed:** `31f5bf5` (HEAD). Diff since round 6 (`cbb0a60`): `deposit_check.py`, `tests/conftest.py`, `tests/test_deposit_check.py`, `tests/test_failsafe.py`.
- **Reviewer:** independent, new to this amendment; not a previous reviewer.
- **Date:** 2026-10-14.

## Round-6 findings

**F3 (lone `-` underline with trailing whitespace): FIXED.**
- `deposit_check.py:198-201` now rstrips each line and the previous line before stripping container prefixes. `"- "`, `"-\t"`, `"> - "` and `"  - "` reduce to a bare `-` underline and close the guard.
- New test `test_lone_dash_underline_with_trailing_space_closes` (`tests/test_deposit_check.py:358-363`) covers the four strings from round 6.
- **Mutant `old_container`** restores `inner = line[CONTAINER_RE.match(line).end():]` with no rstrip. It is killed: all 4 new parametrised cases fail and the other 142 pass.
- **Differential fuzz** against a CommonMark renderer (markdown-it-py, `commonmark` preset), run on temporary files only. The oracle: the guard opens, but the renderer finds a heading other than the title and `## A1`.
  - The test set had 31 232 documents. 11 232 were systematic: 12 paragraph prefixes × 13 underline containers × 9 markers × 8 trailing characters (space, tab, mixed, NBSP, FF, VT). The other 20 000 were random 1-5-line combinations of heading, underline and container lines.
  - **HEAD: 0 fail-open.**
  - **Oracle check:** the same fuzz on a scratch copy with the old container code finds 285 fail-open cases. So the oracle does detect the defect.

**F4 (fail-safe tests did not pin relative-token resolution or the protected-cwd rule): FIXED.**
- `test_relative_path_from_an_unprotected_cwd_is_resolved` (`tests/test_failsafe.py:154-166`):
  - runs from `PROJECT`, which is unprotected;
  - uses `../VIT_MIL/Code/MIML-SELFVIT/never_exists.mat`, which does not exist and does not contain a protected root as text;
  - covers `subprocess.run`, `os.system`, a `<` redirect and a `dd if=` argument.
- `test_protected_cwd_alone_is_refused` (`:169-172`) runs `/usr/bin/true` with `cwd` set to a protected root. Nothing else names that path.
- The hook now splits tokens on `[\s<>=;|&()'"]+` (`conftest.py:150-154`), which closes the round-6 redirect and `key=path` note.
- **Mutants** were applied in memory through a scratch pytest plugin, after collection, with the fail-safe otherwise active. The accident-scenario tests were deselected.

| mutant | change | killed by |
|---|---|---|
| `abs_tokens_only` | resolve only absolute tokens (re-introduces round-5 F2) | `test_relative_path_from_an_unprotected_cwd_is_resolved` |
| `no_cwd_check` | delete `conftest.py:155-156` | `test_protected_cwd_alone_is_refused` |
| `whitespace_split` | restore the round-6 `t.split()` tokenisation | `test_relative_path_from_an_unprotected_cwd_is_resolved` (the `<` redirect case) |

Each mutant kills exactly the intended test; the other 20 selected tests pass.

## What I ran

1. `./.venv/bin/python -m pytest experiments/revision_r1/tests -q`: **390 passed, 8 errors**. The 8 errors are the TabPFN tests, which by design refuse tabpfn 8.2.0. Round 6 had 384 + 8; the difference is the 6 new tests.
2. `.tabpfn_env/bin/python -m pytest …/test_tabpfn_arms.py …/test_tie_neutral.py …/test_deposit_check.py …/test_failsafe.py -q`: **240 passed**. Round 6 had 234; again, +6 new tests.
3. The four mutants above:
   - `test_failsafe.py`, accident tests deselected: 3 mutants;
   - `test_deposit_check.py`: 1 mutant.
4. The CommonMark differential fuzz at HEAD and on the `old_container` copy.
5. **Real `AMENDMENT.md`** (`python3 -I`, deposit_check only; no data path touched):
   - **Forbidden constructs:** none. No `FORBIDDEN_RE` match, no HTML-block line, no line with trailing whitespace.
   - **Rendered structure:** the CommonMark tokens are paragraphs, lists, one `hr`, and exactly two headings, the h1 title and the A1 h2.
   - **Closed at HEAD:** `amendment_status()` gives `{'A1': None}` and `deposit_recorded()` is False.
   - **Opens once A1's deposit line is filled**, checked under the **real clock** (2026-10-14) and the **default `required`** (`dc.PLAN` pointed at a temporary plan), in three variants: LF; CRLF; and with an `## E1 (2026-10-14)` section appended. In each it opens. With the deposit line unfilled it stays closed.
   - `test_real_amendment_file_opens_once_a1_is_deposited` passes in both suites.
6. **Checked against the code, every statement about the guard and the fail-safe:**
   - `AMENDMENT.md:5-18` (heading grammar, no leading zero, date range, the exactly-one deposit line, DOI distinct case-insensitively from the plan and other A sections, date ordering, E sections, the eight fail-closed conditions, "none of these constructs is used in this file");
   - `:83-89` (open, subprocess, `os.system`, exec and spawn events; protected cwd; text and resolved arguments with symlinks; no child-process tracing; the listed roots incl. configured data dirs; evidence write-protect; case-insensitive comparison; every `loadmat` binding (`h2_common` plus the three `miml_clam.data` modules, which are the only bindings in the tree); the `synthetic_data_dir` exception);
   - `:97` (`h2_common.deposit_guard` applies `deposit_check`);
   - `:5`, "single real-data guard of every revision tool": all six entry points route through `deposit_check.deposit_recorded`: `library_harness:94`, `run_tabpfn_arms:125`, `t03_checks:293`, `export_library_design:71`, `h2_common:70`, which `h2a_rebuild` and `h2b_masks` use.

   **All of these hold at HEAD.**
7. **Simulated the v1.1 Zenodo tree** in scratch, laid out as `build_deposit_v11.py` lays it out: `amendments/A1/{AMENDMENT.md, code/, code/tests/}` plus `plan/PREREGISTERED.md`. I ran the deposited tests there (finding F5).

## New findings

**F5. MINOR: the A1 test claims cannot be checked from the v1.1 deposit as the builder assembles it.**

*Where:*
- `revision_access_44676/tools/build_deposit_v11.py:24-36` (the file set) and `:81-98` (the README text);
- the claims are made at `AMENDMENT.md:5`, `:55`, `:83` and `:104`.

`build_deposit_v11.py` is outside A1's own code. It is listed here because it builds the Zenodo copy, the version a referee will see. That copy is permanent once published.

*What a referee sees on Zenodo:*
- **The fail-safe files are missing.** `AMENDMENT.md:83` and `:104` describe the test-suite fail-safe and point to `tests/conftest.py` and `tests/test_failsafe.py`. Neither file is in the deposit.
- **The tie-neutral tests cannot be collected.** `AMENDMENT.md:55` says `tests/test_tie_neutral.py` checks the closed forms against brute-force enumeration and against `miml_metrics.py`. The deposited copy fails at import with `ModuleNotFoundError: miml_clam`. Its `sys.path` climbs four levels to `MIML_CLAM_Release` (`tests/test_tie_neutral.py:11`), which does not exist in the deposit tree. `miml_metrics.py` is not among the files v1.1 adds; I could not check whether v1.0 contains it.
- **Two deposited deposit-check tests fail** in that tree: 2 failed, 144 passed. Both read the plan and `AMENDMENT.md` beside `deposit_check.py`, but in the deposit those sit in `plan/` and in `amendments/A1/`:
  - `test_real_plan_records_the_deposit` (`tests/test_deposit_check.py:128`);
  - `test_real_amendment_file_opens_once_a1_is_deposited` (`:301`).
- **The README cannot answer this.** It cites a "Source repository commit". Per `CLAUDE.md` known gap 3, that repository is not public.

None of this affects the science or any guard behaviour. But it is the one remaining place where a statement in the deposited A1 cannot be supported by the deposited record.

*Fix, before the v1.1 upload:* make the deposited tests self-contained, or say plainly that they are not.
- **Option 1 (self-contained).** In `build_deposit_v11.py`:
  - add `miml_clam/metrics/miml_metrics.py` (this is the deposited scorer the plan names);
  - have `test_tie_neutral.py` import it from the deposit when `MIML_CLAM_Release` is absent;
  - have the two real-file tests skip when `dc.PLAN` or the `AMENDMENT.md` beside it does not exist.
- **Option 2 (state it).** Add one README paragraph saying:
  - the deposited tests run inside the source repository's layout;
  - in this tree, `test_deposit_check.py` runs standalone (144 of 146; the 2 real-file tests need the repository layout);
  - `test_tie_neutral.py` needs `miml_clam`;
  - the fail-safe files `tests/conftest.py` and `tests/test_failsafe.py` are not deposited.

  Option 2 also requires depositing `conftest.py` and `test_failsafe.py` as documentation.

## Notes (no change required)

- **Token resolution.** `conftest.py:152` splits on quotes and whitespace, so a quoted relative path that contains a space is resolved piece by piece. `AMENDMENT.md:83` does not promise shell-accurate tokenisation, and every real call site passes absolute paths, which the text check catches. Globs remain unclosable without a shell parser, as round 6 said.
- **Fail-closed side effect of the F3 fix.** After the rstrip, an empty list item `- ` directly after a paragraph line now closes the guard. That over-closes, and the real file has no such line (verified above).
- **Unchanged since earlier rounds, and still described accurately:**
  - link-reference titles (`:18` claims structure only);
  - no tracing into child processes (`:83` says so);
  - renames in the evidence tree (`:85` claims write-mode opens only).

## Summary

- **Round-6 F3 and F4 are fixed.** Every round-6 mutant is killed by the new tests, and so is a third that restores whitespace-only splitting. The guard shows 0 fail-open cases in 31 232 CommonMark-differential documents, against 285 for the pre-fix code.
- **The real AMENDMENT.md** has no forbidden construct. It is closed at HEAD and opens once A1's deposit line is filled: under the real clock, under the default `required`, with LF, with CRLF, and with an E section appended.
- **Every statement in the A1 text about the guard and the fail-safe matches the code.**
- **One MINOR finding remains (F5).** The v1.1 deposit the builder produces cannot back the text's test claims:
  - the fail-safe files are absent;
  - `test_tie_neutral.py` cannot be imported;
  - 2 of 146 deposit-check tests fail in the deposit layout.

VERDICT: NOT RESOLVED — 1 findings
