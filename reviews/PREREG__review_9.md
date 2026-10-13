# Review 9 of `experiments/revision_r1/PREREGISTERED.md` (v3 after the round-8 fixes; git `86e0988`, 836 lines, working tree identical to HEAD)

Reviewer role: independent statistician (cross-validation inference, multiple testing, compute protocols on shared hardware) and MIML practitioner; did not write v1–v3 or reviews 1–8. Date: 2026-10-13.

Scope, as set by the task: verify against `git diff 155e4e2 -- experiments/revision_r1/PREREGISTERED.md` that only the round-8 fixes, the splice-artefact fix and the round-8 response table changed, and that each fix is exact; then a whole-document readiness check for public deposit as the binding analysis plan: (a) path uniqueness under every branch (G available; global MPS fallback; each §6.4 PCA outcome), (b) every procedure executable without post-data judgement, (c) consistency with every row of `revision_access_44676/DECISIONS.md`, (d) no internal contradictions. Only issues that cause a wrong result, an unexecutable step, a reviewer objection or a contradiction count as findings.

## Part 1 — The round-8 fixes, verified against the diff

`git diff --stat 155e4e2` touches only this document (+27/−7) and `PREREG__review_8.md`. `git status` is clean. `DECISIONS.md`, `power_table.py` and `T05__power_table.txt` are untouched; no number in §7 moved.

| hunk | what changed | matches review 8? |
|---|---|---|
| Header, History and Version-control rows | Extended through review 8 and commit `155e4e2` | N2: exact |
| §1.5 `<config>` line | Adds "an arm for which the PCA switch is a no-op (d ≤ 500) carries `native`" and "For logreg arms `<config>` is `default` (`LogisticRegression(max_iter=1000)`, no tuned quantity)" | F2 and N1: exact; the logreg constructor matches `run_foundation_baselines.py:103` as review 8 recorded it |
| §1.5 reuse list | New lead bullet defining `<dev>` = `g`, or `mps` under the §6.1 fallback; the Yeast and Scene bullets now carry `main+<dev>`; new bullet: under the fallback §6.9's Letter Frost `tabpfn_bagmean` unit is `letter_frost/submitted5/tabpfn_bagmean/native/main+mps`, which is the T03-g unit, reused, and §6.9 is then reported as a same-device environment check, not a cross-device check; the §5 tokens become `verify-2fit` / `verify-1fit` "each with the device token of §6.1" | F1: the collision is declared as one reused unit and the reporting under that branch is fixed. Review 8 suggested also a clause in §6.9; the plan put the whole statement in §1.5 and left §6.9 unchanged. That is sufficient: §6.1 row 1 already lists the cross-device check among the arms the global switch moves to MPS, so §6.9's "on G" resolves to MPS under the fallback by the same rule every other "on G" in the document uses, and the no-overwrite writer plus the §1.5 reuse rule give one executable path. No contradiction between §6.9 and the new bullet |
| §1.5, after the reuse list | "All stored predictions are released (R2-08 item 9)" moved out of the §5 bullet onto its own line | The splice-artefact fix; the sentence now scopes every unit, which is what R2-08 item 9 asked for |
| Round-7 response table, N3 row | Wording generalised to the device-token phrasing | Consistent with the §1.5 text |
| Appended round-8 response table | F1, F2, N1, N2 | Each row describes exactly what its hunk does |

No other line changed.

## Part 2 — Readiness checks

### (a) Path uniqueness under every branch

Path: `<dataset>/<version>/<arm>/<config>/<condition>/r<repeat>_f<fold>[_i<inner>].npz`; `W` ∈ {native, pca500}, `D` ∈ {g, mps}. I re-ran review 8's enumeration with the two round-8 changes (logreg `<config>` = `default`; every TabPFN `D` = `mps` under the fallback), under both PCA outcomes per dataset.

