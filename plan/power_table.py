#!/usr/bin/env python3
"""Power table for PREREGISTERED.md section 7 (task T05, revision R1), v3.

Deterministic (the only randomness, Part D, uses a fixed seed), one command
from the project root:

    ./.venv/bin/python experiments/revision_r1/power_table.py

Part A (design-level, no data). For each design in PREREGISTERED.md §0/§1 and
each H1 Holm family size m, the Bouckaert-Frank corrected repeated k-fold
t-test of §1.6:

    t = dbar / sqrt((1/n + rho) * s_d^2),  n = r*k,  df = n - 1,  two-sided,
    rho = n2/n1 = (1/k) / ((1 - 1/k) * f)

where f = n1 / (outer training size). For the MIML-PFN-vs-library table
f = 0.8 (MIML-PFN's context is 0.8 x the outer training fold, §1.3, F5;
§1.6 n1 rule, M8).

(a) critical |t| at the first Holm step (alpha/m) and the last (alpha);
(b) minimum d_z = dbar/s_d that reaches it:  d_z,min = t_crit * sqrt(1/n + rho);
(c) approximate power at d_z in {0.5, 1, 2, 3}: T ~ noncentral t, df = n - 1,
    ncp = d_z / sqrt(1/n + rho), i.e. assuming the corrected variance is the
    true variance of dbar (the assumption the test itself makes).

Part C (design-level, other families: H2, H4, H4-padded, H5), first Holm step,
with each family's own n1 fraction f.

Part D (global Wilcoxon signed-rank test over datasets, §1.6). Monte Carlo
power, seed 20261012, 20 000 draws per cell, two-sided alpha = 0.05,
scipy.stats.wilcoxon(method="exact"). Dataset deltas are drawn (i) from the
8 observed submitted-protocol mean dAP values (Part B) plus Gaussian jitter
sd 0.005 (so |d| has no ties and the exact null applies), (i') from
N(observed mean, observed SD), and (ii) from the
observed |dAP| values (same jitter) with a positive sign with probability
p_pos, the sign-consistent alternative.

Part B (descriptive, submitted protocol; not a result of the pre-registration).
For each of the 8 evaluated datasets, our reported arm vs the best published
AP, both selected exactly as paper_ieee_access/make_tables.py ours()/best()
(test-selected best published method -- optimistic for the baseline). Observed
d_z, corrected p under the design actually used (single k-fold), and Holm at
m = 8 and at the planned primary m = 16 (a scenario: untested rows last).

Output: stdout and revision_access_44676/evidence/T05__power_table.txt.
"""
import importlib.util
import math
import os
import sys

import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
EVIDENCE = os.path.join(ROOT, "revision_access_44676", "evidence",
                        "T05__power_table.txt")

ALPHA = 0.05
TRAIN_FRAC = 0.8          # MIML-PFN context = 0.8 x outer training fold
# v3 H1 families (§1.6, user decision 2026-10-13): the primary family F-H1
# has 16 planned rows (all datasets); the pre-specified sensitivity family
# F-H1-newdata restricts it to the 10 new-data rows.
M_PRIMARY = 16
M_NEWDATA = 10
FAMILY_SIZES = [10, 12, 14, 16]
DZ_GRID = [0.5, 1.0, 2.0, 3.0]

# (label, r, k, datasets it applies to under §1.1/§1.2)
DESIGNS = [
    ("single 10-fold (r=1,k=10)", 1, 10,
     "Scene, Reuters, Birds (MLSP 2013), VOC2012, Protein x4, Emotions-R, "
     "Yeast-R, Medical-R, Corel5K-R"),
    ("repeated 5x5 (r=5,k=5)", 5, 5, "MSRC v2, Letter Frost, Letter Carroll"),
    ("repeated 5x10 (r=5,k=10)", 5, 10, "HJA Birdsong"),
    ("single 5-fold (r=1,k=5)", 1, 5,
     "REFERENCE ONLY: submitted design for MSRC v2 / Letters"),
]

