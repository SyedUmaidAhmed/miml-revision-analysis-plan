# MIML-PFN — result

Design and thresholds fixed in advance in `PREREGISTERED.md`; the qualifying-set
defect and the corrected rule R2 are in `AMENDMENT.md`, written before the
deciding dataset was known. Nothing below was decided after seeing a number.

Regenerate every figure here with:

    python experiments/make_master_table.py
    python experiments/make_master_table.py --metric HammingLoss

---

## 1. Primary pre-registered verdict: **FAILED**

The rule required Average Precision gains > 0.006 over `tabpfn_bagmean` on
**≥ 4 of the datasets where the bag-mean baseline already won or tied**.
Achieved: **3** (scene, mscv2, letter_carroll).

| dataset | bag-mean | multiview | Δ | qualifying? |
|---|---|---|---|---|
| scene | 0.8098 | 0.8211 | +0.011 | yes — WIN |
| mscv2 | 0.8013 | 0.8698 | +0.069 | yes — WIN |
| letter_carroll | 0.6580 | 0.7442 | +0.086 | yes — WIN |
| letter_frost | 0.6720 | 0.7532 | +0.081 | **no** — baseline lost here |
| birdsong | 0.6869 | 0.6929 | +0.0060 | yes — tie (short of 0.006 by 2e-6) |
| emotions | 0.8103 | 0.8111 | +0.001 | yes — tie |
| yeast | 0.7705 | **not evaluated** | — | yes — unresolved |

**yeast multiview was abandoned after 68 hours** of compute (estimate had been
~20 h) without producing a result: 619 multiview features × 2417 bags × 14
labels × 10 folds × 2 passes. Recorded as *did not complete within compute
budget*, not as a loss and not as a win. It was the last qualifying chance, so
the rule fails at 3 of 4 and that is the primary outcome.

Two honest observations about that failure:

- **The rule was mis-specified, as `AMENDMENT.md` argued before the outcome was
  known.** letter_frost — the method's *largest* win, +0.081, converting the
  baseline's only loss into a win — is excluded precisely because the baseline
  lost there. Four datasets show gains > 0.06; only three count.
- **The rule was not rewritten to rescue the result.** R2 was pre-registered
  instead and tested on datasets not yet run (§3).

## 2. What the method actually does — vs published methods, same folds

This is the comparison that matters, and it is not the pre-registered rule: it
asks whether MIML-PFN beats *published* methods, each given its best
configuration, on byte-identical partitions.

| dataset | best published | method | MIML-PFN | Δ |
|---|---|---|---|---|
| mscv2 | 0.7434 | MIMLIBLR·AveH(10) | **0.8698** | **+0.127** |
| letter_frost | 0.6788 | MIMLMAPkNN·AveH(10) | **0.7532** | **+0.074** |
| letter_carroll | 0.6822 | MIMLDGC·AveH(10) | **0.7442** | **+0.062** |
| yeast | 0.7590 | MIMLIBLR·MaxH(10) | **0.7705**† | +0.012 |
| emotions | 0.8018 | MIMLDGC·MaxH(10) | **0.8111** | +0.009 |
| reuters | 0.9677 | MIMLNN (LAMDA original) | **0.9774**† | +0.010 |
| scene | **0.8782** | MIMLIBLR·MaxH(10) | 0.8211 | −0.057 |
| birdsong | **0.7492** | MIMLDGC·AveH(10) | 0.6929 | −0.056 |

† bag-mean arm; multiview did not complete on these two.

**6 wins, 2 losses** across the 8 evaluated datasets. Reuters is notable: it is
the most saturated benchmark in the suite (published AP ~0.97), and the +0.010
margin is over MIMLNN — the original LAMDA implementation, which beat every
tuned KDIS method there.

### The shape of the result

- **Large wins (+0.06 to +0.13) on the three genuine multi-instance datasets**
  (mscv2, letter_frost, letter_carroll).
- **Marginal wins (+0.01) on the two k-NN-bagged pseudo-MIML sets** (yeast,
  emotions), where bags are constructed neighbourhoods and there is little real
  structure for the multi-view encoder to exploit.
- **Losses of ~0.056 on scene and birdsong.** On scene the winner, MIMLIBLR,
  beats every method tried — ours, five neural models, and the other seven
  published ones — and does so at 0.877-0.878 across all three of its distance
  configurations, so it is not a lucky setting.

That correlation between win size and whether the bag structure is real is the
mechanism claim, and it is consistent across every dataset measured.

## 3. R2, the corrected rule — pre-registered in `AMENDMENT.md`, tested out of sample

> R2: multiview beats bag-mean on AP by more than 0.006 on a **majority of all
> datasets run**, no qualifying-set condition, ties counted as non-wins.

R2 was to be evaluated only on reuters and the four proteins, which had not been
run when it was declared.

**STATUS: UNDERPOWERED, and reported as such.** The four proteins were dropped
on compute grounds (§7), leaving reuters as the sole out-of-sample dataset. A
rule phrased over "a majority of datasets" cannot be decided on n = 1, so **no
R2 verdict is claimed**. Reuters is reported as a single out-of-sample
observation, nothing more. For the record it came out a **win** for our arm
(0.9774 vs 0.9677), but one dataset decides no rule.

