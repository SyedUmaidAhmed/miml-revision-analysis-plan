# MIML-PFN — does bag structure help an in-context tabular foundation model?

Pre-registration, written 2026-08-14 **before any multiview number exists**.
Candidate A in `../../method/00_CANDIDATE_TECHNIQUES.md`.

## The observation this is built on

A zero-training tabular foundation model on **bag-mean** features — no
multi-instance information whatsoever — already beats the published MIML
literature on two of four datasets measured so far:

| dataset | best logreg AP | TabPFN bag-mean AP | published range |
|---|---|---|---|
| scene | 0.7484 | **0.8098** | .738–.772 (7 methods) |
| mscv2 | 0.7229 | **0.8013** | — |
| letter_carroll | 0.6587 | 0.6580 | — |
| letter_frost | 0.6881 | 0.6720 | — |

Source: `../../results/foundation_baselines.json`, protocol in
`../foundation_baselines/PREREGISTERED.md`.

## Question

The bag is currently destroyed by averaging. **Does giving the in-context
learner actual multi-instance structure beat destroying it?**

This is the question that decides whether we have a *method* or merely a
*negative result about the subfield*.

## Design, fixed here

`tabpfn_multiview`: each bag becomes one tabular row built from
permutation-invariant statistics over its instances, concatenated:

1. **mean** (the existing baseline, retained as the first block)
2. **max** (classical MIL assumption)
3. **min**
4. **std** across instances (dispersion — how heterogeneous is the bag)
5. **quantiles** at 0.25 / 0.75
6. **bag cardinality** (one scalar)

Feature count grows 6×+1 over bag-mean. Where this exceeds what TabPFN accepts,
the **same** dimensionality reduction is applied to every arm and reported.

Ablation arms, all on identical folds:
- `tabpfn_bagmean` — already run (baseline)
- `tabpfn_bagmax` — isolates whether max alone explains any gain
- `tabpfn_multiview` — the proposed method

## Decision rule, fixed here

**MIML-PFN is judged a real method** if `tabpfn_multiview` beats
`tabpfn_bagmean` on Average Precision by **more than 0.006** (the measured
across-seed sd on Scene) on **≥ 4 of the datasets where TabPFN already wins or
ties**, and does not *lose* by more than 0.006 on more datasets than it wins.

**Falsification condition.** If multiview does **not** clear that bar, then bag
structure adds nothing recoverable this way. In that case:

- the "MIML" part of MIML-PFN is empty and **the method is abandoned**, not
  rescued by adding blocks until it wins;
- the finding is written up as what it actually is — *a tabular foundation
  model on bag means beats twenty years of MIML methods, and the
  multi-instance structure those methods model is not what produces the gain* —
  which is a negative result about the subfield, and is reported as such.

Either outcome is written. Neither is softened.

## Anti-fishing rules

- The feature set above is fixed. No statistic is added after seeing a result.
- Every dataset that runs is reported, including losses.
- No dataset is dropped post hoc; a technical failure is reported as a failure.
- The comparison is TabPFN-vs-TabPFN on identical folds, so ensembling,
  preprocessing and fold construction cannot confound it (`../../CLAUDE.md`
  lesson 3).
- Comparisons to *published* numbers remain indicative only: our folds are the
  10CV.mat splits, not the papers' 30 random splits. This caveat is carried into
  every write-up.

## Known threats, stated in advance

- TabPFN v2.2.1, not the license-gated v8.2.0. Reviewers may ask for current.
- The gain so far is concentrated on larger datasets; TabPFN loses on
  letter_frost (144 bags). Multiview raises feature count, which may worsen the
  small-data arms. **This is expected and will be reported, not hidden.**
- Bag-mean already implicitly encodes cardinality-weighted content; some
  multiview statistics are correlated with it. Correlated features can hurt
  in-context learners, so a null result is a live possibility.
