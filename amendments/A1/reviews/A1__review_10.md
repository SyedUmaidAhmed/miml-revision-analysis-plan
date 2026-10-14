# A1 review 10: Zenodo v1.1 deposit (AMENDMENT A1)

- **Commit reviewed:** `5f5343f` ("v1.1 deposit builder: README commit placeholder fixed and asserted (F7); redact only lines naming another manuscript (F8); project_reference folder row (F9)"). The diff since round 9 (`e16f6e2`) touches only `revision_access_44676/tools/build_deposit_v11.py`, plus the round-9 review itself.
- **Reviewer:** an independent senior reviewer acting as the referee who opens the v1.1 deposit. I did not write any of the reviewed material and was not a previous reviewer.

## Round-9 findings

**F7 (the README printed a literal `{commit}`): RESOLVED.**
- The trailing README literal is now an f-string (`build_deposit_v11.py`, the `+ f"""` after the PATH_MAP join).
- `assert "{commit}" not in readme and commit in readme` runs before the README is written.
- The built README, line 73, reads "Source repository commit for v1.1: 5f5343f41b3a9faf530fc81b4fa2af3d2686abac". That is the project HEAD at build time, and the working tree was clean.

**F8 (the "Public deposit route" row was over-redacted): RESOLVED.**
- `OTHER` now matches only the specific manuscript, venue and memo names listed in the grep line below. The bare generic phrase "other manuscripts" has been removed from the pattern.
- The build redacted 3 lines. I checked each against its source:
  - `project_reference/DECISIONS.md:13`. The source row names the authors' other manuscripts by venue, and the memo about them. It names another manuscript, so the redaction is correct.
  - `project_reference/DECISIONS.md:19`. The source row is about one other manuscript, which it names together with its venue. It names another manuscript, so the redaction is correct.
  - `reviews/A1__review_9.md:58`. This is round 9's "What I ran" step 5. It lists the other manuscripts' venue names and folder names as grep targets. It names other manuscripts, so the redaction is correct under the rule. See note 1.
- `DECISIONS.md:22` (Public deposit route) is now kept verbatim. So is the generic mention of "other manuscripts" in deposited review 9 (lines 75 and 77).
- A case-insensitive grep over all of `amendments/` (`.md`, `.py` and `.json` included) returned **no hits**. The grep searched for these names:
[line redacted from the public copy: refers to a different manuscript, outside the scope of this plan]
- The README's redaction list now reads "Redactions in v1.1 (lines that name another manuscript by the same authors)", with `project_reference/DECISIONS.md` at 2 lines and `reviews/A1__review_9.md` at 1 line. This matches the build output and the diff exactly.

**F9 (the folder table omitted `project_reference/`): RESOLVED.**
- `find amendments -type d` gives these folders under `amendments/A1/`:
  - `code`, `code/failsafe_reference`, `code/miml_clam(/metrics)`, `code/tests`
  - `evidence`
  - `project_reference`, `project_reference/tests`
  - `reviews`
- The README folder table has a row for every top-level folder: `code/`, `code/failsafe_reference/`, `evidence/`, `reviews/` and now `project_reference/`. It also has a row for `AMENDMENT.md`.
- The sub-folders `code/miml_clam/`, `code/tests/` and `project_reference/tests/` are named in their parent rows and in the path table.
- The new row's description matches the 13 files in that folder.

## What I ran

All work was done in scratch under `review_A1_r10/`.

1. **Build.** I made two fresh clones of `github.com/SyedUmaidAhmed/miml-revision-analysis-plan`, both at `17f14ec`. In the first I ran `./.venv/bin/python revision_access_44676/tools/build_deposit_v11.py <c1>`.
   - Output: "added 39 files under amendments/A1/; redactions: {'project_reference/DECISIONS.md': 2, 'reviews/A1__review_9.md': 1}; plan/PREREGISTERED.md sha256 unchanged: 7830946ac1603650dde0bc734f54ac90b83338282a388a46892ca9152a050f9a".
   - `git status` in the project afterwards was empty.
