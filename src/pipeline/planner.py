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
            if src.kind == "gh-release":
                continue  # release assets are fetched at runtime, not mounted
            url = (
                f"hf://buckets/{src.id}"
                if src.kind == "bucket"
                else f"hf://datasets/{src.id}"
            )
            mount = src.mount or f"/data/{idx}"
            volumes.append(Volume(url, mount, "ro"))
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
