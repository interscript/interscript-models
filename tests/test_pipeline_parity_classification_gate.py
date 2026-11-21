"""WO92 — the classification parity gate law: per-char classification
artifacts (the plane family) gate on the DER delta vs the fp32
reference on the committed eval slice; the confident-flip criterion
remains a generation-artifact law.

Measured basis (TODO.sota/92 ship-gate round, job heb-wo92-shipgate,
600-row eval600 heb slice, results recorded via PR #458): per-char
flips are expected quantization behavior — int8-dynamic flips 33.8% of
rows and int8-static 48.0% while the DER deltas are +0.05pp and
+1.21pp. A generation artifact's flip means a different generated
string; a classifier's flip means a low-margin character. The gate law
must tell those apart.
"""

from __future__ import annotations

import pytest

from pipeline.contracts import RecipeSpec
from pipeline.gates import check_parity, registered_gates


def _recipe(parity: dict) -> RecipeSpec:
    return RecipeSpec.model_validate({
        "id": "heb-vocalized-plane",
        "task": "diacritization",
        "corpora": {"train": "heb-src@v1", "test": "heb-src@v1#test"},
        "model": "plane-base",
        "stages": [{"stage": "plane", "params": {"classes": 180}}],
        "gates": {
            "quality": {"cer_max": 0.1},
            "convention": "row-mean",
            "anchor": "TODO.sota/92 ship-gate round",
            "parity": parity,
        },
    })


def _classify(parity: dict, recipe: RecipeSpec) -> object:
    return check_parity(recipe, parity)


# ---- contract: the criterion is declared per artifact kind ------------------


def test_classification_gate_declares_no_agree_min() -> None:
    """A classification recipe declares the DER budget and nothing about
    decode-mode agreement — the flip/agreement criterion is not its law."""
    gate = _recipe({"kind": "classification"}).gates.parity
    assert gate.kind == "classification"
    assert gate.der_delta_max_pp == pytest.approx(0.25)
    assert gate.min_samples == 500


def test_generation_gate_still_requires_agree_min() -> None:
    with pytest.raises(ValueError, match="agree_min"):
        _recipe({})


def test_generation_gate_defaults_unchanged() -> None:
    gate = _recipe({"agree_min": 0.98}).gates.parity
    assert gate.kind == "generation"
    assert gate.three_way is True


# ---- the WO92 measured round, gated both ways -------------------------------


def test_int8_dynamic_der_neutral_passes() -> None:
    """The measured int8-dynamic arm: +0.0549pp DER — inside the 0.25pp
    budget on the 600-row slice, while the flip gate scored it FAIL."""
    recipe = _recipe({"kind": "classification"})
    result = _classify(
        {"der_reference_pp": 9.8276, "der_candidate_pp": 9.8825,
         "samples": 600},
        recipe,
    )
    assert result.passed
    assert "0.0549pp" in result.detail
    assert "600 samples" in result.detail


def test_int8_static_der_cost_fails() -> None:
    """The measured int8-static arm: +1.2146pp DER — outside the budget,
    the gate must still catch the arm that actually costs quality."""
    recipe = _recipe({"kind": "classification"})
    result = _classify(
        {"der_reference_pp": 9.8276, "der_candidate_pp": 11.0422,
         "samples": 600},
        recipe,
    )
    assert not result.passed
    assert "1.2146pp" in result.detail
    assert "0.25pp budget" in result.detail


def test_declared_der_delta_passes() -> None:
    recipe = _recipe({"kind": "classification"})
    result = _classify({"der_delta_pp": 0.05, "samples": 600}, recipe)
    assert result.passed


def test_declared_der_delta_over_budget_fails() -> None:
    recipe = _recipe({"kind": "classification"})
    result = _classify({"der_delta_pp": 1.21, "samples": 600}, recipe)
    assert not result.passed


# ---- loud failures: silence is never success --------------------------------


def test_missing_der_inputs_fail_loudly() -> None:
    recipe = _recipe({"kind": "classification"})
    result = _classify({"samples": 600}, recipe)
    assert not result.passed
    assert "der_delta_pp" in result.detail


def test_missing_sample_count_fails_loudly() -> None:
    recipe = _recipe({"kind": "classification"})
    result = _classify({"der_delta_pp": 0.05}, recipe)
    assert not result.passed
    assert "sample count" in result.detail


def test_thin_slice_fails_the_sample_floor() -> None:
    recipe = _recipe({"kind": "classification"})
    result = _classify({"der_delta_pp": 0.05, "samples": 100}, recipe)
    assert not result.passed
    assert "500-sample floor" in result.detail


# ---- the generation law is untouched -----------------------------------------


def test_generation_flip_agreement_path_unchanged() -> None:
    """Generation artifacts keep the existing law: single-row agreement
    (and three-way when declared) — no DER branch, no classification
    fields consulted."""
    recipe = _recipe({"agree_min": 0.98})
    result = _classify(
        {"ort_single_cer": 0.1, "single_vs_batched_agree": 0.99,
         "agree_bf16_ort": 0.99},
        recipe,
    )
    assert result.passed
    assert "classification" not in result.detail

    result = _classify(
        {"ort_single_cer": 0.1, "single_vs_batched_agree": 0.90,
         "agree_bf16_ort": 0.99},
        recipe,
    )
    assert not result.passed
    assert "agreement 0.9 < 0.98" in result.detail


def test_parity_gate_still_registered() -> None:
    assert "parity" in registered_gates()
