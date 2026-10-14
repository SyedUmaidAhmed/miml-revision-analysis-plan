"""Published-library arms (KDIS Java + LAMDA MIMLNN) for revision R1, task T03.

Binding spec: experiments/revision_r1/PREREGISTERED.md (tag prereg-v3-final),
sections 1.3 (inner selection, grids, tie-break, refit, MIMLNN seeds), 1.4 (raw
features; VOC2012 instance PCA), 1.5 (prediction storage, no-overwrite writer,
PredictDump), 6.1 (Xmx, concurrency, thread pinning, CPU time), 6.2 (cost
records), 6.3 (pilots), 6.5 (VOC2012 grid), 6.6 (CPU-time limits, crashes).

This module is a library (the CLI is run_nested_library.py):
  - the candidate grids (84 KDIS configurations, 9 MIMLNN configurations);
  - inner folds per outer fold (seed 1000 + fold + 100 x repeat; H2-A grouped);
  - export of one outer fold's bags to ARFF+XML (KDIS) and .mat (Octave),
    lossless (shortest round-trip float64 text);
  - one child process per unit (PredictDump.java or run_mimlnn.m), CPU time and
    peak RSS from os.wait4 of that child, CPU limit by `ulimit -t`;
  - scoring of every unit on the dumped predictions: Hamming loss by
    miml_metrics.py, the four ranking metrics tie-neutral (AMENDMENT.md A1);
  - selection per metric with the pre-registered tie-break order.

Split designs and the no-overwrite writer are imported from tabpfn_arms.py so
the library arms and the TabPFN arms see byte-identical outer folds.
"""
import os

# §6.1: thread pools pinned in every process. Must precede the numpy import.
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"

import json  # noqa: E402
import math  # noqa: E402
import re  # noqa: E402
import signal  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import threading  # noqa: E402
import time  # noqa: E402
from dataclasses import dataclass  # noqa: E402

import numpy as np  # noqa: E402
from scipy.io import savemat  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
EXPERIMENTS = os.path.dirname(HERE)
PROJECT = os.path.dirname(EXPERIMENTS)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(EXPERIMENTS, "kdis"))

import tabpfn_arms as ta  # noqa: E402  (split designs, writer, synthetic data)
from run_kdis_baselines import DISTANCES, classifier_block  # noqa: E402
from miml_clam.metrics.miml_metrics import (  # noqa: E402
    AveragePrecision, CoverageError, HammingLoss, OneErrorLoss, RankingLoss)
import tie_neutral_metrics as tn  # noqa: E402  (AMENDMENT.md A1)

FIVE = ta.FIVE
HIGHER_BETTER = {"AveragePrecision"}

JAR = os.path.join(PROJECT, "external", "MIML", "dist", "miml-1.4-jar-with-dependencies.jar")
JAR_SHA256 = "cce956458a2c67061932b09982568859ceb3ae38f98b8b7b9ed7468454a9faf2"
KDIS_BUILD = os.path.join(EXPERIMENTS, "kdis", "build")
LAMDA_DIR = os.path.join(EXPERIMENTS, "lamda")
SEED_SHIM = os.path.join(LAMDA_DIR, "seed_shim")
MIMLNN_CODE = os.path.join(PROJECT, "data", "third_party", "lamda_mimlnn", "extracted", "MIMLNN")
MIMLNN_SHA256 = "e5a6070b98dccddebfa325105a07d6ce2f8d9d1a906414a7521ff530bdcb3b26"

# --------------------------------------------------------------------------
# Deposit guard at the I/O choke points (HARD RULE; §6.0 step 0)
# --------------------------------------------------------------------------
# Real data may be read, and real output trees written, only after the plan's
# Public-timestamp row is filled. Synthetic runs may never write into the real
# output trees. Paths are compared after realpath (symlinks) and casefold (APFS
# is case-insensitive), by os.path.commonpath containment, not by prefix.
REAL_OUTPUT_ROOTS = (os.path.join(PROJECT, "results"),
                     os.path.join(PROJECT, "revision_access_44676", "evidence"))
_RUN_MODE = {"synthetic": None}          # None = not declared: every write refused


class GuardError(SystemExit):
    pass


def set_run_mode(synthetic):
    _RUN_MODE["synthetic"] = bool(synthetic)


import deposit_check  # noqa: E402  (the ONE shared deposit rule; DECISIONS.md 2026-10-13)

PREREG = deposit_check.PLAN


def deposit_recorded(prereg_path=PREREG):
    """Thin wrapper: the shared, strict whole-cell rule of deposit_check.py
    (line 8 value cell == `https://doi.org/<DOI> (YYYY-MM-DD)`, real date, no
    placeholder DOI). Kept so every T03 caller has one name to call."""
    return deposit_check.deposit_recorded(prereg_path)


# Path aliases on this Mac (T02 review 3): realpath leaves the firmlink
# /System/Volumes/Data/... (same inode as /...), case (case-insensitive APFS)
# and Unicode normalisation (NFC vs NFD name the same entry) unresolved.
FIRMLINK = "/System/Volumes/Data"