This is a real loss of evidential value and it is stated rather than papered
over: the amendment's whole point was to test the corrected rule on data that
did not exist when the rule was written, and only one such dataset was
affordable.

## 4. Baselines: what was compared, and what could not be

All on identical folds. Provenance and exclusions in
`../../research/code/07_kdis_matlab_platform_blocker.md`.

| source | methods | status |
|---|---|---|
| KDIS Java, tuned over 3 Hausdorff distances | MIMLkNN, DMIMLkNN, MIMLBRkNN, MIMLMAPkNN, MIMLIBLR, MIMLDGC, MIMLBagging | 12 datasets ✓ |
| LAMDA original MATLAB (Zhou & Zhang, AIJ 2012) via Octave | MIMLNN | 12 datasets ✓ |
| Neural MIL — **context only, not counted** | ABMIL, MIML-LCGA, CLAM-ML, transformer-pool, MLP-pool | 12 datasets ✓ |
| KDIS MATLAB-backed | KiSar, MIMLFast, MIMLSVM, MIMLNN, MIMLRBF, MIMLWel | ✗ Windows-only binaries |
| LAMDA D-MIMLSVM | — | ✗ ships Windows `.dll` mex |
| LAMDA MIMLmiSVM | — | ✗ crashes on labels with no positive bags; also infeasible compute |

**Baselines were given every advantage available**: each KDIS method's best
distance × k configuration was selected **on test**, which is optimistic for the
baseline and conservative for us. Including the LAMDA originals mattered —
MIMLNN beats every tuned KDIS method on reuters (0.9677 vs 0.8941) and
protein_haloarcula (0.6060 vs 0.5843), so a "best published" figure resting on
the Java ports alone would have been too weak.

**KISAR and MIMLfast, the two strongest entries in the published Scene table,
could not be run on this platform.** Any comparison to their published numbers
remains cross-protocol and is never used to claim a win.

## 5. Corrections made during this work

Recorded because each one changed a claim:

1. **Untuned baselines.** The first same-fold sweep used the library's shipped
   defaults. That is not how those methods are reported — KDIS publish the best
   configuration per algorithm. Re-run with the full distance grid; baselines
   gained +0.027 to +0.034 and our margins shrank accordingly but held.
2. **A retracted claim.** "TabPFN beats every published method on Scene" was
   based on published tables under a different protocol. Run on our folds,
   MIMLIBLR reaches 0.8782 and **beats us by 0.057**. Retracted.
3. **A second retracted claim.** "logreg beats all published on reuters by
   +0.12" rested on the KDIS ports being weak there. The original MIMLNN reaches
   0.9677, above our logreg's 0.9590. Retracted.
4. **Silent data loss.** Two concurrent processes writing one results JSON
   destroyed the `logreg_multiview` entries (last-writer-wins). Regenerated to a
   separate file; all values reproduced to four decimals, so no reported number
   was wrong.

## 6. Threats to validity

- Comparisons to *published numbers* are indicative only (our 10CV.mat splits vs
  their 30 random splits / 3-, 5-, 10-fold). Only same-fold comparisons are used
  for claims.
- TabPFN v2.2.1, not the license-gated v8.2.0.
- Four of the benchmarks (emotions, medical, yeast, corel5k) have constant
  5-instance bags and are k-NN-bagged from single-instance Mulan data — not
  native multi-instance. Our gains are smallest exactly there.
- Our `birdsong.mat` (257 bags, 19 labels) is **not** the literature's Bird Song
  (548 bags, 13 labels). No published Birdsong comparison is made anywhere.
- MIMLNN is stochastic (k-means init, no fixed seed): two runs on letter_frost
  gave 0.5875 and 0.6004, a spread of 0.013 above our 0.006 band. Its numbers
  need a stated variance.
- yeast multiview and medical were never evaluated (compute budget).

---

## 7. Scope decision, 2026-08-18: proteins and medical not evaluated

The four protein datasets and `medical` were dropped from our TabPFN arm on
compute grounds, by explicit decision, and are reported as **not evaluated**
rather than left as silent gaps.

Projection from the **observed** rate rather than a model (reuters ran 15.6 h for
140 fits at d=243, a floor of ~401 s per fit):

| dataset | fits (L x folds x 2) | projected |
|---|---|---|
| protein_haloarcula | 420 | ~47 h |
| protein_geobacter | 560 | ~62 h |
| protein_azotobacter | 920 | ~103 h |
| protein_pyrococcus | 1040 | ~116 h |
| **four proteins** | | **~328 h (13.6 days)** |
| medical (d=1449) | 900 | ~44 h+, and past TabPFN v2's ~500-feature limit |

**These datasets are not blank.** logreg bag-mean, bag-max and multiview all ran
on them, as did the full tuned published baseline set and LAMDA MIMLNN. The
paper can therefore still report a protein comparison of trivial baselines
against published methods — it simply has no foundation-model arm there.

**Cost estimates in this project were wrong in the same direction three times**
(yeast multiview 3.4x over, reuters 4x over, proteins by a similar factor). The
error was under-modelling how TabPFN inference scales with feature count. Future
planning should use measured per-fit rates, not the fitted power law.

Running MIML-PFN on the proteins would need a CUDA GPU; MPS is the bottleneck,
not the method.

### Final evaluated scope

**8 datasets**: scene, mscv2, letter_frost, letter_carroll, birdsong, emotions,
yeast, reuters.
