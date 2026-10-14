import os
import re
import sys

import pytest

TABPFN_VERSION = "2.2.1"
CMD = ".tabpfn_env/bin/python -m pytest experiments/revision_r1/tests"


def pytest_configure(config):
    config.addinivalue_line("markers", "tabpfn: fits real TabPFN 2.2.1 on CPU (tiny synthetic data)")
    config.addinivalue_line("markers", "synthetic_data_dir: the test points MIML_DATA_DIR / "
                            "set_data_dir at synthetic files it wrote itself; only then is a data "
                            "directory configured during the test left unprotected")


@pytest.fixture(autouse=True)
def _pinned_tabpfn_only(request):
    """Tests marked `tabpfn` refuse to run on any TabPFN but the pinned 2.2.1
    of .tabpfn_env (./.venv holds the licence-gated 8.x)."""
    if request.node.get_closest_marker("tabpfn") is None:
        return
    try:
        import tabpfn
        ver = getattr(tabpfn, "__version__", None)
    except Exception as exc:  # pragma: no cover
        ver = f"unavailable ({type(exc).__name__})"
    if ver != TABPFN_VERSION:
        pytest.fail(f"REFUSED: TabPFN tests need tabpfn=={TABPFN_VERSION} (.tabpfn_env); "
                    f"this interpreter ({sys.executable}) has {ver}. Run: {CMD}",
                    pytrace=False)


# ------------------------------------------------- no real data in any test
# A1 reviews 2-5: a reviewer's in-memory guard mutant turned a refusal test into
# a real Letter Frost run (quarantine/2026-10-13_accidental_letter_frost_run/).
# Two layers, both active in EVERY test, whatever the guards do:
#  1. an audit hook (sys.addaudithook) refuses any file open, and any subprocess,
#     os.system, exec or spawn call whose arguments name (as text, or after
#     resolving relative to its cwd, default the current directory, with
#     symlinks followed) or whose cwd is a path under a protected root: the real
#     data directories, any data directory configured now (MIML_DATA_DIR /
#     set_data_dir, also during the test), the production output tree
#     results/revision_r1/ and quarantine/. Write-mode opens under the tracked
#     evidence tree are refused as well. Paths compare case-insensitively. This
#     covers open(), np.load and every loadmat import path. It does not follow
#     into child processes: a child is refused only by what its command names.
#  2. every known loadmat binding is wrapped as well (a second, independent check).
# A test marked `synthetic_data_dir` may point the data directory at synthetic
# files it wrote itself; the static roots stay protected even then.
# Audit hooks cannot be removed; the hook is inert outside a test (flag).
HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
STATIC_ROOTS = [
    os.path.realpath(os.path.join(PROJECT, "..", "VIT_MIL", "Code", "MIML-SELFVIT")),
    # data/: the raw source datasets and any rebuilt sets; data/third_party/
    # (the LAMDA authors' MIMLNN code, used by the harness tests) is code, not data
    os.path.realpath(os.path.join(PROJECT, "data", "mulan_raw")),
    os.path.realpath(os.path.join(PROJECT, "data", "mulan_github_raw")),
    os.path.realpath(os.path.join(PROJECT, "data", "openml_raw")),
    os.path.realpath(os.path.join(PROJECT, "data", "rebuilt")),
    os.path.realpath(os.path.join(PROJECT, "experiments", "kdis", "arff")),
    os.path.realpath(os.path.join(PROJECT, "experiments", "lamda", "folds")),
    os.path.realpath(os.path.join(PROJECT, "results", "revision_r1")),
    os.path.realpath(os.path.join(PROJECT, "quarantine")),
]
# the tracked evidence tree: tests may read it, never write it (A1 review 4, N4)
WRITE_PROTECTED_ROOTS = [os.path.realpath(os.path.join(PROJECT, "revision_access_44676", "evidence"))]
REAL_DATA_ROOTS = list(STATIC_ROOTS)          # per-test additions (tests may extend it)
LOADMAT_MODULES = ["scipy.io", "scipy.io.matlab", "miml_clam.data.miml_dataset_cv",
                   "miml_clam.data.miml_dataset_dd", "miml_clam.data.flat_knn_dataset",
                   "h2_common"]
_HOOK = {"on": False, "dynamic": True}
_WRITE_FLAGS = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_APPEND | os.O_TRUNC


class RealDataRead(AssertionError):
    pass


def _norm(p):
    # macOS volumes are case-insensitive: compare case-folded real paths
    return os.path.realpath(p).casefold()


def current_roots():
    """Protected roots, recomputed at every check: the static ones, the per-test
    list, and any data directory configured right now (MIML_DATA_DIR, or
    tabpfn_arms.set_data_dir), including one configured during the test."""
    roots = list(REAL_DATA_ROOTS)
    if not _HOOK["dynamic"]:               # @pytest.mark.synthetic_data_dir
        return [_norm(r) for r in roots]
    if os.environ.get("MIML_DATA_DIR"):
        roots.append(os.environ["MIML_DATA_DIR"])
    ta = sys.modules.get("tabpfn_arms")
    if ta is not None and getattr(ta, "_DATA_DIR_OVERRIDE", {}).get("dir"):
        roots.append(ta._DATA_DIR_OVERRIDE["dir"])
    return [_norm(r) for r in roots]


