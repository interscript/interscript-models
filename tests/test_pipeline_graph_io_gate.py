"""WO83 — the graph-IO dtype gate: no artifact ships fp16 at the graph
boundary (weights may stay fp16; ruby has no Float16 and node ORT
corrupts the boundary — WO79).
"""

from __future__ import annotations

import zipfile
from pathlib import Path

import onnx
from onnx import TensorProto, helper

from pipeline.gates import GateContext, GraphIoGate, registered_gates


def _save_graph(path: Path, in_type: int, out_type: int) -> None:
    g = helper.make_graph(
        [helper.make_node("Cast", ["x"], ["c1"], to=TensorProto.FLOAT),
         helper.make_node("Cast", ["c1"], ["y"], to=out_type)],
        "g",
        [helper.make_tensor_value_info("x", in_type, [2, 2])],
        [helper.make_tensor_value_info("y", out_type, [2, 2])],
    )
    m = helper.make_model(g, opset_imports=[helper.make_opsetid("", 14)])
    m.ir_version = 10
    onnx.save(m, str(path))


def _artifact(tmp_path: Path, in_type: int, out_type: int) -> Path:
    graph = tmp_path / "encoder.onnx"
    _save_graph(graph, in_type, out_type)
    art = tmp_path / "artifact.zip"
    with zipfile.ZipFile(art, "w") as z:
        z.writestr("metadata.yaml", "format: imf-v1\n")
        z.write(graph, "encoder.onnx")
    return art


def test_graph_io_gate_is_registered() -> None:
    assert "graph_io" in registered_gates()


def test_fp16_boundary_fails(tmp_path: Path) -> None:
    art = _artifact(tmp_path, TensorProto.FLOAT16, TensorProto.FLOAT16)
    result = GraphIoGate().check(
        recipe=None, ctx=GateContext(extra={"artifact_path": str(art)}))
    assert not result.passed
    assert "fp16" in result.detail


def test_fp32_boundary_passes(tmp_path: Path) -> None:
    art = _artifact(tmp_path, TensorProto.FLOAT, TensorProto.FLOAT)
    result = GraphIoGate().check(
        recipe=None, ctx=GateContext(extra={"artifact_path": str(art)}))
    assert result.passed


def test_fp16_weights_with_fp32_boundary_pass(tmp_path: Path) -> None:
    """The WO79 shape: fp16 graph math inside, fp32 IO — legal."""
    art = tmp_path / "artifact.zip"
    graph = tmp_path / "encoder.onnx"
    g = helper.make_graph(
        [helper.make_node("Cast", ["x"], ["h"], to=TensorProto.FLOAT16),
         helper.make_node("Cast", ["h"], ["y_raw"], to=TensorProto.FLOAT16),
         helper.make_node("Cast", ["y_raw"], ["y"], to=TensorProto.FLOAT)],
        "g",
        [helper.make_tensor_value_info("x", TensorProto.FLOAT, [2, 2])],
        [helper.make_tensor_value_info("y", TensorProto.FLOAT, [2, 2])],
    )
    m = helper.make_model(g, opset_imports=[helper.make_opsetid("", 14)])
    m.ir_version = 10
    onnx.save(m, str(graph))
    with zipfile.ZipFile(art, "w") as z:
        z.writestr("metadata.yaml", "format: imf-v1\n")
        z.write(graph, "encoder.onnx")
    result = GraphIoGate().check(
        recipe=None, ctx=GateContext(extra={"artifact_path": str(art)}))
    assert result.passed


def test_missing_artifact_notes_without_failing() -> None:
    result = GraphIoGate().check(recipe=None, ctx=GateContext())
    assert result.passed
    assert "not evaluated" in result.detail
