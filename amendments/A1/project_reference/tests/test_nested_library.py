"""Synthetic-data tests for the nested published-library harness (task T03).

No real dataset is read. Data come from tabpfn_arms.make_synthetic. Java tests
call PredictDump.java against the unmodified KDIS jar; Octave tests call the
authors' MIMLNN.m. Each test names the PREREGISTERED.md rule it checks.

Run: ./.venv/bin/python -m pytest experiments/revision_r1/tests/test_nested_library.py -q
"""
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
R1 = os.path.dirname(HERE)
sys.path.insert(0, R1)

import deposit_check  # noqa: E402
import library_harness as lh  # noqa: E402
import run_nested_library as rnl  # noqa: E402
import t03_checks  # noqa: E402
import tabpfn_arms as ta  # noqa: E402
from run_kdis_baselines import classifier_block, run_one as kdis_native_run  # noqa: E402

HAVE_JAVA = shutil.which("java") is not None and os.path.exists(
    os.path.join(lh.KDIS_BUILD, "PredictDump.class"))
HAVE_OCTAVE = shutil.which("octave") is not None and os.path.exists(
    os.path.join(lh.MIMLNN_CODE, "MIMLNN.m"))
needs_java = pytest.mark.skipif(not HAVE_JAVA, reason="java or PredictDump build missing")
needs_octave = pytest.mark.skipif(not HAVE_OCTAVE, reason="octave or MIMLNN.m missing")

@pytest.fixture(autouse=True)
def _synthetic_mode():
    """Every test is a synthetic run (deposit guard: mode must be declared)."""
    lh.set_run_mode(True)
    yield
    lh.set_run_mode(True)


REAL_TODAY = deposit_check._today       # the module's real UTC clock, captured at import

SMALL = ["--grid-k", "5,10", "--grid-distances", "AveH,MaxH", "--grid-mimlnn", "0.4:1",
         "--grid-seeds", "0,1"]


def _split(n=60, design="repeated"):
    v, canonical = rnl.synthetic_version(n, design)
    return v, canonical


# --------------------------------------------------------------------- grids
def test_grid_sizes_full_and_voc():
    """§1.3: 7 x 3 x 4 = 84 KDIS + 3 x 3 MIMLNN, seeds 0-4, inner 5-fold.
    §6.5: VOC2012 2 distances x 2 k, ratio {0.2, 0.4}, lambda 1, seeds {0, 1}, inner 3."""
    g = lh.grid_for("letter_frost")
    assert sum(not c.is_mimlnn for c in g.candidates) == 84
    assert sum(c.is_mimlnn for c in g.candidates) == 9
    assert g.mimlnn_seeds == (0, 1, 2, 3, 4) and g.inner_k == 5
    v = lh.grid_for("voc2012")
    assert sum(not c.is_mimlnn for c in v.candidates) == 7 * 2 * 2
    assert {(c.ratio, c.lam) for c in v.candidates if c.is_mimlnn} == {(0.2, 1.0), (0.4, 1.0)}
    assert v.mimlnn_seeds == (0, 1) and v.inner_k == 3
    assert {c.method for c in g.candidates} == set(lh.LIBRARY_METHODS)


def test_kdis_block_changes_only_metric_and_k():
    """§1.3: every other line of each <classifier> block is the shipped one, verbatim."""
    for m in lh.KDIS_METHODS:
        shipped = classifier_block(m).splitlines()
        for d in ("AveH", "MaxH", "MinH"):
            for k in (5, 10, 15, 20):
                tuned = lh.kdis_block(lh.Candidate(m, distance=d, k=k)).splitlines()
                assert len(tuned) == len(shipped)
                for a, b in zip(shipped, tuned):
                    if a != b:
                        assert re.search(r"<metric name=|<(numOfNeighbours|nReferences|nCiters)>", a), (m, a, b)


def test_tokens():
    """§1.5 key tokens: <config> and MIMLNN seed conditions joined with '+'."""
    assert lh.Candidate("MIMLkNN", distance="AveH", k=10).config == "AveH-k10"
    assert lh.Candidate("MIMLNN", ratio=0.4, lam=1.0).config == "ratio0.4-lambda1"
    assert lh.Candidate("MIMLNN", ratio=0.2, lam=0.1).config == "ratio0.2-lambda0.1"
    assert lh.condition_token("main") == "main"
    assert lh.condition_token("main", 3) == "seed-s3"
    assert lh.condition_token("control-s1", 3) == "control-s1+seed-s3"


# --------------------------------------------------------------- inner folds
def test_inner_folds_partition_and_seed():
    """§1.3: inner permutation seed = 1000 + outer fold + 100 x repeat; contiguous blocks."""
    tr = np.random.default_rng(7).permutation(97)[:83]
    for r, f in ((0, 0), (2, 3)):
        folds = lh.inner_folds(tr, r, f, 5)
        assert [i for i, _, _ in folds] == list(range(5))
        tests = [te for _, _, te in folds]
        assert sorted(np.concatenate(tests).tolist()) == sorted(tr.tolist())
        sizes = [len(t) for t in tests]
        assert max(sizes) - min(sizes) <= 1
        for _, trn, te in folds:
            assert not set(trn) & set(te) and len(trn) + len(te) == len(tr)
            assert np.array_equal(trn, np.sort(trn))        # Q17: ascending canonical index
        order = np.random.default_rng(1000 + f + 100 * r).permutation(tr)   # addendum, literally
        assert np.array_equal(np.concatenate(tests), order)
        assert np.array_equal(order, tr[np.random.default_rng(1000 + f + 100 * r).permutation(len(tr))])
        again = lh.inner_folds(tr, r, f, 5)
        assert all(np.array_equal(a[2], b[2]) for a, b in zip(folds, again))
    assert not np.array_equal(lh.inner_folds(tr, 0, 1, 5)[0][2], lh.inner_folds(tr, 1, 1, 5)[0][2])


def test_inner_folds_grouped_h2a():
    """H2-A step 5: 9 training pools ranked by fold index, pool rank rho -> inner fold rho mod 5
    (2, 2, 2, 2, 1 pools)."""
    n = 100
    canonical = [(None, list(range(10 * g, 10 * g + 10))) for g in range(10)]
    groups = lh.pool_groups(canonical)
    f = 3
    tr = np.array([i for i in range(n) if groups[i] != f])
    folds = lh.inner_folds(tr, 0, f, 5, groups)
    pools_per = [sorted({groups[int(b)] for b in te}) for _, _, te in folds]
    assert pools_per == [[0, 6], [1, 7], [2, 8], [4, 9], [5]]
    for _, trn, te in folds:
        assert not {groups[int(b)] for b in trn} & {groups[int(b)] for b in te}
        assert np.array_equal(trn, np.sort(trn))            # Q17


# ----------------------------------------------------------------- selection
C = lh.Candidate


def test_select_orientation_and_mean():
    """AP is maximised; Hamming loss, one-error, coverage, ranking loss minimised
    (review r1 F4: every metric pinned)."""
    s = {C("A", "AveH", 5): [0.5, 0.6], C("B", "AveH", 5): [0.7, 0.8]}
    for m in lh.FIVE:
        assert lh.select(s, m)[0].method == ("B" if m == "AveragePrecision" else "A"), m
    assert lh.HIGHER_BETTER == {"AveragePrecision"}


def test_select_tiebreak_order():
    """§1.3 tie-break: better inner mean -> lower inner SD -> method name -> smaller k."""
    w, _, by = lh.select({C("B", "AveH", 5): [0.375, 0.625], C("A", "AveH", 5): [0.25, 0.75]},
                         "AveragePrecision")
    assert (w.method, by) == ("B", "inner SD")
    # Q13: means 1 ulp apart (0.6 vs 0.6000000000000001) are tied; SD decides
    assert np.mean([0.5, 0.7]) != np.mean([0.4, 0.8])
    w, table, by = lh.select({C("B", "AveH", 5): [0.5, 0.7], C("A", "AveH", 5): [0.4, 0.8]},
                             "AveragePrecision")
    assert (w.method, by) == ("B", "inner SD") and all(r["tied_on_mean"] for r in table)
    # a difference above 1e-12 is not a tie
    w, _, by = lh.select({C("B", "AveH", 5): [0.6, 0.6], C("A", "AveH", 5): [0.6 + 2e-12] * 2},
                         "AveragePrecision")
    assert (w.method, by) == ("A", "inner mean")
    w, _, by = lh.select({C("B", "AveH", 5): [0.6, 0.6], C("A", "AveH", 10): [0.6, 0.6]},
                         "AveragePrecision")
    assert (w.method, by) == ("A", "method name")
    w, _, by = lh.select({C("A", "AveH", 15): [0.6, 0.6], C("A", "MaxH", 10): [0.6, 0.6]},
                         "HammingLoss")
    assert (w.k, by) == (10, "k")
    w, _, by = lh.select({C("A", "MinH", 10): [0.6, 0.6], C("A", "AveH", 10): [0.6, 0.6]},
                         "HammingLoss")
    assert (w.distance, by) == ("AveH", "distance")          # §1.3 addendum
    w, _, by = lh.select({C("MIMLNN", ratio=0.4, lam=1.0): [0.6, 0.6],
                          C("MIMLNN", ratio=0.2, lam=10.0): [0.6, 0.6]}, "Coverage")
    assert (w.ratio, by) == (0.2, "ratio")                    # §1.3 addendum


def test_select_excludes_failed():
    """§1.3: a candidate that failed in any inner fold is excluded in that outer fold."""
    s = {C("A", "AveH", 5): None, C("B", "AveH", 5): [0.1, 0.2]}
    w, table, _ = lh.select(s, "AveragePrecision")
    assert w.method == "B" and len(table) == 1
    assert lh.select({C("A", "AveH", 5): None}, "AveragePrecision")[0] is None


def test_score_hamming_from_native_bipartition():
    """§1.3: KDIS/MIMLNN produce bipartitions natively; ranking metrics use scores."""
    Y = np.array([[1, 0, 1], [0, 1, 0]])
    scores = np.array([[0.9, 0.8, 0.1], [0.2, 0.3, 0.1]])
    bip = np.array([[1, 0, 1], [0, 1, 0]], dtype=np.uint8)
    m = lh.score(Y, scores, bip)
    assert m["HammingLoss"] == 0.0           # from bip, not from scores > 0.5
    assert m["OneError"] == 0.0 and m["AveragePrecision"] < 1.0


# --------------------------------------------------------------------- inputs
def test_arff_is_lossless(tmp_path):
    """§1.4: raw features, exactly: every float64 survives the text round trip."""
    rng = np.random.default_rng(0)
    bags = {i: rng.normal(size=(3, 4)) * 10.0 ** rng.integers(-8, 8) for i in range(5)}
    Y = {i: np.array([1, 0]) for i in range(5)}
    p = tmp_path / "x.arff"
    lh.write_arff(str(p), "x", np.arange(5), bags, Y)
    lines = [l for l in p.read_text().splitlines() if re.match(r"^\d+,\"", l)]
    for l in lines:
        i = int(l.split(",")[0])
        body = l.split('"')[1]
        vals = np.array([[float(v) for v in row.split(",")] for row in body.split("\\n")])
        assert np.array_equal(vals, bags[i])


