# WO39 — AR oracle-distillation: capture the measured ensemble ceiling in one model

## Motivation

WO35 closed with run-047-large-strip e6 at WikiNews first-alt
**3.5607 WER / 1.4588 DER** (gap to QCRI frontier 2.70: **0.86**).
The 3-way oracle over {run-029 specialist, run-040 base-strip,
run-047 large-strip} measures a **2.9861/1.2828** ceiling —
complementarity is real (−0.57 WER available), but runtime routing
is closed (threshold <2, WO28) and the frontier sits BELOW the
ceiling. The standard way to capture an ensemble's complementarity
in a single shippable model: **oracle-distillation** — relabel
training rows with the per-row best arm (edit distance to silver),
then continue-train the best single arm on those targets.

Secondary effect: QCRI silver is BiLSTM-labeled (noisy). Where arms
disagree, the oracle pick filters label noise toward the
model-consensus∩silver intersection — the target is cleaner than
silver itself.

## Stages

1. **Relabel (a100-large, ~10-14 GPU-h)** — `distill_oracle_hf.py`:
   reproduce run-047's corpus exactly (MIX=qcri, R8_GOLD=none,
   PSEUDO_CAP=900K, seed 7 article shuffle, WINDOW=600,
   STRIP_ALT primary-reading targets), take the first 300K shuffled
   rows, greedy-decode each src with all three arms (bs 32 large /
   64 base, bf16, max_new_tokens=1200), write
   `arm-preds.jsonl` {src, silver, p029, p040, p047} + oracle pick
   (min char-edit-distance to stripped silver; ties → p047) →
   `oracle-targets.jsonl`. Report: disagreement rate, per-arm CER,
   **oracle-train CER** (the distill label ceiling).
2. **Continue-train (a100-large, ~10-14h)** —
   `continue_oracle_train_hf.py`: from run-047/best (the e6 leg),
   +2 epochs, lr 3e-5 cosine (200 warmup), bs 8×accum 2, bf16,
   WINDOW=600 protocol; in-job eval = run-047's exact surfaces
   (Sadeed default + WikiNews multiref RAW and first-alt corrected
   protocol, project_haraqat on stitched windows).
3. **Gate**: WikiNews first-alt WER < **3.5607** (must beat its own
   teacher). Stretch: ≤ 2.70 (frontier parity → SHIP).
   Abort: ≥ 3.56 → distillation on train-corpus picks does not
   transfer; record NEGATIVE and park (QCRI full-silver ask remains
   the owner lever).
4. **Ship chain (if gate passes)**: export int8 IMF (the
   use_external_data_format=False pin), ORT parity vs torch on 300
   WikiNews windows, staged zip — release name is the owner's call.

## Fleet notes

- Stage 1 waits for the a100 slot (e12 student continuation occupies
  one; mdeberta-en-resume the other — ≤2 big-GPU budget, WO-modal
  memory). Launch on e12 completion if e12 PASSES its gate; if e12
  misses AND the 500h slice is ready, teacher v4 (WO36 stage 3)
  goes first — HE has the wider absolute gap.
- run-047/best contains two 4.9GB `.tmp*` upload remnants — never
  delete (global law); they are inert.
- No LLM teachers anywhere (memory law): all labels here derive from
  our own trained arms + the QCRI silver corpus.

## Cost

≈ 20-28 GPU-h total (relable 10-14 + train 10-14). Under every
prior arm's budget; no new data, no new infra.

## Stage-1 COMPLETE (2026-10-18, resume9)

290,575 rows consolidated in minutes once the consolidation levenshtein
moved to the C wheel (the pure-python loop needed ~56h vs the 23h
timeout — resume6/8 died exactly there). Stats:

- arm CER vs silver: p047 0.72% · p040 0.74% · p029 0.82%
- disagreement 31.4% — the oracle's opportunity space
- **oracle CER 0.54%** (−25% vs best single arm); picks: p047 87%,
  p040 11%, p029 2%

**Stage-2 LAUNCHED THROUGH THE SPINE** (job 6ad494b9): the ara recipe's
sft stage planned it (O_* envs, both mounts) and the Runner's budget
guard cleared it — the first dogfooded launch; hand-typed job commands
retire here. Gate: first-alt WER < 3.5607; stretch ≤ 2.70.

## FINAL (2026-10-19): stage-2 REJECTED — ara canonical unchanged

oepoch-1 dual-surface eval (the training itself converged, loss 0.002;
eval initially crashed on missing pandas — rerun eval-only):

- SadeedDiac-25: Total DER **8.32** (gate: hold r7's 2.29) — identity
  COLLAPSE
- WikiNews-2024 multiref: RAW 9.95 WER / 9.06 DER; first-alt
  **3.97 WER** (gate < 3.5607) — MISS

The stage-1 oracle was real (0.54% relabel CER) but continue-training
on the relabeled 290K subset regressed both surfaces — domain-narrowed
distillation destroyed general calibration. Same family of negative as
fas stage-2. **ara canonical: ara-diac-2.0 (shipped, DER 2.29); the
oracle-distillation lever is now data-closed for BOTH ara and fas.**

Ops scars recorded: spine deps gap (fixed, #303), eval-only rerun
pattern (eval_oepoch1.py), eval extras belong in recipe deps.
