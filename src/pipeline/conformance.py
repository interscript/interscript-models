"""WO52 M5 — conformance fixtures: the client-side IMF contract.

A vectors file pins (model, decode mode, src -> exact output); every
runtime must reproduce the outputs byte-exactly under the declared
decode mode. The ONNX decoder implements the single-row greedy byt5
path (ids byte+3 with trailing EOS) — the mode WO51 proved to be the
artifact contract.
"""

from __future__ import annotations

import json
import os
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


def validate_vectors(v: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    if not v.get("model"):
        problems.append("missing 'model' (the models.yaml id)")
    mode = (v.get("decode") or {}).get("mode")
    if mode != "single-row-greedy":
        problems.append(f"decode.mode must be 'single-row-greedy', got {mode!r}")
    vectors = v.get("vectors")
    if not vectors:
        problems.append("'vectors' is empty — a fixture pins at least one row")
        return problems
    for i, row in enumerate(vectors):
        if not row.get("src"):
            problems.append(f"vectors[{i}]: missing 'src'")
        if "out" not in row:
            problems.append(f"vectors[{i}]: missing 'out' (expected output)")
    return problems


def load_vectors(path: Path) -> dict[str, Any]:
    v = json.loads(Path(path).read_text(encoding="utf-8"))
    problems = validate_vectors(v)
    if problems:
        raise ValueError(f"invalid conformance vectors: {'; '.join(problems)}")
    return v


@dataclass
class ConformanceResult:
    model: str
    passed: bool
    checked: int
    mismatches: list[dict] = field(default_factory=list)


def run_conformance(
    vectors: dict[str, Any], decode: Callable[[str], str]
) -> ConformanceResult:
    rows = vectors["vectors"]
    mismatches = []
    for i, row in enumerate(rows):
        got = decode(row["src"])
        if got != row["out"]:
            mismatches.append(
                {"index": i, "src": row["src"], "expected": row["out"], "got": got}
            )
    return ConformanceResult(
        model=vectors["model"],
        passed=not mismatches,
        checked=len(rows),
        mismatches=mismatches,
    )


def ort_single_row_decoder(zip_path: Path) -> Callable[[str], str]:
    """The reference decoder: IMF zip, single-row greedy byt5 decode.

    Import-lazy so the pure logic above is testable without onnxruntime.
    """
    import tempfile
    import zipfile

    import numpy as np

    tmp = Path(tempfile.mkdtemp())
    with zipfile.ZipFile(zip_path) as z:
        for name in ("encoder.onnx", "decoder.onnx"):
            (tmp / name).write_bytes(z.read(name))
    import onnxruntime as ort

    opts = ort.SessionOptions()
    opts.intra_op_num_threads = max(1, (os.cpu_count() or 1) // 2)
    es = ort.InferenceSession(str(tmp / "encoder.onnx"), opts,
                              providers=["CPUExecutionProvider"])
    ds = ort.InferenceSession(str(tmp / "decoder.onnx"), opts,
                              providers=["CPUExecutionProvider"])
    enc_in = es.get_inputs()[0].name
    dec_in = [i.name for i in ds.get_inputs()]

    def decode(src: str) -> str:
        ids = np.array([[b + 3 for b in src.encode("utf-8")] + [1]],
                       dtype=np.int64)  # byte+3, trailing EOS
        h = es.run(None, {enc_in: ids})[0]
        cur = np.zeros((1, 1), dtype=np.int64)
        seq: list[int] = []
        for _ in range(512):
            lg = ds.run(None, {dec_in[0]: cur, dec_in[1]: h})[0]
            t = int(lg[:, -1, :].argmax(-1)[0])
            if t == 1:
                break
            seq.append(t)
            cur = np.concatenate([cur, [[t]]], 1)
        return bytes(max(0, t - 3) for t in seq).decode("utf-8", "replace")

    return decode