# ------------------------------------------------------------ child processes
def test_run_child_statuses(tmp_path):
    """§6.6: CPU-time limit -> timeout; non-zero exit -> crash; OutOfMemoryError -> oom."""
    py = sys.executable
    ok = lh.run_child([py, "-c", "print(1)"], str(tmp_path / "a.log"), 60)
    assert ok["status"] == "ok" and ok["cpu_s"] >= 0 and ok["peak_rss_bytes"] > 0
    crash = lh.run_child([py, "-c", "import sys; sys.exit(3)"], str(tmp_path / "b.log"), 60)
    assert crash["status"] == "crash" and crash["returncode"] == 3
    oom = lh.run_child(["/bin/sh", "-c", "echo java.lang.OutOfMemoryError; exit 1"],
                       str(tmp_path / "c.log"), 60)
    assert oom["status"] == "oom"
    # load-robust: the verdict and the bounds are in the child's own CPU seconds,
    # never in wall time (a loaded machine only slows the child down)
    to = lh.run_child([py, "-c", "while True: pass"], str(tmp_path / "d.log"), 1,
                      wall_guard_s=LOAD_SAFE_WALL_GUARD_S)
    assert to["status"] == "timeout" and 0.9 <= to["cpu_s"] <= 1.0 + CPU_TOL_S, to
    assert {"load1_start", "concurrent_at_start", "wall_s"} <= set(ok)


def test_memory_budget_bounds_concurrency():
    """§6.1: N x Xmx <= 16 GiB and N <= 8."""
    assert lh.concurrency(2) == 8 and lh.concurrency(8) == 2
    assert lh.default_xmx_gib("voc2012") == 8 and lh.default_xmx_gib("corel5k") == 8
    assert lh.default_xmx_gib("scene") == 2
    budget, active, peak, lock = lh.MemoryBudget(16, 8), [0], [0], threading.Lock()

    def job():
        with budget(8):
            with lock:
                active[0] += 1
                peak[0] = max(peak[0], active[0])
            time.sleep(0.5)          # long hold: overlap is reliable even under load
            with lock:
                active[0] -= 1
    ts = [threading.Thread(target=job) for _ in range(6)]
    [t.start() for t in ts]
    [t.join() for t in ts]
    assert peak[0] == 2


# ------------------------------------------------------------------- Java
@needs_java
def test_predictdump_reproduces_library_run(tmp_path):
    """§1.5: PredictDump on the unmodified jar gives the predictions the library's
    own EvaluatorHoldout run scores; Mulan's measures on the dump equal the
    library report, and miml_metrics AP equals Mulan AP."""
    v, _ = _split()
    s = v.splits[0]
    inputs = lh.export_split(s, str(tmp_path / "in"), "t", {"refit": (s.ids_tr, s.ids_te)}, ("kdis",))
    Yte = np.stack([s.Y[int(i)] for i in s.ids_te])
    for m in ("MIMLkNN", "MIMLIBLR", "MIMLBagging"):
        c = lh.Candidate(m, distance="MaxH", k=5)
        rec, sc, bip = lh.run_kdis_unit(c, inputs, "refit", s.ids_te, str(tmp_path / m), 2, 600)
        assert rec["status"] == "ok", rec["log_tail"]
        assert sc.shape == Yte.shape and set(np.unique(bip)) <= {0, 1}
        native, err = kdis_native_run(m, lh.kdis_block(c), *inputs.pairs["refit"], inputs.xml,
                                      str(tmp_path / m / "native"))
        assert err is None
        for k in lh.FIVE:
            assert abs(rec["native_measures"][k] - native[k]) <= 1e-12, (m, k)
        # deposited scorer (as before AMENDMENT.md A1) and Mulan's own tie rule
        assert abs(lh.score_prereg(Yte, sc, bip)["AveragePrecision"] - native["AveragePrecision"]) <= 1e-12
        assert abs(lh.score_prereg(Yte, sc, bip)["HammingLoss"] - native["HammingLoss"]) <= 1e-12
        assert abs(lh.score(Yte, sc, bip)["HammingLoss"] - native["HammingLoss"]) <= 1e-12
        mu = lh.tn.ranking_four_mulan(Yte, sc)
        for k in lh.tn.RANKING_METRICS:
            assert abs(mu[k] - rec["native_measures"][k]) <= 1e-12, (m, k)
        # primary (A1): tie-neutral ranking metrics on the dumped scores
        assert lh.score(Yte, sc, bip)["AveragePrecision"] == lh.tn.ranking_four(Yte, sc)["AveragePrecision"]


@needs_java
def test_predictdump_deterministic_and_header_rule(tmp_path):
    """T03-a on synthetic: twice -> byte-identical. Also pins finding F2: MIMLIBLR
    depends on the declared id set, so every file of a fold declares the universe."""
    v, _ = _split()
    s = v.splits[0]
    _, tr, te = lh.inner_folds(s.ids_tr, 0, 0, 5)[0]
    inputs = lh.export_split(s, str(tmp_path / "in"), "t", {"i0": (tr, te)}, ("kdis",))
    hdr = open(inputs.pairs["i0"][0]).read().split("@attribute bag")[0]
    assert all(str(int(i)) in hdr for i in s.ids_te)       # universe declared
    c = lh.Candidate("MIMLIBLR", distance="AveH", k=10)
    outs = []
    for rep in (1, 2):
        rec, sc, _ = lh.run_kdis_unit(c, inputs, "i0", te, str(tmp_path / f"r{rep}"), 2, 600)
        assert rec["status"] == "ok"
        outs.append(open(tmp_path / f"r{rep}" / "unit.scores.csv").read())
    assert outs[0] == outs[1]


@needs_java
def test_mulanscore_runs(tmp_path):
    rng = np.random.default_rng(0)
    Y = rng.integers(0, 2, size=(8, 3))
    (tmp_path / "s").mkdir()
    np.savetxt(tmp_path / "t.csv", Y, fmt="%d", delimiter=",")
    S = rng.uniform(size=Y.shape)
    np.savetxt(tmp_path / "s" / "0000.csv", S, fmt="%.17g", delimiter=",")
    subprocess.run(["java", "-cp", f"{lh.JAR}:{lh.KDIS_BUILD}", "MulanScore", str(tmp_path / "t.csv"),
                    str(tmp_path / "s"), str(tmp_path / "o.csv")], check=True, capture_output=True)
    row = open(tmp_path / "o.csv").read().splitlines()[1].split(",")
    assert abs(float(row[5]) - lh.score(Y, S, (S > 0.5).astype(np.uint8))["AveragePrecision"]) < 1e-12 \
        or (Y.sum(1) == 0).any()


# ------------------------------------------------------------------ Octave
@needs_octave
def test_mimlnn_seed_control(tmp_path):
    """T03-e on synthetic: the same Octave seed twice -> identical outputs, through
    the clock shim (MIML_cluster.m reseeds from the clock)."""
    v, _ = _split()
    s = v.splits[0]
    inputs = lh.export_split(s, str(tmp_path / "in"), "t", {}, ("mimlnn",))
    c = lh.Candidate("MIMLNN", ratio=0.4, lam=1.0)
    runs = {}
    for tag, seed in (("a", 0), ("b", 0), ("c", 1)):
        rec, sc, bip = lh.run_mimlnn_unit(c, seed, inputs, s.ids_tr, s.ids_te, str(tmp_path / tag), 600)
        assert rec["status"] == "ok", rec["log_tail"]
        assert rec["timing_note"] == "fit + predict, not separable"
        assert rec["max_abs_imag"] >= 0 and rec["flag_imag_above_1e-8"] in (False, True)
        runs[tag] = open(tmp_path / tag / "unit.scores.csv").read()
    assert runs["a"] == runs["b"]
    assert runs["a"] != runs["c"]


@needs_octave
def test_run_mimlnn_legacy_mode_unchanged(tmp_path):
    """The 3-argument call used for the submission still works (called as
    run_lamda_baselines.py calls it: Auxiliary added by the caller)."""
    from scipy.io import savemat
    bags, Y = ta.make_synthetic(n_bags=30, d=3, L=3, seed=1)
    cell = lambda idx: np.array([[np.asarray(bags[i], float)] for i in idx], dtype=object)
    T = np.where(Y > 0, 1.0, -1.0)
    savemat(tmp_path / "f.mat", {"train_bags": cell(range(20)), "train_target": T[:20].T,
                                 "test_bags": cell(range(20, 30)), "test_target": T[20:].T})
    subprocess.run(["octave", "--no-gui", "--norc", "--quiet", "--path", lh.LAMDA_DIR, "--eval",
                    f"addpath('{lh.MIMLNN_CODE}/Auxiliary'); "
                    f"run_mimlnn('{tmp_path / 'f.mat'}','{lh.MIMLNN_CODE}','{tmp_path / 'o.csv'}')"],
                   check=True, capture_output=True, env=dict(os.environ, **{"OMP_NUM_THREADS": "1"}),
                   cwd=tmp_path)
    assert open(tmp_path / "o.csv").read().startswith("HammingLoss,OneError")


# ---------------------------------------------------------------- runner
def _run(tmp_path, *extra, methods="MIMLkNN,MIMLNN", folds=2, n=60):
    root, work = tmp_path / "root", tmp_path / "work"
    argv = ["--synthetic", str(n), "--dataset", "synthetic", "--folds", str(folds),
            "--root", str(root), "--workdir", str(work), "--methods", methods, *SMALL, *extra]
    return rnl.main(argv), root


def _results(root):
    return json.load(open(root / "library" / "synthetic__original__main.json"))


