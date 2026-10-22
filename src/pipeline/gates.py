"""WO52 M2 gates — hardened by WO51, registried by WO55.

Gates are REGISTERED objects: `evaluate()` runs every registered gate
and adding a gate (conformance, regression, a future claims gate) is a
registration, never an edit to this module. Each gate receives a
GateContext; missing inputs fail the gate loudly — silence is never
success.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, ClassVar

from pipeline.contracts import (
    RecipeSpec,
    _license_blocked_source,
    load_corpus,
)


@dataclass
class GateResult:
    name: str
    passed: bool
    detail: str


@dataclass
class GateContext:
    metrics: dict | None = None
    parity: dict | None = None
    corpora_dir: Path | None = None
    conformance_path: Path | None = None
    registry: dict | None = None
    extra: dict[str, Any] = field(default_factory=dict)


class BaseGate:
    name: ClassVar[str] = "gate"

    def check(self, recipe: RecipeSpec, ctx: GateContext) -> GateResult:
        raise NotImplementedError


_REGISTRY: dict[str, BaseGate] = {}


def register_gate(gate: BaseGate) -> None:
    _REGISTRY[gate.name] = gate


def registered_gates() -> list[str]:
    return sorted(_REGISTRY)


# ---- the three proven gates -------------------------------------------------


def check_quality(recipe: RecipeSpec, metrics: dict | None) -> GateResult:
    if metrics is None:
        return GateResult("quality", False, "no metrics provided")
    failures: list[str] = []
    details: list[str] = []
    for key, threshold in recipe.gates.quality.items():
        metric = key.removesuffix("_max")
        value = metrics.get(metric)
        if value is None:
            failures.append(f"metric '{metric}' missing")
        elif value > threshold:
            failures.append(f"{metric} {value} > {key} {threshold}")
        else:
            details.append(f"{metric}={value}<={threshold}")
    if failures:
        return GateResult("quality", False, "; ".join(failures))
    return GateResult("quality", True, ", ".join(details))


def check_parity(recipe: RecipeSpec, parity: dict | None) -> GateResult:
    if parity is None:
        return GateResult("parity", False, "no parity results provided")
    gate = recipe.gates.parity
    if gate.mode == "single-row":
        cer = parity.get("ort_single_cer")
        if cer is None:
            return GateResult(
                "parity",
                False,
                "mode is single-row but no ort_single_cer in results — "
                "the harness must decode the way the runtime decodes",
            )
        agree = parity.get("single_vs_batched_agree")
        if agree is None or agree < gate.agree_min:
            return GateResult(
                "parity",
                False,
                f"single-row agreement {agree} < {gate.agree_min}",
            )
    detail = f"mode={gate.mode} agree={parity.get('single_vs_batched_agree')}"
    if gate.three_way:
        three = parity.get("agree_bf16_ort")
        if three is None or three < gate.agree_min:
            return GateResult(
                "parity",
                False,
                f"three-way bf16/ORT agreement {three} < {gate.agree_min}",
            )
        detail += f" three_way={three}"
    return GateResult("parity", True, detail)


def check_license(recipe: RecipeSpec, corpora_dir: Path) -> GateResult:
    names = {ref.split("@", 1)[0] for ref in recipe.corpora.values()}
    for name in sorted(names):
        try:
            corpus = load_corpus(Path(corpora_dir) / f"{name}.yaml")
        except Exception as e:  # noqa: BLE001 — restricted/unreadable registry entry
            return GateResult("license", False, f"corpus '{name}': {e}")
        bad = [s for s in corpus.sources if _license_blocked_source(s)]
        if bad:
            ids = ", ".join(f"{s.id}={s.license}" for s in bad)
            return GateResult(
                "license",
                False,
                f"corpus '{name}': restricted or unread license ({ids}) — "
                "owner review required before publishing",
            )
    return GateResult("license", True, f"corpora {sorted(names)} licensed")


# ---- gate adapters (registry form of the functions above) -------------------


class QualityGate(BaseGate):
    name = "quality"

    def check(self, recipe: RecipeSpec, ctx: GateContext) -> GateResult:
        return check_quality(recipe, ctx.metrics)


class ParityGate(BaseGate):
    name = "parity"

    def check(self, recipe: RecipeSpec, ctx: GateContext) -> GateResult:
        return check_parity(recipe, ctx.parity)


class LicenseGate(BaseGate):
    name = "license"

    def check(self, recipe: RecipeSpec, ctx: GateContext) -> GateResult:
        return check_license(recipe, ctx.corpora_dir)


# ---- WO55 gates (exist because the registry makes them cheap) ---------------


class ConformanceGate(BaseGate):
    """The frozen-fixture gate: a model ships conformance vectors or it
    does not pass. Validated against the vectors schema; byte-exact
    execution stays with `isxml conformance` (needs the artifact)."""

    name = "conformance"

    def check(self, recipe: RecipeSpec, ctx: GateContext) -> GateResult:
        from pipeline.conformance import validate_vectors

        if ctx.conformance_path is None:
            return GateResult(
                "conformance",
                False,
                "no conformance vectors file — a model ships frozen "
                "fixtures or not at all",
            )
        path = Path(ctx.conformance_path)
        if not path.is_file():
            return GateResult("conformance", False,
                              f"vectors file missing: {path}")
        import json

        vectors = json.loads(path.read_text(encoding="utf-8"))
        problems = validate_vectors(vectors)
        if problems:
            return GateResult("conformance", False, "; ".join(problems))
        return GateResult(
            "conformance",
            True,
            f"{len(vectors['vectors'])} vectors, "
            f"{vectors['decode']['mode']}",
        )


class RegressionGate(BaseGate):
    """Flag-only comparison against the registry's best-known numbers:
    a candidate worse than the shipped line never blocks silently — it
    flags for the owner to waive (spec L2)."""

    name = "regression"

    def check(self, recipe: RecipeSpec, ctx: GateContext) -> GateResult:
        if not ctx.registry or recipe.id not in ctx.registry:
            return GateResult("regression", True,
                              "no registry baseline for this recipe")
        entry = ctx.registry[recipe.id]
        best = (entry.get("best") or {}) if isinstance(entry, dict) else {}
        flags: list[str] = []
        improves: list[str] = []
        for key in recipe.gates.quality:
            metric = key.removesuffix("_max")
            known = (best.get(metric))
            value = (ctx.metrics or {}).get(metric)
            if known is None or value is None:
                continue
            if value > known:
                flags.append(f"{metric} {value} > best-known {known}")
            elif value < known:
                improves.append(f"{metric} {value} < best-known {known}")
        if flags:
            return GateResult("regression", True,
                              "FLAG (owner waives): " + "; ".join(flags))
        if improves:
            return GateResult("regression", True, "improves: "
                              + "; ".join(improves))
        return GateResult("regression", True, "at parity with registry")




class BudgetGate(BaseGate):
    """C3: declared performance budgets vs actual index values.

    The index entry may declare perf budgets (size_mb today; latency
    budgets ride the fixture decode in CI). A declared budget that the
    actual artifact violates blocks the gate — regressions are release
    failures, not notes."""

    name = "budgets"

    def check(self, recipe: RecipeSpec, ctx: GateContext) -> GateResult:
        entry = (ctx.extra or {}).get("index_entry") or {}
        perf = entry.get("perf") or {}
        size_mb = perf.get("size_mb")
        if size_mb is None:
            return GateResult(self.name, True, "no perf budgets declared")
        size = entry.get("size")
        if size is None:
            return GateResult(self.name, False,
                              "perf.size_mb declared but index has no size")
        actual_mb = size / 1_000_000
        if actual_mb > float(size_mb):
            return GateResult(self.name, False,
                              f"artifact {actual_mb:.1f} MB exceeds the "
                              f"declared {float(size_mb):.1f} MB budget")
        detail = (f"{actual_mb:.1f} MB within the "
                  f"{float(size_mb):.1f} MB budget")

        budget_ms = perf.get("decode_ms_per_row")
        if budget_ms is not None:
            measured = (ctx.extra or {}).get("measured") or {}
            ms = measured.get("decode_ms_per_row")
            if ms is None:
                return GateResult(
                    self.name, False,
                    "perf.decode_ms_per_row declared but never assumed: "
                    "no measurement supplied — run tools/bench_decode.py "
                    "or the CI decode bench")
            if float(ms) > float(budget_ms):
                return GateResult(
                    self.name, False,
                    f"decode {float(ms):.1f} ms/row exceeds the declared "
                    f"{float(budget_ms):.1f} ms/row budget")
            detail += (f"; decode {float(ms):.1f} ms/row within the "
                       f"{float(budget_ms):.1f} ms/row budget")
        return GateResult(self.name, True, detail)


register_gate(QualityGate())
register_gate(ParityGate())
register_gate(LicenseGate())
register_gate(ConformanceGate())
register_gate(RegressionGate())
register_gate(BudgetGate())


def evaluate(
    recipe: RecipeSpec,
    corpora_dir: Path,
    metrics: dict | None = None,
    parity: dict | None = None,
    conformance_path: Path | None = None,
    registry: dict | None = None,
) -> list[GateResult]:
    ctx = GateContext(
        metrics=metrics,
        parity=parity,
        corpora_dir=corpora_dir,
        conformance_path=conformance_path,
        registry=registry,
    )
    return [gate.check(recipe, ctx) for gate in _REGISTRY.values()]
