"""WO52 M0 — corpus/recipe contracts: schema + cross-validation laws.

Laws under test (TODO.sota/52):
- every stage declares either a legacy route or params (implementable)
- no LLM-teacher stages for diacritization (validator-enforced ban)
- corpus refs are name@pin[#split]; pin is a date or version, never
  a moving ref ("latest", "main")
- recipe corpus refs resolve into the corpora registry; tasks agree
- license gate: sources with UNVERIFIED license are blocking problems
- shipped corpora/ + recipes/ validate with only enumerated open items
"""

from __future__ import annotations

from pathlib import Path

import pytest

from pipeline.contracts import (
    CorpusSpec,
    RecipeSpec,
    load_corpus,
    load_recipe,
    validate_recipe_dir,
)

FIXTURES = Path(__file__).parent / "fixtures"
RECIPES = Path(__file__).parent.parent / "recipes"
CORPORA = Path(__file__).parent.parent / "corpora"


def test_valid_recipe_loads() -> None:
    r = load_recipe(FIXTURES / "recipes" / "urd-diac.yaml")
    assert r.id == "urd-diac"
    assert r.task == "diacritization"
    assert r.stages[0].stage == "sft"
    assert r.stages[1].params["rep_penalty"] == pytest.approx(1.2)


def test_stage_needs_route_or_params() -> None:
    body = {
        "id": "xx-test",
        "task": "transliteration",
        "corpora": {"train": "xx-src@v1", "test": "xx-src@v1#test"},
        "model": "byt5-small",
        "stages": [{"stage": "sft"}],
        "gates": {"quality": {"cer_max": 0.1}, "convention": "row-mean",
                   "anchor": "run-047",
                   "parity": {"agree_min": 0.98}},
    }
    with pytest.raises(ValueError, match="route"):
        RecipeSpec.model_validate(body)


def test_no_llm_teachers_for_diacritization() -> None:
    body = {
        "id": "xx-diac",
        "task": "diacritization",
        "corpora": {"train": "xx-src@v1", "test": "xx-src@v1#test"},
        "model": "byt5-small",
        "stages": [{"stage": "distill", "route": "legacy:llm_teacher.py"}],
        "gates": {"quality": {"cer_max": 0.1}, "convention": "row-mean",
                   "anchor": "run-047",
                   "parity": {"agree_min": 0.98}},
    }
    with pytest.raises(ValueError, match="llm"):
        RecipeSpec.model_validate(body)


def test_corpus_ref_pin_format() -> None:
    body = {
        "id": "xx-test",
        "task": "transliteration",
        "corpora": {"train": "xx-src@latest", "test": "xx-src@v1#test"},
        "model": "byt5-small",
        "stages": [{"stage": "sft", "params": {"epochs": 1}}],
        "gates": {"quality": {"cer_max": 0.1}, "convention": "row-mean",
                   "anchor": "run-047",
                   "parity": {"agree_min": 0.98}},
    }
    with pytest.raises(ValueError, match="pin"):
        RecipeSpec.model_validate(body)


def test_quality_gate_metric_keys() -> None:
    body = {
        "id": "xx-test",
        "task": "transliteration",
        "corpora": {"train": "xx-src@v1", "test": "xx-src@v1#test"},
        "model": "byt5-small",
        "stages": [{"stage": "sft", "params": {"epochs": 1}}],
        "gates": {"quality": {"bleu_max": 0.1}, "parity": {"agree_min": 0.98}},
    }
    with pytest.raises(ValueError, match="metric"):
        RecipeSpec.model_validate(body)


def test_corpus_spec_requires_train_and_test() -> None:
    body = {
        "id": "xx-src",
        "task": "transliteration",
        "sources": [{"kind": "hf-dataset", "id": "org/ds", "license": "CC-BY-SA-4.0"}],
        "splits": {"train": {"path": "train.jsonl", "rows": 10}},
    }
    with pytest.raises(ValueError, match="test"):
        CorpusSpec.model_validate(body)


def test_recipe_refs_resolve_into_registry(tmp_path: Path) -> None:
    (tmp_path / "recipes").mkdir()
    (tmp_path / "corpora").mkdir()
    recipe = {
        "id": "xx-test",
        "task": "transliteration",
        "corpora": {"train": "xx-src@v1", "test": "xx-src@v1#test"},
        "model": "byt5-small",
        "stages": [{"stage": "sft", "params": {"epochs": 1}}],
        "gates": {"quality": {"cer_max": 0.1}, "convention": "row-mean",
                   "anchor": "run-047",
                   "parity": {"agree_min": 0.98}},
    }
    import yaml  # noqa: PLC0415

    (tmp_path / "recipes" / "xx-test.yaml").write_text(yaml.safe_dump(recipe))
    problems = validate_recipe_dir(tmp_path / "recipes", tmp_path / "corpora")
    assert any("xx-src" in p for p in problems)


