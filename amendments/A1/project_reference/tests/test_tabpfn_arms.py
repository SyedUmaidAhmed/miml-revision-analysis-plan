"""Synthetic-data tests for tabpfn_arms.py (T04/T07). No real dataset is read.

Run:  .tabpfn_env/bin/python -m pytest experiments/revision_r1/tests -q
"""
import json
import math
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tabpfn_arms as ta  # noqa: E402
import run_foundation_baselines as rfb  # noqa: E402
from miml_clam.metrics.miml_metrics import AllFiveWithThresholds, optimize_thresholds  # noqa: E402


def synth_version(n_bags=50, L=3, variable_size=True, num_folds=2, seed=0):
    bags, Y = ta.make_synthetic(n_bags=n_bags, L=L, seed=seed, variable_size=variable_size)
    return ta.splits_from_bags("synthetic", "original", bags, Y, cfg={"default_folds": 5},
                               ds=bags, num_folds=num_folds), bags, Y


def manifest(tmp_path):
    return ta.Manifest(str(tmp_path), ta.new_run_id(), {"test": True})


# ---------------------------------------------------------------- features
def test_features_identical_to_submission_pool():
    bags, _ = ta.make_synthetic(30)
    for arm, how in (("tabpfn_bagmean", "mean"), ("tabpfn_bagmax", "max"),
                     ("tabpfn_multiview", "multiview"), ("tabpfn_padded", "multiview")):
        a, b = ta.build_features(bags, arm), rfb.pool(bags, how)
        assert a.dtype == b.dtype and np.array_equal(a, b)
    card = ta.build_features(bags, "tabpfn_bagmean_card")
    assert card.shape == (30, 5)
    assert np.array_equal(card[:, :4], rfb.pool(bags, "mean").astype(card.dtype))
    assert np.array_equal(card[:, 4], [len(b) for b in bags])
    assert np.array_equal(card[:, 4], rfb.pool(bags, "multiview")[:, -1])


# ------------------------------------------------------- padded permutation
def test_padded_permutation_correctness():
    bags, _ = ta.make_synthetic(40, d=4)
    X = rfb.pool(bags, "multiview")
    tr, te = X[:30], X[30:]
    a, b = ta.padded_permute(tr, te, 4, seed=1)
    # bag-mean block kept, row for row
    assert np.array_equal(a[:, :4], tr[:, :4]) and np.array_equal(b[:, :4], te[:, :4])
    # every other column (incl. the cardinality column) is a within-fold permutation
    for j in range(4, 25):
        assert np.array_equal(np.sort(a[:, j]), np.sort(tr[:, j]))
        assert np.array_equal(np.sort(b[:, j]), np.sort(te[:, j]))
    assert a.shape == tr.shape and b.shape == te.shape
    # association with the bag is broken (columns permuted independently)
    moved = [j for j in range(4, 25) if not np.array_equal(a[:, j], tr[:, j])]
    assert len(moved) >= 19
    perms = {tuple(np.argsort(np.argsort(a[:, j]))) for j in range(4, 24)}
    assert len(perms) > 1
    # deterministic per seed; seeds differ
    a2, b2 = ta.padded_permute(tr, te, 4, seed=1)
    assert np.array_equal(a, a2) and np.array_equal(b, b2)
    a3, _ = ta.padded_permute(tr, te, 4, seed=2)
    assert not np.array_equal(a, a3)
    # inputs untouched
    assert np.array_equal(tr, X[:30])


def test_padded_requires_multiview_width():
    with pytest.raises(ValueError):
        ta.padded_permute(np.zeros((5, 4)), np.zeros((3, 4)), 4, 0)


def test_padded_unit_uses_fold_local_permutation(tmp_path):
    version, bags, Y = synth_version(num_folds=1)
    spec = ta.UnitSpec("synthetic", "original", "tabpfn_padded", "native", "padded-s0",
                       model="logreg")
    f, kw = ta.make_factory("logreg", "cpu")
    r = ta.run_split(spec, version, version.splits[0], f, kw)
    sp = version.splits[0]
    X_tr = rfb.pool([bags[i] for i in sp.ids_tr], "multiview")
    X_te = rfb.pool([bags[i] for i in sp.ids_te], "multiview")
    a, b = ta.padded_permute(X_tr, X_te, 4, 0)
    v = r["v"]
    mu, sd = a[v:].mean(0), a[v:].std(0) + 1e-8
    pv = rfb.fit_predict("logreg", ((a - mu) / sd)[v:], Y[sp.ids_tr][v:], ((b - mu) / sd))
    assert np.array_equal(pv, r["pt"])


# -------------------------------------------------------------- subsampling
def test_subsample_sizes_and_determinism():
    ids = np.array([5, 1, 3, 0])
    sizes = np.array([4, 7, 1, 9])
    for tok, f in (("f0.25", .25), ("f0.5", .5), ("f0.75", .75)):
        sel = ta.subsample_indices(ids, sizes, tok, 0)
        for i, n in zip(ids, sizes):
            m = len(sel[int(i)])
            assert m == max(1, int(np.ceil(f * n)))
            assert len(set(sel[int(i)])) == m and sel[int(i)].max() < n
        assert all(np.array_equal(sel[k], ta.subsample_indices(ids, sizes, tok, 0)[k]) for k in sel)
    single = ta.subsample_indices(ids, sizes, "single", 2)
    assert all(len(v) == 1 for v in single.values())


def test_subsample_same_subset_across_folds_and_arms():
    version, _, _ = synth_version(num_folds=2)
    s0 = ta.apply_subsample(version.splits[0], "f0.5", 1)
    s1 = ta.apply_subsample(version.splits[1], "f0.5", 1)
    for i in version.splits[0].universe:
        assert np.array_equal(s0.bags[int(i)], s1.bags[int(i)])
    with pytest.raises(ValueError):
        ta.check_arm_condition("tabpfn_bagmax", "original", "sub-f0.5-s1")


# --------------------------------------------------- fit modes / submission
def test_two_fit_reproduces_submission_fit_predict_logreg():
    rng = np.random.default_rng(0)
    Xf, Xv, Xt = rng.normal(size=(40, 5)), rng.normal(size=(10, 5)), rng.normal(size=(12, 5))
    Yf = (rng.normal(size=(40, 3)) > 0).astype(int)
    Yf[:, 2] = 1  # a constant label
    f, _ = ta.make_factory("logreg", "cpu")
    pv, pt, recs = ta.fit_predict_labels(f, Xf, Yf, Xv, Xt, "two")
    assert np.array_equal(pv, rfb.fit_predict("logreg", Xf, Yf, Xv))
    assert np.array_equal(pt, rfb.fit_predict("logreg", Xf, Yf, Xt))
    assert recs[2]["constant"] and recs[2]["fits"] == []
    assert [x["pass"] for x in recs[0]["fits"]] == ["val", "test"]


@pytest.mark.tabpfn
def test_two_fit_reproduces_submission_fit_predict_tabpfn():
    rng = np.random.default_rng(1)
    Xf, Xv, Xt = rng.normal(size=(40, 4)), rng.normal(size=(8, 4)), rng.normal(size=(9, 4))
    Yf = (Xf[:, :2] > 0).astype(int)
    f, _ = ta.make_factory("tabpfn", "cpu")
    pv, pt, _ = ta.fit_predict_labels(f, Xf, Yf, Xv, Xt, "two")
    # the submission's constructor (defaults) vs ours (explicit 8 / 0): same numbers
    assert np.array_equal(pv, rfb.fit_predict("tabpfn", Xf, Yf, Xv, "cpu"))
    assert np.array_equal(pt, rfb.fit_predict("tabpfn", Xf, Yf, Xt, "cpu"))