@needs_java
@needs_octave
def test_runner_end_to_end_and_reuse(tmp_path):
    """§1.3 selection per metric for the library and each method; §1.5 keys,
    no-overwrite and reuse; §6.2 cost fields."""
    rc, root = _run(tmp_path)
    assert rc == 0
    d = _results(root)
    assert set(d["folds"]) == {"r0_f0", "r0_f1"}
    f0 = d["folds"]["r0_f0"]
    assert set(f0["selection"]) == {"library", "MIMLkNN", "MIMLNN"}
    for proc in f0["selection"].values():
        assert set(proc) == set(lh.FIVE)
        for e in proc.values():
            assert e["test"] is not None and e["decided_by"] and "inner_sd" in e
    assert f0["inner_sizes"] and len(f0["inner_sizes"]) == 5
    # review r3 F1: MIMLNN outer test = mean over seeds, across-seed SD ddof = 1
    t = f0["refit_test"]["MIMLNN/ratio0.4-lambda1"]
    assert len(t["per_seed"]) == 2 and t["repetitions"] == "seeded"
    for m in lh.FIVE:
        vals = [p[m] for p in t["per_seed"]]
        assert t[m] == pytest.approx(np.mean(vals), abs=1e-15)
        assert t["across_run_sd"][m] == pytest.approx(np.std(vals, ddof=1), abs=1e-15)
    npz = sorted(glob.glob(str(root / "predictions" / "**" / "*.npz"), recursive=True))
    # inner units: (4 KDIS + 1 MIMLNN x 2 seeds) x 5 inner x 2 folds; plus refits
    inner = [p for p in npz if re.search(r"_i\d\.npz$", p)]
    assert len(inner) == (4 + 2) * 5 * 2
    assert any("/MIMLNN/ratio0.4-lambda1/seed-s1/r0_f1.npz" in p for p in npz)
    z = np.load(inner[0])
    assert z["scores"].dtype == np.float64 and z["bip"].dtype == np.uint8 and z["test_idx"].dtype == np.int64
    side = json.load(open(inner[0].replace(".npz", ".json")))
    assert {"cpu_s", "peak_rss_bytes", "load1_start", "concurrent_at_start"} <= set(side["record"])
    mt = {p: os.stat(p).st_mtime_ns for p in npz}
    # rerun: every unit reused, nothing rewritten, selection identical
    d0 = json.dumps(d["folds"]["r0_f0"]["selection"], sort_keys=True)
    rc, _ = _run(tmp_path, "--recompute-selection")
    assert rc == 0
    assert {p: os.stat(p).st_mtime_ns for p in npz} == mt
    d1 = _results(root)
    assert json.dumps(d1["folds"]["r0_f0"]["selection"], sort_keys=True) == d0
    manifests = sorted(glob.glob(str(root / "manifests" / "*.jsonl")))
    last = [json.loads(l) for l in open(manifests[-1])]
    assert {r["type"] for r in last} == {"run", "reuse"}
    # a stored unit with a different identity is never reused silently
    s = json.load(open(inner[0].replace(".npz", ".json")))
    s["identity"]["train_ids_sha256"] = "x"
    os.chmod(inner[0].replace(".npz", ".json"), 0o644)
    json.dump(s, open(inner[0].replace(".npz", ".json"), "w"))
    with pytest.raises(RuntimeError, match="different identity"):
        _run(tmp_path, "--recompute-selection")


@needs_java
def test_second_writer_refused(tmp_path):
    """Lesson 9 / §1.7: one writer per results JSON."""
    root = tmp_path / "root"
    w = rnl.ResultsWriter(str(root / "library" / "x.json"))
    try:
        with pytest.raises(SystemExit, match="another writer"):
            rnl.ResultsWriter(str(root / "library" / "x.json"))
    finally:
        w.close()


def _fake_mimlnn(tmp_path, body):
    d = tmp_path / "fake_mimlnn"
    (d / "Auxiliary").mkdir(parents=True)
    (d / "MIMLNN.m").write_text(
        "function [HL,RL,OE,CV,AP,AR,AF,Outputs,Pre_Labels]=MIMLNN(train_bags,train_target,"
        "test_bags,test_target,ratio,lambda)\n" + body +
        "\n  Outputs = repmat(mean(train_target,2), 1, size(test_target,2)) + 1e-3*(1:size(test_target,1))';\n"
        "  Pre_Labels = 2*(Outputs>=0)-1; HL=0;RL=0;OE=0;CV=0;AP=0;AR=0;AF=0;\nend\n")
    return str(d)


@needs_java
@needs_octave
def test_failed_candidate_excluded_and_not_retried(tmp_path):
    """§1.3: a candidate that crashes in an inner fold is excluded for that outer
    fold (reported); §6.6: crashes twice -> failed; a failed unit is not rerun."""
    code = _fake_mimlnn(tmp_path, "  error('synthetic crash');")
    rc, root = _run(tmp_path, "--mimlnn-code", code, folds=1)
    assert rc == 0
    f0 = _results(root)["folds"]["r0_f0"]
    assert "MIMLNN/ratio0.4-lambda1" in f0["excluded"]
    assert f0["selection"]["MIMLNN"]["AveragePrecision"]["n_eligible"] == 0
    assert f0["selection"]["library"]["AveragePrecision"]["selected"]["method"] == "MIMLkNN"
    fails = glob.glob(str(root / "predictions" / "**" / "*.fail.json"), recursive=True)
    assert len(fails) == 2 * 5
    rec = json.load(open(fails[0]))["record"]
    assert [a["status"] for a in rec["attempts"]] == ["crash", "crash"]
    mt = os.stat(fails[0]).st_mtime_ns
    rc, _ = _run(tmp_path, "--mimlnn-code", code, "--recompute-selection", folds=1)
    assert os.stat(fails[0]).st_mtime_ns == mt


@needs_java
@needs_octave
def test_refit_failure_reported_not_replaced(tmp_path):
    """§1.3 addendum: the selected candidate's refit fails -> that (fold, metric) is
    recorded failed and held under the §6.7 stop rule (exit 3); no fallback to the
    runner-up; later independent folds still run (continuation rule)."""
    code = _fake_mimlnn(tmp_path, "  if numel(train_bags) > 50, error('refit crash'); end")
    rc, root = _run(tmp_path, "--mimlnn-code", code, methods="MIMLNN", folds=2)
    assert rc == 3
    d = _results(root)
    e = d["folds"]["r0_f0"]["selection"]["MIMLNN"]["AveragePrecision"]
    assert e["selected"]["method"] == "MIMLNN" and e["test"] is None and e["refit_failed"]
    assert set(d["held"]) == {"r0_f0", "r0_f1"}


@needs_java
def test_pilot_writes_times_only(tmp_path):
    """§6.3: the pilot times inner fold 0 and the refit of fold 0 for every
    candidate; predictions are discarded unscored."""
    root = tmp_path / "root"
    rc = rnl.main(["--synthetic", "60", "--dataset", "synthetic", "--root", str(root),
                   "--workdir", str(tmp_path / "w"), "--methods", "MIMLkNN,MIMLNN", "--grid-k", "5",
                   "--grid-distances", "AveH", "--grid-mimlnn", "0.4:1", "--grid-seeds", "0",
                   "--pilot"])
    assert rc == 0
    p = json.load(open(root / "pilots" / "library__synthetic__original__main.json"))
    u = p["units"]["MIMLkNN/AveH-k5"]
    assert u["inner"]["status"] == "ok" and u["refit"]["cpu_s"] > 0
    proj = p["projection_process_hours"]
    assert proj["total"] > 0 and proj["refit_upper_bound"] > 0
    # §6.3 addendum: per method, the 5 largest refit times (here 1 candidate)
    assert abs(proj["refit_bound_per_outer_fold_s_by_method"]["MIMLkNN"] - u["refit"]["cpu_s"]) < 1e-9
    assert p["mimlnn_per_call_cpu_s"]["refit"]["n_calls"] == 1      # Q10
    assert not (root / "predictions").exists()


@needs_java
def test_grouped_inner_and_repeated_design(tmp_path):
    """H2-A grouped inner folds run end to end; §1.2 repeated design keys r<s>_f<j>."""
    rc, root = _run(tmp_path, "--synthetic-grouped", methods="MIMLkNN", folds=1)
    assert rc == 0
    v, _ = rnl.synthetic_version(60, "repeated")
    assert [(s.repeat, s.fold) for s in v.splits][:6] == [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 0)]
    assert len(v.splits) == 25


def test_real_data_refused_before_deposit(tmp_path, monkeypatch):
    """HARD RULE / §6.0 step 0: no real-data run before the deposit. Fail-safe
    (A1 review 2, F8): every output path is under tmp_path, and a run that got
    past the guard would stop at its first real read (conftest._no_real_data)."""
    monkeypatch.setattr(lh, "deposit_recorded", lambda *a, **k: False)
    with pytest.raises(SystemExit, match="PENDING"):
        rnl.main(["--dataset", "letter_frost", "--root", str(tmp_path / "root"),
                  "--workdir", str(tmp_path / "w")])
    with pytest.raises(SystemExit, match="not deposited"):
        t03_checks.main(["a", "--evidence-dir", str(tmp_path / "ev"), "--workdir", str(tmp_path / "w2")])


# --------------------------------------------------------------- T03 checks
@needs_java
@needs_octave
def test_t03_checks_on_synthetic(tmp_path):
    rc = t03_checks.main(["a,b,d,e,f", "--synthetic", "60", "--n-matrices", "20",
                          "--evidence-dir", str(tmp_path / "ev"), "--workdir", str(tmp_path / "w")])
    assert rc == 0
    a = json.load(open(tmp_path / "ev" / "T03-a__synthetic60.json"))
    assert a["pass"]
    b = json.load(open(tmp_path / "ev" / "T03-b__synthetic60.json"))
    assert all(m["mulan_inprocess_equals_library_run"] for m in b["methods"].values())
    e = json.load(open(tmp_path / "ev" / "T03-e__synthetic60.json"))
    assert e["pass"]
    f = json.load(open(tmp_path / "ev" / "T03-f__synthetic60.json"))
    assert f["mulan"]["pass"]
    # LAMDA's AP drops bags carrying every label; on the remaining bags it agrees exactly
    assert f["diagnostic_lamda_on_bags_with_some_but_not_all_labels"]["max_abs_dAP"] < 1e-12


def test_t03g_compare_to_stored():
    a = {"per_fold": [{m: 0.5 for m in lh.FIVE}, {m: 0.25 for m in lh.FIVE}]}
    b = {"per_fold": [{m: 0.5 for m in lh.FIVE}, {m: 0.25 + 1e-10 for m in lh.FIVE}]}
    ok, rows = t03_checks.compare_to_stored(a, b, 1e-9, lh.FIVE)
    assert ok
    b["per_fold"][1]["AveragePrecision"] += 1e-6
    ok, rows = t03_checks.compare_to_stored(a, b, 1e-9, lh.FIVE)
    assert not ok and rows[1]["above_tol"]


def test_export_design_matches_runner_folds(tmp_path):
    """Deliverable 1: the exported design is the runner's design (same ids)."""
    import export_library_design as eld
    out = tmp_path / "d.json"
    assert eld.main(["--synthetic", "60", "--dataset", "synthetic", "--synthetic-design", "repeated",
                     "--out", str(out), "--write-files", str(tmp_path / "files")]) == 0
    d = json.load(open(out))
    v, _ = rnl.synthetic_version(60, "repeated")
    assert len(d["folds"]) == 25 and d["inner_k"] == 5
    for rec, s in zip(d["folds"], v.splits):
        assert rec["train_ids"] == s.ids_tr.tolist() and rec["test_ids"] == s.ids_te.tolist()
        inner = lh.inner_folds(s.ids_tr, s.repeat, s.fold, 5)
        assert [x["test_ids"] for x in rec["inner"]] == [te.tolist() for _, _, te in inner]
    assert (tmp_path / "files" / "r4_f4" / "refit_train.arff").exists()
    assert (tmp_path / "files" / "r0_f0" / "i4_test.arff").exists()
    with pytest.raises(FileExistsError):
        eld.main(["--synthetic", "60", "--dataset", "synthetic", "--out", str(out)])


