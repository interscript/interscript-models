"""WO52 M5 — conformance fixtures: the client-side IMF contract.

A conformance vectors file pins (model id, decode mode, src -> exact
output). Any runtime — python, ruby, typescript, the API worker — must
reproduce the outputs byte-exactly under the declared decode mode or
the change does not merge (the frozen-fixture rule).

Decode mode for byt5 IMF artifacts is single-row greedy: ids are
byte+3 with trailing EOS (the byt5 byte-table rule — raw text bytes
are silent garbage).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from pipeline.conformance import (
    load_vectors,
    run_conformance,
    validate_vectors,
)

VECTORS = {
    "model": "urd-vocalized-base-1.0",
    "decode": {"mode": "single-row-greedy"},
    "vectors": [
        {"src": "سلام", "out": "سَلَام"},
        {"src": "کتاب", "out": "کِتَاب"},
    ],
}


def test_validate_vectors_accepts_good(tmp_path: Path) -> None:
    p = tmp_path / "v.json"
    p.write_text(json.dumps(VECTORS), encoding="utf-8")
    v = load_vectors(p)
    assert v["model"] == "urd-vocalized-base-1.0"
    assert validate_vectors(v) == []


def test_validate_vectors_rejects_missing_fields(tmp_path: Path) -> None:
    bad = {"vectors": [{"src": "x"}]}
    p = tmp_path / "v.json"
    p.write_text(json.dumps(bad), encoding="utf-8")
    with pytest.raises(ValueError, match="model"):
        load_vectors(p)
    problems = validate_vectors(dict(VECTORS, vectors=[{"src": "x"}]))
    assert any("out" in q for q in problems)
    assert any("empty" in q for q in validate_vectors(dict(VECTORS, vectors=[])))


def test_conformance_passes_byte_exact() -> None:
    expected = {v["src"]: v["out"] for v in VECTORS["vectors"]}
    res = run_conformance(VECTORS, decode=expected.__getitem__)
    assert res.passed
    assert res.checked == 2
    assert res.mismatches == []


def test_conformance_reports_mismatch_row() -> None:
    res = run_conformance(VECTORS, decode=lambda s: "غلط" if s == "کتاب" else "سَلَام")
    assert not res.passed
    assert res.mismatches[0]["index"] == 1
    assert res.mismatches[0]["expected"] == "کِتَاب"
    assert res.mismatches[0]["got"] == "غلط"
