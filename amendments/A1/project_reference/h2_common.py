"""Shared data access and no-overwrite I/O for the H2 constructions.

Binding spec: experiments/revision_r1/PREREGISTERED.md (tag prereg-v3-final-addendum),
sections H2-A, H2-B, 0.1, 1.1, 1.5. Used by h2a_rebuild.py and h2b_masks.py.

Nothing here touches results; it only loads inputs and writes files that do
not exist yet (lesson 9; PREREGISTERED.md 1.5 "a writer refuses to overwrite
an existing file").
"""
import hashlib
import io
import json
import os
import sys
import unicodedata
import zipfile

import numpy as np
from scipy.io import loadmat

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import deposit_check  # noqa: E402  (the shared real-data guard)

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(os.path.dirname(HERE))
PLAN = os.path.join(HERE, "PREREGISTERED.md")
RELEASE = os.path.join(os.path.dirname(PROJECT), "MIML_CLAM_Release")

# Output root for construction artefacts (PREREGISTERED.md 1.5, "Construction
# artefacts", pre-deposit addendum 2026-10-13).
OUT_ROOT = os.path.join(PROJECT, "results", "revision_r1", "constructions")
CSV_DIR = os.path.join(PROJECT, "results")
RESULTS = os.path.join(PROJECT, "results")

# The four constructed sets (0.1, 0.2).
CONSTRUCTED = ("emotions", "yeast", "medical", "corel5k")
N_FOLDS = 10   # canonical single 10-fold (1.1)


class ConstructionBug(RuntimeError):
    """A pre-registered zero-overlap or consistency check failed: stop (H2)."""


class RefuseOverwrite(FileExistsError):
    """The target file exists; the writer never replaces a file (1.5)."""


class NotDeposited(RuntimeError):
    """Real-data run refused: the plan has no public timestamp yet (1.8, 6.0)."""


# --------------------------------------------------------------------------- guard

def deposit_guard(plan_path=PLAN):
    """Refuse real-data runs until the plan records its public deposit.

    6.0: "Step 0 of both queues is the deposit of 1.8; nothing in either queue
    runs before it." The test is the single shared rule of every revision tool,
    deposit_check.deposit_recorded (DECISIONS.md 2026-10-13, "Deposit-line
    format and a single shared check"): line 8 must be exactly
    `| Public timestamp | https://doi.org/<DOI> (YYYY-MM-DD) |`, and every
    amendment in AMENDMENT.md must carry its own deposit line (A1 review 1, F5).
    """
    ref = deposit_check.deposit_reference(plan_path)
    if ref is None:
        raise NotDeposited(
            "PREREGISTERED.md line 8 does not record the deposit in the form "
            "'https://doi.org/<DOI> (YYYY-MM-DD)' (deposit_check.py), so real-data "
            "constructions may not run (6.0 step 0). Use --dry-run, or explicit toy paths.")
    if not deposit_check.deposit_recorded(plan_path):
        raise NotDeposited(
            "an amendment in AMENDMENT.md has no valid '**Deposited:** https://doi.org/<DOI> "
            "(YYYY-MM-DD)' line (deposit_check.py; A1 review 1, finding 5), so real-data "
            "constructions may not run. Use --dry-run, or explicit toy paths.")
    amend = deposit_check.amendment_status(plan_path) or {}
    extra = "".join("; %s https://doi.org/%s (%s)" % (k, v[0], v[1])
                    for k, v in sorted(amend.items()) if k.startswith("A"))
    return ("deposit https://doi.org/%s (%s)" % ref) + extra


FIRMLINK = "/System/Volumes/Data"


def _fold(p):
    """realpath, with the aliases realpath leaves alone folded away, so that two
    spellings of one directory compare equal (fails closed: it may over-refuse
    on a case-sensitive volume, never under-refuse):
      - the macOS firmlink prefix /System/Volumes/Data (an alias of /Users/...);
      - Unicode normalisation (APFS is normalisation-insensitive): NFC;
      - case (APFS here is case-insensitive): casefold."""
    q = os.path.realpath(p)
    if q == FIRMLINK or q.startswith(FIRMLINK + "/"):
        q = q[len(FIRMLINK):] or "/"
    return unicodedata.normalize("NFC", q).casefold()


def _under(p, root):
    """True iff p is root or lies inside it (case-folded realpaths)."""
    a, r = _fold(p), _fold(root)
    try:
        return os.path.commonpath([a, r]) == r
    except ValueError:              # different drives / mixed absolute-relative
        return False


def _real_input_files():
    return [p for d in CONSTRUCTED for p in dataset_paths(d)]


def _is_real_input(p, real_files):
    """An input is real if it lies in a real data directory or under results/
    (case-folded containment), or is the same file as a real input by
    (st_dev, st_ino), which also catches hard links and symlinks."""
    if any(_under(p, os.path.dirname(f)) for f in real_files) or _under(p, RESULTS):
        return True
    try:
        st = os.stat(p)
    except OSError:
        return False
    for f in real_files:
        try:
            g = os.stat(f)
        except OSError:
            continue
        if (st.st_dev, st.st_ino) == (g.st_dev, g.st_ino):
            return True
    return False


