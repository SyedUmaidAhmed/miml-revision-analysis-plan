# Amendments to the deposited analysis plan (PREREGISTERED.md)

Deposited plan: `https://doi.org/10.5281/zenodo.23341630` (2026-10-13), commit `17f14ec` of github.com/SyedUmaidAhmed/miml-revision-analysis-plan. **The deposited text is not edited.** Each amendment below is dated, and states the defect, the corrected rule, the alternatives considered, and what had been observed when it was written.

Under §1.8 the archived copy governs. An analysis amendment therefore takes effect only once it is itself deposited, as a new version of the same Zenodo record with its own DOI. This is enforced mechanically by `deposit_check.deposit_recorded()`, the single real-data guard of every revision tool (`deposit_check.amendment_status`; tests in `tests/test_deposit_check.py`). The rules:
- **Analysis amendments** are headed exactly `## A<n> (YYYY-MM-DD)` (n = 1, 2, … without a leading zero; the date is the day the amendment was written, is mandatory, and must be a real calendar date between 2026-10-13 and the day of the check; the heading may continue after a space or colon). Each carries exactly one line beginning `**Deposited:**`, in the form `**Deposited:** https://doi.org/<DOI> (YYYY-MM-DD)`. That line must match the same grammar as plan line 8. Its DOI must differ, compared case-insensitively, from the plan's and from every other A section's (each deposit is a new Zenodo version with its own DOI, so a line copied from another section does not count). Its date must be no earlier than the plan's and no earlier than the section's own heading date.
- **Cap and budget decisions** are headed exactly `## E<n> (YYYY-MM-DD)`, with the same date rule. The plan sends three kinds of decision to "a dated AMENDMENT": §6.7 budget extensions (lines 243 and 544), and §6.5 cap approvals, including the choice of the pre-registered VOC2012 reduced grid (line 525, the grid fixed at line 524). These change no analysis rule, so they need no deposit, and the §6.7 continuation rule (line 546) is unaffected (DECISIONS.md, "Budget extensions in AMENDMENT.md"). **An E section may contain only:** the unit, its projection, the hours used, the hours requested or the pre-registered option chosen, and the DECISIONS.md row that records the user's decision. Anything else is an analysis amendment and must be an A section. This content limit is a rule for whoever writes the section. The guard does not check content; it checks only the structure described next.
- **Fail closed.** The guard stays closed on any of the following:
  - a code fence, an HTML comment, or a pre or heading tag anywhere in the file;
  - a line that starts an HTML block (a tag at the start of a line, also inside a blockquote);
  - any other heading-like line after the title, including one inside a blockquote or list item, or behind indentation;
  - a setext heading, also inside a blockquote or list item;
  - a duplicated section;
  - a heading date that is not a real date in range;
  - a `**Deposited:**` line outside an A section;
  - a missing required section (`deposit_check.REQUIRED_SECTIONS`, currently {A1}; each committed amendment is added).

  None of these constructs is used in this file, so nothing can be hidden in them. The guard is not a Markdown renderer. It checks only this structure: the A and E headings, their dates, and the deposit lines.

**Reading note.** In the deposited plan, the bare "`AMENDMENT.md`" at lines 336, 503 and 557 ("R2, from AMENDMENT.md") means `experiments/miml_pfn/AMENDMENT.md`, the August amendment. The "dated `AMENDMENT.md` in `experiments/revision_r1/`" at line 544 means this file. So does "a dated AMENDMENT" at lines 243 (§6.7) and 525 (§6.5 cap approvals).

---

## A1 (2026-10-13): ranking metrics are computed tie-neutral

**Deposited:** pending (Zenodo version v1.1 of record 23341630)

**Decided by:** the user (2026-10-13), choosing the orchestrator's recommended option out of three. DECISIONS.md row "A1 tie-neutral ranking metrics".

**Deposited text this amendment supersedes:**
- §1.3, library procedure (plan line 102): "all candidates scored by `miml_metrics.py` on dumped predictions".
- §1.3, degenerate labels (line 115): "The metric conventions of `miml_metrics.py` … apply identically to every method".
- §1.5 (line 134): "Every number is computed by … `miml_metrics.py` from stored per-bag predictions".
- §6.8, T03-b (line 563): "Primary scoring stays `miml_metrics.py` on the dumped predictions".
- H5, theory note (line 418): "our ranking-loss metric (`sklearn.metrics.label_ranking_loss`)". Under A1, H5's ranking loss is the tie-neutral version of that function. The two are identical on tie-free rows, and both are normalised, so the argument made there is unchanged.
- §1.5 fallback (line 157), which would make a harness's native scoring primary if it could not dump per-bag scores. **Not triggered:** T03-b, T03-c and T03-f show that PredictDump and the Octave driver dump scores. If it were ever triggered, the affected harness would be reported on its native rule, as a separate comparator, and never mixed with tie-neutral scores.
- §1.8, as described above: A1 governs only from its deposit.

