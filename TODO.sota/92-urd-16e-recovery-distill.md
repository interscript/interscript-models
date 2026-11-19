# WO92 — urd 16(e) recovery: internal teacher + distillation (CLE licensing gate)

Status: IN_PROGRESS — owner-approved internal-teacher + distillation path;
teacher relabel job launched (run-093-urd-teacher-relabel)
Goal: a publishable Urdu vocalized candidate that passes the calibrated
Clause 16(e) gate while staying within the quality bar of the shipped
champion (urd-diac-1.0, full-split raw CER 0.0377, WO37 protocol).
NOT retrain-from-scratch, NOT no-release (owner decision, 2026-11-19).

## Background: why run-092 failed

run-092-urd-dapt-cle/step-4000 (ByT5-base, urd-diac-base-1.0 init,
CLE span-corruption DAPT + 0.3 replay) trained clean — domain CE
19.86 → 1.62, retention CER 0.03567 vs init 0.03566 on the full
11,940-row lineage test split (no forgetting) — but FAILED the
publish gate. The naive MIA that first gated it reported AUC 0.4432
(inverted); the reference-calibrated MIA (method of record since
urdu-dev#17) shows real memorization: AUC 0.6319 (tolerance ±0.05),
success-rate 0.616 (tolerance 0.6), reference self-control correctly
0.5 — the harness is sound, the candidate genuinely carries CLE
passages. Schedule C prohibits releasing any model from which the
resources can be extracted, so the DAPT plane can never itself be the
release artifact. The domain knowledge is usable only behind an
internal teacher.

## Design (three artifacts, one exposure boundary)

1. **Teacher — INTERNAL, never published.** run-092-step-4000
   (ByT5-base) is exactly the model the clause blocks from release:
   full vocalization ability (retention CER 0.0357, champion-tier) +
   CLE domain adaptation (domain CE 1.62). It stays in the
   access-controlled training bucket (`Interscript/isx-training`,
   private) and exists only to generate supervision. No LLM is
   involved — labels come from our own trained weights (registry law).

2. **Distillation corpus — teacher OUTPUTS, never the licensed text.**
   The student trains on (bare src → teacher vocalization) pairs where
   the bare src is the **public-lineage** `data-diacrit` train source
   side (573,130 rows, bucket `rhtse/jobs-artifacts/rababa-urdu-cc174b96`,
   owner-approved license review 2026-10-18). The student never sees
   CLE text in any form — not as input, not as target. This is the
   memorization-reduction lever.
   Data hygiene in the same prep pass:
   - exact-duplicate removal on src (global across shards, first
     occurrence kept; per-shard removal counts in the manifest;
     provenance-preserving — surviving lines are byte-identical and
     carry their original row index; non-duplicate lines never altered);
   - regurgitation guard — drop any pair whose teacher output shares a
     normalized 8-word shingle with the CLE train plane (mounted
     read-only in-job; count disclosed in the manifest, no text
     emitted — Clause 19 aggregate-only logging).

3. **Student — the publish candidate.** ByT5-small (the
   `urd-diac-1.0` / `urd-vocalized-1.0` tier), init
   `google/byt5-small`, the lineage recipe verbatim (WO38 → run-066):
   3 epochs, bs 16 × accum 2, lr 3e-4 cosine (200 warmup), bf16
   autocast, MAXLEN 256, step checkpoints every 1000, cross-job
   resumable — trained only on the distillation corpus.

## Gates (all pre-registered here)

- **Privacy gate:** calibrated Clause 16(e) suite on the student
  (reference-calibrated LiRA-style MIA per urdu-dev#17; reference =
  `google/byt5-small` — same tokenizer, same eval config, never
  trained on the CLE plane; reference self-control MUST sit at 0.5 or
  the probe fails as broken; AUC tolerance ±0.05, success-rate
  tolerance 0.6; verbatim floor 25 words — Clause 18(d), extraction,
  WordNet vocab scan). Run through the urdu-dev hfjob gate runner
  (GATE_CONFIG selector envs). Naive statistics preserved as
  `naive_*` for disclosure; the gated keys are the calibrated ones.
- **Quality gate:** full-split raw CER ≤ **0.0377** on the
  `data-diacrit` test split (urd-diac-1.0 champion bar, WO37
  protocol). The teacher's own 0.0357 is the ceiling context; the
  student is not required to beat the base tier, only to hold the
  shipped champion's bar.
- **Standard ship gates** (models-repo publish.py): parity ≥ 500
  samples in shipped decode mode, conformance fixtures, license
  strings, Schedule D attribution (CLE citation) in the model card,
  compliance certificate coverage, owner-stated version.

## Kill criteria

- Student CER > 0.0377 → quality MISS; record the negative, no
  publish consideration; owner decides next arm (teacher DAPT
  extension, top-k/logit distillation, capacity change).
- Calibrated MIA FAIL on the student → the distillation lever failed;
  stop, retain records (2-year retention clock), escalate to owner
  with the full probe artifacts. Candidate arms, in order: tighten the
  regurgitation guard (5-word shingles), add loss-magnitude filtering,
  logit-level distillation.
- Reference self-control ≠ 0.5 → harness broken; fix harness first,
  numbers invalid.

## Jobs (HF Jobs only — never Modal; `--detach`, `--timeout ≥ 4h`,
bucket I/O via HfFileSystem volumes, corpora never touch local disk,
≤ 2 concurrent big-GPU apps, monitor via `hf jobs ps --all`)

| job | purpose | mounts |
|---|---|---|
| `run-093-urd-teacher-relabel` | teacher greedy decode over the public-lineage src + dedupe + regurgitation guard → shard jsonl + manifest (now) | teacher ckpt `isx-training` ro; replay bucket ro; CLE plane ro (guard only); `isx-training` rw (output) |
| `run-094-urd-diac-distill` | student ByT5-small on the distillation corpus (after run-093) | distill corpus ro; replay bucket ro (test split eval); `isx-training` rw |
| 16(e) gate run | calibrated suite on the student via urdu-dev GATE_CONFIG machinery (after run-094) | student ckpt ro; CLE plane ro; WordNet ro; reference `google/byt5-small` |

ETA: run-093 ≈ 573K rows / bs 32 greedy on a100-large ≈ 6–10 GPU-h
(timeout 24h, --attempts 2, shard-resumable: each 10K-row shard
commits a `.done` marker, retries lose at most one shard).
run-094 ≈ run-059/run-066 measured scale ≈ 5.5 GPU-h.

## Compliance map

- Teacher: internal-only; never crosses the access-controlled channel;
  no release path exists for it in this WO.
- Distillation corpus: derived artifact (teacher outputs over
  public-lineage sources), unlisted under Schedule C → treated as
  PROHIBITED for release until CLE written clearance (Clause 16(d));
  it lives only in the private training bucket and is never a release
  channel. Only the STUDENT is a release candidate.
- Student: release requires the full pk-cle-urdu COMPLIANCE.md
  checklist (16(e) PASS records, Schedule D citation in card/NOTICE,
  compliance certificate, no Prohibited Use/Derivative) + owner-stated
  version. Retention clock: records kept 2 years post-expiry
  (2028-11 window).
- Aggregate-only logging everywhere; corpus text never in logs, PRs,
  or reports.

## Verdicts

(run-093 / run-094 / gate results recorded here as they land)