def _canon(path):
    """realpath -> strip the /System/Volumes/Data firmlink -> NFC -> casefold."""
    import unicodedata
    q = os.path.realpath(os.path.abspath(path))
    if q == FIRMLINK or q.startswith(FIRMLINK + "/"):
        q = q[len(FIRMLINK):] or "/"
    return unicodedata.normalize("NFC", q).casefold()


def is_within(path, root):
    """Containment by commonpath on _canon of BOTH sides (fail closed: a
    ValueError, e.g. mixed absolute/relative, counts as inside)."""
    c, r = _canon(path), _canon(root)
    try:
        return os.path.commonpath([c, r]) == r
    except ValueError:
        return True


def real_dataset_names():
    import run_baseline_experiments as rbe
    names = set(rbe.DATASET_CONFIGS) | set(ta.EXTRA_CONFIGS) | set(ta.CONSTRUCTED)
    return {n.casefold() for n in names}


def guard_dataset(name, synthetic):
    """Real dataset names need the deposit; a synthetic run may not borrow one
    (case-insensitively), so synthetic artefacts can never pass for real ones."""
    real = name.casefold() in real_dataset_names()
    if synthetic and real:
        raise GuardError(f"synthetic run may not use the real dataset name {name!r}")
    if not synthetic and not deposit_recorded():
        raise GuardError("PREREGISTERED.md 'Public timestamp' is PENDING, or an amendment in "
                         "AMENDMENT.md is not deposited: real-data runs are refused before the "
                         "deposit (§6.0 step 0, §1.8)")


def guard_write(path):
    """Called by every writer before it creates anything at `path`."""
    mode = _RUN_MODE["synthetic"]
    if mode is None:
        raise GuardError(f"write to {path} refused: run mode (synthetic or real) not declared")
    if mode:
        for root in REAL_OUTPUT_ROOTS:
            if is_within(path, root):
                raise GuardError(f"synthetic run may not write into the real output tree {root}: {path}")
    elif not deposit_recorded():
        raise GuardError(f"write to {path} refused: plan or an amendment (AMENDMENT.md) not deposited "
                         "(§6.0 step 0, §1.8)")


# --------------------------------------------------------------------------
# Grids (§1.3, §6.5)
# --------------------------------------------------------------------------
KDIS_METHODS = ("MIMLkNN", "DMIMLkNN", "MIMLBRkNN", "MIMLMAPkNN", "MIMLIBLR",
                "MIMLDGC", "MIMLBagging")
LIBRARY_METHODS = KDIS_METHODS + ("MIMLNN",)
K_TAGS = {"MIMLkNN": ("nReferences", "nCiters"), "MIMLBagging": ("nReferences", "nCiters")}


@dataclass(frozen=True)
class Candidate:
    method: str
    distance: str = None     # KDIS
    k: int = None            # KDIS
    ratio: float = None      # MIMLNN
    lam: float = None        # MIMLNN

    @property
    def config(self):
        """The <config> token of the §1.5 key."""
        if self.method == "MIMLNN":
            return f"ratio{self.ratio:g}-lambda{self.lam:g}"
        return f"{self.distance}-k{self.k}"

    @property
    def is_mimlnn(self):
        return self.method == "MIMLNN"


@dataclass(frozen=True)
class Grid:
    candidates: tuple
    mimlnn_seeds: tuple
    inner_k: int
    name: str


def grid_for(dataset, methods=LIBRARY_METHODS):
    """§1.3 full grid; §6.5 reduced grid on VOC2012 (its configuration, not a fallback)."""
    if dataset == "voc2012":
        dists, ks, ratios, lams, seeds, inner_k, name = (
            ("AveH", "MaxH"), (10, 20), (0.2, 0.4), (1.0,), (0, 1), 3, "voc2012 (§6.5)")
    else:
        dists, ks, ratios, lams, seeds, inner_k, name = (
            ("AveH", "MaxH", "MinH"), (5, 10, 15, 20), (0.2, 0.4, 0.6), (0.1, 1.0, 10.0),
            (0, 1, 2, 3, 4), 5, "full (§1.3)")
    cands = [Candidate(m, distance=d, k=k) for m in KDIS_METHODS if m in methods
             for d in dists for k in ks]
    if "MIMLNN" in methods:
        cands += [Candidate("MIMLNN", ratio=r, lam=l) for r in ratios for l in lams]
    return Grid(tuple(cands), seeds, inner_k, name)


def check_build():
    """Refuse to run PredictDump/MulanScore classes not compiled from the
    current sources (review r1 F3). Returns the build record for run logs."""
    if ta.sha256_file(JAR) != JAR_SHA256:
        raise SystemExit("KDIS jar sha256 changed")
    srcfile = os.path.join(KDIS_BUILD, "SOURCES.sha256")
    for f in ("PredictDump.class", "MulanScore.class"):
        if not os.path.exists(os.path.join(KDIS_BUILD, f)):
            raise SystemExit("run experiments/kdis/build_predictdump.sh first")
    if not os.path.exists(srcfile):
        raise SystemExit(f"{srcfile} missing: rebuild with experiments/kdis/build_predictdump.sh")
    built = {}
    for line in open(srcfile):
        if line.strip():
            h, path = line.split(None, 1)
            built[os.path.basename(path.strip())] = h
    current = {n: ta.sha256_file(os.path.join(EXPERIMENTS, "kdis", n))
               for n in ("PredictDump.java", "MulanScore.java")}
    if built != current:
        raise SystemExit("experiments/kdis/build/ was not compiled from the current "
                         f"PredictDump.java/MulanScore.java (built {built}, now {current}); "
                         "rerun experiments/kdis/build_predictdump.sh")
    jv = os.path.join(KDIS_BUILD, "JAVA_VERSION.txt")
    return {"sources_sha256": current, "jar_sha256": JAR_SHA256,
            "build_java_version": open(jv).read().strip() if os.path.exists(jv) else None}


