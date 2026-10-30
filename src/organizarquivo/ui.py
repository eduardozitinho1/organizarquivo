"""Formatacao de saida, progresso e resumo."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterable


class ProgressBar:
    """Barra de progresso simples, sem dependencias.

    So imprime se sys.stdout.isatty() e total >= min_total.
    """

    def __init__(self, total: int, *, min_total: int = 10, width: int = 40) -> None:
        self.total = total
        self.width = width
        self.enabled = sys.stdout.isatty() and total >= min_total
        self.last_drawn = -1

    def update(self, current: int, total: int | None = None) -> None:
        if not self.enabled:
            return

        tot = total if total is not None else self.total
        if tot <= 0:
            return

        fraction = min(1.0, current / tot)
        if int(fraction * 100) == self.last_drawn:
            return
        self.last_drawn = int(fraction * 100)

        filled = int(self.width * fraction)
        bar = "#" * filled + "-" * (self.width - filled)
        sys.stdout.write(f"\r  [{bar}] {current}/{tot}")
        sys.stdout.flush()

    def finish(self) -> None:
        if not self.enabled:
            return
        sys.stdout.write("\n")
        sys.stdout.flush()


def format_bytes(size: int) -> str:
    units = ["B", "KiB", "MiB", "GiB", "TiB"]
    n = float(size)
    for unit in units:
        if n < 1024 or unit == units[-1]:
            return f"{n:.1f} {unit}" if unit != "B" else f"{int(n)} B"
        n /= 1024
    return f"{size} B"


def print_dry_run(
    target: Path,
    planned: Iterable[tuple[Path, Path]],
    categories: dict[str, set[str]],
) -> None:
    from .categories import category_for

    print(f"[dry-run] organizando: {target}")
    entries = list(planned)
    if not entries:
        print("  nada a mover.")
        return

    print(f"[dry-run] moveria {len(entries)} arquivos:")

    grouped: dict[str, list[tuple[Path, Path]]] = {}
    for source, destination in entries:
        category = category_for(source.suffix, categories)
        grouped.setdefault(category, []).append((source, destination))

    for category in sorted(grouped):
        print(f"\n  {category}/")
        for source, _ in sorted(grouped[category], key=lambda p: p[0].name):
            try:
                size = source.stat().st_size
                marker = f" ({format_bytes(size)})"
            except OSError:
                marker = ""
            print(f"    {source.name}{marker}")


def print_stats(result: dict, target: Path) -> None:
    moved = result.get("moved", 0)
    failed = result.get("failed", 0)
    per_category = result.get("per_category", {})

    print(f"\nResumo: {moved} arquivo(s) organizado(s)")
    if failed:
        print(f"        {failed} falha(s)")

    if per_category:
        print("\nPor categoria:")
        for category, count in sorted(per_category.items(), key=lambda x: -x[1]):
            print(f"  {category:<16} {count}")

    pairs = result.get("moved_pairs", [])
    if pairs:
        print("\nMaiores arquivos movidos:")
        sizes: list[tuple[str, int]] = []
        for _, dest in pairs:
            try:
                size = Path(dest).stat().st_size
                sizes.append((Path(dest).name, size))
            except OSError:
                continue
        for name, size in sorted(sizes, key=lambda x: -x[1])[:5]:
            print(f"  {name}  {format_bytes(size)}")
