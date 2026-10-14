"""Tie-neutral ranking metrics (AMENDMENT.md A1, 2026-10-13).

Each of the four ranking metrics is the exact expected value of the
miml_metrics.py metric when tied scores are ordered uniformly at random.
Ties mean exact float64 equality. Every other convention of miml_metrics.py
is kept:
  - OneError, Coverage and AveragePrecision skip bags with no relevant label;
  - RankingLoss averages over all bags, and a bag with no relevant or no
    irrelevant label contributes 0 (sklearn.metrics.label_ranking_loss);
  - Coverage is (rank of the lowest-ranked relevant label) - 1, rank 1 = top.
Edge cases follow miml_metrics.py too: with no relevant label in any bag,
OneError and AveragePrecision are 0.0 and Coverage is -1.0
(miml_metrics' `cover / max(0, 1) - 1`); fewer than 2 labels raise ValueError,
as sklearn's label_ranking_loss does inside miml_metrics.RankingLoss.
Ties are judged on the scores exactly as passed in, i.e. after the §1.3 F4
degenerate-label overwrite in the harness, cast to float64 (float32 outputs
are cast exactly, so float64 equality is float32 equality).
For a score row without ties, every value equals miml_metrics.py's
(tests/test_tie_neutral.py checks this, and also checks against brute-force
enumeration of every tie order).

Closed forms, for one bag with scores s and relevant set P:
  OneError     1 - |T & P| / |T|, where T = labels sharing the maximum score.
  RankingLoss  (#{(p, n): s_p < s_n} + 0.5 #{(p, n): s_p == s_n}) / (|P| |N|).
  Coverage     a + r (g + 1) / (r + 1) - 1, where s* = min over P of s_p,
               a = #{j: s_j > s*}, g = #{j: s_j == s*}, r = #{p in P: s_p == s*}.
               The last relevant label among r of g randomly ordered slots
               sits at expected position r (g + 1) / (r + 1).
  AvgPrecision mean over p in P of E[prec_p]. Let p's tie group have size g with
               r relevant labels (p included), and let A (A_rel) be the number
               of labels (relevant labels) scored strictly above p. p sits at
               slot j, uniform on 1..g, so its rank is A + j. The relevant
               labels ahead of p inside the group number on average
               (j - 1)(r - 1)/(g - 1), so
               E[prec_p] = (1/g) sum_j (A_rel + 1 + (j-1)(r-1)/(g-1)) / (A + j).
"""
import numpy as np

RANKING_METRICS = ("OneError", "Coverage", "RankingLoss", "AveragePrecision")


def _rows(Y, S):
    Y = np.asarray(Y) > 0
    S = np.asarray(S, dtype=np.float64)
    if Y.shape != S.shape or Y.ndim != 2:
        raise ValueError(f"shape mismatch: Y {Y.shape}, scores {S.shape}")
    if Y.shape[1] < 2:
        raise ValueError("ranking metrics need at least 2 labels")
    if not np.all(np.isfinite(S)):
        raise ValueError("non-finite score")
    return Y, S


def one_error(Y, S):
    Y, S = _rows(Y, S)
    vals = []
    for y, s in zip(Y, S):
        if not y.any():
            continue
        top = s == s.max()
        vals.append(1.0 - y[top].sum() / top.sum())
    return float(np.mean(vals)) if vals else 0.0


def coverage(Y, S):
    Y, S = _rows(Y, S)
    vals = []
    for y, s in zip(Y, S):
        if not y.any():
            continue
        s_star = s[y].min()
        a = int((s > s_star).sum())
        g = int((s == s_star).sum())
        r = int((y & (s == s_star)).sum())
        vals.append(a + r * (g + 1) / (r + 1) - 1.0)
    return float(np.mean(vals)) if vals else -1.0


