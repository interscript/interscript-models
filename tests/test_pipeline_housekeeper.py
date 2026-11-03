"""WO56 — housekeeper tests: classify, never delete; dry-run default.

The housekeeper's iron law: this module classifies and proposes. It
has no delete capability at all — pruning plans are explicit,
reviewable lists that a separate owner-authorized step consumes.
"""

from __future__ import annotations

from pipeline.housekeeper import classify_run, inventory, prune_plan


def _listing(*names: str) -> list[dict]:
    return [{"name": f"run-x/{n}", "size": 100} for n in names]


def test_complete_run_with_epochs_flags_prune_candidates() -> None:
    inv = classify_run("run-a", _listing(
        "RELABEL_DONE", "best", "epoch-0", "epoch-1", "preds-p047.jsonl"))
    assert inv.complete
    assert inv.epoch_dirs == ["epoch-0", "epoch-1"]
    assert any("prune candidates" in n for n in inv.notes)


def test_incomplete_run_never_flags_prune() -> None:
    inv = classify_run("run-b", _listing("best", "epoch-0"))
    assert not inv.complete
    assert not prune_plan(inventory({"run-b": _listing("best", "epoch-0")})), (
        "an incomplete run must never appear in a prune plan"
    )


def test_prune_plan_keeps_best_and_warns_without_it() -> None:
    inv = inventory({
        "run-a": _listing("TRAIN_DONE", "best", "epoch-0", "epoch-1"),
        "run-c": _listing("GATE_DONE", "epoch-0"),  # complete, no best/
    })
    plan = prune_plan(inv)
    assert "run-a/epoch-0" in plan and "run-a/epoch-1" in plan
    assert "run-c/epoch-0" in plan
    assert any("no best/" in p for p in plan if p.startswith("run-c")), (
        "pruning the only checkpoint of a run must warn loudly"
    )


def test_prune_plan_is_dry_run_only() -> None:
    """The plan is strings; nothing here can touch a filesystem."""
    inv = inventory({"run-a": _listing("TRAIN_DONE", "epoch-0")})
    assert all(isinstance(p, str) for p in prune_plan(inv))
    assert not hasattr(__import__("pipeline.housekeeper",
                                 fromlist=["inventory"]), "delete")
