#!/usr/bin/env python3
"""T03 harness checks a-g (PREREGISTERED.md §6.8; tolerances fixed there).

Each check writes one evidence JSON (no-overwrite) and prints PASS / FAIL /
REPORT. Results go to revision_access_44676/tasks/T03-baseline-harness-checks.md
(written by hand from these files after the run).

  a  KDIS determinism: 7 methods, AveH, k = 10, outer fold 0, run twice;
     predictions byte-identical.
  b  KDIS dump fidelity: for the same runs, miml_metrics.py on PredictDump
     output vs (i) Mulan's measures on the same outputs (in PredictDump) and
     (ii) the library's own run (RunAlgorithm + EvaluatorHoldout + BaseMIMLReport
     on per-fold ARFF); every |diff| > 1e-3 reported. Also: PredictDump's
     one-file subset mode == its two-file mode, byte for byte.
  c  MIMLNN scoring agreement: ratio 0.4, lambda 1, seed 0, the 5 outer folds
     of repeat 0; miml_metrics.py vs the authors' own five metrics.
  d  distance cache: not applicable unless caching is used (it is not).
  e  Octave seed control: MIMLNN seed 0 twice -> identical outputs.
  f  scorer agreement without a harness run: 1000 uniform score matrices
     (default_rng(3)) with the dataset's label matrix; miml_metrics.py vs Mulan
     (MulanScore.java) and vs the LAMDA .m functions; tolerance 1e-3 AP.
  g  same-device reproduction (logreg part): rerun the submitted
     run_foundation_baselines.py config with §6.1 pinning and compare per fold
     with the stored JSON (<= 1e-9, all five metrics). The TabPFN part is run
     by T04 (lead decision Q20) and is refused here.

Folds (lead decision Q11): a check that compares against a STORED submitted
number uses the submitted split (g: Scene canonical 10CV; Letter Frost would be
submitted5, which is what run_foundation_baselines.splits_for returns). All
other checks (a-f) use the §1.2 5 x 5 design, repeat 0: r0_f0 for a, b, e and
r0_f0..f4 for c.

Real data (Letter Frost, Scene) is refused until the plan is deposited; the
tests run every check on synthetic data.
"""
import os

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"

import argparse  # noqa: E402
import filecmp  # noqa: E402
import json  # noqa: E402
import shutil  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import tempfile  # noqa: E402

import numpy as np  # noqa: E402
from scipy.io import savemat  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import library_harness as lh  # noqa: E402
import run_nested_library as rnl  # noqa: E402
import tabpfn_arms as ta  # noqa: E402
from run_kdis_baselines import run_one as kdis_native_run  # noqa: E402

T03A_WALL_GUARD_S = 4 * rnl.CPU_FLOOR_S  # wall guard = 4 x the §6.6 CPU floor (Q16)
EVIDENCE = os.path.join(lh.PROJECT, "revision_access_44676", "evidence", "T03__checks")
TOL_REPORT = 1e-3


def _version(args):
    if args.synthetic is not None:
        v, _ = rnl.synthetic_version(args.synthetic, "repeated")
        return v
    v, _ = rnl.load_version(args.dataset, "original", "main", None)
    return v


def _all_Y(v):
    s = v.splits[0]
    ids = lh.split_universe(s)
    return ids, np.stack([s.Y[int(i)] for i in ids])


def _conventions(Y, scores):
    """Facts that explain expected convention differences (T03-b/c causes):
    bags with no label or every label (miml_metrics skips only the former in
    OneError/Coverage/AP; LAMDA skips both; Mulan skips neither in some
    measures) and tied scores (tie handling differs between scorers)."""
    Y = np.asarray(Y)
    ties = sum(len(np.unique(r)) < len(r) for r in np.asarray(scores))
    return {"n_bags": int(len(Y)), "n_no_label": int((Y.sum(1) == 0).sum()),
            "n_all_labels": int((Y.sum(1) == Y.shape[1]).sum()),
            "n_bags_with_tied_scores": int(ties)}


def _diffs(ours, theirs, label):
    out = {}
    for m in lh.FIVE:
        if theirs.get(m) is None:
            continue
        d = float(ours[m]) - float(theirs[m])
        out[m] = {"ours": float(ours[m]), label: float(theirs[m]), "diff": d,
                  "above_1e-3": abs(d) > TOL_REPORT}
    return out