def kdis_block(cand, seed=None):
    """Shipped <classifier> block, verbatim except metric and neighbourhood size.

    seed: only under the KDIS non-determinism fallback (DECISIONS.md
    2026-10-13 "KDIS non-determinism fallback"), and only for MIMLBagging, whose
    shipped block has <seed>1</seed>; it is then set to `seed` (0..4).
    """
    block = classifier_block(cand.method, cand.distance, cand.k)
    if block is None:
        raise ValueError(f"no shipped config for {cand.method}")
    tags = K_TAGS.get(cand.method, ("numOfNeighbours",))
    for t in tags:
        if f"<{t}>{cand.k}</{t}>" not in block:
            raise ValueError(f"{cand.method}: <{t}> not set to {cand.k}")
    want = DISTANCES[cand.distance]
    if set(re.findall(r'<metric name="([^"]+)"', block)) != {want}:
        raise ValueError(f"{cand.method}: metric not set to {want}")
    if seed is not None and cand.method in KDIS_SEEDED:
        if len(re.findall(r"<seed>\d+</seed>", block)) != 1:
            raise ValueError(f"{cand.method}: expected exactly one <seed> tag")
        block = re.sub(r"<seed>\d+</seed>", f"<seed>{int(seed)}</seed>", block)
    return block


# KDIS non-determinism fallback (DECISIONS.md 2026-10-13): methods T03-a finds
# non-deterministic are run KDIS_REPEATS times per (candidate, fold); metrics
# are averaged over the runs before selection, as for MIMLNN's seeds.
# Labelling (DECISIONS.md 2026-10-13, "KDIS fallback labelling"): every KDIS
# repetition is UNCONTROLLED (token rep-r<k>, uncontrolled=true). A method is
# repeated only when T03-a found it non-identical; for MIMLBagging that means
# its shipped fixed <seed> did not control its randomness, so its runs are not
# seeded runs either. Its <seed> is still set to k (0..4) in run k, so the five
# configurations are not nominally identical; the identity records it.
KDIS_REPEATS = (0, 1, 2, 3, 4)
KDIS_SEEDED = ("MIMLBagging",)          # methods whose block has a <seed> tag to vary


def repeat_kind(cand):
    """'seed' for MIMLNN (Octave seed via the clock shim); 'rep' for every KDIS
    repetition, MIMLBagging included (DECISIONS.md "KDIS fallback labelling")."""
    return "seed" if cand.is_mimlnn else "rep"


def condition_token(base, seed=None, kind="seed"):
    """§1.5 <condition>: MIMLNN units carry seed-s<s>, joined with '+'; under the
    KDIS fallback, uncontrolled repetitions carry rep-r<k>."""
    if seed is None:
        return base
    tok = f"seed-s{seed}" if kind == "seed" else f"rep-r{seed}"
    return tok if base == "main" else f"{base}+{tok}"


T03A_REAL = os.path.join(PROJECT, "revision_access_44676", "evidence", "T03__checks",
                         "T03-a__letter_frost.json")


def kdis_repeat_methods(t03a_path, real=False):
    """Methods to repeat, read from a T03-a evidence JSON (DECISIONS.md
    2026-10-13, "T03 implementation rules derived from the plan").

    Integrity: check == "T03-a"; all 7 KDIS methods present, each with two
    statuses and a byte_identical flag; in real mode the file must be the
    Letter Frost result (dataset tag "letter_frost") and was produced by the
    PredictDump build in use (its build.sources_sha256 equals check_build()'s).
    (b) A crash or timeout in either run of any method is a FAILED check routed
    to the §6.7 stop rule, never evidence of non-determinism: refused. Only two
    completed runs with differing predictions put a method in the repeat set.
    Returns (methods, record for the run log)."""
    try:
        d = json.load(open(t03a_path))
    except (OSError, ValueError) as exc:
        raise SystemExit(f"T03-a result {t03a_path} unreadable: {exc}")
    if d.get("check") != "T03-a":
        raise SystemExit(f"{t03a_path} is not a T03-a result")
    methods = d.get("methods") or {}
    if set(methods) != set(KDIS_METHODS):
        raise SystemExit(f"{t03a_path}: methods {sorted(methods)} != the 7 KDIS methods")
    for m, r in methods.items():
        st = r.get("status")
        if not isinstance(st, list) or len(st) != 2 or "byte_identical" not in r:
            raise SystemExit(f"{t03a_path}: {m} lacks two run statuses or byte_identical")
    failed = sorted(m for m, r in methods.items() if r["status"] != ["ok", "ok"])
    if failed:
        raise SystemExit(f"T03-a FAILED for {failed} (statuses "
                         f"{ {m: methods[m]['status'] for m in failed} }): a crash or timeout is a "
                         "failed check, not non-determinism; route it through the §6.7 stop rule")
    if real:
        if d.get("dataset") != "letter_frost":
            raise SystemExit(f"{t03a_path}: real runs need the Letter Frost T03-a result, "
                             f"this one is for {d.get('dataset')!r}")
        built = (d.get("build") or {}).get("sources_sha256")
        if built != check_build()["sources_sha256"]:
            raise SystemExit(f"{t03a_path}: T03-a ran a different PredictDump build "
                             f"({built}); re-run T03-a")
    bad = sorted(m for m, r in methods.items() if not r["byte_identical"])
    return tuple(bad), {"t03a_file": os.path.abspath(t03a_path),
                        "t03a_sha256": ta.sha256_file(t03a_path),
                        "t03a_dataset": d.get("dataset"), "repeated_methods": bad}