@pytest.mark.tabpfn
def test_one_fit_equals_two_fit_tabpfn_toy():
    rng = np.random.default_rng(2)
    Xf, Xv, Xt = rng.normal(size=(50, 4)), rng.normal(size=(10, 4)), rng.normal(size=(15, 4))
    Yf = np.column_stack([(Xf[:, 0] > 0), (Xf[:, 1] + Xf[:, 2] > 0), np.ones(50)]).astype(int)
    f, _ = ta.make_factory("tabpfn", "cpu")
    pv2, pt2, _ = ta.fit_predict_labels(f, Xf, Yf, Xv, Xt, "two")
    pv1, pt1, recs = ta.fit_predict_labels(f, Xf, Yf, Xv, Xt, "one")
    assert np.array_equal(pv1, pv2) and np.array_equal(pt1, pt2)
    assert len(recs[0]["fits"]) == 1


def test_one_fit_equals_two_fit_logreg_and_verify_verdict(tmp_path):
    version, _, _ = synth_version(num_folds=2)
    m = manifest(tmp_path)
    f, kw = ta.make_factory("logreg", "cpu")
    for cond in ("verify-2fit", "verify-1fit"):
        spec = ta.UnitSpec("synthetic", "original", "tabpfn_bagmean", "native", cond,
                           model="logreg")
        ta.run_unit(spec, version, str(tmp_path), m, factory=f, kw=kw, log=lambda *_: None)
    res = ta.compare_verify(str(tmp_path), "synthetic", "original", "cpu")
    assert res["pass"] and all(x["max_abs_score_diff"] == 0 for x in res["folds"])
    # review 1 #2: each verify sidecar declares the mode it actually used
    for cond, mode, passes in (("verify-2fit", "two", ["val", "test"]),
                               ("verify-1fit", "one", ["val+test"])):
        side = json.load(open(os.path.join(ta.unit_dir(
            str(tmp_path), "synthetic", "original", "tabpfn_bagmean", "native", cond, "cpu"),
            "r0_f0.json")))
        assert side["identity"]["fit_mode"] == mode
        fitted = [x for x in side["timing"]["per_label"] if not x["constant"]]
        assert [f["pass"] for f in fitted[0]["fits"]] == passes
        # review 1 #15: determinism probe stored in every verify unit
        assert side["determinism_probe"]["max_abs_diff_test"] == 0.0
    assert all(f["determinism_probe"]["verify-1fit"] is not None for f in res["folds"])
    assert ta.onefit_allowed(str(tmp_path), "cpu")[0] is False
    path, verdict = ta.write_verify_verdict(str(tmp_path), "cpu", [res])
    assert verdict["pass"] and ta.onefit_allowed(str(tmp_path), "cpu")[0] is True
    with pytest.raises(FileExistsError):
        ta.write_verify_verdict(str(tmp_path), "cpu", [res])


def test_verify_detects_difference(tmp_path):
    version, _, _ = synth_version(num_folds=1)
    m = manifest(tmp_path)
    f, kw = ta.make_factory("logreg", "cpu")
    ta.run_unit(ta.UnitSpec("synthetic", "original", "tabpfn_bagmean", "native", "verify-2fit",
                            model="logreg"), version, str(tmp_path), m, factory=f, kw=kw,
                log=lambda *_: None)
    from sklearn.linear_model import LogisticRegression
    weak = (lambda: LogisticRegression(max_iter=1000, C=1e-4)), {"max_iter": 1000, "C": 1e-4}
    ta.run_unit(ta.UnitSpec("synthetic", "original", "tabpfn_bagmean", "native", "verify-1fit",
                            model="logreg"), version, str(tmp_path), m, factory=weak[0],
                kw=weak[1], log=lambda *_: None)
    assert ta.compare_verify(str(tmp_path), "synthetic", "original", "cpu")["pass"] is False


def test_unit_pipeline_reproduces_submission_loop(tmp_path):
    """run_unit == the inner loop of run_foundation_baselines.main (logreg)."""
    version, bags, Y = synth_version(num_folds=2)
    spec = ta.UnitSpec("synthetic", "original", "tabpfn_multiview", "native", "main",
                       model="logreg")
    f, kw = ta.make_factory("logreg", "cpu")
    ta.run_unit(spec, version, str(tmp_path), manifest(tmp_path), factory=f, kw=kw,
                log=lambda *_: None)
    X = rfb.pool(bags, "multiview")
    for sp in version.splits:
        tr = np.array(sp.ids_tr)
        v = max(1, int(0.2 * len(tr)))
        val_i, fit_i = tr[:v], tr[v:]
        mu, sd = X[fit_i].mean(0), X[fit_i].std(0) + 1e-8
        Xn = (X - mu) / sd
        pv = rfb.fit_predict("logreg", Xn[fit_i], Y[fit_i], Xn[val_i])
        pt = rfb.fit_predict("logreg", Xn[fit_i], Y[fit_i], Xn[sp.ids_te])
        th = optimize_thresholds(Y[val_i], pv, metric="hamming")
        want = AllFiveWithThresholds(Y[sp.ids_te], pt, th)
        d = os.path.join(ta.unit_dir(str(tmp_path), "synthetic", "original", "tabpfn_multiview",
                                     "native", "main", "cpu"))
        side = json.load(open(os.path.join(d, f"r0_f{sp.fold}.json")))
        z = np.load(os.path.join(d, f"r0_f{sp.fold}.npz"))
        assert np.array_equal(z["scores"], pt) and np.array_equal(z["val_scores"], pv)
        assert np.array_equal(z["thresholds"], th)
        assert np.array_equal(z["test_idx"], sp.ids_te)
        assert np.array_equal(z["pred"], (pt > th).astype(np.int8))
        for k in ta.FIVE:
            assert side["metrics"][k] == float(want[k])
        for k in ("preprocess_s", "fit_s", "predict_s", "wall_s", "cpu_s"):
            assert side["timing"][k] >= 0
        assert side["energy"]["energy_mJ"] is None and "not measured" in side["energy"]["energy_note"]
        assert {"device", "versions", "loadavg_1min", "concurrency", "memory",
                "code_sha256"} <= set(side)
        assert side["identity"]["constructor"] == {"max_iter": 1000}


@pytest.mark.tabpfn
def test_tabpfn_constructor_recorded(tmp_path):
    version, _, _ = synth_version(n_bags=30, L=2, num_folds=1)
    spec = ta.UnitSpec("synthetic", "original", "tabpfn_bagmean", "native", "main")
    ta.run_unit(spec, version, str(tmp_path), manifest(tmp_path), log=lambda *_: None)
    side = json.load(open(os.path.join(ta.unit_dir(str(tmp_path), "synthetic", "original",
                                                   "tabpfn_bagmean", "native", "main", "cpu"),
                                       "r0_f0.json")))
    assert side["identity"]["constructor"] == {"device": "cpu", "n_estimators": 8,
                                               "random_state": 0,
                                               "ignore_pretraining_limits": True}
    assert side["checkpoint"]["path"].endswith(".ckpt")
    assert side["versions"]["tabpfn"] == "2.2.1"
    assert len(side["timing"]["per_label"]) == 2


# ---------------------------------------------------------------- storage
def test_unit_dir_matches_prereg_key():
    p = ta.unit_dir("/R", "yeast", "original", "tabpfn_multiview", "native", "main", "g")
    assert p == "/R/predictions/yeast/original/tabpfn_multiview/native/main+g"
    keys = set()
    for v in ("original", "rebuilt", "rcv10"):
        for w in ("native", "pca500"):
            for c in ("main", "padded-s1", "sub-f0.25-s0", "sub-single-s2", "verify-1fit"):
                for d in ("g", "mps"):
                    keys.add(ta.unit_dir("/R", "x", v, "tabpfn_padded", w, c, d))
    assert len(keys) == 3 * 2 * 5 * 2
    for bad in (("x", "orig", "tabpfn_bagmean", "native", "main", "g"),
                ("x", "original", "logreg_bagmean", "native", "main", "g"),
                ("x", "original", "tabpfn_bagmean", "pca", "main", "g"),
                ("x", "original", "tabpfn_bagmean", "pca0", "main", "g"),
                ("x", "original", "tabpfn_bagmean", "pca500x", "main", "g"),
                ("x", "original", "tabpfn_bagmean", "native", "padded-s3", "g"),
                ("x", "original", "tabpfn_bagmean", "native", "main", "gpu")):
        with pytest.raises(ValueError):
            ta.unit_dir("/R", *bad)


