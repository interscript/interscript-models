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

### Launch record (2026-11-19)

- Lane code: urdu-dev PR #18 (`training/teacher_distill/`, branch
  `wo92-teacher-distill`).
- Job 1 full: `run-093-urd-teacher-relabel` — HF Jobs
  `rhtse/6afeb4b4545f95df1c0716a7`, a100-large, detached, 24h timeout,
  `--attempts 2`, resume-proof (shard jsonl + `.done` markers carry
  per-shard dedupe/overlong/drop/rows counts; restarts rebuild
  truthful totals). Config: bs 32, MAXLEN 256 src cap (overlong
  skipped + counted), MAX_NEW 512, GUARD_N 8, SHARD_ROWS 10000,
  58 shards, teacher sha8 6ac0f27c, guard index 554,196 CLE 8-gram
  shingles (9 files), source 573,130 rows.
- Earlier attempts, cancelled (negatives recorded verbatim):
  - `rhtse/6afe8ed7e41aae15936d23e1` (smoke, run-093a): cancelled
    queued — superseded by the full job exercising the same chain.
  - `rhtse/6afe9451545f95df1c0702bb`: ran 2h with ZERO script output
    (no crash, no retry, no run dir). Diagnosis: safetensors mmap
    loading over the bucket FUSE mount page-faults the model through
    ranged network reads (~2 s per MB measured). The loader now copies
    the checkpoint to /dev/shm first (2.33 GB in **10 s** sequential)
    and logs every stage. Lesson for every bucket-mounted from_pretrained:
    copy-then-load, never mmap a network mount.
  - `rhtse/6afeb018e41aae15936d3265`: with logging on, crashed in
    ~15 min at the source-rows line (`counts` referenced before init) —
    a bug py_compile cannot catch. Root-caused + fixed + validated by a
    stubbed local dry-run (fresh chain AND resume over committed shards
    assert dup/overlong/guard counts and original-index provenance).
- ETA: at the measured 26.7 rows/s eval decode rate, 573K rows ≈ 6 h;
  run-092's retention eval is the rate basis (11,940 rows / 447 s).
- Next gate after run-093: manifest review (hygiene counts disclosed),
  then run-094 student smoke + full, then the calibrated 16(e) suite
  on the student (reference google/byt5-small, self-control 0.5
  required) + CER ≤ 0.0377 bar.

### run-093 manifest review (2026-11-20) — CLEAN; student lane unblocked

- Completing job: `rhtse/6afebe6ee41aae15936d3e12` COMPLETED, 8 h 41 m
  (created 2026-11-19 09:16:30 UTC under the final PR #18 config,
  MAX_NEW 256 / bs 64; `seconds_total` 31,250 agrees). The launch
  record above lists `rhtse/6afeb4b4545f95df1c0716a7` — that job was
  CANCELED before start when the config changed; it produced no
  artifacts and is superseded by the completing job.
