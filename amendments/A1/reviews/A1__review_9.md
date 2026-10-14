# A1 review 9: AMENDMENT.md (A1) and the v1.1 public deposit

- **Commit reviewed:** `e16f6e2` (HEAD). Diff since round 8 (`e28804a`): `revision_access_44676/tools/build_deposit_v11.py`, which adds `project_reference/`, `PATH_MAP`, `MAPPED_TOKENS` and `check_path_map`, plus the round-8 review file.
- **Reviewer:** independent and new to this amendment. I am not a previous reviewer.
- **Date:** 2026-10-14.

## Round-8 finding

**F6 (AMENDMENT.md's paths do not resolve in the deposit): FIXED.** I built the deposit myself (run 1 below) and checked every path that `amendments/A1/AMENDMENT.md` cites against the README's "Paths in AMENDMENT.md" table. I included plainly named files and module-qualified names, not only backticked ones.

- **(i) Deposited under a different path. All mapped, and each target exists.**
  - The evidence `.txt` (`:45`) → `evidence/tie_neutral_on_letter_frost_f0.txt`.
  - `T03-baseline-harness-checks.md` (`:110`) → `evidence/`.
  - `tests/conftest.py` and `tests/test_failsafe.py` (`:83`, `:104`) → `code/failsafe_reference/`.
  - `experiments/miml_pfn/AMENDMENT.md` (`:20`) → `original_aug2026/AMENDMENT.md`.
  - "plan line N" → `plan/PREREGISTERED.md`.
- **(ii) Previously absent. Now deposited for reading, or listed as not deposited with a reason.**
  - Byte-identical to the repo (`cmp`): `library_harness.py`, `tabpfn_arms.py`, `run_nested_library.py`, `t03_checks.py` and `h2_common.py`.
  - Also byte-identical: `TNEW-sensitivity-rows.md` and the quarantine `MANIFEST.sha256`.
  - `DECISIONS.md` is deposited redacted; F8 below concerns that redaction.
  - Every symbol AMENDMENT.md names resolves in the deposited files:
    - `library_harness.py`: `score` at `:790`, `score_prereg` at `:801`;
    - `tabpfn_arms.py`: `metrics_prereg` at `:1049-1066`, `optimize_thresholds` at `:1047`;
    - `run_nested_library.py`: `meta.scorer` at `:500`;
    - `h2_common.py`: `deposit_guard` at `:54`, which calls `deposit_check.amendment_status`;
    - `t03_checks.py`: calls `score_prereg` at `:129` and `:162`;
    - `tie_neutral_metrics.py`: `ranking_four` at `:114`, `ranking_four_mulan` at `:142`;
    - `deposit_check.py`: `REQUIRED_SECTIONS` at `:117`, `amendment_status` at `:169`, `deposit_recorded` at `:243`.
  - The three DECISIONS.md rows AMENDMENT.md cites by name are present and unredacted: "A1 tie-neutral ranking metrics", "Budget extensions in AMENDMENT.md" and "Sensitivity rows (a)-(c)".
  - Listed as not deposited, each with a reason:
    - `PROJECTIONS.md`: it does not exist yet, and the plan places it at §6.0, lines 434, 442 and 503;
    - `LEDGER`;
    - `results/revision_r1/`;
    - the KDIS and Mulan Java sources. I checked `MIMLClassifier.java:154`, which is the `setValue(…, 1)` line, and `mulan-1-5-0-sources.jar`, which ships in `external/MIML/…/resources/`.
- **(iii) The named tests are now inspectable.** They are at `project_reference/tests/`:
  - `test_nested_library.py`: `:252` and `:1390`;
  - `test_tabpfn_arms.py`: `:1090`;
  - `test_h2.py`: `:1110`.

**The builder check works for what it claims to check.** `check_path_map` runs first in `main()`, before anything is written. I mutated copies of the builder and of AMENDMENT.md in scratch:
- A new backticked path (`../../revision_access_44676/NEW.md`) is caught.
- A new bare `newtool.py` is caught.
- Dropping `deposit_check.py` or `results/revision_r1/` from `MAPPED_TOKENS` is caught.
- A mutated builder with `ROOT` pinned to the project and `deposit_check.py` unmapped aborted with the AssertionError, and the third clone stayed clean (`git status` empty).

Its scope limits are recorded under Notes.

## What I ran

1. **Built v1.1 from a fresh clone.** I cloned `github.com/SyedUmaidAhmed/miml-revision-analysis-plan`, checked out `17f14ec`, and ran `./.venv/bin/python revision_access_44676/tools/build_deposit_v11.py <clone>`. It printed: "added 38 files under amendments/A1/; redactions: {'project_reference/DECISIONS.md': 3}", with the plan sha256 unchanged. The project's working tree stayed clean.
2. **Byte identity against a second, untouched clone of `17f14ec`.**
   - Every tracked v1.0 file except README.md, SHA256SUMS and .zenodo.json is `cmp`-identical.
   - `plan/PREREGISTERED.md` sha256 = `7830946ac1603650dde0bc734f54ac90b83338282a388a46892ca9152a050f9a`.
   - `git diff README.md` removes no lines, so the build only appends.
   - `.zenodo.json` changes `version` and `description`, and reformats whitespace.
3. **Deposited tests in isolation.** From `amendments/A1/code/`, `.venv/bin/python -I -m pytest tests -q -p no:cacheprovider -rs` gave **157 passed, 2 skipped**. The two skips are the real-plan and real-amendment tests (`test_deposit_check.py:128` and `:303`), with the stated reasons.
4. **SHA256SUMS.** `shasum -a 256 -c` passes on all 66 entries. Those 66 are every built file. The only unlisted files are the `__pycache__` files created by my own test run in step 3.
[line redacted from the public copy: refers to a different manuscript, outside the scope of this plan]
   - The paper's own references remain: "Access-2026-44676", "IEEE Access" and "submitted manuscript" appear in AMENDMENT.md, the evidence, `project_reference/` and the reviews.
   - The three redactions are DECISIONS.md lines 13, 19 and 22. Line 22 is over-redacted (F8).
6. Mutation runs of `check_path_map`, as above.

No real-data entry point was called, nothing was pushed, and no quarantine data file was opened. Only the quarantine `MANIFEST.sha256` was compared.

## New findings

**F7. MINOR (a regression in this commit): the v1.1 README prints a literal `{commit}` where the source commit should be.**
- **Where:** `revision_access_44676/tools/build_deposit_v11.py:180-187`.
- **Cause:** The README text is now built as `f"""…""" + "".join(...) + """…"""`. The last piece is a plain string, not an f-string. So line 185, "Source repository commit for v1.1: {commit}", is written verbatim.
- **Effect:** The built README reads "Source repository commit for v1.1: {commit} (the authors' working repository, … available to the editor on request)". The only link from the deposit to the code version it was built from is lost. An editor asking for that commit cannot name it. At `e28804a` the whole block was one f-string, so the field was filled correctly then.
- **Fix:** make the trailing literal an f-string (`+ f"""…"""`), or `.format(commit=commit)` it. A check such as `assert "{commit}" not in readme` before writing would stop it recurring.

**F8. MINOR: DECISIONS.md line 22 (the "Public deposit route" row) is redacted as "refers to a different manuscript", which is false.**
- **Where:** `build_deposit_v11.py:60-61`.
- **Cause:** The redaction regex `OTHER` matches the generic phrase "other manuscripts". Line 22 is the 2026-10-13 row that sets up this very deposit (plan-only GitHub repo plus Zenodo). It matches only because its last sentence says "Four out-of-scope rows (decisions about other manuscripts) are redacted in the public copy". It names no other manuscript.
- **Effect:** In the deposited `project_reference/DECISIONS.md`, line 39 ("**Deposit route (amends the public-deposit-route row)**") amends a row that the reader is told is about a different manuscript. The redaction marker is a false statement in a public record, and it hides a row directly about this deposit.
- **Fix:** leave line 22 unredacted. It names no other manuscript, and the grep in run 5 stays clean without redacting it. Do this either by tightening `OTHER` (for example, drop the bare `other manuscripts` alternative and rely on the specific names) or with an explicit allow-list of rows, then rebuild. The README's redaction count becomes 2.

**F9. MINOR: the README's folder table omits `amendments/A1/project_reference/`.**
- **Where:** `build_deposit_v11.py:167-173`.
- **Effect:** The folder table lists every v1.1 folder except the one this commit adds, which holds 13 files. The folder appears only indirectly, in the path table's right-hand column. A reader scanning the folder list will not learn what `project_reference/` is, or that it is read-only.
- **Fix:** add a row: `| amendments/A1/project_reference/ | project files and records A1 cites (harness, arms, runners, guard, named tests, DECISIONS.md redacted, TNEW task, quarantine README and manifest), deposited for reading; they run only inside the authors' full project |`.

## Notes (no change required)

- **Scope of `check_path_map`.** It matches only backticked tokens that contain `/` or end in `.md`, `.py`, `.json` or `.txt`. My mutations confirmed it does **not** catch:
  - unbackticked filenames (e.g. `NEWFILE.md`; AMENDMENT.md's own `DECISIONS.md` is unbackticked);
  - module-qualified names (`newmod.func`, as `library_harness.score` and `h2_common.deposit_guard` are written);
  - other extensions (`.csv`, `.m`, a slash-free `Foo.java:12`).

  It also checks `MAPPED_TOKENS`, a set kept separately from the `PATH_MAP` rows the README prints, and it does not verify that a mapped target exists in the deposit. Every citation in today's AMENDMENT.md is mapped and resolves (verified by hand above), so this matters only for future amendments. The builder comment ("every backticked path") states the scope accurately.
- **The `experiments/revision_r1/ → plan/` row.** At AMENDMENT.md:20 that directory is cited as the home of "this file", which in the deposit is `amendments/A1/`. The adjacent "AMENDMENT.md (this file)" row resolves it, so this is cosmetic.
- **`results/revision_r1/`.** The README says it was "empty at the time of this deposit". In fact it does not exist in the working tree, which is a stronger form of the same claim.
- **Path-table formatting.** The first column puts descriptions inside the code span (e.g. `` `experiments/revision_r1/ (the plan's directory)` ``). This is cosmetic.
- **Archive hygiene.** If the deposited tests are run before archiving, `__pycache__/*.pyc` files appear that SHA256SUMS does not list. Archive from a fresh build, as was done for v1.0.
- **Symbols that are not paths.** `PredictDump` (Java), `set_data_dir` and `MIML_DATA_DIR` are referenced by name but are not deposited. They are described in the deposited harness code and the evidence file. No action is needed.

VERDICT: NOT RESOLVED — 3 findings