def check_a_b(args, work):
    v = _version(args)
    split = v.splits[0]
    inputs = lh.export_split(split, os.path.join(work, "inputs"), "t03ab",
                             {"refit": (lh.refit_train_ids(split.ids_tr), split.ids_te)}, ("kdis",))
    tr_arff, te_arff = inputs.pairs["refit"]
    Yte = np.stack([split.Y[int(i)] for i in split.ids_te])
    a, b = {}, {}
    for m in lh.KDIS_METHODS:
        c = lh.Candidate(m, distance="AveH", k=args.k)
        recs = []
        for rep in (1, 2):
            wd = os.path.join(work, m, f"run{rep}")
            # review r4 note 3: a CPU-idle hang fails the check (wall-guard), §6.6/Q16
            rec, s, bip = lh.run_kdis_unit(c, inputs, "refit", split.ids_te, wd, args.xmx,
                                           rnl.CPU_FLOOR_S, T03A_WALL_GUARD_S)
            recs.append((wd, rec, s, bip))
        (wd1, r1, s1, b1), (wd2, r2, s2, b2) = recs
        ident = (r1["status"] == r2["status"] == "ok"
                 and filecmp.cmp(os.path.join(wd1, "unit.scores.csv"),
                                 os.path.join(wd2, "unit.scores.csv"), shallow=False)
                 and filecmp.cmp(os.path.join(wd1, "unit.bip.csv"),
                                 os.path.join(wd2, "unit.bip.csv"), shallow=False))
        a[m] = {"byte_identical": bool(ident), "status": [r1["status"], r2["status"]]}
        if r1["status"] != "ok":
            b[m] = {"status": r1["status"], "log": r1.get("log_tail")}
            continue
        ours = lh.score_prereg(Yte, s1, b1)
        # the library's own run (RunAlgorithm + EvaluatorHoldout + BaseMIMLReport)
        # on the very same ARFF pair
        native, err = kdis_native_run(m, lh.kdis_block(c), tr_arff, te_arff, inputs.xml,
                                      os.path.join(work, m, "native"))
        b[m] = {"miml_metrics": ours,
                "vs_mulan_inprocess": _diffs(ours, r1["native_measures"], "mulan_inprocess"),
                "vs_library_run": _diffs(ours, native, "library_run") if native else {"error": err},
                "conventions": _conventions(Yte, s1),
                "mulan_inprocess_equals_library_run": (
                    bool(native) and all(abs(r1["native_measures"][m_] - native[m_]) <= 1e-12
                                         for m_ in lh.FIVE))}
    return ({"check": "T03-a", "rule": "byte-identical predictions, run twice",
             "pass": all(x["byte_identical"] for x in a.values()), "methods": a},
            {"check": "T03-b", "rule": "report every |diff| > 1e-3 with its cause (documents, does not select)",
             "methods": b})


def check_c_e(args, work):
    v = _version(args)
    c = lh.Candidate("MIMLNN", ratio=0.4, lam=1.0)
    folds = [s for s in v.splits if s.repeat == 0][:5]
    per_fold, e = [], None
    # review 5: T03-c/e MIMLNN runs carry the same wall guard as T03-a
    for s in folds:
        inputs = lh.export_split(s, os.path.join(work, f"f{s.fold}", "inputs"), "t03c", {}, ("mimlnn",))
        Yte = np.stack([s.Y[int(i)] for i in s.ids_te])
        wd = os.path.join(work, f"f{s.fold}", "seed0")
        rec, sc, bip = lh.run_mimlnn_unit(c, 0, inputs, lh.refit_train_ids(s.ids_tr), s.ids_te, wd, rnl.CPU_FLOOR_S, T03A_WALL_GUARD_S,
                                          codedir=args.mimlnn_code)
        if rec["status"] != "ok":
            per_fold.append({"fold": s.fold, "status": rec["status"], "log": rec.get("log_tail")})
            continue
        ours = lh.score_prereg(Yte, sc, bip)
        per_fold.append({"fold": s.fold, "miml_metrics": ours,
                         "vs_authors": _diffs(ours, rec["native_measures"], "authors"),
                         "conventions": _conventions(Yte, sc),
                         "complex_outputs": rec["complex_outputs"],
                         "max_abs_imag": rec["max_abs_imag"],
                         "flag_imag_above_1e-8": rec["flag_imag_above_1e-8"]})
        if s.fold == 0:
            wd2 = os.path.join(work, "f0", "seed0_again")
            rec2, _, _ = lh.run_mimlnn_unit(c, 0, inputs, lh.refit_train_ids(s.ids_tr), s.ids_te, wd2, rnl.CPU_FLOOR_S, T03A_WALL_GUARD_S,
                                            codedir=args.mimlnn_code)
            wd3 = os.path.join(work, "f0", "seed1")
            rec3, _, _ = lh.run_mimlnn_unit(c, 1, inputs, lh.refit_train_ids(s.ids_tr), s.ids_te, wd3, rnl.CPU_FLOOR_S, T03A_WALL_GUARD_S,
                                            codedir=args.mimlnn_code)
            same = all(filecmp.cmp(os.path.join(wd, f"unit.{x}.csv"),
                                   os.path.join(wd2, f"unit.{x}.csv"), shallow=False)
                       for x in ("scores", "bip"))
            other = rec3["status"] == "ok" and not filecmp.cmp(
                os.path.join(wd, "unit.scores.csv"), os.path.join(wd3, "unit.scores.csv"), shallow=False)
            e = {"check": "T03-e", "rule": "the same seed twice gives identical outputs",
                 "pass": bool(same), "seed0_twice_identical": bool(same),
                 "seed1_differs_from_seed0 (informative only)": bool(other)}
    return ({"check": "T03-c", "rule": "report every |diff| > 1e-3 with its cause",
             "candidate": "ratio 0.4, lambda 1, seed 0", "folds": per_fold}, e)


