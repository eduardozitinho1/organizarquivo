"""Leitura e merge de ~/.organizarquivo.toml."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

from .categories import CATEGORIES, INFRASTRUCTURE_DIRS

try:
    import tomllib as _toml
    _HAS_TOMLLIB = True
except ModuleNotFoundError:
    _HAS_TOMLLIB = False
    try:
        import tomli as _toml  # type: ignore
    except ModuleNotFoundError:
        _toml = None  # type: ignore


DEFAULT_CONFIG_FILENAME = "organizarquivo.toml"


def default_config_path() -> Path:
    override = os.environ.get("ORGANIZARQUIVO_CONFIG")
    if override:
        return Path(override).expanduser()
    return Path.home() / f".{DEFAULT_CONFIG_FILENAME}"


def cache_dir() -> Path:
    """Diretorio de cache cross-platform, sem depender de platformdirs."""
    override = os.environ.get("ORGANIZARQUIVO_CACHE")
    if override:
        return Path(override).expanduser()

    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA", str(Path.home() / ".cache")))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Caches"
    else:
        base = Path(os.environ.get("XDG_CACHE_HOME", str(Path.home() / ".cache")))

    return base / "organizarquivo"


class Config:
    """Configuracao efetiva (defaults + arquivo do usuario)."""

    def __init__(
        self,
        categories: dict[str, set[str]],
        excludes: list[str],
        excluded_directories: set[str],
        confirm: bool,
        source_path: Path | None = None,
    ) -> None:
        self.categories = categories
        self.excludes = excludes
        self.excluded_directories = excluded_directories
        self.confirm = confirm
        self.source_path = source_path

    @classmethod
    def defaults(cls) -> "Config":
        return cls(
            categories={k: set(v) for k, v in CATEGORIES.items()},
            excludes=[],
            excluded_directories=set(INFRASTRUCTURE_DIRS),
            confirm=True,
        )

    @classmethod
    def load(cls, path: Path | None = None) -> "Config":
        config = cls.defaults()
        if _toml is None:
            return config

        source = path or default_config_path()
        if not source.is_file():
            return config

        try:
            with source.open("rb") as fh:
                data: dict[str, Any] = _toml.load(fh)
        except (OSError, ValueError):
            print(
                f"aviso: nao foi possivel ler {source}. usando defaults.",
                file=sys.stderr,
            )
            return config

        config.source_path = source
        config._merge(data)
        return config

    def _merge(self, data: dict[str, Any]) -> None:
        user_categories = data.get("categories", {})
        if isinstance(user_categories, dict):
            declared: dict[str, set[str]] = {}
            for name, extensions in user_categories.items():
                if not isinstance(name, str) or not name:
                    continue
                if not isinstance(extensions, list):
                    continue
                normalized = {
                    ext.lower() if ext.startswith(".") else f".{ext.lower()}"
                    for ext in extensions
                    if isinstance(ext, str) and ext
                }
                if normalized:
                    declared[name] = normalized

            # Extensoes declaradas pelo usuario saem de qualquer outra categoria,
            # para que .docx em "Trabalho" nao continue casando em "Documents".
            all_declared: set[str] = set()
            for exts in declared.values():
                all_declared |= exts

            for existing in list(self.categories.keys()):
                if existing in declared:
                    continue
                self.categories[existing] -= all_declared

            for name, exts in declared.items():
                self.categories[name] = exts

        user_exclude = data.get("exclude", {})
        if isinstance(user_exclude, dict):
            patterns = user_exclude.get("patterns", [])
            if isinstance(patterns, list):
                self.excludes.extend(
                    p for p in patterns if isinstance(p, str) and p
                )
            directories = user_exclude.get("directories", [])
            if isinstance(directories, list):
                self.excluded_directories.update(
                    d for d in directories if isinstance(d, str) and d
                )

        behavior = data.get("behavior", {})
        if isinstance(behavior, dict):
            confirm = behavior.get("confirm")
            if isinstance(confirm, bool):
                self.confirm = confirm


def load_config(path: Path | None = None) -> Config:
    return Config.load(path)