- **Logreg units** (the newly defined slot): §1.9 `<ds>/rcv10/logreg_{bagmean,multiview}/default/main/r<r>_f<k>`; H2-B `<ds>/purged/logreg_*/default/{leak,control-s<j>}/r0_f<k>`; T03-g `scene/original/logreg_bagmean/default/main/r0_f<k>`. Logreg is in no H1, H3 or H4 arm, so no logreg unit shares dataset, version and condition with another. Distinct.
- **G branch:** identical to review 8's table; every pair resolves, and the declared reuses (H3 ↔ H1-leaky Yeast at coinciding width; §6.9 Scene ↔ H1; H4 f = 1.0 ↔ H1; library re-selections ↔ stored candidates) each name a fit that is the computation the consuming procedure requires (same split, `tr` order, z-scoring, width, device, fit count).
- **Fallback branch (every TabPFN unit `+mps`):** the three collapses that the device token no longer separates are all declared reuses: §1.9's sixth run = H1 `main+mps` (identical computation: canonical split, the dataset's §6.4 width, MPS); §6.9 Scene = H1 Scene = §1.9's sixth Scene run (a triple reuse, consistent); §6.9 Letter Frost bag-mean = T03-g (identical: `submitted5`, native, recreated `tabpfn_env`, pinned settings, MPS). §6.9's Letter Frost multiview is `letter_frost/submitted5/tabpfn_multiview/native/main+mps`, which nothing else writes. §5's `verify-*+mps` units are distinct by token from T03-g's `main+mps` unit on the same data, and are deliberately kept rather than reused (round-7 N3), so no overwrite is attempted.
- **PCA outcomes:** the width decision is per dataset and inherited by every non-H1 arm, so any two units sharing dataset, version, arm, condition and device share `W`, except the one H3 Yeast pair that `W` now separates. Letter Frost (d = 16) and Scene (d = 15) cannot trigger, so every T03-g, §5 and §6.9 unit is `native` in both branches; the no-op convention of round 8 makes the token deterministic for every arm.

No pair collides without a declared reuse, in any branch.

### (b) Executability without post-data judgement

Every data-dependent switch is a fixed rule on a pre-stated quantity: §6.4 (projections only), §1.9 gates and §6.5–§6.7 (projections and measured hours, through the stop rule and a dated AMENDMENT), §6.6 limits, T03-a/f, §5 (1e-9, fit count), T03-g and §6.9 (1e-3, labelling), H2-B "not estimable" (80 %), the H4 gate (CI above 0), Wilcoxon ties (run as written, count reported), H3 outcomes (b)/(b′)/(b″), G1–G3. Seeds are enumerated for every stochastic step (§1.2, §1.3, §1.9, H2-B, H4, H5, §7 D, T03-f). The §1.5 reuse rule removes the last place where a writer could refuse a path. Nothing requires choosing a configuration, a row set or a test after a number is seen.

### (c) `DECISIONS.md`, every row

| row | plan |
|---|---|
| 2026-10-12 rebuild leak-free, rerun every arm | H2-A; §6.10 |
| run ALL missing arms; nothing descoped | H1 covers proteins, multiview Reuters and Yeast (H3 leaky, H1 rebuilt), Medical, Corel5K, rebuilt sets; §6.7 stop rule replaces every drop rule |
| Corel5K through every arm | H1 rebuilt, leaky column, H2-B, H4 |
| GPU arms wait for credits; local work first | §6.0 two queues; C queue first; fallback serialises C first |
| release bundle to GitHub and Zenodo | §1.8 (public GitHub archived to Zenodo, or OSF) |
| no second foundation model | none in the plan |
| process: independent reviewer "RESOLVED, 100%" | this review series |
| contribution 1 = provenance audit; four sets built by us; leak-free rebuild as correct protocol; negative controls; no "field's suite" claim | §0.1 groups (6 + 4 + 3 = 13; 7 + 4 + 4 + 1 = 16), §0.2, H1 "leaky (constructed by the authors)", H2 interpretation (F15) |
| [row redacted from the public copy: a decision about a different manuscript, outside the scope of this plan] | — |
| 2026-10-12 orchestrator H1 labelling (seen = EXPLORATORY) | superseded; the plan cites the amending row |
| R5-S full concession | not a prereg matter |
| 2026-10-13 user: all CONFIRMATORY, "direction previously observed", sensitivity on never-run sets | Labels header; §1.6 F-H1 (m = 16, 8 qualified rows) and F-H1-newdata (m = 10); H1; §7 |
| 2026-10-13 clarification: m = 16 membership; leaky originals in no family; m = 10 membership | §1.6 lists the same 16 and 10; leaky originals EXPLORATORY, no family |
| 2026-10-13 budget overruns: stop, record, AMENDMENT; priority list = execution order only | §6.5, §6.6, §6.7, §1.9, H3 |
| [row redacted from the public copy: a decision about a different manuscript, outside the scope of this plan] | — |