**Defect, found by T03-b (§6.8) on 2026-10-13:**
- `miml_metrics.py` has no single rule for tied scores:
  - OneError takes `np.argmax`, so the first tied label wins.
  - Coverage and AveragePrecision take `np.argsort`, whose order within ties depends on the implementation.
  - RankingLoss is `sklearn.metrics.label_ranking_loss`, which counts every tied relevant–irrelevant pair as a full error.
- Several KDIS baselines output heavily tied scores. On the T03-b fold (Letter Frost, 5×5 repeat 0, fold 0, AveH, k = 10), the number of distinct score values is: MIMLkNN 2 (exactly {0, 1}), MIMLBagging 5, MIMLBRkNN 11, MIMLMAPkNN 115, MIMLDGC 373, DMIMLkNN 460, MIMLIBLR 613. For tie-heavy methods, the deposited rule's value is therefore decided largely by how ties are handled.
- **The direction of the defect is metric-specific** (`../../revision_access_44676/evidence/T03__checks/diagnosis/tie_neutral_on_letter_frost_f0.txt`):
  - **RankingLoss:** the deposited rule is never lower than the tie-neutral value and is systematically higher on tied outputs. MIMLkNN: 0.659 deposited vs 0.335 tie-neutral (0.371 under Mulan's rule). MIMLBagging: 0.492 vs 0.299. MIMLBRkNN: 0.198 vs 0.154. This favours a method with untied scores against tie-heavy baselines.
  - **OneError, Coverage, AveragePrecision:** the deposited value depends on label index order, and its direction varies by method. Tie-neutral is worse than deposited for OneError on MIMLkNN (0.276 → 0.285), MIMLBRkNN (0.138 → 0.172) and MIMLIBLR (0.724 → 0.791). It is better for OneError on MIMLBagging (0.517 → 0.505). OneError is unchanged for DMIMLkNN, MIMLMAPkNN and MIMLDGC. AveragePrecision is worse under tie-neutral for MIMLBRkNN (0.695 → 0.689), MIMLBagging (0.474 → 0.455) and, marginally, MIMLDGC (−1.3e-4), and better for MIMLkNN (0.484 → 0.507), MIMLIBLR (0.315 → 0.321) and, marginally, DMIMLkNN and MIMLMAPkNN (+5.5e-5 each). Coverage improves for all 7 on this fold.
  - In short, the deposited rule is biased on RankingLoss and arbitrary on the other three ranking metrics.
- **TabPFN and logreg** output probabilities, but they can still tie: labels predicted constant under §1.3 F4, and saturated logreg probabilities. How often that happens has not been measured. For every arm, the share of test bags whose scores contain a tie involving a relevant label is reported with the results.

**Corrected rule (binding for every analysis from its deposit on):**
1. **OneError, Coverage, RankingLoss and AveragePrecision** are computed as the **exact expected value of the `miml_metrics.py` metric when tied scores are ordered uniformly at random**.
   - A tie means exact float64 equality. Scores are cast to float64 first; float32 outputs (TabPFN, the H5 models) are cast exactly, so a float64 tie is a float32 tie.
   - Ties are judged on the scores exactly as scored, i.e. after the §1.3 F4 degenerate-label overwrite.
   - Implementation: `tie_neutral_metrics.py::ranking_four`. The closed forms are in its docstring. Tests (`tests/test_tie_neutral.py`) check them against brute-force enumeration of every tie order to within 1e-12, and against `miml_metrics.py` on tie-free scores.
   - Every other convention of `miml_metrics.py` is kept, including the edge cases. OneError, Coverage and AveragePrecision skip bags with no relevant label. RankingLoss gives 0 to a bag with no relevant or no irrelevant label. With no relevant label in any bag, Coverage is −1.0 and the others 0.0. Fewer than 2 labels raise an error.
2. **HammingLoss is unchanged:** the native bipartition for KDIS and MIMLNN, and `optimize_thresholds` thresholds tuned on `val_i` for TabPFN, logreg and the H5 models.
3. The rule applies to **every** method and arm (KDIS, MIMLNN, TabPFN, logreg, H5), to **inner selection** (§1.3) as well as outer test scores, and to every hypothesis (H1–H5) and to §1.9. Both sides of every contrast use the same rule.
4. **Sensitivity rows.** Each is reported alongside every primary ranking-metric result, applied to both sides of every contrast, and recomputed from the stored predictions. Each row reports the §1.6 statistic and the unadjusted p. Holm is applied over each sensitivity row's own p-values, family by family, with the same m as the corresponding primary family; primary p-values are never adjusted by them. Each row also reports the §1.6 confirmatory global Wilcoxon (plan line 191). **The rows are descriptive and change no verdict.**
   - **(a) Deposited pipeline.** The plan as deposited, end to end. Inner selection is redone with the deposited scorer on the stored inner predictions (`library_harness.score_prereg`), and the outer test is scored with the deposited scorer (`score_prereg` for the library; `metrics_prereg` for TabPFN and logreg units). Where the re-selected winner differs from the A1 winner, that candidate is refit on the outer training fold and scored. The row lists every (fold, metric) whose selection differs. **Approved by the user on 2026-10-14** (DECISIONS.md, "Sensitivity rows (a)-(c)").
     - **Budget and schedule:** these refits are real-data library runs. They are charged to the library budget (§6.7) and projected as a separate term in `PROJECTIONS.md`, bounded as in §6.3 (the 5 largest measured candidate refit times per method). They run **after every primary library unit of the C queue** (after the last library position of the §6.7 execution order). **While any primary library unit is held, or is awaiting a user decision under §6.7, no row-(a) refit starts**, even though §6.7's continuation rule (plan line 546) lets independent units continue. A refit therefore never spends library budget that a held primary unit could still need, and it can never hold, delay or reorder a primary unit. They fall under the §6.7 stop rule like any unit. A refit that is held or fails is reported as "row (a): selection differs, refit held/failed [reason]", with no imputation.
     - **H5:** measurement (c) of H5 (plan line 410) scores the exact metric at every epoch. The H5 runner therefore stores the per-epoch outer-test score matrices, so that the rows can be recomputed from stored predictions.
     - **Gate:** the row-(a) analysis code (re-selection, the selection-differs bookkeeping, the conditional refits) is written and code-reviewed **before the first library unit of the C queue runs**, not merely before the first analysis that reports it. The gate and the H5 storage requirement are tracked as their own task, with a review gate, in `../../revision_access_44676/tasks/TNEW-sensitivity-rows.md` and in the LEDGER.
   - **(b) Mulan convention.** Mulan 1.5's own rule (`tie_neutral_metrics.ranking_four_mulan`, which reproduces Mulan's in-process measures to ≤ 1.1e-16 on all 7 KDIS methods of the T03-b fold), on the A1-selected candidates.
   - **(c) Hybrid, labelled as such.** The A1-selected candidates scored with the deposited scorer, with no re-selection. This isolates the scorer's effect from the selection's.
