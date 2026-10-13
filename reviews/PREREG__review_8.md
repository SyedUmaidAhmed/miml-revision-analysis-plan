# Review 8 of `experiments/revision_r1/PREREGISTERED.md` (v3 after the round-7 fixes; git `155e4e2`, 823 lines, working tree identical to HEAD)

Reviewer role: independent statistician (CV inference, multiple testing, compute protocols on shared hardware) and MIML practitioner; did not write v1–v3 or reviews 1–7. Date: 2026-10-13.

Scope, as set by the task: verify the round-7 fix (finding 1: `<config>` undefined for TabPFN arms, H3 / H1-leaky Yeast width collision; notes N1–N4) exactly against `git diff 55105f4`; re-run the exhaustive path-uniqueness enumeration over every unit under both §6.4 PCA-trigger outcomes for every dataset **and under both device branches of §6.1** (G available; global MPS fallback); confirm that every reuse statement names a unit that is the identical fit the consuming procedure requires; check for contradictions with any section and with `revision_access_44676/DECISIONS.md`.

## What I checked

| check | result |
|---|---|
| `git diff 55105f4 -- experiments/revision_r1/PREREGISTERED.md` | Five hunks: §1.5 `<config>` line (width token for TabPFN; surrogate for H5); §1.5 reuse paragraph (general rule + four fixed reuses: H3/H1-leaky Yeast, §1.9 sixth run under fallback, §6.9 Scene, §5 outputs under `verify-2fit+g` / `verify-1fit+g`); §5 names the splits (`submitted5` for Letter Frost, canonical for Scene); §6.1 row 3 "one of the two MPS exceptions, with T03-g"; the appended round-7 response table. No other line changed. |
| `git diff --stat 55105f4`; `git status` | Only this document and `PREREG__review_7.md` changed. `DECISIONS.md`, `power_table.py`, `T05__power_table.txt` untouched; no number in §7 moved. Working tree clean. |
| Round-7 response table vs the hunks | Each of the six rows describes exactly what its hunk does. |
| `DECISIONS.md`, every row | All round-7 changes are manifest bookkeeping and fit-reuse; no unit is dropped or reduced, so the 2026-10-12 "nothing descoped" row and the 2026-10-13 budget row are untouched. No contradiction. |
| Stored results the reuse/reproduction statements rest on (`results/foundation_baselines.json`) | `letter_frost/tabpfn_bagmean` and `letter_frost/tabpfn_multiview` are stored with `num_folds = 5` on the harness's `np.random.seed(42)` shuffle (`run_foundation_baselines.py:63`), so `submitted5` names the right split for T03-g, §6.9 and §5, and §6.9's multiview comparator exists. `scene/tabpfn_bagmean`, `scene/logreg_bagmean`, `yeast/tabpfn_bagmean` are stored at 10 folds. |
| Harness settings vs the plan | `TabPFNClassifier(device, ignore_pretraining_limits=True)` with library defaults `n_estimators = 8`, `random_state = 0` (`run_foundation_baselines.py:100`), as H4 states; logreg is `LogisticRegression(max_iter=1000)` with no tuned hyperparameter (`:103`). |

## Part 1 — The round-7 fix, verified

**Finding 1 (width token; H3 vs H1-leaky Yeast): resolved as specified.** `<config>` for TabPFN arms is now the width token `native` / `pca500`, so under a Yeast trigger H3's `yeast/original/tabpfn_multiview/native/main+g` and the leaky-column `…/pca500/main+g` are distinct files, and without a trigger the leaky-column rows are declared to *be* the H3 units (one fit, re-read). The reused fit is identical to what H3 requires: canonical split (§1.1), leaky original file, native width 619, `tr` in `get_cv_splits` order (§1.3), `fit_i` z-scoring, the harness constructor, device G. The H1 leaky column is EXPLORATORY and in no family, so reading the H3 fit there changes no test.

