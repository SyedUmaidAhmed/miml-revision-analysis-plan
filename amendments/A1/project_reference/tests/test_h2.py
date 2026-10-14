"""Synthetic-data tests for h2a_rebuild.py and h2b_masks.py (task T02).

No real dataset is read. A toy multi-label set is generated, k-NN-bagged by the
original (leaky) recipe of T01 A, and written as a .mat, a _10CV.mat and a
provenance CSV in the format of experiments/provenance/verify_knn_bags.py.
Each test cites the PREREGISTERED.md rule it checks.

Run: ./.venv/bin/python -m pytest experiments/revision_r1/tests -q
"""
import os
import subprocess
import sys
from fractions import Fraction
import math

import numpy as np
import pytest
from scipy.io import savemat

HERE = os.path.dirname(os.path.abspath(__file__))
R1 = os.path.dirname(HERE)
PROJECT = os.path.dirname(os.path.dirname(R1))
PY = sys.executable
sys.path.insert(0, R1)

import h2_common as hc  # noqa: E402
import h2a_rebuild as h2a  # noqa: E402
import h2b_masks as h2b  # noqa: E402

N, D, L = 103, 5, 4         # n mod 10 = 3, like Emotions and Corel5K; pools of 10
P = N // 10                 # pool size before any duplicate drop
NP = 10 * P                 # pooled rows (remainder excluded)


# --------------------------------------------------------------------------- toy data

def _perm(n):
    return np.random.RandomState(42).permutation(n)