5. **Unchanged, and on the deposited scorer:**
   - the §6.8 checks (`t03_checks.py` calls `score_prereg`);
   - any comparison against a stored number produced by the deposited scorer, which includes T03-g and the §6.9 cross-device check: new G runs against the stored MPS results, compared on `metrics_prereg`.
   - Platform caveat: the deposited scorer's tie order comes from `np.argsort` (default kind), which can differ between numpy builds and CPUs. For §6.9 and for rows (a) and (c), both sides are therefore recomputed with the deposited scorer **on one machine from the stored npz files**, with the numpy version recorded. §6.9 is also reported on the tie-neutral metrics, which do not depend on order.
   - Analysis scripts read `metrics` (or `library_harness.score`) for primary rows, and `metrics_prereg` / `score_prereg` only for sensitivity rows (a) and (c) and for the comparisons listed here.

**Alternatives considered:**
- **Keep the deposited rule**, adding tie-neutral as a non-pre-registered sensitivity analysis. Rejected: the primary ranking-loss results would then carry a known bias against tie-heavy baselines.
- **Adopt Mulan's convention** (the rule behind every submitted KDIS number). Rejected: it also breaks ties by label index, so it is arbitrary in the same way. It remains a sensitivity row (b).
- **Tie-neutral (chosen).** It does not depend on label order, it equals the deposited value on tie-free outputs, and it treats every method identically.

**What had been observed when A1 was written:**
- **No outcome under the revision protocol existed.** No production run, pilot or H1–H5 comparison had produced a number.
- **Before the decision, the following had been seen:**
  - The §6.8 check outputs: T03-a to T03-f on Letter Frost (library methods only, one fold for T03-a and T03-b, five folds of MIMLNN for T03-c), and T03-g, the stored Scene logreg row.
  - The three-rule table for the 7 KDIS methods on the T03-b fold (deposited / Mulan / tie-neutral; the evidence file above).
  - The submitted manuscript's method-versus-library comparisons, tabulated in the plan at §7 Part B. Those used a different protocol: a single 10-fold or 5-fold split, a test-selected comparator, KDIS scored by Mulan's rule, and MIMLNN by the authors' code.
