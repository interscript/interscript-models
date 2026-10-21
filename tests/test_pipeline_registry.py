"""WO55 — extension-point registries: the spine's OCP round.

Before this round, adding a gate, stage type, corpus source kind, or
license policy meant EDITING contracts/gates/planner. After it, each
is a registry: the modules are closed for modification, open for
extension — and the two new gates (conformance, regression) land as
the proof that extension needs no core edits.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from pipeline.contracts import CorpusSpec, RecipeSpec, register_stage_type
from pipeline.gates import evaluate
from pipeline.planner import plan_stage

REPO = Path(__file__).parent.parent
RECIPES = REPO / "recipes"
CORPORA = REPO / "corpora"


def _recipe_body() -> dict:
    return {
        "id": "xx-test",
        "task": "transliteration",
        "corpora": {"train": "xx-src@v1", "test": "xx-src@v1#test"},
        "model": "byt5-small",
        "stages": [{"stage": "sft", "route": "legacy:train_xx.py",
                    "params": {"epochs": 1}}],
        "gates": {
            "quality": {"cer_max": 0.1},
            "convention": "row-mean",
            "anchor": "run-047",
            "parity": {"agree_min": 0.98},
        },
    }


def test_register_stage_type_extends_contracts() -> None:
    register_stage_type("my_custom_stage")
    body = _recipe_body()
    body["stages"] = [{"stage": "my_custom_stage", "params": {"x": 1}}]
    r = RecipeSpec.model_validate(body)  # no edit to contracts needed
    assert r.stages[0].stage == "my_custom_stage"


def test_register_gate_extends_evaluate(tmp_path: Path) -> None:
    from pipeline.gates import BaseGate, GateContext, GateResult, register_gate

    class AlwaysFlag(BaseGate):
        name = "always_flag"

        def check(self, recipe: RecipeSpec, ctx: GateContext) -> GateResult:
            return GateResult(self.name, True, "flagged by test")

    register_gate(AlwaysFlag())
    recipe = load_recipe(tmp_path)
    results = evaluate(recipe, CORPORA, metrics={"cer": 0.05}, parity=None)
    names = {g.name for g in results}
    assert "always_flag" in names, "registry gate must appear without core edits"
    assert "quality" in names and "parity" in names and "license" in names


def load_recipe(tmp_path: Path) -> RecipeSpec:
    import yaml as _yaml

    (tmp_path / "recipes").mkdir(exist_ok=True)
    (tmp_path / "recipes" / "xx-test.yaml").write_text(
        _yaml.safe_dump(_recipe_body()), encoding="utf-8"
    )
    from pipeline.contracts import load_recipe as _load

    return _load(tmp_path / "recipes" / "xx-test.yaml")


def test_conformance_gate_is_registered(tmp_path: Path) -> None:
    recipe = load_recipe(tmp_path)
    # missing conformance input -> gate fails loudly, not silently absent
    results = evaluate(recipe, CORPORA, metrics={"cer": 0.05}, parity=None)
    by_name = {g.name: g for g in results}
    assert "conformance" in by_name
    assert not by_name["conformance"].passed
    # present and valid -> passes
    import json

    vec = tmp_path / "vectors.json"
    vec.write_text(
        json.dumps({"model": "xx", "decode": {"mode": "single-row-greedy"},
                    "vectors": [{"src": "a", "out": "b"}]}),
        encoding="utf-8",
    )
    ok = evaluate(recipe, CORPORA, metrics={"cer": 0.05}, parity=None,
                  conformance_path=vec)
    assert [g for g in ok if g.name == "conformance"][0].passed


def test_regression_gate_flags_against_registry(tmp_path: Path) -> None:
    recipe = load_recipe(tmp_path)
    registry = {"xx-test": {"best": {"cer": 0.01}}}
    results = evaluate(recipe, CORPORA, metrics={"cer": 0.05}, parity=None,
                       registry=registry)
    reg = [g for g in results if g.name == "regression"][0]
    assert reg.passed, "regression is flag-only (owner waives), never blocks"
    assert "0.05" in reg.detail and "0.01" in reg.detail
    # better-than-registry -> clean detail
    better = evaluate(recipe, CORPORA, metrics={"cer": 0.005}, parity=None,
                      registry=registry)
    assert "improves" in [g for g in better if g.name == "regression"][0].detail


def test_volume_provider_registry_extends_planner(tmp_path: Path) -> None:
    from pipeline.planner import register_volume_provider
    from pipeline.runner import Volume

    register_volume_provider("test-kind",
                             lambda src, idx: Volume(f"test://{src.id}",
                                                     f"/test{idx}", "ro"))
    corpus = {
        "id": "xx-src",
        "task": "transliteration",
        "sources": [{"kind": "test-kind", "id": "org/ds", "license": "CC0-1.0"}],
        "splits": {
            "train": {"path": "train.jsonl", "rows": 10},
            "test": {"path": "test.jsonl", "rows": 5},
        },
    }
    CorpusSpec.model_validate(corpus)  # kinds are schema data, not a Literal
    recipe_body = _recipe_body()
    (tmp_path / "corpora").mkdir(exist_ok=True)
    (tmp_path / "corpora" / "xx-src.yaml").write_text(yaml.safe_dump(corpus))
    (tmp_path / "recipes").mkdir(exist_ok=True)
    (tmp_path / "recipes" / "xx-test.yaml").write_text(yaml.safe_dump(recipe_body))
    recipe = load_recipe(tmp_path)  # module helper: writes + loads the recipe
    spec = plan_stage(recipe, recipe.stages[0], run="r1",
                      corpora_dir=tmp_path / "corpora")
    urls = {v.url for v in spec.volumes}
    assert "test://org/ds" in urls, "provider registry must mount new kinds"


def test_license_policy_is_encapsulated() -> None:
    from pipeline.contracts import CorpusSource

    src = CorpusSource.model_validate({
        "kind": "hf-dataset", "id": "o/d", "license": "LicenseRef-x",
        "license_review": {"status": "owner-approved",
                           "date": "2026-10-19", "note": "n"},
    })
    from pipeline.contracts import DEFAULT_LICENSE_POLICY

    assert not DEFAULT_LICENSE_POLICY.blocked(src)
    restricted = CorpusSource.model_validate({
        "kind": "hf-dataset", "id": "o/d", "license": "LicenseRef-y",
        "license_review": {"status": "owner-approved",
                           "date": "2026-10-19", "note": "n"},
    })
    strict = type(DEFAULT_LICENSE_POLICY)(allow_waivers=False)
    assert strict.blocked(restricted), "policies vary without core edits"