def test_write_noclobber_refuses_overwrite(tmp_path):
    p = str(tmp_path / "a" / "x.json")
    ta.save_json_noclobber(p, {"v": 1})
    with pytest.raises(FileExistsError):
        ta.save_json_noclobber(p, {"v": 2})
    assert json.load(open(p)) == {"v": 1}
    q = str(tmp_path / "a" / "y.npz")
    ta.save_npz_noclobber(q, a=np.arange(3))
    with pytest.raises(FileExistsError):
        ta.save_npz_noclobber(q, a=np.arange(4))
    assert np.array_equal(np.load(q)["a"], np.arange(3))
    assert sorted(os.listdir(tmp_path / "a")) == ["x.json", "y.npz"]  # no temp left


def test_rerun_reuses_and_identity_mismatch_refused(tmp_path):
    version, _, _ = synth_version(num_folds=2)
    f, kw = ta.make_factory("logreg", "cpu")
    spec = ta.UnitSpec("synthetic", "original", "tabpfn_bagmean", "native", "main",
                       model="logreg", procedures=("H1",))
    m1 = manifest(tmp_path)
    ta.run_unit(spec, version, str(tmp_path), m1, factory=f, kw=kw, log=lambda *_: None)
    d = ta.unit_dir(str(tmp_path), "synthetic", "original", "tabpfn_bagmean", "native",
                    "main", "cpu")
    mtimes = {x: os.stat(os.path.join(d, x)).st_mtime_ns for x in os.listdir(d)}
    spec2 = ta.UnitSpec("synthetic", "original", "tabpfn_bagmean", "native", "main",
                        model="logreg", procedures=("§6.9",))
    m2 = ta.Manifest(str(tmp_path), ta.new_run_id() + "b", {})
    ta.run_unit(spec2, version, str(tmp_path), m2, factory=f, kw=kw, log=lambda *_: None)
    assert {x: os.stat(os.path.join(d, x)).st_mtime_ns for x in os.listdir(d)} == mtimes
    lines = [json.loads(x) for x in open(m2.path)]
    assert [x["type"] for x in lines[1:]] == ["reuse", "reuse"]
    assert lines[1]["procedures"] == ["§6.9"]
    spec3 = ta.UnitSpec("synthetic", "original", "tabpfn_bagmean", "native", "main",
                        model="logreg", fit_mode="one")
    with pytest.raises(RuntimeError, match="different identity"):
        ta.run_unit(spec3, version, str(tmp_path), m2, factory=f, kw=kw, log=lambda *_: None)


def test_orphan_npz_refused(tmp_path):
    version, _, _ = synth_version(num_folds=1)
    d = ta.unit_dir(str(tmp_path), "synthetic", "original", "tabpfn_bagmean", "native",
                    "main", "cpu")
    ta.save_npz_noclobber(os.path.join(d, "r0_f0.npz"), a=np.zeros(1))
    f, kw = ta.make_factory("logreg", "cpu")
    with pytest.raises(RuntimeError, match="incomplete"):
        ta.run_unit(ta.UnitSpec("synthetic", "original", "tabpfn_bagmean", "native", "main",
                                model="logreg"), version, str(tmp_path), manifest(tmp_path),
                    factory=f, kw=kw, log=lambda *_: None)


def test_manifest_and_device_lock_single_writer(tmp_path):
    rid = ta.new_run_id()
    ta.Manifest(str(tmp_path), rid, {})
    with pytest.raises(FileExistsError):
        ta.Manifest(str(tmp_path), rid, {})
    with ta.DeviceLock(str(tmp_path), "g"):
        with pytest.raises(RuntimeError, match="one per device"):
            with ta.DeviceLock(str(tmp_path), "g"):
                pass
    with ta.DeviceLock(str(tmp_path), "g"):
        pass


def test_bagmean_card_skipped_on_constant_cardinality(tmp_path):
    version, _, _ = synth_version(variable_size=False)
    m = manifest(tmp_path)
    out = ta.run_unit(ta.UnitSpec("synthetic", "original", "tabpfn_bagmean_card", "native",
                                  "main", model="logreg"), version, str(tmp_path), m,
                      log=lambda *_: None)
    assert out == [] and not os.path.exists(os.path.join(str(tmp_path), "predictions"))
    assert json.loads(open(m.path).readlines()[-1])["type"] == "skip"
    assert ta.run_pilot(ta.UnitSpec("synthetic", "original", "tabpfn_bagmean_card", "native",
                                    "main", model="logreg"), version, str(tmp_path), "r") is None


def test_condition_rules():
    ok = [("tabpfn_padded", "original", "padded-s2"), ("tabpfn_multiview", "rebuilt", "sub-single-s0"),
          ("tabpfn_bagmean", "purged", "control-s1"), ("tabpfn_multiview", "purged", "leak")]
    for a in ok:
        ta.check_arm_condition(*a)
    bad = [("tabpfn_padded", "original", "main"), ("tabpfn_multiview", "original", "padded-s0"),
           ("tabpfn_bagmean", "original", "leak"), ("tabpfn_bagmean", "purged", "main"),
           ("tabpfn_multiview", "original", "verify-1fit"), ("tabpfn_bagmax", "original", "sub-f0.5-s0")]
    for a in bad:
        with pytest.raises(ValueError):
            ta.check_arm_condition(*a)


# ---------------------------------------------------------------- PCA
def test_pca_components_rule():
    # final decision row: d' = min(500, min_f n_rows(fit_i) - 1, d)
    assert ta.pca_components(1440, 1459) == 500          # Reuters multiview
    assert ta.pca_components(220, 1297) == 219           # Protein Haloarcula multiview
    assert ta.pca_components(698, 8695) == 500           # Medical rebuilt
    assert ta.pca_components(900, 501) == 500
    assert ta.n_fit_of(274) == 220 and ta.n_fit_of(1800) == 1440
    assert ta.PCA_CFG == {"order": "zscore_then_pca", "svd_solver": "full", "random_state": 0}


def test_width_plan_repeated_design_unequal_folds():
    bags, Y = ta.make_synthetic(n_bags=53, d=90, L=2, seed=1)      # widths 541 (multiview)
    v = ta.splits_from_bags("mscv2", "original", bags, Y)          # 5x5, block sizes 10/11
    nfits = sorted({ta.n_fit_of(len(s.ids_tr)) for s in v.splits})
    assert len(nfits) == 2                                          # folds differ in size
    assert ta.width_plan("pca", v, 541) == (f"pca{nfits[0] - 1}", nfits[0] - 1)
    assert ta.width_plan("pca", v, 90) == ("native", None)         # no-op at d <= 500
    assert ta.width_plan("pca", v, 500) == ("native", None)
    assert ta.width_plan("native", v, 541) == ("native", None)
    with pytest.raises(ValueError):
        ta.width_plan("pca500", v, 541)


def test_dprime_per_dataset_from_fold_sizes():
    # DECISIONS.md "d' scope": min over the H1 folds and the §1.9 rcv10 folds
    sz = ta.dataset_train_sizes("protein_haloarcula", 304)
    assert min(sz) == 273 and 274 in sz                              # rcv10 273, canonical 274
    assert ta.pca_components(min(ta.n_fit_of(t) for t in sz), 1297) == 218   # pca218 everywhere
    sz = ta.dataset_train_sizes("reuters", 2000)
    assert ta.pca_components(min(ta.n_fit_of(t) for t in sz), 1459) == 500
    sz = ta.dataset_train_sizes("hja_birdsong", 548)                  # 5x10, no rcv10
    assert sorted(set(sz)) == [493, 494]
    with pytest.raises(ValueError, match="n_bags"):
        ta.dataset_train_sizes("scene")


