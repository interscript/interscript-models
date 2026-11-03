"""WO56 — the housekeeper: bucket inventory + checkpoint hygiene.

KLF's law, adopted: storage hygiene runs with a DRY-RUN DEFAULT and
never deletes without an explicit allowlist. This module only ever
CLASSIFIES; pruning is a separate, explicitly-authorized step that
takes the inventory as input.

Classification (per run directory on the training bucket):
- terminal marker present (RELABEL_DONE / TRAIN_DONE / GATE_DONE /
  VERIFY_DONE / verdict.json) → complete
- candidate epochs: epoch-N / oepoch-N dirs and best/ dirs
- stray: large files outside a recognized run shape
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

TERMINAL_MARKERS = {
    "RELABEL_DONE", "TRAIN_DONE", "GATE_DONE", "VERIFY_DONE", "EXPORT_DONE",
    "ANATOMY_DONE", "verdict.json", "relabel_stats.json",
}
EPOCH_DIR_PREFIXES = ("epoch-", "oepoch-")


@dataclass
class RunInventory:
    name: str
    complete: bool
    markers: list[str] = field(default_factory=list)
    epoch_dirs: list[str] = field(default_factory=list)
    best_dirs: list[str] = field(default_factory=list)
    files: int = 0
    bytes: int = 0
    notes: list[str] = field(default_factory=list)


def classify_run(name: str, listing: list[dict[str, Any]]) -> RunInventory:
    """listing = HfFileSystem.ls() entries for one run dir (name/size)."""
    inv = RunInventory(name=name, complete=False)
    for entry in listing:
        n = entry["name"].rsplit("/", 1)[-1]
        size = entry.get("size", 0) or 0
        inv.files += 1
        inv.bytes += size
        if n in TERMINAL_MARKERS:
            inv.complete = True
            inv.markers.append(n)
        elif any(n.startswith(p) for p in EPOCH_DIR_PREFIXES):
            inv.epoch_dirs.append(n)
        elif n == "best":
            inv.best_dirs.append(n)
    if not inv.complete:
        inv.notes.append("no terminal marker — possibly still running")
    if inv.epoch_dirs and inv.complete:
        inv.notes.append(
            f"{len(inv.epoch_dirs)} epoch dirs are prune candidates "
            "(keep best/ unless the recipe says otherwise)"
        )
    return inv


def inventory(runs: dict[str, list[dict[str, Any]]]) -> list[RunInventory]:
    return [classify_run(name, listing) for name, listing in sorted(runs.items())]


def prune_plan(inv: list[RunInventory], keep_best: bool = True) -> list[str]:
    """The explicit, reviewable prune list. Dry-run output only —
    executing it is a separate, owner-authorized step."""
    plan: list[str] = []
    for run in inv:
        if run.complete and run.epoch_dirs:
            for d in run.epoch_dirs:
                plan.append(f"{run.name}/{d}")
            if keep_best and not run.best_dirs:
                plan.append(
                    f"{run.name}  (WARNING: no best/ — keep epoch-final)"
                )
    return plan
