"""WO52 publish last-mile — the owner-gated guard layer.

Publishing refuses unless: the version is explicit (never a moving
ref — versions are the owner's decision), every gate is green with
licenses strictly enforced, and a conformance vectors file exists for
the model. The actual artifact publication stays the proven legacy
path (scripts/publish_model.py + the index-vN flow); this module is
the gate that decides whether it may run at all.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from pathlib import Path

from pipeline.contracts import RecipeSpec
from pipeline.gates import evaluate

VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")


class PublishRefusal(RuntimeError):
    pass


def check_publish_ready(
    recipe: RecipeSpec,
    corpora_dir: Path,
    version: str,
    metrics: dict | None,
    parity: dict | None,
    conformance_path: Path | None,
) -> dict:
    if not VERSION_RE.match(version or ""):
        raise PublishRefusal(
            f"version {version!r} is not an explicit semver — versions are "
            "the owner's decision and never a moving ref"
        )
    try:
        results = evaluate(recipe, corpora_dir, metrics=metrics, parity=parity)
    except Exception as e:  # noqa: BLE001 — restricted-corpus schema errors
        raise PublishRefusal(f"license/registry: {e}") from e
    gate_map = {g.name: g.passed for g in results}
    license_detail = next(
        (g.detail for g in results if g.name == "license" and not g.passed), ""
    )
    if not gate_map.get("license", False):
        raise PublishRefusal(f"license gate: {license_detail or 'blocked'}")
    for name in ("quality", "parity"):
        if not gate_map.get(name, False):
            detail = next(g.detail for g in results if g.name == name)
            raise PublishRefusal(f"{name} gate: {detail}")
    if conformance_path is None or not Path(conformance_path).is_file():
        raise PublishRefusal(
            "no conformance vectors file — a model ships frozen fixtures or not at all"
        )
    return {"gates": gate_map, "conformance": True, "version": version}


def run_publisher(
    publisher: Callable[[list[str]], int], argv: list[str]
) -> int:
    """Invoke the injected publisher (legacy scripts/publish_model.py
    adapter) after the guard has passed."""
    return publisher(argv)
