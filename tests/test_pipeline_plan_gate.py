"""WO52 M2 — planner (recipe→job translation) + gates.

Proof lane: the shipped urd-diac recipe must plan to a budget-guarded,
law-encoded job and its gate must PASS against the real run-066
verdicts while CORRECTLY refusing to publish on the UNVERIFIED
license. Stages with a legacy route become jobs; stages without a
route are metadata (decode policy travels with the artifact).
"""

from __future__ import annotations

import json
from pathlib import Path

from pipeline.contracts import load_recipe
from pipeline.gates import evaluate
from pipeline.planner import plan_stage

REPO = Path(__file__).parent.parent
RECIPES = REPO / "recipes"
CORPORA = REPO / "corpora"


def test_plan_sft_stage_builds_lawful_job() -> None:
    recipe = load_recipe(RECIPES / "urd-diac.yaml")
    sft = recipe.stages[0]
    spec = plan_stage(recipe, sft, run="run-066-urd-diac-base")
    assert spec.name == "run-066-urd-diac-base"
    assert spec.command[0] == "bash" and spec.command[1] == "-c"
    assert spec.command[2].endswith("train_urd_diac_base_hf.py")
    mounts = [v.mount for v in spec.volumes]
    assert "/ckpt" in mounts and "/data-dia" in mounts
    ro = {v.mount: v.mode for v in spec.volumes}
    assert ro["/data-dia"] == "ro" and ro["/ckpt"] == "rw"
    assert spec.env["U_EPOCHS"] == "2"
    assert spec.env["U_RUN"] == "run-066-urd-diac-base"


def test_plan_params_map_to_script_env() -> None:
    recipe = load_recipe(RECIPES / "urd-diac.yaml")
    spec = plan_stage(recipe, recipe.stages[0], run="r1")
    assert spec.env["U_BS"] == "16" and spec.env["U_ACCUM"] == "2"


def test_metadata_stage_yields_no_job() -> None:
    recipe = load_recipe(RECIPES / "urd-diac.yaml")
    assert plan_stage(recipe, recipe.stages[1], run="r1") is None


def test_env_prefix_and_dataset_mounts() -> None:
    recipe = load_recipe(RECIPES / "ara-diac.yaml")
    relabel = plan_stage(recipe, recipe.stages[0], run="run-x")
    assert relabel is not None
    assert relabel.env["D_SUBSET"] == "300000"
    assert relabel.env["D_RUN"] == "run-x"
    urls = {v.url for v in relabel.volumes}
    assert "hf://datasets/Interscript/arabic-r8" in urls
    mounts = {v.mount: v.mode for v in relabel.volumes}
    assert mounts["/train_data"] == "ro" and mounts["/ckpt"] == "rw"
    sft = plan_stage(recipe, recipe.stages[1], run="run-x")
    assert sft.env["O_EPOCHS"] == "2" and sft.env["O_RUN"] == "run-x"


def test_quality_gate() -> None:
    recipe = load_recipe(RECIPES / "urd-diac.yaml")
    ok = evaluate(recipe, CORPORA, metrics={"cer": 0.0352}, parity=None)
    q = [g for g in ok if g.name == "quality"][0]
    assert q.passed
    bad = evaluate(recipe, CORPORA, metrics={"cer": 0.05}, parity=None)
    assert not [g for g in bad if g.name == "quality"][0].passed


def test_parity_gate_runtime_mode() -> None:
    recipe = load_recipe(RECIPES / "urd-diac.yaml")
    real_run066 = {
        "ort_single_cer": 0.0352,
        "single_vs_batched_agree": 1.0,
        "agree_bf16_ort": 1.0,
    }
    passed = evaluate(recipe, CORPORA, metrics={"cer": 0.0352}, parity=real_run066)
    p = [g for g in passed if g.name == "parity"][0]
    assert p.passed
    poisoned = {
        "ort_single_cer": 0.1391,
        "single_vs_batched_agree": 0.54,
        "agree_bf16_ort": 0.54,
    }
    failed = evaluate(recipe, CORPORA, metrics={"cer": 0.0352}, parity=poisoned)
    assert not [g for g in failed if g.name == "parity"][0].passed


def test_license_gate_blocks_publish(tmp_path: Path) -> None:
    # the shipped urd-dia is owner-waived (2026-10-18) and must PASS now
    recipe = load_recipe(RECIPES / "urd-diac.yaml")
    waived = evaluate(recipe, CORPORA, metrics={"cer": 0.0352}, parity=None)
    assert [g for g in waived if g.name == "license"][0].passed
    # an UNWAIVED restricted source still blocks — synthetic registry
    import yaml as _yaml

    corpus = {
        "id": "xx-src",
        "task": "diacritization",
        "sources": [{"kind": "bucket", "id": "org/data",
                     "license": "LicenseRef-unresolved"}],
        "splits": {
            "train": {"path": "train.jsonl", "rows": 10},
            "test": {"path": "test.jsonl", "rows": 5},
        },
    }
    rec = {
        "id": "xx-diac",
        "task": "diacritization",
        "corpora": {"train": "xx-src@v1", "test": "xx-src@v1#test"},
        "model": "byt5-small",
        "stages": [{"stage": "sft", "params": {"epochs": 1}}],
        "gates": {"quality": {"cer_max": 0.1}, "convention": "row-mean",
                  "parity": {"agree_min": 0.98}},
    }
    (tmp_path / "corpora").mkdir()
    (tmp_path / "recipes").mkdir()
    (tmp_path / "corpora" / "xx-src.yaml").write_text(_yaml.safe_dump(corpus))
    (tmp_path / "recipes" / "xx-diac.yaml").write_text(_yaml.safe_dump(rec))
    results = evaluate(load_recipe(tmp_path / "recipes" / "xx-diac.yaml"),
                       tmp_path / "corpora", metrics={"cer": 0.05}, parity=None)
    lic = [g for g in results if g.name == "license"][0]
    assert not lic.passed
    assert "owner review" in lic.detail


def test_gate_results_files_end_to_end(tmp_path: Path) -> None:
    metrics = tmp_path / "metrics.json"
    parity = tmp_path / "parity.json"
    metrics.write_text(json.dumps({"cer": 0.0352}))
    parity.write_text(
        json.dumps(
            {
                "ort_single_cer": 0.0352,
                "single_vs_batched_agree": 1.0,
                "agree_bf16_ort": 1.0,
            }
        )
    )
    recipe = load_recipe(RECIPES / "urd-diac.yaml")
    results = evaluate(
        recipe,
        CORPORA,
        metrics=json.loads(metrics.read_text()),
        parity=json.loads(parity.read_text()),
    )
    by_name = {g.name: g.passed for g in results}
    assert by_name == {"quality": True, "parity": True, "license": True}


def test_plan_wraps_legacy_deps() -> None:
    """The first dogfooded launch (stage-2, 6ad494b9) died on a bare
    python command — the spine must install the recipe's deps."""
    recipe = load_recipe(RECIPES / "ara-diac.yaml")
    spec = plan_stage(recipe, recipe.stages[1], run="run-x")
    assert spec.command[0] == "bash" and spec.command[1] == "-c"
    cmd = spec.command[2]
    assert cmd.startswith("pip install -q ")
    assert "torch==" in cmd and "transformers==" in cmd
    assert cmd.endswith("python /ckpt/run-x/continue_oracle_train_hf.py")
