# Review 7 of `experiments/revision_r1/PREREGISTERED.md` (v3 after the round-6 fixes; git `55105f4`, 808 lines, working tree identical to HEAD, sha256 `4554371b47ef4fde0de427b49d2c6d7c3a19f753fd325ba41d5c7a73f7430818`)

Reviewer role: independent statistician (CV inference, multiple testing, compute protocols on shared hardware) and MIML practitioner; did not write v1–v3 or reviews 1–6. Date: 2026-10-13.

Scope of this round, as set by the task: verify the round-6 fix (finding 1: device token and `submitted5` version; notes N1, N2) exactly against `git diff 5e29f54`; then test §1.5's assertion "No two units share a path" exhaustively by enumerating every unit the plan defines; confirm no contradiction with any other section or with `revision_access_44676/DECISIONS.md`.

## What I checked

| check | result |
|---|---|
| `git diff 5e29f54 -- experiments/revision_r1/PREREGISTERED.md` | Four hunks: header History and Version-control rows; §1.5 `<version>` line and a new "Device token (round 6)" line; §1.9 "one of the two MPS exceptions in §6.1, with T03-g"; the appended "Response to `PREREG__review_6.md`" table. No other line changed. |
| `git diff 5e29f54 --stat`; `git status` | Only this document and `PREREG__review_6.md` changed since `5e29f54`; `DECISIONS.md`, `power_table.py`, `T05__power_table.txt` untouched, so no number in §7 moved. Working tree clean for the prereg and for `DECISIONS.md`. |
| Round-6 response table vs the hunks | Each of the three rows describes exactly what its hunk does. |
| `DECISIONS.md`, every row | The device token and the `submitted5` version are bookkeeping; no row is touched. The 2026-10-12 "GPU arms wait for Inception credits" row and the 2026-10-13 budget row are unaffected. |

## Part 1 — The round-6 fix, verified

**Finding 1 (device token; `submitted5`): resolved as specified.** §1.5 now requires every TabPFN unit's `<condition>` to end in `+g` or `+mps`, CPU arms carry none, and `<version>` gains `submitted5` = the submitted seed-42 single 5-fold splits, `r0_f0..4`, named for T03-g and §6.9 on Letter Frost, with Scene staying `original`. The two collisions review 6 named are gone: the §1.9 sixth run is `<ds>/original/tabpfn_*/<config>/main+mps/r0_f<k>` against H1's `main+g`; T03-g is `letter_frost/submitted5/tabpfn_bagmean/<config>/main+mps/r0_f<k>` against §6.9's `main+g`. `submitted5` is consistent with §1.2 ("submitted seed-42 5-fold results for MSRC v2 and the Letter sets"), with T03-g's "must reproduce the stored result" (stored on that split) and with §6.9's "against the stored MPS results". Under the §6.1 fallback every TabPFN unit carries `+mps`, which keeps "G and MPS are never mixed within a comparison" checkable from the manifest.

**N1: resolved** in §1.9. **N2: resolved** in the header (reviews 5 and 6, commits `d2c1103`, `5e29f54`).

## Part 2 — Exhaustive path enumeration

Path: `<dataset>/<version>/<arm>/<config>/<condition>/r<repeat>_f<fold>[_i<inner>].npz`. Every unit the plan defines, with its path pattern:

| source | units | path pattern | distinct? |
|---|---|---|---|
| H1 TabPFN (16 rows, §1.6; §6.7 pos. 1, 3) | `tabpfn_multiview`, `tabpfn_bagmean`; `original` for 12 native sets, `rebuilt` for the four constructed sets; r0 on canonical splits, r0..4 on §1.2 sets | `<ds>/{original,rebuilt}/tabpfn_{multiview,bagmean}/<config>/main+g/r<r>_f<k>` | yes |
| H1 library (84 KDIS + 9 MIMLNN configs × 5 Octave seeds; inner 5-fold, 3-fold on VOC2012) | per candidate, outer and inner | `<ds>/{original,rebuilt}/<method>/<config>/main[+seed-s<j>]/r<r>_f<k>[_i<q>]` | yes. The 8 per-method rows (§1.3) and H2-B's "MIMLkNN on its own" re-select over the same stored candidate files; that is a reuse, not a second write. |
| H1 leaky column (§6.7 pos. 7) | both TabPFN arms and the library on the leaky originals of the four constructed sets | `<ds>/original/<arm>/<config>/main+g/r0_f<k>` | yes against everything **except H3 on Yeast — finding 1** |
| H1 Reuters de-dup | rescoring of stored predictions, no refit | `reuters/dedup/...` if the rescored subsets are written; no new fit | yes |
| H2-A (§6.10) | = the H1 rows above on `rebuilt`; inner folds `_i0.._i4` (pools 2,2,2,2,1) | as H1 | yes |
| H2-B (7 methods × 4 sets) | `leak`, `control-s0..s2`; library candidates with inner folds; MIMLNN seeds; TabPFN with device | `<ds>/purged/<arm>/<config>/{leak,control-s<j>}[+seed-s<j>][+g]/r0_f<k>[_i<q>]` | yes |
| H3 Yeast pair (§6.7 pos. 2) | `tabpfn_multiview` at **native width 619** (§6.4 exception), `tabpfn_bagmean` (d = 103, never PCA'd), leaky original, canonical split, G | `yeast/original/tabpfn_{multiview,bagmean}/<config>/main+g/r0_f<k>` | **same path as the H1 leaky Yeast row — finding 1** |
| H3 Birds, H3 R2 | stored submitted pair; Reuters and protein H1 runs | no new unit | — |
| H4 arms | `tabpfn_bagmax`, `tabpfn_bagmean_card` (10 variable-size rows), `tabpfn_padded` (3 seeds), subsampling of multiview and bagmean (4 sizes × 3 seeds); multiview and bagmean `main+g` are the H1 files | `<ds>/{original,rebuilt}/tabpfn_bagmax/<config>/main+g/…`, `…/tabpfn_bagmean_card/…/main+g/…`, `…/tabpfn_padded/…/padded-s<j>+g/…`, `…/tabpfn_{multiview,bagmean}/…/sub-{f0.25,f0.5,f0.75,single}-s<j>+g/…` | yes |
| H5 | `mlp_bagmean`, `abmil` × 5 surrogates × seeds {0,1,2}; Scene, Birds r0; MSRC v2, Letter Frost r0..4 | `<ds>/original/{mlp_bagmean,abmil}/{bce,ranking,oneerror,coverage,smoothap}/seed-s<j>/r<r>_f<k>` | yes |
| §1.9 repeated CV (8 datasets) | logreg ×2, TabPFN ×2 on MPS, library; seeds 10..14 → r0..4 | `<ds>/rcv10/<arm>/<config>/main[+seed-s<j>][+mps]/r<r>_f<k>[_i<q>]` | yes |
| §1.9 sixth run | TabPFN ×2, canonical split, MPS | `<ds>/original/tabpfn_*/<config>/main+mps/r0_f<k>` | yes vs H1 `main+g` (note N1 for the fallback case) |
| T03-g | logreg Scene on C; `tabpfn_bagmean` Letter Frost on MPS, seed-42 split | `scene/original/logreg_bagmean/<config>/main/r0_f<k>`; `letter_frost/submitted5/tabpfn_bagmean/<config>/main+mps/r0_f<k>` | yes (no other logreg unit on Scene `original` exists in the plan) |
| §6.9 | `tabpfn_bagmean` Letter Frost and Scene, `tabpfn_multiview` Letter Frost, on G | `letter_frost/submitted5/tabpfn_{bagmean,multiview}/<config>/main+g/r0_f<k>`; `scene/original/tabpfn_bagmean/<config>/main+g/r0_f<k>` | Letter Frost yes; Scene is **the H1 Scene bag-mean unit** (note N2) |
| §5 one-fit check | two-fit vs one-fit `tabpfn_bagmean`, Letter Frost and Scene, G | both procedures map to the same path (note N3) | — |
| timing pilots (§6.3) | predictions discarded unscored | none | — |

Everything resolves except one pair, where two units that the plan distinguishes by **feature width** have identical paths, because the path has no width token and `<config>` is defined only for library candidates.

## Part 3 — Findings

**1. The path cannot separate H3's native-width Yeast multiview run from the H1 leaky-column Yeast multiview run, which §6.4 puts at PCA-500 if the Yeast trigger fires; and `<config>` is undefined for every TabPFN arm.**
§1.5: "`<config>` is the candidate (method, distance, k / ratio, λ)" — a library notion; no TabPFN arm has a candidate, so a doer has to invent a token for `<config>` on every TabPFN unit, and nothing says what it must carry. The quantity that *does* vary between TabPFN units on one (dataset, version, arm, condition) is width: §6.4 says that when the trigger fires on a dataset "all TabPFN arms on all versions of that dataset use PCA … to d′ = 500", with exactly one exception, "H3's registered Yeast pair on the leaky file stays at native width" (d = 619, H3). The H1 leaky column (§H1 "the leaky original is reported beside it"; §6.7 position 7) is also `tabpfn_multiview` on Yeast `original`, canonical split, G — and it is *not* excepted, so under a Yeast trigger it runs at 500. Two different fits, both `yeast/original/tabpfn_multiview/<config>/main+g/r0_f<k>.npz`: the second is refused by the no-overwrite writer (an unexecutable step), or, if filed under an ad-hoc token, the released manifest cannot show which file the CONFIRMATORY H3 rule was evaluated on (a wrong-result risk on the one row whose outcome sentence, (b)/(b′), goes in the abstract). The condition is not far-fetched: Yeast multiview is the arm that "did not complete" in August, and lesson 10 of the project record says the TabPFN cost estimates were off by 3–4× three times. When the trigger does *not* fire, positions 2 and 7 call for the same Yeast fit twice and the plan nowhere says that the H1 leaky row reuses the H3 unit; the writer again refuses the second, harmlessly, but the plan should say which it is rather than leave the doer to discover it.
*Fix (two lines in §1.5, one in H1 or H3).* Define `<config>` for TabPFN arms as the width token, `native` or `pca500` (so the manifest shows width as it now shows device), and state that the H1 leaky-column Yeast rows are the H3 units whenever the widths coincide, and separate units at `pca500` otherwise. Changes no experiment and no statistic.

## Notes (no action required)

- **N1.** Under the §6.1 global MPS fallback, H1's canonical TabPFN run carries `main+mps` and is byte-for-byte the same computation as §1.9's "sixth run"; the sixth run is then redundant and its write would be refused. A clause "(under the fallback, the H1 run is that run)" in §1.9 would spare the doer a refused write. Same arithmetic either way.
- **N2.** §6.9's Scene `tabpfn_bagmean` on G is the H1 Scene bag-mean unit (same dataset, version, arm, condition, device, width). §1.5's "Scene keeps `original`" implies the authors intend reuse; §6.0 G-queue step 8 and §6.7 position 9 read as a separate run. One phrase ("the H1 unit, re-read; no new fit") would settle it. No result changes.
- **N3.** §5 writes two prediction sets (two-fit and one-fit) for the same (Scene, Letter Frost) `tabpfn_bagmean` units on G; the path has no fit-count token and §5 does not say its predictions are discarded. Whichever is written first becomes the H1 Scene file; by §5's own pass criterion the two differ by ≤ 1e-9, so this cannot move a number. A sentence "§5 predictions are written outside `predictions/` (or discarded), as for pilots" would close it. §5 also does not name which Letter Frost split it uses (`original` r0 or `submitted5`); immaterial to the check.
- **N4.** §6.1 row 3 still reads "(the one exception; …)" after row 1 was changed in round 5 to list two exceptions; §1.9's wording was fixed in round 6 but this row was not. Reconcilable (row 3 is the one MPS row), as review 6 said of §1.9.
- **N5.** Reviews 5 and 6's remaining notes stand as stated.

## Summary

The round-6 fix is exactly the one requested and nothing else moved since `5e29f54`. The exhaustive enumeration confirms the device token and `submitted5` separate every pair review 6 named and every pair that differs by device, split, seed, condition or inner fold. One pair remains that differs by **width**: the H3 native-width Yeast multiview run and the H1 leaky-column Yeast multiview run, which are distinct units under a §6.4 trigger on Yeast and share a path because the path has no width token and `<config>` is not defined for TabPFN arms. It is a two-line fix of the same kind as rounds 5 and 6, and changes no experiment.

MAJOR: none. MINOR: 1.

VERDICT: NOT RESOLVED — 1 findings
