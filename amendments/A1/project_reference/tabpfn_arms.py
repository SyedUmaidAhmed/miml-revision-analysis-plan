"""TabPFN arms for revision R1 (tasks T04 and T07).

Binding spec: experiments/revision_r1/PREREGISTERED.md (tag prereg-v3-final).
This module adds new code paths only. It never changes the submitted configs in
experiments/run_foundation_baselines.py: bag features are built by that file's
own `pool` (so `bagmean`, `bagmax` and `multiview` are byte-identical to the
submission), and the two-fit path reproduces its `fit_predict` call order.

What lives here (pure library; the CLI is run_tabpfn_arms.py):
  - feature builders for every H1/H4 arm, incl. `bagmean_card` and `padded`
    (PREREGISTERED H4);
  - the instance-subsampling transform (H4);
  - split designs: canonical 10CV, repeated r x k (§1.2, §1.9), submitted5,
    and the H2-A rebuilt files and H2-B masks written by T02's h2a_rebuild.py
    and h2b_masks.py (format read as T02 defines it; see the T04 task file);
  - the per-unit pipeline: tr[:v] validation, fit_i z-scoring, optional
    PCA-500 on fit_i (§6.4), per-label binary relevance, Hamming thresholds on
    val_i (§1.3), one-fit or two-fit (§5);
  - storage under the §1.5 key with a no-overwrite writer, reuse checks and a
    per-run sha256 manifest;
  - per-fit timing, device, versions, constructor args, load average,
    concurrency, memory and an NVML energy hook (§6.2).

Nothing in this module runs on real data by itself. The CLI refuses real
datasets until the shared deposit_check.deposit_recorded() accepts line 8 (and every
amendment deposit line, AMENDMENT.md) of
PREREGISTERED.md.
"""
import os

# §6.1: thread pools pinned in every process. Must precede the numpy import.
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import hashlib  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import platform  # noqa: E402
import re  # noqa: E402
import resource  # noqa: E402
import socket  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
import uuid  # noqa: E402
from dataclasses import dataclass, field  # noqa: E402

import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.dirname(HERE))  # experiments/

import run_foundation_baselines as rfb  # noqa: E402
from miml_clam.metrics.miml_metrics import (  # noqa: E402
    AllFiveWithThresholds, optimize_thresholds)
import tie_neutral_metrics as tn  # noqa: E402  (AMENDMENT.md A1)
import torch  # noqa: E402  (already imported by miml_clam)

torch.set_num_threads(1)                 # §6.1, named explicitly in the plan

PREREG = os.path.join(HERE, "PREREGISTERED.md")
DATA_DIR = "/Users/umaidahmed/Desktop/Research/Research_Writer/ML_Papers/VIT_MIL/Code/MIML-SELFVIT"
_DATA_DIR_OVERRIDE = {"dir": os.environ.get("MIML_DATA_DIR")}


def set_data_dir(path):
    """Portability (review 1 #17): read every dataset file by basename from
    `path` instead of the macOS paths in the configs. None restores them."""
    _DATA_DIR_OVERRIDE["dir"] = path


def data_path(path):
    d = _DATA_DIR_OVERRIDE["dir"]
    return path if (d is None or path is None) else os.path.join(d, os.path.basename(path))
FIVE = ["HammingLoss", "OneError", "Coverage", "RankingLoss", "AveragePrecision"]

# --------------------------------------------------------------------------
# Plan constants (PREREGISTERED §0.1, §0.2, §1.1, §1.2, §1.4, §1.9)
# --------------------------------------------------------------------------
CONSTRUCTED = ("emotions", "yeast", "medical", "corel5k")
REPEATED_K = {"mscv2": 5, "letter_frost": 5, "letter_carroll": 5, "hja_birdsong": 10}
PRIMARY_SEEDS = (0, 1, 2, 3, 4)          # §1.2
RCV10_SEEDS = (10, 11, 12, 13, 14)       # §1.9
RCV10_DATASETS = ("scene", "reuters", "birdsong", "protein_haloarcula",
                  "protein_pyrococcus", "protein_geobacter", "protein_azotobacter",
                  "voc2012")
INSTANCE_PCA = {"voc2012": 128}          # §1.4, VOC2012 only
EXTRA_CONFIGS = {                        # not in run_baseline_experiments
    "hja_birdsong": {"data_path": os.path.join(DATA_DIR, "hja_birdsong.mat"),
                     "dataset_format": "dd"},
    "voc2012": {"data_path": os.path.join(DATA_DIR, "voc2012.mat"),
                "cv_mat_path": os.path.join(DATA_DIR, "voc2012_10CV.mat"),
                "bag_key": "bags", "label_key": "labels"},
}

VERSIONS = ("original", "rebuilt", "purged", "dedup", "rcv10", "submitted5")
ARMS = ("tabpfn_bagmean", "tabpfn_bagmax", "tabpfn_multiview",
        "tabpfn_bagmean_card", "tabpfn_padded")
WIDTHS = ("native", "pca")              # requested switch; stored token native | pca<d'>
WIDTH_TOKEN_RE = re.compile(r"^(native|pca[1-9][0-9]*)$")
DEVICE_TOKENS = {"cuda": "g", "mps": "mps", "cpu": "cpu"}  # cpu: not a plan device
SUB_FRACTIONS = {"f0.25": 0.25, "f0.5": 0.5, "f0.75": 0.75, "single": None}
CONDITION_RE = re.compile(
    r"^(main|leak|control-s[0-2]|padded-s[0-2]|sub-(f0\.25|f0\.5|f0\.75|single)-s[0-2]"
    r"|verify-2fit|verify-1fit)$")
PCA_DIM = 500                            # §6.4


# --------------------------------------------------------------------------
# Features
# --------------------------------------------------------------------------
def _bagmean_card(b):
    """Bag mean plus cardinality as one scalar (H4). Same dtype rule as
    rfb._multiview, whose last column is also len(b)."""
    b = np.asarray(b)
    return np.concatenate([b.mean(0), [len(b)]])


def build_features(bags, arm):
    """Bag-level feature matrix for one arm. `tabpfn_padded` returns the plain
    multiview matrix; the permutation is applied per fold by `padded_permute`."""
    if arm == "tabpfn_bagmean":
        return rfb.pool(bags, "mean")
    if arm == "tabpfn_bagmax":
        return rfb.pool(bags, "max")
    if arm in ("tabpfn_multiview", "tabpfn_padded"):
        return rfb.pool(bags, "multiview")
    if arm == "tabpfn_bagmean_card":
        return np.stack([_bagmean_card(b) for b in bags])
    raise ValueError(f"unknown arm {arm}")


def feature_dim(arm, d):
    """Bag-level width of an arm for instance dimension d."""
    return {"tabpfn_bagmean": d, "tabpfn_bagmax": d, "tabpfn_bagmean_card": d + 1,
            "tabpfn_multiview": 6 * d + 1, "tabpfn_padded": 6 * d + 1}[arm]


def padded_permute(X_tr, X_te, d, seed):
    """Width-matched control (H4 `tabpfn_padded`).

    Columns [0, d) (the bag-mean block) are kept. Every other column of the
    6d+1 multiview matrix (max, min, SD, q25, q75 blocks and the cardinality
    column) is permuted independently across the outer-training rows and,
    separately, across the outer-test rows, so no value moves between folds.

    RNG protocol (implementation choice, fixed before any run): a fresh
    numpy.random.default_rng(seed) per outer fold; first one permutation per
    padded column of the training rows in ascending column order, then one per
    padded column of the test rows in ascending column order.
    """
    if X_tr.shape[1] != 6 * d + 1 or X_te.shape[1] != 6 * d + 1:
        raise ValueError("padded_permute expects the 6d+1 multiview matrix")
    rng = np.random.default_rng(seed)
    Xtr, Xte = X_tr.copy(), X_te.copy()
    for j in range(d, Xtr.shape[1]):
        Xtr[:, j] = X_tr[rng.permutation(len(X_tr)), j]
    for j in range(d, Xte.shape[1]):
        Xte[:, j] = X_te[rng.permutation(len(X_te)), j]
    return Xtr, Xte