**N1 (sixth run under the fallback): resolved.** The H1 `main+mps` canonical unit is the identical computation (same split, width by the §6.4 decision, MPS) that §1.9's same-device comparison needs; §1.9's arms run at execution position 8, after H1's positions 1 and 3, so the unit exists when read. **N2 (§6.9 Scene): resolved** — Scene bag-mean is d = 15 → width 15, always `native`, so the H1 Scene unit is the one §6.9 needs. **N3 (§5 outputs): resolved** — dedicated tokens, kept and deposited; the H1 Scene unit is a separate fit, which is deterministic (`random_state = 0`) and in any case bound to the §5 pass criterion of 1e-9. **N4: resolved** in §6.1 row 3.

## Part 2 — Exhaustive path enumeration

Path: `<dataset>/<version>/<arm>/<config>/<condition>/r<repeat>_f<fold>[_i<inner>].npz`. `W` ∈ {native, pca500} is the width token; `D` ∈ {g, mps} is the device token (`g` when G is available, `mps` for every TabPFN unit under the §6.1 fallback). Under a §6.4 trigger on a dataset, every TabPFN arm on every version of it carries the same `W`, except H3's Yeast pair; so within one dataset `W` separates exactly the one pair §6.4 distinguishes.

| source | units | path pattern | distinct? |
|---|---|---|---|
| H1 TabPFN (16 rows) | `tabpfn_multiview`, `tabpfn_bagmean`; `original` for 12 native sets, `rebuilt` for 4 constructed; r0 on canonical splits, r0..4 on §1.2 sets | `<ds>/{original,rebuilt}/tabpfn_{multiview,bagmean}/W/main+D/r<r>_f<k>` | yes |
| H1 library (84 KDIS + 9 MIMLNN × 5 Octave seeds; inner 5-fold, 3-fold on VOC2012) | outer and inner, per candidate | `<ds>/{original,rebuilt}/<method>/<candidate>/main[+seed-s<j>]/r<r>_f<k>[_i<q>]` | yes. The 8 per-method rows (§1.3) and H2-B's "MIMLkNN on its own" re-select over these same files — reuse of identical fits, correct for a validation-selected procedure |
| H1 leaky column (§6.7 pos. 7) | both TabPFN arms and the library on the leaky originals of Emotions, Medical, Corel5K, Yeast | `<ds>/original/<arm>/W or <candidate>/main+D/r0_f<k>` | yes. Yeast TabPFN rows = the H3 units when `W` coincides (declared); under a Yeast trigger the multiview row is `pca500` vs H3 `native` |
| H1 Reuters de-dup | rescoring of stored predictions, no refit | `reuters/dedup/…` if written | yes |
| H2-A (§6.10) | = the H1 `rebuilt` rows; inner folds `_i0.._i4` (pools 2,2,2,2,1) | as H1 | yes |
| H2-B (7 methods × 4 sets) | `leak`, `control-s0..s2`; library with inner folds; MIMLNN seeds; TabPFN with `W`, `D`; logreg | `<ds>/purged/<arm>/W or <candidate> or ?/{leak,control-s<j>}[+seed-s<j>][+D]/r0_f<k>[_i<q>]` | yes (logreg `<config>` slot undefined — finding 2; no collision) |
| H3 Yeast pair (§6.7 pos. 2) | multiview at native 619 (§6.4 exception), bag-mean d = 103 (always native), leaky original, canonical split | `yeast/original/tabpfn_{multiview,bagmean}/native/main+D/r0_f<k>` | yes; see H1 leaky column |
| H3 Birds, R2 | stored pair; Reuters and protein H1 runs | no new unit | — |
| H4 | `tabpfn_bagmax`, `tabpfn_bagmean_card` (10 rows), `tabpfn_padded` (3 seeds), subsampling of multiview and bagmean (4 sizes × 3 seeds); the `main+D` multiview/bagmean rows are the H1 files (f = 1.0), identical fits by H4's own constructor statement; `bagmean_card` on constant-size rows reuses the bag-mean result and writes nothing | `<ds>/{original,rebuilt}/tabpfn_bagmax/W/main+D/…`, `…/tabpfn_bagmean_card/W/main+D/…`, `…/tabpfn_padded/W/padded-s<j>+D/…`, `…/tabpfn_{multiview,bagmean}/W/sub-{f0.25,f0.5,f0.75,single}-s<j>+D/…` | yes |
| H5 | `mlp_bagmean`, `abmil` × 5 surrogates × seeds {0,1,2}; Scene, Birds r0; MSRC v2, Letter Frost r0..4 | `<ds>/original/{mlp_bagmean,abmil}/{bce,ranking,oneerror,coverage,smoothap}/seed-s<j>/r<r>_f<k>` | yes |
| §1.9 repeated CV (8 datasets) | logreg ×2, TabPFN ×2 on MPS, library; seeds 10..14 → r0..4 | `<ds>/rcv10/<arm>/W or <candidate> or ?/main[+seed-s<j>][+mps]/r<r>_f<k>[_i<q>]` | yes |
| §1.9 sixth run | TabPFN ×2, canonical split, MPS | G available: `<ds>/original/tabpfn_*/W/main+mps/r0_f<k>` vs H1 `main+g` — yes. Fallback: = H1 `main+mps`, reused (declared) | yes |
| T03-g | logreg Scene on C; `tabpfn_bagmean` Letter Frost on MPS, seed-42 split | `scene/original/logreg_bagmean/?/main/r0_f<k>`; `letter_frost/submitted5/tabpfn_bagmean/native/main+mps/r0_f<k>` | yes when G is available |
| §6.9 | `tabpfn_bagmean` Letter Frost and Scene, `tabpfn_multiview` Letter Frost, on the §6.1 device | `letter_frost/submitted5/tabpfn_{bagmean,multiview}/native/main+D/r0_f<k>`; Scene = the H1 unit, reused (declared) | **G available: yes. Fallback (`D = mps`): the Letter Frost bag-mean unit is the T03-g unit — finding 1** |
| §5 | two-fit and one-fit `tabpfn_bagmean`, Scene canonical and Letter Frost `submitted5` | `scene/original/tabpfn_bagmean/native/verify-{2fit,1fit}+D/r0_f<k>`; `letter_frost/submitted5/…/verify-{2fit,1fit}+D/r0_f<k>` | yes |
| timing pilots (§6.3) | predictions discarded unscored | none | — |

