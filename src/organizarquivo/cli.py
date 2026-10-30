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


def organize(target: Path) -> dict[str, object]:
    target = target.expanduser().resolve()

    if not target.exists():
        raise FileNotFoundError(f"Pasta nao encontrada: {target}")
    if not target.is_dir():
        raise NotADirectoryError(f"Nao e uma pasta: {target}")

    category_names = set(CATEGORIES) | {OTHER}

    candidates = [
        path
        for path in target.rglob("*")
        if path.is_file() and path.parent.name not in category_names
    ]

    if not candidates:
        return {"moved": 0, "failed": 0, "per_category": {}}

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
    }


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)

    if len(args) != 1:
        print("Uso: organizarquivo <pasta>", file=sys.stderr)
        return 1

    target = Path(args[0])
    print(f"Organizando: {target}")

    try:
        result = organize(target)
    except (FileNotFoundError, NotADirectoryError) as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1

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
