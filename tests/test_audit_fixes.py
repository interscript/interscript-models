"""Framework audit fixes (2026-10-18):

G2 — metric convention is schema-required. The fas saga (five arms
reproducing 0.60-0.81% against a recorded 0.52%) proved that a gate
number without its aggregation convention is not a gate: row-mean and
corpus-level CER differ by ~0.2 points on this data.

G3 — the publish last-mile refuses to run without an explicit owner
version, green gates (license strict), and conformance fixtures.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from pipeline.contracts import CorpusSpec, _license_blocked_source, load_recipe
from pipeline.publish import PublishRefusal, check_publish_ready

REPO = Path(__file__).parent.parent
RECIPES = REPO / "recipes"
CORPORA = REPO / "corpora"


def test_gate_convention_required() -> None:
    body = {
        "id": "xx-test",
        "task": "transliteration",
        "corpora": {"train": "xx-src@v1", "test": "xx-src@v1#test"},
        "model": "byt5-small",
        "stages": [{"stage": "sft", "params": {"epochs": 1}}],
        "gates": {"quality": {"cer_max": 0.1}, "parity": {"agree_min": 0.98}},
    }
    with pytest.raises(ValueError, match="convention"):
        __import__("pipeline.contracts", fromlist=["RecipeSpec"]).RecipeSpec.model_validate(body)


def test_shipped_recipes_declare_convention() -> None:
    for rpath in sorted(RECIPES.glob("*.yaml")):
        r = load_recipe(rpath)
        assert r.gates.convention in ("row-mean", "corpus-level"), rpath


def _tmp_registry(tmp_path: Path, license_value: str) -> Path:
    corpus = {
        "id": "xx-src",
        "task": "transliteration",
        "sources": [{"kind": "hf-dataset", "id": "org/ds", "license": license_value}],
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
        "gates": {
            "quality": {"cer_max": 0.1},
            "parity": {"agree_min": 0.98},
            "convention": "row-mean", "anchor": "run-047",
        },
    }
    (tmp_path / "corpora").mkdir()
    (tmp_path / "recipes").mkdir()
    (tmp_path / "corpora" / "xx-src.yaml").write_text(yaml.safe_dump(corpus))
    (tmp_path / "recipes" / "xx-test.yaml").write_text(yaml.safe_dump(recipe))
    return tmp_path


def test_publish_refuses_moving_version(tmp_path: Path) -> None:
    reg = _tmp_registry(tmp_path, "CC0-1.0")
    recipe = load_recipe(reg / "recipes" / "xx-test.yaml")
    with pytest.raises(PublishRefusal, match="version"):
        check_publish_ready(
            recipe,
            reg / "corpora",
            version="latest",
            metrics={"cer": 0.05},
            parity={"ort_single_cer": 0.05, "single_vs_batched_agree": 1.0,
                    "agree_bf16_ort": 1.0},
            conformance_path=reg / "vectors.json",
        )


def test_publish_refuses_blocked_license(tmp_path: Path) -> None:
    reg = _tmp_registry(tmp_path, "LicenseRef-non-commercial")
    recipe = load_recipe(reg / "recipes" / "xx-test.yaml")
    with pytest.raises(PublishRefusal, match="owner review"):
        check_publish_ready(
            recipe,
            reg / "corpora",
            version="1.0.0",
            metrics={"cer": 0.05},
            parity={"ort_single_cer": 0.05, "single_vs_batched_agree": 1.0,
                    "agree_bf16_ort": 1.0},
            conformance_path=reg / "vectors.json",
        )


def test_publish_refuses_failing_quality(tmp_path: Path) -> None:
    reg = _tmp_registry(tmp_path, "CC0-1.0")
    recipe = load_recipe(reg / "recipes" / "xx-test.yaml")
    with pytest.raises(PublishRefusal, match="quality"):
        check_publish_ready(
            recipe,
            reg / "corpora",
            version="1.0.0",
            metrics={"cer": 0.5},
            parity={"ort_single_cer": 0.05, "single_vs_batched_agree": 1.0,
                    "agree_bf16_ort": 1.0},
            conformance_path=reg / "vectors.json",
        )


def test_publish_refuses_missing_conformance(tmp_path: Path) -> None:
    reg = _tmp_registry(tmp_path, "CC0-1.0")
    recipe = load_recipe(reg / "recipes" / "xx-test.yaml")
    with pytest.raises(PublishRefusal, match="conformance"):
        check_publish_ready(
            recipe,
            reg / "corpora",
            version="1.0.0",
            metrics={"cer": 0.05},
            parity={"ort_single_cer": 0.05, "single_vs_batched_agree": 1.0,
                    "agree_bf16_ort": 1.0},
            conformance_path=None,
        )


def test_publish_ready_happy_path(tmp_path: Path) -> None:
    reg = _tmp_registry(tmp_path, "CC0-1.0")
    (reg / "vectors.json").write_text(
        json.dumps({"model": "xx", "vectors": [{"src": "a", "out": "b"}]})
    )
    recipe = load_recipe(reg / "recipes" / "xx-test.yaml")
    checks = check_publish_ready(
        recipe,
        reg / "corpora",
        version="1.0.0",
        metrics={"cer": 0.05},
        parity={"ort_single_cer": 0.05, "single_vs_batched_agree": 1.0,
                "agree_bf16_ort": 1.0},
        conformance_path=reg / "vectors.json",
    )
    assert checks["gates"]["license"] is True
    assert checks["conformance"] is True


def test_owner_approved_waiver_opens_the_gate(tmp_path: Path) -> None:
    """Owner decisions 2026-10-18: restricted/unlocated sources may ship
    with a dependency note — but only via an explicit recorded waiver,
    never by loosening the license string itself."""

    corpus = {
        "id": "xx-src",
        "task": "transliteration",
        "sources": [{
            "kind": "hf-dataset",
            "id": "org/ds",
            "license": "LicenseRef-unresolved",
            "license_review": {
                "status": "owner-approved",
                "date": "2026-10-18",
                "note": "ship with dependency note; research-only",
            },
        }],
        "splits": {
            "train": {"path": "train.jsonl", "rows": 10},
            "test": {"path": "test.jsonl", "rows": 5},
        },
    }
    c = CorpusSpec.model_validate(corpus)
    assert not _license_blocked_source(c.sources[0])
    unwaived = dict(corpus["sources"][0])
    unwaived.pop("license_review")
    with pytest.raises(ValueError, match="review"):
        CorpusSpec.model_validate({**corpus, "sources": [unwaived]})
