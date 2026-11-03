"""WO52 M2 — recipe→job translation.

A stage with a legacy route becomes a budget-guarded JobSpec (script
runs verbatim, params map to the legacy U_* env convention, ckpt
bucket mounts rw, corpus sources mount ro at their declared points).
A stage without a route is metadata — decode policy travels with the
artifact, not as a job.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pipeline.contracts import RecipeSpec, StageSpec, load_corpus
from pipeline.runner import JobSpec, Volume

CKPT_BUCKET = "hf://buckets/Interscript/isx-training"
CKPT_MOUNT = "/ckpt"
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CORPORA_DIR = REPO_ROOT / "corpora"

# Volume providers are a REGISTRY (WO55): a new corpus source kind is a
# registered mount strategy, never an edit to plan_stage. A provider
# returns a Volume or None (skip).
_VOLUME_PROVIDERS: dict[str, Any] = {}


def register_volume_provider(kind: str, provider) -> None:
    _VOLUME_PROVIDERS[kind] = provider


def _bucket_volume(src, idx: int):
    return Volume(f"hf://buckets/{src.id}", src.mount or f"/data/{idx}", "ro")


def _dataset_volume(src, idx: int):
    return Volume(f"hf://datasets/{src.id}", src.mount or f"/data/{idx}", "ro")


def _skip_volume(src, idx: int):
    return None  # release assets are fetched at runtime, not mounted


register_volume_provider("bucket", _bucket_volume)
register_volume_provider("hf-dataset", _dataset_volume)
register_volume_provider("gh-release", _skip_volume)


def plan_stage(
    recipe: RecipeSpec,
    stage: StageSpec,
    run: str,
    corpora_dir: Path | None = None,
    flavor: str = "a100-large",
    timeout_h: int = 23,
    image: str = "python:3.12",
) -> JobSpec | None:
    if not stage.route:
        return None
    corpora_dir = corpora_dir or DEFAULT_CORPORA_DIR
    script = stage.route.split(":", 1)[-1].rsplit("/", 1)[-1]
    prefix = stage.env_prefix
    env = {f"{prefix}_{k.upper()}": str(v) for k, v in stage.params.items()}
    env[f"{prefix}_RUN"] = run
    # legacy scripts need their wheels; the recipe declares them and the
    # planner installs before exec (the bare-python launch, 6ad494b9,
    # died on `No module named torch` — this is that scar, encoded)
    bootstrap = "pip install -q " + " ".join(recipe.deps)
    command = ["bash", "-c", f"{bootstrap} && python {CKPT_MOUNT}/{run}/{script}"]
    volumes = [Volume(CKPT_BUCKET, CKPT_MOUNT, "rw")]
    seen: set[str] = set()
    idx = 0
    for ref in recipe.corpora.values():
        name = ref.split("@", 1)[0]
        if name in seen:
            continue
        seen.add(name)
        corpus = load_corpus(corpora_dir / f"{name}.yaml")
        for src in corpus.sources:
            provider = _VOLUME_PROVIDERS.get(src.kind)
            if provider is None:
                raise ValueError(
                    f"corpus '{corpus.id}': no volume provider for source "
                    f"kind '{src.kind}' (registered: "
                    f"{sorted(_VOLUME_PROVIDERS)}) — register one via "
                    "register_volume_provider"
                )
            vol = provider(src, idx)
            if vol is not None:
                volumes.append(vol)
                idx += 1
    return JobSpec(
        name=run,
        command=command,
        flavor=flavor,
        timeout_h=timeout_h,
        volumes=volumes,
        env=env,
        image=image,
    )