def ranking_loss(Y, S):
    Y, S = _rows(Y, S)
    vals = []
    for y, s in zip(Y, S):
        npos = int(y.sum())
        if npos == 0 or npos == len(y):
            vals.append(0.0)
            continue
        sp, sn = s[y][:, None], s[~y][None, :]
        bad = (sp < sn).sum() + 0.5 * (sp == sn).sum()
        vals.append(bad / (npos * (len(y) - npos)))
    return float(np.mean(vals))


def average_precision(Y, S):
    Y, S = _rows(Y, S)
    vals = []
    for y, s in zip(Y, S):
        if not y.any():
            continue
        precs = []
        for p in np.flatnonzero(y):
            same = s == s[p]
            g = int(same.sum())
            r = int((y & same).sum())
            above = s > s[p]
            A = int(above.sum())
            A_rel = int((y & above).sum())
            j = np.arange(1, g + 1, dtype=np.float64)
            ahead = (j - 1) * (r - 1) / (g - 1) if g > 1 else np.zeros(1)
            precs.append(float(np.mean((A_rel + 1 + ahead) / (A + j))))
        vals.append(np.mean(precs))
    return float(np.mean(vals)) if vals else 0.0


def ranking_four(Y, S):
    """The four tie-neutral ranking metrics, keyed as in miml_metrics.AllFive."""
    return {"OneError": one_error(Y, S), "Coverage": coverage(Y, S),
            "RankingLoss": ranking_loss(Y, S), "AveragePrecision": average_precision(Y, S)}


def mulan_ranks(s, small=1e-6):
    """Mulan 1.5 MultiLabelOutput.ranksFromValues via weka Utils.stableSort:
    values within weka's Utils.SMALL (1e-6) of a run's FIRST element are tied
    (not chained through neighbours), and a tie is broken by label index, the
    later label ranking higher. Verified against `javap -c weka.core.Utils`
    (stableSort, eq, <clinit>: SMALL = 1.0E-6) in the shipped KDIS jar and
    against ranksFromValues called from Java on 3 002 rows (review A1-1).
    Rank 1 = top. Used only for the sensitivity rows (AMENDMENT.md A1)."""
    s = np.asarray(s, dtype=np.float64)
    order = list(np.argsort(s, kind="stable"))
    out, i = [], 0
    while i < len(order):
        k = i + 1
        while k < len(order) and abs(s[order[k]] - s[order[i]]) < small:
            k += 1
        out += sorted(order[i:k])
        i = k
    ranks = np.empty(len(s), dtype=np.int64)
    ranks[np.array(out)] = len(s) - np.arange(len(s))
    return ranks


def ranking_four_mulan(Y, S):
    """The four ranking metrics exactly as Mulan 1.5 computes them (sensitivity
    only): Mulan's ranks (mulan_ranks) and Mulan's bag conventions, which
    differ from miml_metrics.py on bags with no relevant label. OneError counts
    such a bag as an error (its top label is never relevant); Coverage counts it
    with depth 0; AveragePrecision skips it; RankingLoss gives 0 to a bag with no
    relevant or no irrelevant label. Every bag counts in the denominator except
    the ones AveragePrecision skips (mulan/evaluation/measure/*.java, loss/*.java)."""
    Y, S = _rows(Y, S)
    oe, cov, rl, ap = [], [], [], []
    for y, s in zip(Y, S):
        r = mulan_ranks(s)
        oe.append(0.0 if y[np.argmin(r)] else 1.0)
        cov.append(float(r[y].max() - 1) if y.any() else 0.0)
        P, N = np.flatnonzero(y), np.flatnonzero(~y)
        rl.append(float((r[P][:, None] > r[N][None, :]).sum()) / (len(P) * len(N))
                  if len(P) and len(N) else 0.0)
        if len(P):
            ap.append(float(np.mean([(r[P] <= r[p]).sum() / r[p] for p in P])))
    return {"OneError": float(np.mean(oe)), "Coverage": float(np.mean(cov)),
            "RankingLoss": float(np.mean(rl)),
            "AveragePrecision": float(np.mean(ap)) if ap else 0.0}
