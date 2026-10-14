# A1 review 8: AMENDMENT.md (A1) and the v1.1 public deposit

- **Commit reviewed:** `e28804a` (HEAD). Diff since round 7 (`31f5bf5`): `revision_access_44676/tools/build_deposit_v11.py` and `experiments/revision_r1/tests/test_deposit_check.py` (two `skipif` markers). The rest of the diff is the review files for rounds 5-7.
- **Reviewer:** independent and new to this amendment. I am not a previous reviewer.
- **Date:** 2026-10-14.

## Round-7 finding

**F5 (the v1.1 deposit cannot back the text's test claims): FIXED.** Each part of F5 was checked against a deposit I built myself (see "What I ran"):
- **Fail-safe files.** `amendments/A1/code/failsafe_reference/conftest.py` and `test_failsafe.py` are deposited, byte-identical to `experiments/revision_r1/tests/`. The README says they are there to be read and that they run only inside the authors' full project. That is true: they need the project's data and output tree.
- **`test_tie_neutral.py` imports.** The deposit now contains `amendments/A1/code/miml_clam/metrics/miml_metrics.py`, byte-identical (`cmp`) to `../MIML_CLAM_Release/miml_clam/metrics/miml_metrics.py` (sha256 `5e8182d3…42d0ba`; that file was last modified 2026-03-21, so "unchanged" holds). The builder adds empty package markers `miml_clam/__init__.py` and `miml_clam/metrics/__init__.py`. Collection now succeeds.
- **The two real-file tests.** `test_real_plan_records_the_deposit` (`tests/test_deposit_check.py:128`) and `test_real_amendment_file_opens_once_a1_is_deposited` (`:303`) skip when their files are absent. In the deposit they are reported as SKIPPED, with the stated reason. In the project they still run (full suite below).
- **README.** It now says the source repository is not public and is available to the editor on request. It also gives run instructions, and those instructions are accurate.
- **Isolation.** Run with `python -I`, every module the tests imported resolved inside the deposit, with no `sys.path` entry into the authors' tree. The details are under run 3.

## What I ran

1. **Built v1.1 from a fresh clone.** I cloned `github.com/SyedUmaidAhmed/miml-revision-analysis-plan`, checked out `17f14ec`, and ran `./.venv/bin/python revision_access_44676/tools/build_deposit_v11.py <clone>`.
   - Output: "added 25 files under amendments/A1/; redactions: none". The plan sha256 was unchanged (`7830946a…050f9a`, as in the v1.0 SHA256SUMS).
   - The project working tree stayed clean.
2. **Byte identity against a second, untouched clone of `17f14ec`.** Every tracked v1.0 file except `README.md`, `SHA256SUMS` and `.zenodo.json` is byte-identical (`cmp`), including `plan/PREREGISTERED.md`.
   - `git diff README.md` has no removed lines, so the v1.0 README is kept verbatim and v1.1 only appends.
   - `.zenodo.json` gains `version: "1.1"` and a new description. Nothing else changes except whitespace.
   - The deposited `AMENDMENT.md`, `tie_neutral_metrics.py`, `deposit_check.py` and both test files are byte-identical to the repo copies.
3. **Ran the deposited tests in isolation.** From `<clone>/amendments/A1/code/`: `python -I -m pytest tests -q -p no:cacheprovider` gave **157 passed, 2 skipped**. The 2 skips are the two real-file tests.
   - A second run loaded a session-finish plugin from outside the deposit. It found no imported module under `Research_Writer/` apart from `.venv` site-packages, and no `sys.path` entry into the project.
   - `tie_neutral_metrics`, `deposit_check` and `miml_clam.metrics.miml_metrics` were all loaded from the deposit.
4. **SHA256SUMS.** `shasum -a 256 -c SHA256SUMS` passes for all 53 entries, and these are exactly the 53 non-`.git` files apart from SHA256SUMS itself.
5. **Project suite.** `./.venv/bin/python -m pytest experiments/revision_r1/tests -q` gave **390 passed, 8 errors**. The 8 errors are the TabPFN tests, which refuse to run under tabpfn 8.2.0, as expected in `.venv`.
6. **Checked the numbers in the text.**
   - Every plan line that AMENDMENT.md cites (8, 102, 115, 134, 157, 191, 243, 336, 410, 418, 503, 524, 525, 544, 546, 557, 563) says what the text says it does, in the deposited plan.
   - `REQUIRED_SECTIONS = frozenset({"A1"})` (`deposit_check.py:117`), as stated at `:16`.
   - Every number at `AMENDMENT.md:46-47` and `:90` matches `evidence/tie_neutral_on_letter_frost_f0.txt`, including the MIMLIBLR exception (0.3285 / 0.3425 / 0.3259) and the ≤ 1.1e-16 Mulan reproduction claimed at `:64`.
   - The direction claim at `:90` holds: for 6 of 7 methods, |tie-neutral − Mulan| < |deposited − Mulan|.

No real-data entry point was called, no guard was disabled, and no quarantine file was opened.

## New findings

**F6. MINOR: in the deposit, many of AMENDMENT.md's file references do not resolve, and nothing marks them as project-only.**

The deposited `amendments/A1/AMENDMENT.md` is the repo file byte for byte. Its paths are therefore relative to `experiments/revision_r1/` in the private repository, and a referee reading it on Zenodo cannot follow them.

Three kinds of reference are affected.

*(i) Files that are deposited, but under a different path:*

| AMENDMENT.md | cites | where the deposit has it |
|---|---|---|
| `:45` | `../../revision_access_44676/evidence/T03__checks/diagnosis/tie_neutral_on_letter_frost_f0.txt` | `evidence/tie_neutral_on_letter_frost_f0.txt` |
| `:110` | `../../revision_access_44676/tasks/T03-baseline-harness-checks.md` | `evidence/T03-baseline-harness-checks.md` |
| `:83`, `:104` | `tests/conftest.py`, `tests/test_failsafe.py` | `code/failsafe_reference/` |
| `:20` | `experiments/miml_pfn/AMENDMENT.md` | `original_aug2026/AMENDMENT.md` (the README's description implies this, but nothing maps it) |

*(ii) Files that are not deposited and are not marked as such:*
- `DECISIONS.md` (`:7`, `:28`, `:60`);
- `PROJECTIONS.md` (`:61`);
- `../../revision_access_44676/tasks/TNEW-sensitivity-rows.md` and the LEDGER (`:63`);
- `library_harness.score` / `score_prereg` and `metrics_prereg` (`:60`, `:70`, `:94`);
- `t03_checks.py` (`:67`);
- `tabpfn_arms.py`, `run_nested_library.py` and `h2_common.deposit_guard` (`:95-97`);
- `quarantine/…` and its manifest (`:83`).

*(iii) Test claims a Zenodo reader cannot check.* These are listed as A1 tests under "Code":
- `tests/test_nested_library.py::test_selection_uses_the_tie_neutral_rule` and `::test_predictdump_reproduces_library_run` (`:100-101`);
- `tests/test_tabpfn_arms.py::test_unit_stores_tie_neutral_primary_and_prereg_separately` (`:102`);
- `tests/test_h2.py::test_deposit_guard_requires_every_amendment` (`:103`).

None of these files is in the deposit. The README's statement that "every test in `tests/test_tie_neutral.py` and `tests/test_deposit_check.py` runs standalone" is accurate. But it does not say that the other test files A1 names are absent.

This is the same class of problem as F5, extended from the tests to the whole text. It changes no rule, no number and no guard.

*Fix (builder only; leave AMENDMENT.md byte-identical).* In `build_deposit_v11.py`, add a "Paths in AMENDMENT.md" table to the v1.1 README section (`:93-111`) that maps every path in (i) to its deposit location. Then add one sentence saying that the files in (ii) and the test files in (iii) belong to the authors' working repository, are not deposited, and are available to the editor on request. Optionally, deposit `library_harness.py`, `tabpfn_arms.py` and the three test files "for reading", as was done for the fail-safe. Then (iii) is at least inspectable.

## Notes (no change required)
- **Shadowing order in `test_tie_neutral.py:10-11`.** The `MIML_CLAM_Release` path is inserted after the deposit's code directory, so it lands at position 0 and takes precedence over it. In the deposit, that path is four levels above `tests/`, i.e. beside the unpacked archive's top folder. Only someone who unpacks the deposit next to a `MIML_CLAM_Release` checkout (in practice, the authors) would silently test against that copy rather than the deposited one. Since the two are byte-identical today, this has no effect.
- **SHA256SUMS format.** v1.0 lists paths as `./path`, while v1.1 lists `path`. Both verify with `shasum -c`; the format is cosmetic.
- **This review will be deposited.** The builder globs `A1__review_*.md`, so this review will be in v1.1. Its README will also cite whatever commit is HEAD at build time, not `e28804a`. Both are expected.
- **The plan's own line 134** points at `../../../MIML_CLAM_Release/…/miml_metrics.py`. The v1.0 plan cannot be edited, so the README's sentence naming the deposited copy is the correct place for the mapping, and that sentence exists.

VERDICT: NOT RESOLVED — 1 findings