def test_unverified_license_is_blocking(tmp_path: Path) -> None:
    corpus = {
        "id": "xx-src",
        "task": "transliteration",
        "sources": [{"kind": "hf-dataset", "id": "org/ds", "license": "UNVERIFIED"}],
        "splits": {
            "train": {"path": "train.jsonl", "rows": 10},
            "test": {"path": "test.jsonl", "rows": 5},
        },
    }
    recipe = {
        "id": "xx-test",
        "task": "transliteration",
        "corpora": {"train": "xx-src@v1", "test": "xx-src@v1#test"},
        "model": "byt5-small",
        "stages": [{"stage": "sft", "params": {"epochs": 1}}],
        "gates": {"quality": {"cer_max": 0.1}, "convention": "row-mean",
                   "anchor": "run-047",
                   "parity": {"agree_min": 0.98}},
    }
    import yaml  # noqa: PLC0415

    (tmp_path / "corpora").mkdir()
    (tmp_path / "recipes").mkdir()
    (tmp_path / "corpora" / "xx-src.yaml").write_text(yaml.safe_dump(corpus))
    (tmp_path / "recipes" / "xx-test.yaml").write_text(yaml.safe_dump(recipe))
    problems = validate_recipe_dir(tmp_path / "recipes", tmp_path / "corpora")
    assert any("UNVERIFIED" in p for p in problems)


def test_shipped_contracts_validate() -> None:
    problems = validate_recipe_dir(RECIPES, CORPORA)
    blocked = [p for p in problems if "owner review" in p]
    unexpected = [p for p in problems if "owner review" not in p]
    assert unexpected == [], f"contract drift: {unexpected}"
    open_corpora = {"urd-dia", "qcri-wiki", "urd-g2p-dict"}
    for p in blocked:
        assert any(c in p for c in open_corpora), p
    assert not any("fas-dia" in p for p in blocked), (
        "fas CC0 verification must keep the fas lane clear"
    )


def test_restricted_but_read_license_blocks(tmp_path: Path) -> None:
    from pipeline.contracts import _license_blocked  # noqa: PLC0415

    assert _license_blocked("LicenseRef-non-commercial")
    assert _license_blocked("LicenseRef-no-license-found")
    assert not _license_blocked("CC0-1.0")
    assert not _license_blocked("GPLv2")

    import yaml  # noqa: PLC0415

    corpus = {
        "id": "xx-src",
        "task": "transliteration",
        "sources": [
            {"kind": "hf-dataset", "id": "org/ds", "license": "LicenseRef-non-commercial"}
        ],
        "splits": {
            "train": {"path": "train.jsonl", "rows": 10},
            "test": {"path": "test.jsonl", "rows": 5},
        },
    }
    recipe = {
        "id": "xx-test",
        "task": "transliteration",
        "corpora": {"train": "xx-src@v1", "test": "xx-src@v1#test"},
        "model": "byt5-small",
        "stages": [{"stage": "sft", "params": {"epochs": 1}}],
        "gates": {"quality": {"cer_max": 0.1}, "convention": "row-mean",
                   "anchor": "run-047",
                   "parity": {"agree_min": 0.98}},
    }
    (tmp_path / "corpora").mkdir()
    (tmp_path / "recipes").mkdir()
    (tmp_path / "corpora" / "xx-src.yaml").write_text(yaml.safe_dump(corpus))
    (tmp_path / "recipes" / "xx-test.yaml").write_text(yaml.safe_dump(recipe))
    problems = validate_recipe_dir(tmp_path / "recipes", tmp_path / "corpora")
    assert any("LicenseRef-non-commercial" in p and "owner review" in p for p in problems)


def test_load_corpus_roundtrip() -> None:
    c = load_corpus(FIXTURES / "corpora" / "urd-dia.yaml")
    assert c.id == "urd-dia"
    assert "train" in c.splits and "test" in c.splits


def test_gate_block_requires_anchor_and_convention() -> None:
    base = {
        "id": "xx-anchor",
        "task": "transliteration",
        "corpora": {"train": "xx-src@v1", "test": "xx-src@v1#test"},
        "model": "byt5-small",
        "stages": [{"stage": "sft", "params": {"epochs": 1}}],
    }
    no_anchor = {
        **base,
        "gates": {"quality": {"cer_max": 0.1}, "convention": "row-mean",
                   "parity": {"agree_min": 0.98}},
    }
    with pytest.raises(ValueError, match="anchor"):
        RecipeSpec.model_validate(no_anchor)

    no_convention = {
        **base,
        "gates": {"quality": {"cer_max": 0.1}, "anchor": "run-047",
                   "parity": {"agree_min": 0.98}},
    }
    with pytest.raises(ValueError, match="convention"):
        RecipeSpec.model_validate(no_convention)