def toy_rows(cross_pool_dup):
    """Integer features in {0,1,2,3} (many exact distance ties) plus one constant
    column (zero variance). Rows 0..n-1 are the source rows. One duplicate pair
    inside a canonical pool, optionally one duplicate pair spanning two pools,
    rows are otherwise distinct."""
    rng = np.random.default_rng(7)
    grid = np.array(np.meshgrid(*[np.arange(4)] * (D - 1), indexing="ij")).reshape(D - 1, -1).T
    rows = grid[rng.choice(len(grid), size=N, replace=False)].astype(np.float64)  # distinct
    X = np.insert(rows, 2, 4.0, axis=1)             # zero-variance column 2
    blocks = _perm(N)[: (N // 10) * 10].reshape(10, -1)
    a, b = sorted(blocks[2][:2])                    # same pool
    X[b] = X[a]
    if cross_pool_dup:
        c, d = sorted([blocks[4][0], blocks[7][0]])  # different pools
        X[d] = X[c]
    Y = (rng.random((N, L)) < 0.35).astype(np.int8)
    Y[:, 3] = 0                                      # a label with no positive bag
    return X, Y


def leaky_bags(X):
    """The original recipe (T01 A): scaler and neighbour index on ALL rows,
    bag i = row i + 4 nearest others; stored raw."""
    from sklearn.preprocessing import StandardScaler
    Xs = StandardScaler().fit_transform(X)
    bags = []
    for i in range(len(X)):
        cand = np.delete(np.arange(len(X)), i)
        d2 = ((Xs[cand] - Xs[i]) ** 2).sum(1)
        nb = cand[np.lexsort((cand, d2))[:4]]
        bags.append(X[np.concatenate([[i], nb])])
    return bags


def write_toy(tmp, cross_pool_dup=False):
    X, Y = toy_rows(cross_pool_dup)
    bags = leaky_bags(X)
    mat = os.path.join(tmp, "toy.mat")
    cv = os.path.join(tmp, "toy_10CV.mat")
    csv = os.path.join(tmp, "provenance_bag_rows_toy.csv")
    cell = np.empty((N, 1), dtype=object)
    for i, b in enumerate(bags):
        cell[i, 0] = b
    savemat(mat, {"bags": cell, "labels": np.where(Y > 0, 1, -1).astype(np.int32)})
    savemat(cv, {"Indexes": (_perm(N) + 1).astype(np.uint16)[None, :]})
    # CSV exactly as verify_knn_bags.source_check writes it.
    rows_of = {}
    for r, row in enumerate(X):
        rows_of.setdefault(row.tobytes(), []).append(r)
    with open(csv, "w") as fh:
        fh.write("bag,centre_row,member_rows\n")
        for i, b in enumerate(bags):
            rws = [rows_of[r.tobytes()] for r in b]
            fh.write(f"{i},{rws[0][0] if i not in rws[0] else i},"
                     f"{' '.join(str(r[0]) for r in rws[1:])}\n")
    return {"X": X, "Y": Y, "bags": bags, "mat": mat, "cv": cv, "csv": csv}


@pytest.fixture
def toy(tmp_path):
    return write_toy(str(tmp_path))


@pytest.fixture
def toy_cross(tmp_path):
    return write_toy(str(tmp_path), cross_pool_dup=True)


def splits_of(t):
    return hc.canonical_splits(t["cv"], N)


def ref_bag(Xs, pool, i, rtol=h2a.TIE_RTOL):
    """Independent reference for step 3: pure Python; squared direct differences
    summed exactly as rationals, rounded once; tie groups within rtol of their
    first member; order (group, index)."""
    cand = [j for j in pool if j != i]
    d = {j: math.sqrt(float(sum((Fraction((float(Xs[j, c]) - float(Xs[i, c])) ** 2)
                                 for c in range(Xs.shape[1])), Fraction(0)))) for j in cand}
    grp, lead, g = {}, None, -1
    for j in sorted(cand, key=lambda j: (d[j], j)):
        if lead is None or d[j] - lead > rtol * lead:
            g, lead = g + 1, d[j]
        grp[j] = g
    return [i] + sorted(cand, key=lambda j: (grp[j], j))[:4]


def test_true_tie_split_by_rounding(toy):
    """Why a tie tolerance (T02 Q4): find a row i and candidates j1 < j2 of its
    pool whose raw differences from i are equal in every column up to sign (a
    true tie), whose scaled float distances nevertheless differ, with j1 the
    farther in float. With rtol = 1e-9 the plan's rule applies (j1 first);
    with rtol = 0 rounding puts j2 first."""
    X = toy["X"]
    pools, rem = h2a.pools_from_splits(splits_of(toy), N)
    fit = np.concatenate(pools[1:])
    _, _, Xs = h2a.fit_scaler(X, fit)
    dist = lambda a, b: math.sqrt(math.fsum(((Xs[a] - Xs[b]) ** 2).tolist()))
    found = None
    for p in pools:
        for i in p:
            for j1 in p:
                for j2 in p:
                    if i in (j1, j2) or j1 >= j2:
                        continue
                    if np.array_equal(np.abs(X[j1] - X[i]), np.abs(X[j2] - X[i])) and dist(i, j1) > dist(i, j2):
                        _, mem, _, _ = h2a.pool_bags(Xs, p)
                        bag = [m for m in mem if m[0] == i][0].tolist()
                        if j1 in bag and j2 in bag:
                            found = (p, int(i), int(j1), int(j2), bag)
                            break
                if found: break
            if found: break
        if found: break
    assert found, "toy has no rounding-split tie; change the toy seed"
    p, i, j1, j2, bag = found
    assert abs(dist(i, j1) - dist(i, j2)) < 1e-12 * dist(i, j1)
    assert bag.index(j1) < bag.index(j2)
    _, mem0, _, _ = h2a.pool_bags(Xs, p, tie_rtol=0.0)
    bag0 = [m for m in mem0 if m[0] == i][0].tolist()
    assert j2 in bag0 and (j1 not in bag0 or bag0.index(j2) < bag0.index(j1))


# --------------------------------------------------------------------------- inputs

def test_loader_and_identity(toy):
    """T01 3 identity mapping: row i = bags[i][0]; labels are {0,1}."""
    bags, Y = hc.load_constructed(toy["mat"])
    X = hc.source_rows(bags)
    assert np.array_equal(X, toy["X"]) and np.array_equal(Y, toy["Y"])


def test_vector_id_map(toy_cross):
    """H2-B round 4 m1: a row identical to a lower-indexed row takes that row's id."""
    X = toy_cross["X"]
    vid = hc.vector_id_map(X)
    for r in range(N):
        same = [q for q in range(N) if np.array_equal(X[q], X[r])]
        assert vid[r] == min(same)
    assert np.sum(vid != np.arange(N)) == 2


# --------------------------------------------------------------------------- H2-A

def test_pools_and_remainder(toy):
    """Step 1: ten pools of floor(n/10), disjoint; n mod 10 remainder rows."""
    pools, rem = h2a.pools_from_splits(splits_of(toy), N)
    assert [len(p) for p in pools] == [N // 10] * 10
    assert len(rem) == N % 10 == 3
    assert set(np.concatenate(pools)) | set(rem) == set(range(N))
    assert np.array_equal(np.sort(rem), np.sort(_perm(N)[NP:]))


def test_scaler_outer_training_rows_only(toy):
    """Step 2: ddof 0, zero-variance column unscaled, fit on the nine training pools only."""
    X = toy["X"]
    pools, rem = h2a.pools_from_splits(splits_of(toy), N)
    fit = np.concatenate([pools[g] for g in range(10) if g != 3])
    mean, scale, Xs = h2a.fit_scaler(X, fit)
    assert np.allclose(mean, X[fit].mean(0))
    sd = X[fit].std(0, ddof=0)
    assert scale[2] == 1.0 and np.allclose(scale[sd > 0], sd[sd > 0])
    assert np.allclose(Xs, (X - mean) / scale)


@pytest.mark.parametrize("cross", [False, True])
def test_split_rules(tmp_path, cross):
    """Steps 0-5 on every split, on both toys: bags within own (post-drop) pool,
    reference neighbours with the lower-index tie rule, raw instances, centre
    labels, remainder and dropped rows excluded, ascending training order,
    inner folds of 2,2,2,2,1 pools, zero overlap by row and by vector id."""
    toy = write_toy(str(tmp_path), cross_pool_dup=cross)
    X, Y = toy["X"], toy["Y"]
    raw, rem = h2a.pools_from_splits(splits_of(toy), N)
    vid = hc.vector_id_map(X)
    pools, dropped, _ = h2a.drop_duplicates(raw, rem, vid, Y)
    out, meta = h2a.build_dataset(X, Y, splits_of(toy))
    for f in range(10):
        arr, diag = out[f"r0_f{f}.npz"], meta["splits"][f]
        fit = np.concatenate([pools[g] for g in range(10) if g != f])
        _, _, Xs = h2a.fit_scaler(X, fit)
        pool_of = {int(r): g for g, p in enumerate(pools) for r in p}
        for ids, mem in ((arr["train_bag_ids"], arr["train_members"]),
                         (arr["test_bag_ids"], arr["test_members"])):
            for i, m in zip(ids, mem):
                assert m.tolist() == ref_bag(Xs, sorted(pools[pool_of[int(i)]]), int(i))
        assert np.array_equal(arr["train_bag_ids"], np.sort(fit))
        assert np.array_equal(arr["test_bag_ids"], pools[f])
        used = set(arr["train_members"].ravel()) | set(arr["test_members"].ravel())
        assert not used & set(rem) and not used & set(dropped)
        assert np.array_equal(arr["dropped_rows"], dropped)
        assert np.array_equal(arr["Y_train"], Y[arr["train_bag_ids"]])
        assert np.array_equal(arr["Y_test"], Y[arr["test_bag_ids"]])
        inner_pools = [len({pool_of[int(i)] for i, q in zip(arr["train_bag_ids"], arr["train_inner_fold"]) if q == k})
                       for k in range(5)]
        assert inner_pools == [2, 2, 2, 2, 1]
        for q, gs in diag["inner_fold_pools"].items():
            ranks = [sorted(g for g in range(10) if g != f).index(g) for g in gs]
            assert all(r % 5 == int(q) for r in ranks)
        assert all(v == 0 for v in diag["overlap_source_rows"].values())
        assert all(v == 0 for v in diag["overlap_vector_ids"].values())


def test_tie_lower_index_wins():
    """Step 3 / F14: equal distances go to the lower source index."""
    Xs = np.array([[0.0, 0], [1, 0], [0, 1], [-1, 0], [0, -1], [2, 0], [0, 2]])
    pool = np.array([6, 5, 4, 3, 2, 1, 0])
    rows, mem, _, _ = h2a.pool_bags(Xs, pool)
    a = list(rows).index(0)
    assert mem[a].tolist() == [0, 1, 2, 3, 4]          # four rows at distance 1
    # Five rows tie at distance 1 for row 0; only the four lowest indices fit.
    Xs2 = np.vstack([Xs[:5], [[np.sqrt(0.5), np.sqrt(0.5)]], [[3, 3]]])
    Xs2[5] = Xs2[1]                                     # exact copy: distance 1 exactly
    rows, mem, btie, exact = h2a.pool_bags(Xs2, pool)
    a = list(rows).index(0)
    assert mem[a].tolist() == [0, 1, 2, 3, 4] and btie[a] and exact[a]
    pool_rev = np.array([5, 4, 3, 2, 1, 0, 6])          # input order is irrelevant
    _, mem2, _, _ = h2a.pool_bags(Xs2, pool_rev)
    assert np.array_equal(mem, mem2)


def test_duplicates_dropped_before_pooling(toy_cross):
    """Rule B (addendum, T02 Q2): later duplicates dropped before pooling, lowest
    index kept, label-agnostic; absent from bags, candidates, scaler fit and
    test pools; pool sizes asserted before, reported after; label conflicts recorded."""
    X, Y = toy_cross["X"], toy_cross["Y"].copy()
    vid = hc.vector_id_map(X)
    later = np.flatnonzero(vid != np.arange(N))
    assert len(later) == 2
    Y[later[0]] = 1 - Y[vid[later[0]]]                   # force one label conflict
    out, meta = h2a.build_dataset(X, Y, splits_of(toy_cross))
    rep = meta["duplicates"]
    assert rep["n_dropped_rows"] == 2 and rep["n_dropped_rows_labels_differ"] >= 1
    assert [r["row"] for r in rep["dropped_rows"]] == later.tolist()
    assert all(r["kept_row"] == vid[r["row"]] < r["row"] for r in rep["dropped_rows"])
    assert rep["dropped_rows"][0]["labels_differ_from_kept_row"]
    assert rep["pool_sizes_before"] == [P] * 10
    assert sum(rep["pool_sizes_after"]) == NP - 2
    for f in range(10):
        a = out[f"r0_f{f}.npz"]
        assert not set(later) & (set(a["train_bag_ids"]) | set(a["test_bag_ids"]))
        assert not set(later) & (set(a["train_members"].ravel()) | set(a["test_members"].ravel()))
        fit = a["train_bag_ids"]
        assert np.allclose(a["scaler_mean"], X[fit].mean(0))   # scaler never saw a dropped row
        assert meta["splits"][f]["duplicates"]["duplicate_groups"] == 0


def test_remainder_guard(tmp_path):
    """Rule B (d): if a group's lowest row is a remainder row, the vector leaves H2-A."""
    t = write_toy(str(tmp_path))
    X, Y = t["X"].copy(), t["Y"]
    perm = _perm(N)
    r0 = int(perm[NP:].min())                            # a remainder row
    later = next(int(r) for r in perm[:NP] if r > r0)    # a pooled row with higher index
    X[later] = X[r0]
    out, meta = h2a.build_dataset(X, Y, splits_of(t))
    rep = meta["duplicates"]
    assert r0 in rep["vectors_leaving_h2a_lowest_row_in_remainder"]
    for a in out.values():
        used = set(a["train_members"].ravel()) | set(a["test_members"].ravel())
        assert later not in used and r0 not in used


def test_overlap_check_stops_on_injected_bug(toy):
    """Step 4 / H2: a non-zero source-example overlap is a construction bug."""
    tr = np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]])
    te = np.array([[10, 11, 12, 13, 4]])                 # row 4 in both
    ov = h2a.overlap(tr, te, np.arange(20))
    assert ov["frac_test_bags_sharing_an_example_with_train"] == 1.0
    assert ov["frac_test_instances_in_train_bags"] == pytest.approx(0.2)
    X, Y = toy["X"], toy["Y"]
    pools, rem = h2a.pools_from_splits(splits_of(toy), N)
    bad = [p.copy() for p in pools]
    bad[1] = bad[1].copy(); bad[1][0] = bad[0][0]        # same row in two pools
    with pytest.raises(hc.ConstructionBug):
        h2a.pools_from_splits([(None, p) for p in bad], N)
    real = h2a.overlap
    try:
        h2a.overlap = lambda a, b, ident: dict(real(a, b, ident), frac_test_centres_in_train_bags=0.1)
        with pytest.raises(hc.ConstructionBug):
            h2a.build_split(X, Y, pools, rem, 0)
    finally:
        h2a.overlap = real


