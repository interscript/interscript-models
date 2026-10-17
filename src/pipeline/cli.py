"""isxml — WO52 pipeline CLI.

M0 scope: contract validation. Later milestones add corpus / train /
gate / publish verbs (TODO.sota/52 migration plan).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pipeline.contracts import validate_recipe_dir


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="isxml")
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("validate", help="validate corpora/ + recipes/ contracts")
    v.add_argument("--recipes", type=Path, default=Path("recipes"))
    v.add_argument("--corpora", type=Path, default=Path("corpora"))
    args = ap.parse_args(argv)

    if args.cmd == "validate":
        problems = validate_recipe_dir(args.recipes, args.corpora)
        for p in problems:
            print(f"FAIL {p}", file=sys.stderr)
        print(f"{len(problems)} problem(s)")
        return 1 if problems else 0
    return 2  # unreachable: subparsers required


if __name__ == "__main__":
    sys.exit(main())
