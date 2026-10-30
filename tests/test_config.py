from pathlib import Path

import pytest

from organizarquivo.categories import CATEGORIES
from organizarquivo.config import Config, load_config


def test_default_config_matches_defaults():
    cfg = Config.defaults()
    assert set(cfg.categories) == set(CATEGORIES)
    assert cfg.excludes == []
    assert cfg.confirm is True


def test_load_returns_defaults_when_missing(tmp_path, monkeypatch):
    monkeypatch.setenv("ORGANIZARQUIVO_CONFIG", str(tmp_path / "missing.toml"))
    cfg = load_config()
    assert set(cfg.categories) == set(CATEGORIES)


def test_load_merges_custom_category(tmp_path, monkeypatch):
    config_file = tmp_path / "config.toml"
    config_file.write_text(
        '[categories]\n"Trabalho" = [".docx", ".xlsx"]\n', encoding="utf-8"
    )
    monkeypatch.setenv("ORGANIZARQUIVO_CONFIG", str(config_file))
    cfg = load_config()
    assert "Trabalho" in cfg.categories
    assert cfg.categories["Trabalho"] == {".docx", ".xlsx"}
    assert "Documents" in cfg.categories


def test_load_extends_existing_category(tmp_path, monkeypatch):
    config_file = tmp_path / "config.toml"
    config_file.write_text(
        '[categories]\n"Documents" = [".md", ".rst"]\n', encoding="utf-8"
    )
    monkeypatch.setenv("ORGANIZARQUIVO_CONFIG", str(config_file))
    cfg = load_config()
    assert ".md" in cfg.categories["Documents"]
    assert ".rst" in cfg.categories["Documents"]
    assert ".pdf" not in cfg.categories["Documents"]


def test_load_reads_excludes(tmp_path, monkeypatch):
    config_file = tmp_path / "config.toml"
    config_file.write_text(
        '[exclude]\npatterns = ["*.tmp", "*.bak"]\n'
        'directories = ["Important"]\n',
        encoding="utf-8",
    )
    monkeypatch.setenv("ORGANIZARQUIVO_CONFIG", str(config_file))
    cfg = load_config()
    assert "*.tmp" in cfg.excludes
    assert "*.bak" in cfg.excludes
    assert "Important" in cfg.excluded_directories


def test_load_reads_confirm_behavior(tmp_path, monkeypatch):
    config_file = tmp_path / "config.toml"
    config_file.write_text("[behavior]\nconfirm = false\n", encoding="utf-8")
    monkeypatch.setenv("ORGANIZARQUIVO_CONFIG", str(config_file))
    cfg = load_config()
    assert cfg.confirm is False


def test_malformed_config_falls_back_to_defaults(tmp_path, monkeypatch):
    config_file = tmp_path / "config.toml"
    config_file.write_text("not [valid toml", encoding="utf-8")
    monkeypatch.setenv("ORGANIZARQUIVO_CONFIG", str(config_file))
    cfg = load_config()
    assert set(cfg.categories) == set(CATEGORIES)


def test_normalizes_extensions_without_dot(tmp_path, monkeypatch):
    config_file = tmp_path / "config.toml"
    config_file.write_text(
        '[categories]\n"Custom" = ["foo", ".bar"]\n', encoding="utf-8"
    )
    monkeypatch.setenv("ORGANIZARQUIVO_CONFIG", str(config_file))
    cfg = load_config()
    assert ".foo" in cfg.categories["Custom"]
    assert ".bar" in cfg.categories["Custom"]
