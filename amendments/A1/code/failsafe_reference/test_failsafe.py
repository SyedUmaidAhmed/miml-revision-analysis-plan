"""The suite-wide real-data fail-safe (conftest; A1 reviews 2-3, F8/F3).

Re-creates the 2026-10-13 accident: with every guard disabled in memory, a
real-data entry point must stop at its first protected read and write nothing.
Also checks each layer of the fail-safe directly, without reading real data:
the paths used below are refused before any byte is read."""
import os
import subprocess
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import conftest  # noqa: E402
import library_harness as lh  # noqa: E402
import run_nested_library as rnl  # noqa: E402
import t03_checks  # noqa: E402

REAL = os.path.join(conftest.STATIC_ROOTS[0], "scene.mat")


def test_every_loadmat_binding_is_wrapped():
    import importlib
    for name in conftest.LOADMAT_MODULES:
        assert getattr(importlib.import_module(name).loadmat, "_no_real_data", False), name


@pytest.mark.parametrize("root", conftest.STATIC_ROOTS)
def test_open_np_load_and_loadmat_are_refused_under_every_root(root):
    path = os.path.join(root, "anything.npz")
    with pytest.raises(conftest.RealDataRead):
        open(path, "rb")
    with pytest.raises(conftest.RealDataRead):
        np.load(path)
    import scipy.io
    with pytest.raises(conftest.RealDataRead):
        scipy.io.loadmat(path)


def test_writes_under_protected_roots_are_refused():
    with pytest.raises(conftest.RealDataRead):
        open(os.path.join(conftest.PROJECT, "results", "revision_r1", "x.json"), "w")


def test_configured_data_dir_is_protected(tmp_path, monkeypatch):
    """The GPU machine reads data through MIML_DATA_DIR / set_data_dir: a path
    there is refused like the default data directory."""
    import tabpfn_arms as ta
    d = tmp_path / "gpu_data"
    d.mkdir()
    (d / "scene.mat").write_bytes(b"not real")
    monkeypatch.setattr(conftest, "REAL_DATA_ROOTS", conftest.REAL_DATA_ROOTS + [str(d.resolve())])
    with pytest.raises(conftest.RealDataRead):
        open(d / "scene.mat", "rb")
    assert ta._DATA_DIR_OVERRIDE.get("dir") is None and "MIML_DATA_DIR" not in os.environ


def test_subprocess_on_a_protected_path_is_refused():
    with pytest.raises(conftest.RealDataRead):
        subprocess.run(["cat", REAL], capture_output=True)


def _disable_guards(monkeypatch):
    import deposit_check
    monkeypatch.setattr(deposit_check, "deposit_recorded", lambda *a, **k: True)
    monkeypatch.setattr(lh, "deposit_recorded", lambda *a, **k: True)
    monkeypatch.setattr(lh, "guard_dataset", lambda *a, **k: None)
    monkeypatch.setattr(lh, "guard_write", lambda *a, **k: None)

    def no_run(*a, **k):
        raise AssertionError("a library unit was started")
    monkeypatch.setattr(lh, "run_kdis_unit", no_run)
    monkeypatch.setattr(lh, "run_mimlnn_unit", no_run)


def _files(p):
    return [f for f in p.rglob("*") if f.is_file()]


def test_accident_scenario_runner_stops_at_first_read(tmp_path, monkeypatch):
    _disable_guards(monkeypatch)
    with pytest.raises(conftest.RealDataRead):
        rnl.main(["--dataset", "letter_frost", "--root", str(tmp_path / "root"),
                  "--workdir", str(tmp_path / "work")])
    assert _files(tmp_path) == []


def test_accident_scenario_t03_checks_stop_at_first_read(tmp_path, monkeypatch):
    _disable_guards(monkeypatch)
    with pytest.raises(conftest.RealDataRead):
        t03_checks.main(["a", "--dataset", "letter_frost", "--evidence-dir", str(tmp_path / "ev"),
                         "--workdir", str(tmp_path / "w")])
    assert _files(tmp_path) == []