No contradiction with any row.

### (d) Internal consistency

Cross-checked: the 8 "direction previously observed" rows (header, §1.6, H1, §7 B) agree; the 16/10 family memberships agree across §1.6, H1, §6.7 and §7; §0.1/§0.2 counts and n mod 10 values are arithmetically right; the §7 numbers quoted in §1.1, §1.2, §1.6 and the §7 interpretation (1.80 → 1.95; 4.56 → 1.95; 9–12 %; 0.25–0.37; 0.17–0.26; 18–29 %) match `T05__power_table.txt` (1.803, 1.954, 4.556, 0.120/0.087, 0.245/0.365, 0.167/0.263, 0.175/0.285); H4's 10 variable-cardinality rows are the right 10; H2-A's inner pools give 2, 2, 2, 2, 1; §7 C's f = 0.864 and 0.691 follow from e = 0.136. The three August sha256 values in the header reproduce on disk; every file in the §1.8 deposit list exists; the stored rows that T03-g, §5 and §6.9 reproduce exist in `results/foundation_baselines.json` at the fold counts the plan assumes (Letter Frost at 5, Scene and Yeast at 10).

## Part 3 — Findings

None.

## Notes (no action required; none changes an experiment, a statistic or an executable path)

- **N1.** Under the fallback, §6.9's outcome clause ("the manuscript reports the device of every row") is vacuous, since every row is MPS; the informative action is T03-g's fail wording (label stored rows by environment). No test in the plan mixes a stored August row with a new row (H3 Birds is stored-vs-stored; H3 Yeast and §1.9 are new-vs-new; the "as submitted" column is supplementary), so the clause can affect a label only, never a number. A one-line cross-reference from §6.9 to the §1.5 bullet would help a reader of §6.9 alone.
- **N2.** H5 has no position in the §6.7 execution order, and under the fallback T03-g's TabPFN part has no stated position in the G queue beyond "before §6.9". Neither can change a result: H5 has its own total budget and feeds nothing else; T03-g is deterministic (`random_state = 0`) and outside the budgets; and the stop rule pauses rather than drops, so order never decides which units are reported. Within-position order is likewise unspecified for every other position.
- **N3.** §1.4 says the H5 neural models z-score "bag-level features"; H5 specifies instance-level z-scoring for ABMIL (bag-mean level for the MLP). H5's statement is the operative one and the two are not in tension once read together.
- **N4.** §1.5's round-6 sentence ("the T03-g (MPS) and §6.9 (G) runs never share a path") is a G-branch statement, marked as such by its device parentheticals; the round-8 bullet governs the fallback branch.
- **N5.** §6.4's trigger reads "any H1 version of a dataset". For the constructed sets this is the rebuilt version; the leaky original has the same d and n to within the remainder rows, so the two projections cannot fall on opposite sides of 72 h in practice, and §6.3 pilots both versions regardless.
- **N6.** Reviews 5–8's remaining notes stand; nothing in the round-8 fixes touched them.

## Summary

The round-8 fixes are exactly the ones requested, placed in §1.5 with §6.9 unchanged, and nothing else moved since `155e4e2`. With the width token, the device token, the `default` logreg token and the five declared reuses, the path enumeration resolves every unit under both device branches and both PCA outcomes. Every procedure runs on pre-stated rules; the plan agrees with every row of `DECISIONS.md`; the numbers it quotes reproduce from the deposited power table and the header hashes reproduce from disk. The document is ready to deposit as the binding analysis plan.

MAJOR: none. MINOR: none.

VERDICT: RESOLVED, 100%