def check_f(args, work, n_mat=1000):
    v = _version(args)
    _, Y = _all_Y(v)
    rng = np.random.default_rng(3)
    S = rng.uniform(size=(n_mat,) + Y.shape)
    ours = [lh.score_prereg(Y, S[j], (S[j] > 0.5).astype(np.uint8)) for j in range(n_mat)]
    # Mulan, called directly
    sdir = os.path.join(work, "scores")
    os.makedirs(sdir, exist_ok=True)
    truth = os.path.join(work, "truth.csv")
    np.savetxt(truth, Y, fmt="%d", delimiter=",")
    for j in range(n_mat):
        np.savetxt(os.path.join(sdir, f"{j:04d}.csv"), S[j], fmt="%.17g", delimiter=",")
    mout = os.path.join(work, "mulan.csv")
    subprocess.run(["java", "-XX:+UseSerialGC", "-Xmx2g", "-cp", f"{lh.JAR}{os.pathsep}{lh.KDIS_BUILD}",
                    "MulanScore", truth, sdir, mout], check=True, env=lh.child_env(),
                   capture_output=True)
    mulan = np.genfromtxt(mout, delimiter=",", names=True, dtype=None, encoding=None)
    # LAMDA .m functions, called directly
    mat = os.path.join(work, "lamda_in.mat")
    savemat(mat, {"target": np.where(Y > 0, 1.0, -1.0).T, "S": np.transpose(S, (1, 2, 0))})
    lout = os.path.join(work, "lamda.csv")
    subprocess.run(["octave", "--no-gui", "--norc", "--quiet", "--path", lh.LAMDA_DIR, "--eval",
                    f"t03f_lamda_score('{mat}','{os.path.join(args.mimlnn_code, 'Auxiliary')}','{lout}')"],
                   check=True, env=lh.child_env(), capture_output=True)
    lamda = np.loadtxt(lout, delimiter=",", skiprows=1, ndmin=2)
    ap_ours = np.array([o["AveragePrecision"] for o in ours])
    ap_mulan = np.asarray(mulan["AveragePrecision"], dtype=float)
    ap_lamda = lamda[:, 4]
    res = {"check": "T03-f", "rule": "|dAP| <= 1e-3 on every matrix", "n_matrices": n_mat,
           "label_matrix_shape": list(Y.shape),
           "bags_with_no_label": int((Y.sum(1) == 0).sum()),
           "bags_with_all_labels": int((Y.sum(1) == Y.shape[1]).sum())}
    for name, other, cols in (("mulan", None, None), ("lamda", lamda, None)):
        ap = ap_mulan if name == "mulan" else ap_lamda
        d = np.abs(ap_ours - ap)
        res[name] = {"max_abs_dAP": float(d.max()), "n_above_1e-3": int((d > 1e-3).sum()),
                     "pass": bool((d <= 1e-3).all())}
        for k, m in enumerate(lh.FIVE):
            o = np.array([x[m] for x in ours])
            t = np.asarray(mulan[m], dtype=float) if name == "mulan" else lamda[:, k]
            res[name][f"max_abs_d_{m}"] = float(np.abs(o - t).max())
    res["pass"] = res["mulan"]["pass"] and res["lamda"]["pass"]
    # Diagnostic, not the rule: LAMDA drops bags carrying every label; score
    # ours on the same bag subset to separate convention from arithmetic.
    keep = (Y.sum(1) > 0) & (Y.sum(1) < Y.shape[1])
    ap_cm = np.array([lh.score_prereg(Y[keep], S[j][keep], (S[j][keep] > 0.5).astype(np.uint8))
                      ["AveragePrecision"] for j in range(n_mat)])
    res["diagnostic_lamda_on_bags_with_some_but_not_all_labels"] = {
        "max_abs_dAP": float(np.abs(ap_cm - ap_lamda).max())}
    return res