def test_dprime_same_for_every_version_and_assert_stops(t02_root):
    root, X, Y, bags, splits = t02_root
    rb = ta.load_rebuilt("emotions", X, root=root)
    assert ta.dataset_train_sizes("emotions", constructions_root=root) == \
        [len(s.ids_tr) for s in rb.splits]
    k = ta.pca_components(min(ta.n_fit_of(len(s.ids_tr)) for s in rb.splits), 600)
    assert ta.width_plan("pca", rb, 600, root) == (f"pca{k}", k)
    leaky = ta.splits_from_bags("emotions", "original", bags, Y, cfg={"default_folds": 10},
                                ds=_DS(bags))                        # larger folds, same d'
    assert ta.width_plan("pca", leaky, 600, root) == (f"pca{k}", k)
    small = ta.Version("emotions", "purged", "x",
                       [ta.Split(0, 0, np.arange(30), np.arange(30, 33), {}, {})],
                       3, 4, False, 53)                              # n_fit - 1 = 23 < d'
    with pytest.raises(RuntimeError, match="stop"):
        ta.width_plan("pca", small, 600, root)


def test_pca_fit_on_fit_rows_only():
    rng = np.random.default_rng(0)
    n_tr, v, d = 640, 100, 601
    X_tr, X_te = rng.normal(size=(n_tr, d)), rng.normal(size=(30, d))
    a, b, info = ta.standardise_and_reduce(X_tr, X_te, v, 500)
    assert a.shape == (n_tr, 500) and b.shape == (30, 500) and info["width_token"] == "pca500"
    assert info["feature_dim_used"] == 500 and info["pca"]["n_fit"] == 540
    # changing test rows or validation rows changes nothing fitted
    X_te2 = X_te + 100 * rng.normal(size=X_te.shape)
    X_tr2 = X_tr.copy()
    X_tr2[:v] += 50
    a2, _, _ = ta.standardise_and_reduce(X_tr, X_te2, v, 500)
    a3, _, _ = ta.standardise_and_reduce(X_tr2, X_te, v, 500)
    assert np.array_equal(a, a2)
    assert np.allclose(a3[v:], a[v:], atol=1e-10)
    # exactly the addendum recipe: z-score on fit_i, PCA(full, rs=0) on fit_i, no re-scaling
    from sklearn.decomposition import PCA
    mu, sd = X_tr[v:].mean(0), X_tr[v:].std(0) + 1e-8
    p = PCA(n_components=500, svd_solver="full", random_state=0).fit(((X_tr - mu) / sd)[v:])
    assert np.array_equal(p.transform((X_te - mu) / sd), b)
    assert np.array_equal(p.transform((X_tr - mu) / sd), a)
    # changing a fit row does change the projection
    X_tr4 = X_tr.copy()
    X_tr4[v + 1] += 50
    a4, _, _ = ta.standardise_and_reduce(X_tr4, X_te, v, 500)
    assert not np.allclose(a4[v:], a[v:])


def test_pca_below_500_fit_rows():
    rng = np.random.default_rng(0)
    a, b, info = ta.standardise_and_reduce(rng.normal(size=(274, 1297)),
                                           rng.normal(size=(30, 1297)), 54, 219)
    assert a.shape == (274, 219) and b.shape == (30, 219)
    assert info["width_token"] == "pca219" and info["feature_dim_used"] == 219
    with pytest.raises(ValueError, match="exceeds"):
        ta.standardise_and_reduce(rng.normal(size=(274, 1297)), rng.normal(size=(30, 1297)),
                                  54, 221)


def test_no_pca_is_plain_zscore():
    rng = np.random.default_rng(0)
    X_tr, X_te = rng.normal(size=(60, 20)), rng.normal(size=(10, 20))
    a, b, info = ta.standardise_and_reduce(X_tr, X_te, 12, None)
    mu, sd = X_tr[12:].mean(0), X_tr[12:].std(0) + 1e-8
    assert info["width_token"] == "native"
    assert np.array_equal(a, (X_tr - mu) / sd) and np.array_equal(b, (X_te - mu) / sd)


def test_pca_unit_stores_token_and_dprime(tmp_path):
    bags, Y = ta.make_synthetic(n_bags=60, d=90, L=2, seed=4)   # multiview width 541 > 500
    version = ta.splits_from_bags("synthetic", "original", bags, Y, cfg={"default_folds": 5},
                                  ds=bags)
    f, kw = ta.make_factory("logreg", "cpu")
    w = ta.run_unit(ta.UnitSpec("synthetic", "original", "tabpfn_multiview", "pca", "main",
                                model="logreg"), version, str(tmp_path), manifest(tmp_path),
                    factory=f, kw=kw, folds={(0, 0)}, log=lambda *_: None)
    side = json.load(open(w[0]))
    assert "/pca38/main+cpu/" in w[0]                            # n_fit = 39 in every fold
    assert side["feature"]["feature_dim"] == 541
    assert side["feature"]["feature_dim_used"] == side["n_fit"] - 1 == 38
    assert side["identity"]["width"] == "pca38" and side["identity"]["pca_cfg"] == ta.PCA_CFG
    w2 = ta.run_unit(ta.UnitSpec("synthetic", "original", "tabpfn_bagmean", "pca", "main",
                                 model="logreg"), version, str(tmp_path), manifest(tmp_path / "b"),
                     factory=f, kw=kw, folds={(0, 0)}, log=lambda *_: None)
    assert "/native/main+cpu/" in w2[0]                          # 90 wide: switch is a no-op


def test_instance_pca_fit_on_training_instances_only():
    version, bags, Y = synth_version(num_folds=1)
    sp = version.splits[0]
    old = ta.INSTANCE_PCA
    s1 = ta.apply_instance_pca(sp, 2, svd_solver="full")
    bags2 = dict(sp.bags)
    for i in sp.ids_te:
        bags2[int(i)] = sp.bags[int(i)] * 100 + 7
    sp2 = ta.Split(sp.repeat, sp.fold, sp.ids_tr, sp.ids_te, bags2, sp.Y, sp.universe)
    s2 = ta.apply_instance_pca(sp2, 2, svd_solver="full")
    for i in sp.ids_tr:
        assert np.array_equal(s1.bags[int(i)], s2.bags[int(i)])
    assert ta.INSTANCE_PCA is old


# -------------------------------------------------------- split designs
def test_repeated_splits_design():
    n, k = 23, 5
    trip = ta.repeated_splits(n, k, (0, 1))
    assert len(trip) == 10
    for r, s in enumerate((0, 1)):
        perm = np.random.default_rng(s).permutation(n)
        tested = np.concatenate([te for rr, _, _, te in trip if rr == r])
        assert sorted(tested) == list(range(n))
        sizes = [len(te) for rr, _, _, te in trip if rr == r]
        assert max(sizes) - min(sizes) <= 1
        for rr, j, tr, te in trip:
            if rr == r:
                assert np.array_equal(tr, perm[~np.isin(perm, te)])  # permutation order


# ------------------------------------------- H2-A / H2-B interop with T02
# Files are produced by T02's own builders (h2a_rebuild, h2b_masks) on a toy
# constructed set, written with T02's writer, then read by our loaders.
import h2_common as hc  # noqa: E402
import h2a_rebuild as h2a  # noqa: E402
import h2b_masks as h2b  # noqa: E402


def toy_constructed(n=53, d=4, L=3, seed=11):
    """Distinct source rows, leaky k-NN bags (T01 recipe), canonical-style
    splits (permutation cut into 10 blocks of n // 10, remainder in training)."""
    rng = np.random.default_rng(seed)
    X = rng.normal(size=(n, d))
    Y = (rng.random((n, L)) < .4).astype(np.int8)
    members = []
    for i in range(n):
        cand = np.delete(np.arange(n), i)
        d2 = ((X[cand] - X[i]) ** 2).sum(1)
        members.append(np.concatenate([[i], cand[np.lexsort((cand, d2))[:4]]]))
    bags = [X[m] for m in members]
    perm, fs = np.random.RandomState(42).permutation(n), n // 10
    splits = [(np.concatenate([perm[:f * fs], perm[(f + 1) * fs:]]), perm[f * fs:(f + 1) * fs])
              for f in range(10)]
    return X, Y, bags, members, splits


