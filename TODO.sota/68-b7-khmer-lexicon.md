# WO68 — B7: Khmer — Chuon Nath lexicon conditioning (CER < 15)

Status: IN_PROGRESS — Chuon Nath reading arm TRAINED (2026-10-22,
run-080-khm-lex-2): ByT5-small on 2,935 gold pairs -> dev CER 15.02%
(326 held-out dictionary rows, 8 epochs, descending to the end).
Caveats: dictionary-internal dev (memorization scale), NOT novel-word
performance; SBBIC's 72,048 staged rows are word-only (ipa: null) —
**the open Khmer phoneme supply is exhausted at ~3.3k gold pairs**
(ipa_dic.txt 3,286 lines = the whole local source). The CER < 15
khm-latn target therefore runs through (a) the khm-latn lineage
recovery (Khmer->Latin pairs, different and larger supply) or (b)
owner-gated licensing (SEAlang / full Chuon Nath IPA). GPU finding:
ByT5-small + 2.9k pairs trains to sub-16% in ~7 min — the learner is
never the bottleneck here.
Phase 1 DONE: khm-dict corpus built + pinned (corpora/khm-dict.yaml) —
3,261 gold Chuon-Nath (word→IPA) pairs, 326-row holdout, 72,048 SBBIC
vocab rows; staged at bucket Interscript/isx-training/run-080-khm-lexicon
(size-verified). License LGPL-2.1 recorded; owner note on
LGPL-for-data semantics. NEXT: hit-rate vs the khm-latn eval set (in
the phase-2 job, which mounts it), lexicon-conditioned ByT5 fallback
training, three-way probe.
Goal: khm-latn 27.4 → CER < 15 with hit-rate reported.
Method: build the Chuon Nath-conditioned dataset (headword→reading
pairs, syllabification-aware); lexicon-conditioned ByT5 (retrieval or
prefix conditioning); fp16 zip hygiene (khm fp32 corruption lesson);
conformance fixtures for the new artifact.
Acceptance: gates green; hit-rate + CER on held-out; release via the
strict publish path.


## Lineage recovery (2026-10-25)

khm-latn-1.0 traces to the **secryst project**
(`~/src/interscript/secryst`; README documents
`scripts/export_onnx_byt5.py <hf_checkpoint_dir> khm-latn-byt5.zip`).
The training corpus is re-derivable from the secryst repo's data
pipeline + khmer-dict-spice — the recovery question is now concrete:
pin the exact secryst-era corpus files, run them through
corpora/khm-latn.yaml provenance, and the retrain is unblocked.


## Lineage sources pinned precisely (2026-10-29)

- **khm-latn lineage** (the 27.4 CER model): trains on
  `secryst/data-khmer-translit` — 17,911 word pairs in two parallel CSVs
  (data_kh.csv, data_rom.csv), fetched by the secryst-era
  train_khmer_byt5.py from **raw.githubusercontent (a data-law violation to
  retire)**. The repo carries **no license file** (default copyright) — but
  it is the predecessor project's own repository, so the fix is the owner
  adding a license to it (or blessing the migration of the CSVs into our
  GitHub Releases channel under a license the owner names). No third-party
  negotiation involved.
- **khmer-dict-spice** (local clone confirmed): the DICT/IPA line, NOT the
  latn pairs — ipa_dic.txt (3,286 gold pairs, the exhausted open supply),
  SBBICkm_KH.txt (72,048 words), kh_dictionary.{csv,sqlite},
  trained_chuon_small.txt (a frequency list). LGPL-2.1, already recorded.
- Consequence: **the CER < 15 recovery path needs NO third-party license.**
  The single owner decision is the secryst data repo's license. The
  SEAlang / full Chuon Nath licensing only gates expansion beyond the
  17,911 pairs + 3,286 gold pairs.
- Recovery plan once the license lands: re-release the two CSVs as a pinned
  GitHub Release artifact with sha256 + provenance YAML (retiring the
  raw.githubusercontent fetch), port the Modal training script to HF Jobs
  (--detach, >=4h, step ckpts), retrain ByT5, eval against khm-latn-1.0's
  27.4 CER on the same protocol, ship via the strict publish path if better.


## Lineage recovery VERIFIED by reproduction (2026-10-29)

run-081-khm-latn-recovery (HF job rhtse/6ae32d5e3fb22a235dd5896f, seed 42,
legacy recipe; first attempt CANCELED externally at epoch 4, attempt 2 of 3
completed): held-out 5% test split, 895 rows —

- greedy: EM 58.21%, CER 28.13%
- beam4: EM 58.44%, **CER 27.49%**

Against khm-latn-1.0's 27.42 CER this is reproduction within noise: the
secryst/data-khmer-translit corpus is confirmed as the khm-latn training
lineage, and the provenance pin in corpora/khm-latn.yaml is now verified by
reproduction (the strongest evidence class). Best checkpoint:
bucket Interscript/isx-training/khmer-translit/run-081-recovery/best.

Consequence for the target: recovery is closed, but reproduction at ~27.5
also confirms the corpus ceiling — **CER < 15 requires data expansion**, so
the owner's licensing decision (SEAlang / full Chuon Nath IPA, or a blessed
corpus-release license opening other sources) is now THE B7 blocker.


## Data expansion attempt 1: Wiktionary/kaikki (2026-10-29, launched)

The owner reports SEAlang / full Chuon Nath IPA are not findable/obtainable.
Alternative license-clear expansion paths identified, attempt 1 launched:

- **kaikki/Wiktionary Khmer** (CC BY-SA 4.0, the tha-lexicon-kaikki-1.0
  precedent): the dump exists at
  kaikki.org/dictionary/Khmer/kaikki.org-dictionary-Khmer.jsonl. Job
  run-082-khm-wikt-expansion extracts word->IPA and word->romanization
  pairs for Khmer-script headwords.
- **Self-training expansion** (attempt 2, designed): khm-phonemic-1.0
  (24.5 CER) labels the 72,048 SBBIC words (license-clear, in
  khmer-dict-spice) -> confidence-filtered gold expansion. Caution: the
  noisy-student negative (WO64) was correlated-teacher Arabic — the Khmer
  regime (tiny gold, huge unlabeled) is the case self-training is for;
  confidence filtering + held-out VRR-style validation mandatory.
- FLEURS-Khmer alignment (heavier, parked).

The expansion path makes CER < 15 reachable WITHOUT SEAlang/Chuon Nath.


## Attempt 2 launched: self-training on the license-clear SBBIC list (2026-10-29)

khm-phonemic-1.0 (our shipped 24.5-CER model — not an LLM; the LLM-teacher
law is not implicated) labels the 75,039-word SBBIC list (LGPL-2.1, in
khmer-dict-spice, staged to the training bucket) with IPA readings plus mean
token log-prob confidence (run-082b-khm-sbbic-label, HF job
rhtse/6ae33c0441e90535df78b820). Stage B filters hard on confidence and
retrains; the Khmer regime (tiny gold, huge unlabeled) is the case weak
supervision exists for, with held-out validation mandatory against the WO64
correlated-teacher negative. This path makes CER < 15 reachable without
SEAlang / Chuon Nath.


### Expansion attempt 2 — stage A done, stage B negative (mis-design), B2 in flight (2026-10-30)

SBBIC 75,039-word list labeled with the shipped khm-phonemic-1.0 teacher
(house runtime, checkpointed rotating parts): **73,954 labels** persisted
(bucket khmer-expansion/sbbic-labeled.jsonl, 4.56 MB; 10,046 resume dupes
dropped; 1,038 unique words dropped by the labeler's empty-output guard —
words where the teacher emits nothing; 1.4%, acceptable).

**Stage B NEGATIVE — an artifact of target-convention mismatch** (my
script bug, recorded so it is never re-read as evidence): it trained on
the teacher's Latin romanizations (SBBIC weak labels) but evaluated
against the Chuon Nath IPA holdout. CER 0.735 / EM 0 vs the 0.245
reference measures the Latin-vs-IPA convention gap, not expansion value.
NO_BETTER_THAN_TEACHER from that run carries no information.

**Stage B2 (corrected, running as run-082d-khm-expansion2)**: matched
surface — SBBIC weak Latin labels + the translit corpus train anchor
(exact run-081 protocol: sorted pairs, seed-42 shuffle, 5/5/90), with
translit words dropped from the weak set (contamination control). The
teacher is scored on the IDENTICAL 895-row translit test split in-job
(house runtime on the shipped artifact), so the verdict is
student-vs-teacher on the same rows and surface. Gate: student CER <
teacher CER on that split -> EXPANSION_PAYS. Note the translit test's
anchor CER band is ~27.4 (run-081 reproduction); the teacher's own CER
on the same rows is the number that matters.


**Stage B2 VERDICT: EXPANSION_PAYS** (2026-10-30, run-082d). Matched-surface
result on the translit romanization test split (895 rows, exact run-081
protocol): student CER 40.25% / EM 52.4% vs the phonemic teacher
(khm-phonemic-1.0, same rows in-job) 47.15% / EM 44.6% — the 57K SBBIC
weak labels + 16K translit anchor beat the teacher by 6.9 CER points on
its own surface. Caveat carried forward: this compares against the
PHONEMIC teacher; the khm-latn lineage's own band is 27.4, and the
translit-surface score of a convention-blended model is not a lineage
benchmark.

Attempt 3 (running): the convention-correct experiment — SBBIC labeled
with the SHIPPED khm-latn-1.0 artifact (run-082e-khm-latn-label, 24
CPU processes on a100-large, rotating parts, sha256-verified Release
fetch; plain decoders are batch=1-traced but words are tiny) -> weak
labels in the translit convention -> train byt5-small (weak + translit
train anchor, exact run-081 split) -> gate: student CER < teacher CER
on the identical 895 test rows (the lineage comparison vs 27.4).
Verdict script: train_khm_expansion3.py (stage-b3 outputs under
bucket khmer-latn/).


**Attempt 3 verdict: nominal EXPANSION_PAYS, statistically a TIE** (2026-10-31,
run-082f). All 74,992 unique SBBIC words labeled with the shipped
khm-latn-1.0 (0 empties this pass). Student (byt5-small, 74,992-convention
weak labels + 16,120 translit anchor) vs teacher on the identical 895-row
translit test split:

- student CER 27.079% / EM 59.89%
- teacher CER 27.417% / EM 59.66%  (reproduces the published 27.42
  benchmark exactly — protocol identity verified)

The +0.34 CER delta is within noise at n=895. Interpretation: weak-label
expansion REPLICATES the teacher (the labels are the teacher's own
outputs — training converges to the teacher, including its errors). No
evidence expansion alone reaches the CER<15 B7 target. The line's next
real lever is NEW GOLD, not more teacher output: SEAlang / Chuon Nath
full IPA remain the owner-held data asks (B7 blocker unchanged), since
a second decorrelated latn-convention teacher for agreement-denoising
does not exist today.
