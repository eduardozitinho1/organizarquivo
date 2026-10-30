from pathlib import Path

import pytest

from organizarquivo.cli import (
    INFRASTRUCTURE_DIRS,
    collect_candidates,
    has_hidden_or_infra_segment,
    main,
    organize,
)


def test_hidden_folder_is_ignored(tmp_path):
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_bytes(b"x")
    (tmp_path / ".env").write_bytes(b"y")
    (tmp_path / "foto.jpg").write_bytes(b"z")

    organize(tmp_path, confirm=False)

    assert (tmp_path / ".git" / "config").exists()
    assert (tmp_path / ".env").exists()
    assert (tmp_path / "Images" / "foto.jpg").exists()


def test_git_repository_preserved(tmp_path):
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "HEAD").write_bytes(b"ref: refs/heads/main\n")
    (tmp_path / ".git" / "config").write_bytes(b"[core]\n")
    (tmp_path / "README.md").write_bytes(b"# projeto")
    (tmp_path / "foto.jpg").write_bytes(b"x")

    organize(tmp_path, confirm=False)

    assert (tmp_path / ".git" / "HEAD").exists()
    assert (tmp_path / ".git" / "config").exists()
    # README.md nao esta em nenhuma categoria conhecida, entao vai para Others
    assert (tmp_path / "Others" / "README.md").exists()
    assert not (tmp_path / "README.md").exists()
    assert (tmp_path / "Images" / "foto.jpg").exists()


@pytest.mark.parametrize("folder", ["node_modules", "__pycache__", ".venv", "target", "build"])
def test_infrastructure_folders_ignored(tmp_path, folder):
    (tmp_path / folder).mkdir()
    (tmp_path / folder / "arquivo.txt").write_bytes(b"x")
    (tmp_path / "foto.jpg").write_bytes(b"y")

    organize(tmp_path, confirm=False)

    assert (tmp_path / folder / "arquivo.txt").exists()
    assert (tmp_path / "Images" / "foto.jpg").exists()


def test_subfolder_files_are_not_moved_by_default(tmp_path):
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "foto.jpg").write_bytes(b"a")
    (tmp_path / "raiz.jpg").write_bytes(b"b")

    organize(tmp_path, confirm=False)

    assert (tmp_path / "sub" / "foto.jpg").exists()
    assert (tmp_path / "Images" / "raiz.jpg").exists()
    assert not (tmp_path / "Images" / "foto.jpg").exists()


def test_category_folder_not_reorganized(tmp_path):
    (tmp_path / "Images").mkdir()
    (tmp_path / "Images" / "antiga.jpg").write_bytes(b"x")
    (tmp_path / "nova.jpg").write_bytes(b"y")

    organize(tmp_path, confirm=False)

    assert (tmp_path / "Images" / "antiga.jpg").exists()
    assert (tmp_path / "Images" / "nova.jpg").exists()


def test_has_hidden_or_infra_detects_git():
    assert has_hidden_or_infra_segment(Path(".git") / "config")
    assert has_hidden_or_infra_segment(Path("node_modules") / "x.js")
    assert not has_hidden_or_infra_segment(Path("foto.jpg"))


def test_collect_candidates_only_root_files(tmp_path):
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "inner.jpg").write_bytes(b"x")
    (tmp_path / "foto.jpg").write_bytes(b"y")
    (tmp_path / ".hidden.jpg").write_bytes(b"z")

    candidates = collect_candidates(tmp_path)

    names = sorted(p.name for p in candidates)
    assert names == ["foto.jpg"]


def test_main_dry_run_does_not_move(tmp_path, capsys):
    (tmp_path / "foto.jpg").write_bytes(b"a")
    (tmp_path / "doc.pdf").write_bytes(b"b")

    code = main([str(tmp_path), "--dry-run"])

    assert code == 0
    captured = capsys.readouterr()
    assert "[dry-run]" in captured.out
    assert "foto.jpg -> Images/" in captured.out
    assert (tmp_path / "foto.jpg").exists()
    assert (tmp_path / "doc.pdf").exists()
    assert not (tmp_path / "Images").exists()


def test_main_yes_flag_skips_confirmation(tmp_path, monkeypatch):
    (tmp_path / "foto.jpg").write_bytes(b"a")

    monkeypatch.setattr("builtins.input", lambda *_: pytest.fail("input should not be called"))

    code = main([str(tmp_path), "--yes"])

    assert code == 0
    assert (tmp_path / "Images" / "foto.jpg").exists()


def test_main_cancel_on_no(tmp_path, monkeypatch):
    (tmp_path / "foto.jpg").write_bytes(b"a")

    monkeypatch.setattr("builtins.input", lambda *_: "n")

    code = main([str(tmp_path)])

    assert code == 0
    assert (tmp_path / "foto.jpg").exists()
    assert not (tmp_path / "Images").exists()


def test_main_unknown_option_returns_1(capsys):
    code = main(["--bogus"])
    assert code == 1
    captured = capsys.readouterr()
    assert "Opcao desconhecida" in captured.err


def test_main_help_returns_0(capsys):
    code = main(["--help"])
    assert code == 0
    captured = capsys.readouterr()
    assert "Uso: organizarquivo" in captured.out
