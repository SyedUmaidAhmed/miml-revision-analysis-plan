#!/usr/bin/env python3
"""Nested, validation-selected published library (KDIS + MIMLNN), task T03.

Binding spec: experiments/revision_r1/PREREGISTERED.md (tag prereg-v3-final),
§1.3, §1.5, §6.1-§6.6. One invocation = one (dataset, version, condition);
its results JSON has exactly one writer (lesson 9, enforced by a lock file).

Per outer fold (repeat r, fold f):
  1. export the fold's bags once (ARFF+XML for KDIS, .mat for Octave; VOC2012:
     instance PCA-128 fitted on the outer training fold, §1.4);
  2. inner phase: every candidate (84 KDIS + 9 MIMLNN x 5 seeds; §6.5 grid on
     VOC2012) on every inner fold; each unit's predictions stored under the
     §1.5 key `<dataset>/<version>/<method>/<config>/<condition>/r<r>_f<f>_i<i>.npz`;
  3. selection per metric, for the library (all 8 methods) and for each method
     alone, by mean inner score with the §1.3 tie-break; a candidate that
     failed in any inner unit is excluded for that outer fold;
  4. refit phase: each selected candidate on 100 % of the outer training fold,
     evaluated once on the outer test fold (`r<r>_f<f>.npz`);
  5. per-fold record: selected candidate per (procedure, metric), its inner
     mean/SD, the deciding tie-break level, exclusions, test metrics (MIMLNN:
     mean over seeds), CPU time, RSS, load average, concurrency.

Every score is computed from stored predictions (Hamming: miml_metrics.py;
ranking metrics: tie-neutral, AMENDMENT.md A1); library-native scores
are kept beside each unit as a check (§1.5).

Real datasets are refused until the plan's Public-timestamp row is filled.

Examples (synthetic only before deposit):
  ./.venv/bin/python experiments/revision_r1/run_nested_library.py \
      --synthetic 60 --dataset synthetic --version original --folds 2 \
      --root $TMPDIR/libtest --methods MIMLkNN,MIMLNN
"""
import os

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"

import argparse  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import shutil  # noqa: E402
import socket  # noqa: E402
import sys  # noqa: E402
import threading  # noqa: E402
import time  # noqa: E402
import uuid  # noqa: E402
from concurrent.futures import ThreadPoolExecutor  # noqa: E402

import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import library_harness as lh  # noqa: E402
import tabpfn_arms as ta  # noqa: E402

DEFAULT_ROOT = os.path.join(lh.PROJECT, "results", "revision_r1")
CPU_FLOOR_S = 7200            # §6.6: max(7200 s, 3 x its pilot)


class UnitCapReached(RuntimeError):
    pass


# --------------------------------------------------------------------------
# Dataset versions
# --------------------------------------------------------------------------
def synthetic_version(n_bags, design, seed=0, L=4, d=3):
    """Synthetic stand-in. `canonical` mimics get_cv_splits (10 contiguous
    blocks of floor(n/10) of a fixed permutation; remainder always in training);
    `repeated` is the §1.2 5 x 5 design."""
    bags, Y = ta.make_synthetic(n_bags=n_bags, d=d, L=L, seed=seed)
    if design == "repeated":
        triples = ta.repeated_splits(n_bags, 5, ta.PRIMARY_SEEDS)
    else:
        perm = np.random.default_rng(99).permutation(n_bags)
        fs = n_bags // 10
        triples = [(0, f, np.concatenate([perm[:f * fs], perm[(f + 1) * fs:]]),
                    perm[f * fs:(f + 1) * fs]) for f in range(10)]
    sizes = np.array([len(b) for b in bags])
    v = ta.Version("synthetic", "original", f"synthetic {design}",
                   ta._plain_splits(bags, Y, triples), Y.shape[1], d,
                   bool((sizes == sizes[0]).all()))
    canonical = [(tr, te) for _, _, tr, te in triples] if design != "repeated" else None
    return v, canonical


def load_version(dataset, version, condition, constructions_root):
    """Real data: the same loaders, with the same arguments, as the TabPFN arms
    (run_tabpfn_arms.build_version), so both arms see identical bags and folds.
    Rebuilt bags come back as float32 like every other version (§1.4 addendum)
    and are then written losslessly."""
    lh.guard_dataset(dataset, synthetic=False)        # choke point for reading real data
    bags, Y, cfg, ds = ta.load_original(dataset)
    groups = None
    if version in ("original", "rcv10", "submitted5"):
        v = ta.splits_from_bags(dataset, version, bags, Y, cfg=cfg, ds=ds)
    elif version == "rebuilt":
        import h2_common as hc           # T02: raw source rows by the identity mapping
        src_bags, _ = hc.load_constructed(hc.dataset_paths(dataset)[0])
        v = ta.load_rebuilt(dataset, hc.source_rows(src_bags), root=constructions_root)
        groups = lh.pool_groups(ta.rfb.splits_for(ds, cfg, None))   # H2-A step 5 pools
    elif version == "purged":
        v = ta.load_purged(dataset, condition, bags, Y, cfg, ds, root=constructions_root)
    else:
        raise SystemExit(f"version {version!r}: not a library run (dedup rescoring "
                         "uses stored predictions, H1)")
    return v, groups


# --------------------------------------------------------------------------
# Store
# --------------------------------------------------------------------------
def unit_stem(root, dataset, version, cand, cond, repeat, fold, inner=None):
    d = os.path.join(root, "predictions", dataset, version, cand.method, cand.config, cond)
    s = f"r{repeat}_f{fold}" + (f"_i{inner}" if inner is not None else "")
    return os.path.join(d, s)


def _sha_ids(ids):
    return hashlib.sha256(",".join(str(int(i)) for i in ids).encode()).hexdigest()


