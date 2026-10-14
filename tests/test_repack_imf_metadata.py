"""Tests for repack_imf_metadata — the publish-prep pass."""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from repack_imf_metadata import repack_meta, repack_zip, restamp  # noqa: E402


def test_repack_meta_fills_without_clobbering():
    meta = {"metrics": [
        {"name": "cer", "value": 15.65, "protocol": "existing",
         "source": "old"},
        {"name": "em", "value": 33.6, "source": "old"},
    ]}
    meta, yb = repack_meta(meta, b"readme", "proto-x", "anchor-x", 500, 0.02)
    assert meta["metrics"][0]["protocol"] == "existing"  # preserved
    assert meta["metrics"][1]["protocol"] == "proto-x"   # filled
    assert meta["metrics"][0]["source"] == "anchor-x"
    assert meta["parity"] == {"samples": 500, "cer_delta": 0.02}
    assert yaml.safe_load(yb)["parity"]["samples"] == 500


def test_repack_zip_idempotent_members(tmp_path):
    src = tmp_path / "m.zip"
    with zipfile.ZipFile(src, "w") as z:
        z.writestr("metadata.yaml", b"a: 1")
        z.writestr("encoder.onnx", b"\x00onnx")
    meta, yb = repack_meta({"metrics": []}, b"README", "p", "a", 500, 0.0)
    out = tmp_path / "out.zip"
    size, sha = repack_zip(src, out, yb, b"README")
    with zipfile.ZipFile(out) as z:
        assert z.namelist() == ["metadata.yaml", "encoder.onnx", "README.md"]
        assert z.read("encoder.onnx") == b"\x00onnx"  # graph bytes untouched
        assert z.read("README.md") == b"README"
    assert size == out.stat().st_size
    assert len(sha) == 64


def test_restamp_updates_exactly_one_entry(tmp_path):
    p = tmp_path / "models.yaml"
    p.write_text(
        "m-1:\n    sha256: " + "a" * 64 + "\n    size: 100\n"
        "m-2:\n    sha256: " + "b" * 64 + "\n    size: 200\n")
    restamp(p, "m-1", "c" * 64, 300)
    s = p.read_text()
    assert "c" * 64 in s and "a" * 64 not in s
    assert "b" * 64 in s  # untouched


def test_restamp_rejects_missing_entry(tmp_path):
    p = tmp_path / "models.yaml"
    p.write_text("m-1:\n    sha256: " + "a" * 64 + "\n    size: 100\n")
    try:
        restamp(p, "nope", "c" * 64, 300)
        raised = False
    except SystemExit:
        raised = True
    assert raised