2. **v1.0 byte identity.** I compared every tracked v1.0 file against the untouched clone with `cmp`. Only `.zenodo.json`, `README.md` and `SHA256SUMS` differ.
   - `git diff README.md` is append-only.
   - `.zenodo.json` changes `description` and adds `version: "1.1"`; the rest is whitespace reformatting.
   - The `plan/PREREGISTERED.md` sha256 is `7830946a…f9a`.
3. **SHA256SUMS.** `shasum -a 256 -c` reported 0 failures across 67 entries. Every file in the built tree is listed except `SHA256SUMS` itself, which is checked before any test run.
4. **Deposited tests, in isolation.** From `amendments/A1/code/` I ran `<project>/.venv/bin/python -I -m pytest tests -q -p no:cacheprovider -rs`.
   - Result: **157 passed, 2 skipped**.
   - The skips are `test_deposit_check.py:128` and `:303`. Both are the real-plan and real-amendment checks, and both skip with the reason stated in the README.
5. **Referee read (B).**
   - I read the v1.1 README section in full and the deposited `AMENDMENT.md` in full. The deposited `AMENDMENT.md` is `cmp`-identical to `experiments/revision_r1/AMENDMENT.md`.
   - I spot-checked AMENDMENT.md's concrete references against the deposit:
     - All four named tests exist in `project_reference/tests/`.
     - `ranking_four` and `ranking_four_mulan` are in `tie_neutral_metrics.py`.
     - `score` and `score_prereg` are in `library_harness.py`.
     - `metrics_prereg` is in `tabpfn_arms.py`.
     - `meta.scorer` is in `run_nested_library.py`.
     - `h2_common.deposit_guard` calls `deposit_check`.
     - `REQUIRED_SECTIONS = {"A1"}`.
     - The DECISIONS rows cited by name ("A1 tie-neutral ranking metrics", "Budget extensions in AMENDMENT.md", "Sensitivity rows (a)-(c)", 2026-10-14) are present and unredacted.
     - Every PATH_MAP target that the README says is deposited exists.

I called no real-data entry point, pushed nothing, opened no quarantine file, and modified no repo file other than this report.

## New findings

None. I found nothing false, broken or misleading in the v1.1 README section or in the deposited AMENDMENT.md.

## Notes (no change required)

1. **Deposited review 9 loses its step 5.**
   - Under the rule, `reviews/A1__review_9.md:58` is correctly redacted, because it names the other manuscripts' folders.
   - The cost: deposited review 9 keeps step 5's sub-bullets (lines 59-61) and the later reference to "the grep in run 5" (line 77), but loses the step's header.
   - The redaction marker says the line "refers to a different manuscript". That is true only in the sense that it names their folders; the step itself verified this deposit.
   - A reader can still follow the review. This review records the check that was lost (F8 evidence above).
   - Anyone who wants to avoid this in later reviews should keep such grep lists on a single line. This review does that.
2. **Rebuild after this review is committed.**
   - The builder deposits every `A1__review_*.md` and cites the HEAD commit. The archived v1.1 should therefore be built from the commit that contains this review, so that "every independent review round" stays true and the cited commit matches.
   - This review keeps the list of other-manuscript names on one line (the grep list under F8), so only that line will be redacted.
3. **Archive hygiene (repeated from round 9).** Running the deposited tests creates `__pycache__` files that SHA256SUMS does not list. Archive from a fresh build.
4. **DECISIONS.md:22 says "Four out-of-scope rows … are redacted in the public copy".** This refers to v1.0, which redacts four rows across `reviews/PREREG__review_{4,5,9}.md`, and it is accurate for v1.0. The v1.1 copy of DECISIONS.md redacts 2 lines. The README lists both counts separately, so they do not conflict.

VERDICT: RESOLVED, 100%