def subsample_indices(ids, sizes, frac_token, seed):
    """Instance subsets for the H4 subsampling curve.

    Keeps ceil(f * n_i) instances (at least 1) for f in {0.25, 0.5, 0.75}, or
    exactly 1 for `single`. One numpy.random.default_rng(seed) per call; bags
    are visited in ascending bag id over the whole universe passed in (all bags
    of the dataset version, training and test alike), so a bag gets the same
    subset in every fold and in both the multiview and bag-mean arms.
    Returns {bag_id: sorted instance positions}.
    """
    frac = SUB_FRACTIONS[frac_token]
    rng = np.random.default_rng(seed)
    out = {}
    order = np.argsort(np.asarray(ids), kind="stable")
    for k in order:
        n = int(sizes[k])
        m = 1 if frac is None else max(1, math.ceil(frac * n))
        out[int(ids[k])] = np.sort(rng.choice(n, size=m, replace=False))
    return out


def parse_condition(cond):
    if not CONDITION_RE.match(cond):
        raise ValueError(f"condition token {cond!r} not in PREREGISTERED §1.5")
    if cond.startswith("padded-"):
        return {"kind": "padded", "seed": int(cond[-1])}
    if cond.startswith("sub-"):
        _, frac, s = cond.split("-")
        return {"kind": "sub", "frac": frac, "seed": int(s[1:])}
    if cond.startswith("control-"):
        return {"kind": "h2b", "seed": int(cond[-1])}
    if cond == "leak":
        return {"kind": "h2b", "seed": None}
    if cond.startswith("verify-"):
        return {"kind": "verify", "fit_mode": "two" if cond == "verify-2fit" else "one"}
    return {"kind": "main"}


def check_arm_condition(arm, version, cond):
    c = parse_condition(cond)
    if c["kind"] == "padded" and arm != "tabpfn_padded":
        raise ValueError("padded-sX conditions belong to tabpfn_padded only")
    if arm == "tabpfn_padded" and c["kind"] != "padded":
        raise ValueError("tabpfn_padded needs a padded-sX condition")
    if c["kind"] == "sub" and arm not in ("tabpfn_multiview", "tabpfn_bagmean"):
        raise ValueError("subsampling conditions belong to multiview and bag-mean")
    if (c["kind"] == "h2b") != (version == "purged"):
        raise ValueError("leak/control-sX conditions go with version `purged` only")
    if c["kind"] == "verify" and arm != "tabpfn_bagmean":
        raise ValueError("§5 verification uses tabpfn_bagmean only")
    return c


# --------------------------------------------------------------------------
# Data versions and split designs
# --------------------------------------------------------------------------
@dataclass
class Split:
    repeat: int
    fold: int
    ids_tr: np.ndarray          # bag ids, in the §1.3 order (tr[:v] = val_i)
    ids_te: np.ndarray
    bags: dict                  # bag id -> (n_i, d) array, for this split
    Y: dict                     # bag id -> (L,) int label vector
    universe: np.ndarray = None  # bag ids the subsampling draw runs over
    info: dict = field(default_factory=dict)


@dataclass
class Version:
    dataset: str
    version: str
    design: str
    splits: list
    L: int
    d: int
    sizes_constant: bool
    n_bags: int = None          # bags of the original file (for the d' arithmetic)


def load_original(name):
    """(bags, Y, cfg) exactly as the submission loads them."""
    from miml_clam.data import MIMLDatasetCV, MIMLDatasetDD
    # Same construction as rfb.load; paths pass through data_path (#17).
    cfg = dict(EXTRA_CONFIGS[name] if name in EXTRA_CONFIGS else rfb.rbe.DATASET_CONFIGS[name])
    for k in ("data_path", "cv_mat_path"):
        if cfg.get(k):
            cfg[k] = data_path(cfg[k])
    ds = (MIMLDatasetDD(mat_path=cfg["data_path"]) if cfg.get("dataset_format") == "dd"
          else MIMLDatasetCV(mat_path=cfg["data_path"], bag_key=cfg.get("bag_key", "bags"),
                             label_key=cfg.get("label_key", "labels")))
    bags = [b.numpy() if hasattr(b, "numpy") else np.asarray(b) for b in ds.bags]
    Y = (np.stack([l.numpy() if hasattr(l, "numpy") else np.asarray(l)
                   for l in ds.labels]) > 0).astype(int)
    return bags, Y, cfg, ds


def repeated_splits(n, k, seeds):
    """§1.2/§1.9: permutation from default_rng(seed); fold j = j-th of k
    contiguous blocks (sizes differ by at most 1); tr = the permutation with
    the test block removed, in permutation order."""
    out = []
    for r, s in enumerate(seeds):
        perm = np.random.default_rng(s).permutation(n)
        blocks = np.array_split(perm, k)
        for j in range(k):
            tr = np.concatenate([blocks[i] for i in range(k) if i != j])
            out.append((r, j, tr, blocks[j]))
    return out


def _plain_splits(bags, Y, triples):
    ids = np.arange(len(bags))
    bd = {i: bags[i] for i in ids}
    yd = {i: Y[i] for i in ids}
    return [Split(r, f, np.asarray(tr, dtype=np.int64), np.asarray(te, dtype=np.int64),
                  bd, yd, universe=ids) for r, f, tr, te in triples]


def splits_from_bags(dataset, version, bags, Y, cfg=None, ds=None, num_folds=None):
    """Split designs over an in-memory bag list (real data or synthetic)."""
    if version == "original":
        if dataset in REPEATED_K:
            triples = repeated_splits(len(bags), REPEATED_K[dataset], PRIMARY_SEEDS)
            design = f"repeated r={len(PRIMARY_SEEDS)} k={REPEATED_K[dataset]} seeds {PRIMARY_SEEDS}"
        else:
            sp = rfb.splits_for(ds, cfg, None)
            triples = [(0, f, tr, te) for f, (tr, te) in enumerate(sp)]
            design = "canonical 10CV (get_cv_splits)"
    elif version == "rcv10":
        if dataset not in RCV10_DATASETS:
            raise ValueError(f"§1.9 does not include {dataset}")
        triples = repeated_splits(len(bags), 10, RCV10_SEEDS)
        design = f"repeated r=5 k=10 seeds {RCV10_SEEDS}"
    elif version == "submitted5":
        if dataset not in ("mscv2", "letter_frost", "letter_carroll"):
            raise ValueError("submitted5 exists for MSRC v2 and the Letter sets only")
        sp = rfb.splits_for(ds, cfg, None)
        triples = [(0, f, tr, te) for f, (tr, te) in enumerate(sp)]
        design = "submitted seed-42 single 5-fold (splits_for)"
    else:
        raise ValueError(f"version {version} needs a file input (rebuilt/purged)")
    if num_folds is not None:
        triples = triples[:num_folds]
    sizes = np.array([len(b) for b in bags])
    return Version(dataset, version, design, _plain_splits(bags, Y, triples),
                   Y.shape[1], bags[0].shape[1], bool((sizes == sizes[0]).all()), len(bags))


CONSTRUCTIONS_ROOT = os.path.join(PROJECT, "results", "revision_r1", "constructions")  # T02 OUT_ROOT