# Part C: other families. (name, m, r, k, f, note)
# H2: e = 0.136 is the largest mean fraction of training bags emptied by the
# instance-level purge on vector ids (Medical; PREREGISTERED.md H2-B table); the
# library arm uses f = 1 - e, TabPFN arms f = 0.8 * (1 - e).
E_PURGE = 0.136
OTHER = [
    ("H2 (7 methods x 4 sets), library arms", 28, 1, 10, 1.0 - E_PURGE,
     "n1 = post-purge training bags"),
    ("H2 (7 methods x 4 sets), TabPFN/logreg arms", 28, 1, 10,
     TRAIN_FRAC * (1.0 - E_PURGE), "n1 = 0.8 x post-purge training bags"),
    ("H4 (bagmax 16 + card 10 + multiview 16)", 42, 1, 10, TRAIN_FRAC, ""),
    ("H4 (same), 5x5 rows", 42, 5, 5, TRAIN_FRAC, ""),
    ("H4-padded (multiview vs width-matched padded, 16)", 16, 1, 10,
     TRAIN_FRAC, ""),
    ("H4-padded (same), 5x5 rows", 16, 5, 5, TRAIN_FRAC, ""),
    ("H5 per (dataset, model), 20 off-diagonal", 20, 1, 10, TRAIN_FRAC,
     "Scene, Birds"),
    ("H5 per (dataset, model), 20 off-diagonal", 20, 5, 5, TRAIN_FRAC,
     "MSRC v2, Letter Frost"),
]

# Part D: global test sizes. (label, n)
GLOBAL_N = [
    ("primary: all 16 H1 rows", 16),
    ("primary, collapsed (proteins -> 1, Letters -> 1)", 12),
    ("sensitivity: 10 new-data rows", 10),
    ("sensitivity, collapsed (proteins -> 1)", 7),
]
P_POS = [0.6, 0.75, 0.9]
N_DRAWS = 20000
SEED = 20261012
JITTER = 0.005


def rho(k, f=TRAIN_FRAC):
    return (1.0 / k) / ((1.0 - 1.0 / k) * f)


def tcrit(alpha, df):
    return float(stats.t.ppf(1.0 - alpha / 2.0, df))


def power(dz, r, k, alpha, f=TRAIN_FRAC):
    n = r * k
    df = n - 1
    c = tcrit(alpha, df)
    ncp = dz / math.sqrt(1.0 / n + rho(k, f))
    # scipy's nct.cdf returns nan when the far lower tail underflows; that
    # tail is then < 1e-12 and contributes nothing.
    lower = stats.nct.cdf(-c, df, ncp)
    return float(stats.nct.sf(c, df, ncp) + (0.0 if np.isnan(lower) else lower))


def corrected_p(d, k):
    n = len(d)
    s2 = d.var(ddof=1)
    t = d.mean() / math.sqrt((1.0 / n + rho(k)) * s2)
    return float(t), float(2.0 * stats.t.sf(abs(t), n - 1))


def holm(pvals, m):
    """Holm step-down with family size m >= len(pvals); the unobserved
    m - len(pvals) tests are assumed to rank after every observed one."""
    order = np.argsort(pvals, kind="stable")
    out = [False] * len(pvals)
    for rank, i in enumerate(order):
        if pvals[i] <= ALPHA / (m - rank):
            out[i] = True
        else:
            break
    return out


def load_make_tables():
    path = os.path.join(ROOT, "paper_ieee_access", "make_tables.py")
    spec = importlib.util.spec_from_file_location("make_tables", path)
    mt = importlib.util.module_from_spec(spec)
    cwd = os.getcwd()
    os.chdir(ROOT)
    try:
        spec.loader.exec_module(mt)
    finally:
        os.chdir(cwd)
    return mt


