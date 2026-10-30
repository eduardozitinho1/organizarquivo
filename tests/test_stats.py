from pathlib import Path

from organizarquivo.config import Config
from organizarquivo.history import History
from organizarquivo.organizer import organize
from organizarquivo.ui import format_bytes, print_stats


def test_format_bytes_units():
    assert format_bytes(500) == "500 B"
    assert format_bytes(1024) == "1.0 KiB"
    assert format_bytes(1024 * 1024) == "1.0 MiB"


def test_stats_output_contains_counts(tmp_path, capsys):
    (tmp_path / "a.jpg").write_bytes(b"x" * 100)
    (tmp_path / "b.pdf").write_bytes(b"y" * 200)
    (tmp_path / "c.zip").write_bytes(b"z" * 300)

    from organizarquivo.history import History
    result = organize(
        tmp_path, confirm=False,
        config=Config.defaults(),
        history=History(tmp_path / ".h"),
    )

    capsys.readouterr()
    print_stats(result, tmp_path)
    out = capsys.readouterr().out

    assert "3 arquivo" in out
    assert "Images" in out
    assert "Documents" in out
    assert "Archives" in out
