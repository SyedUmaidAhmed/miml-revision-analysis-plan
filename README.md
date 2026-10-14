# Analysis plan for the revision of IEEE Access manuscript Access-2026-44676

This archive is the **binding pre-registration (analysis plan)** for every new analysis in the revision of
*Re-examining the Multi-Instance Multi-Label Benchmark Suite* (Syed Umaid Ahmed, Atif Tahir, Muhammad Waqas).
It is deposited **before any revision experiment has produced a number**.

| folder | contents |
|---|---|
| plan/ | PREREGISTERED.md (v3 with its pre-deposit addendum; final and binding), power_table.py and its output, and the duplicate-row evidence behind the H2-A rule |
| original_aug2026/ | the original MIML-PFN pre-registration, amendment and result (2026-08-14/15). These were local, unversioned files until 2026-10-12; their local dates and sha256 are in the plan's header. |
| history/ | v2 of the revision plan (superseded) |
| reviews/ | independent reviews 1–15 of the plan. Review 1 is the only record of v1. |

Source repository commit: 105475e188006b72411f1729fd92f0cea4018ba5.
The checksum of plan/PREREGISTERED.md in this archive is binding (plan §1.8).

## Redactions
Lines in the review files that refer to **other, unrelated manuscripts** by the same authors are redacted in this public copy and marked in place. They only recorded that those decisions do not conflict with this plan. Nothing about this plan, its analyses or its decision rules is redacted. The unredacted reviews are kept by the authors and available to the editor on request.
- `reviews/PREREG__review_12.md`: 1 line(s)
- `reviews/PREREG__review_4.md`: 1 line(s)
- `reviews/PREREG__review_5.md`: 1 line(s)
- `reviews/PREREG__review_9.md`: 2 line(s)


## Version 1.1: AMENDMENT A1 (tie-neutral ranking metrics)

`amendments/A1/AMENDMENT.md` amends the plan above; the plan text itself is unchanged, and its v1.0 checksum
stays binding. A1 takes effect only from this deposit (plan §1.8). The deposited copy reads
"**Deposited:** pending" in its own deposit line, because it cannot contain its own DOI; the authors' repository
records this version's DOI in that line afterwards, exactly as was done for the plan's line 8.

| folder | contents |
|---|---|
| amendments/A1/AMENDMENT.md | the amendment: defect, corrected rule, sensitivity rows, alternatives considered, what had been observed |
| amendments/A1/code/ | the tie-neutral scorer, the real-data guard (`deposit_check.py`), their tests, and the deposited scorer `miml_clam/metrics/miml_metrics.py` (unchanged) |
| amendments/A1/code/failsafe_reference/ | the test-suite fail-safe (`conftest.py`, `test_failsafe.py`), deposited for reading; it runs only inside the authors' full project |
| amendments/A1/evidence/ | the harness-check results behind A1, including the KDIS/Mulan ground-truth bug and its effect on the submitted numbers |
| amendments/A1/reviews/ | every independent review round of A1 and of the harness checks |
| amendments/A1/project_reference/ | project files and records A1 cites, deposited for reading: harness modules and tests, DECISIONS.md, the sensitivity-rows task, the quarantine README and manifest |

**Paths in AMENDMENT.md.** The amendment is deposited byte for byte, so its paths are those of the authors'
working repository. This table gives the location of each one in this deposit:

| path in AMENDMENT.md | in this deposit |
|---|---|
| `experiments/revision_r1/ (the plan's directory)` | plan/ |
| `PREREGISTERED.md / "the deposited plan" / plan line N` | plan/PREREGISTERED.md (v1.0, unchanged) |
| `experiments/miml_pfn/AMENDMENT.md` | original_aug2026/AMENDMENT.md |
| `AMENDMENT.md (this file)` | amendments/A1/AMENDMENT.md |
| `tie_neutral_metrics.py, tie_neutral_metrics.py::ranking_four` | amendments/A1/code/tie_neutral_metrics.py |
| `deposit_check.py` | amendments/A1/code/deposit_check.py |
| `miml_metrics.py (the deposited scorer)` | amendments/A1/code/miml_clam/metrics/miml_metrics.py |
| `tests/test_tie_neutral.py, tests/test_deposit_check.py` | amendments/A1/code/tests/ (run standalone) |
| `tests/conftest.py, tests/test_failsafe.py` | amendments/A1/code/failsafe_reference/ (read only) |
| `library_harness.py, tabpfn_arms.py, run_nested_library.py, t03_checks.py, h2_common.py` | amendments/A1/project_reference/ (read only) |
| `tests/test_nested_library.py, tests/test_tabpfn_arms.py, tests/test_h2.py (named tests)` | amendments/A1/project_reference/tests/ (read only) |
| `DECISIONS.md (rows cited by name)` | amendments/A1/project_reference/DECISIONS.md (redacted as stated) |
| `../../revision_access_44676/tasks/TNEW-sensitivity-rows.md` | amendments/A1/project_reference/TNEW-sensitivity-rows.md |
| `../../revision_access_44676/tasks/T03-baseline-harness-checks.md` | amendments/A1/evidence/T03-baseline-harness-checks.md |
| `../../revision_access_44676/evidence/T03__checks/diagnosis/tie_neutral_on_letter_frost_f0.txt` | amendments/A1/evidence/tie_neutral_on_letter_frost_f0.txt |
| `t03b_reproduced.json (evidence)` | amendments/A1/evidence/t03b_reproduced.json |
| `quarantine/, quarantine/2026-10-13_accidental_letter_frost_run/` | amendments/A1/project_reference/quarantine_README.md and quarantine_MANIFEST.sha256 (the quarantined files themselves are not deposited and were never read) |
| `results/revision_r1/` | not deposited: the production output tree, empty at the time of this deposit |
| `PROJECTIONS.md` | not deposited: written before the first production run (plan §6.0) |
| `LEDGER` | not deposited: the authors' tracking file, available to the editor on request |
| `external/MIML/mavenProject/src/main/java/miml/classifiers/miml/MIMLClassifier.java:154` | not deposited: the KDIS MIML library source (GPL-3.0, github.com/kdis-lab/MIML) |
| `mulan/evaluation/Evaluator.java:210` | not deposited: Mulan 1.5 source, mulan-1-5-0-sources.jar shipped with the KDIS library |

**Running the deposited tests.** From `amendments/A1/code/`, with Python 3, numpy, scipy, scikit-learn and pytest:
`python -m pytest tests -q`. Every test in `tests/test_tie_neutral.py` and `tests/test_deposit_check.py` runs standalone,
except two that check the authors' live plan and amendment files and skip themselves when those files are absent.

Source repository commit for v1.1: 9542b495430d1c7063efdb7307e028b075777158 (the authors' working repository, which is not public; available to the
editor on request).

Redactions in v1.1 (lines that name another manuscript by the same authors):
- `amendments/A1/project_reference/DECISIONS.md`: 2 line(s)
- `amendments/A1/reviews/A1__review_10.md`: 1 line(s)
- `amendments/A1/reviews/A1__review_9.md`: 1 line(s)