def test_vector_overlap_hard_stop(toy_cross):
    """Rule B: vector-level overlap is a hard stop. Without the drop, the
    cross-pool duplicate pair overlaps by vector id (not by row) and must stop."""
    X, Y = toy_cross["X"], toy_cross["Y"]
    raw, rem = h2a.pools_from_splits(splits_of(toy_cross), N)
    with pytest.raises(hc.ConstructionBug, match="vector-id overlap"):
        for f in range(10):
            h2a.build_split(X, Y, raw, rem, f)
    out, meta = h2a.build_dataset(X, Y, splits_of(toy_cross))   # with the drop: passes
    assert len(out) == 10


def test_materialise_raw_features(toy, tmp_path):
    """Step 3: stored instances are raw; materialised bags equal source rows."""
    out = str(tmp_path / "out")
    h2a.run("toy", toy["mat"], toy["cv"], out)
    tb, ytr, sb, yte = h2a.materialise(os.path.join(out, "toy", "rebuilt", "r0_f0.npz"), toy["X"])
    z = np.load(os.path.join(out, "toy", "rebuilt", "r0_f0.npz"))
    for b, m in zip(tb, z["train_members"]):
        assert np.array_equal(b, toy["X"][m]) and np.array_equal(b[0], toy["X"][m[0]])
    assert len(tb) == len(z["train_bag_ids"]) and len(sb) == len(z["test_bag_ids"])
    assert len(tb) + len(sb) == NP - 1                   # one within-pool duplicate dropped
    assert all(len(b) == 5 for b in tb + sb)


def _tree(root):
    out = {}
    for d, _, fs in os.walk(root):
        for f in fs:
            p = os.path.join(d, f)
            out[os.path.relpath(p, root)] = open(p, "rb").read()
    return out


def test_h2a_cli_deterministic_and_no_overwrite(toy, tmp_path):
    """1.5: byte-identical reruns, manifest, and refusal to overwrite."""
    args = ["--datasets", "toy", "--data-mat", toy["mat"], "--cv-mat", toy["cv"]]
    o1, o2 = str(tmp_path / "o1"), str(tmp_path / "o2")
    assert h2a.main(args + ["--out-root", o1]) == 0
    assert h2a.main(args + ["--out-root", o2]) == 0
    t1, t2 = _tree(o1), _tree(o2)
    assert t1 == t2 and len(t1) == 12
    man = t1[os.path.join("toy", "rebuilt", "MANIFEST.sha256")].decode().splitlines()
    assert len(man) == 11
    with pytest.raises(hc.RefuseOverwrite):
        h2a.main(args + ["--out-root", o1])
    assert _tree(o1) == t1


def test_h2a_dry_run_writes_nothing(tmp_path):
    out = str(tmp_path / "dry")
    r = subprocess.run([PY, os.path.join(R1, "h2a_rebuild.py"), "--dry-run", "--out-root", out],
                       capture_output=True, text=True)
    assert r.returncode == 0 and r.stdout.count("plan ") == 4 * 12
    assert not os.path.exists(out)


CANONICAL = "https://doi.org/10.5281/zenodo.1234567 (2026-10-20)"


@pytest.fixture
def pinned_today(monkeypatch):
    """Pin deposit_check's reference date (its 'date <= today UTC' rule) to the
    CANONICAL date, so the open cases do not depend on the machine's clock."""
    import datetime
    import deposit_check
    monkeypatch.setattr(deposit_check, "_today", lambda: datetime.date(2026, 10, 20))


def _plan_with(path, cell, line=8, label="| Public timestamp |"):
    """A plan file whose `line`-th line is the Public-timestamp row (shared rule: line 8)."""
    rows = [f"| header row {i} | x |" for i in range(1, line)] + [f"{label} {cell} |", "rest"]
    path.write_text("\n".join(rows) + "\n")
    return str(path)


def _real_utc_today():
    import datetime
    return datetime.datetime.now(datetime.timezone.utc).date()


def _plan_deposited():
    """Is the REAL plan deposited, under the REAL clock? Used in skipif
    decorators, which are evaluated at collection, before any fixture (such as
    pinned_today) applies (code review 7)."""
    try:
        hc.deposit_guard()
    except hc.NotDeposited:
        return False
    return True


def test_scratch_plan_guard_opens_only_when_recorded(tmp_path, pinned_today):
    """6.0 step 0 on scratch plans (clock pinned): PENDING closes, the canonical line opens."""
    plan = tmp_path / "plan.md"
    with pytest.raises(hc.NotDeposited):
        hc.deposit_guard(_plan_with(plan, "**PENDING (user action).**"))
    assert "10.5281/zenodo.1234567" in hc.deposit_guard(_plan_with(plan, CANONICAL))


@pytest.mark.skipif(_plan_deposited(), reason="plan deposited; the real-data refusal no longer applies")
def test_real_data_refused_before_deposit(tmp_path):
    """6.0 step 0 on the real plan, real clock only (no pinned_today): the
    builders' CLIs refuse a real dataset. The subprocesses use the real clock
    too, so the skip decision and the refusal cannot disagree (code review 7)."""
    for script in ("h2a_rebuild.py", "h2b_masks.py"):
        r = subprocess.run([PY, os.path.join(R1, script), "--datasets", "emotions",
                            "--out-root", str(tmp_path / "x")], capture_output=True, text=True)
        assert r.returncode != 0 and "NotDeposited" in r.stderr
        assert not os.path.exists(tmp_path / "x")


# --------------------------------------------------------------------------- H2-B

def _b_inputs(t):
    bags, _ = hc.load_constructed(t["mat"])
    X = hc.source_rows(bags)
    vid = hc.vector_id_map(X)
    ids = h2b.bag_vector_ids(hc.read_bag_rows_csv(t["csv"]), vid, bags, X)
    return bags, X, vid, ids


def test_csv_mapping_checked_against_mat(toy_cross, tmp_path):
    """H2-B: CSV centres mapped to vector ids; every position matches the .mat."""
    bags, X, vid, ids = _b_inputs(toy_cross)
    for i, v in enumerate(ids):
        assert np.array_equal(X[v], bags[i]) and v[0] == vid[i]
    rows = hc.read_bag_rows_csv(toy_cross["csv"])
    wrong = next(r for r in range(N) if vid[r] == r and r not in rows[5][2] and r != 5)
    rows[5] = (5, 5, [wrong] + rows[5][2][1:])          # a member that is not in the bag
    with pytest.raises(hc.ConstructionBug, match="disagrees"):
        h2b.bag_vector_ids(rows, vid, bags, X)
    dup = int(np.flatnonzero(vid != np.arange(N))[0])   # a duplicate row's own index
    rows = hc.read_bag_rows_csv(toy_cross["csv"])
    rows[0] = (0, 0, [dup] + rows[0][2][1:])            # members must be lowest indices
    with pytest.raises(hc.ConstructionBug, match="lowest index"):
        h2b.bag_vector_ids(rows, vid, bags, X)


def test_centre_position_first_equal_instance():
    """H2-B: centre = first instance equal to source row i; later copies are non-centre."""
    vid = np.array([0, 1, 1, 3])                         # row 2 duplicates row 1
    assert h2b.centre_position(2, np.array([3, 1, 0, 1, 3]), vid) == 1
    with pytest.raises(hc.ConstructionBug):
        h2b.centre_position(0, np.array([3, 1, 1]), vid)