def compare_to_stored(new, stored, tol, metrics):
    """Per-fold comparison of two run_foundation_baselines entries."""
    rows, ok = [], True
    if len(new["per_fold"]) != len(stored["per_fold"]):
        return False, [{"error": "fold count differs"}]
    for f, (a, b) in enumerate(zip(new["per_fold"], stored["per_fold"])):
        d = {m: abs(a[m] - b[m]) for m in metrics}
        bad = {m: x for m, x in d.items() if x > tol}
        ok &= not bad
        rows.append({"fold": f, "max_abs_diff": max(d.values()), "above_tol": bad})
    return ok, rows


def check_g(args, work):
    """Rerun the submitted config (unchanged code) with pinning; compare.
    Uses the submitted split by construction (Q11)."""
    if not args.g_config.startswith("logreg"):
        raise SystemExit("T03-g TabPFN part is run by T04 (lead decision Q20)")
    out = os.path.join(work, "rerun.json")
    py = args.python or sys.executable
    cmd = [py, os.path.join(lh.EXPERIMENTS, "run_foundation_baselines.py"), "--datasets",
           args.dataset, "--configs", args.g_config, "--out", out]
    if args.g_device:
        cmd += ["--device", args.g_device]
    subprocess.run(cmd, check=True, env=lh.child_env(), cwd=lh.PROJECT)
    new = json.load(open(out))[f"{args.dataset}/{args.g_config}"]
    stored = json.load(open(args.g_stored))[f"{args.dataset}/{args.g_config}"]
    tol = 1e-9 if args.g_config.startswith("logreg") else 1e-3
    metrics = lh.FIVE if tol == 1e-9 else ["AveragePrecision"]
    ok, rows = compare_to_stored(new, stored, tol, metrics)
    return {"check": "T03-g", "config": args.g_config, "dataset": args.dataset,
            "device": args.g_device or "cpu", "tolerance": tol, "metrics": metrics,
            "pass": ok, "per_fold": rows, "python": py}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("checks", help="comma list of a,b,c,d,e,f,g (a and b run together; c and e too)")
    ap.add_argument("--dataset", default="letter_frost")
    ap.add_argument("--synthetic", type=int, default=None)
    ap.add_argument("--k", type=int, default=10)
    ap.add_argument("--xmx", type=int, default=2)
    ap.add_argument("--n-matrices", type=int, default=1000)
    ap.add_argument("--mimlnn-code", default=lh.MIMLNN_CODE)
    ap.add_argument("--evidence-dir", default=EVIDENCE)
    ap.add_argument("--workdir", default=None)
    ap.add_argument("--g-config", default="logreg_bagmean")
    ap.add_argument("--g-device", default=None)
    ap.add_argument("--g-stored", default=os.path.join(lh.PROJECT, "results", "foundation_baselines.json"))
    ap.add_argument("--python", default=None, help="interpreter for g (tabpfn_env for the TabPFN part)")
    args = ap.parse_args(argv)
    lh.set_run_mode(args.synthetic is not None)
    if args.synthetic is None and not lh.deposit_recorded():
        raise SystemExit("plan or an amendment (AMENDMENT.md) not deposited: real-data checks refused (§6.0 step 0, §1.8)")
    lh.guard_dataset(args.dataset if args.synthetic is None else "synthetic", args.synthetic is not None)
    lh.guard_write(args.evidence_dir)
    build = lh.check_build()          # review r1 F3
    tag = f"synthetic{args.synthetic}" if args.synthetic is not None else args.dataset
    work = args.workdir or tempfile.mkdtemp(prefix="t03checks_")
    os.makedirs(args.evidence_dir, exist_ok=True)
    todo = set(args.checks.split(","))
    results = []
    if todo & {"a", "b"}:
        a, b = check_a_b(args, os.path.join(work, "ab"))
        results += [("a", a), ("b", b)]
    if todo & {"c", "e"}:
        c, e = check_c_e(args, os.path.join(work, "ce"))
        results += [("c", c), ("e", e)]
    if "d" in todo:
        results.append(("d", {"check": "T03-d", "status": "not applicable: no distance cache is used"}))
    if "f" in todo:
        results.append(("f", check_f(args, os.path.join(work, "f"), args.n_matrices)))
    if "g" in todo:
        results.append(("g", check_g(args, os.path.join(work, "g"))))
    for name, r in results:
        r["dataset"] = tag
        r["build"] = build
        path = os.path.join(args.evidence_dir, f"T03-{name}__{tag}.json")
        lh.guard_write(path)
        ta.save_json_noclobber(path, r)
        verdict = {True: "PASS", False: "FAIL"}.get(r.get("pass"), "REPORT")
        print(f"T03-{name} [{tag}]: {verdict} -> {path}", flush=True)
    if args.workdir is None:
        shutil.rmtree(work, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