def write_t02(root, dataset, X, Y, members, splits):
    out, _ = h2a.build_dataset(X, Y, splits)
    files = {f"rebuilt/{k}": hc.npz_bytes(v) for k, v in out.items()}
    vid = hc.vector_id_map(X)
    outb, _, _ = h2b.build_dataset([vid[m] for m in members], vid, splits)
    files.update({f"purged/{k}": hc.npz_bytes(v) for k, v in outb.items()})
    for rel, data in files.items():
        hc.write_new(os.path.join(root, dataset, rel), data)


class _DS(list):
    pass


@pytest.fixture
def t02_root(tmp_path):
    X, Y, bags, members, splits = toy_constructed()
    root = str(tmp_path / "constructions")
    write_t02(root, "emotions", X, Y, members, splits)
    return root, X, Y, bags, splits


def test_load_rebuilt_reads_t02_files(t02_root):
    root, X, Y, _, splits = t02_root
    v = ta.load_rebuilt("emotions", X, root=root)
    assert v.sizes_constant and v.L == 3 and v.d == 4 and len(v.splits) == 10
    for f, sp in enumerate(v.splits):
        assert np.all(np.diff(sp.ids_tr) > 0)                       # §1.3 ascending
        assert np.array_equal(sp.ids_te, splits[f][1])             # test = pool f
        assert not set(sp.ids_tr) & set(sp.ids_te)
        assert len(sp.ids_tr) == 9 * 5                             # remainder rows excluded
        tb, Ytr, eb, Yte = h2a.materialise(sp.info["source"], X)    # T02's own reader
        assert all(np.array_equal(sp.bags[int(i)], b.astype(np.float32))
                   for i, b in zip(sp.ids_tr, tb))
        assert all(np.array_equal(sp.bags[int(i)], b.astype(np.float32))
                   for i, b in zip(sp.ids_te, eb))
        assert np.array_equal(np.stack([sp.Y[int(i)] for i in sp.ids_tr]), Ytr)
        assert all(sp.bags[int(i)].dtype == np.float32 for i in sp.ids_tr)


def test_load_rebuilt_rejects_bad_files(t02_root, tmp_path):
    root, X, *_ = t02_root
    p = os.path.join(root, "emotions", "rebuilt", "r0_f1.npz")
    z = dict(np.load(p))
    z["train_bag_ids"] = z["train_bag_ids"][::-1]
    os.remove(p)
    np.savez(p, **z)
    with pytest.raises(ValueError, match="ascending"):
        ta.load_rebuilt("emotions", X, root=root)


def test_load_purged_reads_t02_masks(t02_root):
    root, X, Y, bags, splits = t02_root
    cfg, ds = {"cv_mat_path": "unused"}, _DS(bags)
    orig_splits_for = rfb.splits_for
    rfb.splits_for = lambda *_a, **_k: [(list(tr), list(te)) for tr, te in splits]
    try:
        for cond in ("leak", "control-s0", "control-s2"):
            v = ta.load_purged("emotions", cond, bags, Y, cfg, ds, root=root)
            for f, sp in enumerate(v.splits):
                tr, te = splits[f]
                applied = h2b.apply_mask(bags, sp.info["source"])     # T02's own reader
                assert len(applied) == len(sp.ids_tr)
                assert all(np.array_equal(sp.bags[int(i)], b) for i, b in zip(sp.ids_tr, applied))
                assert [i for i in tr if i in set(sp.ids_tr)] == list(sp.ids_tr)  # canonical order
                assert np.array_equal(sp.ids_te, te)
                assert all(np.array_equal(sp.bags[int(i)], bags[i]) for i in te)
                if cond == "leak":   # the purge leaves no test vector in training
                    test_rows = {r.tobytes() for i in te for r in bags[i]}
                    assert not any(r.tobytes() in test_rows
                                   for i in sp.ids_tr for r in sp.bags[int(i)])
        bad = [(list(tr), list(te)) for tr, te in splits]
        bad[0] = (bad[0][0][::-1], bad[0][1])
        rfb.splits_for = lambda *_a, **_k: bad
        with pytest.raises(ValueError, match="canonical split"):
            ta.load_purged("emotions", "leak", bags, Y, cfg, ds, root=root)
    finally:
        rfb.splits_for = orig_splits_for


def test_rebuilt_and_purged_units_run_end_to_end(t02_root, tmp_path):
    root, X, Y, bags, splits = t02_root
    f, kw = ta.make_factory("logreg", "cpu")
    out = str(tmp_path / "out")
    v = ta.load_rebuilt("emotions", X, root=root, folds=range(2))
    w = ta.run_unit(ta.UnitSpec("emotions", "rebuilt", "tabpfn_multiview", "native", "main",
                                model="logreg"), v, out, manifest(tmp_path / "m1"),
                    factory=f, kw=kw, log=lambda *_: None)
    assert len(w) == 2 and json.load(open(w[0]))["split_info"]["sha256"]
    orig = rfb.splits_for
    rfb.splits_for = lambda *_a, **_k: [(list(tr), list(te)) for tr, te in splits]
    try:
        vp = ta.load_purged("emotions", "control-s1", bags, Y, {}, _DS(bags), root=root,
                            folds={0})
    finally:
        rfb.splits_for = orig
    w = ta.run_unit(ta.UnitSpec("emotions", "purged", "tabpfn_bagmean", "native", "control-s1",
                                model="logreg"), vp, out, manifest(tmp_path / "m2"),
                    factory=f, kw=kw, log=lambda *_: None)
    assert w[0].endswith("predictions/emotions/purged/tabpfn_bagmean/native/control-s1+cpu/r0_f0.json")


# ---------------------------------------------------------- pilot, guard
def test_pilot_record(tmp_path):
    version, _, _ = synth_version(L=4, num_folds=2)
    f, kw = ta.make_factory("logreg", "cpu")
    rec = ta.run_pilot(ta.UnitSpec("synthetic", "original", "tabpfn_multiview", "native",
                                   "main", model="logreg"), version, str(tmp_path), "rid",
                       factory=f, kw=kw)
    assert len(rec["per_label"]) == 3 and rec["L"] == 4 and rec["n_outer_folds"] == 2
    assert rec["feature_dim"] == 25 and rec["fit_mode"] == "two"
    assert rec["n_nonconstant_labels"] == 4 and not any(x["constant"] for x in rec["per_label"])
    line = json.loads(open(os.path.join(str(tmp_path), "pilots", "rid.jsonl")).readline())
    assert line["arm"] == "tabpfn_multiview"
    assert not os.path.exists(os.path.join(str(tmp_path), "predictions"))


def test_pilot_skips_constant_labels(tmp_path):
    bags, Y = ta.make_synthetic(n_bags=50, L=5, seed=0)
    Y[:, 0] = 1                       # constant everywhere
    Y[:, 2] = 0
    version = ta.splits_from_bags("synthetic", "original", bags, Y, cfg={"default_folds": 5},
                                  ds=bags, num_folds=1)
    f, kw = ta.make_factory("logreg", "cpu")
    rec = ta.run_pilot(ta.UnitSpec("synthetic", "original", "tabpfn_bagmean", "native", "main",
                                   model="logreg"), version, str(tmp_path), "rid",
                       factory=f, kw=kw)
    assert [x["label"] for x in rec["per_label"]] == [1, 3, 4]
    assert rec["n_nonconstant_labels"] == 3 and all(x["seconds"] > 0 for x in rec["per_label"])


