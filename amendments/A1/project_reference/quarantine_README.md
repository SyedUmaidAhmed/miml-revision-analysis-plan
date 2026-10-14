# Quarantine: accidental real-data run, 2026-10-13 (user decision: quarantine unread)

**What happened.** While mutation-testing the real-data guard for review A1-2, the reviewer agent replaced
`library_harness.guard_dataset` / `guard_write` in memory with line-8-only versions. With line 8 open,
`tests/test_nested_library.py::test_real_data_refused_before_deposit` called
`run_nested_library.main(["--dataset", "letter_frost"])` with the default results root and workdir,
which started a real Letter Frost nested-library run (pid 56303, 19:14–19:54 local, 14:14–14:54 UTC), killed by the reviewer.
It happened before A1 was deposited, i.e. before any real-data run was permitted.
Source: `revision_access_44676/reviews/A1__review_2.md`.

**What was done (2026-10-13, by the orchestrator, on the user's decision).** Both output trees were moved here
**without being opened**:
- `results_revision_r1/` (was `results/revision_r1/`: a manifest jsonl, `library/letter_frost__original__main.json` + `.lock`,
  `predictions/letter_frost/original/*` for 8 methods);
- `tmp_nested_library/` (was `$TMPDIR/nested_library/`).

`MANIFEST.sha256` lists every file (2 639) with its sha256, computed after the move. No file's content was read
by the orchestrator or by any analysis; the files are excluded from git (`.gitignore`) and from every results path.
Production reruns Letter Frost from scratch. These files are never an input to any analysis.