# --------------------------------------------------------------------------
# Inner folds (§1.3; H2-A step 5)
# --------------------------------------------------------------------------
def inner_folds(ids_tr, repeat, fold, inner_k, groups=None):
    """Inner folds of one outer training fold, as (i, train_ids, test_ids).

    Default (§1.3, pre-deposit addendum): order =
    np.random.default_rng(1000 + fold + 100 * repeat).permutation(tr); inner
    fold i = np.array_split(order, inner_k)[i] (larger blocks first). Inner
    training order = ascending canonical bag index of the inner-training bags
    (lead decision Q17, 2026-10-13); inner test order = block order.

    groups (H2-A): dict bag id -> pool index g. The training pools are ranked by
    pool index and pool of rank rho goes to inner fold rho mod inner_k; inner
    training order = outer training order with the inner test bags removed.
    """
    ids_tr = np.asarray(ids_tr, dtype=np.int64)
    out = []
    # Q17: inner training bags in ascending canonical index, both rules
    if groups is None:
        order = np.random.default_rng(1000 + fold + 100 * repeat).permutation(ids_tr)
        blocks = np.array_split(np.arange(len(order)), inner_k)
        for i, blk in enumerate(blocks):
            mask = np.ones(len(order), bool)
            mask[blk] = False
            out.append((i, np.sort(order[mask]), order[blk]))
        return out
    pools = sorted({int(groups[int(b)]) for b in ids_tr})  # grouped rule
    assign = {g: rho % inner_k for rho, g in enumerate(pools)}
    fold_of = np.array([assign[int(groups[int(b)])] for b in ids_tr])
    for i in range(inner_k):
        out.append((i, np.sort(ids_tr[fold_of != i]), ids_tr[fold_of == i]))
    return out


def refit_train_ids(ids_tr):
    """Refit training order: ascending canonical bag index of the outer-training
    bags (plan clarification, review 11 finding 5; same rule as the inner
    training order, Q17). The §1.3 order of ids_tr is used only to draw the
    inner permutation."""
    return np.sort(np.asarray(ids_tr, dtype=np.int64))


def pool_groups(canonical_splits):
    """bag id -> canonical fold block g, from get_cv_splits output (H2-A pools)."""
    g = {}
    for f, (_, te) in enumerate(canonical_splits):
        for b in te:
            g[int(b)] = f
    return g


# --------------------------------------------------------------------------
# Inputs: one outer fold's bags, lossless
# --------------------------------------------------------------------------
def _num(v):
    return repr(float(v))


def split_universe(split):
    ids = set(int(i) for i in split.ids_tr) | set(int(i) for i in split.ids_te)
    return np.array(sorted(ids), dtype=np.int64)


def write_arff(path, name, ids, bags, Y, header_ids=None):
    """Bags `ids`, in that order. The nominal id attribute declares header_ids
    (default: ids); a train/test pair must declare the same set, or Weka
    rejects the pair as incompatible."""
    d = np.asarray(bags[int(ids[0])]).shape[1]
    L = len(Y[int(ids[0])])
    header_ids = ids if header_ids is None else header_ids
    with open(path, "w") as fh:
        fh.write(f"@relation {name}\n\n")
        fh.write("@attribute id {" + ",".join(str(int(i)) for i in header_ids) + "}\n")
        fh.write("@attribute bag relational\n")
        for j in range(d):
            fh.write(f"  @attribute f{j} numeric\n")
        fh.write("@end bag\n")
        for l in range(L):
            fh.write(f"@attribute L{l} {{0,1}}\n")
        fh.write("\n@data\n")
        for i in ids:
            b = np.asarray(bags[int(i)], dtype=np.float64)
            body = "\\n".join(",".join(_num(v) for v in row) for row in b)
            labs = ",".join(str(int(v)) for v in Y[int(i)])
            fh.write(f'{int(i)},"{body}",{labs}\n')


def write_xml(path, L):
    with open(path, "w") as fh:
        fh.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n')
        fh.write('<labels xmlns="http://mulan.sourceforge.net/labels">\n')
        for l in range(L):
            fh.write(f'\t<label name="L{l}" />\n')
        fh.write("</labels>\n")