Width is never ambiguous across procedures: the PCA decision is per dataset (G-queue step 4) and inherited by H2-B, H4 and §1.9, so any two units that share dataset, version, arm, condition and device also share `W` — except the one H3 pair, which `W` now separates. Letter Frost (d = 16) and Scene (d = 15) can never trigger, so every T03-g, §6.9 and §5 unit is `native` in both branches.

Under the G branch every pair resolves. Under the fallback branch the enumeration re-runs with every `D = mps`; all declared reuses hold (H3 = H1-leaky Yeast at `main+mps`; §1.9 sixth run = H1; §6.9 Scene = H1), and exactly one pair that the device token separated in review 7 collapses: §6.9's Letter Frost bag-mean and T03-g's Letter Frost bag-mean.

## Part 3 — Findings

**1. Under the §6.1 global MPS fallback, §6.9's Letter Frost `tabpfn_bagmean` run and T03-g's Letter Frost `tabpfn_bagmean` run are the same unit, and the plan does not say so.**
§6.1 row 1 lists the "cross-device check" among the arms that move to MPS under the fallback, and §6.0 C-queue step 8 moves T03-g's TabPFN part to the G queue "which then runs on MPS". Both are then `tabpfn_bagmean` on the submitted seed-42 split of Letter Frost, native width, same recreated `tabpfn_env`, same pinned settings, same device: `letter_frost/submitted5/tabpfn_bagmean/native/main+mps/r0_f<k>.npz`. Review 7 cleared this pair by the device token (`+mps` vs `+g`), which holds only when G is available. In the fallback branch the second write is refused by the no-overwrite writer (an unexecutable step by the standard of rounds 6 and 7), and §6.9 itself is no longer a cross-device check: both of its sides are MPS, so it reduces to T03-g's environment reproduction plus a Letter Frost multiview reproduction, and its 1e-3 rule ("the manuscript reports the device of every row") has nothing to attribute to a device. The round-7 reuse list already handles the two other fallback reuses (§1.9 sixth run, §6.9 Scene) but not this one.
*Fix (one bullet in the §1.5 reuse list, one clause in §6.9).* "Under the §6.1 fallback, §6.9's Letter Frost bag-mean unit is the T03-g unit, reused; §6.9 is then reported as a same-device (MPS) environment check of the stored rows, not a device check, and its multiview Letter Frost run is a new `+mps` unit." While there, write the §1.5 literal tokens (`main+g` in the three reuse bullets, `verify-2fit+g` / `verify-1fit+g`) as "with the device token of §6.1", since all of them read `+mps` under the fallback. Changes no experiment and no statistic.