def part_a(w):
    w("## A. Design-level power, H1 families (corrected test of §1.6, "
      "alpha = 0.05; MIML-PFN vs library, n1 = 0.8 x outer training)")
    w("")
    w("rho = n2/n1 = (1/k)/((1-1/k)*0.8); n = r*k; df = n-1. "
      "d_z,min = t_crit * sqrt(1/n + rho). "
      f"Planned: primary F-H1 m = {M_PRIMARY}; sensitivity F-H1-newdata "
      f"m = {M_NEWDATA}.")
    w("")
    w("| design | n | df | rho | factor sqrt(1/n+rho) | applies to |")
    w("|---|---|---|---|---|---|")
    for lab, r, k, ds in DESIGNS:
        n = r * k
        w(f"| {lab} | {n} | {n-1} | {rho(k):.4f} | "
          f"{math.sqrt(1/n + rho(k)):.4f} | {ds} |")
    w("")
    w("### A1. Critical |t| and minimum d_z")
    w("")
    w("| design | m | t_crit first step (alpha/m) | d_z,min first step | "
      "t_crit last step (alpha) | d_z,min last step |")
    w("|---|---|---|---|---|---|")
    for lab, r, k, _ in DESIGNS:
        n = r * k
        f = math.sqrt(1 / n + rho(k))
        cl = tcrit(ALPHA, n - 1)
        for m in FAMILY_SIZES:
            tag = {M_PRIMARY: f"{m} (primary, planned)",
                   M_NEWDATA: f"{m} (new-data sensitivity)"}.get(m, str(m))
            cf = tcrit(ALPHA / m, n - 1)
            w(f"| {lab} | {tag} | {cf:.3f} | {cf*f:.3f} | {cl:.3f} | "
              f"{cl*f:.3f} |")
    w("")
    w("### A2. Approximate power at the first Holm step (alpha/m) and the "
      "last (alpha)")
    w("")
    w("Noncentral t, df = n-1, ncp = d_z/sqrt(1/n+rho).")
    w("")
    hdr = " | ".join(f"d_z={z:g}" for z in DZ_GRID)
    w(f"| design | step | {hdr} |")
    w("|---|---|" + "---|" * len(DZ_GRID))
    for lab, r, k, _ in DESIGNS:
        for m in FAMILY_SIZES + [1]:
            a = ALPHA / m
            step = "last (alpha)" if m == 1 else f"first, m={m}"
            cells = " | ".join(f"{power(z, r, k, a):.3f}" for z in DZ_GRID)
            w(f"| {lab} | {step} | {cells} |")
    w("")


def part_c(w):
    w("## C. Other families: first Holm step (alpha/m), each with its own n1")
    w("")
    w("f = n1 / outer training size; rho = (1/k)/((1-1/k)*f). "
      f"H2 uses e = {E_PURGE} (largest mean fraction of training bags "
      "emptied by the instance purge, Medical).")
    w("")
    w("| family | m | design | f | rho | d_z,min first step | "
      "power d_z=1 | power d_z=2 | power d_z=3 | note |")
    w("|---|---|---|---|---|---|---|---|---|---|")
    for name, m, r, k, f, note in OTHER:
        n = r * k
        fac = math.sqrt(1 / n + rho(k, f))
        cf = tcrit(ALPHA / m, n - 1)
        pw = [power(z, r, k, ALPHA / m, f) for z in (1.0, 2.0, 3.0)]
        w(f"| {name} | {m} | r={r},k={k} | {f:.3f} | {rho(k, f):.4f} | "
          f"{cf*fac:.3f} | {pw[0]:.3f} | {pw[1]:.3f} | {pw[2]:.3f} | "
          f"{note} |")
    w("")


def wilcoxon_power(draw, n, rng):
    hits = 0
    for _ in range(N_DRAWS):
        d = draw(n, rng)
        p = stats.wilcoxon(d, alternative="two-sided", method="exact").pvalue
        hits += p <= ALPHA
    return hits / N_DRAWS


def part_d(w, observed):
    obs = np.asarray(observed, float)
    absobs = np.abs(obs)
    w("## D. Global Wilcoxon signed-rank test over datasets: Monte Carlo power")
    w("")
    w(f"Two-sided, alpha = {ALPHA}, exact null; {N_DRAWS} draws per cell; "
      f"numpy default_rng({SEED}). Observed submitted-protocol dataset deltas "
      f"(Part B): mean {obs.mean():+.4f}, SD {obs.std(ddof=1):.4f}. "
      f"Every draw adds N(0, {JITTER}^2) jitter so |d| has no ties.")
    w("")
    w("(i) 'observed' = resample the 8 observed deltas with replacement. "
      "(i') 'normal' = N(observed mean, observed SD), the form used in "
      "PREREG__review_2.md computation (c). "
      "(ii) 'sign p' = resample the 8 observed |delta| and give each a "
      "positive sign with probability p (sign-consistent alternative).")
    w("")
    hdr = " | ".join(f"(ii) sign p={p:g}" for p in P_POS)
    w(f"| test | n | min attainable p | (i) observed | (i') normal | {hdr} |")
    w("|---|---|---|---|---|" + "---|" * len(P_POS))
    rng = np.random.default_rng(SEED)

    def draw_obs(n, g):
        return g.choice(obs, n) + g.normal(0, JITTER, n)

    def draw_norm(n, g):
        return g.normal(obs.mean(), obs.std(ddof=1), n)

    for lab, n in GLOBAL_N:
        pmin = 2.0 / 2 ** n
        cells = [f"{wilcoxon_power(draw_obs, n, rng):.3f}",
                 f"{wilcoxon_power(draw_norm, n, rng):.3f}"]
        for pp in P_POS:
            def draw_sign(nn, g, pp=pp):
                mag = g.choice(absobs, nn) + g.normal(0, JITTER, nn)
                sgn = np.where(g.random(nn) < pp, 1.0, -1.0)
                return sgn * np.abs(mag)
            cells.append(f"{wilcoxon_power(draw_sign, n, rng):.3f}")
        w(f"| {lab} | {n} | {pmin:.2g} | " + " | ".join(cells) + " |")
    w("")


