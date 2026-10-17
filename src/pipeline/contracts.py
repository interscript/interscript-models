"""WO52 L0 contracts — corpora and recipes.

A corpus is a pinned, licensed dataset artifact; a recipe is a
per-language DAG of registered stages with machine-checkable gates.
`isxml validate` rejects contract violations before any GPU time is
spent. Standing laws enforced here: test split mandatory, corpus pins
are dates or versions (never moving refs), stages must be
implementable (route or params), and diacritization recipes may never
declare an LLM teacher (TODO.sota/52).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

TaskKind = Literal["diacritization", "g2p", "transliteration"]
METRIC_KEYS = ("cer_max", "wer_max", "per_max")
KNOWN_STAGES = frozenset(
    {"sft", "oracle_relabel", "distill", "decode_policy", "plane", "lexicon_fusion"}
)
LANG_RE = re.compile(r"^[a-z]{2,3}-[a-z0-9-]+$")
CORPUS_REF_RE = re.compile(
    r"^(?P<name>[a-z][a-z0-9-]*)@"
    r"(?P<pin>\d{4}-\d{2}-\d{2}|v\d+(?:\.\d+)*)"
    r"(?:#(?P<split>[a-z0-9-]+))?$"
)
LLM_TEACHER_RE = re.compile(r"llm|gpt|claude|gemini|glm", re.IGNORECASE)


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class CorpusSource(_Strict):
    kind: Literal["hf-dataset", "bucket", "gh-release"]
    id: str
    revision: str | None = None
    sha256: str | None = None
    license: str


class SplitSpec(_Strict):
    path: str
    rows: int | None = Field(default=None, ge=0)
    sha256: str | None = None


class CorpusSpec(_Strict):
    id: str = Field(pattern=LANG_RE.pattern)
    task: TaskKind
    sources: list[CorpusSource] = Field(min_length=1)
    splits: dict[str, SplitSpec]

    @model_validator(mode="after")
    def _splits(self) -> CorpusSpec:
        missing = {"train", "test"} - set(self.splits)
        if missing:
            raise ValueError(
                f"corpus '{self.id}': splits missing {sorted(missing)} "
                "(a held-out test split is mandatory)"
            )
        return self


class ParityGate(_Strict):
    mode: Literal["single-row", "batched-mask"] = "single-row"
    agree_min: float = Field(ge=0.0, le=1.0)
    three_way: bool = True


class GateSpec(_Strict):
    quality: dict[str, float]
    parity: ParityGate
    license: bool = True

    @field_validator("quality")
    @classmethod
    def _metrics(cls, v: dict[str, float]) -> dict[str, float]:
        bad = set(v) - set(METRIC_KEYS)
        if not v or bad:
            raise ValueError(
                f"quality gates: unknown metric key(s) {sorted(bad)}; "
                f"allowed: {', '.join(METRIC_KEYS)} (at least one required)"
            )
        return v


class StageSpec(_Strict):
    stage: str
    route: str | None = None
    params: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _implementable(self) -> StageSpec:
        if self.stage not in KNOWN_STAGES:
            raise ValueError(
                f"unknown stage '{self.stage}'; known: {sorted(KNOWN_STAGES)}"
            )
        if not self.route and not self.params:
            raise ValueError(
                f"stage '{self.stage}' needs route (legacy path) or params — "
                "an unconfigured stage is unimplementable"
            )
        return self


class RecipeSpec(_Strict):
    id: str = Field(pattern=LANG_RE.pattern)
    task: TaskKind
    corpora: dict[Literal["train", "test"], str]
    model: str
    stages: list[StageSpec] = Field(min_length=1)
    gates: GateSpec
    negative_results: list[str] = Field(default_factory=list)
    channel: Literal["gh-releases"] = "gh-releases"

    @field_validator("corpora")
    @classmethod
    def _refs(cls, v: dict[str, str]) -> dict[str, str]:
        for role, ref in v.items():
            if not CORPUS_REF_RE.match(ref):
                raise ValueError(
                    f"corpus {role} ref '{ref}': pin must be a date "
                    "(YYYY-MM-DD) or version (v1[.2]), not a moving ref"
                )
        return v

    @model_validator(mode="after")
    def _laws(self) -> RecipeSpec:
        if self.task == "diacritization":
            for s in self.stages:
                if LLM_TEACHER_RE.search(f"{s.stage} {s.route or ''}"):
                    raise ValueError(
                        "diacritization recipes may not use LLM-teacher "
                        f"stages (standing law): {s.route or s.stage}"
                    )
        return self


def load_recipe(path: Path) -> RecipeSpec:
    body = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return RecipeSpec.model_validate(body)


def load_corpus(path: Path) -> CorpusSpec:
    body = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return CorpusSpec.model_validate(body)


def validate_recipe_dir(recipes_dir: Path, corpora_dir: Path) -> list[str]:
    problems: list[str] = []
    corpora: dict[str, CorpusSpec] = {}
    for cpath in sorted(Path(corpora_dir).glob("*.yaml")):
        try:
            c = load_corpus(cpath)
        except Exception as e:  # noqa: BLE001
            problems.append(f"{cpath.name}: {e}")
            continue
        corpora[c.id] = c
    rpaths = sorted(Path(recipes_dir).glob("*.yaml"))
    if not rpaths:
        problems.append(f"no recipes found in {recipes_dir}")
    for rpath in rpaths:
        try:
            r = load_recipe(rpath)
        except Exception as e:  # noqa: BLE001
            problems.append(f"{rpath.name}: {e}")
            continue
        refs = {CORPUS_REF_RE.match(ref).group("name"): ref for ref in r.corpora.values()}
        for name in refs:
            c = corpora.get(name)
            if c is None:
                problems.append(
                    f"{rpath.name}: corpus '{name}' not found in registry"
                )
                continue
            if c.task != r.task:
                problems.append(
                    f"{rpath.name}: corpus '{c.id}' task '{c.task}' != "
                    f"recipe task '{r.task}'"
                )
            if r.gates.license and any(
                s.license == "UNVERIFIED" for s in c.sources
            ):
                problems.append(
                    f"{rpath.name}: corpus '{c.id}' has UNVERIFIED license — "
                    "resolve before publishing (gates.license)"
                )
    return problems
