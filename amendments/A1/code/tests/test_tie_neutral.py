"""Tests for tie_neutral_metrics.py (AMENDMENT.md A1)."""
import itertools
import os
import sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "..", "MIML_CLAM_Release"))

import tie_neutral_metrics as tn  # noqa: E402
from miml_clam.metrics.miml_metrics import (  # noqa: E402
    AveragePrecision, CoverageError, OneErrorLoss, RankingLoss)

MM = {"OneError": OneErrorLoss, "Coverage": CoverageError,
      "RankingLoss": RankingLoss, "AveragePrecision": AveragePrecision}


def _labels(rng, n, L, allow_empty=True, allow_full=True):
    Y = (rng.random((n, L)) < 0.35).astype(int)
    if allow_empty:
        Y[0] = 0
    if allow_full:
        Y[1] = 1
    return Y


def test_equals_miml_metrics_without_ties():
    rng = np.random.default_rng(0)
    for L in (2, 5, 26):
        Y = _labels(rng, 60, L)
        S = rng.random((60, L))
        assert all(len(np.unique(r)) == L for r in S)
        got = tn.ranking_four(Y, S)
        for k, f in MM.items():
            assert got[k] == pytest.approx(float(f(Y.astype(float), S)), abs=1e-12), (k, L)


def _brute(Y, S):
    """Exact average over every tie order: each of the L! label permutations is
    used as a secondary key, which makes every within-group order equally likely."""
    L = S.shape[1]
    acc = {k: 0.0 for k in MM}
    perms = list(itertools.permutations(range(L)))
    for perm in perms:
        key = np.array(perm, dtype=np.float64)
        R = np.empty_like(S)
        for i, s in enumerate(S):
            order = np.lexsort((key, -s))          # best first
            R[i, order] = L - np.arange(L)          # strictly ordered scores
        for k, f in MM.items():
            acc[k] += float(f(Y.astype(float), R))
    return {k: v / len(perms) for k, v in acc.items()}


@pytest.mark.parametrize("seed", range(6))
def test_matches_brute_force_enumeration_with_heavy_ties(seed):
    rng = np.random.default_rng(100 + seed)
    L = 6
    Y = _labels(rng, 12, L)
    S = rng.integers(0, 3, size=(12, L)).astype(np.float64)   # few distinct values
    S[2] = 0.0                                                 # a fully tied row
    exact = _brute(Y, S)
    got = tn.ranking_four(Y, S)
    for k in MM:
        assert got[k] == pytest.approx(exact[k], abs=1e-12), k


def test_binary_scores_example():
    # one bag, scores {0,1}: P = {0, 2}; label 0 scored 1, labels 1-3 scored 0.
    Y = np.array([[1, 0, 1, 0]])
    S = np.array([[1.0, 0.0, 0.0, 0.0]])
    got = tn.ranking_four(Y, S)
    assert got["OneError"] == 0.0
    # pairs: (0,1),(0,3) correct; (2,1),(2,3) tied -> 0.5 each -> 1 / 4
    assert got["RankingLoss"] == pytest.approx(0.25)
    # lowest relevant (label 2) is tied with 2 others at s*=0: a=1, g=3, r=1 -> 1 + 2 - 1
    assert got["Coverage"] == pytest.approx(2.0)


def test_mulan_convention_reproduces_known_ranks():
    s = np.array([0.5, 0.5 + 5e-7, 0.9, 0.1])
    # 0.5 and 0.5+5e-7 tie under SMALL=1e-6; the later label (1) ranks higher.
    assert list(tn.mulan_ranks(s)) == [3, 2, 1, 4]


@pytest.mark.parametrize("s, ranks", [
    # Java-verified (MultiLabelOutput.ranksFromValues, review A1-1 finding 9).
    # First-element grouping: 0 and 6e-7 tie, 1.2e-6 is > SMALL from 0 and starts
    # a new run with 1.8e-6; neighbour chaining would give [2, 3, 4, 5, 1].
    ([1.8e-6, 1.2e-6, 6e-7, 0.0, 0.5], [3, 2, 5, 4, 1]),
    # A tie in which the later label has the SMALLER value: exact ordering
    # (small = 0) would give [2, 3, 1, 4].
    ([0.5 + 5e-7, 0.5, 0.9, 0.1], [3, 2, 1, 4]),
])
def test_mulan_tolerance_and_first_element_grouping(s, ranks):
    assert list(tn.mulan_ranks(np.array(s))) == ranks


def test_edge_cases_follow_miml_metrics():
    Y = np.zeros((3, 4), dtype=int)                 # no relevant label anywhere
    S = np.random.default_rng(1).random((3, 4))
    got = tn.ranking_four(Y, S)
    assert got["Coverage"] == float(CoverageError(Y.astype(float), S)) == -1.0
    assert got["OneError"] == float(OneErrorLoss(Y.astype(float), S)) == 0.0
    assert got["AveragePrecision"] == float(AveragePrecision(Y.astype(float), S)) == 0.0
    with pytest.raises(ValueError):
        tn.ranking_four(np.ones((3, 1)), np.ones((3, 1)))


def test_rejects_bad_input():
    with pytest.raises(ValueError):
        tn.ranking_four(np.zeros((2, 3)), np.zeros((2, 4)))
    with pytest.raises(ValueError):
        tn.ranking_four(np.ones((1, 2)), np.array([[np.nan, 0.0]]))
