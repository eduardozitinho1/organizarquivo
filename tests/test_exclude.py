from pathlib import Path

from organizarquivo.config import Config
from organizarquivo.history import History
from organizarquivo.organizer import collect_candidates, organize


def test_exclude_pattern_skips_file(tmp_path):
    (tmp_path / "a.jpg").write_bytes(b"x")
    (tmp_path / "b.tmp").write_bytes(b"y")

    cands = collect_candidates(tmp_path, excludes=["*.tmp"])
    assert [p.name for p in cands] == ["a.jpg"]


def test_exclude_multiple_patterns(tmp_path):
    (tmp_path / "a.jpg").write_bytes(b"x")
    (tmp_path / "b.tmp").write_bytes(b"y")
    (tmp_path / "c.bak").write_bytes(b"z")

    cands = collect_candidates(tmp_path, excludes=["*.tmp", "*.bak"])
    assert [p.name for p in cands] == ["a.jpg"]


def test_exclude_from_config(tmp_path):
    (tmp_path / "keep.jpg").write_bytes(b"x")
    (tmp_path / "drop.tmp").write_bytes(b"y")

    cfg = Config.defaults()
    cfg.excludes = ["*.tmp"]

    from organizarquivo.history import History
    organize(tmp_path, confirm=False, config=cfg, history=History(tmp_path / ".h"))

    assert (tmp_path / "drop.tmp").exists()
    assert (tmp_path / "Images" / "keep.jpg").exists()


def test_cli_exclude_overrides_config(tmp_path, monkeypatch):
    (tmp_path / "a.tmp").write_bytes(b"x")
    (tmp_path / "b.tmp").write_bytes(b"y")
    (tmp_path / "c.jpg").write_bytes(b"z")

    monkeypatch.setenv("ORGANIZARQUIVO_CACHE", str(tmp_path / ".h"))

    from organizarquivo.cli import main
    code = main([str(tmp_path), "--exclude", "*.tmp", "-y"])
    assert code == 0
    assert (tmp_path / "a.tmp").exists()
    assert (tmp_path / "b.tmp").exists()
    assert (tmp_path / "Images" / "c.jpg").exists()