def part_b(w, mt):
    w("## B. Observed effects (descriptive, submitted protocol; not a result "
      "of this pre-registration)")
    w("")
    w("Ours = make_tables.ours() arm (multiview where it completed, else "
      "bag-mean); published = make_tables.best(PUB, ds, AP), selected on "
      "test. d = ours - published per fold. d_z = mean(d)/sd(d, ddof=1), "
      "uncorrected. t_corr/p_corr = §1.6 test with r=1, k = folds actually "
      "used, rho = (1/k)/((1-1/k)*0.8). p_naive = ttest_rel (as in the "
      "submitted paper). Holm at m=8 (the 8 tests together) and at "
      f"m={M_PRIMARY} (planned primary size). The m={M_PRIMARY} column is a "
      "scenario: the 8 untested rows are placed after every observed row, "
      "which gives the observed rows the strictest thresholds that do not "
      "depend on the untested rows; it is not a bound in either direction. "
      "Yeast and Emotions here are the leaky originals; their primary rows "
      "in v3 are the rebuilt versions.")
    w("")
    rows = []
    for key, name, _ in mt.EVALUATED:
        pn, _ = mt.best(mt.PUB, key, "AveragePrecision")
        _, armname = mt.ours(key, "AveragePrecision")
        arm = "tabpfn_multiview" if armname == "multi-view" else "tabpfn_bagmean"
        of = mt.perfold(mt.MINE, f"{key}/{arm}", "AveragePrecision")
        pf = mt.perfold(mt.PUB, f"{key}/{pn}", "AveragePrecision")
        if of is None or pf is None or len(of) != len(pf):
            w(f"- {key}: per-fold vectors unavailable, skipped")
            continue
        d = of - pf
        k = len(d)
        dz = d.mean() / d.std(ddof=1)
        tc, pc = corrected_p(d, k)
        pnaive = float(stats.ttest_rel(of, pf).pvalue)
        dzmin = tcrit(ALPHA / M_PRIMARY, k - 1) * math.sqrt(1 / k + rho(k))
        rows.append(dict(key=key, name=name.split("$")[0], arm=armname,
                         pn=pn, k=k, dbar=d.mean(), dz=dz, tc=tc, pc=pc,
                         pn_=pnaive, dzmin=dzmin))
    p = np.array([r["pc"] for r in rows])
    h8 = holm(p, 8)
    hm = holm(p, M_PRIMARY)
    w("| dataset | ours | best published | k | mean dAP | d_z | t_corr | "
      f"p_corr | p_naive | Holm m=8 | Holm m={M_PRIMARY} (scenario) | "
      f"d_z,min first step m={M_PRIMARY}, this k |")
    w("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r, a, b in zip(rows, h8, hm):
        he = "pass" if b else "fail"
        w(f"| {r['name']} | {r['arm']} | {r['pn']} | {r['k']} | "
          f"{r['dbar']:+.4f} | {r['dz']:+.2f} | {r['tc']:+.2f} | "
          f"{r['pc']:.3g} | {r['pn_']:.2g} | {'pass' if a else 'fail'} | "
          f"{he} | {r['dzmin']:.2f} |")
    w("")
    w(f"Survivors: {sum(h8)}/{len(rows)} at m=8; {sum(hm)}/{len(rows)} "
      f"at m={M_PRIMARY} (scenario).")
    w("")
    return rows


def main():
    lines = []
    w = lines.append
    w("# T05 power table, v3 (generated by "
      "experiments/revision_r1/power_table.py)")
    w("")
    part_a(w)
    part_c(w)
    mt = load_make_tables()
    rows = part_b(w, mt)
    part_d(w, [r["dbar"] for r in rows])
    text = "\n".join(lines)
    print(text)
    os.makedirs(os.path.dirname(EVIDENCE), exist_ok=True)
    with open(EVIDENCE, "w") as fh:
        fh.write(text + "\n")
    print(f"\nwrote {EVIDENCE}", file=sys.stderr)


if __name__ == "__main__":
    main()
