"""WO73/C3 — the decode-latency budget: perf.decode_ms_per_row declared
in the index entry vs the measured value (ctx.extra["measured"]), which
the bench tool (tools/bench_decode.py) or CI produces.
"""

from __future__ import annotations

from pipeline.gates import BudgetGate, GateContext


def _ctx(perf: dict, measured: dict | None) -> GateContext:
    entry = {"size": 1_000_000, "perf": perf}
    extra = {"index_entry": entry}
    if measured is not None:
        extra["measured"] = measured
    return GateContext(extra=extra)


def test_latency_within_budget_passes() -> None:
    result = BudgetGate().check(
        recipe=None,
        ctx=_ctx({"size_mb": 10, "decode_ms_per_row": 500},
                 {"decode_ms_per_row": 321.5}),
    )
    assert result.passed
    assert "321.5" in result.detail


def test_latency_over_budget_fails() -> None:
    result = BudgetGate().check(
        recipe=None,
        ctx=_ctx({"size_mb": 10, "decode_ms_per_row": 100},
                 {"decode_ms_per_row": 140.0}),
    )
    assert not result.passed
    assert "exceeds" in result.detail


def test_declared_latency_without_measurement_fails() -> None:
    result = BudgetGate().check(
        recipe=None, ctx=_ctx({"size_mb": 10, "decode_ms_per_row": 100}, None))
    assert not result.passed
    assert "never assumed" in result.detail


def test_no_budgets_passes_with_note() -> None:
    result = BudgetGate().check(recipe=None, ctx=_ctx({}, None))
    assert result.passed
    assert "no perf budgets declared" in result.detail