def write_mat(path, ids, bags, Y):
    cell = np.empty((len(ids), 1), dtype=object)
    for r, i in enumerate(ids):
        cell[r, 0] = np.asarray(bags[int(i)], dtype=np.float64)
    T = np.stack([np.where(np.asarray(Y[int(i)]) > 0, 1.0, -1.0) for i in ids]).T
    savemat(path, {"bags": cell, "target": T, "ids": np.asarray(ids, dtype=np.float64)},
            do_compression=True)


def data_sha256(split, ids):
    """Content hash of a fold's bags and labels (ids, float64 instances, 0/1
    labels). Unit identity uses this, not file bytes: scipy's .mat header
    carries a creation timestamp, so the same data never hashes the same."""
    h = __import__("hashlib").sha256()
    for i in ids:
        b = np.ascontiguousarray(np.asarray(split.bags[int(i)], dtype=np.float64))
        h.update(np.int64(i).tobytes())
        h.update(np.int64(b.shape[0]).tobytes())
        h.update(b.tobytes())
        h.update(np.asarray(split.Y[int(i)], dtype=np.int8).tobytes())
    return h.hexdigest()


@dataclass
class Inputs:
    dir: str
    xml: str
    mat: str
    ids: np.ndarray            # the fold's bag universe; row order of the .mat file
    pairs: dict                # pair key -> (train.arff, test.arff)
    sha256: dict               # file name -> sha256
    data_sha256: str = None    # content hash of the fold's bags (unit identity)


def export_split(split, outdir, name, pairs, need=("kdis", "mimlnn")):
    """Write one outer fold's inputs once; every unit of that fold reads them.

    KDIS: one train/test ARFF pair per key of `pairs` (key -> (train_ids,
    test_ids)), i.e. per inner fold and for the refit. Each file holds only its
    own bags (so a test bag's instances are never in a training file) and
    every file of the fold declares the same nominal id set, the fold's whole
    bag universe, as the submission's converter did. Both choices matter:
    a one-file design changed MIMLIBLR and MIMLBagging predictions, and
    MIMLIBLR's predictions depend on the declared id set (T03 findings F1, F2).
    Octave: one .mat with every bag of the fold; units index rows.
    """
    guard_write(outdir)
    os.makedirs(outdir, exist_ok=True)
    ids = split_universe(split)
    L = len(split.Y[int(ids[0])])
    xml, mat = os.path.join(outdir, "labels.xml"), os.path.join(outdir, "bags.mat")
    sha, files = {}, {}
    if "kdis" in need:
        write_xml(xml, L)
        sha["labels.xml"] = ta.sha256_file(xml)
        for key, (tr, te) in pairs.items():
            ptr, pte = (os.path.join(outdir, f"{key}_{s}.arff") for s in ("train", "test"))
            write_arff(ptr, f"{name}_{key}", tr, split.bags, split.Y, header_ids=ids)
            write_arff(pte, f"{name}_{key}", te, split.bags, split.Y, header_ids=ids)
            files[key] = (ptr, pte)
            sha[os.path.basename(ptr)] = ta.sha256_file(ptr)
            sha[os.path.basename(pte)] = ta.sha256_file(pte)
    if "mimlnn" in need:
        write_mat(mat, ids, split.bags, split.Y)
        sha["bags.mat"] = ta.sha256_file(mat)
    return Inputs(outdir, xml, mat, ids, files, sha, data_sha256(split, ids))


def pair_key(inner):
    return "refit" if inner is None else f"i{inner}"


# --------------------------------------------------------------------------
# Child processes: CPU time, RSS, limits (§6.1, §6.6)
# --------------------------------------------------------------------------
_ACTIVE = {"n": 0}
_ACTIVE_LOCK = threading.Lock()


def child_env():
    env = dict(os.environ)
    env["OMP_NUM_THREADS"] = "1"
    env["OPENBLAS_NUM_THREADS"] = "1"
    return env


# Per-process CPU time read by the parent (review CODE-T03 r1, F1). Octave
# installs a handler that ignores SIGXCPU and macOS never escalates to SIGKILL
# at the hard RLIMIT_CPU, so `ulimit -t` alone does not stop an Octave child.
# The parent therefore sums user + sys CPU of every process in the child's
# process group each poll and SIGKILLs the group at the limit.
if sys.platform == "darwin":
    import ctypes
    import struct
    _LIBPROC = ctypes.CDLL("/usr/lib/libproc.dylib")
    _LIBC = ctypes.CDLL("/usr/lib/libSystem.dylib")

    class _Timebase(ctypes.Structure):
        _fields_ = [("numer", ctypes.c_uint32), ("denom", ctypes.c_uint32)]
    _TB = _Timebase()
    _LIBC.mach_timebase_info(ctypes.byref(_TB))
    _TICK_S = _TB.numer / _TB.denom / 1e9          # rusage_info times are mach ticks

    def _proc_cpu_s(pid):
        """user + sys of pid and of its reaped children (rusage_info_v2)."""
        buf = ctypes.create_string_buffer(512)
        if _LIBPROC.proc_pid_rusage(int(pid), 2, buf) != 0:
            return 0.0
        u, s_ = struct.unpack_from("QQ", buf.raw, 16)
        cu, cs = struct.unpack_from("QQ", buf.raw, 16 + 8 * 10)
        return (u + s_ + cu + cs) * _TICK_S

    def _group_pids(pgid):
        buf = (ctypes.c_int * 1024)()
        n = _LIBPROC.proc_listpgrppids(int(pgid), buf, ctypes.sizeof(buf))
        return [buf[i] for i in range(max(0, min(n, 1024))) if buf[i] > 0]
