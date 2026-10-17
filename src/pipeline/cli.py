"""isxml — WO52 pipeline CLI.

Verbs: validate (M0), plan + gate (M2). plan prints the exact,
budget-guarded job argv per executing stage and never launches; gate
evaluates machine-checkable gates and exits nonzero on any failure.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from pipeline.contracts import load_recipe, validate_recipe_dir
from pipeline.gates import evaluate
from pipeline.planner import DEFAULT_CORPORA_DIR, plan_stage
from pipeline.runner import Runner

REPO_ROOT = Path(__file__).resolve().parents[2]


def _recipes_dir(args: argparse.Namespace) -> Path:
    return getattr(args, "recipes", None) or (REPO_ROOT / "recipes")


def _find_recipe(path: Path, recipe_id: str) -> Path:
    candidate = path / f"{recipe_id}.yaml"
    if not candidate.is_file():
        raise SystemExit(f"recipe not found: {candidate}")
    return candidate


def cmd_validate(args: argparse.Namespace) -> int:
    problems = validate_recipe_dir(args.recipes, args.corpora)
    for p in problems:
        print(f"FAIL {p}", file=sys.stderr)
    print(f"{len(problems)} problem(s)")
    return 1 if problems else 0


def cmd_plan(args: argparse.Namespace) -> int:
    recipe = load_recipe(_find_recipe(_recipes_dir(args), args.recipe))
    runner = Runner()
    rc = 0
    for stage in recipe.stages:
        spec = plan_stage(
            recipe,
            stage,
            run=args.run,
            corpora_dir=args.corpora,
            flavor=args.flavor,
        )
        if spec is None:
            print(f"# {stage.stage}: metadata stage — no job")
            continue
        print(f"# {stage.stage}:")
        runner.launch(spec, dry_run=True)
    return rc


def cmd_gate(args: argparse.Namespace) -> int:
    recipe = load_recipe(_find_recipe(_recipes_dir(args), args.recipe))
    metrics = (
        json.loads(Path(args.metrics).read_text(encoding="utf-8"))
        if args.metrics
        else None
    )
    parity = (
        json.loads(Path(args.parity).read_text(encoding="utf-8"))
        if args.parity
        else None
    )
    results = evaluate(recipe, args.corpora, metrics=metrics, parity=parity)
    failed = False
    for g in results:
        mark = "PASS" if g.passed else "FAIL"
        print(f"{mark} {g.name}: {g.detail}")
        failed = failed or not g.passed
    return 1 if failed else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="isxml")
    sub = ap.add_subparsers(dest="cmd", required=True)

    v = sub.add_parser("validate", help="validate corpora/ + recipes/ contracts")
    v.add_argument("--recipes", type=Path, default=REPO_ROOT / "recipes")
    v.add_argument("--corpora", type=Path, default=DEFAULT_CORPORA_DIR)
    v.set_defaults(fn=cmd_validate)

    p = sub.add_parser("plan", help="print the exact job argv per stage (no launch)")
    p.add_argument("recipe", help="recipe id (e.g. urd-diac)")
    p.add_argument("--run", required=True, help="run directory name on the bucket")
    p.add_argument("--flavor", default="a100-large")
    p.add_argument("--recipes", type=Path, default=REPO_ROOT / "recipes")
    p.add_argument("--corpora", type=Path, default=DEFAULT_CORPORA_DIR)
    p.set_defaults(fn=cmd_plan)

    g = sub.add_parser("gate", help="evaluate quality/parity/license gates")
    g.add_argument("recipe", help="recipe id (e.g. urd-diac)")
    g.add_argument("--metrics", help="metrics JSON file (e.g. {\"cer\": 0.0352})")
    g.add_argument("--parity", help="parity JSON file (single-row + three-way)")
    g.add_argument("--recipes", type=Path, default=REPO_ROOT / "recipes")
    g.add_argument("--corpora", type=Path, default=DEFAULT_CORPORA_DIR)
    g.set_defaults(fn=cmd_gate)

    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
