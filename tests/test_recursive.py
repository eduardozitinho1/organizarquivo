from pathlib import Path

from organizarquivo.config import Config
from organizarquivo.organizer import collect_candidates, organize


def test_recursive_false_only_root(tmp_path):
    (tmp_path / "a.jpg").write_bytes(b"x")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "b.jpg").write_bytes(b"y")

    cands = collect_candidates(tmp_path, recursive=False)
    assert [p.name for p in cands] == ["a.jpg"]


def test_recursive_true_includes_subfolders(tmp_path):
    (tmp_path / "a.jpg").write_bytes(b"x")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "b.jpg").write_bytes(b"y")

    cands = collect_candidates(tmp_path, recursive=True)
    names = sorted(p.name for p in cands)
    assert names == ["a.jpg", "b.jpg"]


def test_recursive_skips_infrastructure(tmp_path):
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_bytes(b"x")
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "x.js").write_bytes(b"y")
    (tmp_path / "a.jpg").write_bytes(b"z")

    cands = collect_candidates(tmp_path, recursive=True)
    names = [p.name for p in cands]
    assert names == ["a.jpg"]


def test_recursive_skips_category_folders(tmp_path):
    (tmp_path / "Images").mkdir()
    (tmp_path / "Images" / "old.jpg").write_bytes(b"x")
    (tmp_path / "new.jpg").write_bytes(b"y")

    cands = collect_candidates(tmp_path, recursive=True)
    assert [p.name for p in cands] == ["new.jpg"]


def test_recursive_organizes_end_to_end(tmp_path):
    (tmp_path / "sub1").mkdir()
    (tmp_path / "sub2").mkdir()
    (tmp_path / "sub1" / "a.jpg").write_bytes(b"1")
    (tmp_path / "sub2" / "b.pdf").write_bytes(b"2")
    (tmp_path / "c.zip").write_bytes(b"3")

    cfg = Config.defaults()
    result = organize(
        tmp_path, confirm=False, recursive=True, config=cfg,
        history=__import__("organizarquivo.history", fromlist=["History"]).History(tmp_path / ".h"),
    )

    assert result["moved"] == 3
    assert (tmp_path / "Images" / "a.jpg").exists()
    assert (tmp_path / "Documents" / "b.pdf").exists()
    assert (tmp_path / "Archives" / "c.zip").exists()


def test_recursive_handles_name_collisions(tmp_path):
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    (tmp_path / "a" / "foto.jpg").write_bytes(b"first")
    (tmp_path / "b" / "foto.jpg").write_bytes(b"second")

    cfg = Config.defaults()
    from organizarquivo.history import History
    organize(
        tmp_path, confirm=False, recursive=True, config=cfg,
        history=History(tmp_path / ".h"),
    )

    images = sorted((tmp_path / "Images").iterdir())
    assert len(images) == 2
    contents = sorted(p.read_bytes() for p in images)
    assert contents == [b"first", b"second"]