else:                                                # Linux fallback
    _CLK = os.sysconf("SC_CLK_TCK")

    def _proc_cpu_s(pid):
        try:
            f = open(f"/proc/{int(pid)}/stat").read().rsplit(")", 1)[1].split()
            return (int(f[11]) + int(f[12]) + int(f[13]) + int(f[14])) / _CLK
        except (OSError, IndexError, ValueError):
            return 0.0

    def _group_pids(pgid):
        out = []
        for d in os.listdir("/proc"):
            if d.isdigit():
                try:
                    if os.getpgid(int(d)) == pgid:
                        out.append(int(d))
                except OSError:
                    pass
        return out


def group_cpu_s(pgid):
    return float(sum(_proc_cpu_s(p) for p in _group_pids(pgid)))


def _killpg(pgid):
    try:
        os.killpg(pgid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass


def run_child(cmd, log_path, cpu_limit_s, wall_guard_s=None, cwd=None, poll_s=0.05):
    """Run one child in its own process group; enforce the §6.6 CPU limit.

    Two lines of defence: `ulimit -t` (enough for Java, which dies on SIGXCPU)
    and the parent's poll, which SIGKILLs the whole process group when the
    group's user + sys CPU reaches cpu_limit_s (needed for Octave, which
    ignores SIGXCPU). Either way the status is 'timeout'. wall_guard_s kills a
    child that hangs without using CPU ('wall-guard'). CPU seconds and peak
    RSS in the record come from os.wait4 of this child alone.
    """
    wrapped = ["/bin/sh", "-c", f'ulimit -t {int(math.ceil(cpu_limit_s))}; exec "$@"', "sh", *cmd]
    with _ACTIVE_LOCK:
        _ACTIVE["n"] += 1
        concurrent = _ACTIVE["n"]
    load0 = os.getloadavg()[0]
    t0 = time.time()
    guard_hit = cpu_hit = False
    polled = 0.0
    try:
        with open(log_path, "w") as log:
            p = subprocess.Popen(wrapped, stdout=log, stderr=subprocess.STDOUT,
                                 env=child_env(), cwd=cwd, start_new_session=True)
            pgid = p.pid
            while True:
                pid, status, ru = os.wait4(p.pid, os.WNOHANG)
                if pid == p.pid:
                    break
                if not (guard_hit or cpu_hit):
                    polled = max(polled, group_cpu_s(pgid))
                    if polled >= cpu_limit_s:
                        cpu_hit = True
                        _killpg(pgid)
                    elif wall_guard_s and time.time() - t0 > wall_guard_s:
                        guard_hit = True
                        _killpg(pgid)
                time.sleep(poll_s)
            p.returncode = os.waitstatus_to_exitcode(status)
            _killpg(pgid)                 # no orphan of the group survives the unit
    finally:
        with _ACTIVE_LOCK:
            _ACTIVE["n"] -= 1
    wall = time.time() - t0
    cpu = ru.ru_utime + ru.ru_stime
    rc = p.returncode
    try:
        tail = open(log_path, errors="replace").read()[-4000:]
    except OSError:
        tail = ""
    if rc == 0 and not cpu_hit:
        status_s = "ok"
    elif cpu_hit:
        status_s = "timeout"
    elif guard_hit:
        status_s = "wall-guard"
    elif rc in (-signal.SIGXCPU, -signal.SIGKILL) and cpu >= cpu_limit_s - 1.0:
        status_s = "timeout"
    elif "OutOfMemoryError" in tail:
        status_s = "oom"
    else:
        status_s = "crash"
    return {"status": status_s, "returncode": rc, "cpu_user_s": ru.ru_utime,
            "cpu_sys_s": ru.ru_stime, "cpu_s": cpu, "wall_s": wall,
            "cpu_polled_max_s": polled, "killed_by": ("parent cpu poll" if cpu_hit else
                                                       "wall guard" if guard_hit else None),
            "peak_rss_bytes": int(ru.ru_maxrss),  # bytes on macOS
            "load1_start": load0, "load1_end": os.getloadavg()[0],
            "concurrent_at_start": concurrent, "cpu_limit_s": cpu_limit_s,
            "wall_guard_s": wall_guard_s,
            "log_tail": tail[-600:] if rc != 0 else ""}


class MemoryBudget:
    """§6.1: N x Xmx <= 16 GiB, N <= 8. Each JVM reserves its Xmx; each Octave
    run reserves 16/8 = 2 GiB. An OOM retry at doubled Xmx reserves double,
    which halves the concurrency available to it."""

    def __init__(self, total_gib=16, max_jobs=8):
        self.total, self.free, self.cv = total_gib, total_gib, threading.Condition()
        self.slots = threading.BoundedSemaphore(max_jobs)

    def __call__(self, gib):
        budget = self

        class _Ctx:
            def __enter__(self_):
                budget.slots.acquire()
                with budget.cv:
                    while budget.free < min(gib, budget.total):
                        budget.cv.wait()
                    budget.free -= min(gib, budget.total)

            def __exit__(self_, *exc):
                with budget.cv:
                    budget.free += min(gib, budget.total)
                    budget.cv.notify_all()
                budget.slots.release()
        return _Ctx()


def default_xmx_gib(dataset):
    """§6.1: -Xmx2g by default, -Xmx8g for VOC2012 and every Corel5K version."""
    return 8 if dataset in ("voc2012", "corel5k") else 2


def concurrency(xmx_gib):
    return min(8, 16 // xmx_gib)


# --------------------------------------------------------------------------
# One unit
# --------------------------------------------------------------------------
def _write_ids(path, ids):
    with open(path, "w") as fh:
        fh.write("\n".join(str(int(i)) for i in ids) + "\n")


def _read_csv(path, dtype=float):
    a = np.loadtxt(path, delimiter=",", dtype=dtype, ndmin=2)
    return a


def run_kdis_unit(cand, inputs, key, test_ids, workdir, xmx_gib, cpu_limit_s,
                  wall_guard_s=None, seed=None):
    """PredictDump on the ARFF pair `key` of the fold. Returns (record, scores, bip)."""
    os.makedirs(workdir, exist_ok=True)
    cfg = os.path.join(workdir, "run.config")
    with open(cfg, "w") as fh:
        fh.write("<configuration>\n" + kdis_block(cand, seed) + "\n</configuration>\n")
    tr, te = inputs.pairs[key]
    out = os.path.join(workdir, "unit")
    cmd = ["java", "-XX:+UseSerialGC", f"-Xmx{xmx_gib}g", "-cp",
           f"{JAR}{os.pathsep}{KDIS_BUILD}", "PredictDump", "--config", cfg,
           "--xml", inputs.xml, "--train-arff", tr, "--test-arff", te, "--out", out]
    rec = run_child(cmd, os.path.join(workdir, "child.log"), cpu_limit_s, wall_guard_s)
    rec["xmx_gib"] = xmx_gib
    if rec["status"] != "ok":
        return rec, None, None
    meta = json.load(open(out + ".meta.json"))
    ids_out = np.loadtxt(out + ".ids.csv", dtype=np.int64, ndmin=1)
    if not np.array_equal(ids_out, np.asarray(test_ids, dtype=np.int64)):
        rec.update(status="crash", log_tail="PredictDump test-id order mismatch")
        return rec, None, None
    scores = _read_csv(out + ".scores.csv")
    bip = _read_csv(out + ".bip.csv", dtype=np.int64).astype(np.uint8) \
        if meta["has_bipartition"] else None
    rec.update({"fit_wall_s": meta["build_wall_ns"] / 1e9,
                "fit_thread_cpu_s": meta["build_thread_cpu_ns"] / 1e9,
                "predict_wall_s": meta["predict_wall_ns"] / 1e9,
                "predict_thread_cpu_s": meta["predict_thread_cpu_ns"] / 1e9,
                "native_measures": meta["native_measures"],
                "java_version": meta["java_version"], "n_train": meta["n_train"]})
    return rec, scores, bip


def run_mimlnn_unit(cand, seed, inputs, train_ids, test_ids, workdir, cpu_limit_s,
                    wall_guard_s=None, codedir=MIMLNN_CODE):
    os.makedirs(workdir, exist_ok=True)
    row = {int(b): r + 1 for r, b in enumerate(inputs.ids)}       # 1-based rows
    tr, te = os.path.join(workdir, "train.rows"), os.path.join(workdir, "test.rows")
    _write_ids(tr, [row[int(b)] for b in train_ids])
    _write_ids(te, [row[int(b)] for b in test_ids])
    out = os.path.join(workdir, "unit")
    call = (f"run_mimlnn('dump','{inputs.mat}','{tr}','{te}',{cand.ratio!r},"
            f"{cand.lam!r},{int(seed)},'{codedir}','{SEED_SHIM}','{out}')")
    cmd = ["octave", "--no-gui", "--norc", "--quiet", "--no-window-system",
           "--path", LAMDA_DIR, "--eval", call]
    rec = run_child(cmd, os.path.join(workdir, "child.log"), cpu_limit_s, wall_guard_s)
    if rec["status"] != "ok":
        return rec, None, None
    if not os.path.exists(out + ".scores.csv"):
        rec.update(status="crash", log_tail=rec.get("log_tail", "") + " no scores written")
        return rec, None, None
    scores = _read_csv(out + ".scores.csv")
    bip = _read_csv(out + ".bip.csv", dtype=np.int64).astype(np.uint8)
    meta = dict(line.strip().split("=", 1) for line in open(out + ".meta.txt") if "=" in line)
    nat = open(out + ".native.csv").read().strip().splitlines()
    native = dict(zip(nat[0].split(","), (float(v) for v in nat[1].split(","))))
    rec.update({"fit_predict_wall_s": float(meta["fit_predict_wall_s"]),
                "fit_predict_cpu_s": float(meta["fit_predict_cpu_s"]),
                "timing_note": meta["timing"], "complex_outputs": int(meta["complex_outputs"]),
                "max_abs_imag": float(meta["max_abs_imag"]),
                "flag_imag_above_1e-8": float(meta["max_abs_imag"]) > 1e-8,  # Q19
                "octave_version": meta["octave_version"], "native_measures": native,
                "n_train": int(meta["n_train"])})
    return rec, scores, bip


# --------------------------------------------------------------------------
# Scoring and selection (§1.3, §1.5)
# --------------------------------------------------------------------------
# §1.3 F4 (pre-deposit addendum): a label with no positive bag in a unit's
# training split is predicted constant negative, for library outputs as for
# TabPFN. The constant is the bottom of each method's own scale: 0.0 for KDIS
# confidences (in [0, 1]; TabPFN uses its probability 0.0) and -1.0 for MIMLNN,
# whose outputs regress onto +1/-1 targets. [Value: T03 Q14.]
NEGATIVE_SCORE = {"kdis": 0.0, "mimlnn": -1.0}


def degenerate_labels(Y_train):
    Y_train = np.asarray(Y_train)
    return np.flatnonzero(Y_train.sum(0) == 0).astype(np.int64)


def apply_degenerate(scores, bip, labels, negative):
    s, b = np.array(scores, dtype=np.float64), np.array(bip, dtype=np.uint8)
    s[:, labels] = negative
    b[:, labels] = 0
    return s, b


def score(Y, scores, bip):
    """Primary scoring (AMENDMENT.md A1). Hamming loss: miml_metrics.py on the
    library's native bipartition (§1.3: KDIS and MIMLNN produce bipartitions
    natively). The four ranking metrics: tie-neutral, i.e. the exact expected
    miml_metrics.py value when tied scores are ordered uniformly at random."""
    Y = np.asarray(Y, dtype=float)
    out = {"HammingLoss": float(HammingLoss(Y, np.asarray(bip, dtype=float)))}
    out.update(tn.ranking_four(Y, scores))
    return {m: out[m] for m in FIVE}


def score_prereg(Y, scores, bip):
    """The deposited scorer: miml_metrics.py as is (its own tie handling).
    Kept for the T03 checks (§6.8 specifies them on miml_metrics.py) and for
    the pre-registered sensitivity rows (AMENDMENT.md A1)."""
    Y = np.asarray(Y, dtype=float)
    return {"HammingLoss": float(HammingLoss(Y, np.asarray(bip, dtype=float))),
            "OneError": float(OneErrorLoss(Y, scores)),
            "Coverage": float(CoverageError(Y, scores)),
            "RankingLoss": float(RankingLoss(Y, scores)),
            "AveragePrecision": float(AveragePrecision(Y, scores))}


MEAN_TIE_ABS = 1e-12      # lead decision Q13: |dmean| <= 1e-12 is a tie


def tie_key(cand, sd):
    """Order inside a tie on the inner mean (§1.3 with the addendum): lower
    inner SD, method name, smaller k, distance name; MIMLNN smaller ratio,
    then smaller lambda."""
    return (sd, cand.method,
            cand.k if cand.k is not None else -1, cand.distance or "",
            cand.ratio if cand.ratio is not None else -1.0,
            cand.lam if cand.lam is not None else -1.0)


def select(inner_scores, metric):
    """inner_scores: {Candidate: [fold value, ...] or None (excluded)}.

    Fold values are already averaged over MIMLNN seeds; SD has ddof=1 over the
    inner folds. The best inner mean wins; every candidate whose mean is within
    MEAN_TIE_ABS (absolute) of the best is tied with it (Q13), and the tie is
    broken by tie_key. Returns (winner, table, decided_by); the table lists the
    tie group first, then the rest by mean.
    """
    hb = metric in HIGHER_BETTER
    rows = []
    for cand, vals in inner_scores.items():
        if vals is None:
            continue
        v = np.asarray(vals, dtype=float)
        mean = float(v.mean())
        sd = float(v.std(ddof=1)) if len(v) > 1 else 0.0
        rows.append((cand, mean, sd))
    if not rows:
        return None, [], "no eligible candidate"
    best = max(m for _, m, _ in rows) if hb else min(m for _, m, _ in rows)
    tied = sorted([r for r in rows if abs(r[1] - best) <= MEAN_TIE_ABS],
                  key=lambda r: tie_key(r[0], r[2]))
    rest = sorted([r for r in rows if abs(r[1] - best) > MEAN_TIE_ABS],
                  key=lambda r: (-r[1] if hb else r[1]) , )
    decided_by = "inner mean"
    if len(tied) > 1:
        a, b = tie_key(tied[0][0], tied[0][2]), tie_key(tied[1][0], tied[1][2])
        for level, name in enumerate(("inner SD", "method name", "k", "distance",
                                      "ratio", "lambda")):
            if a[level] != b[level]:
                decided_by = name
                break
    table = [{"method": c.method, "config": c.config, "inner_mean": m, "inner_sd": s_,
              "tied_on_mean": i < len(tied)}
             for i, (c, m, s_) in enumerate(tied + rest)]
    return tied[0][0], table, decided_by
