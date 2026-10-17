"""WO52 M2 — recipe→job translation.

A stage with a legacy route becomes a budget-guarded JobSpec (script
runs verbatim, params map to the legacy U_* env convention, ckpt
bucket mounts rw, corpus sources mount ro at their declared points).
A stage without a route is metadata — decode policy travels with the
artifact, not as a job.
"""

from __future__ import annotations

from pathlib import Path

from pipeline.contracts import RecipeSpec, StageSpec, load_corpus
from pipeline.runner import JobSpec, Volume

CKPT_BUCKET = "hf://buckets/Interscript/isx-training"
CKPT_MOUNT = "/ckpt"
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CORPORA_DIR = REPO_ROOT / "corpora"


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
    env = {f"U_{k.upper()}": str(v) for k, v in stage.params.items()}
    env["U_RUN"] = run
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
            if src.kind != "bucket":
                continue
            mount = src.mount or f"/data/{idx}"
            volumes.append(Volume(f"hf://buckets/{src.id}", mount, "ro"))
            idx += 1
    return JobSpec(
        name=run,
        command=["python", f"{CKPT_MOUNT}/{run}/{script}"],
        flavor=flavor,
        timeout_h=timeout_h,
        volumes=volumes,
        env=env,
        image=image,
    )
