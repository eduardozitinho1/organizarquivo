import json
from pathlib import Path

from organizarquivo.history import History


def test_begin_creates_file(tmp_path):
    history = History(tmp_path)
    entry = history.begin(
        Path("/tmp/x"),
        [(Path("/tmp/x/a.jpg"), Path("/tmp/x/Images/a.jpg"))],
    )
    path = tmp_path / "history" / f"{entry.id}.json"
    assert path.is_file()
    data = json.loads(path.read_text())
    assert data["status"] == "in_progress"
    assert len(data["moves"]) == 1


def test_complete_updates_status(tmp_path):
    history = History(tmp_path)
    entry = history.begin(
        Path("/tmp/x"),
        [(Path("/tmp/x/a.jpg"), Path("/tmp/x/Images/a.jpg"))],
    )
    history.complete(
        entry,
        succeeded=[("/tmp/x/a.jpg", "/tmp/x/Images/a.jpg")],
        failed=[],
    )
    data = json.loads((tmp_path / "history" / f"{entry.id}.json").read_text())
    assert data["status"] == "completed"
    assert data["moves"][0]["status"] == "moved"
    assert data["moved"] == 1


def test_list_entries_returns_recent_first(tmp_path):
    history = History(tmp_path)
    e1 = history.begin(Path("/tmp/a"), [])
    e2 = history.begin(Path("/tmp/b"), [])
    entries = history.list_entries()
    assert entries[0].id == e2.id
    assert entries[1].id == e1.id


def test_get_returns_entry(tmp_path):
    history = History(tmp_path)
    entry = history.begin(Path("/tmp/x"), [])
    found = history.get(entry.id)
    assert found is not None
    assert found.id == entry.id


def test_get_returns_none_for_unknown(tmp_path):
    history = History(tmp_path)
    assert history.get("nope") is None


def test_undo_reverses_moves(tmp_path):
    src = tmp_path / "a.jpg"
    dst = tmp_path / "Images" / "a.jpg"
    src.write_bytes(b"x")
    dst.parent.mkdir()
    src.rename(dst)

    history = History(tmp_path / ".hist")
    entry = history.begin(tmp_path, [(src, dst)])
    history.complete(entry, [(str(src), str(dst))], [])

    result = history.undo(history.get(entry.id))

    assert len(result["undone"]) == 1
    assert src.exists()
    assert not dst.exists()


def test_undo_skips_pending_moves(tmp_path):
    src = tmp_path / "a.jpg"
    dst = tmp_path / "Images" / "a.jpg"

    history = History(tmp_path / ".hist")
    entry = history.begin(tmp_path, [(src, dst)])
    result = history.undo(history.get(entry.id))

    assert len(result["skipped"]) == 1
    assert result["undone"] == []


def test_undo_fails_when_source_occupied(tmp_path):
    src = tmp_path / "a.jpg"
    dst = tmp_path / "Images" / "a.jpg"
    src.write_bytes(b"old")
    dst.parent.mkdir()
    src.rename(dst)
    src.write_bytes(b"new")

    history = History(tmp_path / ".hist")
    entry = history.begin(tmp_path, [(src, dst)])
    history.complete(entry, [(str(src), str(dst))], [])

    result = history.undo(history.get(entry.id))
    assert len(result["failed"]) == 1


def test_undo_skips_missing_destination(tmp_path):
    src = tmp_path / "a.jpg"
    dst = tmp_path / "Images" / "a.jpg"

    history = History(tmp_path / ".hist")
    entry = history.begin(tmp_path, [(src, dst)])
    history.complete(entry, [(str(src), str(dst))], [])

    result = history.undo(history.get(entry.id))
    assert len(result["skipped"]) == 1
    assert "nao existe" in result["skipped"][0][2]


def test_history_prunes_old_entries(tmp_path, monkeypatch):
    from organizarquivo import history as history_mod
    monkeypatch.setattr(history_mod, "MAX_ENTRIES", 3)

    h = History(tmp_path)
    for i in range(5):
        h.begin(Path(f"/tmp/{i}"), [])

    files = list((tmp_path / "history").glob("*.json"))
    assert len(files) <= 3