@pytest.mark.tabpfn
def test_cli_refuses_real_data_and_project_root(tmp_path, monkeypatch):
    import run_tabpfn_arms as cli
    import deposit_check
    # Since the deposit (2026-10-13) the real plan passes the guard, so the
    # closed-guard case is simulated, and the open case must reach the next guard.
    with monkeypatch.context() as mp:
        mp.setattr(deposit_check, "deposit_recorded", lambda *a, **k: False)
        with pytest.raises(SystemExit, match="line 8"):
            cli.main(["--dataset", "scene", "--device", "cuda", "--out-root", str(tmp_path)])
    # Open guard: the run must get past it and stop at the next guard. The device
    # log is pointed at an absent tmp file so this holds whether or not the real
    # DEVICE_LOG.md exists (review A1-1 F12).
    with monkeypatch.context() as mp:
        mp.setattr(deposit_check, "deposit_recorded", lambda *a, **k: True)
        mp.setattr(ta, "DEVICE_LOG", str(tmp_path / "absent" / "DEVICE_LOG.md"))
        with pytest.raises(SystemExit, match="DEVICE_LOG"):
            cli.main(["--dataset", "scene", "--device", "cuda", "--out-root", str(tmp_path)])
    with pytest.raises(SystemExit, match="outside"):
        cli.main(["--dataset", "x", "--synthetic", "--device", "cpu"])
    with pytest.raises(SystemExit, match="one-fit"):
        cli.main(["--dataset", "x", "--synthetic", "--device", "cpu", "--fit-mode", "one",
                  "--out-root", str(tmp_path)])


# ------------------------------------------------- pinned TabPFN environment
def test_tabpfn_env_guard(monkeypatch):
    import tabpfn
    if tabpfn.__version__ == ta.TABPFN_VERSION:
        ver, ck = ta.check_tabpfn_env()
        assert ver == "2.2.1" and os.path.basename(ck["path"]) == ta.TABPFN_CKPT
    monkeypatch.setattr(tabpfn, "__version__", "8.2.0")
    with pytest.raises(RuntimeError, match="tabpfn_env"):
        ta.check_tabpfn_env()
    with pytest.raises(RuntimeError, match="tabpfn_env"):
        ta.make_factory("tabpfn", "cpu")


# ------------------------------------------------------------ review 1 fixes
def test_padded_exact_draw_order():
    # reviewer-supplied (review 1 #9): train columns first, then test, one generator per fold
    bags, _ = ta.make_synthetic(40, d=3)
    X = rfb.pool(bags, "multiview"); tr, te = X[:28], X[28:]; d = 3
    a, b = ta.padded_permute(tr, te, d, seed=7)
    rng = np.random.default_rng(7); etr, ete = tr.copy(), te.copy()
    for j in range(d, 6 * d + 1):
        etr[:, j] = tr[rng.permutation(len(tr)), j]
    for j in range(d, 6 * d + 1):
        ete[:, j] = te[rng.permutation(len(te)), j]
    assert np.array_equal(a, etr) and np.array_equal(b, ete)


def test_subsample_exact_draw_order():
    # reviewer-supplied (review 1 #9): ascending bag id visit order
    ids = np.array([5, 1, 3, 0, 2]); sizes = np.array([4, 7, 1, 9, 6])
    for tok, f in (("f0.25", .25), ("f0.5", .5), ("f0.75", .75), ("single", None)):
        got = ta.subsample_indices(ids, sizes, tok, 3)
        rng = np.random.default_rng(3); exp = {}
        for i in sorted(ids):
            n = int(sizes[list(ids).index(i)])
            m = 1 if f is None else max(1, math.ceil(f * n))
            exp[int(i)] = np.sort(rng.choice(n, size=m, replace=False))
        assert all(np.array_equal(got[k], exp[k]) for k in exp), tok


def test_construction_hash_in_identity(t02_root, tmp_path):
    # review 1 #4: a regenerated T02 file is never silently reused
    root, X, *_ = t02_root
    v = ta.load_rebuilt("emotions", X, root=root, folds=range(1))
    f, kw = ta.make_factory("logreg", "cpu")
    spec = ta.UnitSpec("emotions", "rebuilt", "tabpfn_bagmean", "native", "main", model="logreg")
    out = str(tmp_path / "out")
    w = ta.run_unit(spec, v, out, manifest(tmp_path / "m1"), factory=f, kw=kw, log=lambda *_: None)
    ident = json.load(open(w[0]))["identity"]["construction"]
    assert ident == {"source": "r0_f0.npz", "sha256": v.splits[0].info["sha256"]}
    v.splits[0].info["sha256"] = "0" * 64
    with pytest.raises(RuntimeError, match="different identity"):
        ta.run_unit(spec, v, out, manifest(tmp_path / "m2"), factory=f, kw=kw,
                    log=lambda *_: None)


def test_thread_pinning_explicit():
    # review 1 #5
    import torch
    assert torch.get_num_threads() == 1
    v = ta.versions()
    assert v["torch_num_threads"] == 1
    assert v["thread_env"] == {"OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1",
                               "MKL_NUM_THREADS": "1"}


@pytest.mark.tabpfn
def test_checkpoint_pinned_by_sha256(monkeypatch):
    # review 1 #7
    ver, ck = ta.check_tabpfn_env()
    assert ck["sha256"] == ta.TABPFN_CKPT_SHA256
    monkeypatch.setattr(ta, "TABPFN_CKPT_SHA256", "0" * 64)
    with pytest.raises(RuntimeError, match="sha256"):
        ta.check_tabpfn_env()


def test_width_decision_enforced(tmp_path):
    # review 1 #3
    pj = tmp_path / "P.json"
    pj.write_text(json.dumps({"pca_decision": {
        "medical": {"triggered": True, "complete": True},
        "reuters": {"triggered": False, "complete": True},
        "yeast": {"triggered": True, "complete": True},
        "voc2012": {"triggered": True, "complete": False}}}))
    p = str(pj)
    assert ta.check_width_decision(p, "medical", "rebuilt", 8695, "pca") == "pca"
    assert ta.check_width_decision(None, "scene", "original", 91, "pca") == "native"  # <= 500
    assert ta.check_width_decision(p, "reuters", "original", 1459, "native") == "native"
    for args in (("medical", "rebuilt", 8695, "native"), ("reuters", "original", 1459, "pca"),
                 ("voc2012", "original", 769, "pca"), ("hja_birdsong", "original", 900, "native")):
        with pytest.raises(RuntimeError):
            ta.check_width_decision(p, *args)
    with pytest.raises(RuntimeError, match="--projections"):
        ta.check_width_decision(None, "medical", "rebuilt", 8695, "pca")
    # H3 Yeast pair stays native; the leaky-column row follows the decision
    assert ta.check_width_decision(p, "yeast", "original", 619, "native", ("H3",)) == "native"
    with pytest.raises(RuntimeError):
        ta.check_width_decision(p, "yeast", "original", 619, "pca", ("H3",))
    assert ta.check_width_decision(p, "yeast", "original", 619, "pca", ("H1-leaky",)) == "pca"


def test_device_log_guard(tmp_path):
    # review 1 #13
    log = str(tmp_path / "DEVICE_LOG.md")
    assert ta.check_device_log("cpu", path=log) is None
    assert ta.check_device_log("mps", mps_fallback=False, path=log) is None   # §1.9 / T03-g
    with pytest.raises(RuntimeError, match="missing"):
        ta.check_device_log("cuda", path=log)
    with pytest.raises(RuntimeError, match="missing"):
        ta.check_device_log("mps", mps_fallback=True, path=log)
    open(log, "w").write(f"device: {ta.cpu_brand()}\n")
    with pytest.raises(RuntimeError, match="fallback"):
        ta.check_device_log("mps", mps_fallback=True, path=log)
    open(log, "w").write(f"G unavailable: global MPS fallback. device: {ta.cpu_brand()}\n")
    assert ta.check_device_log("mps", mps_fallback=True, path=log) == ta.cpu_brand()
    open(log, "w").write("global MPS fallback on some other machine\n")
    with pytest.raises(RuntimeError, match="does not name"):
        ta.check_device_log("mps", mps_fallback=True, path=log)