- **An accidental real-data run, before A1 was deposited.** While mutation-testing the guard for A1 review 2, the reviewer agent disabled the guard in memory. A refusal test then started a real Letter Frost nested-library run (2026-10-13, 14:14–14:54 UTC), which the reviewer killed. Its outputs (2 639 files) were moved unopened, on the user's decision, to `quarantine/2026-10-13_accidental_letter_frost_run/` with a sha256 manifest. Nobody has read them, no analysis uses them, and production reruns Letter Frost from scratch. **Test-suite fail-safe** (`tests/conftest.py`, `tests/test_failsafe.py`): during every test, a Python audit hook refuses any file open under the protected locations. It also refuses any subprocess, `os.system`, exec or spawn call whose working directory is there, or one of whose arguments points there, read as text or resolved against the working directory with symlinks followed. It does not follow into child processes: a child is refused only through what its command names.
  - Those locations are the raw data directories (the default one, and any configured through `MIML_DATA_DIR` or `set_data_dir`, including one configured during the test), the generated fold files, the production output tree `results/revision_r1/`, and `quarantine/`.
  - Write-mode opens under the tracked evidence tree are refused too.
  - Paths are compared case-insensitively, as macOS resolves them.
  - Every `loadmat` binding is also wrapped.
  - The one exception is a test marked `synthetic_data_dir`, which points the data directory at synthetic files it wrote itself; the static locations stay protected even then.
  - This protects these locations against the test suite. It is not a guarantee about code run outside the tests, which the deposit guard covers.
- For 6 of the 7 KDIS methods on the T03-b fold, A1 moves the primary RankingLoss from the deposited value, which is harsh on ties, toward Mulan's, i.e. toward the convention behind the submitted KDIS numbers. MIMLIBLR is the exception: deposited 0.3285, Mulan 0.3425, tie-neutral 0.3259. On OneError and AveragePrecision it moves individual KDIS methods in both directions. The amendment was chosen for its definition (label-order-free, method-agnostic), not by its effect on any comparison. The sensitivity rows in item 4 let a reader see what the deposited rule would have concluded.

**Code:**
- `tie_neutral_metrics.py` (new).
- `library_harness.score` (primary) and `score_prereg` (deposited).
- `tabpfn_arms.py` stores `metrics` (primary) and `metrics_prereg`.
- `run_nested_library.py` records the scorer in `meta.scorer`.
- `deposit_check.py` holds the amendment-deposit guard, which `h2_common.deposit_guard` now also applies.
- Tests:
  - `tests/test_tie_neutral.py`: closed forms, edge cases, and Mulan's 1e-6 first-element grouping (Java-verified vectors);
  - `tests/test_nested_library.py::test_selection_uses_the_tie_neutral_rule`: selection follows A1 where the two rules disagree;
  - `::test_predictdump_reproduces_library_run`: deposited AP and Hamming still equal the library's, and `ranking_four_mulan` equals Mulan's to 1e-12;
  - `tests/test_tabpfn_arms.py::test_unit_stores_tie_neutral_primary_and_prereg_separately`;
  - `tests/test_deposit_check.py`, amendment sections (structure fails closed, E sections, required sections); `tests/test_h2.py::test_deposit_guard_requires_every_amendment`;
  - `tests/conftest.py` + `tests/test_failsafe.py`: the test-suite fail-safe described above, including a re-creation of the accident.
- The analysis code for sensitivity row (a) is gated as stated in item 4(a).

**Also recorded here (no rule change):** T03-b found that the KDIS library's own report, which supplied every KDIS number in the submitted manuscript, scores against corrupted ground truth.
- KDIS `MIMLClassifier.makePrediction` writes 1 into the last label of the instance it is given (`external/MIML/mavenProject/src/main/java/miml/classifiers/miml/MIMLClassifier.java:154`; the method is `final`, so every KDIS MIML classifier does this).
- Mulan 1.5's `Evaluator.prepareMeasures` passes the uncopied test bag 0 to it (`mulan/evaluation/Evaluator.java:210`) before evaluating.
- The harness's `PredictDump` never passes an uncopied instance, so the deposited §1.5 design (scoring from dumped predictions, with the library report as a check only) is unaffected. Its effect on the submitted numbers is quantified in `../../revision_access_44676/tasks/T03-baseline-harness-checks.md`.