# ------------------------------------------------- A1 review 4 (N3, N4)
def test_case_variant_path_is_refused():
    upper = conftest.STATIC_ROOTS[0].upper()
    with pytest.raises(conftest.RealDataRead):
        open(os.path.join(upper, "SCENE.MAT"), "rb")


def test_data_dir_configured_during_the_test_is_protected(tmp_path, monkeypatch):
    import tabpfn_arms as ta
    d1, d2 = tmp_path / "env_dir", tmp_path / "set_dir"
    for d in (d1, d2):
        d.mkdir()
        (d / "scene.mat").write_bytes(b"not real")
    monkeypatch.setenv("MIML_DATA_DIR", str(d1))
    with pytest.raises(conftest.RealDataRead):
        open(d1 / "scene.mat", "rb")
    monkeypatch.setitem(ta._DATA_DIR_OVERRIDE, "dir", str(d2))
    with pytest.raises(conftest.RealDataRead):
        open(d2 / "scene.mat", "rb")


def test_subprocess_cwd_and_os_system_are_checked():
    with pytest.raises(conftest.RealDataRead):
        subprocess.run(["cat", "scene.mat"], cwd=conftest.STATIC_ROOTS[0], capture_output=True)
    with pytest.raises(conftest.RealDataRead):
        os.system(f"cat {REAL} > /dev/null")


def test_evidence_tree_is_write_protected(tmp_path):
    ev = conftest.WRITE_PROTECTED_ROOTS[0]
    with pytest.raises(conftest.RealDataRead):
        open(os.path.join(ev, "T03__checks", "never_written.json"), "w")
    with pytest.raises(conftest.RealDataRead):
        os.open(os.path.join(ev, "never_written.txt"), os.O_WRONLY | os.O_CREAT)
    with open(os.path.join(ev, "T03__checks", "T03-a__letter_frost.json")) as fh:   # reading is fine
        assert fh.read(1) == "{"


# ------------------------------------------------- A1 review 5 (F2)
def test_relative_path_without_cwd_is_resolved(monkeypatch):
    monkeypatch.chdir(conftest.STATIC_ROOTS[0])
    with pytest.raises(conftest.RealDataRead):
        subprocess.run(["cat", "scene.mat"], capture_output=True)
    with pytest.raises(conftest.RealDataRead):
        os.system("cat scene.mat > /dev/null")


def test_symlink_into_a_protected_root_is_resolved(tmp_path):
    link = tmp_path / "innocent"
    link.symlink_to(conftest.STATIC_ROOTS[0])
    with pytest.raises(conftest.RealDataRead):
        subprocess.run(["cat", str(link / "scene.mat")], capture_output=True)
    with pytest.raises(conftest.RealDataRead):
        os.system(f"cat {link / 'scene.mat'} > /dev/null")


# ------------------------------------------------- A1 review 6 (F4)
def test_relative_path_from_an_unprotected_cwd_is_resolved(monkeypatch):
    """The relative path contains no protected root as text, and the cwd is
    not protected: only resolving the token catches it (names a file that does
    not exist, so even a broken hook reads nothing)."""
    monkeypatch.chdir(conftest.PROJECT)
    rel = "../VIT_MIL/Code/MIML-SELFVIT/never_exists.mat"
    with pytest.raises(conftest.RealDataRead):
        subprocess.run(["cat", rel], capture_output=True)
    with pytest.raises(conftest.RealDataRead):
        os.system(f"cat {rel} > /dev/null")
    with pytest.raises(conftest.RealDataRead):
        os.system(f"head -c 1 <{rel}")
    with pytest.raises(conftest.RealDataRead):
        os.system(f"dd if={rel} of=/dev/null 2>/dev/null")


def test_protected_cwd_alone_is_refused():
    with pytest.raises(conftest.RealDataRead):
        subprocess.run(["/usr/bin/true"], cwd=conftest.STATIC_ROOTS[0])
