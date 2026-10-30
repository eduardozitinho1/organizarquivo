"""Logica central de organizacao."""

from __future__ import annotations

import fnmatch
import shutil
import sys
from pathlib import Path

from .categories import (
    INFRASTRUCTURE_DIRS,
    OTHER,
    all_category_names,
    category_for,
)
from .config import Config
from .history import History, history_for


def unique_destination(destination: Path) -> Path:
    if not destination.exists():
        return destination

    stem = destination.stem
    suffix = destination.suffix
    parent = destination.parent
    counter = 1
    while True:
        candidate = parent / f"{stem} ({counter}){suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def has_hidden_or_infra_segment(relative: Path, extra_infra: set[str] | None = None) -> bool:
    infra = INFRASTRUCTURE_DIRS | (extra_infra or set())
    for part in relative.parts:
        if part.startswith("."):
            return True
        if part in infra:
            return True
    return False


def detect_git_repo(target: Path) -> bool:
    return (target / ".git").is_dir()


def _matches_exclude(name: str, patterns: list[str]) -> bool:
    for pattern in patterns:
        if fnmatch.fnmatch(name, pattern):
            return True
    return False


def collect_candidates(
    target: Path,
    *,
    recursive: bool = False,
    excludes: list[str] | None = None,
    categories: dict[str, set[str]] | None = None,
    extra_infra: set[str] | None = None,
) -> list[Path]:
    """Lista os arquivos que serao movidos.

    Sem recursive: apenas arquivos na raiz de target.
    Com recursive: percorre subpastas, pulando infra e categorias.
    """
    category_names = all_category_names(categories)
    exclude_patterns = excludes or []
    candidates: list[Path] = []

    if not recursive:
        for entry in target.iterdir():
            if not entry.is_file():
                continue
            if entry.name in category_names:
                continue
            if has_hidden_or_infra_segment(Path(entry.name), extra_infra):
                continue
            if _matches_exclude(entry.name, exclude_patterns):
                continue
            candidates.append(entry)
        return sorted(candidates)

    for root in target.rglob("*"):
        if not root.is_file():
            continue
        try:
            relative = root.relative_to(target)
        except ValueError:
            continue

        if any(part in category_names for part in relative.parts):
            continue
        if has_hidden_or_infra_segment(relative, extra_infra):
            continue
        if _matches_exclude(root.name, exclude_patterns):
            continue
        candidates.append(root)

    return sorted(candidates)


def plan_moves(
    target: Path,
    candidates: list[Path],
    categories: dict[str, set[str]],
) -> list[tuple[Path, Path]]:
    """Calcula pares (origem, destino) respeitando colisoes."""
    planned: list[tuple[Path, Path]] = []
    used_destinations: dict[Path, Path] = {}

    for source in candidates:
        category = category_for(source.suffix, categories)
        base = target / category / source.name
        taken = used_destinations.get(base)

        if taken is None and not base.exists():
            destination = base
        else:
            destination = _unique_in_plan(base, used_destinations)

        used_destinations[destination] = source
        planned.append((source, destination))

    return planned


def _unique_in_plan(destination: Path, used: dict[Path, Path]) -> Path:
    stem = destination.stem
    suffix = destination.suffix
    parent = destination.parent
    counter = 1
    while True:
        candidate = parent / f"{stem} ({counter}){suffix}"
        if not candidate.exists() and candidate not in used:
            return candidate
        counter += 1


def organize(
    target: Path,
    *,
    confirm: bool = True,
    assume_yes: bool = False,
    recursive: bool = False,
    excludes: list[str] | None = None,
    config: Config | None = None,
    history: History | None = None,
    on_progress: "callable | None" = None,
) -> dict[str, object]:
    """Organiza a pasta alvo.

    Retorno:
      moved, failed, per_category, cancelled, history_id
    """
    target = Path(target).expanduser().resolve()
    cfg = config or Config.defaults()

    if not target.exists():
        raise FileNotFoundError(f"Pasta nao encontrada: {target}")
    if not target.is_dir():
        raise NotADirectoryError(f"Nao e uma pasta: {target}")

    exclude_patterns = list(cfg.excludes)
    if excludes:
        exclude_patterns.extend(excludes)

    candidates = collect_candidates(
        target,
        recursive=recursive,
        excludes=exclude_patterns,
        categories=cfg.categories,
        extra_infra=cfg.excluded_directories - INFRASTRUCTURE_DIRS,
    )

    if not candidates:
        return {
            "moved": 0,
            "failed": 0,
            "per_category": {},
            "cancelled": False,
            "history_id": None,
        }

    if detect_git_repo(target):
        print(
            f"aviso: {target} e um repositorio git. "
            "Arquivos da raiz serao movidos, mas .git e preservado.",
            file=sys.stderr,
        )

    planned = plan_moves(target, candidates, cfg.categories)

    if confirm and not assume_yes:
        try:
            answer = input(f"Mover {len(planned)} arquivos? [s/N] ").strip().lower()
        except EOFError:
            answer = ""
        if answer not in {"s", "sim", "y", "yes"}:
            print("Cancelado.")
            return {
                "moved": 0,
                "failed": 0,
                "per_category": {},
                "cancelled": True,
                "history_id": None,
            }

    history_instance = history or history_for()
    entry = history_instance.begin(target, planned)

    used_categories = sorted({category_for(src.suffix, cfg.categories) for src, _ in planned})
    for category in used_categories:
        (target / category).mkdir(parents=True, exist_ok=True)

    per_category: dict[str, int] = {category: 0 for category in used_categories}
    succeeded: list[tuple[str, str]] = []
    failed: list[tuple[str, str, str]] = []
    total = len(planned)
    step = 0

    for source, destination in planned:
        step += 1
        try:
            shutil.move(str(source), str(destination))
            succeeded.append((str(source), str(destination)))
            per_category[category_for(source.suffix, cfg.categories)] += 1
        except (OSError, shutil.Error) as exc:
            failed.append((str(source), str(destination), str(exc)))
            print(f"  falha: {source.name}: {exc}", file=sys.stderr)

        if on_progress is not None:
            on_progress(step, total)

    history_instance.complete(entry, succeeded, failed)

    return {
        "moved": len(succeeded),
        "failed": len(failed),
        "per_category": {k: v for k, v in per_category.items() if v > 0},
        "cancelled": False,
        "history_id": entry.id,
        "moved_pairs": succeeded,
        "failed_pairs": failed,
    }
