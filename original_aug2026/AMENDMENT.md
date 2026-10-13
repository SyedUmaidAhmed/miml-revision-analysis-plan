# Amendment: the qualifying-set clause is mis-specified

Written 2026-08-15, **while yeast (the deciding dataset) was still running** and
before its result was known. Amends `PREREGISTERED.md`. Decision taken on the
user's instruction to "do what is best".

## The defect

The pre-registered rule requires

> more than 0.006 AP over `tabpfn_bagmean` on **≥ 4 of the datasets where TabPFN
> already wins or ties**

The second clause conditions the qualifying set on how the **baseline** performed
against logistic regression. That is backwards for the hypothesis actually under
test.

The hypothesis is *"bag structure adds signal an in-context learner can use"* —
a claim about `multiview` vs `bagmean`. Whether `bagmean` happened to beat
logistic regression on a dataset is irrelevant to it. The clause was written to
guard against cherry-picking datasets favourable to the foundation-model story,
which was a reasonable worry, but it implements that guard by discarding
exactly the datasets where bag-mean is weakest — i.e. where structure has the
most to add.

The consequence is now concrete: **letter_frost, where multiview posted +0.0812
and converted the baseline's only loss into a win, does not count**, because the
baseline lost there. Four large wins are on the board and only three of them are
admissible.

## What is NOT being done

The rule is **not** being rewritten to admit letter_frost and declare success.
The data has been seen; changing a threshold after seeing it is precisely the
failure mode `../../CLAUDE.md` was written to prevent, and it is how the
previous six years of work went wrong. **The original rule stands and its
verdict is reported as the primary outcome, pass or fail.**

## What is being done instead

Three things, in order.

**1. The original verdict is recorded as primary.** If yeast does not win,
MIML-PFN **failed its pre-registered bar at 3 of 4**, and the write-up says so
in those words. The four wins and their sizes are reported alongside, without
being used to overturn the verdict.

**2. A corrected rule is pre-registered here, and tested only out of sample.**

> **Corrected rule (R2).** `tabpfn_multiview` beats `tabpfn_bagmean` on AP by
> more than 0.006 on a **majority of all datasets run**, with no qualifying-set
> condition, counting ties as non-wins.

R2 is *not* evaluated on the seven datasets already run — those numbers are
known, so R2 would be unfalsifiable on them. It is evaluated on datasets not yet
touched by the multiview arm: **reuters and the four protein sets**. Those five
are held out as a confirmatory sample. R2 is declared before any of them runs.

**Falsification of R2:** if multiview does not win a majority of those five,
the effect does not generalise beyond the low-dimensional benchmarks and the
method is reported as *dataset-dependent*, not general.

**3. Feasibility constraint, stated in advance.** Multiview multiplies feature
count by ~6, putting reuters at 1459 and the proteins at 1297 features. Where
this is computationally infeasible, a **fixed-budget PCA is applied identically
to every arm** (bag-mean and multiview alike) and the reduction is reported.
The comparison stays within-protocol; no arm gets a preprocessing advantage.
`medical` (8695 multiview features) and `corel5k` (2995) are excluded from R2 on
feasibility grounds, stated now rather than after seeing results.

## Why this is the honest resolution

It costs us the clean headline: the primary verdict may be "failed". But it
converts a rule defect discovered mid-experiment into a **stronger** design — a
pre-registered confirmatory test on held-out datasets — instead of a post-hoc
rescue. A reviewer can check that R2 was fixed before its data existed, because
the datasets it applies to had not been run.

If both hold — primary rule fails on a technicality, R2 passes out of sample —
that is reported as exactly that, and the reader is given both.
