# TNEW-sensitivity-rows: analysis code for AMENDMENT A1 sensitivity rows (a)-(c), and H5 storage

Status: **OPEN**. Gate: must be RESOLVED (independent reviewer, "RESOLVED, 100%") **before the first library unit of the C queue runs** (AMENDMENT.md A1 item 4(a)).

## Linked
AMENDMENT.md A1 item 4; DECISIONS.md "Sensitivity rows (a)-(c)" (user, 2026-10-14); reviews A1__review_1 F3, A1__review_2 F3, A1__review_3 F6. Comments: R1-M04, R1-M07, R1-M08, R5-03 (selection protocol), R1-m05 (ties).

## Scope
1. **Row (a), deposited pipeline.**
   - Re-select every (outer fold, metric, procedure) from the stored inner npz files with `library_harness.score_prereg`, using the same tie-break order as §1.3.
   - List every cell whose winner differs from the A1 winner.
   - Refit the changed winners on the outer training fold. These refits are a separate term in `PROJECTIONS.md`, run after every primary library unit of the C queue and never start while a primary library unit is held or awaiting a user decision (DECISIONS.md 2026-10-14, "Row-(a) refits wait for held primaries"), are charged to the library budget, and fall under the §6.7 stop rule. A held or failed refit is reported as such.
   - Score the outer test with `score_prereg` (library) or `metrics_prereg` (TabPFN/logreg).
   - For every family: the §1.6 statistic, the unadjusted p, Holm over the row's own p-values with the primary family's m, and the global Wilcoxon (plan line 191).
2. **Row (b), Mulan convention:** `tie_neutral_metrics.ranking_four_mulan` on the A1-selected candidates, applied to both sides of every contrast.
3. **Row (c), hybrid:** the A1-selected candidates scored with the deposited scorer.
4. **Platform:** both sides of rows (a)/(c) and of §6.9 are recomputed with the deposited scorer on one machine from the stored npz files, with the numpy version recorded. §6.9 is also reported on the tie-neutral metrics.
5. **H5 storage:** the H5 runner stores per-epoch outer-test score matrices, so that measurement (c) (plan line 410) and the sensitivity rows can be recomputed from stored predictions.
6. **Tie prevalence:** for every arm, the share of test bags whose scores contain a tie involving a relevant label (A1, defect section).

## Review log
| round | reviewer file | verdict |
|---|---|---|