def test_leak_purge_rules(toy_cross):
    """H2-B leak purge: deletes exactly the training instances whose vector id is
    in S_f (test centres as vector ids included); zero test vectors survive;
    emptied bags dropped from the surviving list; test bag ids untouched."""
    bags, X, vid, ids = _b_inputs(toy_cross)
    splits = splits_of(toy_cross)
    out, stats, summary = h2b.build_dataset(ids, vid, splits)
    for f, (tr, te) in enumerate(splits):
        S = {int(v) for j in te for v in ids[j]}
        assert S >= {int(vid[j]) for j in te}
        z = out[f"leak/r0_f{f}.npz"]
        off, keep = z["bag_offsets"], z["keep"]
        for b, i in enumerate(tr):
            want = np.array([int(v) not in S for v in ids[i]])
            assert np.array_equal(keep[off[b]:off[b + 1]], want)
        surviving = [i for b, i in enumerate(tr) if keep[off[b]:off[b + 1]].any()]
        assert z["surviving_bag_ids"].tolist() == list(surviving)
        left = {int(v) for b, i in enumerate(tr) for v in ids[i][keep[off[b]:off[b + 1]]]}
        assert not left & S
        assert np.array_equal(z["test_bag_ids"], te) and np.array_equal(z["train_bag_ids"], tr)
        assert stats[f]["frac_training_rows_removed"] == pytest.approx(1 - keep.mean())


def test_leak_check_stops_on_injected_bug(toy):
    """H2-B: a test vector left in a surviving training bag stops the run."""
    bags, X, vid, ids = _b_inputs(toy)
    tr, te = splits_of(toy)[0]
    S = {int(v) for j in te for v in ids[j]}
    fm = h2b.fold_masks(ids, vid, tr, te)
    h2b.check_leak(ids, tr, fm["masks"]["leak"], S)          # the real mask passes
    keep_all = np.ones_like(fm["masks"]["leak"])
    with pytest.raises(hc.ConstructionBug, match="test vector"):
        h2b.check_leak(ids, tr, keep_all, S)
    one = fm["masks"]["leak"].copy()
    one[np.flatnonzero(~one)[0]] = True                       # restore one purged row
    with pytest.raises(hc.ConstructionBug):
        h2b.check_leak(ids, tr, one, S)


def test_control_stratified_and_matched(toy_cross):
    """H2-B control: per bag the same count as the leak purge; centre deleted iff
    the leak purge deleted it; other deletions only among non-centre rows;
    k = 5 bags emptied in both; seeds reproducible and different."""
    bags, X, vid, ids = _b_inputs(toy_cross)
    splits = splits_of(toy_cross)
    out, stats, _ = h2b.build_dataset(ids, vid, splits)
    for f, (tr, te) in enumerate(splits):
        L_ = out[f"leak/r0_f{f}.npz"]
        off, cpos, k, cdel = L_["bag_offsets"], L_["centre_pos"], L_["n_deleted"], L_["centre_deleted"]
        for s in h2b.SEEDS:
            C = out[f"control-s{s}/r0_f{f}.npz"]["keep"]
            for b in range(len(tr)):
                seg = C[off[b]:off[b + 1]]
                assert (~seg).sum() == k[b]
                assert (not seg[cpos[b]]) == cdel[b]
                if k[b] == 5:
                    assert not seg.any()
            assert np.array_equal(out[f"control-s{s}/r0_f{f}.npz"]["surviving_bag_ids"],
                                  L_["surviving_bag_ids"])
            # Reference consumption of default_rng(seed), fresh per fold (Q3).
            rng = np.random.default_rng(s)
            ref = np.ones(off[-1], dtype=bool)
            for b in range(len(tr)):
                if cdel[b]:
                    ref[off[b] + cpos[b]] = False
                m = int(k[b] - cdel[b])
                if m:
                    ref[off[b] + rng.choice(np.delete(np.arange(5), cpos[b]), size=m, replace=False)] = False
            assert np.array_equal(C, ref)
        cs = [out[f"control-s{s}/r0_f{f}.npz"]["keep"] for s in h2b.SEEDS]
        assert not (np.array_equal(cs[0], cs[1]) and np.array_equal(cs[1], cs[2]))
        assert stats[f]["centre_deleted_rate_surviving_bags"] == pytest.approx(
            cdel[k < 5].mean() if (k < 5).any() else 0.0)


def test_control_check_rejects_mismatch(toy):
    bags, X, vid, ids = _b_inputs(toy)
    tr, te = splits_of(toy)[0]
    fm = h2b.fold_masks(ids, vid, tr, te)
    h2b.check_control(fm)
    b = int(np.flatnonzero((fm["n_deleted"] > 0) & (fm["n_deleted"] < 5))[0])
    o = fm["offsets"][b]
    fm["masks"]["control-s0"][o:o + 5] = True            # deletes nothing
    with pytest.raises(hc.ConstructionBug):
        h2b.check_control(fm)


def test_stats_and_not_estimable():
    """H2-B descriptive statistics, and 'not estimable' above 80 % of rows removed."""
    vid = np.arange(12)
    tr, te = np.array([0, 1, 2]), np.array([3])
    # S = {3, 2, 9}. Bag 0 loses 9; bag 1 loses 3; bag 2 loses all (centre included).
    ids = [np.array([0, 9, 10]), np.array([1, 3, 11]), np.array([2, 9, 3]), np.array([3, 2, 9])]
    out, stats, summary = h2b.build_dataset(ids, vid, [(tr, te)], seeds=(0,))
    st = stats[0]
    assert st["frac_training_rows_removed"] == pytest.approx(5 / 9)
    assert st["frac_training_bags_emptied"] == pytest.approx(1 / 3)
    assert st["rows_left_per_surviving_bag"] == pytest.approx(2.0)
    assert st["centre_deleted_rate_surviving_bags"] == 0.0
    assert st["centre_deleted_rate_unstratified_uniform_would_give"] == pytest.approx(1 / 3)
    assert st["frac_training_bags_touched_bag_level_purge"] == 1.0
    assert out["leak/r0_f0.npz"]["surviving_bag_ids"].tolist() == [0, 1]
    assert out["control-s0/r0_f0.npz"]["surviving_bag_ids"].tolist() == [0, 1]
    assert not summary["not_estimable"]
    # S = {3, 0, 1, 2, 9}: 8 of 9 training rows removed (> 80 %).
    ids = [np.array([0, 9, 1]), np.array([1, 3, 11]), np.array([2, 9, 3]), np.array([3, 0, 1, 2, 9])]
    _, stats, summary = h2b.build_dataset(ids, vid, [(tr, te)], seeds=(0,))
    assert stats[0]["frac_training_rows_removed"] == pytest.approx(8 / 9)
    assert stats[0]["centre_deleted_rate_surviving_bags"] == 1.0
    assert summary["not_estimable"]


def test_apply_mask(toy, tmp_path):
    out = str(tmp_path / "out")
    h2b.run("toy", toy["mat"], toy["cv"], toy["csv"], out)
    p = os.path.join(out, "toy", "purged", "leak", "r0_f0.npz")
    z = np.load(p)
    got = h2b.apply_mask(toy["bags"], p)
    assert len(got) == len(z["surviving_bag_ids"])
    assert sum(len(b) for b in got) == int(z["keep"].sum())


def test_h2b_cli_deterministic_and_no_overwrite(toy, tmp_path):
    args = ["--datasets", "toy", "--data-mat", toy["mat"], "--cv-mat", toy["cv"],
            "--bag-rows-csv", toy["csv"]]
    o1, o2 = str(tmp_path / "o1"), str(tmp_path / "o2")
    assert h2b.main(args + ["--out-root", o1]) == 0
    assert h2b.main(args + ["--out-root", o2]) == 0
    t1 = _tree(o1)
    assert t1 == _tree(o2) and len(t1) == 4 * 10 + 2
    with pytest.raises(hc.RefuseOverwrite):
        h2b.main(args + ["--out-root", o1])
    assert _tree(o1) == t1
    r = subprocess.run([PY, os.path.join(R1, "h2b_masks.py"), "--dry-run",
                        "--out-root", o1, "--datasets", "toy"], capture_output=True, text=True)
    assert r.stdout.count("EXISTS (would refuse)") == 42


def test_write_new_refuses_and_is_atomic(tmp_path):
    p = str(tmp_path / "a" / "x.bin")
    hc.write_new(p, b"one")
    with pytest.raises(hc.RefuseOverwrite):
        hc.write_new(p, b"two")
    assert open(p, "rb").read() == b"one"
    assert os.listdir(tmp_path / "a") == ["x.bin"]
    with pytest.raises(hc.RefuseOverwrite):
        hc.write_all(str(tmp_path / "a"), {"y.bin": b"y", "x.bin": b"z"})
    assert os.listdir(tmp_path / "a") == ["x.bin"]       # nothing partial


