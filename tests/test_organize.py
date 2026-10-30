from pathlib import Path

import pytest

from organizarquivo.cli import category_for, organize, unique_destination


def test_category_for_known_extension():
    assert category_for(".pdf") == "Documents"
    assert category_for(".mp3") == "Audios"


def test_category_for_is_case_insensitive():
    assert category_for(".JPG") == "Images"
    assert category_for(".PDF") == "Documents"


def test_category_for_unknown_goes_to_others():
    assert category_for(".iso") == "Others"
    assert category_for("") == "Others"


def test_unique_destination_when_no_collision(tmp_path):
    target = tmp_path / "foto.jpg"
    assert unique_destination(target) == target


def test_unique_destination_when_one_collision(tmp_path):
    (tmp_path / "foto.jpg").write_bytes(b"a")
    assert unique_destination(tmp_path / "foto.jpg") == tmp_path / "foto (1).jpg"


def test_unique_destination_when_two_collisions(tmp_path):
    (tmp_path / "foto.jpg").write_bytes(b"a")
    (tmp_path / "foto (1).jpg").write_bytes(b"b")
    assert unique_destination(tmp_path / "foto.jpg") == tmp_path / "foto (2).jpg"


def test_organize_moves_each_extension(tmp_path):
    (tmp_path / "doc.pdf").write_bytes(b"a")
    (tmp_path / "img.jpg").write_bytes(b"b")
    (tmp_path / "vid.mp4").write_bytes(b"c")
    (tmp_path / "song.mp3").write_bytes(b"d")
    (tmp_path / "plan.xlsx").write_bytes(b"e")
    (tmp_path / "arquivo.iso").write_bytes(b"f")

    result = organize(tmp_path, confirm=False)

    assert (tmp_path / "Documents" / "doc.pdf").exists()
    assert (tmp_path / "Images" / "img.jpg").exists()
    assert (tmp_path / "Videos" / "vid.mp4").exists()
    assert (tmp_path / "Audios" / "song.mp3").exists()
    assert (tmp_path / "Spreadsheets" / "plan.xlsx").exists()
    assert (tmp_path / "Others" / "arquivo.iso").exists()
    assert result["moved"] == 6
    assert result["failed"] == 0


def test_organize_does_not_overwrite(tmp_path):
    # arquivo ja organizado em Images/, e um novo arquivo com mesmo nome na raiz
    (tmp_path / "Images").mkdir()
    (tmp_path / "Images" / "foto.jpg").write_bytes(b"antigo")
    (tmp_path / "foto.jpg").write_bytes(b"novo")

    organize(tmp_path, confirm=False)

    images = sorted((tmp_path / "Images").iterdir())
    assert len(images) == 2
    names = [p.name for p in images]
    assert "foto.jpg" in names
    assert "foto (1).jpg" in names
    assert (tmp_path / "Images" / "foto.jpg").read_bytes() == b"antigo"
    assert (tmp_path / "Images" / "foto (1).jpg").read_bytes() == b"novo"


def test_organize_skips_files_already_organized(tmp_path):
    (tmp_path / "Documents").mkdir()
    (tmp_path / "Documents" / "old.pdf").write_bytes(b"x")
    (tmp_path / "new.jpg").write_bytes(b"y")

    organize(tmp_path, confirm=False)

    assert (tmp_path / "Documents" / "old.pdf").exists()
    assert (tmp_path / "Images" / "new.jpg").exists()


def test_organize_empty_folder_does_not_create_others(tmp_path):
    result = organize(tmp_path, confirm=False)
    assert result["moved"] == 0
    assert not (tmp_path / "Others").exists()
    assert not (tmp_path / "Documents").exists()


def test_organize_only_used_categories_created(tmp_path):
    (tmp_path / "a.pdf").write_bytes(b"x")

    organize(tmp_path, confirm=False)

    assert (tmp_path / "Documents").exists()
    assert not (tmp_path / "Images").exists()
    assert not (tmp_path / "Others").exists()


def test_organize_nonexistent_folder():
    with pytest.raises(FileNotFoundError):
        organize(Path("/caminho/que/nao/existe"))


def test_organize_when_target_is_a_file(tmp_path):
    file = tmp_path / "arquivo.txt"
    file.write_bytes(b"x")
    with pytest.raises(NotADirectoryError):
        organize(file)


def test_main_py_is_treated_like_any_other_file(tmp_path):
    (tmp_path / "main.py").write_bytes(b"x")
    organize(tmp_path, confirm=False)
    assert (tmp_path / "Others" / "main.py").exists()