def test_degenerate_label_override():
    """§1.3 F4 (addendum): a label with no positive training bag is predicted
    constant negative for library outputs too; raw output kept beside it."""
    Ytr = np.array([[1, 0, 0], [0, 0, 1]])
    deg = lh.degenerate_labels(Ytr)
    assert deg.tolist() == [1]
    s, b = lh.apply_degenerate(np.array([[0.2, 0.9, 0.1]]), np.array([[0, 1, 0]]), deg, -1.0)
    assert s.tolist() == [[0.2, -1.0, 0.1]] and b.tolist() == [[0, 0, 0]]


@needs_java
def test_runner_stores_raw_and_overwritten(tmp_path):
    """Stored unit carries scores/bip used for scoring and the raw library output."""
    bags, Y = ta.make_synthetic(n_bags=60, d=3, L=4, seed=0)
    rc, root = _run(tmp_path, methods="MIMLkNN", folds=1)
    z = np.load(glob.glob(str(root / "predictions" / "**" / "r0_f0_i0.npz"), recursive=True)[0])
    assert {"scores", "bip", "scores_raw", "bip_raw", "degenerate_labels", "negative_score"} <= set(z.files)
    s, b = lh.apply_degenerate(z["scores_raw"], z["bip_raw"], z["degenerate_labels"], float(z["negative_score"]))
    assert np.array_equal(s, z["scores"]) and np.array_equal(b, z["bip"])


def test_t03g_tabpfn_part_refused(monkeypatch):
    """Q20: the TabPFN part of T03-g belongs to T04."""
    monkeypatch.setattr(lh, "deposit_recorded", lambda *a, **k: True)
    with pytest.raises(SystemExit, match="T04"):
        t03_checks.main(["g", "--dataset", "letter_frost", "--g-config", "tabpfn_bagmean"])


@needs_java
@needs_octave
def test_refit_training_order_ascending(tmp_path):
    """Plan clarification (review 11 finding 5): the refit trains on the outer
    training bags in ascending canonical index, for KDIS (training ARFF row
    order) and MIMLNN (row file), although ids_tr itself is in §1.3 order."""
    rc, root = _run(tmp_path, "--keep-inputs", "--keep-workdirs", folds=1)
    assert rc == 0
    v, _ = rnl.synthetic_version(60, "canonical")
    s = v.splits[0]
    assert not np.array_equal(s.ids_tr, np.sort(s.ids_tr))     # the §1.3 order is not sorted
    want = np.sort(s.ids_tr)
    arff = glob.glob(str(tmp_path / "work" / "**" / "inputs" / "refit_train.arff"), recursive=True)[0]
    rows = [int(l.split(",")[0]) for l in open(arff) if re.match(r"^\d+,\"", l)]
    assert rows == want.tolist()
    for side in glob.glob(str(root / "predictions" / "**" / "r0_f0.json"), recursive=True):
        assert json.load(open(side))["identity"]["train_ids_sha256"] == rnl._sha_ids(want)
    rowfile = glob.glob(str(tmp_path / "work" / "**" / "MIMLNN" / "**" / "refit" / "a1" / "train.rows"),
                        recursive=True)
    for rf in rowfile:
        r1 = np.loadtxt(rf, dtype=int)
        assert np.all(np.diff(r1) > 0)          # .mat rows are the sorted universe, so ascending ids
    assert rowfile
    assert lh.refit_train_ids(np.array([5, 2, 9])).tolist() == [2, 5, 9]



# ------------------------------------------------- code review 1 (CODE-T03 r1)
# Timing tests are load-robust (T04 saw failures at load ~8.5 from other
# agents): limits are CPU seconds read by the same accounting as production
# (os.wait4 / the parent's group poll), the wall guard is far away so it can
# never decide a CPU-limit test, and no assertion uses wall time.
LOAD_SAFE_WALL_GUARD_S = 600.0
CPU_TOL_S = 2.0          # generous overshoot: poll interval and start-up CPU


def _gone(pid, wait_s=30.0):
    """True once pid no longer exists (allows a loaded machine time to reap)."""
    t0 = time.time()
    while time.time() - t0 < wait_s:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return True
        time.sleep(0.1)
    return False


SIGXCPU_IGNORING_BUSY = ("import signal\nsignal.signal(signal.SIGXCPU, signal.SIG_IGN)\n"
                         "while True: pass")


def test_cpu_limit_enforced_when_child_ignores_sigxcpu(tmp_path):
    """r1 F1/F5: a child that ignores SIGXCPU (as Octave does) is still stopped
    at the §6.6 CPU limit by the parent and classified 'timeout'."""
    r = lh.run_child([sys.executable, "-c", SIGXCPU_IGNORING_BUSY], str(tmp_path / "a.log"), 1.0,
                     wall_guard_s=LOAD_SAFE_WALL_GUARD_S)
    assert r["status"] == "timeout" and r["killed_by"] == "parent cpu poll", r
    assert 0.9 <= r["cpu_s"] <= 1.0 + CPU_TOL_S, r


def test_cpu_limit_counts_whole_process_group(tmp_path):
    """r1 F1: CPU of every process in the child's group counts and the whole
    group is killed (no orphan keeps burning CPU)."""
    marker = tmp_path / "pids"
    script = (f"{sys.executable} -c '{SIGXCPU_IGNORING_BUSY}' & echo $! >> {marker}; "
              f"{sys.executable} -c '{SIGXCPU_IGNORING_BUSY}' & echo $! >> {marker}; wait")
    r = lh.run_child(["/bin/sh", "-c", script], str(tmp_path / "b.log"), 2.0,
                     wall_guard_s=LOAD_SAFE_WALL_GUARD_S)
    assert r["status"] == "timeout" and r["killed_by"] == "parent cpu poll", r
    assert 2.0 <= r["cpu_polled_max_s"] <= 2.0 + CPU_TOL_S, r
    for pid in map(int, marker.read_text().split()):
        assert _gone(pid), pid


def test_wall_guard_kills_idle_child(tmp_path):
    r = lh.run_child([sys.executable, "-c", "import time; time.sleep(600)"], str(tmp_path / "c.log"),
                     100, wall_guard_s=1.0)
    # CPU-idle child: only the wall guard can stop it; bounds are loose on purpose
    assert r["status"] == "wall-guard" and r["killed_by"] == "wall guard", r
    assert r["wall_s"] >= 1.0 and r["cpu_s"] < 100


@needs_octave
def test_octave_busy_loop_stopped_at_cpu_limit(tmp_path):
    """r1 F1: the production case, Octave ignoring SIGXCPU."""
    r = lh.run_child(["octave", "--no-gui", "--norc", "--quiet", "--eval", "while true, end"],
                     str(tmp_path / "o.log"), 2.0, wall_guard_s=LOAD_SAFE_WALL_GUARD_S)
    assert r["status"] == "timeout" and r["killed_by"] == "parent cpu poll", r
    assert 2.0 <= r["cpu_polled_max_s"] <= 2.0 + CPU_TOL_S, r


@needs_java
def test_unit_cap_counts_prior_hours(tmp_path):
    """r1 F2: hours stored by earlier runs count against the cap inside a fold."""
    root = tmp_path / "root"
    path = root / "library" / "synthetic__original__main.json"
    path.parent.mkdir(parents=True)
    cap = 1.0
    json.dump({"process_hours_used": cap - 1e-7}, open(path, "w"))
    rc, _ = _run(tmp_path, "--unit-cap-hours", str(cap), "--jobs", "1", methods="MIMLkNN", folds=1)
    assert rc == 3
    d = _results(root)
    assert "paused" in d and d["process_hours_used"] > cap
    npz = glob.glob(str(root / "predictions" / "**" / "*.npz"), recursive=True)
    assert len(npz) == 1          # the first charged unit trips the cap; nothing else runs


def test_build_must_match_sources(tmp_path, monkeypatch):
    """r1 F3: classes not compiled from the current sources are refused."""
    fake = tmp_path / "build"
    shutil.copytree(lh.KDIS_BUILD, fake)
    monkeypatch.setattr(lh, "KDIS_BUILD", str(fake))
    assert lh.check_build()["sources_sha256"]["PredictDump.java"]
    lines = (fake / "SOURCES.sha256").read_text().splitlines()
    lines[0] = "0" * 64 + lines[0][64:]
    (fake / "SOURCES.sha256").write_text("\n".join(lines) + "\n")
    with pytest.raises(SystemExit, match="not compiled from the current"):
        lh.check_build()
    (fake / "SOURCES.sha256").unlink()
    with pytest.raises(SystemExit, match="missing"):
        lh.check_build()


@needs_java
@needs_octave
def test_pilot_flags_failed_units_and_cap_refuses(tmp_path):
    """r1 F6: failed pilot units are listed and the projection is marked
    incomplete; r1 F9: no unit cap is derived from such a pilot."""
    code = _fake_mimlnn(tmp_path, "  error('synthetic crash');")
    root = tmp_path / "root"
    rnl.main(["--synthetic", "60", "--dataset", "synthetic", "--root", str(root),
              "--workdir", str(tmp_path / "w"), "--methods", "MIMLkNN,MIMLNN", "--grid-k", "5",
              "--grid-distances", "AveH", "--grid-mimlnn", "0.4:1", "--grid-seeds", "0",
              "--mimlnn-code", code, "--pilot"])
    pj = root / "pilots" / "library__synthetic__original__main.json"
    p = json.load(open(pj))
    assert p["n_units_not_ok"] == 2 and p["projection_process_hours"]["incomplete"]
    assert all(k.startswith("MIMLNN/") for k in p["units_not_ok"])
    with pytest.raises(SystemExit, match="incomplete"):
        _run(tmp_path, "--pilot-json", str(pj), methods="MIMLkNN", folds=1)


def test_unit_cap_derivation():
    """r1 F9: cap = min(3 x pilot projection, 450); an override is logged."""
    class A:
        unit_cap_hours = None
    pilot = {"projection_process_hours": {"total": 10.0, "incomplete": False, "retime_needed": False}}
    assert rnl.resolve_unit_cap(A, pilot) == (30.0, "min(3 x pilot projection, 450) (§6.6)")
    pilot["projection_process_hours"]["total"] = 200.0
    assert rnl.resolve_unit_cap(A, pilot)[0] == 450.0
    A.unit_cap_hours = 12.0
    cap, src = rnl.resolve_unit_cap(A, pilot)
    assert cap == 12.0 and "operator override" in src and "450" in src
    A.unit_cap_hours = None
    assert rnl.resolve_unit_cap(A, None) == (None, "none (no pilot JSON, no override)")


