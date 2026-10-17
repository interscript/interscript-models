"""WO52 M2 — machine-checkable gates.

Gates evaluate in the runtime's actual decode mode (WO51): the parity
gate reads single-row ORT results, never a batched harness. A missing
result fails the gate — silence is never success.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pipeline.contracts import RecipeSpec, load_corpus


@dataclass
class GateResult:
    name: str
    passed: bool
    detail: str


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
        corpus = load_corpus(Path(corpora_dir) / f"{name}.yaml")
        bad = [s for s in corpus.sources if s.license == "UNVERIFIED"]
        if bad:
            ids = ", ".join(s.id for s in bad)
            return GateResult(
                "license",
                False,
                f"corpus '{name}': UNVERIFIED license ({ids}) — "
                "resolve provenance before publishing",
            )
    return GateResult("license", True, f"corpora {sorted(names)} licensed")


def evaluate(
    recipe: RecipeSpec,
    corpora_dir: Path,
    metrics: dict | None = None,
    parity: dict | None = None,
) -> list[GateResult]:
    return [
        check_quality(recipe, metrics),
        check_parity(recipe, parity),
        check_license(recipe, corpora_dir),
    ]