# --------------------------------------------------------------------------- T04 interface adapters

def test_flat_split_adapter(toy, tmp_path):
    """h2a.flat_split gives T04's layout and agrees with the stored mapping."""
    out = str(tmp_path / "out")
    h2a.run("toy", toy["mat"], toy["cv"], out)
    for f in range(10):
        p = os.path.join(out, "toy", "rebuilt", f"r0_f{f}.npz")
        z, fl = np.load(p), h2a.flat_split(p, toy["X"])
        tr, te = z["train_bag_ids"], z["test_bag_ids"]
        assert fl["split"] == f and fl["instances"].dtype == np.float64 and fl["labels"].dtype == np.int8
        assert np.array_equal(fl["bag_index"][~fl["is_test"]], tr) and np.array_equal(fl["bag_index"][fl["is_test"]], te)
        assert not set(tr) & set(te)
        tb, ytr, sb, yte = h2a.materialise(p, toy["X"])
        bags = [fl["instances"][fl["bag_ptr"][b]:fl["bag_ptr"][b + 1]] for b in range(len(fl["bag_index"]))]
        assert all(np.array_equal(a, b) for a, b in zip(bags, tb + sb))
        assert np.array_equal(fl["labels"], np.concatenate([ytr, yte]))


def test_full_keep_adapter(toy, tmp_path):
    """h2b.full_keep: mask over all original bags in file order; test rows all kept;
    training rows equal the stored mask; size mismatch refused."""
    out = str(tmp_path / "out")
    h2b.run("toy", toy["mat"], toy["cv"], toy["csv"], out)
    sizes = np.array([len(b) for b in toy["bags"]])
    start = np.concatenate([[0], np.cumsum(sizes)])
    for f, (tr, te) in enumerate(splits_of(toy)):
        for cond in h2b.CONDITIONS:
            p = os.path.join(out, "toy", "purged", cond, f"r0_f{f}.npz")
            fk = h2b.full_keep(p, sizes)
            assert fk["fold"] == f and fk["condition"] == cond and len(fk["keep"]) == sizes.sum()
            assert all(fk["keep"][start[j]:start[j + 1]].all() for j in te)
            masked = [toy["bags"][i][fk["keep"][start[i]:start[i + 1]]] for i in tr]
            ref = h2b.apply_mask(toy["bags"], p)
            assert all(np.array_equal(a, b) for a, b in zip([m for m in masked if len(m)], ref))
    bad = sizes.copy(); bad[splits_of(toy)[0][0][0]] += 1
    with pytest.raises(hc.ConstructionBug):
        h2b.full_keep(os.path.join(out, "toy", "purged", "leak", "r0_f0.npz"), bad)


# --------------------------------------------------------------------------- acceptance checks (addendum, plan lines 275, 287)

import json  # noqa: E402

import h2_acceptance as acc  # noqa: E402


def test_matches_printed_precision():
    """'Reproduce at the table's printed precision': within half a unit of the last digit."""
    assert acc.matches_printed(0.4684, 0.468, 3) and acc.matches_printed(0.4676, 0.468, 3)
    assert acc.matches_printed(0.4685, 0.468, 3)          # exact half: either convention
    assert not acc.matches_printed(0.46851, 0.468, 3) and not acc.matches_printed(0.4674, 0.468, 3)
    assert acc.matches_printed(2.8449, 2.84, 2) and not acc.matches_printed(2.8451, 2.84, 2)
    assert acc.matches_printed(0.0644, 0.064, 3) and not acc.matches_printed(0.0656, 0.064, 3)