def test_export_hashes_projected_data_without_files(tmp_path, monkeypatch):
    """r1 F7: the instance PCA is applied whether or not files are written, so
    fold_data_sha256 equals the runner's identity hash."""
    import export_library_design as eld
    monkeypatch.setattr(ta, "INSTANCE_PCA", {"synthetic": 2})
    eld.main(["--synthetic", "60", "--dataset", "synthetic", "--out", str(tmp_path / "a.json")])
    eld.main(["--synthetic", "60", "--dataset", "synthetic", "--out", str(tmp_path / "b.json"),
              "--write-files", str(tmp_path / "f")])
    a, b = (json.load(open(tmp_path / n)) for n in ("a.json", "b.json"))
    assert [f["fold_data_sha256"] for f in a["folds"]] == [f["fold_data_sha256"] for f in b["folds"]]
    v, _ = rnl.synthetic_version(60, "canonical")
    s = ta.apply_instance_pca(v.splits[0], 2)
    assert a["folds"][0]["fold_data_sha256"] == lh.data_sha256(s, lh.split_universe(s))


@needs_java
@needs_octave
def test_retry_failed_after_decision(tmp_path):
    """r1 F8 / r2 F3: after an approved §6.7 decision a failed unit is re-run only
    if the text identifies exactly one DECISIONS.md row and that row names the
    unit; the old failure record is moved aside and the move is in the manifest."""
    bad = _fake_mimlnn(tmp_path, "  error('synthetic crash');")
    rc, root = _run(tmp_path, "--mimlnn-code", bad, methods="MIMLNN", folds=1)
    fails = glob.glob(str(root / "predictions" / "**" / "*.fail.json"), recursive=True)
    assert len(fails) == 10
    unit = "synthetic/original/MIMLNN/ratio0.4-lambda1"
    dec = tmp_path / "DECISIONS.md"
    dec.write_text("| date | decision | by |\n|---|---|---|\n"
                   "| 2026-10-14 | T03-RETRY-A approved: rerun synthetic/original/MIMLkNN/AveH-k5 | user |\n"
                   f"| 2026-10-14 | T03-RETRY-B approved: rerun {unit} with fixed code | user |\n"
                   "| 2026-10-14 | T03-OTHER unrelated | user |\n")
    good = tmp_path / "good"
    shutil.copytree(bad, good)
    (good / "MIMLNN.m").write_text((good / "MIMLNN.m").read_text().replace("error('synthetic crash');", ""))
    common = ["--recompute-selection", "--decisions-file", str(dec), "--mimlnn-code", str(good)]
    # not cited, and a non-unique substring ("T03" is in three rows): refused before anything runs
    for text, n in (("NOT-THERE", 0), ("T03", 3), ("approved", 2)):
        with pytest.raises(SystemExit, match=f"matches {n} table rows"):
            _run(tmp_path, *common, "--retry-failed", text, methods="MIMLNN", folds=1)
    # exactly one row, but it does not name this unit: nothing re-runs, refusal logged
    rc, _ = _run(tmp_path, *common, "--retry-failed", "T03-RETRY-A", methods="MIMLNN", folds=1)
    assert len(glob.glob(str(root / "predictions" / "**" / "*.fail.json"), recursive=True)) == 10
    last = [json.loads(l) for l in open(sorted(glob.glob(str(root / "manifests" / "*.jsonl")),
                                                key=os.path.getmtime)[-1])]
    assert sum(r["type"] == "retry_refused" for r in last) == 10
    assert not any(r["type"] == "retry" for r in last)
    # the valid case: one row, naming the unit
    rc, _ = _run(tmp_path, *common, "--retry-failed", "T03-RETRY-B", methods="MIMLNN", folds=1)
    assert rc == 0
    assert not glob.glob(str(root / "predictions" / "**" / "*.fail.json"), recursive=True)
    moved = glob.glob(str(root / "predictions" / "**" / "*.fail.*.json"), recursive=True)
    assert len(moved) == 10
    last = [json.loads(l) for l in open(sorted(glob.glob(str(root / "manifests" / "*.jsonl")),
                                                key=os.path.getmtime)[-1])]
    retries = [r for r in last if r["type"] == "retry"]
    assert len(retries) == 10 and all(unit in r["decision_row"] for r in retries)
    e = _results(root)["folds"]["r0_f0"]["selection"]["MIMLNN"]["AveragePrecision"]
    assert e["test"] is not None


def test_manifest_add_is_serialised(tmp_path):
    """r1 F10: concurrent manifest appends from worker threads stay whole lines."""
    r = rnl.Runner.__new__(rnl.Runner)
    r._mlock = threading.Lock()
    r.manifest = ta.Manifest(str(tmp_path), "x", {"t": 1})
    big = "y" * 20000
    ts = [threading.Thread(target=lambda i=i: [r.madd({"i": i, "j": j, "pad": big}) for j in range(50)])
          for i in range(8)]
    [t.start() for t in ts]
    [t.join() for t in ts]
    lines = open(r.manifest.path).read().splitlines()
    assert len(lines) == 1 + 400 and all(json.loads(l) for l in lines)


def test_results_writer_releases_lock_on_bad_json(tmp_path):
    """r1 F11: a corrupt results JSON does not leave the lock behind."""
    p = tmp_path / "x.json"
    p.write_text("{not json")
    with pytest.raises(json.JSONDecodeError):
        rnl.ResultsWriter(str(p))
    assert not os.path.exists(str(p) + ".lock")



# ------------------------------------------- KDIS non-determinism fallback
def _t03a(tmp_path, bad, dataset="synthetic60", status=None, build=None, name="T03-a.json"):
    p = tmp_path / name
    status = status or {}
    d = {"check": "T03-a", "dataset": dataset, "pass": not bad,
         "methods": {m: {"byte_identical": m not in bad, "status": status.get(m, ["ok", "ok"])}
                     for m in lh.KDIS_METHODS}}
    if build is not None:
        d["build"] = build
    p.write_text(json.dumps(d))
    return str(p)


def test_kdis_repeat_methods_from_t03a(tmp_path):
    """DECISIONS.md 2026-10-13: only methods T03-a found non-deterministic repeat."""
    m, rec = lh.kdis_repeat_methods(_t03a(tmp_path, {"MIMLBagging", "MIMLIBLR"}))
    assert m == ("MIMLBagging", "MIMLIBLR") and rec["t03a_sha256"]
    assert lh.kdis_repeat_methods(_t03a(tmp_path, set()))[0] == ()
    bad = tmp_path / "x.json"
    bad.write_text(json.dumps({"check": "T03-b", "methods": {}}))
    with pytest.raises(SystemExit, match="not a T03-a"):
        lh.kdis_repeat_methods(str(bad))


def test_mimlbagging_seed_and_tokens():
    """Repetition k changes only <seed> in MIMLBagging's shipped block. Every KDIS
    repetition, MIMLBagging included, is uncontrolled (rep-r<k>; DECISIONS.md
    "KDIS fallback labelling"); only MIMLNN carries seed-s<k>."""
    c = lh.Candidate("MIMLBagging", distance="AveH", k=10)
    base, s3 = lh.kdis_block(c).splitlines(), lh.kdis_block(c, 3).splitlines()
    diff = [(a, b) for a, b in zip(base, s3) if a != b]
    assert len(diff) == 1 and "<seed>1</seed>" in diff[0][0] and "<seed>3</seed>" in diff[0][1]
    k = lh.Candidate("MIMLkNN", distance="AveH", k=10)
    assert lh.kdis_block(k, 3) == lh.kdis_block(k)          # no seed exists to set
    assert lh.condition_token("main", 3, lh.repeat_kind(c)) == "rep-r3"     # MIMLBagging: uncontrolled
    assert lh.condition_token("main", 3, lh.repeat_kind(k)) == "rep-r3"
    assert lh.condition_token("control-s1", 2, lh.repeat_kind(k)) == "control-s1+rep-r2"
    assert lh.repeat_kind(lh.Candidate("MIMLNN", ratio=0.4, lam=1.0)) == "seed"


@needs_java
def test_kdis_repeat_harness_end_to_end(tmp_path):
    """Off by default; with a T03-a file, the flagged methods run 5 times per
    unit, metrics are averaged before selection, across-run SD is reported."""
    rc, root = _run(tmp_path, methods="MIMLkNN,MIMLBagging", folds=1)
    assert rc == 0
    assert not glob.glob(str(root / "predictions" / "**" / "rep-r*"), recursive=True)
    tmp2 = tmp_path / "second"
    tmp2.mkdir()
    rc, root2 = _run(tmp2, "--kdis-repeat-file", _t03a(tmp_path, {"MIMLkNN", "MIMLBagging"}),
                     methods="MIMLkNN,MIMLBagging", folds=1)
    assert rc == 0
    d = _results(root2)
    pred = root2 / "predictions" / "synthetic" / "original"
    for r in range(5):
        assert (pred / "MIMLkNN" / "AveH-k5" / f"rep-r{r}" / "r0_f0_i0.npz").exists()
        assert (pred / "MIMLBagging" / "AveH-k5" / f"rep-r{r}" / "r0_f0_i0.npz").exists()
        assert not (pred / "MIMLBagging" / "AveH-k5" / f"seed-s{r}").exists()
    side = json.load(open(pred / "MIMLBagging" / "AveH-k5" / "rep-r2" / "r0_f0_i0.json"))
    assert "<seed>2</seed>" in side["identity"]["classifier_block"]
    # DECISIONS.md "KDIS fallback labelling": MIMLBagging repeated => its <seed> did not
    # control it => uncontrolled, though <seed> is still varied (block_seed)
    assert side["identity"]["repetition"] == 2 and side["identity"]["uncontrolled"] is True
    assert side["identity"]["block_seed"] == 2
    side = json.load(open(pred / "MIMLkNN" / "AveH-k5" / "rep-r4" / "r0_f0_i0.json"))
    assert side["identity"]["uncontrolled"] is True
    f0 = d["folds"]["r0_f0"]
    # inner score = mean over the 5 runs, per inner fold (re-scored from stored units)
    v, _ = rnl.synthetic_version(60, "canonical")
    s = v.splits[0]
    inner = lh.inner_folds(s.ids_tr, 0, 0, 5)
    want = []
    for i, _, te in inner:
        Y = np.stack([s.Y[int(b)] for b in te])
        per = [lh.score(Y, *(lambda z: (z["scores"], z["bip"]))(np.load(
            pred / "MIMLBagging" / "AveH-k5" / f"rep-r{r}" / f"r0_f0_i{i}.npz")))["AveragePrecision"]
            for r in range(5)]
        want.append(np.mean(per))
    assert np.allclose(f0["inner_scores"]["MIMLBagging/AveH-k5"]["AveragePrecision"], want, atol=1e-12)
    sel = f0["selection"]["MIMLBagging"]["AveragePrecision"]["selected"]
    t = f0["refit_test"][f"MIMLBagging/{sel['config']}"]
    assert len(t["per_seed"]) == 5 and t["repetitions"] == "uncontrolled"
    # review r3 F1: outer test = mean over runs; across-run SD has ddof = 1
    # (MIMLBagging's runs differ, so both are detectable here)
    for m in lh.FIVE:
        vals = [p[m] for p in t["per_seed"]]
        assert t[m] == pytest.approx(np.mean(vals), abs=1e-15)
        assert t["across_run_sd"][m] == pytest.approx(np.std(vals, ddof=1), abs=1e-15)
    vals = [p["AveragePrecision"] for p in t["per_seed"]]
    assert np.std(vals) > 0 and t["AveragePrecision"] != vals[0]
    t = f0["refit_test"][f"MIMLkNN/{f0['selection']['MIMLkNN']['AveragePrecision']['selected']['config']}"]
    assert t["repetitions"] == "uncontrolled"
    # MIMLkNN is deterministic: its uncontrolled repetitions agree exactly
    assert t["across_run_sd"]["AveragePrecision"] == 0.0
    assert d["runs"][-1]["kdis_repeat"]["repeated_methods"] == ["MIMLBagging", "MIMLkNN"]