def guard_real_run(dataset, paths, out_root, plan_path=PLAN):
    """Call deposit_guard whenever a run could touch real data or real outputs:
    the dataset name (case-insensitively) is one of the constructed sets, any
    input is a real data file (see _is_real_input), or out_root lies anywhere
    under the project's results/ (nothing pre-deposit writes there). Called by
    both builders' run(); write_all/write_new add a second check at the point
    where files are created."""
    real_name = str(dataset).casefold().strip() in CONSTRUCTED
    real_root = _under(out_root, RESULTS)
    real_files = _real_input_files()
    real_path = any(_is_real_input(p, real_files) for p in paths)
    if real_root or real_name or real_path:
        return deposit_guard(plan_path)
    return None


# --------------------------------------------------------------------------- inputs

def dataset_paths(name):
    """(.mat, _10CV.mat) for a constructed set, from the configs every run used."""
    if RELEASE not in sys.path:
        sys.path.insert(0, RELEASE)
    import run_baseline_experiments as rbe   # noqa: E402  (heavy; imported lazily)
    cfg = rbe.DATASET_CONFIGS[name]
    return cfg["data_path"], cfg["cv_mat_path"]


def load_constructed(mat_path):
    """Bags (float64, as stored: raw features) and the {0,1} label matrix."""
    m = loadmat(mat_path)
    raw = m["bags"]
    bags = [np.ascontiguousarray(raw[i, 0], dtype=np.float64) for i in range(raw.shape[0])]
    Y = (np.asarray(m["labels"]) > 0).astype(np.int8)
    assert len(bags) == len(Y), (len(bags), Y.shape)
    return bags, Y


def source_rows(bags):
    """Source feature matrix by the identity mapping (H2-A step 1, T01 3).

    Bag i is centred on source row i and its first instance is that row byte
    for byte (T01 3: "centre = source row with same index 100%", stored
    features raw), so row i = bags[i][0].
    """
    X = np.ascontiguousarray(np.stack([b[0] for b in bags]), dtype=np.float64)
    if not np.isfinite(X).all():
        bad = np.argwhere(~np.isfinite(X))
        raise ConstructionBug(f"{len(bad)} non-finite source value(s), first at row/col {bad[0].tolist()}")
    return X


def vector_id_map(X):
    """vid[r] = lowest r' whose row is byte-identical to row r (H2-B, round 4 m1)."""
    first = {}
    vid = np.empty(len(X), dtype=np.int64)
    for r, row in enumerate(np.ascontiguousarray(X, dtype=np.float64)):
        vid[r] = first.setdefault(row.tobytes(), r)
    return vid


def canonical_splits(cv_mat_path, n):
    """The canonical folds, from the function every paper run used (1.1)."""
    if RELEASE not in sys.path:
        sys.path.insert(0, RELEASE)
    from miml_clam.data.miml_dataset_cv import get_cv_splits   # noqa: E402
    import torch                                                # imported by the line above
    torch.set_num_threads(1)                                    # 6.1 thread pinning
    return [(np.asarray(tr, dtype=np.int64), np.asarray(te, dtype=np.int64))
            for tr, te in get_cv_splits(cv_mat_path, n, N_FOLDS)]


def read_bag_rows_csv(path):
    """results/provenance_bag_rows_<ds>.csv -> list of (bag, centre_row, [members])."""
    out = []
    with open(path, encoding="utf-8") as fh:
        assert fh.readline().strip() == "bag,centre_row,member_rows"
        for line in fh:
            b, c, mem = line.rstrip("\n").split(",")
            out.append((int(b), int(c), [int(x) for x in mem.split()] if mem else []))
    return out


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# --------------------------------------------------------------------------- outputs

def npz_bytes(arrays):
    """A .npz readable by np.load, byte-deterministic (fixed zip timestamps)."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for key in sorted(arrays):
            arr = io.BytesIO()
            np.lib.format.write_array(arr, np.asarray(arrays[key]), allow_pickle=False)
            info = zipfile.ZipInfo(key + ".npy", date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, arr.getvalue())
    return buf.getvalue()


def json_bytes(obj):
    return (json.dumps(obj, indent=1, sort_keys=True) + "\n").encode("utf-8")


def write_new(path, data):
    """Create `path` with `data`; raise RefuseOverwrite if it exists.

    Written to a temporary sibling, then hard-linked into place: os.link fails
    atomically if the target exists, so a concurrent writer cannot replace it
    and a crash never leaves a partial file under the final name.
    """
    if _under(path, RESULTS):           # choke point: every writer passes here
        deposit_guard()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.lexists(path):
        raise RefuseOverwrite(path)
    tmp = f"{path}.tmp{os.getpid()}"
    with open(tmp, "xb") as fh:
        fh.write(data)
    try:
        os.link(tmp, path)
    except FileExistsError:
        raise RefuseOverwrite(path) from None
    finally:
        os.unlink(tmp)
    return hashlib.sha256(data).hexdigest()


def write_all(root, files):
    """Write {relative path: bytes} under root, then a MANIFEST.sha256 beside them.

    Every target is checked first, so an existing file refuses the whole set
    before anything is written.
    """
    if _under(root, RESULTS):           # choke point, before any target is created
        deposit_guard()
    targets = {rel: os.path.join(root, rel) for rel in files}
    targets["MANIFEST.sha256"] = os.path.join(root, "MANIFEST.sha256")
    clash = [p for p in targets.values() if os.path.lexists(p)]
    if clash:
        raise RefuseOverwrite(", ".join(sorted(clash)))
    lines = []
    for rel in sorted(files):
        lines.append(f"{write_new(targets[rel], files[rel])}  {rel}\n")
    write_new(targets["MANIFEST.sha256"], "".join(lines).encode("utf-8"))
    return sorted(targets.values())
