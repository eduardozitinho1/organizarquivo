from pathlib import Path

from organizarquivo.cli import main
from organizarquivo.config import Config
from organizarquivo.history import History
from organizarquivo.organizer import organize


def test_organize_records_history(tmp_path, monkeypatch):
    monkeypatch.setenv("ORGANIZARQUIVO_CACHE", str(tmp_path / ".cache"))
    (tmp_path / "a.jpg").write_bytes(b"x")
    (tmp_path / "b.pdf").write_bytes(b"y")

    result = organize(tmp_path, confirm=False, history=History(tmp_path / ".cache"))

    assert result["history_id"]
    history_files = list((tmp_path / ".cache" / "history").glob("*.json"))
    assert len(history_files) == 1


def test_undo_via_cli_restores_files(tmp_path, monkeypatch):
    monkeypatch.setenv("ORGANIZARQUIVO_CACHE", str(tmp_path / ".cache"))

    (tmp_path / "a.jpg").write_bytes(b"aaa")
    (tmp_path / "b.pdf").write_bytes(b"bbb")

    assert main([str(tmp_path), "-y"]) == 0
    assert (tmp_path / "Images" / "a.jpg").exists()
    assert (tmp_path / "Documents" / "b.pdf").exists()

    assert main(["undo"]) == 0
    assert (tmp_path / "a.jpg").exists()
    assert (tmp_path / "b.pdf").exists()
    assert not (tmp_path / "Images").exists() or not any((tmp_path / "Images").iterdir())


def test_undo_list_shows_operations(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("ORGANIZARQUIVO_CACHE", str(tmp_path / ".cache"))
    (tmp_path / "a.jpg").write_bytes(b"x")

    main([str(tmp_path), "-y"])
    capsys.readouterr()

    main(["undo", "--list"])
    out = capsys.readouterr().out
    assert "Operacoes recentes" in out
    assert str(tmp_path) in out


def test_undo_unknown_id_returns_1(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("ORGANIZARQUIVO_CACHE", str(tmp_path / ".cache"))
    code = main(["undo", "nonexistent-id"])
    assert code == 1


def test_undo_without_history_returns_1(tmp_path, monkeypatch):
    monkeypatch.setenv("ORGANIZARQUIVO_CACHE", str(tmp_path / ".cache"))
    code = main(["undo"])
    assert code == 1