def test_expected_constants_are_the_plan_lines():
    """The hard-coded H2-B constants equal the numbers printed in PREREGISTERED.md."""
    rows = {}
    with open(hc.PLAN, encoding="utf-8") as fh:
        for line in fh:
            for ds, tag in (("emotions", "| Emotions (0 duplicate rows) |"), ("yeast", "| Yeast (0) |"),
                            ("medical", "| Medical (11) |"), ("corel5k", "| Corel5K (2) |")):
                if line.strip().startswith(tag):
                    rows[ds] = line
    assert set(rows) == set(acc.H2B_EXPECTED)
    for ds, line in rows.items():
        e = acc.H2B_EXPECTED[ds]
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        assert float(cells[1]) == e["rows_removed"][0]
        assert float(cells[2].rstrip(" %")) / 100 == pytest.approx(e["bags_emptied"][0], abs=1e-12)
        assert float(cells[3]) == e["rows_left"][0]
        m, rng = cells[4].split(" [")
        lo, hi = rng.rstrip("]").split("–")
        assert (float(m), float(lo), float(hi)) == (e["centre_mean"][0], e["centre_min"][0], e["centre_max"][0])
        assert float(cells[5]) == e["unstratified"][0]
    with open(hc.PLAN, encoding="utf-8") as fh:
        plan = fh.read()
    assert "Medical 445, 301, 246, 310, 376, 607, 818, 398, 357, 853, 873; Corel5K 2465, 4676" in plan
    assert ", ".join(map(str, acc.H2A_EXPECTED["medical"]["dropped"])) == "445, 301, 246, 310, 376, 607, 818, 398, 357, 853, 873"
    assert "sizes 96, 96, 96, 96, 95, 97, 96, 94, 97, 96 of ⌊978/10⌋ = 97" in plan
    assert ", ".join(map(str, acc.H2A_EXPECTED["medical"]["pool_sizes"])) == "96, 96, 96, 96, 95, 97, 96, 94, 97, 96"
    assert "pools 4 and 5 lose 1 row each (486 of 487)" in plan
    c = acc.H2A_EXPECTED["corel5k"]["pool_sizes"]
    assert c[4] == c[5] == 486 and all(v == 487 for i, v in enumerate(c) if i not in (4, 5))
    assert acc.H2A_EXPECTED["emotions"]["pool_sizes"] == [593 // 10] * 10
    assert acc.H2A_EXPECTED["yeast"]["pool_sizes"] == [2417 // 10] * 10


def _h2a_meta(dropped, sizes, differ, leaving=(), overlap=0.0):
    zero = {"frac_test_bags_sharing_an_example_with_train": overlap}
    return {"duplicates": {"dropped_rows": [{"row": r} for r in dropped],
                           "pool_sizes_after": list(sizes), "n_dropped_rows_labels_differ": differ,
                           "vectors_leaving_h2a_lowest_row_in_remainder": list(leaving)},
            "splits": [{"split": 0, "overlap_source_rows": {"x": 0.0}, "overlap_vector_ids": zero}]}


def test_check_h2a_pass_and_each_mismatch():
    e = acc.H2A_EXPECTED["medical"]
    good = _h2a_meta(e["dropped"][::-1], e["pool_sizes"], 2)    # order-insensitive
    assert acc.check_h2a("medical", good) == []
    assert acc.check_h2a("medical", _h2a_meta(e["dropped"][:-1], e["pool_sizes"], 2))
    assert acc.check_h2a("medical", _h2a_meta(e["dropped"] + [12], e["pool_sizes"], 2))
    sizes = list(e["pool_sizes"]); sizes[7] += 1
    assert acc.check_h2a("medical", _h2a_meta(e["dropped"], sizes, 2))
    assert acc.check_h2a("medical", _h2a_meta(e["dropped"], e["pool_sizes"], 1))
    assert acc.check_h2a("medical", _h2a_meta(e["dropped"], e["pool_sizes"], 2, leaving=[3]))
    assert acc.check_h2a("medical", _h2a_meta(e["dropped"], e["pool_sizes"], 2, overlap=0.01))
    assert acc.check_h2a("emotions", _h2a_meta([], [59] * 10, 0)) == []
    assert acc.check_h2a("emotions", _h2a_meta([4], [59] * 10, 0))


def _folds(rows, emptied, left, centres, unstrat):
    return [{"frac_training_rows_removed": rows, "frac_training_bags_emptied": emptied,
             "rows_left_per_surviving_bag": left, "centre_deleted_rate_surviving_bags": c,
             "centre_deleted_rate_unstratified_uniform_would_give": unstrat} for c in centres]


def test_h2b_fold_means_and_check():
    """Mean, min and max over folds; pass at printed precision; each column can fail."""
    centres = [0.193, 0.275] + [0.2385] * 8                  # mean 0.2376 -> 0.238
    meta = {"folds": _folds(0.4681, 0.0641, 2.842, centres, 0.4318), "not_estimable": False}
    m = acc.h2b_fold_means(meta["folds"])
    assert m["centre_min"] == 0.193 and m["centre_max"] == 0.275
    assert m["centre_mean"] == pytest.approx(np.mean(centres))
    assert acc.check_h2b("emotions", meta) == []
    for kw, val in (("rows", 0.470), ("emptied", 0.066), ("left", 2.85), ("unstrat", 0.434)):
        args = dict(rows=0.4681, emptied=0.0641, left=2.842, centres=centres, unstrat=0.4318)
        args[kw] = val
        assert acc.check_h2b("emotions", {"folds": _folds(**args)}), kw
    assert acc.check_h2b("emotions", {"folds": _folds(0.4681, 0.0641, 2.842, [0.19] + centres[1:], 0.4318)})
    assert acc.check_h2b("emotions", dict(meta, not_estimable=True)) == []   # plan line 302: flag, not a mismatch


def test_checks_read_the_real_summary_structures(toy, tmp_path):
    """The checks run on construction.json / masks.json exactly as written."""
    out = str(tmp_path / "out")
    h2a.run("toy", toy["mat"], toy["cv"], out)
    h2b.run("toy", toy["mat"], toy["cv"], toy["csv"], out)
    cj = json.load(open(os.path.join(out, "toy", "rebuilt", "construction.json")))
    mj = json.load(open(os.path.join(out, "toy", "purged", "masks.json")))
    d = cj["duplicates"]
    exp_a = {"toy": {"dropped": [r["row"] for r in d["dropped_rows"]],
                     "pool_sizes": d["pool_sizes_after"], "labels_differ": d["n_dropped_rows_labels_differ"]}}
    assert len(exp_a["toy"]["dropped"]) == 1 and acc.check_h2a("toy", cj, exp_a) == []
    exp_a["toy"]["dropped"] = []
    assert acc.check_h2a("toy", cj, exp_a)
    means = acc.h2b_fold_means(mj["folds"])
    exp_b = {"toy": {k: (round(v, 3), 3) for k, v in means.items()}}
    assert acc.check_h2b("toy", mj, exp_b) == []
    exp_b["toy"]["rows_removed"] = (round(means["rows_removed"], 3) + 0.002, 3)
    assert acc.check_h2b("toy", mj, exp_b)


def test_builders_stop_before_writing_on_mismatch(toy, tmp_path, monkeypatch):
    """'A mismatch stops the construction / the H2-B runs': toy data under a real
    dataset name fails the plan's expected values and nothing is written. The
    deposit guard (which a real name triggers) is stubbed as if deposited."""
    monkeypatch.setattr(hc, "deposit_guard", lambda *a, **k: "deposited (test stub)")
    out = str(tmp_path / "out")
    with pytest.raises(acc.AcceptanceFailure, match="medical H2-A dropped rows"):
        h2a.run("medical", toy["mat"], toy["cv"], out)
    with pytest.raises(acc.AcceptanceFailure, match="emotions H2-B"):
        h2b.run("emotions", toy["mat"], toy["cv"], toy["csv"], out)
    assert not os.path.exists(out)


def test_acceptance_cli_exit_codes(tmp_path):
    """0 = pass, 1 = mismatch, 2 = a summary file missing."""
    root = tmp_path / "c"
    e = acc.H2A_EXPECTED["medical"]
    (root / "medical" / "rebuilt").mkdir(parents=True)
    (root / "medical" / "rebuilt" / "construction.json").write_text(
        json.dumps(_h2a_meta(e["dropped"], e["pool_sizes"], 2)))
    args = ["--root", str(root), "--datasets", "medical"]
    assert acc.main(args + ["--which", "h2a"]) == 0
    assert acc.main(args + ["--which", "h2b"]) == 2
    (root / "medical" / "purged").mkdir()
    (root / "medical" / "purged" / "masks.json").write_text(
        json.dumps({"folds": _folds(0.629, 0.136, 2.14, [0.051, 0.097] + [0.0765] * 8, 0.571)}))
    assert acc.main(args) == 0
    (root / "medical" / "purged" / "masks.json").write_text(
        json.dumps({"folds": _folds(0.640, 0.136, 2.14, [0.051, 0.097] + [0.0765] * 8, 0.571)}))
    assert acc.main(args) == 1



# --------------------------------------------------------------------------- code review 1 (CODE-T02__review_1.md)

@pytest.mark.skipif(_plan_deposited(), reason="plan deposited; the real-data refusal no longer applies")
def test_guard_every_route_to_real_data(toy, tmp_path, monkeypatch):
    """Finding 1: run() and the explicit-path CLI refuse before deposit when the
    dataset name is real, an input path is real, or out_root is the real root.
    The loader is stubbed to fail loudly, so no real file can be read."""
    def _no_load(*a, **k):
        raise AssertionError("loader reached: guard bypassed")
    monkeypatch.setattr(hc, "load_constructed", _no_load)
    rmat, rcv = hc.dataset_paths("medical")
    rcsv = os.path.join(hc.CSV_DIR, "provenance_bag_rows_medical.csv")
    tmp = str(tmp_path / "o")
    routes_a = [("medical", toy["mat"], toy["cv"], tmp),      # real name
                ("toy", rmat, toy["cv"], tmp),                # real .mat path
                ("toy", toy["mat"], rcv, tmp),                # real CV path
                ("toy", toy["mat"], toy["cv"], hc.OUT_ROOT)]  # real output root
    for ds, m, c, o in routes_a:
        with pytest.raises(hc.NotDeposited):
            h2a.run(ds, m, c, o)
        with pytest.raises(hc.NotDeposited):
            h2b.run(ds, m, c, toy["csv"], o)
    with pytest.raises(hc.NotDeposited):
        h2a.main(["--datasets", "medical", "--data-mat", rmat, "--cv-mat", rcv, "--out-root", tmp])
    with pytest.raises(hc.NotDeposited):
        h2b.main(["--datasets", "medical", "--data-mat", rmat, "--cv-mat", rcv,
                  "--bag-rows-csv", rcsv, "--out-root", tmp])
    with pytest.raises(hc.NotDeposited):
        h2a.main(["--datasets", "toy", "--data-mat", toy["mat"], "--cv-mat", toy["cv"]])  # default root = real
    with pytest.raises(hc.NotDeposited):                       # review 4 note 2: the real CSV alone
        h2b.run("toy", toy["mat"], toy["cv"], rcsv, tmp)
    assert not os.path.exists(tmp) and not os.path.exists(hc.OUT_ROOT)


def test_toy_routes_not_guarded(toy, tmp_path):
    """The guard does not fire for toy names, toy paths and a scratch root."""
    assert hc.guard_real_run("toy", (toy["mat"], toy["cv"], toy["csv"]), str(tmp_path)) is None


def test_not_estimable_masks_written_and_flagged(toy, tmp_path, monkeypatch):
    """Finding 2 / plan line 302: masks are still written and flagged, and the
    acceptance check (table only) does not refuse them."""
    monkeypatch.setattr(h2b, "NOT_ESTIMABLE_ABOVE", 0.0)
    out = str(tmp_path / "out")
    h2b.run("toy", toy["mat"], toy["cv"], toy["csv"], out)
    mj = json.load(open(os.path.join(out, "toy", "purged", "masks.json")))
    assert mj["not_estimable"] is True
    assert os.path.exists(os.path.join(out, "toy", "purged", "leak", "r0_f0.npz"))
    exp = {"toy": {k: (round(v, 3), 3) for k, v in acc.h2b_fold_means(mj["folds"]).items()}}
    assert acc.check_h2b("toy", mj, exp) == []


def test_not_estimable_boundary_is_strict():
    """Finding 5 / plan 'more than 80 %': exactly 4 of 5 rows removed is estimable."""
    vid = np.arange(6)
    ids = [np.array([0, 2, 3, 4, 5]), np.array([1, 2, 3, 4, 5])]
    _, stats, summary = h2b.build_dataset(ids, vid, [(np.array([0]), np.array([1]))], seeds=(0,))
    assert stats[0]["frac_training_rows_removed"] == 0.8
    assert summary["not_estimable"] is False


def test_leak_share_is_measured_and_stored(toy, monkeypatch):
    """Finding 3: the stored overlap is the value check_leak returns (0 on a
    correct purge), not a literal: a sentinel returned by check_leak must reach
    the stored statistics; and a mask that leaves a test vector raises."""
    bags, X, vid, ids = _b_inputs(toy)
    out, stats, _ = h2b.build_dataset(ids, vid, splits_of(toy))
    assert all(s["leak_overlap_test_vectors_in_surviving_train"] == 0.0 for s in stats)
    real = h2b.check_leak
    monkeypatch.setattr(h2b, "check_leak", lambda *a: real(*a) - 0.125)    # sentinel offset
    _, stats2, _ = h2b.build_dataset(ids, vid, splits_of(toy))
    assert all(s["leak_overlap_test_vectors_in_surviving_train"] == -0.125 for s in stats2)
    monkeypatch.setattr(h2b, "check_leak", real)
    tr, te = splits_of(toy)[0]
    S = {int(v) for j in te for v in ids[j]}
    assert h2b.check_leak(ids, tr, out["leak/r0_f0.npz"]["keep"], S) == 0.0
    with pytest.raises(hc.ConstructionBug, match="1 test vector"):
        keep = out["leak/r0_f0.npz"]["keep"].copy()
        off = out["leak/r0_f0.npz"]["bag_offsets"]
        flat = np.concatenate([ids[i] for i in tr])
        pos = int(np.flatnonzero(~keep)[0])
        keep[np.flatnonzero(flat == flat[pos])] = True       # restore every copy of one test vector
        h2b.check_leak(ids, tr, keep, S)


def test_tie_rule_is_relative_and_recorded(toy, tmp_path):
    """Finding 4: the tie tolerance is relative to the group's smallest distance.
    At scale 1e4 two distances 5e-10 apart (relative) tie, though 5e-6 apart in
    absolute terms; at scale 1e-4 two distances 5e-6 apart (relative) do not tie,
    though 5e-10 apart in absolute terms. The rule is written to construction.json."""
    far = [[3, 0], [0, 3], [-3, 0], [0, -3]]
    # Large scale: row 1 is 5e-10 (relative) farther than row 2 -> a tie -> lower index first.
    Xs = np.array([[0, 0], [1 + 5e-10, 0], [0, 1]] + far) * 1e4
    assert h2a.pool_bags(Xs, np.arange(7))[1][0].tolist()[1:3] == [1, 2]
    # Small scale: row 1 is relatively farther (5e-6) -> no tie -> row 2 first.
    Xs = np.array([[0, 0], [1 + 5e-6, 0], [0, 1], [3, 0], [0, 3], [-3, 0], [0, -3]]) * 1e-4
    assert h2a.pool_bags(Xs, np.arange(7))[1][0].tolist()[1:3] == [2, 1]
    out = str(tmp_path / "out")
    h2a.run("toy", toy["mat"], toy["cv"], out)
    cj = json.load(open(os.path.join(out, "toy", "rebuilt", "construction.json")))
    assert cj["tie_rtol"] == 1e-9 and "relative tolerance" in cj["tie_rule"]
    assert "anchored on its smallest distance" in cj["tie_rule"]


def test_released_summaries_cite_the_plan_not_working_notes(toy, tmp_path):
    """Finding 6: no task-question numbers or superseded tags in released JSON."""
    import re
    out = str(tmp_path / "out")
    h2a.run("toy", toy["mat"], toy["cv"], out)
    h2b.run("toy", toy["mat"], toy["cv"], toy["csv"], out)
    for rel in ("rebuilt/construction.json", "purged/masks.json"):
        text = open(os.path.join(out, "toy", rel)).read()
        assert not re.search(r"\bT0\d|\bQ\d\b|prereg-v3-final\b(?!-addendum)", text), rel
        assert "PREREGISTERED.md" in text and "pre-deposit addendum 2026-10-13" in text


def test_non_finite_source_stops(tmp_path):
    """Finding 7: a NaN or inf source value stops both builders before any bag."""
    for k, bad in enumerate((np.nan, np.inf)):
        d = tmp_path / f"t{k}"
        d.mkdir()
        t = write_toy(str(d))
        cell = np.empty((N, 1), dtype=object)
        for i, b in enumerate(t["bags"]):
            cell[i, 0] = b.copy()
        cell[7, 0][0, 1] = bad                               # centre of bag 7 = source row 7
        savemat(t["mat"], {"bags": cell, "labels": np.where(t["Y"] > 0, 1, -1).astype(np.int32)})
        out = str(d / "out")
        with pytest.raises(hc.ConstructionBug, match="non-finite"):
            h2a.run("toy", t["mat"], t["cv"], out)
        with pytest.raises(hc.ConstructionBug, match="non-finite"):
            h2b.run("toy", t["mat"], t["cv"], t["csv"], out)
        assert not os.path.exists(out)


# --------------------------------------------------------------------------- code review 2 (CODE-T02__review_2.md)

def _case_variant(p):
    """Flip the case of the last path component that has letters."""
    head, tail = os.path.split(p)
    return os.path.join(head, tail.swapcase())


def test_under_helper():
    """Finding 2's containment helper: case-folded, realpath-based, not a prefix match."""
    root = hc.OUT_ROOT
    assert hc._under(root, root)
    assert hc._under(os.path.join(root, "scratch"), root)
    assert hc._under(_case_variant(root), root)
    assert hc._under(os.path.join(os.path.dirname(root), "constructions_x"), hc.RESULTS)
    assert not hc._under(os.path.dirname(root), root)                  # parent is not inside
    assert not hc._under(root + "_x", root)                            # sibling with a shared prefix
    assert not hc._under("/tmp/scratch", root)
    # Review 3: Unicode normalisation (APFS is normalisation-insensitive).
    nfc, nfd = "caf\u00e9", "cafe\u0301"
    assert nfc != nfd
    assert hc._under(os.path.join("/tmp", nfd, "x"), os.path.join("/tmp", nfc))
    assert hc._under(os.path.join("/tmp", nfc.upper()), os.path.join("/tmp", nfd))
    # Review 3: the macOS firmlink alias of /Users/... (string level; no filesystem needed).
    assert hc._under(hc.FIRMLINK + root, root) and hc._under(root, hc.FIRMLINK + root)
    assert hc._under(hc.FIRMLINK + os.path.join(root, "x"), hc.RESULTS)
    assert not hc._under(hc.FIRMLINK + "X" + root, root)                # not a prefix match


@pytest.mark.skipif(_plan_deposited(), reason="plan deposited; the real-data refusal no longer applies")
def test_guard_case_variants_nested_roots_and_hard_links(toy, tmp_path, monkeypatch):
    """Review 2, findings 1 and 2: case-variant out_root and data path, a root
    nested in or beside the real root under results/, a mixed-case dataset name,
    and a hard link to a real .mat are all refused before any load."""
    def _no_load(*a, **k):
        raise AssertionError("loader reached: guard bypassed")
    monkeypatch.setattr(hc, "load_constructed", _no_load)
    rmat, rcv = hc.dataset_paths("medical")
    lower_mat = os.path.join(os.path.dirname(rmat).lower(), os.path.basename(rmat))
    assert os.path.exists(lower_mat)                                  # case-insensitive volume
    link = str(tmp_path / "linked.mat")
    try:
        os.link(rmat, link)                                           # same inode, scratch name
    except OSError:
        link = None
    tmp = str(tmp_path / "o")
    routes = [("toy", toy["mat"], toy["cv"], _case_variant(hc.OUT_ROOT)),       # CONSTRUCTIONS
              ("toy", toy["mat"], toy["cv"], hc.OUT_ROOT.upper()),               # whole path upper-case
              ("toy", toy["mat"], toy["cv"], os.path.join(hc.OUT_ROOT, "scratch")),
              ("toy", toy["mat"], toy["cv"], os.path.dirname(hc.OUT_ROOT)),       # results/revision_r1
              ("toy", lower_mat, toy["cv"], tmp),                                 # lower-case data path
              ("Medical", toy["mat"], toy["cv"], tmp),                            # mixed-case name
              ("MEDICAL", toy["mat"], toy["cv"], tmp)]
    if link:
        routes.append(("toy", link, toy["cv"], tmp))                              # hard link
    if os.path.isdir(hc.FIRMLINK + "/Users"):                                    # review 3: firmlink alias
        routes.append(("toy", toy["mat"], toy["cv"], hc.FIRMLINK + hc.OUT_ROOT))
        routes.append(("toy", toy["mat"], toy["cv"], hc.FIRMLINK + hc.RESULTS))
    for ds, m, c, o in routes:
        with pytest.raises(hc.NotDeposited):
            h2a.run(ds, m, c, o)
        with pytest.raises(hc.NotDeposited):
            h2b.run(ds, m, c, toy["csv"], o)
    assert not os.path.exists(tmp) and not os.path.exists(os.path.dirname(hc.OUT_ROOT))
    if link:
        os.unlink(link)


@pytest.mark.skipif(_plan_deposited(), reason="plan deposited; the real-data refusal no longer applies")
def test_writer_choke_point(toy):
    """Review 2, finding 2: build_dataset + write_all (or write_new) aimed at the
    real root, by any spelling, is refused at the writer before anything is created."""
    X, Y = toy["X"], toy["Y"]
    out, meta = h2a.build_dataset(X, Y, splits_of(toy))
    files = {rel: hc.npz_bytes(a) for rel, a in out.items()}
    roots = [os.path.join(hc.OUT_ROOT, "medical", "rebuilt"),
             os.path.join(_case_variant(hc.OUT_ROOT), "medical", "rebuilt"),
             os.path.join(hc.OUT_ROOT, "scratch"),
             os.path.join(hc.RESULTS, "revision_r1", "elsewhere")]                  # review 3: RESULTS-wide
    if os.path.isdir(hc.FIRMLINK + "/Users"):
        roots.append(hc.FIRMLINK + os.path.join(hc.OUT_ROOT, "medical", "rebuilt"))  # review 3: firmlink
    for root in roots:
        with pytest.raises(hc.NotDeposited):
            hc.write_all(root, files)
        with pytest.raises(hc.NotDeposited):
            hc.write_new(os.path.join(root, "x.bin"), b"x")
    assert not os.path.exists(os.path.dirname(hc.OUT_ROOT))
    assert not os.path.exists(os.path.join(hc.RESULTS, "revision_r1"))


def test_run_normalises_the_dataset_name(toy, tmp_path):
    """Review 3, note 3: one spelling of the name in output paths and JSON."""
    out = str(tmp_path / "out")
    h2a.run(" ToY ", toy["mat"], toy["cv"], out)
    h2b.run("TOY", toy["mat"], toy["cv"], toy["csv"], out)
    assert os.listdir(out) == ["toy"]
    for rel in ("rebuilt/construction.json", "purged/masks.json"):
        assert json.load(open(os.path.join(out, "toy", rel)))["dataset"] == "toy"


def test_mixed_case_name_still_gets_acceptance_check(toy, tmp_path, monkeypatch):
    """Review 2, note in finding 1: a mis-cased real name does not skip the
    acceptance check (guard stubbed as deposited)."""
    monkeypatch.setattr(hc, "deposit_guard", lambda *a, **k: "deposited (test stub)")
    out = str(tmp_path / "out")
    with pytest.raises(acc.AcceptanceFailure, match="medical H2-A"):
        h2a.run("Medical", toy["mat"], toy["cv"], out)
    with pytest.raises(acc.AcceptanceFailure, match="emotions H2-B"):
        h2b.run("EMOTIONS", toy["mat"], toy["cv"], toy["csv"], out)
    assert not os.path.exists(out)



# --------------------------------------------------------------------------- review 4 / cross-tool rule (T04 review 2)

def test_deposit_guard_follows_the_shared_rule(tmp_path, pinned_today, monkeypatch):
    """Review 5 / DECISIONS.md 2026-10-13: h2_common has no local deposit rule;
    deposit_guard opens exactly when deposit_check.deposit_recorded does. Only the
    canonical line-8 form opens. Every other cell stays closed: T04's earlier 11
    closed cells, its 4 non-canonical 'open' cells, review 5's escaped-pipe attack,
    a wrong label, the row on another line, and the real plan row."""
    import deposit_check
    assert not hasattr(hc, "deposit_recorded")                          # local logic deleted
    p = tmp_path / "P.md"
    closed = ["**PENDING (user action).** x", "pending (user action)", "Pending", "TBD",
              "", "to be filled", "pending: Zenodo upload in progress https://zenodo.org/x",
              "http://zenodo.org/records/1", "https://example.com/10", "done", "tbd 10.5281/x",
              "https://doi.org/10.5281/zenodo.1234567", "10.5281/zenodo.1234567 (2026-10-20)",
              "https://zenodo.org/records/1234567", "https://osf.io/abcd2/",
              "DOI 10.17605/OSF.IO/ABCD2, https://osf.io/abcd2",
              "10.5281/zenodo.1234567 \\| pending publication",
              "https://doi.org/10.5281/zenodo.NNNNNNN (2026-10-20)",
              "https://doi.org/10.5281/zenodo.1234567 (2026-13-40)",
              CANONICAL + " pending",
              "https://doi.org/10.5281/zenodo.1234567 (2026-10-21)"]          # after (pinned) today
    for cell in closed:
        path = _plan_with(p, cell)
        assert deposit_check.deposit_recorded(path) is False, cell
        with pytest.raises(hc.NotDeposited):
            hc.deposit_guard(path)
    path = _plan_with(p, CANONICAL)
    assert deposit_check.deposit_recorded(path) is True
    assert hc.deposit_guard(path) == "deposit https://doi.org/10.5281/zenodo.1234567 (2026-10-20)"
    for path in (_plan_with(p, CANONICAL, line=7), _plan_with(p, CANONICAL, line=9),
                 _plan_with(p, CANONICAL, label="| Public timestamp (planned) |"),
                 _plan_with(p, CANONICAL, label="| Deposited version |")):
        with pytest.raises(hc.NotDeposited):
            hc.deposit_guard(path)
    # The real plan row, judged under the REAL clock (re-pinned, as
    # test_deposit_check.test_real_plan_is_closed does).
    monkeypatch.setattr(deposit_check, "_today", _real_utc_today)
    if not _plan_deposited():
        assert deposit_check.deposit_recorded() is False


def test_cli_normalises_names_before_paths_and_dry_run(tmp_path, capsys):
    """Review 4 note 3: --datasets Medical plans medical/..., as run() writes."""
    out = str(tmp_path / "dry")
    assert h2a.main(["--dry-run", "--out-root", out, "--datasets", " Medical "]) == 0
    assert h2b.main(["--dry-run", "--out-root", out, "--datasets", "MEDICAL"]) == 0
    text = capsys.readouterr().out
    assert "/medical/rebuilt/" in text and "/medical/purged/" in text
    assert "Medical" not in text and "MEDICAL" not in text


def test_deposit_guard_requires_every_amendment(tmp_path, pinned_today):
    """A1 review 2, F7: deposit_guard's amendment branch. With line 8 deposited,
    a pending A1 keeps H2 closed; a deposited A1 opens it and is named in the
    returned reference; a §6.7 extension section (## E1) needs no deposit."""
    p = _plan_with(tmp_path / "P.md", CANONICAL)
    (tmp_path / "AMENDMENT.md").write_text("# Amendments\n\n## A1 (2026-10-13): x\n\n**Deposited:** pending\n")
    with pytest.raises(hc.NotDeposited, match="amendment"):
        hc.deposit_guard(p)
    ok = "**Deposited:** https://doi.org/10.5281/zenodo.7654321 (2026-10-20)"
    (tmp_path / "AMENDMENT.md").write_text(f"# Amendments\n\n## A1 (2026-10-13): x\n\n{ok}\n\n## E1 (2026-10-15): budget\n\ntext\n")
    ref = hc.deposit_guard(p)
    assert "zenodo.1234567" in ref and "A1 https://doi.org/10.5281/zenodo.7654321 (2026-10-20)" in ref
    assert "E1" not in ref