def test_nvml_failure_is_loud_on_cuda():
    # review 1 #14 (no NVML on this Mac, so the CUDA branch fails)
    with pytest.raises(RuntimeError, match="allow-no-nvml"):
        ta.EnergyMeter("cuda")
    m = ta.EnergyMeter("cuda", allow_missing=True)
    m.start()
    e = m.stop()
    assert e["energy_status"] == "failed" and e["energy_note"].startswith("failed")
    c = ta.EnergyMeter("cpu")
    c.start()
    assert c.stop()["energy_status"] == "not measured"


def test_pca_guard_strict_n_fit_minus_1():
    # review 1 #16
    rng = np.random.default_rng(0)
    with pytest.raises(ValueError, match="n_fit - 1"):
        ta.standardise_and_reduce(rng.normal(size=(274, 1297)), rng.normal(size=(30, 1297)),
                                  54, 220)                              # n_fit 220


@pytest.mark.synthetic_data_dir
def test_data_dir_override(tmp_path):
    # review 1 #17: datasets read by basename from --data-dir
    from scipy.io import savemat
    rng = np.random.default_rng(0)
    sizes = [2, 3, 1, 4]
    X = rng.normal(size=(sum(sizes), 5))
    XtB = np.repeat(np.arange(1, 5), sizes)[:, None].astype(float)
    YB = np.array([[1, -1], [-1, 1], [1, 1], [-1, -1]], dtype=float)
    dd = {"X": X, "XtB": XtB, "B": np.arange(1, 5)[:, None].astype(float), "YB": YB,
          "YR": np.zeros((sum(sizes), 2))}
    savemat(str(tmp_path / "hja_birdsong.mat"), {"DD": dd})
    assert ta.data_path("/a/b/hja_birdsong.mat") == "/a/b/hja_birdsong.mat"
    try:
        ta.set_data_dir(str(tmp_path))
        assert ta.data_path("/a/b/hja_birdsong.mat") == str(tmp_path / "hja_birdsong.mat")
        bags, Y, cfg, _ = ta.load_original("hja_birdsong")
        assert cfg["data_path"] == str(tmp_path / "hja_birdsong.mat")
        assert [len(b) for b in bags] == sizes and Y.tolist() == [[1, 0], [0, 1], [1, 1], [0, 0]]
    finally:
        ta.set_data_dir(None)


def test_feature_dtype_recorded_per_arm(tmp_path):
    # plan §1.4 footnote (review 1 #6): float32 for bag-mean/bag-max; float64 for
    # every arm carrying the cardinality column (multiview incl. subsampled, padded,
    # bagmean_card), as in the submitted runner
    version, _, _ = synth_version(num_folds=1)
    f, kw = ta.make_factory("logreg", "cpu")
    cases = (("tabpfn_bagmean", "main", "float32"), ("tabpfn_bagmax", "main", "float32"),
             ("tabpfn_multiview", "main", "float64"),
             ("tabpfn_multiview", "sub-f0.5-s0", "float64"),
             ("tabpfn_multiview", "sub-single-s1", "float64"),
             ("tabpfn_bagmean", "sub-f0.25-s2", "float32"),
             ("tabpfn_padded", "padded-s1", "float64"),
             ("tabpfn_bagmean_card", "main", "float64"))
    for arm, cond, dt in cases:
        w = ta.run_unit(ta.UnitSpec("synthetic", "original", arm, "native", cond, model="logreg"),
                        version, str(tmp_path), manifest(tmp_path / f"{arm}-{cond}"),
                        factory=f, kw=kw, log=lambda *_: None)
        assert json.load(open(w[0]))["feature"]["dtype"] == dt, (arm, cond)



# ------------------------------------------------------------ review 2 fixes
def _results_tree(tmp_path):
    root = tmp_path / "proj" / "results"
    (root / "revision_r1").mkdir(parents=True)
    return root


def test_results_containment_folds_case_symlink_firmlink(tmp_path):
    # review 2 #1: T02's folding (realpath, firmlink, NFC, casefold) + commonpath
    import run_tabpfn_arms as cli
    root = _results_tree(tmp_path)
    assert cli.under(str(root / "revision_r1"), str(root))
    assert cli.under(str(root / "anything" / "deeper"), str(root))
    # case variant (APFS here folds case; the check folds it regardless)
    assert cli.under(str(tmp_path / "proj" / "RESULTS" / "Revision_R1"), str(root))
    # symlinked parent
    os.symlink(str(root), str(tmp_path / "link"))
    assert cli.under(str(tmp_path / "link" / "revision_r1"), str(root))
    # firmlink alias of the same directory
    alias = "/System/Volumes/Data" + os.path.realpath(str(root))
    if os.path.isdir(alias):
        assert cli.under(os.path.join(alias, "revision_r1"), str(root))
    # sibling sharing a string prefix is NOT inside
    (tmp_path / "proj" / "results_scratch").mkdir()
    assert not cli.under(str(tmp_path / "proj" / "results_scratch"), str(root))
    assert not cli.under(str(tmp_path / "proj"), str(root))


def test_cli_refuses_smoke_writes_anywhere_under_results(tmp_path, monkeypatch):
    # review 2 #1 through the CLI: the refusal precedes every other check
    import run_tabpfn_arms as cli
    root = _results_tree(tmp_path)
    monkeypatch.setattr(cli, "RESULTS_ROOT", str(root))
    os.symlink(str(root), str(tmp_path / "link"))
    variants = [root / "revision_r1", tmp_path / "proj" / "RESULTS" / "Revision_R1",
                tmp_path / "link" / "revision_r1", root / "other_dir"]
    alias = "/System/Volumes/Data" + os.path.realpath(str(root / "revision_r1"))
    if os.path.isdir(alias):
        variants.append(alias)
    for out in variants:
        for extra in (["--synthetic"], ["--device", "cpu"], ["--folds-limit", "1"]):
            argv = ["--dataset", "x", "--out-root", str(out)] + extra
            if "--device" not in extra:
                argv += ["--device", "cpu"] if extra != ["--folds-limit", "1"] else []
            with pytest.raises(SystemExit, match="outside the project results"):
                cli.main(argv)


def test_h3_and_h1_leaky_split_when_yeast_triggers(tmp_path):
    # review 2 #8
    pj = tmp_path / "P.json"
    pj.write_text(json.dumps({"pca_decision": {"yeast": {"triggered": True, "complete": True}}}))
    with pytest.raises(RuntimeError, match="separate"):
        ta.check_width_decision(str(pj), "yeast", "original", 619, "native", ("H3", "H1-leaky"))
    assert ta.check_width_decision(str(pj), "yeast", "original", 619, "native", ("H3",)) == "native"
    assert ta.check_width_decision(str(pj), "yeast", "original", 619, "pca", ("H1-leaky",)) == "pca"
    assert ta.check_width_decision(str(pj), "yeast", "original", 103, "native",
                                   ("H3", "H1-leaky")) == "native"     # bag-mean: no switch
    pj.write_text(json.dumps({"pca_decision": {"yeast": {"triggered": False, "complete": True}}}))
    assert ta.check_width_decision(str(pj), "yeast", "original", 619, "native",
                                   ("H3", "H1-leaky")) == "native"     # same unit serves both


def _fake_ckpt(monkeypatch, tmp_path):
    """Pinned sha of a fake payload; HOME / caches redirected so nothing can
    touch the real ~/Library/Caches/tabpfn."""
    import hashlib
    payload = b"fake-checkpoint-bytes"
    monkeypatch.setattr(ta, "TABPFN_CKPT_SHA256", hashlib.sha256(payload).hexdigest())
    for var in ("HOME", "XDG_CACHE_HOME", "HF_HOME"):
        monkeypatch.setenv(var, str(tmp_path / "home"))
    target = tmp_path / "home" / "cache" / "tabpfn" / ta.TABPFN_CKPT
    return payload, target