def load_rebuilt(dataset, X_source, root=CONSTRUCTIONS_ROOT, folds=range(10),
                 dtype=np.float32):
    """H2-A input, T02 format: <root>/<dataset>/rebuilt/r0_f<f>.npz with
    train_bag_ids / train_members / Y_train / test_bag_ids / test_members /
    Y_test (h2a_rebuild.build_split). Instances are source-row indices into
    X_source (raw rows, h2_common.source_rows); bags are materialised as
    X_source[members] like h2a_rebuild.materialise, then cast to `dtype`
    (float32 = how the submission loader holds every other version; T04 Q4).
    Training bags must be in ascending canonical bag index (§1.3)."""
    splits, sizes = [], []
    for f in folds:
        p = os.path.join(root, dataset, "rebuilt", f"r0_f{f}.npz")
        z = np.load(p, allow_pickle=False)
        need = ("split", "train_bag_ids", "train_members", "Y_train", "test_bag_ids",
                "test_members", "Y_test")
        for k in need:
            if k not in z:
                raise ValueError(f"{p}: missing key {k}")
        if int(z["split"]) != f:
            raise ValueError(f"{p}: split field {int(z['split'])} != {f}")
        tr, te = z["train_bag_ids"].astype(np.int64), z["test_bag_ids"].astype(np.int64)
        if np.any(np.diff(tr) <= 0):
            raise ValueError(f"{p}: training bags not in ascending canonical index (§1.3)")
        if np.intersect1d(tr, te).size:
            raise ValueError(f"{p}: a bag id is in both training and test")
        bags, yd = {}, {}
        for ids, mem, Ym in ((tr, z["train_members"], z["Y_train"]),
                             (te, z["test_members"], z["Y_test"])):
            if len(ids) != len(mem) or len(ids) != len(Ym):
                raise ValueError(f"{p}: ids, members and labels differ in length")
            for i, m, y in zip(ids, mem, Ym):
                bags[int(i)] = np.asarray(X_source[np.asarray(m)], dtype=dtype)
                yd[int(i)] = (np.asarray(y) > 0).astype(int)
                sizes.append(len(m))
        splits.append(Split(0, f, tr, te, bags, yd, universe=np.sort(np.concatenate([tr, te])),
                            info={"source": p, "sha256": sha256_file(p)}))
    L = len(next(iter(splits[0].Y.values())))
    return Version(dataset, "rebuilt", "H2-A per-split rebuild on canonical folds",
                   splits, L, X_source.shape[1], len(set(sizes)) == 1)


def load_purged(dataset, condition, bags, Y, cfg, ds, root=CONSTRUCTIONS_ROOT, folds=None):
    """H2-B input, T02 format: <root>/<dataset>/purged/<condition>/r0_f<f>.npz
    with train_bag_ids, bag_offsets, keep (flat over the training bags'
    instances), surviving_bag_ids, test_bag_ids (h2b_masks.build_dataset).
    Applied to the ORIGINAL bags as the submission loads them. Test bags are
    unchanged; order = canonical get_cv_splits order with emptied bags removed
    (§1.3); every field is checked against this loader's own canonical split."""
    sp = rfb.splits_for(ds, cfg, None)
    out = []
    for f, (tr, te) in enumerate(sp):
        if folds is not None and f not in folds:
            continue
        p = os.path.join(root, dataset, "purged", condition, f"r0_f{f}.npz")
        z = np.load(p, allow_pickle=False)
        if int(z["fold"]) != f or str(z["condition"]) != condition:
            raise ValueError(f"{p}: fold/condition fields do not match the path")
        ztr, zte = z["train_bag_ids"].astype(np.int64), z["test_bag_ids"].astype(np.int64)
        if not (np.array_equal(ztr, np.asarray(tr)) and np.array_equal(zte, np.asarray(te))):
            raise ValueError(f"{p}: train/test bag ids differ from the canonical split")
        off, keep = z["bag_offsets"].astype(np.int64), z["keep"].astype(bool)
        if not np.array_equal(np.diff(off), [len(bags[i]) for i in tr]) or off[-1] != len(keep):
            raise ValueError(f"{p}: mask not aligned with the loaded {dataset} bags")
        bd = {int(i): bags[i] for i in te}
        tr_kept = []
        for b, i in enumerate(tr):
            m = keep[off[b]:off[b + 1]]
            if m.any():
                bd[int(i)] = bags[i][m]
                tr_kept.append(int(i))
        if not np.array_equal(tr_kept, z["surviving_bag_ids"]):
            raise ValueError(f"{p}: surviving_bag_ids disagree with the mask")
        yd = {i: Y[i] for i in bd}
        out.append(Split(0, f, np.asarray(tr_kept, dtype=np.int64),
                         np.asarray(te, dtype=np.int64), bd, yd, universe=None,
                         info={"source": p, "sha256": sha256_file(p),
                               "train_bags_dropped": int(len(tr) - len(tr_kept)),
                               "train_rows_kept": int(keep.sum())}))
    return Version(dataset, "purged", f"H2-B mask `{condition}` on canonical folds",
                   out, Y.shape[1], bags[0].shape[1], False, len(bags))


def apply_instance_pca(split, n_components, *, svd_solver="randomized", random_state=0):
    """§1.4 (VOC2012 only): PCA on the instances of the outer training fold,
    applied to that fold's training and test bags."""
    from sklearn.decomposition import PCA
    tr_inst = np.vstack([split.bags[i] for i in split.ids_tr])
    pca = PCA(n_components=n_components, svd_solver=svd_solver,
              random_state=random_state).fit(tr_inst)
    ids = np.concatenate([split.ids_tr, split.ids_te])
    bags = {int(i): pca.transform(split.bags[int(i)]) for i in ids}
    if split.universe is not None:
        for i in split.universe:
            if int(i) not in bags:
                bags[int(i)] = pca.transform(split.bags[int(i)])
    return Split(split.repeat, split.fold, split.ids_tr, split.ids_te, bags, split.Y,
                 split.universe, dict(split.info, instance_pca=n_components))


def apply_subsample(split, frac_token, seed):
    if split.universe is None:
        raise ValueError("subsampling needs a bag universe (not defined for H2-B)")
    uni = np.asarray(split.universe)
    sizes = np.array([len(split.bags[int(i)]) for i in uni])
    sel = subsample_indices(uni, sizes, frac_token, seed)
    bags = {i: split.bags[i][sel[i]] for i in sel}
    return Split(split.repeat, split.fold, split.ids_tr, split.ids_te, bags, split.Y,
                 split.universe, dict(split.info, subsample=f"{frac_token}-s{seed}"))


# --------------------------------------------------------------------------
# Environment, timing, energy
# --------------------------------------------------------------------------
def sha256_file(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(chunk), b""):
            h.update(blk)
    return h.hexdigest()


def code_sha256():
    return {os.path.basename(p): sha256_file(p) for p in
            (os.path.abspath(__file__), os.path.abspath(rfb.__file__))}


