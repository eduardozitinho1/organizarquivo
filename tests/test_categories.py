from organizarquivo.categories import (
    CATEGORIES,
    INFRASTRUCTURE_DIRS,
    OTHER,
    all_category_names,
    category_for,
)


def test_default_categories_cover_common_archives():
    for ext in (".zip", ".rar", ".7z", ".tar", ".gz"):
        assert category_for(ext) == "Archives"


def test_default_categories_cover_code():
    for ext in (".py", ".js", ".ts", ".cs", ".rs", ".go", ".java"):
        assert category_for(ext) == "Code"


def test_default_categories_cover_books():
    for ext in (".epub", ".mobi", ".azw3"):
        assert category_for(ext) == "Books"


def test_default_categories_cover_fonts():
    for ext in (".ttf", ".otf", ".woff2"):
        assert category_for(ext) == "Fonts"


def test_default_categories_cover_3d():
    for ext in (".blend", ".obj", ".fbx", ".gltf"):
        assert category_for(ext) == "3D"


def test_default_categories_cover_design():
    for ext in (".psd", ".ai", ".sketch", ".fig"):
        assert category_for(ext) == "Design"


def test_default_categories_cover_presentations():
    for ext in (".pptx", ".ppt", ".key", ".odp"):
        assert category_for(ext) == "Presentations"


def test_default_categories_cover_executables():
    for ext in (".exe", ".msi", ".dmg", ".deb", ".rpm"):
        assert category_for(ext) == "Executables"


def test_default_categories_cover_databases():
    for ext in (".sqlite", ".db", ".mdb"):
        assert category_for(ext) == "Databases"


def test_expanded_images():
    for ext in (".gif", ".webp", ".svg", ".ico", ".heic", ".avif"):
        assert category_for(ext) == "Images"


def test_expanded_videos():
    for ext in (".avi", ".webm", ".flv", ".wmv", ".m4v"):
        assert category_for(ext) == "Videos"


def test_expanded_audios():
    for ext in (".flac", ".aac", ".ogg", ".m4a", ".opus"):
        assert category_for(ext) == "Audios"


def test_unknown_extension_goes_to_others():
    assert category_for(".xyz123") == OTHER


def test_case_insensitive():
    assert category_for(".ZIP") == "Archives"
    assert category_for(".PY") == "Code"


def test_custom_categories_override_defaults_via_config(tmp_path, monkeypatch):
    """A resolucao de conflito (custom ganha de default) e responsabilidade
    do config, nao do category_for. Testa o fluxo completo."""
    from organizarquivo.config import load_config

    config_file = tmp_path / "config.toml"
    config_file.write_text(
        '[categories]\n"Trabalho" = [".docx", ".xlsx"]\n',
        encoding="utf-8",
    )
    monkeypatch.setenv("ORGANIZARQUIVO_CONFIG", str(config_file))
    cfg = load_config()

    assert category_for(".docx", cfg.categories) == "Trabalho"
    assert category_for(".xlsx", cfg.categories) == "Trabalho"
    assert category_for(".pdf", cfg.categories) == "Documents"


def test_all_category_names_includes_others():
    names = all_category_names()
    assert OTHER in names
    assert "Documents" in names


def test_infrastructure_dirs_contain_common():
    for name in (".git", ".venv", "node_modules", "__pycache__", "target", "build"):
        assert name in INFRASTRUCTURE_DIRS