**2. `<config>` is still undefined for the logreg arms** (`logreg_bagmean`, `logreg_multiview` in §1.9, H2-B and T03-g). The round-7 line defines the slot for library arms (candidate), TabPFN arms (width) and H5 (surrogate); logreg is none of these, and `LogisticRegression(max_iter=1000)` carries no tuned quantity, so the doer must invent a token with nothing to encode. No two logreg units collide (they differ by version or condition), so this cannot refuse a write or move a number; it is the half of review 7's finding 1 ("a doer has to invent a token") that the fix left open for one arm class, and a reader of the released manifest would ask what the token means.
*Fix (four words in §1.5).* "For logreg arms it is `default`." (or the single constructor string). Changes nothing else.

## Notes (no action required)

- **N1.** When a dataset's trigger fires, §6.4 says arms with d ≤ 500 are "unchanged (no-op)", and the §1.5 Yeast bullet labels bag-mean at d = 103 `native` "in any case", which implies the convention *token = `native` whenever PCA is a no-op*. It is implied, not stated, for the other no-op cases (bag-mean on every dataset except Medical; `bagmean_card` likewise). Harmless either way because the token is per (dataset, arm) and identical across procedures, but one clause ("`pca500` only where PCA was actually applied") would spare a `pca500` label on an unchanged arm.
- **N2.** The header "History" row stops at review 6 and the "Version control" row at `5e29f54`; `55105f4` (round-7 text) and review 7 are not listed, as in review 6's N2. The round-7 response table is present. Not a contradiction; the m2 deposit procedure records whichever commit is deposited.
- **N3.** §6.9 compares G against *stored* MPS rows that were produced with two fits; the G rows use the production fit count fixed by §5. Because §5's pass criterion is 1e-9 on the same device and §6.9's tolerance is 1e-3, fit count cannot confound the device attribution. Likewise T03-g's TabPFN part does not name its fit count; immaterial at its 1e-3 tolerance.
- **N4.** Reviews 5, 6 and 7's remaining notes stand as stated; nothing in the round-7 fixes touched them.

## Summary

The round-7 fix is exactly the one requested and nothing else moved since `55105f4`. With the width token the enumeration resolves every pair under both PCA-trigger outcomes when G is available, and every declared reuse names a fit that is identical to the one the consuming procedure requires (H3 ↔ H1-leaky Yeast; §1.9 sixth run ↔ H1 under the fallback; §6.9 Scene ↔ H1; H4's f = 1.0 rows ↔ H1; library re-selections ↔ stored candidates). Re-running the enumeration in the fallback branch, where every TabPFN unit carries `+mps`, exposes one pair that the device token no longer separates: §6.9's and T03-g's Letter Frost bag-mean runs, which the plan should declare as one reused unit (and §6.9 as a same-device check in that branch). The logreg arms are the one arm class whose `<config>` slot the round-7 definition still omits; no collision follows. Both are one-sentence fixes of the same kind as rounds 5–7 and change no experiment or statistic.

MAJOR: none. MINOR: 2.

VERDICT: NOT RESOLVED — 2 findings