- Artifact set at `isx-training:/run-093-urd-teacher-relabel/`:
  58 shard jsonl + 58 `.done` markers + `manifest.json` +
  `verdict.json` + `GATE_DONE` — exactly the expected 119 entries, no
  orphans. Every `.done` timestamp sits inside the completing job's
  window (09:34:21–18:03:16), so nothing stale survived from the
  cancelled old-cap attempt (whose single shard was removed per the
  PR #18 note).
- Counts (manifest == verdict, verdict PASS):
  - rows_source 573,130 → rows_out **483,289** (84.3% yield);
    exact-dup removed 89,840; skipped_overlong 1;
    **regurgitation guard (8-word CLE shingle) drops 0** — the
    pre-registered MUST-be-zero gate HOLDS.
  - Arithmetic closes exactly: per-shard sums equal the totals; shard
    balance `rows_in = dup + overlong + guard + rows_out` holds on all
    58 shards; shard ids contiguous 0..57 (57 × 10,000 + 3,130 tail).
- Independent spot check: streamed line counts of shard-000000.jsonl
  (9,951) and shard-000057.jsonl (2,339) match their `.done` markers
  exactly. Aggregate counts only were read — no corpus text persisted
  or printed (Clause 19).
- Manifest decode record: bs 64, maxlen 256, max_new 256, greedy,
  bfloat16 — matches the final relabel.env; teacher sha8 6ac0f27c
  matches the launch record.
- Verdict: **corpus CLEAN → run-094 unblocked** (student smoke, then
  full). One prerequisite gap surfaced: `student-smoke.env` points at
  `/ckpt/run-093a-urd-teacher-relabel-smoke`, which never existed —
  the relabel smoke was cancelled queued yesterday (recorded above as
  superseded). The script-defined relabel smoke (2 × 200 rows,
  `relabel-smoke.env` verbatim, no edits) was relaunched to produce
  that corpus for the student smoke: `rhtse/6afff0d44fdc5ab3c55af879`.

### run-094 launch (2026-11-20)

- Relabel smoke re-run COMPLETED in 3 m (created 07:03:48 UTC):
  verdict PASS, 400/400 rows out (2 × 200), dups 0, overlong 0,
  guard drops 0, `GATE_DONE` ok — `run-093a-urd-teacher-relabel-smoke`
  now exists as the corpus `student-smoke.env` expects.
- Student smoke launched (`student-smoke.env` verbatim):
  `rhtse/6b00f8c6efaf5e14f4b4419c`, a100-large, detached, 24 h
  timeout, `--attempts 2` — ByT5-small init, 1 epoch over the 400-pair
  smoke corpus, 200-row eval slice, lineage recipe constants. Chain
  validated before the full student launches (issue #5 doctrine).

### Student smoke verdict + run-094 full launch (2026-11-21)

- Student smoke `rhtse/6b00f8c6efaf5e14f4b4419c` COMPLETED in 1 m 33 s.
  Its verdict VERBATIM (the negative-looking verdict ships with its
  explanation — ledger law):

  ```json
  {
      "run": "run-094a-urd-diac-distill-smoke",
      "init": "google/byt5-small",
      "corpus_run": "run-093a-urd-teacher-relabel-smoke",
      "steps": 13, "epochs": 1, "pairs": 400, "eval_rows": 200,
      "cer": 9.19363,
      "quality_gate_cer": 0.0377,
      "quality_pass": false,
      "verdict": "MISS"
  }
  ```

- Structural analysis: the MISS is predetermined, not a chain failure —
  the script applied the full-run quality bar (CER ≤ 0.0377) to a
  13-step run from raw `google/byt5-small` (never task-trained). An
  untrained model generates long junk against short gold strings, so
  CER ≫ 1 by construction regardless of chain health; no 13-step smoke
  could ever pass that bar. The smoke's registered purpose is chain
  validation.
- Chain evidence (all green): corpus load (400 pairs; corpus_run +
  hygiene read from the run-093a manifest), train loop 13/13 steps at
  3.24 it/s (final loss 3.5523, finite, no NaN skips), checkpoint
  `step-13/` (model/ + optim.pt 2.4 GB + meta.json with all lineage
  fields incl. `privacy_gate_reference: google/byt5-small`), eval
  hookup (200 rows decoded, per-row CER), `verdict.json` +
  `GATE_DONE ok`.
- **Owner ruling (2026-11-21): CHAIN PASS confirmed** — the MISS is
  expected-at-smoke-scale; launch authorized. Semantics gap assigned to
  an upstream urdu-dev PR: add a chain-verdict field (chain PASS =
  checkpoint + eval + verdict artifacts written) so future smokes gate
  on chain and quality stays full-run-only. The full run's gates are
  UNCHANGED.
- **run-094 full launched**: `rhtse/6b011020efaf5e14f4b45001`,
  a100-large, detached, 24 h timeout, `--attempts 2`, `student.env`
  verbatim — ByT5-small init, 483,289 distill pairs (run-093 corpus,
  manifest-reviewed CLEAN), 3 epochs, bs 16 × accum 2, lr 3e-4 cosine
  (200 warmup), bf16 autocast, MAXLEN 256, CKPT_EVERY 1000,
  cross-job resumable, final full-split eval (11,940 rows, WO37
  protocol) against the 0.0377 champion bar. 45,309 optimizer steps;
  ETA ≈ 4.5–5.5 GPU-h + end eval (smoke measured 3.24 it/s → ~4.2 h
  stepping; run-066 measured scale agrees).
- Gates ahead (unchanged, pre-registered): full-run quality CER ≤
  0.0377 → calibrated Clause 16(e) suite (reference google/byt5-small,
  reference self-control exactly 0.5) → standard ship gates →
  owner-stated version.

### run-094 verdict (2026-11-21) — QUALITY MISS; 16(e) spend withheld

- Job `rhtse/6b011020efaf5e14f4b45001` COMPLETED in ~3 h 34 m
  (45,309/45,309 steps at 3.91 it/s; all step checkpoints 1000→45309
  committed; `GATE_DONE ok`). Verdict VERBATIM (ledger law):

  ```json
  {
      "run": "run-094-urd-diac-distill",
      "init": "google/byt5-small",
      "corpus_run": "run-093-urd-teacher-relabel",
      "steps": 45309, "epochs": 3, "pairs": 483289, "eval_rows": 11940,
      "cer": 3.2066,
      "quality_gate_cer": 0.0377,
      "quality_pass": false,
      "verdict": "MISS"
  }
  ```

- **CER 3.2066 vs bar 0.0377 → pre-registered kill criterion fires**:
  quality MISS, record the negative, no publish consideration,
  **calibrated 16(e) suite NOT launched** (no spend on a candidate that
  already failed the quality gate). Owner decides the next arm.
- Training was healthy to the final step: loss 0.006–0.019 across the
  last 500 logged steps (45,000–45,309), zero NaN skips, constant
  rate. The miss is NOT late-training divergence.
- Eval evidence (`eval_progress.jsonl`, all 11,940 rows scored; mean
  3.2066 == verdict — eval arithmetic internally consistent):
  - median CER = **1.0 exactly** (the empty-prediction signature:
    edit distance == gold length), p10 0.9091, p75 5.5, p90 8.875,
    p99 16.0;
  - distribution: CER ≤ 0.0377 — **0 rows**; 0.0377–0.1 — 0;
    0.1–0.5 — 0; 0.5–1 — 8,120; 1–2 — 94; 2–5 — 544; >5 — 3,182
    (of which >10 — 822);
  - ZERO rows anywhere near the bar: free-running decode is bimodal
    empty-or-runaway, the classic byte-level seq2seq mode-collapse /
    exposure-bias failure (teacher-forced loss ≈ 0.01 alongside
    degenerate self-decode — the known "flat byte student" failure
    mode, cf. the Thai seq2seq precedent).
- Ruled OUT: eval arithmetic bug (per-row data matches the verdict;
  the same generate/batch_decode path produced sane teacher outputs
  in run-093 and sane run-092 evals); late-training collapse (loss
  curve above). The WO51 batched-padded-decode export finding is
  about exported unmasked encoders, not in-job HF generate with
  attention_mask — but any post-mortem should re-confirm the eval
  path against it anyway.
- Live differentiators vs the lineage run-066 (same tier, same
  recipe, NO collapse): targets are teacher GREEDY OUTPUTS rather
  than the human-verified corpus (distillation-target degeneracy is
  the prime suspect), 483k vs 573k rows. NO arm is launched —
  candidate directions already pre-registered in the kill criteria
  above (guard tightening, loss-magnitude filtering, logit-level
  distillation) plus the mode-collapse angle are owner's call.

### Decode probe (2026-11-21) — TARGET DEGENERACY confirmed

- Owner-authorized diagnostic (arm decision: "diagnostic first, no
  re-train yet"). One short job, `rhtse/6b014e61efaf5e14f4b487e3`,
  a10g-large, detached, 2 h timeout, COMPLETED in 3 m 24 s —
  `PROBE_DONE ok`, artifact `decode-probe.json` in the run dir.
  Script: urdu-dev PR #20
  (`training/teacher_distill/probe_decode_cer_hf.py`) — the EXACT
  decode path + raw-char CER metric of the training eval, fixed
  200-row head slice of `data-diacrit/test.jsonl`, aggregate-only
  output (Clause 19).
- Trajectory (per-checkpoint free-running greedy decode):

  | step | mean | median | p10 | p90 | hist (≤.0377/.1/.5/1/2/5/>5) |
  |---|---|---|---|---|---|
  | 1000 | 3.88534 | 1.0 | 1.0 | 11.2308 | 0/0/0/137/0/6/57 |
  | 5000 | 3.13578 | 1.0 | 0.9333 | 9.3333 | 0/0/0/144/2/7/47 |
  | 15000 | 3.22094 | 1.0 | 0.9167 | 9.2667 | 0/0/0/136/3/17/44 |
  | 30000 | 2.71357 | 1.0 | 0.9091 | 7.9375 | 0/0/0/142/5/16/37 |
  | 45000 | 2.97611 | 1.0 | 0.9 | 9.0667 | 0/0/0/142/2/8/48 |

- **Read: flat-bad from the first checkpoint → TARGET DEGENERACY
  confirmed** (owner's pre-stated discrimination rule). Not a single
  row at ANY checkpoint lands below CER 0.5 — no good phase ever
  exists to collapse from, which rules out the training-dynamics
  story (a dynamics failure would pass through a decodable regime
  before degrading). The slow mean drift (3.89 → 2.71 → 2.98) with
  teacher-forced loss falling to ~0.01 is the model memorizing
  degenerate targets it cannot free-run: the constant bimodal shape
  (median exactly 1.0 = empty predictions, plus a >5 runaway bucket
  of 37–57 rows per checkpoint at every stage) means termination /
  length control is never learned from these targets.
- Implication (owner's pre-stated mapping, NOT yet launched): next
  arm = regenerate teacher targets — beam-4 decode or logit-level
  distillation, both pre-registered candidates. Diagnostic data
  worth carrying into that arm: a tgt-length/termination histogram
  over the run-093 corpus (the manifest does not record it) to
  separate empty-truncated target pathology from runaway-target
  pathology before regenerating.

### STEP 1 histogram (2026-11-21) — ROOT CAUSE FOUND: relabel input bug; corpus INVALID

- Job `rhtse/6b016cc4efaf5e14f4b4d2d8` (cpu-performance, 1 h cap)
  COMPLETED in seconds of compute over all 58 complete shards /
  483,289 rows; artifact `target-stats.json` + `STATS_DONE ok` in the
  run dir. Script: urdu-dev PR #21
  (`training/teacher_distill/target_stats_hf.py`), aggregate counts
  only (Clause 19).
- Histogram (tgt char lengths): empty 0; 1–5 — **337,005 (69.7%)**;
  6–20 — 36,761; 21–50 — 5,570; >50 — 103,953 (21.5%).
  Degeneracy counters: tgt == src 0; token repetition 0;
  single-char repeat 68; **tgt ≤ 25% of src length — 351,300
  (72.7%)**; tgt ≥ 3× src — 58,838 (12.2%). Cross-tab: for src
  21–50 chars (n=382,073), 276,559 targets are 1–5 chars and 63,308
  are >50 (longer than their source). For a vocalization task the
  target must track the source length — this distribution is
  impossible for real teacher vocalizations.
- **Root cause (structural check, 9,951/9,951 rows of shard-000000):
  every run-093 `src` field IS the raw JSONL line** — starts with
  `{"src"` and parses as a JSON object with both keys. `relabel_teacher_hf.py`
  stored the raw line (`s = line.strip()`) instead of
  `json.loads(line)["src"]` and fed serialized JSON pairs to the
  teacher as if they were bare text. The teacher never saw the bare
  source; it emitted fragments (1–5 chars, 69.7%) and occasional
  rambling (>50 chars, 21.5%) from JSON noise. The teacher itself is
  NOT degenerate — its 0.03567 retention on real inputs (run-092)
  stands; every count-balanced "PASS" in the chain was blind to this
  because the bug sits upstream of every counter.
- Consequences: the run-093 corpus is INVALID; run-094 (and its MISS
  verdict, and the decode probe's checkpoint trajectory) trained on
  JSON-line → fragment mapping. The probe's *mechanical* conclusion
  stands (targets degenerate, training dynamics exonerated) — the
  degeneracy's cause is now identified as our input bug, not teacher
  capability. Beam-4 over the same broken inputs would reproduce the
  garbage at ~26 GPU-h — **the authorized sweep as specified is
  invalid and was NOT launched** (a100 left free).
- Lesson recorded: a count-balanced chain smoke (400/400 rows, all
  counters green) is not semantic validation. Any corpus-producing
  smoke must assert a src-field invariant (e.g., parsed src is
  non-JSON text; tgt length correlates with src length) before a
  corpus is declared CLEAN. This goes into the relabel script's
  checks when it is fixed.
- Corrected STEP 2 (proposed, NOT launched — owner go required):
  fix the parse (`json.loads(line)["src"]`), add the src-field
  invariant to the script, regenerate greedy first (greedy teacher
  behavior on real inputs is proven champion-tier; beam-4 becomes an
  optional later arm, not the fix), same guard (MUST drop 0), shard
  + `.done` + manifest discipline, then the corpus review gate and
  the student retrain.

### Corrected chain (2026-11-21) — OWNER GO; execution records

- Owner ruling: the corrected chain is approved exactly as proposed,
  with the smoke upgraded to SEMANTIC validation. **Incident lesson
  is now LAW: count-balanced smokes are not semantic validation —
  every corpus gate asserts a src/tgt-relationship invariant from
  today.**
- Fix landed: urdu-dev PR #22 (`wo92-relabel-v2`) —
  `relabel_teacher_hf.py` parses `json.loads(line)["src"]`, aborts
  at load time on a JSON-looking src, and enforces the semantic
  invariant per shard BEFORE the `.done` commit: median
  len(tgt)/len(src) inside [0.5, 3.0] and degenerate share
  (ratio < 0.35 — the 1–5-char-on-long-src class) under 1%; a
  violation raises with the shard uncommitted. Manifest/verdict gain
  `semantic_invariant` (totals + pass flag); verdict PASS requires
  it; `.done` markers carry per-shard ratio_median +
  degenerate_share. Validated: py_compile + stubbed dry-run
  (healthy ratios pass; the exact run-093 fragment distribution and
  a 2%-degenerate shard abort).
- Corrected run plan (naming: the run-095 unit = corpus regen +
  student; lettered subruns are its stages):
  1. `run-095a-urd-teacher-relabel-smoke` — 2 × 200 rows, semantic
     smoke (job launched at record time; must show invariant PASS +
     guard drops 0 + ratio median in band).
  2. `run-095b-urd-teacher-relabel` — full 573,130-row greedy
     regeneration, HELD until the smoke PASSes. ETA 7.5–9 h on
     run-093's measured 18.3 rows/s basis (bs 64, MAX_NEW 256);
     24 h timeout, `--attempts 2`, shard `.done` resume, CLE guard
     MUST drop 0.
  3. **Corpus review gate** before any training: manifest review +
     `target_stats_hf.py` over run-095b asserting the invariant
     across all 58 shards (ratio median in band, degenerate share
     < 1%, guard 0, artifact set complete).
  4. `run-095-urd-diac-distill` — student on the corrected corpus,
     recipe identical to run-094 otherwise (ByT5-small init, 3
     epochs, bs 16 × accum 2, lr 3e-4 cosine 200 warmup, bf16,
     MAXLEN 256, CKPT_EVERY 1000, final full-split eval vs 0.0377).
  5. Eval → calibrated Clause 16(e) (reference google/byt5-small,
     self-control exactly 0.5, AUC ±0.05, success-rate 0.6) →
     ship recommendation → owner version.

### run-095b corpus review gate PASS + run-095 student launch (2026-11-23)

- run-095b COMPLETED in 1 h 57 m (`seconds_total` 7,036 — ~62 rows/s,
  far faster than the 18.3 rows/s basis; the JSON-line srcs of
  run-093 were the slow case, not the corpus). VERDICT PASS:
  573,130 → **439,786** rows out (dups 133,344, overlong 0,
  **regurgitation 0**), 58/58 shards, semantic invariant PASS
  (ratio_median 1.6667, degenerate_share 0.0).
- **Manifest review**: artifact set exactly 119 entries (58 jsonl +
  58 `.done` + manifest + verdict + GATE_DONE); every `.done` carries
  `ratio_median` + `degenerate_share`; per-shard ratio_median spans
  1.6667–1.7 — all in [0.5, 3.0]; per-shard degenerate_share max
  0.0003 — all < 1%; global and per-shard balance close exactly;
  last shard 3,130 rows; teacher sha8 6ac0f27c matches. Independent
  streamed line-count spot checks: shard-000000 = 9,918 lines ==
  marker; shard-000057 = 2,016 == marker.
- **Independent stats gate** (`target_stats_hf.py` over run-095b,
  439,786 rows, owner-verified from job logs): tgt buckets empty 1 /
  1–5: 5,455 (1.2%) / 6–20: 379,774 (86.3%) / 21–50: 54,491 /
  >50: 66; degeneracy: tgt_empty 1, single-char 0, token-repetition
  242 (0.06%), tgt==src 6, ≤25%-of-src 1, ≥3×-src 6 — degenerate
  share ~0.05%, targets track sources. **GATE PASS** (owner ruling).
- Process note recorded: the first stats attempt
  (`rhtse/6b0220214fdc5ab3c55e8469`) silently ran with the DEFAULT
  run dir because `--env <(process substitution)` did not deliver the
  env — it re-computed run-093's stats and overwrote that dir's
  `target-stats.json` with bit-identical content (no information
  lost). Relaunched properly with an env file
  (`rhtse/6b026a64efaf5e14f4b79505`). Lesson: stick to the
  campaign's env-file launch pattern; process-substitution envs fail
  silently.
- **run-095 student launched**: `rhtse/6b036c958d268c0fbd22dbc2`,
  a100-large, detached, 24 h timeout, `--attempts 2`,
  `student-run095.env` — ByT5-small init, 439,786 corrected pairs,
  3 epochs, bs 16 × accum 2, lr 3e-4 cosine (200 warmup), bf16,
  MAXLEN 256, CKPT_EVERY 1000, final full-split eval (11,940 rows,
  WO37) vs the 0.0377 bar. 41,232 optimizer steps; ETA ≈ 2.9 h
  stepping at run-094's measured 3.91 it/s + ~15–25 min eval ≈
  **3.2–3.5 h** total.
- Gates ahead (unchanged): full-split CER ≤ 0.0377 → calibrated
  Clause 16(e) suite (reference google/byt5-small, reference
  self-control exactly 0.5, AUC ±0.05, success-rate 0.6) → standard
  ship gates → owner-stated version.

### run-095 QUALITY PASS — beats the shipped champion (2026-11-23)

- Job `rhtse/6b036c958d268c0fbd22dbc2` COMPLETED (~3 h; 4.26–4.36
  it/s live, above the 3.91 precedent — the corrected corpus's
  shorter, cleaner pairs step faster). Verdict VERBATIM:

  ```json
  {
      "run": "run-095-urd-diac-distill",
      "init": "google/byt5-small",
      "corpus_run": "run-095b-urd-teacher-relabel",
      "steps": 41232, "epochs": 3, "pairs": 439785, "eval_rows": 11940,
      "cer": 0.03692,
      "quality_gate_cer": 0.0377,
      "quality_pass": true,
      "chain_pass": true,
      "verdict": "PASS"
  }
  ```

- **Exact number vs the three bars: CER 0.03692 (3.692%)** — gate
  0.0377 PASS; champion **urd-vocalized-1.0 recorded 3.74% → the
  student lands BELOW it: the SOTA-claim condition holds on
  quality** (owner's rule: SOTA requires landing below 3.74).
  chain_pass true (41,232/41,232 steps, final checkpoint usable,
  all 11,940 eval rows scored) — the new chain-verdict field
  working as designed. pairs 439,785 = corpus rows 439,786 − 1
  (the loader drops the single empty-target row the stats counted).
- The corrected chain — parse fix + semantic invariant — took the
  corpus from unusable (run-094: CER 3.2066, decode collapse) to
  champion-beating (run-095: 0.03692) with the SAME recipe. The
  lever was data validity, not training dynamics.
- **Ship naming law (owner, models.yaml WO87 renames)**: canonical
  ship name **`urd-vocalized-2.0`** (NOT urd-diac-2.0); renames
  entry `urd-diac-2.0: urd-vocalized-2.0` mirrors the
  urd-diac-1.0 → urd-vocalized-1.0 precedent. All ship artifacts
  (GH release tag, HF repo id, index entry, certificate, notes)
  use the canonical; the alias preserves legacy lookups. The
  `models:` ship entry is created at ship time with real artifact
  data (sha256/urls are never pre-staged).
- **Calibrated Clause 16(e) launched**:
  `rhtse/6b03c5d4130a00b5aa821ecd` (l4x1, detached, 8 h timeout,
  `--attempts 2`, records bucket rhtse/urdu-16e-gate). Gate branch
  `urdu-16e-run-095` @ d7ac1f8 (pushed + verified):
  `run-095-vocalized-calibrated.json` — candidate
  `run-095-urd-diac-distill/step-41232/model`, reference
  **google/byt5-small** resolved from the hub per the WO92
  pre-registration (gate_job.py parameterized:
  GATE_MODEL_SUBPATH / GATE_REFERENCE_HUB; reference mount check
  skipped for hub ids, from_pretrained fails loudly on a bad id).
  Pre-registered gates: reference self-control EXACTLY 0.5, AUC
  tolerance ±0.05, success-rate 0.6, verbatim floor 25 words
  (Clause 18(d)), WordNet vocab scan. Monitor: single until-loop,
  10-min polls.
- Next: on gate terminal — report AUC + self-control + suite
  verdict verbatim. PASS → ship stage (index-v17 → pins → releases
  → certificate → notes → HF; canonical urd-vocalized-2.0).
  FAIL → stop, retain records (2-year clock), owner decides.

### Calibrated 16(e) verdict (2026-11-23) — FAIL: distillation did not remove the memorization signal

- Job `rhtse/6b03c5d4130a00b5aa821ecd` COMPLETED (~5 h).
  **Suite verdict: FAIL** — `failures: ["mia: FAIL"]`. Candidate
  `run-095-urd-diac-distill/step-41232/model` (sha8 2a29658c),
  reference `google/byt5-small` (sha8 336b39c7, resolved from the
  hub per pre-registration), corpus digest dbaae25c… identical to
  the run-092 gate. Retention clock: records retained to
  **2028-11-23** (2 years).
- Gated metrics, verbatim:
  - **calibrated_auc: 0.6393** (chance 0.5, deviation 0.1393 ≫
    tolerance ±0.05) → FAIL
  - **calibrated_success_rate: 0.6293** (tolerance 0.6) → FAIL
  - naive preserved for disclosure: naive_auc 0.6137,
    naive_success_rate 0.6045
  - **ref_selfcontrol_auc: 0.5 exactly; ref_selfcontrol_success_rate:
    0.5 exactly** — the probe is SOUND; this is real memorization
    signal, not a broken harness (the run-092 lesson inverted: the
    calibrated method of record sees genuine signal).
- All other sub-tests PASS: extraction 0 violations (125 prompts, 5
  templates), verbatim 0 violations (200 probes, 25-word floor),
  WordNet 0 vocab hits (5,131 synsets, 384-byte vocab,
  67,364 content n-grams indexed). mia-scores.jsonl 440 rows
  (300 held-in / 140 held-out).
- **Reading**: the student beats the champion on quality (0.03692
  vs 3.74%) while carrying the teacher's memorization signal almost
  unchanged — run-092 calibrated AUC 0.6319 → run-095 0.6393. The
  distillation channel transferred the teacher's function INCLUDING
  its CLE memorization: the teacher absorbed CLE content during
  DAPT and re-emits enough of it in its outputs for the student to
  inherit the loss-level signal, without ever tripping the exact
  8-word-shingle guard (guard drops were 0 across the corpus).
  Quality and privacy move on different axes: data validity fixed
  quality; it could not fix privacy, because the privacy defect
  lives in the teacher's weight content, not in the training
  pipeline.
- **Kill criterion invoked (pre-registered): the distillation lever
  FAILED.** Stop; records retained (2028-11-23 clock); no ship —
  index-v17 / release / certificate / notes for urd-vocalized-2.0
  are WITHHELD. Full probe artifacts:
  `hf://buckets/rhtse/urdu-16e-gate/urdu-16e-run-095-vocalized-calibrated/`
  (verdict.json, progress.log, job-meta.json, records/
  mia-scores.jsonl + per-probe artifacts, all sha256-listed).
- Owner decides the next arm. Pre-registered candidates, in order:
  (1) tighten the regurgitation guard (5-word shingles) — note the
  evidence suggests loss-level signal survives exact-n-gram guards,
  so its expected yield is limited; (2) loss-magnitude filtering of
  teacher outputs; (3) logit-level distillation (soft targets carry
  different information than argmax text). Honest caveat from this
  round: every arm that keeps the run-092 teacher as the label
  source inherits its memorization through the targets; arms that
  change WHAT the teacher emits (logits, filtering) or WHAT the
  student trains on (a teacher never exposed to CLE) attack the
  root.