def _tree(root):
    return sorted(str(p.relative_to(root)) for p in root.rglob("*"))


def test_fetch_checkpoint_contract_with_fake_downloader(tmp_path, monkeypatch):
    # review 3 #1: the downloader receives the checkpoint FILE path
    payload, target = _fake_ckpt(monkeypatch, tmp_path)
    calls = []

    def download(p):
        calls.append(p)
        open(p, "wb").write(payload)
        return "ok"

    info = ta.fetch_checkpoint(resolve=lambda: str(target), download=download)
    assert calls == [str(target)]
    assert info == {"path": str(target), "sha256": ta.TABPFN_CKPT_SHA256, "fetched": True,
                    "cleaned": []}
    assert ta.fetch_checkpoint(resolve=lambda: str(target), download=download)["fetched"] is False
    assert len(calls) == 1                                           # present: no download
    target.write_bytes(b"corrupted")
    with pytest.raises(RuntimeError, match="sha256"):
        ta.fetch_checkpoint(resolve=lambda: str(target), download=download)
    assert not target.exists() and any(p.name.startswith(ta.TABPFN_CKPT + ".bad-")
                                       for p in target.parent.iterdir())
    with pytest.raises(RuntimeError, match="download failed"):
        ta.fetch_checkpoint(resolve=lambda: str(target), download=lambda p: [OSError("x")])
    with pytest.raises(RuntimeError, match="is not"):
        ta.fetch_checkpoint(resolve=lambda: str(tmp_path / "other.ckpt"), download=download)


@pytest.mark.tabpfn
def test_fetch_checkpoint_real_download_model_hf_branch(tmp_path, monkeypatch):
    # review 3 #1: tabpfn's REAL download_model, huggingface branch faked offline
    import huggingface_hub
    import tabpfn.model_loading as ml
    payload, target = _fake_ckpt(monkeypatch, tmp_path)
    seen = []

    def fake_hf(repo_id, filename, local_dir, **kw):
        seen.append((filename, str(local_dir)))
        meta = os.path.join(local_dir, ".cache", "huggingface")   # as the real one does
        os.makedirs(meta, exist_ok=True)
        out = os.path.join(local_dir, filename)
        open(out, "wb").write(payload if filename == ta.TABPFN_CKPT else b"{}")
        return out

    def no_direct(*a, **k):
        raise AssertionError("direct branch must not run when HF succeeds")

    monkeypatch.setattr(huggingface_hub, "hf_hub_download", fake_hf)
    monkeypatch.setattr(ml, "_try_direct_downloads", no_direct)
    info = ta.fetch_checkpoint(resolve=lambda: str(target))
    assert info["fetched"] and info["path"] == str(target)
    assert info["sha256"] == ta.TABPFN_CKPT_SHA256 and target.read_bytes() == payload
    assert seen[0] == (ta.TABPFN_CKPT, str(target.parent))          # landed in the cache dir
    assert _tree(target.parent) == [ta.TABPFN_CKPT]                 # no stray files inside
    assert ".cache" in info["cleaned"]
    assert _tree(tmp_path / "home") == ["cache", "cache/tabpfn", f"cache/tabpfn/{ta.TABPFN_CKPT}"]


@pytest.mark.tabpfn
def test_fetch_checkpoint_real_download_model_direct_branch(tmp_path, monkeypatch):
    # review 3 #1: HF fails, tabpfn's direct-URL branch writes the file
    import huggingface_hub
    import tabpfn.model_loading as ml
    payload, target = _fake_ckpt(monkeypatch, tmp_path)

    def hf_fails(*a, **k):
        raise OSError("offline")

    class Resp:
        status = 200

        def __init__(self, data):
            self.data = data

        def read(self):
            return self.data

        def __enter__(self):
            return self

        def __exit__(self, *e):
            return False

    urls = []

    def fake_urlopen(url, *a, **k):
        urls.append(url)
        return Resp(payload if ta.TABPFN_CKPT in url else b"{}")

    monkeypatch.setattr(huggingface_hub, "hf_hub_download", hf_fails)
    monkeypatch.setattr(ml.urllib.request, "urlopen", fake_urlopen)
    info = ta.fetch_checkpoint(resolve=lambda: str(target))
    assert info["fetched"] and target.read_bytes() == payload
    assert any(ta.TABPFN_CKPT in u for u in urls)
    assert _tree(target.parent) == [ta.TABPFN_CKPT]                 # config.json removed
    assert info["cleaned"] == ["config.json"]
    assert _tree(tmp_path / "home") == ["cache", "cache/tabpfn", f"cache/tabpfn/{ta.TABPFN_CKPT}"]


@pytest.mark.tabpfn
def test_fetch_checkpoint_real_download_failure_leaves_nothing(tmp_path, monkeypatch):
    import huggingface_hub
    import tabpfn.model_loading as ml
    payload, target = _fake_ckpt(monkeypatch, tmp_path)
    monkeypatch.setattr(huggingface_hub, "hf_hub_download",
                        lambda *a, **k: (_ for _ in ()).throw(OSError("offline")))
    monkeypatch.setattr(ml.urllib.request, "urlopen",
                        lambda *a, **k: (_ for _ in ()).throw(OSError("offline")))
    with pytest.raises(RuntimeError, match="download failed"):
        ta.fetch_checkpoint(resolve=lambda: str(target))
    assert _tree(tmp_path / "home") == ["cache", "cache/tabpfn"]


def test_real_cache_untouched_by_these_tests():
    # the checkpoint the project uses is where it was, with the pinned sha
    ck = os.path.expanduser("~/Library/Caches/tabpfn/" + ta.TABPFN_CKPT)
    if os.path.exists(ck):
        assert ta.sha256_file(ck) == "cf8c519c01eaf1613ee91239006d57b1c806ff5f23ac1aeb1315ba1015210e49"


# ------------------------------------- AMENDMENT.md A1 wiring (review A1-1 F11a)
class _TiedClassifier:
    """predict_proba returns coarse probabilities (0.2 / 0.8), so test scores tie."""
    def fit(self, X, y):
        self.classes_ = np.array(sorted(set(int(v) for v in y)))
        return self

    def predict_proba(self, X):
        p = np.where(np.asarray(X)[:, 0] > 0, 0.8, 0.2)
        return np.stack([1 - p, p], 1) if len(self.classes_) == 2 else np.ones((len(p), 1))


def test_unit_stores_tie_neutral_primary_and_prereg_separately(tmp_path):
    import tie_neutral_metrics as tn
    version, _, _ = synth_version(n_bags=60, L=4, num_folds=2)
    spec = ta.UnitSpec("synthetic", "original", "tabpfn_bagmean", "native", "main",
                       model="logreg")
    ta.run_unit(spec, version, str(tmp_path), manifest(tmp_path), factory=_TiedClassifier,
                kw={}, log=lambda *_: None)
    d = ta.unit_dir(str(tmp_path), "synthetic", "original", "tabpfn_bagmean", "native", "main", "cpu")
    differs = False
    for stem in ("r0_f0", "r0_f1"):
        side = json.load(open(os.path.join(d, stem + ".json")))
        z = np.load(os.path.join(d, stem + ".npz"))
        Y, S, th = z["y_test"].astype(float), z["scores"], z["thresholds"]
        assert any(len(np.unique(r)) < len(r) for r in S)          # the fixture has ties
        neutral = tn.ranking_four(Y, S)
        prereg = AllFiveWithThresholds(Y, S, th)
        for k in tn.RANKING_METRICS:
            assert side["metrics"][k] == pytest.approx(neutral[k], abs=1e-12), k
            assert side["metrics_prereg"][k] == pytest.approx(float(prereg[k]), abs=1e-12), k
            differs |= abs(neutral[k] - float(prereg[k])) > 1e-9
        assert side["metrics"]["HammingLoss"] == side["metrics_prereg"]["HammingLoss"]
    assert differs                                   # a swap of the two keys would be caught