# ------------------------------------------------- deposit guard (T02 lens)
def test_guard_refuses_undeclared_mode(tmp_path):
    lh._RUN_MODE["synthetic"] = None
    with pytest.raises(SystemExit, match="not declared"):
        lh.guard_write(str(tmp_path / "x"))


def test_guard_synthetic_cannot_write_real_tree_case_and_symlink(tmp_path):
    """Synthetic runs never write into results/ or the evidence dir, however the
    path is spelled: different case (APFS), a symlink, or '..' segments."""
    real = os.path.join(lh.PROJECT, "results", "revision_r1", "predictions", "x.npz")
    variants = [real,
                real.replace("/results/", "/RESULTS/"),
                os.path.join(lh.PROJECT, "experiments", "..", "Results", "y"),
                os.path.join(lh.PROJECT, "revision_access_44676", "Evidence", "T03__checks", "z.json")]
    link = tmp_path / "lnk"
    os.symlink(os.path.join(lh.PROJECT, "results"), link)
    variants.append(str(link / "revision_r1" / "w"))
    for p in variants:
        with pytest.raises(SystemExit, match="real output tree"):
            lh.guard_write(p)
    lh.guard_write(str(tmp_path / "ok"))                      # a scratch path is fine
    # commonpath, not prefix: a sibling whose name starts with "results" is fine
    assert not lh.is_within(os.path.join(lh.PROJECT, "results_scratch"), os.path.join(lh.PROJECT, "results"))


def test_guard_cli_refuses_synthetic_into_real_root():
    """The runner's default --root is the real results tree: a synthetic run that
    forgets --root is refused before anything is created."""
    before = os.path.exists(os.path.join(lh.PROJECT, "results", "revision_r1", "library",
                                         "synthetic__original__main.json"))
    with pytest.raises(SystemExit, match="real output tree"):
        rnl.main(["--synthetic", "60", "--dataset", "synthetic", "--folds", "1", "--methods", "MIMLkNN"])
    assert os.path.exists(os.path.join(lh.PROJECT, "results", "revision_r1", "library",
                                       "synthetic__original__main.json")) == before
    with pytest.raises(SystemExit, match="real output tree"):
        t03_checks.main(["d", "--synthetic", "60"])           # default evidence dir is real


def test_guard_dataset_names_case_folded(monkeypatch):
    """A synthetic run may not borrow a real dataset name in any case; a real
    name without --synthetic needs the deposit; and in real mode every write
    needs the deposit."""
    for name in ("letter_frost", "Letter_Frost", "SCENE", "Corel5K", "VOC2012"):
        with pytest.raises(SystemExit, match="real dataset name"):
            lh.guard_dataset(name, synthetic=True)
    monkeypatch.setattr(lh, "deposit_recorded", lambda *a, **k: False)
    with pytest.raises(SystemExit, match="PENDING"):
        lh.guard_dataset("Scene", synthetic=False)
    with pytest.raises(SystemExit, match="PENDING"):
        rnl.load_version("letter_frost", "original", "main", None)    # read choke point
    lh.set_run_mode(False)
    with pytest.raises(SystemExit, match="not deposited"):
        lh.guard_write("/tmp/anything")



# ------------------------------------------- deposit guard = the shared rule
PINNED_TODAY = (2026, 10, 25)


@pytest.fixture
def pinned_today(monkeypatch):
    """deposit_check closes dates after the checking machine's UTC date (DECISIONS
    row 15); pin "today" through T04's injectable helper so the open case is stable."""
    import datetime
    import deposit_check
    monkeypatch.setattr(deposit_check, "_today", lambda: datetime.date(*PINNED_TODAY))


def _plan(tmp_path, value, line=8):
    lines = [f"| row {i} | x |" for i in range(1, line)] + [f"| Public timestamp | {value} |"]
    lines += [f"| row {i} | x |" for i in range(line + 1, 12)]
    p = tmp_path / "P.md"
    p.write_text("\n".join(lines) + "\n")
    return str(p)


@pytest.mark.parametrize("value,lifted", [
    ("https://doi.org/10.5281/zenodo.1234567 (2026-10-20)", True),          # the canonical form
    ("**PENDING (user action).** the URL/DOI is written here", False),
    ("pending", False), ("TBD", False), ("", False), ("to be filled", False),
    ("https://doi.org/10.5281/zenodo.1234567", False),                      # no date
    ("https://zenodo.org/records/1234567 (2026-10-20)", False),             # other host
    ("doi:10.5281/zenodo.1234567 (2026-10-20)", False),                     # not a URL
    ("https://doi.org/10.5281/zenodo.1234567 (2026-02-30)", False),         # not a real date
    ("https://doi.org/10.5281/zenodo.NNNNNNN (2026-10-20)", False),         # placeholder DOI
    ("**https://doi.org/10.5281/zenodo.1234567 (2026-10-20)**", False),     # bold
    ("https://doi.org/10.5281/zenodo.1234567 (2026-10-20) PENDING", False), # trailing text
    ("https://doi.org/10.5281/zenodo.1234567 (2026-10-26)", False),         # after (pinned) today
    ("https://doi.org/10.5281/zenodo.1234567 (2026-10-12)", False),         # before the earliest deposit
])
def test_deposit_guard_is_the_shared_rule(tmp_path, pinned_today, value, lifted):
    """T03 delegates to deposit_check.deposit_recorded; the wrapper and every
    T03 caller agree with it on every case."""
    import deposit_check
    p = _plan(tmp_path, value)
    assert deposit_check.deposit_recorded(p) is lifted
    assert lh.deposit_recorded(p) is lifted


def test_deposit_guard_line_8_and_missing_file(tmp_path, pinned_today):
    ok = "https://doi.org/10.5281/zenodo.1234567 (2026-10-20)"
    assert lh.deposit_recorded(_plan(tmp_path, ok, line=4)) is False      # row not on line 8
    assert lh.deposit_recorded(str(tmp_path / "missing.md")) is False
    assert lh.deposit_recorded(_plan(tmp_path, ok)) is True


def test_real_plan_records_the_deposit(monkeypatch):
    """review r4 note 4: judged with the REAL UTC clock, never with a pinned
    "today". Was test_real_plan_is_closed until the deposit (2026-10-13)."""
    import datetime
    monkeypatch.setattr(deposit_check, "_today", REAL_TODAY)
    assert deposit_check._today() == datetime.datetime.now(datetime.timezone.utc).date()
    # line 8 holds the deposit; the guard as a whole also needs every amendment
    # deposited (A1 review 1, finding 5), so it must agree with the shared check
    assert deposit_check.deposit_reference() == ("10.5281/zenodo.23341630", "2026-10-13")
    assert lh.deposit_recorded() is deposit_check.deposit_recorded()


def test_t03_callers_use_the_shared_check(tmp_path, monkeypatch):
    """The guard in every T03 entry point goes through deposit_check. Every
    output path is under tmp_path (A1 reviews 3-4: refusal tests are fail-safe)."""
    import deposit_check
    monkeypatch.setattr(deposit_check, "deposit_recorded", lambda *a, **k: False)
    with pytest.raises(SystemExit, match="PENDING"):
        lh.guard_dataset("scene", synthetic=False)
    with pytest.raises(SystemExit, match="not deposited"):
        t03_checks.main(["a", "--evidence-dir", str(tmp_path / "ev"), "--workdir", str(tmp_path / "w")])
    import export_library_design as eld
    with pytest.raises(SystemExit, match="not deposited"):
        eld.main(["--dataset", "scene", "--out", str(tmp_path / "never_written.json")])
    assert not any(f.is_file() for f in tmp_path.rglob("*"))
    monkeypatch.setattr(deposit_check, "deposit_recorded", lambda *a, **k: True)
    assert lh.deposit_recorded() is True


# ------------------------------------------- firmlink and Unicode aliases (T02 review 3)
@pytest.mark.skipif(not os.path.isdir("/System/Volumes/Data/Users"), reason="no APFS firmlink")
def test_guard_firmlink_alias_refused():
    real = os.path.join(lh.PROJECT, "results", "revision_r1", "predictions", "x.npz")
    alias = "/System/Volumes/Data" + real
    assert os.path.samefile(os.path.dirname(os.path.dirname(os.path.dirname(alias))),
                            os.path.join(lh.PROJECT, "results"))
    with pytest.raises(SystemExit, match="real output tree"):
        lh.guard_write(alias)
    assert lh.is_within(alias, os.path.join(lh.PROJECT, "results"))
    assert lh.is_within(os.path.join(lh.PROJECT, "results", "a"), "/System/Volumes/Data" + lh.PROJECT)


def test_guard_nfc_nfd_alias(tmp_path):
    """APFS is normalisation-insensitive: NFC and NFD spellings are one directory."""
    import unicodedata
    nfc, nfd = unicodedata.normalize("NFC", "café"), unicodedata.normalize("NFD", "café")
    assert nfc != nfd
    root = tmp_path / nfc
    root.mkdir()
    assert lh.is_within(str(tmp_path / nfd / "x"), str(root))
    assert lh.is_within(str(root / "y"), str(tmp_path / nfd))
    real = os.path.join(lh.PROJECT, "results")
    monkey_root = os.path.join(lh.PROJECT, unicodedata.normalize("NFD", "résults"))
    assert lh._canon(monkey_root) == lh._canon(os.path.join(lh.PROJECT, "résults"))
    assert not lh.is_within(monkey_root, real)      # a genuinely different name stays different



# ------------------------------------------- code review 2 (CODE-T03 r2)
def test_select_sd_is_ddof1():
    """r2 F2: inner SD uses ddof = 1 (§1.3 addendum)."""
    _, table, _ = lh.select({C("A", "AveH", 5): [0.0, 1.0, 0.5]}, "AveragePrecision")
    assert table[0]["inner_sd"] == pytest.approx(np.std([0.0, 1.0, 0.5], ddof=1), abs=1e-15)
    assert table[0]["inner_sd"] != pytest.approx(np.std([0.0, 1.0, 0.5], ddof=0))
    # and it is the SD that breaks a mean tie: ddof does not change the order here,
    # but the reported value must be the ddof=1 one
    _, table, by = lh.select({C("A", "AveH", 5): [0.25, 0.75], C("B", "AveH", 5): [0.5, 0.5]},
                             "AveragePrecision")
    assert by == "inner SD" and table[1]["inner_sd"] == pytest.approx(np.std([0.25, 0.75], ddof=1))


