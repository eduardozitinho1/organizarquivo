"""CLI do organizarquivo, com subcomando undo."""

from __future__ import annotations

import sys
from pathlib import Path

from .categories import (
    CATEGORIES,
    INFRASTRUCTURE_DIRS,
    OTHER,
    category_for,
)
from .config import Config, cache_dir, load_config
from .history import History, history_for
from .organizer import (
    collect_candidates,
    detect_git_repo,
    has_hidden_or_infra_segment,
    organize,
    plan_moves,
    unique_destination,
)
from .ui import ProgressBar, print_dry_run, print_stats

__all__ = [
    "CATEGORIES",
    "INFRASTRUCTURE_DIRS",
    "OTHER",
    "category_for",
    "collect_candidates",
    "detect_git_repo",
    "has_hidden_or_infra_segment",
    "organize",
    "plan_moves",
    "unique_destination",
    "main",
]

USAGE = """uso:
  organizarquivo <pasta> [opcoes]
  organizarquivo undo [--list] [<id>]

opcoes de organizacao:
  -y, --yes           nao perguntar antes de mover
  --dry-run           mostrar o que seria feito, sem mover
  -r, --recursive     incluir subpastas (pula .git, .venv, etc)
  -e, --exclude GLOB  ignorar arquivos que casem com o padrao (repetivel)
  --stats             mostrar estatisticas detalhadas ao final
  -h, --help          mostrar esta ajuda

opcoes de undo:
  --list              listar operacoes recentes
  <id>                reverter uma operacao especifica (padrao: a ultima)
"""


def parse_organize_args(argv: list[str]) -> tuple[Path | None, dict, int]:
    opts = {
        "assume_yes": False,
        "dry_run": False,
        "recursive": False,
        "excludes": [],
        "stats": False,
    }
    positional: list[str] = []
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg in {"-y", "--yes"}:
            opts["assume_yes"] = True
        elif arg == "--dry-run":
            opts["dry_run"] = True
        elif arg in {"-r", "--recursive"}:
            opts["recursive"] = True
        elif arg in {"-e", "--exclude"}:
            i += 1
            if i >= len(argv):
                print("--exclude requer um padrao", file=sys.stderr)
                return None, opts, 1
            opts["excludes"].append(argv[i])
        elif arg == "--stats":
            opts["stats"] = True
        elif arg in {"-h", "--help"}:
            print(USAGE)
            return None, opts, 0
        elif arg.startswith("-") and arg != "-":
            print(f"opcao desconhecida: {arg}", file=sys.stderr)
            return None, opts, 1
        else:
            positional.append(arg)
        i += 1

    if len(positional) != 1:
        print(USAGE, file=sys.stderr)
        return None, opts, 1

    return Path(positional[0]), opts, 0


def cmd_organize(argv: list[str]) -> int:
    target, opts, code = parse_organize_args(argv)
    if code != 0 or target is None:
        return code

    cfg = load_config()
    if not opts["assume_yes"] and not cfg.confirm:
        opts["assume_yes"] = True

    target_resolved = target.expanduser().resolve()
    if not target_resolved.exists():
        print(f"Erro: pasta nao encontrada: {target_resolved}", file=sys.stderr)
        return 1
    if not target_resolved.is_dir():
        print(f"Erro: nao e uma pasta: {target_resolved}", file=sys.stderr)
        return 1

    excludes = list(cfg.excludes) + opts["excludes"]
    candidates = collect_candidates(
        target_resolved,
        recursive=opts["recursive"],
        excludes=excludes,
        categories=cfg.categories,
        extra_infra=cfg.excluded_directories - INFRASTRUCTURE_DIRS,
    )

    if not candidates:
        print("Nada para organizar.")
        return 0

    planned = plan_moves(target_resolved, candidates, cfg.categories)

    if opts["dry_run"]:
        print_dry_run(target_resolved, planned, cfg.categories)
        return 0

    bar = ProgressBar(total=len(planned))

    def on_progress(step: int, total: int) -> None:
        bar.update(step, total)

    print(f"Organizando: {target_resolved}")
    try:
        result = organize(
            target_resolved,
            confirm=not opts["assume_yes"],
            assume_yes=opts["assume_yes"],
            recursive=opts["recursive"],
            excludes=opts["excludes"],
            config=cfg,
            on_progress=on_progress,
        )
    except (FileNotFoundError, NotADirectoryError) as exc:
        bar.finish()
        print(f"Erro: {exc}", file=sys.stderr)
        return 1

    bar.finish()

    if result.get("cancelled"):
        return 0

    moved = result["moved"]
    failed = result["failed"]

    if moved == 0 and failed == 0:
        print("Nada para organizar.")
        return 0

    if opts["stats"]:
        print_stats(result, target_resolved)
    else:
        print(f"Organizados: {moved}")
        if failed:
            print(f"Falhas: {failed}")
        per_category = result.get("per_category", {})
        if per_category:
            print("Por categoria:")
            for category, count in sorted(per_category.items()):
                print(f"  {category}: {count}")

    history_id = result.get("history_id")
    if history_id:
        print(f"\nPara desfazer: organizarquivo undo {history_id}")

    return 0


def cmd_undo(argv: list[str]) -> int:
    cache = cache_dir()
    history = History(cache)

    if "--list" in argv:
        entries = history.list_entries()
        if not entries:
            print("Nenhuma operacao registrada.")
            return 0

        print("Operacoes recentes:")
        for entry in entries[:10]:
            print(
                f"  {entry.id}  {entry.timestamp}  "
                f"{entry.moved} movido(s)  {entry.status}  {entry.target}"
            )
        return 0

    explicit_id = None
    for arg in argv:
        if arg.startswith("-"):
            print(f"opcao desconhecida: {arg}", file=sys.stderr)
            return 1
        if explicit_id is None:
            explicit_id = arg

    if explicit_id:
        entry = history.get(explicit_id)
        if entry is None:
            print(f"Erro: id '{explicit_id}' nao encontrado.", file=sys.stderr)
            return 1
    else:
        entries = history.list_entries()
        if not entries:
            print("Nenhuma operacao para desfazer.", file=sys.stderr)
            return 1
        entry = entries[0]

    print(f"Revertendo {entry.id} ({entry.moved} arquivo(s) em {entry.target})")
    result = history.undo(entry)

    print(f"\nRevertidos: {len(result['undone'])}")
    if result["failed"]:
        print(f"Falhas: {len(result['failed'])}", file=sys.stderr)
        for src, dst, reason in result["failed"]:
            print(f"  falha: {dst} -> {src}: {reason}", file=sys.stderr)
    if result["skipped"]:
        print(f"Ignorados: {len(result['skipped'])}")
        for src, dst, reason in result["skipped"]:
            print(f"  ignorado: {dst} -> {src}: {reason}")

    return 0 if not result["failed"] else 1


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)

    if args and args[0] == "undo":
        return cmd_undo(args[1:])

    if args and args[0] in {"-h", "--help"}:
        print(USAGE)
        return 0

    return cmd_organize(args)
