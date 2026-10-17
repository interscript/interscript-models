"""WO52 M1 — the HF Jobs runner.

The campaign's operational laws live here so no human or agent
re-derives them: jobs always detach and carry an explicit timeout
floored at 4h; job commands travel as literal argv (never shell-joined
— IFS-split assembly once produced silently-dead jobs); launches are
refused at the 2-concurrent-training budget unless forced; dry-run
prints the exact argv and spawns nothing.
"""

from __future__ import annotations

import re
import shlex
import subprocess
from dataclasses import dataclass, field

DEFAULT_TIMEOUT_H = 23
MIN_TIMEOUT_H = 4
MAX_CONCURRENT_RUNS = 2


class ConcurrencyLimit(RuntimeError):
    pass


@dataclass
class Volume:
    url: str
    mount: str
    mode: str = "rw"


@dataclass
class JobSpec:
    name: str
    command: list[str]
    flavor: str = "l4x1"
    timeout_h: int = DEFAULT_TIMEOUT_H
    volumes: list[Volume] = field(default_factory=list)
    secrets: list[str] = field(default_factory=lambda: ["HF_TOKEN"])
    env: dict[str, str] = field(default_factory=dict)
    image: str = "python:3.12"


class Runner:
    def __init__(self, hf_bin: str = "hf") -> None:
        self.hf_bin = hf_bin

    def build_argv(self, spec: JobSpec) -> list[str]:
        if spec.timeout_h < MIN_TIMEOUT_H:
            raise ValueError(
                f"timeout {spec.timeout_h}h below the {MIN_TIMEOUT_H}h floor — "
                "HF's short defaults kill trainers; always set an explicit timeout"
            )
        argv = [self.hf_bin, "jobs", "run", spec.image]
        for v in spec.volumes:
            argv += ["-v", f"{v.url}:{v.mount}:{v.mode}"]
        argv += ["--flavor", spec.flavor]
        for s in spec.secrets:
            argv += ["--secrets", s]
        for k, val in spec.env.items():
            argv += ["-e", f"{k}={val}"]
        argv += ["--name", spec.name, "--timeout", f"{spec.timeout_h}h", "-d", "--"]
        argv += list(spec.command)
        return argv

    def running_run_jobs(self) -> list[str]:
        out = subprocess.run(
            [self.hf_bin, "jobs", "ps"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        names = []
        for line in out.splitlines()[1:]:
            m = re.match(r"^\S+\s+(\S+)\s", line)
            if m and "RUNNING" in line:
                names.append(m.group(1))
        return [n for n in names if n.startswith("run-")]

    def launch(
        self,
        spec: JobSpec,
        dry_run: bool = False,
        force: bool = False,
    ) -> str | None:
        if not dry_run and not force:
            running = self.running_run_jobs()
            if len(running) >= MAX_CONCURRENT_RUNS:
                raise ConcurrencyLimit(
                    f"{len(running)} run-* jobs already RUNNING "
                    f"(budget ≤ {MAX_CONCURRENT_RUNS} concurrent training runs); "
                    "wait for a slot or pass force=True"
                )
        argv = self.build_argv(spec)
        if dry_run:
            print(" ".join(shlex.quote(a) for a in argv))
            return None
        proc = subprocess.run(argv, capture_output=True, text=True)
        if proc.returncode != 0:
            raise RuntimeError(f"hf jobs run failed: {proc.stderr.strip()}")
        m = re.search(r"\bid=(\S+)", proc.stdout)
        return m.group(1) if m else None