def test_pilot_passes_wall_guard(tmp_path, monkeypatch):
    """r2 F1: every pilot child runs with a wall guard (= pilot CPU limit x factor)."""
    seen = []

    def fake_kdis(cand, inputs, key, test_ids, workdir, xmx, cpu_limit_s, wall_guard_s=None, seed=None):
        seen.append((cpu_limit_s, wall_guard_s))
        return {"status": "ok", "cpu_s": 0.1, "wall_s": 0.1}, None, None

    def fake_mimlnn(cand, seed, inputs, tr, te, workdir, cpu_limit_s, wall_guard_s=None, codedir=None):
        seen.append((cpu_limit_s, wall_guard_s))
        return {"status": "ok", "cpu_s": 0.1, "wall_s": 0.1}, None, None
    monkeypatch.setattr(lh, "run_kdis_unit", fake_kdis)
    monkeypatch.setattr(lh, "run_mimlnn_unit", fake_mimlnn)
    rc = rnl.main(["--synthetic", "60", "--dataset", "synthetic", "--root", str(tmp_path / "root"),
                   "--workdir", str(tmp_path / "w"), "--methods", "MIMLkNN,MIMLNN", "--grid-k", "5",
                   "--grid-distances", "AveH", "--grid-mimlnn", "0.4:1", "--grid-seeds", "0",
                   "--pilot", "--pilot-cpu-limit", "50", "--wall-guard-factor", "3"])
    assert rc == 0 and len(seen) == 4            # (KDIS + MIMLNN) x (inner, refit)
    assert all(g == 150.0 for _, g in seen), seen



# ------------------------------------------------- code review 3 (CODE-T03 r3)
@needs_java
def test_partial_repetition_failure_excludes_candidate(tmp_path, monkeypatch):
    """r3 F1: a failure in ANY run (here only run 3 of inner fold 2) excludes the
    candidate for that outer fold."""
    real = lh.run_kdis_unit

    def flaky(cand, inputs, key, test_ids, workdir, xmx, cpu_limit_s, wall_guard_s=None, seed=None):
        if cand.method == "MIMLkNN" and cand.k == 5 and seed == 3 and key == "i2":
            return {"status": "crash", "cpu_s": 0.0, "wall_s": 0.0, "returncode": 1,
                    "log_tail": "synthetic crash"}, None, None
        return real(cand, inputs, key, test_ids, workdir, xmx, cpu_limit_s, wall_guard_s, seed)
    monkeypatch.setattr(lh, "run_kdis_unit", flaky)
    rc, root = _run(tmp_path, "--kdis-repeat-file", _t03a(tmp_path, {"MIMLkNN"}),
                    "--grid-distances", "AveH", methods="MIMLkNN", folds=1)
    assert rc == 0
    f0 = _results(root)["folds"]["r0_f0"]
    assert f0["excluded"] == {"MIMLkNN/AveH-k5": ["failed"]}
    assert "MIMLkNN/AveH-k5" not in f0["inner_scores"]
    assert f0["selection"]["MIMLkNN"]["AveragePrecision"]["selected"]["config"] == "AveH-k10"
    fails = glob.glob(str(root / "predictions" / "**" / "*.fail.json"), recursive=True)
    assert [os.path.relpath(p, root) for p in fails] == [
        "predictions/synthetic/original/MIMLkNN/AveH-k5/rep-r3/r0_f0_i2.fail.json"]


def _fake_units(monkeypatch, cpu=1.0):
    def fk(cand, inputs, key, test_ids, workdir, xmx, cpu_limit_s, wall_guard_s=None, seed=None):
        return {"status": "ok", "cpu_s": cpu, "wall_s": cpu}, None, None

    def fm(cand, seed, inputs, tr, te, workdir, cpu_limit_s, wall_guard_s=None, codedir=None):
        return {"status": "ok", "cpu_s": cpu, "wall_s": cpu}, None, None
    monkeypatch.setattr(lh, "run_kdis_unit", fk)
    monkeypatch.setattr(lh, "run_mimlnn_unit", fm)


PILOT_ARGS = ["--synthetic", "60", "--dataset", "synthetic", "--methods", "MIMLkNN,MIMLBagging,MIMLNN",
              "--grid-k", "5", "--grid-distances", "AveH", "--grid-mimlnn", "0.4:1", "--grid-seeds", "0",
              "--pilot"]


def test_pilot_records_repeat_set_and_scales_by_five(tmp_path, monkeypatch):
    """r3 F2: the pilot JSON records the repeat set; repeated methods get 5 keys
    per candidate (pilot_key tokens rep-r0..4) and a 5x refit bound and inner term."""
    _fake_units(monkeypatch)
    base = tmp_path / "base"
    rnl.main(PILOT_ARGS + ["--root", str(base), "--workdir", str(tmp_path / "w1")])
    rep = tmp_path / "rep"
    rnl.main(PILOT_ARGS + ["--root", str(rep), "--workdir", str(tmp_path / "w2"),
                           "--kdis-repeat-file", _t03a(tmp_path, {"MIMLkNN", "MIMLBagging"})])
    name = "pilots/library__synthetic__original__main.json"
    b, r = json.load(open(base / name)), json.load(open(rep / name))
    assert b["kdis_repeat"] is None
    assert r["kdis_repeat"]["repeated_methods"] == ["MIMLBagging", "MIMLkNN"]
    assert r["kdis_repeat"]["t03a_sha256"]
    for m in ("MIMLkNN", "MIMLBagging"):
        assert sorted(k for k in r["units"] if k.startswith(m + "/")) == \
            [f"{m}/AveH-k5/rep-r{i}" for i in range(5)]
        assert f"{m}/AveH-k5" in b["units"]
    assert "MIMLNN/ratio0.4-lambda1/seed-s0" in r["units"]
    pb, pr = b["projection_process_hours"], r["projection_process_hours"]
    for m in ("MIMLkNN", "MIMLBagging"):
        assert pr["refit_bound_per_outer_fold_s_by_method"][m] == \
            pytest.approx(5 * pb["refit_bound_per_outer_fold_s_by_method"][m])
    assert pr["refit_bound_per_outer_fold_s_by_method"]["MIMLNN"] == \
        pytest.approx(pb["refit_bound_per_outer_fold_s_by_method"]["MIMLNN"])
    # inner term: 2 repeated methods x5, MIMLNN x1 -> (5 + 5 + 1) / 3
    assert pr["inner"] == pytest.approx(pb["inner"] * 11 / 3)


def test_run_refuses_pilot_with_other_repeat_set(tmp_path, monkeypatch):
    """r3 F2: a production run refuses a pilot timed under a different repeat set,
    in both directions."""
    _fake_units(monkeypatch)
    rep = tmp_path / "rep"
    t03a = _t03a(tmp_path, {"MIMLkNN"})
    rnl.main(PILOT_ARGS + ["--root", str(rep), "--workdir", str(tmp_path / "w"), "--kdis-repeat-file", t03a])
    base = tmp_path / "base"
    rnl.main(PILOT_ARGS + ["--root", str(base), "--workdir", str(tmp_path / "w0")])
    name = "pilots/library__synthetic__original__main.json"
    run = ["--synthetic", "60", "--dataset", "synthetic", "--methods", "MIMLkNN", "--folds", "1",
           "--workdir", str(tmp_path / "w3"), "--grid-k", "5", "--grid-distances", "AveH"]
    with pytest.raises(SystemExit, match="re-run the pilot"):
        rnl.main(run + ["--root", str(tmp_path / "r1"), "--pilot-json", str(rep / name)])
    with pytest.raises(SystemExit, match="re-run the pilot"):
        rnl.main(run + ["--root", str(tmp_path / "r2"), "--pilot-json", str(base / name),
                        "--kdis-repeat-file", t03a])


@needs_java
def test_results_file_refuses_mixed_repeat_protocols(tmp_path):
    """r3 F3, the reviewer's demonstration: fold 0 without the repeat file, then
    fold 1 with it, on the same results file -> refused; --recompute-selection
    re-selects every fold under the new set."""
    args = ("--grid-distances", "AveH")
    rc, root = _run(tmp_path, *args, methods="MIMLkNN", folds=1)
    assert rc == 0 and _results(root)["meta"]["repeated_methods"] == []
    t03a = _t03a(tmp_path, {"MIMLkNN"})
    with pytest.raises(SystemExit, match=r"holds folds run with KDIS repeated methods \[\]"):
        _run(tmp_path, *args, "--kdis-repeat-file", t03a, methods="MIMLkNN", folds=2)
    d = _results(root)
    assert set(d["folds"]) == {"r0_f0"} and len(d["runs"]) == 1        # nothing was added
    rc, _ = _run(tmp_path, *args, "--kdis-repeat-file", t03a, "--recompute-selection",
                 methods="MIMLkNN", folds=2)
    assert rc == 0
    d = _results(root)
    assert d["meta"]["repeated_methods"] == ["MIMLkNN"]
    for k in ("r0_f0", "r0_f1"):
        t = d["folds"][k]["refit_test"]
        assert all(v.get("repetitions") == "uncontrolled" for v in t.values())
    # and the reverse direction
    with pytest.raises(SystemExit, match="holds folds run with KDIS repeated methods"):
        _run(tmp_path, *args, methods="MIMLkNN", folds=2)



# ------------------------------------------------- T03-a rules (a) and (b)
def test_t03a_crash_is_failed_check_not_nondeterminism(tmp_path):
    """Rule (b): a crash or timeout in either T03-a run refuses (stop rule);
    only two completed runs with differing predictions trigger the fallback."""
    for st in (["ok", "crash"], ["timeout", "ok"], ["wall-guard", "wall-guard"]):
        p = _t03a(tmp_path, {"MIMLIBLR"}, status={"MIMLIBLR": st}, name=f"x{st[0]}{st[1]}.json")
        with pytest.raises(SystemExit, match="stop rule"):
            lh.kdis_repeat_methods(p)
    # completed and differing -> repeated; completed and identical -> not
    assert lh.kdis_repeat_methods(_t03a(tmp_path, {"MIMLIBLR"}, name="ok.json"))[0] == ("MIMLIBLR",)
    # a crash in a method that was otherwise byte_identical=False is still refused
    p = _t03a(tmp_path, {"MIMLDGC"}, status={"MIMLDGC": ["crash", "crash"]}, name="cc.json")
    with pytest.raises(SystemExit, match="FAILED for \\['MIMLDGC'\\]"):
        lh.kdis_repeat_methods(p)
    # structurally incomplete files are refused
    bad = tmp_path / "inc.json"
    bad.write_text(json.dumps({"check": "T03-a", "methods": {"MIMLkNN": {"byte_identical": True}}}))
    with pytest.raises(SystemExit, match="7 KDIS methods"):
        lh.kdis_repeat_methods(str(bad))


