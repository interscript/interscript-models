"""WO52 M1 — the HF Jobs runner: operational laws as code.

Laws under test (TODO.sota/52 + campaign scars):
- jobs always detach (-d) and always carry an explicit --timeout,
  floored at 4h (HF's short defaults have killed trainers)
- the job command travels as a literal argv tail — never shell-joined
- launches are refused at the 2-concurrent-run budget unless forced
- dry-run prints the exact argv and touches no subprocess
"""

from __future__ import annotations

import subprocess
from types import SimpleNamespace

import pytest

from pipeline.runner import MAX_CONCURRENT_RUNS, JobSpec, Runner, Volume

SPEC = JobSpec(
    name="run-test",
    command=["python", "/ckpt/run-x/train.py", "--epochs", "1"],
    flavor="l4x1",
    volumes=[
        Volume("hf://buckets/Interscript/isx-training", "/ckpt", "rw"),
        Volume("hf://buckets/org/data", "/data", "ro"),
    ],
    env={"U_EPOCHS": "6"},
)


def test_argv_encodes_laws() -> None:
    argv = Runner().build_argv(SPEC)
    joined = " ".join(argv)
    assert "-d" in argv, "jobs must always detach"
    assert "--timeout" in argv and "23h" in joined
    assert "--secrets" in argv and "HF_TOKEN" in argv
    assert "hf://buckets/Interscript/isx-training:/ckpt:rw" in joined
    assert "hf://buckets/org/data:/data:ro" in joined
    assert "-e" in argv and "U_EPOCHS=6" in joined
    assert argv[-len(SPEC.command):] == SPEC.command
    assert "--" in argv[argv.index("--name") :]


def test_timeout_floor() -> None:
    with pytest.raises(ValueError, match="timeout"):
        Runner().build_argv(JobSpec(name="x", command=["true"], timeout_h=1))


def test_dry_run_prints_and_launches_nothing(monkeypatch, capsys) -> None:
    def boom(*a, **k):  # noqa: ARG001
        raise AssertionError("dry-run must not spawn a subprocess")

    monkeypatch.setattr(subprocess, "run", boom)
    assert Runner().launch(SPEC, dry_run=True) is None
    out = capsys.readouterr().out
    assert "run-test" in out and "--epochs" in out


def test_launch_returns_parsed_job_id(monkeypatch) -> None:
    fake = SimpleNamespace(
        returncode=0,
        stdout="id=abc123 name=run-test url=https://example\nHint: logs\n",
        stderr="",
    )
    seen = {}

    def fake_run(argv, **k):  # noqa: ARG001
        seen["argv"] = argv
        return fake

    monkeypatch.setattr(subprocess, "run", fake_run)
    assert Runner().launch(SPEC) == "abc123"
    assert "jobs" in seen["argv"]


def test_launch_failure_raises(monkeypatch) -> None:
    fake = SimpleNamespace(returncode=1, stdout="", stderr="boom")
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: fake)
    with pytest.raises(RuntimeError, match="boom"):
        Runner().launch(SPEC)


PS_SAMPLE = """\
job_id\tname\timage/space\tcommand\tcreated\tstatus\truntime
6a1\trun-a\tpython:3.12\tbash -c train\t2026-10-17 05:06\tRUNNING\t9m
6a2\trun-b\tpython:3.12\tbash -c train\t2026-10-16 22:28\tCANCELED\t--
6a3\tfr-publish\tpython:3.12\tpython3 -c x\t2026-10-17 04:14\tRUNNING\t13s
6a4\trun-c\tpython:3.12\tbash -c eval\t2026-10-15 18:04\tERROR\t22h
"""


def test_running_budget_counts_run_jobs_only(monkeypatch) -> None:
    fake = SimpleNamespace(returncode=0, stdout=PS_SAMPLE, stderr="")
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: fake)
    running = Runner().running_run_jobs()
    assert running == ["run-a"]  # canceled/errored don't count; non-run-* don't


def test_budget_guard_blocks_third_run(monkeypatch) -> None:
    sample = PS_SAMPLE.replace("6a2\trun-b", "6a2\trun-b2").replace(
        "CANCELED", "RUNNING"
    )
    fake = SimpleNamespace(returncode=0, stdout=sample, stderr="")
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: fake)
    with pytest.raises(RuntimeError, match=str(MAX_CONCURRENT_RUNS)):
        Runner().launch(SPEC)


def test_budget_guard_force_overrides(monkeypatch) -> None:
    def fake_run(argv, **k):  # noqa: ARG001
        stdout = PS_SAMPLE if "ps" in argv else "id=abc123 name=run-test\n"
        return SimpleNamespace(returncode=0, stdout=stdout, stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    assert Runner().launch(SPEC, force=True) == "abc123"