def versions():
    out = {"python": platform.python_version(), "platform": platform.platform(),
           "torch_num_threads": torch.get_num_threads(),
           "thread_env": {k: os.environ.get(k) for k in
                          ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")}}
    for mod in ("numpy", "scipy", "sklearn", "torch", "tabpfn"):
        try:
            m = __import__(mod)
            out[mod] = getattr(m, "__version__", "unknown")
        except Exception as exc:  # pragma: no cover
            out[mod] = f"unavailable: {type(exc).__name__}"
    return out


def cpu_brand():
    try:
        return subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"],
                              capture_output=True, text=True, timeout=5).stdout.strip()
    except Exception:
        return platform.processor()


def device_string(device):
    import torch
    if device == "cuda":
        p = torch.cuda.get_device_properties(0)
        return (f"cuda:{torch.cuda.get_device_name(0)}; mem={p.total_memory}; "
                f"torch.cuda={torch.version.cuda}")
    if device == "mps":
        return f"mps:{cpu_brand()}"
    return f"cpu:{cpu_brand()}"


_CKPT = {}


def tabpfn_checkpoint():
    """Resolved classifier checkpoint path and sha256 (once per process)."""
    if not _CKPT:
        try:
            from tabpfn.model_loading import resolve_model_path
            path = resolve_model_path(None, "classifier")[0]
            path = str(path)
            _CKPT.update(path=path, sha256=sha256_file(path) if os.path.exists(path) else None)
        except Exception as exc:
            _CKPT.update(path=None, error=f"{type(exc).__name__}: {exc}")
    return dict(_CKPT)


class EnergyMeter:
    """NVML total-energy counter on CUDA (§6.2); a recorded no-op elsewhere.

    On CUDA a missing or failing NVML is an error (review 1 #14) unless
    allow_missing is set, in which case every record says "failed" with the
    reason (never a silent "not measured")."""

    def __init__(self, device, allow_missing=False):
        self.device, self.h, self.e0, self.reason = device, None, None, None
        self.allow_missing = allow_missing
        if device != "cuda":
            self.reason = "not measured (no NVML on this device)"
            return
        try:
            import pynvml
            pynvml.nvmlInit()
            self.nv = pynvml
            self.h = pynvml.nvmlDeviceGetHandleByIndex(0)
            self.nv.nvmlDeviceGetTotalEnergyConsumption(self.h)
        except Exception as exc:
            self._fail(f"NVML unavailable: {type(exc).__name__}: {exc}")

    def _fail(self, why):
        if not self.allow_missing:
            raise RuntimeError(f"energy counter required on CUDA (§6.2): {why}; "
                               "pass --allow-no-nvml to record 'failed' instead")
        self.h, self.reason = None, f"failed ({why})"

    def start(self):
        if self.h is not None:
            try:
                self.e0 = self.nv.nvmlDeviceGetTotalEnergyConsumption(self.h)
            except Exception as exc:
                self._fail(f"read failed: {type(exc).__name__}: {exc}")

    def stop(self):
        if self.h is None or self.e0 is None:
            return {"energy_mJ": None, "energy_note": self.reason,
                    "energy_status": "failed" if (self.reason or "").startswith("failed")
                    else "not measured"}
        try:
            e1 = self.nv.nvmlDeviceGetTotalEnergyConsumption(self.h)
        except Exception as exc:
            self._fail(f"read failed: {type(exc).__name__}: {exc}")
            return {"energy_mJ": None, "energy_note": self.reason, "energy_status": "failed"}
        return {"energy_mJ": int(e1 - self.e0), "energy_note": "NVML total-energy counter",
                "energy_status": "measured"}


class DeviceMemory:
    def __init__(self, device):
        self.device, self.peak = device, 0

    def reset(self):
        self.peak = 0
        if self.device == "cuda":
            import torch
            torch.cuda.reset_peak_memory_stats()

    def sample(self):
        if self.device == "mps":
            import torch
            self.peak = max(self.peak, int(torch.mps.driver_allocated_memory()))

    def report(self):
        if self.device == "cuda":
            import torch
            return {"device_peak_bytes": int(torch.cuda.max_memory_allocated()),
                    "device_peak_kind": "torch.cuda.max_memory_allocated"}
        if self.device == "mps":
            return {"device_peak_bytes": self.peak,
                    "device_peak_kind": "max sampled torch.mps.driver_allocated_memory"}
        return {"device_peak_bytes": None, "device_peak_kind": "not applicable"}


def peak_rss_bytes():
    r = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(r if sys.platform == "darwin" else r * 1024)


def cpu_seconds():
    r = resource.getrusage(resource.RUSAGE_SELF)
    return r.ru_utime + r.ru_stime


# --------------------------------------------------------------------------
# Classifier and per-label fitting
# --------------------------------------------------------------------------
TABPFN_KW = {"n_estimators": 8, "random_state": 0, "ignore_pretraining_limits": True}  # H4


TABPFN_VERSION = "2.2.1"
TABPFN_CKPT = "tabpfn-v2-classifier-finetuned-zk73skhh.ckpt"
TABPFN_CKPT_SHA256 = "cf8c519c01eaf1613ee91239006d57b1c806ff5f23ac1aeb1315ba1015210e49"


def check_tabpfn_version():
    """Refuse any TabPFN other than the pinned, ungated v2.2.1 of .tabpfn_env
    (CLAUDE.md: ./.venv carries the licence-gated 8.x and must not be used)."""
    import tabpfn
    ver = getattr(tabpfn, "__version__", None)
    if ver != TABPFN_VERSION:
        raise RuntimeError(f"TabPFN {ver} at {tabpfn.__file__}: runs and tests need "
                           f"tabpfn=={TABPFN_VERSION} from .tabpfn_env "
                           "(.tabpfn_env/bin/python ...)")
    return ver


def check_tabpfn_env():
    """Pinned version and pinned checkpoint (name and sha256), before any fit."""
    ver = check_tabpfn_version()
    ck = tabpfn_checkpoint()
    if not ck.get("path") or os.path.basename(ck["path"]) != TABPFN_CKPT:
        raise RuntimeError(f"TabPFN checkpoint {ck} is not {TABPFN_CKPT}")
    if ck.get("sha256") != TABPFN_CKPT_SHA256:      # file must exist and match (#7)
        raise RuntimeError(f"TabPFN checkpoint sha256 {ck.get('sha256')} != pinned "
                           f"{TABPFN_CKPT_SHA256} ({ck['path']})")
    return ver, ck


def make_factory(model, device):
    """Returns (factory, constructor kwargs). `logreg` exists for tests only."""
    if model == "tabpfn":
        check_tabpfn_env()
        torch.set_num_threads(1)
        from tabpfn import TabPFNClassifier
        kw = dict(device=device, **TABPFN_KW)
        return (lambda: TabPFNClassifier(**kw)), kw
    if model == "logreg":
        from sklearn.linear_model import LogisticRegression
        kw = {"max_iter": 1000}
        return (lambda: LogisticRegression(**kw)), kw
    raise ValueError(model)


def _proba1(clf, X):
    p = clf.predict_proba(X)
    return p[:, list(clf.classes_).index(1)] if 1 in clf.classes_ else 0.0


def fit_predict_labels(factory, Xfit, Yfit, Xval, Xte, fit_mode, labels=None, mem=None):
    """Per-label binary relevance with timings.

    fit_mode "two": the submission's order -- one fit per label for the
    validation pass over all labels, then a fresh fit per label for the test
    pass (run_foundation_baselines.main calls fit_predict twice).
    fit_mode "one": one fit per label, then predict_proba on val and on test as
    two separate calls (batch composition kept identical to "two").
    Constant labels in Yfit are predicted constant (as fit_predict does).
    """
    L = Yfit.shape[1]
    labels = range(L) if labels is None else labels
    pv, pt = np.zeros((len(Xval), L)), np.zeros((len(Xte), L))
    recs = {l: {"label": int(l), "constant": False, "fits": []} for l in labels}
    const = {l for l in labels if Yfit[:, l].min() == Yfit[:, l].max()}
    for l in const:
        pv[:, l] = pt[:, l] = float(Yfit[0, l])
        recs[l]["constant"] = True

    def _fit(l):
        clf = factory()
        t0 = time.perf_counter()
        clf.fit(Xfit, Yfit[:, l])
        dt = time.perf_counter() - t0
        if mem is not None:
            mem.sample()
        return clf, dt

    def _pred(clf, X):
        t0 = time.perf_counter()
        p = _proba1(clf, X)
        dt = time.perf_counter() - t0
        if mem is not None:
            mem.sample()
        return p, dt

    fitted = [l for l in labels if l not in const]
    if fit_mode == "two":
        for l in fitted:
            clf, tf = _fit(l)
            pv[:, l], tp = _pred(clf, Xval)
            recs[l]["fits"].append({"pass": "val", "fit_s": tf, "predict_val_s": tp})
        for l in fitted:
            clf, tf = _fit(l)
            pt[:, l], tp = _pred(clf, Xte)
            recs[l]["fits"].append({"pass": "test", "fit_s": tf, "predict_test_s": tp})
    elif fit_mode == "one":
        for l in fitted:
            clf, tf = _fit(l)
            pv[:, l], tv = _pred(clf, Xval)
            pt[:, l], tt = _pred(clf, Xte)
            recs[l]["fits"].append({"pass": "val+test", "fit_s": tf,
                                    "predict_val_s": tv, "predict_test_s": tt})
    else:
        raise ValueError(fit_mode)
    return pv, pt, [recs[l] for l in labels]


PCA_CFG = {"order": "zscore_then_pca", "svd_solver": "full", "random_state": 0}  # addendum Q1


def n_fit_of(n_train):
    """|fit_i| for an outer training fold of n_train bags (§1.3)."""
    return n_train - max(1, int(0.2 * n_train))


def pca_components(min_n_fit, d):
    """d' = min(500, min n_rows(fit_i) - 1, d) (DECISIONS.md "d' scope")."""
    return min(PCA_DIM, min_n_fit - 1, d)


PLAN_DATASETS = ("scene", "reuters", "mscv2", "letter_frost", "letter_carroll", "birdsong",
                 "hja_birdsong", "voc2012", "protein_haloarcula", "protein_pyrococcus",
                 "protein_geobacter", "protein_azotobacter", *CONSTRUCTED)


def dataset_train_sizes(dataset, n_bags=None, constructions_root=CONSTRUCTIONS_ROOT):
    """Outer-training sizes that fix d' for a dataset (DECISIONS.md "d' scope"):
    the folds of its H1 version and, for the §1.9 datasets, of the rcv10 design
    and its canonical sixth run. Fold-size arithmetic only; the four
    constructed sets read the sizes of T02's rebuilt split files (their H1
    version), which depend on the duplicate-row rule."""
    if dataset in CONSTRUCTED:
        return [int(len(np.load(os.path.join(constructions_root, dataset, "rebuilt",
                                             f"r0_f{f}.npz"))["train_bag_ids"]))
                for f in range(10)]
    if n_bags is None:
        raise ValueError(f"{dataset}: n_bags needed for the d' arithmetic")
    if dataset in REPEATED_K:               # §1.2: k contiguous blocks, sizes differ by <= 1
        sizes = [n_bags - len(b) for b in np.array_split(np.arange(n_bags), REPEATED_K[dataset])]
    else:                                   # canonical 10CV: blocks of n // 10 (§1.1)
        sizes = [n_bags - n_bags // 10]
    if dataset in RCV10_DATASETS:           # §1.9 repeated 10-fold
        sizes += [n_bags - len(b) for b in np.array_split(np.arange(n_bags), 10)]
    return sizes


def width_plan(spec_width, version, d_feat, constructions_root=CONSTRUCTIONS_ROOT):
    """(width token, d' or None) for a unit.

    DECISIONS.md "d' scope": one d' per dataset across all of its versions,
    d' = min(500, d, min over the folds of the H1 version and the §1.9 rcv10
    version (with its canonical sixth run) of n_rows(fit_i) - 1). Token
    `pca<d'>`; `native` when the switch is off or d' = d (d <= 500, plan line
    130). Every fold of the version being run must satisfy n_fit - 1 >= d',
    else the run stops. Datasets outside the plan (synthetic tests) use the
    folds of the version itself."""
    if spec_width not in WIDTHS:
        raise ValueError(f"width must be native or pca, not {spec_width!r}")
    if spec_width == "native" or d_feat <= PCA_DIM:
        return "native", None
    if version.dataset in PLAN_DATASETS:
        sizes = dataset_train_sizes(version.dataset, version.n_bags, constructions_root)
    else:
        sizes = [len(s.ids_tr) for s in version.splits]
    k = pca_components(min(n_fit_of(t) for t in sizes), d_feat)
    if k == d_feat:
        return "native", None
    for s in version.splits:
        if n_fit_of(len(s.ids_tr)) - 1 < k:
            raise RuntimeError(f"{version.dataset}/{version.version} r{s.repeat} f{s.fold}: "
                               f"n_fit - 1 = {n_fit_of(len(s.ids_tr)) - 1} < d' = {k}; stop "
                               "(DECISIONS.md d' scope)")
    return f"pca{k}", k


def standardise_and_reduce(X_tr, X_te, v, n_components=None):
    """fit_i z-scoring (§1.4, as submitted) and, when n_components is given,
    PCA fitted on fit_i rows only (§6.4).

    Pre-deposit addendum: z-score with fit_i statistics, then
    sklearn PCA(n_components=d', svd_solver="full", random_state=0) fit on the
    z-scored fit_i rows, applied to val_i and the test fold; no re-scaling
    after PCA. d' is fixed per dataset by `width_plan`.
    Returns (Xtr, Xte, info).
    """
    mu, sd = X_tr[v:].mean(0), X_tr[v:].std(0) + 1e-8
    a, b = (X_tr - mu) / sd, (X_te - mu) / sd
    d = int(X_tr.shape[1])
    # plan §1.4 footnote: dtype of the bag-level matrix as built (before z-scoring)
    info = {"feature_dim": d, "pca": None, "dtype": str(X_tr.dtype)}
    if n_components is None:
        info.update(width_token="native", feature_dim_used=d)
        return a, b, info
    from sklearn.decomposition import PCA
    n_fit = len(X_tr) - v
    if n_components > min(n_fit - 1, d):
        raise ValueError(f"d'={n_components} exceeds min(n_fit - 1 = {n_fit - 1}, d={d})")
    pca = PCA(n_components=n_components, svd_solver=PCA_CFG["svd_solver"],
              random_state=PCA_CFG["random_state"]).fit(a[v:])
    a, b = pca.transform(a), pca.transform(b)
    info.update(width_token=f"pca{n_components}", feature_dim_used=n_components,
                pca={**PCA_CFG, "n_components": n_components, "n_fit": n_fit,
                     "explained_variance_ratio_sum": float(pca.explained_variance_ratio_.sum())})
    return a, b, info


# --------------------------------------------------------------------------
# Storage (§1.5)
# --------------------------------------------------------------------------
def check_tokens(dataset, version, arm, width, condition, devtok):
    if not re.match(r"^[a-z0-9_]+$", dataset):
        raise ValueError(f"bad dataset token {dataset!r}")
    if version not in VERSIONS:
        raise ValueError(f"bad version token {version!r}")
    if arm not in ARMS:
        raise ValueError(f"bad arm token {arm!r}")
    if not WIDTH_TOKEN_RE.match(width):
        raise ValueError(f"bad width token {width!r}")
    parse_condition(condition)
    if devtok not in DEVICE_TOKENS.values():
        raise ValueError(f"bad device token {devtok!r}")


def unit_dir(root, dataset, version, arm, width, condition, devtok):
    """results/revision_r1/predictions/<dataset>/<version>/<arm>/<width>/<condition>+<dev>/"""
    check_tokens(dataset, version, arm, width, condition, devtok)
    return os.path.join(root, "predictions", dataset, version, arm, width,
                        f"{condition}+{devtok}")


def fold_stem(repeat, fold):
    return f"r{repeat}_f{fold}"


def write_noclobber(path, write_fn):
    """Write via a private temp file, then hard-link into place. os.link fails
    if `path` exists, so an existing file is never replaced (lesson 9)."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.lexists(path):
        raise FileExistsError(path)
    tmp = os.path.join(os.path.dirname(path),
                       f".tmp.{os.getpid()}.{uuid.uuid4().hex}.{os.path.basename(path)}")
    try:
        write_fn(tmp)
        os.link(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    return sha256_file(path)


def save_npz_noclobber(path, **arrays):
    def w(tmp):
        with open(tmp, "wb") as fh:
            np.savez(fh, **arrays)
    return write_noclobber(path, w)


def save_json_noclobber(path, obj):
    def w(tmp):
        with open(tmp, "w") as fh:
            json.dump(obj, fh, indent=2, sort_keys=True, default=_json_default)
    return write_noclobber(path, w)


def _json_default(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, np.bool_):
        return bool(o)
    return str(o)


class Manifest:
    """One JSONL file per run (one writer per file, lesson 9)."""

    def __init__(self, root, run_id, header):
        self.path = os.path.join(root, "manifests", f"{run_id}.jsonl")
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
        os.close(fd)
        self.add({"type": "run", **header})

    def add(self, rec):
        with open(self.path, "a") as fh:
            fh.write(json.dumps(rec, sort_keys=True, default=_json_default) + "\n")


class DeviceLock:
    """§6.1: one TabPFN process per device at a time."""

    def __init__(self, root, devtok):
        self.path = os.path.join(root, "locks", f"tabpfn_{devtok}.lock")

    def __enter__(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        try:
            fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
        except FileExistsError:
            raise RuntimeError(f"another TabPFN process holds {self.path} "
                               "(§6.1: one per device); remove it only if that process is dead")
        os.write(fd, json.dumps({"pid": os.getpid(), "host": socket.gethostname(),
                                 "start": time.time()}).encode())
        os.close(fd)
        return self

    def __exit__(self, *exc):
        if os.path.exists(self.path):
            os.unlink(self.path)


def new_run_id():
    return time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()) + f"_{socket.gethostname()}_{os.getpid()}"


# --------------------------------------------------------------------------
# One unit = (dataset, version, arm, width, condition, device) over its folds
# --------------------------------------------------------------------------
@dataclass
class UnitSpec:
    dataset: str
    version: str
    arm: str
    width: str
    condition: str
    device: str = "cpu"
    fit_mode: str = "two"
    model: str = "tabpfn"
    procedures: tuple = ()
    concurrency: int = 1
    constructions_root: str = None
    allow_no_nvml: bool = False

    @property
    def devtok(self):
        return DEVICE_TOKENS[self.device]


def effective_fit_mode(spec):
    """verify-2fit / verify-1fit fix the mode; otherwise the spec's (review 1 #2)."""
    c = parse_condition(spec.condition)
    return c["fit_mode"] if c["kind"] == "verify" else spec.fit_mode


def _identity(spec, version, kw, feature_dim, width_token, split=None):
    ident = {"dataset": spec.dataset, "version": spec.version, "arm": spec.arm,
             "width": width_token, "condition": spec.condition, "device_token": spec.devtok,
             "fit_mode": effective_fit_mode(spec), "model": spec.model,
             "constructor": {k: v for k, v in kw.items()}, "feature_dim": feature_dim,
             "design": version.design,
             "pca_cfg": PCA_CFG if width_token.startswith("pca") else None}
    if spec.version in ("rebuilt", "purged") and split is not None:
        # review 1 #4: a regenerated T02 construction is never silently reused
        ident["construction"] = {"source": os.path.basename(split.info.get("source", "")),
                                 "sha256": split.info.get("sha256")}
    return ident


def prepare_split(spec, split):
    """Version-level transforms in a fixed order: instance PCA (VOC2012),
    then subsampling (H4). Order is open question Q3 in the T04 task file."""
    if spec.dataset in INSTANCE_PCA:
        split = apply_instance_pca(split, INSTANCE_PCA[spec.dataset])
    c = parse_condition(spec.condition)
    if c["kind"] == "sub":
        split = apply_subsample(split, c["frac"], c["seed"])
    return split


def run_split(spec, version, split, factory, kw, labels=None, mem=None, pca_k=None):
    """Features -> padded permutation -> tr[:v] / fit z-score -> PCA -> TabPFN.
    Returns everything a stored unit needs."""
    t_pre0 = time.perf_counter()
    split = prepare_split(spec, split)
    bags_tr = [split.bags[int(i)] for i in split.ids_tr]
    bags_te = [split.bags[int(i)] for i in split.ids_te]
    X_tr, X_te = build_features(bags_tr, spec.arm), build_features(bags_te, spec.arm)
    c = parse_condition(spec.condition)
    if c["kind"] == "padded":
        X_tr, X_te = padded_permute(X_tr, X_te, (X_tr.shape[1] - 1) // 6, c["seed"])
    Y_tr = np.stack([split.Y[int(i)] for i in split.ids_tr])
    Y_te = np.stack([split.Y[int(i)] for i in split.ids_te])
    v = max(1, int(0.2 * len(split.ids_tr)))
    Xtr_n, Xte_n, finfo = standardise_and_reduce(X_tr, X_te, v, pca_k)
    pre_s = time.perf_counter() - t_pre0
    fit_mode = effective_fit_mode(spec)
    pv, pt, recs = fit_predict_labels(factory, Xtr_n[v:], Y_tr[v:], Xtr_n[:v], Xte_n,
                                      fit_mode, labels=labels, mem=mem)
    return {"split": split, "v": v, "Y_tr": Y_tr, "Y_te": Y_te, "pv": pv, "pt": pt,
            "label_recs": recs, "preprocess_s": pre_s, "finfo": finfo, "fit_mode": fit_mode,
            "X": (Xtr_n[v:], Xtr_n[:v], Xte_n)}


def determinism_probe(factory, r):
    """Review 1 #15, inside §5 units only: refit the first fitted label once
    more on the same data and report max |delta| of its val and test
    predictions against the stored ones. Separates device nondeterminism
    from a one-fit effect; does not enter the §5 decision."""
    Xfit, Xval, Xte = r["X"]
    Yfit = r["Y_tr"][r["v"]:]
    fitted = [l for l in range(Yfit.shape[1]) if Yfit[:, l].min() != Yfit[:, l].max()]
    if not fitted:
        return {"label": None, "max_abs_diff_val": None, "max_abs_diff_test": None}
    l = fitted[0]
    clf = factory()
    clf.fit(Xfit, Yfit[:, l])
    return {"label": int(l),
            "max_abs_diff_val": float(np.max(np.abs(_proba1(clf, Xval) - r["pv"][:, l]))),
            "max_abs_diff_test": float(np.max(np.abs(_proba1(clf, Xte) - r["pt"][:, l])))}


def run_unit(spec, version, out_root, manifest, *, factory=None, kw=None, folds=None,
             log=print):
    """Fit, score and store every fold of one unit; reuse folds already stored
    with an identical identity; never overwrite."""
    check_arm_condition(spec.arm, spec.version, spec.condition)
    if spec.arm == "tabpfn_bagmean_card" and version.sizes_constant:
        manifest.add({"type": "skip", "unit": [spec.dataset, spec.version, spec.arm],
                      "reason": "= bag-mean (constant cardinality); H4 m5"})
        log(f"  {spec.arm}: skipped, constant cardinality")
        return []
    if factory is None:
        factory, kw = make_factory(spec.model, spec.device)
    meter = EnergyMeter(spec.device, allow_missing=spec.allow_no_nvml)
    mem = DeviceMemory(spec.device)
    vers, dev_str, ckpt = versions(), device_string(spec.device), \
        (tabpfn_checkpoint() if spec.model == "tabpfn" else None)
    d_feat = feature_dim(spec.arm, INSTANCE_PCA.get(spec.dataset, version.d))
    wtok, pca_k = width_plan(spec.width, version, d_feat,
                             spec.constructions_root or CONSTRUCTIONS_ROOT)
    written = []
    for split in version.splits:
        if folds is not None and (split.repeat, split.fold) not in folds:
            continue
        stem = fold_stem(split.repeat, split.fold)
        udir = unit_dir(out_root, spec.dataset, spec.version, spec.arm, wtok,
                        spec.condition, spec.devtok)
        npz_p, js_p = os.path.join(udir, stem + ".npz"), os.path.join(udir, stem + ".json")
        ident = _identity(spec, version, kw, d_feat, wtok, split)
        if os.path.exists(js_p):
            old = json.load(open(js_p))
            if old["identity"] != json.loads(json.dumps(ident, default=_json_default)):
                raise RuntimeError(f"{js_p} exists with a different identity; refusing "
                                   "to reuse or overwrite")
            manifest.add({"type": "reuse", "path": npz_p, "sha256": old["npz_sha256"],
                          "json": js_p, "procedures": list(spec.procedures)})
            log(f"  {stem}: reused")
            written.append(js_p)
            continue
        if os.path.exists(npz_p):
            raise RuntimeError(f"{npz_p} exists without its sidecar: incomplete unit; "
                               "inspect by hand (never overwritten)")
        load0, cpu0, wall0 = os.getloadavg(), cpu_seconds(), time.perf_counter()
        mem.reset()
        meter.start()
        r = run_split(spec, version, split, factory, kw, mem=mem, pca_k=pca_k)
        energy = meter.stop()
        wall = time.perf_counter() - wall0
        probe = (determinism_probe(factory, r)
                 if parse_condition(spec.condition)["kind"] == "verify" else None)
        th = optimize_thresholds(r["Y_tr"][:r["v"]], r["pv"], metric="hamming")
        pred = np.stack([(r["pt"][:, l] > th[l]) for l in range(len(th))], 1).astype(np.int8)
        metrics_prereg = AllFiveWithThresholds(r["Y_te"], r["pt"], th)
        # AMENDMENT.md A1: thresholded Hamming loss as before; ranking metrics tie-neutral
        metrics = dict(metrics_prereg)
        metrics.update(tn.ranking_four(r["Y_te"], r["pt"]))
        sp = r["split"]
        npz_sha = save_npz_noclobber(
            npz_p, test_idx=sp.ids_te, val_idx=sp.ids_tr[:r["v"]], fit_idx=sp.ids_tr[r["v"]:],
            scores=r["pt"].astype(np.float64), pred=pred,
            val_scores=r["pv"].astype(np.float64), thresholds=th.astype(np.float64),
            y_test=r["Y_te"].astype(np.int8), y_val=r["Y_tr"][:r["v"]].astype(np.int8))
        fits = [f for rec in r["label_recs"] for f in rec["fits"]]
        side = {
            "identity": ident, "npz_sha256": npz_sha, "repeat": split.repeat,
            "fold": split.fold, "n_train": int(len(sp.ids_tr)), "n_val": int(r["v"]),
            "n_fit": int(len(sp.ids_tr) - r["v"]), "n_test": int(len(sp.ids_te)),
            "L": int(r["pt"].shape[1]), "feature": r["finfo"], "split_info": sp.info,
            "metrics": {k: float(v) for k, v in metrics.items()},
            "metrics_prereg": {k: float(v) for k, v in metrics_prereg.items()},
            "timing": {"preprocess_s": r["preprocess_s"],
                       "fit_s": sum(f["fit_s"] for f in fits),
                       "predict_s": sum(f.get("predict_val_s", 0) + f.get("predict_test_s", 0)
                                        for f in fits),
                       "wall_s": wall, "cpu_s": cpu_seconds() - cpu0,
                       "per_label": r["label_recs"]},
            "memory": {"peak_rss_bytes": peak_rss_bytes(), **mem.report()},
            "energy": energy, "device": dev_str, "versions": vers, "checkpoint": ckpt,
            "loadavg_1min": {"start": load0[0], "end": os.getloadavg()[0]},
            "concurrency": spec.concurrency, "procedures": list(spec.procedures),
            "code_sha256": code_sha256(), "created_utc": time.strftime(
                "%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "argv": sys.argv,
            "determinism_probe": probe,
        }
        js_sha = save_json_noclobber(js_p, side)
        manifest.add({"type": "write", "path": npz_p, "sha256": npz_sha, "json": js_p,
                      "json_sha256": js_sha, "procedures": list(spec.procedures)})
        log(f"  {stem}: stored ({wall:.1f}s)")
        written.append(js_p)
    return written


def run_pilot(spec, version, out_root, run_id, *, factory=None, kw=None, n_labels=3):
    """§6.3: first 3 non-constant labels of outer fold 0 (repeat 0), production
    fit count (addendum Q6). Writes times only; predictions are discarded."""
    check_arm_condition(spec.arm, spec.version, spec.condition)
    if spec.arm == "tabpfn_bagmean_card" and version.sizes_constant:
        return None                      # not run on constant-size rows (H4 m5)
    if factory is None:
        factory, kw = make_factory(spec.model, spec.device)
    split = version.splits[0]
    v = max(1, int(0.2 * len(split.ids_tr)))
    Y_fit = np.stack([split.Y[int(i)] for i in split.ids_tr[v:]])
    nonconst = [l for l in range(version.L) if Y_fit[:, l].min() != Y_fit[:, l].max()]
    mem = DeviceMemory(spec.device)
    load0 = os.getloadavg()
    # Addendum Q6: constant labels are not fitted; pilot the first 3 labels
    # that are non-constant in fold 0's fit_i.
    _, pca_k = width_plan(spec.width, version,
                          feature_dim(spec.arm, INSTANCE_PCA.get(spec.dataset, version.d)),
                          spec.constructions_root or CONSTRUCTIONS_ROOT)
    r = run_split(spec, version, split, factory, kw, labels=nonconst[:n_labels], mem=mem,
                  pca_k=pca_k)
    rec = {"type": "pilot", "dataset": spec.dataset, "version": spec.version, "arm": spec.arm,
           "width": r["finfo"]["width_token"], "condition": spec.condition,
           "device_token": spec.devtok, "device": device_string(spec.device),
           "fit_mode": r["fit_mode"], "feature_dim": r["finfo"]["feature_dim"],
           "feature_dim_used": r["finfo"]["feature_dim_used"],
           "L": version.L, "n_nonconstant_labels": len(nonconst), "n_outer_folds": len({s.fold for s in version.splits}),
           "n_repeats": len({s.repeat for s in version.splits}),
           "n_fit": int(len(split.ids_tr) - r["v"]), "n_val": int(r["v"]),
           "n_test": int(len(split.ids_te)), "preprocess_s": r["preprocess_s"],
           "per_label": [{"label": rec["label"], "constant": rec["constant"],
                          "seconds": sum(f["fit_s"] + f.get("predict_val_s", 0)
                                         + f.get("predict_test_s", 0) for f in rec["fits"])}
                         for rec in r["label_recs"]],
           "loadavg_1min": {"start": load0[0], "end": os.getloadavg()[0]},
           "concurrency": spec.concurrency, "memory": {"peak_rss_bytes": peak_rss_bytes(),
                                                       **mem.report()},
           "versions": versions(), "constructor": kw, "created_utc": time.strftime(
               "%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    path = os.path.join(out_root, "pilots", f"{run_id}.jsonl")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a") as fh:
        fh.write(json.dumps(rec, sort_keys=True, default=_json_default) + "\n")
    return rec


# --------------------------------------------------------------------------
# §5 one-fit verification
# --------------------------------------------------------------------------
VERIFY_TARGETS = (("scene", "original"), ("letter_frost", "submitted5"))
VERIFY_TOL = 1e-9


def compare_verify(out_root, dataset, version_name, devtok):
    """Compare stored verify-2fit and verify-1fit sidecars fold by fold."""
    base = os.path.join(out_root, "predictions", dataset, version_name, "tabpfn_bagmean", "native")
    d2, d1 = os.path.join(base, f"verify-2fit+{devtok}"), os.path.join(base, f"verify-1fit+{devtok}")
    stems = sorted(f[:-5] for f in os.listdir(d2) if f.endswith(".json"))
    if sorted(f[:-5] for f in os.listdir(d1) if f.endswith(".json")) != stems or not stems:
        raise RuntimeError(f"verify folds differ or are missing under {base}")
    folds, ok = [], True
    for s in stems:
        a, b = json.load(open(os.path.join(d2, s + ".json"))), json.load(open(os.path.join(d1, s + ".json")))
        diffs = {m: abs(a["metrics"][m] - b["metrics"][m]) for m in FIVE}
        za, zb = np.load(os.path.join(d2, s + ".npz")), np.load(os.path.join(d1, s + ".npz"))
        score_diff = float(max(np.abs(za["scores"] - zb["scores"]).max(),
                               np.abs(za["val_scores"] - zb["val_scores"]).max()))
        fold_ok = all(v <= VERIFY_TOL for v in diffs.values())
        ok &= fold_ok
        folds.append({"fold": s, "metric_abs_diff": diffs, "max_abs_score_diff": score_diff,
                      "pass": fold_ok,
                      "determinism_probe": {"verify-2fit": a.get("determinism_probe"),
                                            "verify-1fit": b.get("determinism_probe")},
                      "hours": (a["timing"]["wall_s"] + b["timing"]["wall_s"]) / 3600})
    return {"dataset": dataset, "version": version_name, "pass": ok, "folds": folds}


def write_verify_verdict(out_root, devtok, results):
    verdict = {"check": "PREREGISTERED §5 one-fit", "tolerance": VERIFY_TOL,
               "device_token": devtok, "pass": all(r["pass"] for r in results),
               "targets": results, "hours_logged": sum(f["hours"] for r in results for f in r["folds"]),
               "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    path = os.path.join(out_root, "verify", f"onefit_{devtok}.json")
    save_json_noclobber(path, verdict)
    return path, verdict


def onefit_allowed(out_root, devtok):
    """Production one-fit only after §5 passed on this device."""
    path = os.path.join(out_root, "verify", f"onefit_{devtok}.json")
    if not os.path.exists(path):
        return False, f"{path} missing: §5 has not run on this device"
    v = json.load(open(path))
    return bool(v.get("pass")), path


# --------------------------------------------------------------------------
# Run preconditions: §6.4 width decision, §6.1 DEVICE_LOG.md (review 1 #3, #13)
# --------------------------------------------------------------------------
DEVICE_LOG = os.path.join(HERE, "DEVICE_LOG.md")


def check_width_decision(projections_path, dataset, version, d_feat, width, procedures=()):
    """Refuse a width that disagrees with the recorded §6.4 decision.

    Arms <= 500 wide are never switched (any request resolves to native).
    For wider arms the requested switch must equal `triggered` for the
    dataset in the committed projections JSON (project_cost.py output); the
    H3 Yeast pair (yeast/original with procedure H3) must be native.
    Returns the expected switch."""
    if d_feat <= PCA_DIM:
        return "native"
    if not projections_path:
        raise RuntimeError(f"{dataset}: arm is {d_feat} wide; --projections (the committed "
                           "§6.4 decision) is required")
    dec = json.load(open(projections_path))["pca_decision"].get(dataset)
    if dec is None or not dec.get("complete"):
        raise RuntimeError(f"{dataset}: no complete §6.4 decision in {projections_path}")
    expected = "pca" if dec["triggered"] else "native"
    if dataset == "yeast" and version == "original" and "H3" in procedures:
        if dec["triggered"] and "H1-leaky" in procedures:
            # review 2 #8: the H1-leaky row is then a separate pca<d'> unit (§1.5)
            raise RuntimeError("yeast/original: the §6.4 trigger fired, so the H1-leaky "
                               f"{d_feat}-wide unit is a separate pca<d'> unit; run H3 "
                               "(native) and H1-leaky (--width pca) as separate commands")
        expected = "native"                         # H3: registered rule, native width
    if width != expected:
        raise RuntimeError(f"{dataset}/{version}: --width {width} but the §6.4 decision "
                           f"requires {expected}; use --width-override REASON only under an "
                           "AMENDMENT")
    return expected


def check_device_log(device, mps_fallback=False, path=None):
    """§6.1: DEVICE_LOG.md must exist and name the device before any G fit
    (CUDA, or MPS under the global fallback, which it must also record)."""
    path = path or DEVICE_LOG
    if device == "cuda" or (device == "mps" and mps_fallback):
        if not os.path.exists(path):
            raise RuntimeError(f"{path} missing: §6.1 requires it before the first G fit")
        text = open(path).read()
        name = torch.cuda.get_device_name(0) if device == "cuda" else cpu_brand()
        if name not in text:
            raise RuntimeError(f"{path} does not name this device ({name!r})")
        if device == "mps" and "fallback" not in text.lower():
            raise RuntimeError(f"{path} does not record the §6.1 MPS fallback")
        return name
    return None


# --------------------------------------------------------------------------
# Fresh-host checkpoint bootstrap. (The real-data guard is the shared
# deposit_check.py, DECISIONS.md 2026-10-13; the CLI calls it.)
# --------------------------------------------------------------------------
def fetch_checkpoint(resolve=None, download=None):
    """Fresh-host bootstrap (review 2 #9, review 3 #1): make sure the pinned
    classifier checkpoint is in TabPFN's cache before any fit.

    If the file is missing it is downloaded with tabpfn's own `download_model`,
    whose `to` argument is the checkpoint FILE path (as tabpfn's own
    load_model_criterion_config passes it; the docstring's "directory" is
    wrong). Entries that the download adds to the cache directory besides
    the checkpoint (tabpfn's config.json, huggingface's .cache metadata) are
    removed. In every case the sha256 is verified against TABPFN_CKPT_SHA256;
    a mismatching file is renamed `<name>.bad-<sha12>` (never used, never
    deleted) and the call raises. Returns {"path", "sha256", "fetched", "cleaned"}."""
    import shutil
    if resolve is None:
        check_tabpfn_version()
        from tabpfn.model_loading import resolve_model_path
        resolve = lambda: str(resolve_model_path(None, "classifier")[0])  # noqa: E731
    if download is None:
        from pathlib import Path
        from tabpfn.model_loading import download_model
        download = lambda p: download_model(Path(p), version="v2",  # noqa: E731
                                            which="classifier", model_name=TABPFN_CKPT)
    path = resolve()
    if os.path.basename(path) != TABPFN_CKPT:
        raise RuntimeError(f"resolved checkpoint {path} is not {TABPFN_CKPT}")
    fetched, cleaned = False, []
    if not os.path.exists(path):
        cache = os.path.dirname(path)
        os.makedirs(cache, exist_ok=True)
        before = set(os.listdir(cache))
        res = download(path)
        for name in sorted(set(os.listdir(cache)) - before - {TABPFN_CKPT}):
            q = os.path.join(cache, name)
            (shutil.rmtree if os.path.isdir(q) and not os.path.islink(q) else os.unlink)(q)
            cleaned.append(name)
        if res != "ok" or not os.path.exists(path):
            raise RuntimeError(f"checkpoint download failed: {res}")
        fetched = True
    sha = sha256_file(path)
    if sha != TABPFN_CKPT_SHA256:
        bad = f"{path}.bad-{sha[:12]}"
        os.rename(path, bad)
        raise RuntimeError(f"checkpoint sha256 {sha} != pinned {TABPFN_CKPT_SHA256}; "
                           f"moved to {bad}")
    _CKPT.clear()                       # re-resolve on the next check
    return {"path": path, "sha256": sha, "fetched": fetched, "cleaned": cleaned}


# --------------------------------------------------------------------------
# Synthetic data (tests and smoke runs only)
# --------------------------------------------------------------------------
def make_synthetic(n_bags=60, d=4, L=3, seed=0, variable_size=True):
    """Small MIML problem whose labels depend on bag statistics."""
    rng = np.random.default_rng(seed)
    sizes = rng.integers(2, 7, n_bags) if variable_size else np.full(n_bags, 5)
    bags = [rng.normal(size=(int(n), d)).astype(np.float32) for n in sizes]
    Y = np.zeros((n_bags, L), dtype=int)
    for i, b in enumerate(bags):
        Y[i, 0] = b[:, 0].max() > 1.0
        Y[i, 1] = b[:, 1].mean() > 0.0
        if L > 2:
            Y[i, 2] = len(b) >= 4
        for l in range(3, L):
            Y[i, l] = b[:, l % d].min() < -1.0
    return bags, Y
