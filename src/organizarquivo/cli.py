"""CLI do Organizarquivo."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path


CATEGORIES: dict[str, set[str]] = {
    "Documents": {".pdf", ".docx", ".doc", ".txt"},
    "Images": {".jpeg", ".jpg", ".png"},
    "Videos": {".mp4", ".mkv", ".mov"},
    "Audios": {".wav", ".mp3"},
    "Spreadsheets": {".xlsx", ".xls", ".csv"},
}

OTHER = "Others"

INFRASTRUCTURE_DIRS: frozenset[str] = frozenset({
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    "node_modules",
    ".idea",
    ".vscode",
    "target",
    "dist",
    "build",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tox",
    ".gradle",
    ".cache",
})


def category_for(extension: str) -> str:
    ext = extension.lower()
    for name, extensions in CATEGORIES.items():
        if ext in extensions:
            return name
    return OTHER


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


def has_hidden_or_infra_segment(relative: Path) -> bool:
    for part in relative.parts:
        if part.startswith("."):
            return True
        if part in INFRASTRUCTURE_DIRS:
            return True
    return False


def collect_candidates(target: Path) -> list[Path]:
    category_names = set(CATEGORIES) | {OTHER}
    candidates: list[Path] = []

    for path in target.iterdir():
        if not path.is_file():
            continue
        if path.name in category_names:
            continue
        if has_hidden_or_infra_segment(Path(path.name)):
            continue
        candidates.append(path)

    return candidates


def detect_git_repo(target: Path) -> bool:
    return (target / ".git").is_dir()


def organize(target: Path, *, confirm: bool = True, assume_yes: bool = False) -> dict[str, object]:
    target = target.expanduser().resolve()

    if not target.exists():
        raise FileNotFoundError(f"Pasta nao encontrada: {target}")
    if not target.is_dir():
        raise NotADirectoryError(f"Nao e uma pasta: {target}")

    candidates = collect_candidates(target)

    if not candidates:
        return {"moved": 0, "failed": 0, "per_category": {}, "cancelled": False}

    if detect_git_repo(target):
        print(
            f"aviso: {target} e um repositorio git. "
            "Arquivos da raiz serao movidos, mas .git e preservado.",
            file=sys.stderr,
        )

    print(f"Arquivos a mover: {len(candidates)}")

    if confirm and not assume_yes:
        try:
            answer = input("Continuar? [s/N] ").strip().lower()
        except EOFError:
            answer = ""
        if answer not in {"s", "sim", "y", "yes"}:
            print("Cancelado.")
            return {"moved": 0, "failed": 0, "per_category": {}, "cancelled": True}

    planned = [(path, category_for(path.suffix)) for path in candidates]
    used_categories = {category for _, category in planned}

    for category in used_categories:
        (target / category).mkdir(parents=True, exist_ok=True)

    per_category: dict[str, int] = {category: 0 for category in used_categories}
    failed = 0

    for source, category in planned:
        destination = unique_destination(target / category / source.name)
        try:
            shutil.move(str(source), str(destination))
        except (OSError, shutil.Error) as exc:
            print(f"  falha: {source.name}: {exc}", file=sys.stderr)
            failed += 1
            continue
        per_category[category] += 1

    return {
        "moved": len(planned) - failed,
        "failed": failed,
        "per_category": {k: v for k, v in per_category.items() if v > 0},
        "cancelled": False,
    }


def parse_args(argv: list[str]) -> tuple[Path | None, bool, bool, int]:
    """Devolve (target, assume_yes, dry_run, exit_code).

    exit_code != 0 indica erro de uso, e target vem None.
    """
    assume_yes = False
    dry_run = False
    positional: list[str] = []

    for arg in argv:
        if arg in {"-y", "--yes"}:
            assume_yes = True
        elif arg == "--dry-run":
            dry_run = True
        elif arg in {"-h", "--help"}:
            print("Uso: organizarquivo <pasta> [-y] [--dry-run]")
            return None, False, False, 0
        elif arg.startswith("-"):
            print(f"Opcao desconhecida: {arg}", file=sys.stderr)
            return None, False, False, 1
        else:
            positional.append(arg)

    if len(positional) != 1:
        print("Uso: organizarquivo <pasta> [-y] [--dry-run]", file=sys.stderr)
        return None, False, False, 1

    return Path(positional[0]), assume_yes, dry_run, 0


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)

    target, assume_yes, dry_run, code = parse_args(args)
    if code != 0 or target is None:
        return code

    print(f"Organizando: {target}")

    try:
        if dry_run:
            resolved = target.expanduser().resolve()
            if not resolved.exists():
                raise FileNotFoundError(f"Pasta nao encontrada: {resolved}")
            if not resolved.is_dir():
                raise NotADirectoryError(f"Nao e uma pasta: {resolved}")
            candidates = collect_candidates(resolved)
            print(f"[dry-run] moveria {len(candidates)} arquivos")
            for path in sorted(candidates):
                category = category_for(path.suffix)
                print(f"  {path.name} -> {category}/")
            return 0

        result = organize(
            target,
            confirm=not assume_yes,
            assume_yes=assume_yes,
        )
    except (FileNotFoundError, NotADirectoryError) as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1

    if result["cancelled"]:
        return 0

    moved = result["moved"]
    failed = result["failed"]
    per_category = result["per_category"]

    if moved == 0 and failed == 0:
        print("Nada para organizar.")
        return 0

    print(f"Organizados: {moved}")
    if failed:
        print(f"Falhas: {failed}")
    if per_category:
        print("Por categoria:")
        for category, count in sorted(per_category.items()):
            print(f"  {category}: {count}")

    return 0