class ResultsWriter:
    """The run's one results JSON. A lock file refuses a second writer."""

    def __init__(self, path):
        self.path, self.lock = path, path + ".lock"
        lh.guard_write(path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        try:
            fd = os.open(self.lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
        except FileExistsError:
            raise SystemExit(f"{self.lock} exists: another writer owns {path} "
                             "(lesson 9). Remove it only if that process is dead.")
        os.write(fd, json.dumps({"pid": os.getpid(), "host": socket.gethostname(),
                                 "start": time.time()}).encode())
        os.close(fd)
        try:
            self.data = json.load(open(path)) if os.path.exists(path) else {}
        except Exception:
            os.unlink(self.lock)     # review r1 F11: never leave our lock behind
            raise

    def save(self):
        tmp = self.path + f".tmp.{os.getpid()}"
        with open(tmp, "w") as fh:
            json.dump(self.data, fh, indent=1, sort_keys=True, default=ta._json_default)
        os.replace(tmp, self.path)

    def close(self):
        if os.path.exists(self.lock):
            os.unlink(self.lock)


# --------------------------------------------------------------------------
# Runner
# --------------------------------------------------------------------------
class Runner:
    def __init__(self, args, version, groups, grid):
        self.a, self.v, self.groups, self.grid = args, version, groups, grid
        self.dataset, self.vname = args.dataset, args.version
        self.base_cond = args.condition
        self.xmx = args.xmx or lh.default_xmx_gib(self.dataset)
        self.n_jobs = args.jobs or lh.concurrency(self.xmx)
        self.budget = lh.MemoryBudget(16, self.n_jobs)
        self.pilot = json.load(open(args.pilot_json)) if args.pilot_json else None
        self.run_id = f"{ta.new_run_id()}_{uuid.uuid4().hex[:8]}"   # unique within a process
        self._mlock = threading.Lock()
        self.prior_s, self.used_s, self.stop_flag = 0.0, 0.0, False
        self.cap_hours, self.cap_source = resolve_unit_cap(args, self.pilot)
        self.kdis_repeat, self.kdis_repeat_record = (), None
        if args.kdis_repeat_file:                    # default off; per method from T03-a
            self.kdis_repeat, self.kdis_repeat_record = lh.kdis_repeat_methods(
                args.kdis_repeat_file, real=args.synthetic is None)
        # review r3 F2: the pilot must have been timed under the same repeat set
        if self.pilot is not None and not args.pilot:
            pr = self.pilot.get("kdis_repeat")
            pilot_set = tuple(pr["repeated_methods"]) if pr else ()
            if pilot_set != tuple(self.kdis_repeat):
                raise SystemExit(f"pilot {args.pilot_json} was timed with KDIS repeated methods "
                                 f"{list(pilot_set)}, this run has {list(self.kdis_repeat)}: "
                                 "re-run the pilot with the same --kdis-repeat-file (§6.3)")
        self.code_sha = {os.path.basename(p): ta.sha256_file(p) for p in (
            os.path.abspath(__file__), lh.__file__, ta.__file__,
            os.path.join(lh.EXPERIMENTS, "kdis", "PredictDump.java"),
            os.path.join(lh.LAMDA_DIR, "run_mimlnn.m"),
            os.path.join(lh.LAMDA_DIR, "concur.m"),
            os.path.join(lh.SEED_SHIM, "clock.m"))}

    # ---- manifest (review r1 F10: worker threads append; serialise) -----------
    def madd(self, rec):
        with self._mlock:
            self.manifest.add(rec)

    # ---- limits ---------------------------------------------------------
    def cpu_limit(self, cand, seed, kind):
        if self.a.cpu_limit is not None:
            return self.a.cpu_limit
        if self.pilot:
            key = pilot_key(cand, seed)
            p = self.pilot.get("units", {}).get(key, {}).get(kind, {}).get("cpu_s")
            if p is not None:
                return max(CPU_FLOOR_S, 3.0 * p)
        return CPU_FLOOR_S

    # ---- one unit (with the §6.6 retry rule) ------------------------------
    def _execute(self, cand, seed, inputs, tr, te, inner, workdir, kind):
        limit = self.cpu_limit(cand, seed, kind)
        guard = limit * self.a.wall_guard_factor
        attempts, xmx = [], self.xmx
        for attempt in (1, 2):
            wd = os.path.join(workdir, f"a{attempt}")
            reserve = xmx if not cand.is_mimlnn else 16 // 8
            with self.budget(reserve):
                if cand.is_mimlnn:
                    rec, s, b = lh.run_mimlnn_unit(cand, seed, inputs, tr, te, wd, limit, guard,
                                                   codedir=self.a.mimlnn_code)
                else:
                    rec, s, b = lh.run_kdis_unit(cand, inputs, lh.pair_key(inner), te, wd,
                                                 xmx, limit, guard, seed=seed)
            attempts.append(rec)
            if rec["status"] == "ok" or rec["status"] in ("timeout", "wall-guard"):
                break
            if rec["status"] == "oom":
                xmx *= 2          # §6.1: retry with doubled Xmx (reserves double)
        rec = dict(attempts[-1])
        rec["attempts"] = [{k: a[k] for k in ("status", "cpu_s", "wall_s", "returncode")}
                           | ({"xmx_gib": a["xmx_gib"]} if "xmx_gib" in a else {})
                           for a in attempts]
        rec["cpu_s_all_attempts"] = float(sum(a["cpu_s"] for a in attempts))
        if not self.a.keep_workdirs and rec["status"] == "ok":
            shutil.rmtree(workdir, ignore_errors=True)
        return rec, (s if rec["status"] == "ok" else None), (b if rec["status"] == "ok" else None)

    def unit(self, split, inputs, cand, seed, inner, tr, te, workroot):
        """Run or reuse one unit. Returns (status, metrics or None, record)."""
        cond = lh.condition_token(self.base_cond, seed, lh.repeat_kind(cand))
        stem = unit_stem(self.a.root, self.dataset, self.vname, cand, cond,
                         split.repeat, split.fold, inner)
        npz, side, fail = stem + ".npz", stem + ".json", stem + ".fail.json"
        ident = {"dataset": self.dataset, "version": self.vname, "arm": cand.method,
                 "config": cand.config, "condition": cond, "repeat": split.repeat,
                 "fold": split.fold, "inner": inner, "train_ids_sha256": _sha_ids(tr),
                 "test_ids_sha256": _sha_ids(te),
                 "fold_data_sha256": inputs.data_sha256}
        if cand.is_mimlnn:
            ident.update(mimlnn_sha256=lh.MIMLNN_SHA256, ratio=cand.ratio, lam=cand.lam, seed=seed)
        else:
            ident.update(jar_sha256=lh.JAR_SHA256, classifier_block=lh.kdis_block(cand, seed))
            if seed is not None:          # KDIS non-determinism fallback
                ident.update(repetition=seed, uncontrolled=lh.repeat_kind(cand) == "rep",
                             block_seed=seed if cand.method in lh.KDIS_SEEDED else None)
        Yte = np.stack([split.Y[int(i)] for i in te])
        for p in (side, fail):
            if os.path.exists(p):
                old = json.load(open(p))
                if old["identity"] != ident:
                    raise RuntimeError(f"{p}: stored unit has a different identity; refusing to reuse")
        lh.guard_write(stem)                    # writer choke point for every unit file
        if os.path.exists(fail):
            if not self.a.retry_failed:
                return "failed", None, json.load(open(fail))["record"]
            # review r2 F3: the one decision row must name this unit
            # (<dataset>/<version>/<method>/<config>, or the full key below it)
            unit_path = f"{self.dataset}/{self.vname}/{cand.method}/{cand.config}"
            if unit_path not in self.retry_row:
                self.madd({"type": "retry_refused", "path": fail, "unit": unit_path,
                           "decision": self.a.retry_failed,
                           "reason": "the decision row does not name this unit"})
                return "failed", None, json.load(open(fail))["record"]
            # review r1 F8: an approved §6.7 decision re-runs a failed unit; the
            # failure record is moved aside (never deleted) and the move logged
            moved = stem + f".fail.{self.run_id}.json"
            os.link(fail, moved)
            os.unlink(fail)
            self.madd({"type": "retry", "path": fail, "moved_to": moved,
                       "decision": self.a.retry_failed, "decision_row": self.retry_row})
        if os.path.exists(npz):
            if not os.path.exists(side):
                raise RuntimeError(f"{npz} exists without its sidecar: incomplete unit")
            z = np.load(npz)
            if not np.array_equal(z["test_idx"], np.asarray(te, dtype=np.int64)):
                raise RuntimeError(f"{npz}: test ids differ from this design")
            self.madd({"type": "reuse", "path": npz, "sha256": json.load(open(side))["npz_sha256"]})
            return "reused", lh.score(Yte, z["scores"], z["bip"]), json.load(open(side))["record"]
        if self.stop_flag:
            return "not-run", None, None
        wd = os.path.join(workroot, "units", cand.method, cand.config, cond,
                          f"i{inner}" if inner is not None else "refit")
        rec, s, b = self._execute(cand, seed, inputs, tr, te, inner, wd,
                                  "inner" if inner is not None else "refit")
        rec["input_files_sha256"] = (
            {"bags.mat": inputs.sha256["bags.mat"]} if cand.is_mimlnn else
            {os.path.basename(p): inputs.sha256[os.path.basename(p)]
             for p in inputs.pairs[lh.pair_key(inner)]})
        self.charge(rec["cpu_s_all_attempts"])
        # §6.1: a timed run whose 1-minute load average exceeded 10 is re-timed
        rec["load_over_10"] = max(rec.get("load1_start", 0), rec.get("load1_end", 0)) > 10
        if rec["status"] != "ok":
            ta.save_json_noclobber(fail, {"identity": ident, "record": rec})
            self.madd({"type": "fail", "path": fail, "status": rec["status"]})
            return "failed", None, rec
        if b is None:
            raise RuntimeError(f"{cand.method}: no native bipartition; §1.3 assumes one")
        # §1.3 F4 (addendum): degenerate labels overwritten before scoring;
        # the library's raw output is stored beside the scored matrices.
        deg = lh.degenerate_labels(np.stack([split.Y[int(i)] for i in tr]))
        neg = lh.NEGATIVE_SCORE["mimlnn" if cand.is_mimlnn else "kdis"]
        s_used, b_used = lh.apply_degenerate(s, b, deg, neg)
        sha = ta.save_npz_noclobber(npz, test_idx=np.asarray(te, dtype=np.int64),
                                    scores=s_used, bip=b_used,
                                    scores_raw=np.asarray(s, dtype=np.float64),
                                    bip_raw=np.asarray(b, dtype=np.uint8),
                                    degenerate_labels=deg,
                                    negative_score=np.float64(neg))
        rec["degenerate_labels_in_train"] = deg.tolist()
        ta.save_json_noclobber(side, {"identity": ident, "record": rec, "npz_sha256": sha,
                                      "run_id": self.run_id})
        self.madd({"type": "write", "path": npz, "sha256": sha, "json": side})
        return "ok", lh.score(Yte, s_used, b_used), rec

    # ---- budget ---------------------------------------------------------
    def charge(self, cpu_s):
        with lh._ACTIVE_LOCK:
            self.used_s += cpu_s
            # review r1 F2: hours used by earlier runs of this unit count too
            if self.cap_hours and (self.prior_s + self.used_s) / 3600 > self.cap_hours:
                self.stop_flag = True

    # ---- one outer fold -------------------------------------------------
    def seeds_of(self, cand):
        if cand.is_mimlnn:
            return self.grid.mimlnn_seeds
        if cand.method in self.kdis_repeat:          # KDIS non-determinism fallback
            return lh.KDIS_REPEATS
        return (None,)

    def run_split(self, split, pool):
        key = f"r{split.repeat}_f{split.fold}"
        if self.vname != "rebuilt" and self.dataset in ta.INSTANCE_PCA:
            split = ta.apply_instance_pca(split, ta.INSTANCE_PCA[self.dataset])
        workroot = os.path.join(self.a.workdir, self.dataset, self.vname, self.base_cond, key)
        need = tuple(n for n, has in (("kdis", any(not c.is_mimlnn for c in self.grid.candidates)),
                                      ("mimlnn", any(c.is_mimlnn for c in self.grid.candidates))) if has)
        inner = lh.inner_folds(split.ids_tr, split.repeat, split.fold, self.grid.inner_k, self.groups)
        pairs = {lh.pair_key(i): (tr_i, te_i) for i, tr_i, te_i in inner}
        refit_tr = lh.refit_train_ids(split.ids_tr)          # ascending canonical index
        pairs["refit"] = (refit_tr, split.ids_te)
        inputs = lh.export_split(split, os.path.join(workroot, "inputs"), f"{self.dataset}_{key}",
                                 pairs, need)

        # inner phase
        jobs = {}
        for cand in self.grid.candidates:
            for seed in self.seeds_of(cand):
                for i, tr_i, te_i in inner:
                    jobs[(cand, seed, i)] = pool.submit(self.unit, split, inputs, cand, seed,
                                                        i, tr_i, te_i, workroot)
        res = {k: f.result() for k, f in jobs.items()}

        inner_scores, excluded, unit_log = {}, {}, {}
        for cand in self.grid.candidates:
            stats = [res[(cand, s, i)] for s in self.seeds_of(cand) for i, _, _ in inner]
            bad = [st for st, _, _ in stats if st not in ("ok", "reused")]
            ck = f"{cand.method}/{cand.config}"
            unit_log[ck] = {"inner_cpu_s": float(sum((r or {}).get("cpu_s_all_attempts", 0.0)
                                                     for st, _, r in stats if st == "ok")),
                            "inner_peak_rss_bytes": max([(r or {}).get("peak_rss_bytes", 0)
                                                         for _, _, r in stats] or [0]),
                            "inner_runs_load_over_10": sum(bool((r or {}).get("load_over_10"))
                                                           for st, _, r in stats if st == "ok"),
                            "statuses": sorted(set(st for st, _, _ in stats)),
                            "units_imag_above_1e-8": sum(bool((r or {}).get("flag_imag_above_1e-8"))
                                                         for _, _, r in stats)}  # Q19
            if bad:
                excluded[ck] = sorted(set(bad))
                continue
            per_fold = {m: [] for m in lh.FIVE}
            for i, _, _ in inner:
                for m in lh.FIVE:
                    per_fold[m].append(float(np.mean([res[(cand, s, i)][1][m]
                                                      for s in self.seeds_of(cand)])))
            inner_scores[cand] = per_fold
        if self.stop_flag:
            raise UnitCapReached(key)

        procedures = {"library": [c for c in self.grid.candidates]}
        for m in lh.LIBRARY_METHODS:
            cs = [c for c in self.grid.candidates if c.method == m]
            if cs:
                procedures[m] = cs
        selection, winners = {}, set()
        for proc, cands in procedures.items():
            selection[proc] = {}
            for metric in lh.FIVE:
                sc = {c: (inner_scores[c][metric] if c in inner_scores else None) for c in cands}
                win, table, decided = lh.select(sc, metric)
                entry = {"n_candidates": len(cands), "n_eligible": len(table), "decided_by": decided}
                if win is not None:
                    entry.update(selected={"method": win.method, "config": win.config},
                                 inner_mean=table[0]["inner_mean"], inner_sd=table[0]["inner_sd"])
                    winners.add(win)
                selection[proc][metric] = entry

        # refit phase
        refit_set = set(self.grid.candidates) if self.a.refit == "all" else winners
        Yte = np.stack([split.Y[int(i)] for i in split.ids_te])
        jobs = {(c, s): pool.submit(self.unit, split, inputs, c, s, None,
                                    refit_tr, split.ids_te, workroot)
                for c in refit_set for s in self.seeds_of(c)}
        rres = {k: f.result() for k, f in jobs.items()}
        if self.stop_flag:
            raise UnitCapReached(key)
        test, held = {}, []
        for c in refit_set:
            st = [rres[(c, s)] for s in self.seeds_of(c)]
            ck = f"{c.method}/{c.config}"
            unit_log.setdefault(ck, {})["refit_cpu_s"] = float(sum(
                (r or {}).get("cpu_s_all_attempts", 0.0) for s_, _, r in st if s_ == "ok"))
            if any(s_ not in ("ok", "reused") for s_, _, _ in st):
                test[ck] = {"failed": sorted(set(s_ for s_, _, _ in st))}
                continue
            per_seed = [m for _, m, _ in st]
            test[ck] = {m: float(np.mean([p[m] for p in per_seed])) for m in lh.FIVE}
            if len(per_seed) > 1:          # MIMLNN seeds, or KDIS fallback repetitions
                test[ck]["per_seed"] = per_seed
                test[ck]["across_run_sd"] = {m: float(np.std([p[m] for p in per_seed], ddof=1))
                                             for m in lh.FIVE}
                test[ck]["repetitions"] = ("uncontrolled" if lh.repeat_kind(c) == "rep"
                                           else "seeded")
        for proc in selection:
            for metric, entry in selection[proc].items():
                if "selected" not in entry:
                    entry["test"] = None
                    continue
                ck = f"{entry['selected']['method']}/{entry['selected']['config']}"
                t = test[ck]
                if "failed" in t:
                    # §1.3 addendum: recorded failed, routed through the §6.7
                    # stop rule; no fallback to the runner-up
                    entry["test"] = None
                    entry["refit_failed"] = t["failed"]
                    held.append({"procedure": proc, "metric": metric, "candidate": ck,
                                 "status": t["failed"]})
                else:
                    entry["test"] = t[metric]
                    entry["test_all_five"] = {m: t[m] for m in lh.FIVE}
        if not self.a.keep_inputs:
            shutil.rmtree(os.path.join(workroot, "inputs"), ignore_errors=True)
        return key, {"repeat": split.repeat, "fold": split.fold,
                     "n_train": int(len(split.ids_tr)), "n_test": int(len(split.ids_te)),
                     "test_ids_sha256": _sha_ids(split.ids_te),
                     "inner_sizes": [int(len(te_i)) for _, _, te_i in inner],
                     "inputs_sha256": inputs.sha256, "excluded": excluded,
                     "inner_scores": {f"{c.method}/{c.config}": v for c, v in inner_scores.items()},
                     "selection": selection, "refit_test": test, "units": unit_log,
                     "held_refit_failures": held,
                     "Y_test_label_counts": Yte.sum(0).tolist()}

    # ---- whole version --------------------------------------------------
    def run(self, writer):
        d = writer.data
        # review r3 F3: one results JSON holds one repeat protocol
        repeated = sorted(self.kdis_repeat)
        stored = d.get("meta", {}).get("repeated_methods")
        if d.get("folds") and stored is not None and stored != repeated \
                and not self.a.recompute_selection:
            raise SystemExit(f"{writer.path} holds folds run with KDIS repeated methods {stored}; "
                             f"this run has {repeated}. Use --recompute-selection to re-select "
                             "every fold from stored units under the new set, or a new results file.")
        if d.get("folds") and stored is None and repeated and not self.a.recompute_selection:
            raise SystemExit(f"{writer.path} holds folds run without the KDIS repeat protocol; "
                             f"this run repeats {repeated} (use --recompute-selection)")
        lh.guard_write(os.path.join(self.a.root, "manifests"))
        self.manifest = ta.Manifest(self.a.root, self.run_id, {
            "arm": "library", "dataset": self.dataset, "version": self.vname,
            "condition": self.base_cond, "code_sha256": self.code_sha})
        self.stop_flag, self.used_s = False, 0.0
        d = writer.data
        self.prior_s = 3600.0 * float(d.get("process_hours_used", 0.0))
        d.setdefault("folds", {})
        d.setdefault("runs", []).append({
            "run_id": self.run_id, "start": time.time(), "xmx_gib": self.xmx,
            "jobs": self.n_jobs, "refit": self.a.refit, "cpu_limit": self.a.cpu_limit,
            "pilot_json": self.a.pilot_json, "wall_guard_factor": self.a.wall_guard_factor,
            "unit_cap_hours": self.cap_hours, "unit_cap_source": self.cap_source,
            "retry_failed_decision": self.a.retry_failed, "retry_decision_row": self.retry_row,
            "build": self.build,
            "kdis_repeat": self.kdis_repeat_record,
            "code_sha256": self.code_sha, "versions": ta.versions(),
            "java": _cmd_version(["java", "-version"]),
            "octave": _cmd_version(["octave", "--version"])})
        d["meta"] = {"dataset": self.dataset, "version": self.vname, "condition": self.base_cond,
                     "design": self.v.design, "grid": self.grid.name, "inner_k": self.grid.inner_k,
                     "mimlnn_seeds": list(self.grid.mimlnn_seeds),
                     "candidates": [f"{c.method}/{c.config}" for c in self.grid.candidates],
                     "hamming_from": "native bipartition", "ranking_metrics_from": "scores",
                     "scorer": "HammingLoss: miml_clam/metrics/miml_metrics.py; ranking metrics: tie_neutral_metrics.py (AMENDMENT.md A1)",
                     "energy": "not measured by this harness (powermetrics needs sudo; §6.2)",
                     "repeated_methods": repeated,
                     "kdis_repeat": self.kdis_repeat_record}
        prior = float(d.get("process_hours_used", 0.0))
        splits = self.v.splits[: self.a.folds] if self.a.folds else self.v.splits
        try:
            with ThreadPoolExecutor(max_workers=max(self.n_jobs, 1)) as pool:
                for split in splits:
                    key = f"r{split.repeat}_f{split.fold}"
                    if key in d["folds"] and not self.a.recompute_selection:
                        print(f"  {key}: done", flush=True)
                        continue
                    if self.cap_hours and prior + self.used_s / 3600 > self.cap_hours:
                        raise UnitCapReached(key)
                    t0 = time.time()
                    k, rec = self.run_split(split, pool)
                    d["folds"][k] = rec
                    d["process_hours_used"] = prior + self.used_s / 3600
                    if rec["held_refit_failures"]:
                        # §6.7 continuation rule: independent later folds go on
                        d.setdefault("held", {})[k] = rec["held_refit_failures"]
                        print(f"  {k}: HELD refit failure(s): {rec['held_refit_failures']}", flush=True)
                    elif k in d.get("held", {}):
                        # review r4 note 1: a fold re-run cleanly (e.g. after an approved
                        # --retry-failed) is no longer held; the history stays in runs[]
                        d["runs"][-1].setdefault("released_holds", {})[k] = d["held"].pop(k)
                        if not d["held"]:
                            d.pop("held")
                    d["summary"] = summarise(d["folds"])
                    writer.save()
                    lib = rec["selection"]["library"]["AveragePrecision"]
                    print(f"  {k}: library AP={lib.get('test')} "
                          f"({lib.get('selected')}, by {lib['decided_by']}) "
                          f"{time.time() - t0:.0f}s", flush=True)
        except UnitCapReached as exc:
            d["process_hours_used"] = prior + self.used_s / 3600
            d["paused"] = {"at": str(exc), "reason": "unit cap (§6.6/§6.7 stop rule)",
                           "process_hours_used": d["process_hours_used"]}
            writer.save()
            print(f"PAUSED at {exc}: unit cap reached; request an extension (§6.7)", flush=True)
            return 3
        d["runs"][-1]["end"] = time.time()
        if "paused" in d:              # review r4 note 1: a completed run is not paused
            d["runs"][-1]["released_pause"] = d.pop("paused")
        writer.save()
        if d.get("held"):
            print("HELD: refit failures need a decision under the §6.7 stop rule "
                  f"({sum(len(v) for v in d['held'].values())} fold x metric entries)", flush=True)
            return 3
        return 0


def pilot_key(cand, seed):
    """Pilot unit key: method/config[/seed-sK | /rep-rK] (same tokens as §1.5)."""
    tok = lh.condition_token("main", seed, lh.repeat_kind(cand)) if seed is not None else None
    return f"{cand.method}/{cand.config}" + (f"/{tok}" if tok else "")


def summarise(folds):
    """Per procedure x metric: per-fold test values, mean and SD (ddof=1)."""
    out = {}
    for rec in folds.values():
        for proc, mets in rec["selection"].items():
            for m, e in mets.items():
                out.setdefault(proc, {}).setdefault(m, []).append(e.get("test"))
    summ = {}
    for proc, mets in out.items():
        for m, vals in mets.items():
            ok = [v for v in vals if v is not None]
            summ.setdefault(proc, {})[m] = {
                "n_folds": len(vals), "n_ok": len(ok),
                "mean": float(np.mean(ok)) if ok else None,
                "sd_ddof1": float(np.std(ok, ddof=1)) if len(ok) > 1 else None}
    return summ


def _cmd_version(cmd):
    try:
        p = __import__("subprocess").run(cmd, capture_output=True, text=True, timeout=30)
        return (p.stdout + p.stderr).strip().splitlines()[0]
    except Exception as exc:
        return f"unavailable: {exc}"


# --------------------------------------------------------------------------
# Pilot (§6.3): times only; predictions discarded unscored
# --------------------------------------------------------------------------
def run_pilot(args, version, groups, grid):
    r = Runner(args, version, groups, grid)
    split = version.splits[0]
    if args.dataset in ta.INSTANCE_PCA and args.version != "rebuilt":
        split = ta.apply_instance_pca(split, ta.INSTANCE_PCA[args.dataset])
    workroot = os.path.join(args.workdir, "pilot", args.dataset, args.version, args.condition)
    _, tr0, te0 = lh.inner_folds(split.ids_tr, split.repeat, split.fold, grid.inner_k, groups)[0]
    inputs = lh.export_split(split, os.path.join(workroot, "inputs"), f"{args.dataset}_pilot",
                             {"i0": (tr0, te0), "refit": (lh.refit_train_ids(split.ids_tr), split.ids_te)})
    n_outer = len(version.splits)
    out = {"build": lh.check_build(), "wall_guard_s": args.pilot_cpu_limit * args.wall_guard_factor,
           "kdis_repeat": r.kdis_repeat_record,          # review r3 F2
           "dataset": args.dataset, "version": args.version, "condition": args.condition,
           "xmx_gib": r.xmx, "jobs": r.n_jobs, "inner_k": grid.inner_k, "n_outer": n_outer,
           "units": {}, "load1_start": os.getloadavg()[0], "start": time.time()}
    tasks = [(c, s, kind, tr, te) for c in grid.candidates for s in r.seeds_of(c)
             for kind, tr, te in (("inner", tr0, te0),
                                  ("refit", lh.refit_train_ids(split.ids_tr), split.ids_te))]

    guard = args.pilot_cpu_limit * args.wall_guard_factor      # review r1 F1: always bounded

    def one(t):
        c, s, kind, tr, te = t
        wd = os.path.join(workroot, "units", c.method, c.config, str(s), kind)
        with r.budget(r.xmx if not c.is_mimlnn else 2):
            if c.is_mimlnn:
                rec, _, _ = lh.run_mimlnn_unit(c, s, inputs, tr, te, wd, args.pilot_cpu_limit,
                                               guard, codedir=args.mimlnn_code)
            else:
                rec, _, _ = lh.run_kdis_unit(c, inputs, "i0" if kind == "inner" else "refit", te, wd,
                                             r.xmx, args.pilot_cpu_limit, guard, seed=s)
        shutil.rmtree(wd, ignore_errors=True)          # predictions discarded unscored
        rec.pop("native_measures", None)
        return t, rec

    with ThreadPoolExecutor(max_workers=r.n_jobs) as pool:
        for (c, s, kind, _, _), rec in pool.map(one, tasks):
            key = pilot_key(c, s)
            out["units"].setdefault(key, {})[kind] = {
                k: rec.get(k) for k in ("status", "cpu_s", "wall_s", "peak_rss_bytes",
                                        "load1_start", "load1_end", "concurrent_at_start",
                                        "killed_by", "fit_wall_s",
                                        "predict_wall_s", "fit_predict_cpu_s")}
    # §6.3 (pre-deposit addendum): inner term over every candidate; refit term
    # bounded per outer fold by, for each of the 8 methods, the sum of its 5
    # largest measured candidate refit times (MIMLNN: all seeds of a candidate).
    total_inner, refit_by_cand = 0.0, {}
    for key, u in out["units"].items():
        total_inner += (u["inner"]["cpu_s"] or 0) * grid.inner_k * n_outer
        cand = "/".join(key.split("/")[:2])
        refit_by_cand[cand] = refit_by_cand.get(cand, 0.0) + (u["refit"]["cpu_s"] or 0)
    bound = 0.0
    per_method = {}
    for m in lh.LIBRARY_METHODS:
        times = sorted((t for c, t in refit_by_cand.items() if c.split("/")[0] == m), reverse=True)
        per_method[m] = sum(times[:5])
        bound += per_method[m]
    # Q10 (lead, 2026-10-13): MIMLNN recomputes the training Hausdorff matrix in
    # every call, so its per-call cost is reported on its own.
    mc = {k: v for k, v in out["units"].items() if k.startswith("MIMLNN/")}
    if mc:
        out["mimlnn_per_call_cpu_s"] = {
            kind: {"mean": float(np.mean([v[kind]["cpu_s"] or 0 for v in mc.values()])),
                   "max": float(max(v[kind]["cpu_s"] or 0 for v in mc.values())),
                   "n_calls": len(mc)} for kind in ("inner", "refit")}
    out["projection_process_hours"] = {
        "inner": total_inner / 3600,
        "refit_upper_bound": bound * n_outer / 3600,
        "total": (total_inner + bound * n_outer) / 3600,
        "refit_bound_per_outer_fold_s_by_method": per_method,
        "formula": "sum over candidates (and MIMLNN seeds) of inner cpu x inner_k x outer folds "
                   "x repeats + [sum over the 8 methods of its 5 largest candidate refit cpu] x "
                   "outer folds x repeats (§6.3, pre-deposit addendum)"}
    # review r1 F6: a projection built from failed or load-contaminated units is
    # flagged, never silently written as complete
    not_ok = sorted(f"{k}/{kind}" for k, u in out["units"].items() for kind, r_ in u.items()
                    if r_["status"] != "ok")
    loaded = sorted(f"{k}/{kind}" for k, u in out["units"].items() for kind, r_ in u.items()
                    if max(r_.get("load1_start") or 0, r_.get("load1_end") or 0) > 10)
    out.update(n_units_not_ok=len(not_ok), units_not_ok=not_ok,
               n_units_load_over_10=len(loaded), units_load_over_10=loaded)
    out["projection_process_hours"]["incomplete"] = bool(not_ok)
    out["projection_process_hours"]["retime_needed"] = bool(loaded)
    if not_ok or loaded:
        print(f"WARNING: pilot projection unsafe: {len(not_ok)} unit(s) not ok, "
              f"{len(loaded)} timed with load > 10 (§6.1: re-time)", flush=True)
    out["end"] = time.time()
    shutil.rmtree(workroot, ignore_errors=True)
    path = args.pilot_out
    lh.guard_write(path)
    ta.save_json_noclobber(path, out)
    print(f"pilot written: {path}; projection "
          f"{out['projection_process_hours']['total']:.3f} process-hours",
          flush=True)
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--version", default="original",
                    choices=("original", "rcv10", "submitted5", "rebuilt", "purged"))
    ap.add_argument("--condition", default="main",
                    help="main | leak | control-s0..s2 (purged only)")
    ap.add_argument("--synthetic", type=int, default=None,
                    help="use a synthetic dataset of N bags (tests; no real data)")
    ap.add_argument("--synthetic-design", default="canonical", choices=("canonical", "repeated"))
    ap.add_argument("--synthetic-grouped", action="store_true",
                    help="synthetic only: H2-A style pool-grouped inner folds")
    ap.add_argument("--methods", default=",".join(lh.LIBRARY_METHODS))
    ap.add_argument("--grid-k", default=None, help="tests only: override the k grid")
    ap.add_argument("--grid-distances", default=None, help="tests only: override distances")
    ap.add_argument("--grid-mimlnn", default=None,
                    help="tests only: 'ratio:lam,ratio:lam' override of the MIMLNN grid")
    ap.add_argument("--grid-seeds", default=None, help="tests only: override MIMLNN seeds")
    ap.add_argument("--folds", type=int, default=None, help="smoke: first N outer folds")
    ap.add_argument("--root", default=DEFAULT_ROOT, help="predictions/ and manifests/ live here")
    ap.add_argument("--results-json", default=None)
    ap.add_argument("--constructions-root",
                    default=os.path.join(lh.PROJECT, "results", "revision_r1", "constructions"))
    ap.add_argument("--workdir", default=os.path.join(os.environ.get("TMPDIR", "/tmp"), "nested_library"))
    ap.add_argument("--keep-inputs", action="store_true")
    ap.add_argument("--keep-workdirs", action="store_true")
    ap.add_argument("--xmx", type=int, default=None, help="GiB; default §6.1 rule")
    ap.add_argument("--jobs", type=int, default=None, help="default min(8, 16 // Xmx)")
    ap.add_argument("--cpu-limit", type=float, default=None,
                    help="seconds per run; default max(7200, 3 x pilot) (§6.6)")
    ap.add_argument("--pilot-json", default=None, help="pilot output feeding the §6.6 limit")
    ap.add_argument("--wall-guard-factor", type=float, default=4.0)
    ap.add_argument("--unit-cap-hours", type=float, default=None,
                    help="min(3 x projection, 450) (§6.6); pause when exceeded")
    ap.add_argument("--retry-failed", default=None, metavar="DECISION",
                    help="re-run units with a .fail.json after an approved §6.7 decision; "
                         "DECISION must appear in --decisions-file; failures are moved aside "
                         "and the move is logged in the manifest")
    ap.add_argument("--decisions-file",
                    default=os.path.join(lh.PROJECT, "revision_access_44676", "DECISIONS.md"))
    ap.add_argument("--kdis-repeat-file", default=None,
                    help="T03-a evidence JSON; KDIS methods it found non-deterministic are run "
                         "5 times per unit (DECISIONS.md 2026-10-13). Default: off")
    ap.add_argument("--refit", default="selected", choices=("selected", "all"))
    ap.add_argument("--recompute-selection", action="store_true",
                    help="redo selection for completed folds from stored units (no refits run twice)")
    ap.add_argument("--mimlnn-code", default=lh.MIMLNN_CODE)
    ap.add_argument("--pilot", action="store_true", help="§6.3 timing pilot: times only")
    ap.add_argument("--pilot-out", default=None)
    ap.add_argument("--pilot-cpu-limit", type=float, default=CPU_FLOOR_S)
    args = ap.parse_args(argv)

    lh.set_run_mode(args.synthetic is not None)
    lh.guard_dataset(args.dataset, args.synthetic is not None)
    lh.guard_write(args.root)
    if args.version != "purged" and args.condition != "main":
        raise SystemExit("condition other than main is defined for the purged version only")
    if args.version == "purged" and args.condition not in ("leak", "control-s0", "control-s1", "control-s2"):
        raise SystemExit("purged needs --condition leak|control-s0..s2")
    build = _check_sources(args)
    retry_row = decision_row(args.retry_failed, args.decisions_file) if args.retry_failed else None
    require_t03a(args)                  # before any real data is read

    groups = None
    if args.synthetic is not None:
        version, canonical = synthetic_version(args.synthetic, args.synthetic_design)
        if args.synthetic_grouped:
            groups = lh.pool_groups(canonical)
    else:
        version, groups = load_version(args.dataset, args.version, args.condition,
                                       args.constructions_root)
    grid = lh.grid_for(args.dataset, tuple(args.methods.split(",")))
    grid = _override_grid(grid, args)

    if args.pilot:
        args.pilot_out = args.pilot_out or os.path.join(
            args.root, "pilots", f"library__{args.dataset}__{args.version}__{args.condition}.json")
        return run_pilot(args, version, groups, grid)

    path = args.results_json or os.path.join(
        args.root, "library", f"{args.dataset}__{args.version}__{args.condition}.json")
    writer = ResultsWriter(path)
    try:
        runner = Runner(args, version, groups, grid)
        runner.build, runner.retry_row = build, retry_row
        return runner.run(writer)
    finally:
        writer.close()


def _override_grid(grid, args):
    if not any((args.grid_k, args.grid_distances, args.grid_mimlnn, args.grid_seeds)):
        return grid
    if args.synthetic is None:
        raise SystemExit("grid overrides are for synthetic tests only")
    ks = [int(k) for k in args.grid_k.split(",")] if args.grid_k else None
    ds = args.grid_distances.split(",") if args.grid_distances else None
    cands = []
    for c in grid.candidates:
        if c.is_mimlnn:
            continue
        if (ks is None or c.k in ks) and (ds is None or c.distance in ds):
            cands.append(c)
    if any(c.is_mimlnn for c in grid.candidates):
        if args.grid_mimlnn:
            for tok in args.grid_mimlnn.split(","):
                r_, l_ = tok.split(":")
                cands.append(lh.Candidate("MIMLNN", ratio=float(r_), lam=float(l_)))
        else:
            cands += [c for c in grid.candidates if c.is_mimlnn]
    seeds = tuple(int(s) for s in args.grid_seeds.split(",")) if args.grid_seeds else grid.mimlnn_seeds
    return lh.Grid(tuple(cands), seeds, grid.inner_k, grid.name + " [TEST OVERRIDE]")


def require_t03a(args):
    """DECISIONS.md 2026-10-13 rule (a): in real mode a KDIS pilot or run starts
    only if the Letter Frost T03-a result exists and passes its integrity check
    (§6.8 orders T03-a first). The file is then always the repeat file: an
    absent --kdis-repeat-file means the default Letter Frost path."""
    if args.synthetic is not None:
        return
    if not any(m in lh.KDIS_METHODS for m in args.methods.split(",")):
        return
    args.kdis_repeat_file = args.kdis_repeat_file or lh.T03A_REAL
    if not os.path.exists(args.kdis_repeat_file):
        raise SystemExit(f"real KDIS runs need the Letter Frost T03-a result first (§6.8): "
                         f"{args.kdis_repeat_file} does not exist")
    lh.kdis_repeat_methods(args.kdis_repeat_file, real=True)     # integrity, or SystemExit


def decision_row(text, decisions_file):
    """review r2 F3: --retry-failed must identify exactly ONE table row of
    DECISIONS.md (a line starting with '|' containing `text`); that row is then
    required to name each unit it re-runs. Anything else is refused."""
    rows = [l.rstrip("\n") for l in open(decisions_file, encoding="utf-8")
            if l.lstrip().startswith("|") and text in l]
    if len(rows) != 1:
        raise SystemExit(f"--retry-failed {text!r} matches {len(rows)} table rows of "
                         f"{decisions_file}; it must identify exactly one approved §6.7 decision")
    return rows[0]


def resolve_unit_cap(args, pilot):
    """§6.6 library unit cap = min(3 x projection, 450) process-hours, derived
    from the pilot JSON (review r1 F9). --unit-cap-hours overrides and is
    logged as an override beside the derived value."""
    derived = None
    if pilot is not None:
        proj = pilot["projection_process_hours"]
        if proj.get("incomplete") or proj.get("retime_needed"):
            raise SystemExit("pilot projection is flagged incomplete/retime_needed (§6.1, §6.3): "
                             "re-run the pilot before deriving the unit cap")
        derived = min(3.0 * float(proj["total"]), 450.0)
    if args.unit_cap_hours is not None:
        src = "operator override" + (f" (pilot-derived {derived:.6g} h)" if derived is not None else "")
        return float(args.unit_cap_hours), src
    if derived is not None:
        return derived, "min(3 x pilot projection, 450) (§6.6)"
    return None, "none (no pilot JSON, no override)"


def _check_sources(args):
    build = lh.check_build()               # review r1 F3: classes match current sources
    if "MIMLNN" in args.methods.split(","):
        p = os.path.join(args.mimlnn_code, "MIMLNN.m")
        if not os.path.exists(p) or (args.mimlnn_code == lh.MIMLNN_CODE
                                     and ta.sha256_file(p) != lh.MIMLNN_SHA256):
            raise SystemExit(f"authors' MIMLNN.m missing or changed at {p}")
    return build


if __name__ == "__main__":
    sys.exit(main())
