"""Historico de operacoes para permitir undo."""

from __future__ import annotations

import json
import os
import sys
import time
import uuid
from pathlib import Path
from typing import Any

HISTORY_VERSION = 1
MAX_ENTRIES = 50


class HistoryEntry:
    """Uma entrada de historico (uma execucao de organize)."""

    def __init__(
        self,
        id: str,
        timestamp: str,
        target: str,
        moves: list[dict[str, str]],
        status: str,
        moved: int = 0,
        failed: int = 0,
    ) -> None:
        self.id = id
        self.timestamp = timestamp
        self.target = target
        self.moves = moves
        self.status = status
        self.moved = moved
        self.failed = failed

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": HISTORY_VERSION,
            "id": self.id,
            "timestamp": self.timestamp,
            "target": self.target,
            "status": self.status,
            "moved": self.moved,
            "failed": self.failed,
            "moves": self.moves,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "HistoryEntry":
        return cls(
            id=data["id"],
            timestamp=data["timestamp"],
            target=data["target"],
            moves=data["moves"],
            status=data["status"],
            moved=data.get("moved", 0),
            failed=data.get("failed", 0),
        )


class History:
    def __init__(self, cache_dir: Path) -> None:
        self.cache_dir = cache_dir
        self.history_dir = cache_dir / "history"
        self.history_dir.mkdir(parents=True, exist_ok=True)

    def begin(self, target: Path, planned_moves: list[tuple[Path, Path]]) -> HistoryEntry:
        """Grava a intencao ANTES de mover. Se houver crash, o undo ainda funciona."""
        entry_id = self._new_id()
        entry = HistoryEntry(
            id=entry_id,
            timestamp=self._now_iso(),
            target=str(target),
            moves=[
                {"source": str(src), "destination": str(dst), "status": "pending"}
                for src, dst in planned_moves
            ],
            status="in_progress",
        )
        self._write(entry)
        self._prune()
        return entry

    def complete(
        self,
        entry: HistoryEntry,
        succeeded: list[tuple[str, str]],
        failed: list[tuple[str, str, str]],
    ) -> None:
        succeeded_set = {src for src, _ in succeeded}
        failed_map = {src: reason for src, _, reason in failed}

        for move in entry.moves:
            src = move["source"]
            if src in succeeded_set:
                move["status"] = "moved"
            elif src in failed_map:
                move["status"] = f"failed: {failed_map[src]}"

        entry.status = "completed"
        entry.moved = len(succeeded)
        entry.failed = len(failed)
        self._write(entry)
        self._prune()

    def list_entries(self) -> list[HistoryEntry]:
        entries: list[HistoryEntry] = []
        if not self.history_dir.is_dir():
            return entries

        for path in sorted(self.history_dir.glob("*.json"), reverse=True):
            try:
                with path.open("r", encoding="utf-8") as fh:
                    data = json.load(fh)
                entries.append(HistoryEntry.from_dict(data))
            except (OSError, ValueError, KeyError):
                continue

        return entries

    def get(self, entry_id: str) -> HistoryEntry | None:
        path = self.history_dir / f"{entry_id}.json"
        if not path.is_file():
            return None
        try:
            with path.open("r", encoding="utf-8") as fh:
                return HistoryEntry.from_dict(json.load(fh))
        except (OSError, ValueError, KeyError):
            return None

    def undo(self, entry: HistoryEntry) -> dict[str, Any]:
        """Reverte os moves que ainda fazem sentido reverter.

        Retorna um dict com:
          undone:  lista de (src, dst) revertidos
          failed:  lista de (src, dst, motivo) nao revertidos
          skipped: lista de (src, dst, motivo) que nao precisam reverter
        """
        undone: list[tuple[str, str]] = []
        failed: list[tuple[str, str, str]] = []
        skipped: list[tuple[str, str, str]] = []

        for move in reversed(entry.moves):
            src = Path(move["source"])
            dst = Path(move["destination"])

            if move["status"] == "pending":
                skipped.append((str(src), str(dst), "nunca chegou a ser movido"))
                continue

            if not dst.exists():
                skipped.append((str(src), str(dst), "destino nao existe mais"))
                continue

            if src.exists():
                failed.append((str(src), str(dst), "origem ja ocupada"))
                continue

            try:
                src.parent.mkdir(parents=True, exist_ok=True)
                dst.rename(src)
                undone.append((str(src), str(dst)))
            except OSError as exc:
                failed.append((str(src), str(dst), str(exc)))

        return {"undone": undone, "failed": failed, "skipped": skipped}

    def _write(self, entry: HistoryEntry) -> None:
        path = self.history_dir / f"{entry.id}.json"
        tmp = path.with_suffix(".json.tmp")
        with tmp.open("w", encoding="utf-8") as fh:
            json.dump(entry.to_dict(), fh, indent=2, ensure_ascii=False)
        tmp.replace(path)

    def _prune(self) -> None:
        files = sorted(self.history_dir.glob("*.json"), reverse=True)
        for old in files[MAX_ENTRIES:]:
            try:
                old.unlink()
            except OSError:
                pass

    @staticmethod
    def _new_id() -> str:
        now = time.time()
        stamp = time.strftime("%Y%m%d-%H%M%S", time.gmtime(now))
        micros = int((now % 1) * 1_000_000)
        short = uuid.uuid4().hex[:8]
        return f"{stamp}-{micros:06d}-{short}"

    @staticmethod
    def _now_iso() -> str:
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def history_for(cache_dir_override: Path | None = None) -> History:
    from .config import cache_dir as default_cache

    return History(cache_dir_override or default_cache())