def _under(p, roots):
    q = _norm(p)
    return any(q == r or q.startswith(r + os.sep) for r in roots)


def _is_real(path):
    try:
        raw = os.fsdecode(os.fspath(path))
    except TypeError:
        return False                       # a file descriptor: opened earlier, already checked
    return _under(raw, current_roots())


def _is_write(mode, flags):
    if isinstance(mode, str) and any(c in mode for c in "wax+"):
        return True
    return isinstance(flags, int) and bool(flags & _WRITE_FLAGS)


def _refuse(msg):
    _HOOK["on"] = False                    # do not re-enter while raising
    try:
        raise RealDataRead(msg)
    finally:
        _HOOK["on"] = True


def _strings(obj):
    if isinstance(obj, (str, bytes, os.PathLike)):
        obj = [obj]
    out = []
    for a in (obj or []):
        try:
            out.append(os.fsdecode(os.fspath(a)))
        except TypeError:
            continue
    return out


def _names_protected(texts, cwd=None):
    """A protected path named by a command: a token that contains a protected
    root as text, or that resolves (relative to cwd, default the current
    directory; symlinks followed) to a path under one; or a protected cwd."""
    roots = current_roots() + [_norm(r) for r in WRITE_PROTECTED_ROOTS]
    base = cwd or os.getcwd()
    for t in texts:
        if any(r in t.casefold() for r in roots):
            return t
        # os.system passes one command string: split on whitespace and shell
        # punctuation, so redirects (<path) and key=path arguments are resolved too
        for tok in re.split(r"[\s<>=;|&()'\"]+", t):
            if tok and _under(tok if os.path.isabs(tok) else os.path.join(base, tok), roots):
                return t
    if _under(base, roots):
        return base
    return None


def _audit(event, args):
    if not _HOOK["on"]:
        return
    if event == "open":
        if not args:
            return
        path = args[0]
        mode = args[1] if len(args) > 1 else None
        flags = args[2] if len(args) > 2 else None
        if _is_real(path):
            _refuse(f"test opened a protected path: {path}")
        try:
            raw = os.fsdecode(os.fspath(path))
        except TypeError:
            return
        if _is_write(mode, flags) and _under(raw, [_norm(r) for r in WRITE_PROTECTED_ROOTS]):
            _refuse(f"test opened the evidence tree for writing: {path}")
    elif event == "subprocess.Popen":
        argv = args[1] if len(args) > 1 else None
        cwd = args[2] if len(args) > 2 else None
        cwd = os.fsdecode(os.fspath(cwd)) if isinstance(cwd, (str, bytes, os.PathLike)) else None
        hit = _names_protected(_strings(argv), cwd)
        if hit:
            _refuse(f"test started a subprocess on a protected path: {hit}")
    elif event in ("os.system", "os.posix_spawn", "os.exec", "os.spawn"):
        hit = _names_protected([t for a in args for t in _strings(a)], None)
        if hit:
            _refuse(f"test ran a command on a protected path: {hit}")


sys.addaudithook(_audit)


@pytest.fixture(autouse=True)
def _no_real_data(monkeypatch, request):
    import importlib
    _HOOK["dynamic"] = request.node.get_closest_marker("synthetic_data_dir") is None
    env_dd = os.environ.get("MIML_DATA_DIR")        # protect it, then hide it from the test
    monkeypatch.delenv("MIML_DATA_DIR", raising=False)
    try:
        import tabpfn_arms
        dd = tabpfn_arms._DATA_DIR_OVERRIDE.get("dir")
        monkeypatch.setitem(tabpfn_arms._DATA_DIR_OVERRIDE, "dir", None)
    except Exception:
        dd = None
    roots = list(STATIC_ROOTS)
    for extra in (env_dd, dd):             # protect what was configured before the test too
        if extra:
            roots.append(os.path.realpath(extra))
    monkeypatch.setattr(sys.modules[__name__], "REAL_DATA_ROOTS", roots)
    for name in LOADMAT_MODULES:
        mod = importlib.import_module(name)         # a missing module is an error, not a skip
        orig = getattr(mod, "loadmat")
        if getattr(orig, "_no_real_data", False):
            continue

        def guarded(path, *a, _orig=orig, **k):
            if _is_real(path):
                raise RealDataRead(f"test read real data: {path}")
            return _orig(path, *a, **k)
        guarded._no_real_data = True
        monkeypatch.setattr(mod, "loadmat", guarded)
    _HOOK["on"] = True
    try:
        yield
    finally:
        _HOOK["on"] = False