def test_t03a_real_mode_integrity(tmp_path):
    """Rule (a) integrity: real mode accepts only the Letter Frost result produced
    by the PredictDump build in use."""
    good = lh.check_build()
    ok = _t03a(tmp_path, set(), dataset="letter_frost", build=good, name="lf.json")
    assert lh.kdis_repeat_methods(ok, real=True)[0] == ()
    with pytest.raises(SystemExit, match="Letter Frost"):
        lh.kdis_repeat_methods(_t03a(tmp_path, set(), dataset="synthetic60", build=good, name="s.json"),
                               real=True)
    stale = dict(good, sources_sha256={"PredictDump.java": "0" * 64, "MulanScore.java": "0" * 64})
    with pytest.raises(SystemExit, match="different PredictDump build"):
        lh.kdis_repeat_methods(_t03a(tmp_path, set(), dataset="letter_frost", build=stale, name="b.json"),
                               real=True)


def test_real_kdis_run_refused_without_t03a(tmp_path, monkeypatch):
    """Rule (a): a real-mode KDIS pilot or run refuses before reading any data if
    the Letter Frost T03-a result is missing or fails its integrity check."""
    def no_real_read(*a, **k):
        raise AssertionError("real data would have been read")
    monkeypatch.setattr(rnl, "load_version", no_real_read)
    monkeypatch.setattr(lh, "deposit_recorded", lambda *a, **k: True)
    monkeypatch.setattr(lh, "T03A_REAL", str(tmp_path / "missing" / "T03-a__letter_frost.json"))
    root = ["--root", str(tmp_path / "root"), "--workdir", str(tmp_path / "w")]
    for extra in ([], ["--pilot"]):
        with pytest.raises(SystemExit, match="T03-a result first"):
            rnl.main(["--dataset", "letter_frost", "--methods", "MIMLkNN"] + root + extra)
    crashed = _t03a(tmp_path, set(), dataset="letter_frost", build=lh.check_build(),
                    status={"MIMLBagging": ["ok", "crash"]}, name="lf_crash.json")
    with pytest.raises(SystemExit, match="stop rule"):
        rnl.main(["--dataset", "letter_frost", "--methods", "MIMLkNN", "--kdis-repeat-file", crashed] + root)
    # MIMLNN-only real runs do not need T03-a (it concerns KDIS only)
    with pytest.raises(AssertionError, match="real data would have been read"):
        rnl.main(["--dataset", "letter_frost", "--methods", "MIMLNN"] + root)



# ------------------------------------------------- code review 4 notes (v7)
@needs_java
@needs_octave
def test_successful_retry_releases_held_fold(tmp_path):
    """review r4 note 1: after an approved --retry-failed fixes a held refit, the
    fold is released (top-level held cleared, recorded in runs[]) and the run
    exits 0 without printing HELD."""
    bad = _fake_mimlnn(tmp_path, "  if numel(train_bags) > 50, error('refit crash'); end")
    rc, root = _run(tmp_path, "--mimlnn-code", bad, methods="MIMLNN", folds=1)
    assert rc == 3 and set(_results(root)["held"]) == {"r0_f0"}
    good = tmp_path / "good"
    shutil.copytree(bad, good)
    (good / "MIMLNN.m").write_text((good / "MIMLNN.m").read_text().replace(
        "if numel(train_bags) > 50, error('refit crash'); end", ""))
    dec = tmp_path / "DECISIONS.md"
    dec.write_text("| 2026-10-14 | T03-RETRY-REFIT: rerun synthetic/original/MIMLNN/ratio0.4-lambda1 | user |\n")
    rc, _ = _run(tmp_path, "--mimlnn-code", str(good), "--recompute-selection", "--retry-failed",
                 "T03-RETRY-REFIT", "--decisions-file", str(dec), methods="MIMLNN", folds=1)
    d = _results(root)
    assert rc == 0 and "held" not in d
    assert d["folds"]["r0_f0"]["selection"]["MIMLNN"]["AveragePrecision"]["test"] is not None
    assert "r0_f0" in d["runs"][-1]["released_holds"]


@needs_java
def test_completed_run_releases_pause(tmp_path):
    """review r4 note 1: a run paused at the unit cap, resumed with an approved
    larger cap and completed, no longer carries the top-level `paused`."""
    root = tmp_path / "root"
    path = root / "library" / "synthetic__original__main.json"
    path.parent.mkdir(parents=True)
    json.dump({"process_hours_used": 1.0 - 1e-7}, open(path, "w"))
    rc, _ = _run(tmp_path, "--unit-cap-hours", "1.0", "--jobs", "1", methods="MIMLkNN", folds=1)
    assert rc == 3 and "paused" in _results(root)
    rc, _ = _run(tmp_path, "--unit-cap-hours", "100", methods="MIMLkNN", folds=1)
    d = _results(root)
    assert rc == 0 and "paused" not in d and d["runs"][-1]["released_pause"]["reason"].startswith("unit cap")


def test_t03a_runs_have_a_wall_guard(tmp_path, monkeypatch):
    """review r4 note 3: every T03-a run carries a wall guard (4 x the CPU floor),
    so a CPU-idle hang fails the check instead of hanging it."""
    seen = []

    def fake(cand, inputs, key, test_ids, workdir, xmx, cpu_limit_s, wall_guard_s=None, seed=None):
        seen.append(wall_guard_s)
        return {"status": "wall-guard", "cpu_s": 0.0, "wall_s": 0.0, "log_tail": "hang"}, None, None
    monkeypatch.setattr(lh, "run_kdis_unit", fake)
    import argparse
    a, b = t03_checks.check_a_b(argparse.Namespace(synthetic=60, dataset="synthetic", k=10, xmx=2),
                                str(tmp_path / "w"))
    assert len(seen) == 14 and set(seen) == {t03_checks.T03A_WALL_GUARD_S}
    assert t03_checks.T03A_WALL_GUARD_S == 4 * rnl.CPU_FLOOR_S
    assert a["pass"] is False and all(r["status"] == ["wall-guard", "wall-guard"] for r in a["methods"].values())



def test_t03ce_mimlnn_runs_have_a_wall_guard(tmp_path, monkeypatch):
    """review 5: T03-c/e's MIMLNN runs (5 folds + seed-0 repeat + seed 1) carry the
    same 4 x CPU-floor wall guard as T03-a."""
    seen = []

    def fake(cand, seed, inputs, tr, te, workdir, cpu_limit_s, wall_guard_s=None, codedir=None):
        seen.append((cpu_limit_s, wall_guard_s))
        os.makedirs(workdir, exist_ok=True)
        L = 4
        sc = np.full((len(te), L), 0.1 * (seed + 1))
        np.savetxt(os.path.join(workdir, "unit.scores.csv"), sc, delimiter=",")
        np.savetxt(os.path.join(workdir, "unit.bip.csv"), np.zeros((len(te), L)), delimiter=",")
        rec = {"status": "ok", "cpu_s": 0.0, "native_measures": {m: 0.0 for m in lh.FIVE},
               "complex_outputs": 0, "max_abs_imag": 0.0, "flag_imag_above_1e-8": False}
        return rec, sc, np.zeros((len(te), L), dtype=np.uint8)
    monkeypatch.setattr(lh, "run_mimlnn_unit", fake)
    import argparse
    c, e = t03_checks.check_c_e(argparse.Namespace(synthetic=60, dataset="synthetic",
                                                   mimlnn_code=lh.MIMLNN_CODE), str(tmp_path / "w"))
    assert len(seen) == 7
    assert set(seen) == {(rnl.CPU_FLOOR_S, t03_checks.T03A_WALL_GUARD_S)}
    assert e["pass"] is True


# ------------------------------------- AMENDMENT.md A1 wiring (review A1-1 F11b)
def test_selection_uses_the_tie_neutral_rule(tmp_path, monkeypatch):
    """Two fake KDIS candidates. AveH-k5 outputs tied 0/1 scores: every relevant
    label is 1 and about half of the irrelevant labels are also 1. AveH-k10
    outputs continuous scores of intermediate quality. The deposited scorer
    (a tied pair is a full error) prefers k10 on RankingLoss; the A1 rule
    (half credit) prefers k5. The runner must follow A1, in selection and in
    the stored inner scores."""
    import tie_neutral_metrics as tn
    v, _ = rnl.synthetic_version(60, "canonical")
    Yall = v.splits[0].Y

    def fake(cand, inputs, key, test_ids, workdir, xmx, cpu_limit_s, wall_guard_s=None, seed=None):
        Y = np.stack([Yall[int(i)] for i in test_ids]).astype(float)
        ids = np.asarray(test_ids, dtype=np.int64)[:, None]
        lab = np.arange(Y.shape[1])[None, :]
        if cand.k == 5:
            s = np.where((Y > 0) | ((ids * 7 + lab * 3) % 2 == 0), 1.0, 0.0)
        else:
            u = ((ids * 2654435761 + lab * 40503) % 1000) / 1000.0
            s = 0.08 * Y + 0.5 * u
        rec = {"status": "ok", "cpu_s": 0.0, "wall_s": 0.0, "returncode": 0,
               "native_measures": {m: 0.0 for m in lh.FIVE}}
        return rec, s, (s > 0.5).astype(np.uint8)
    monkeypatch.setattr(lh, "run_kdis_unit", fake)
    rc, root = _run(tmp_path, "--grid-k", "5,10", "--grid-distances", "AveH",
                    methods="MIMLkNN", folds=1)
    assert rc == 0
    f0 = _results(root)["folds"]["r0_f0"]
    pred = root / "predictions" / "synthetic" / "original" / "MIMLkNN"
    s = v.splits[0]
    means = {}
    for cfg in ("AveH-k5", "AveH-k10"):
        neu, dep = [], []
        for i, _, te in lh.inner_folds(s.ids_tr, 0, 0, 5):
            Y = np.stack([Yall[int(b)] for b in te])
            z = np.load(pred / cfg / "main" / f"r0_f0_i{i}.npz")
            neu.append(tn.ranking_four(Y, z["scores"])["RankingLoss"])
            dep.append(lh.score_prereg(Y, z["scores"], z["bip"])["RankingLoss"])
        assert np.allclose(f0["inner_scores"][f"MIMLkNN/{cfg}"]["RankingLoss"], neu, atol=1e-12)
        means[cfg] = (np.mean(neu), np.mean(dep))
    assert means["AveH-k5"][0] < means["AveH-k10"][0]      # A1 prefers k5
    assert means["AveH-k5"][1] > means["AveH-k10"][1]      # the deposited rule would prefer k10
    assert f0["selection"]["MIMLkNN"]["RankingLoss"]["selected"]["config"] == "AveH-k5"
