# urd-vocalized-2.0

Urdu bare-to-vocalized diacritization, **clean-room distillation**:
ByT5-**small** student trained on 439,786 outputs of the run-066
lineage teacher (ByT5-base + data-diacrit public-lineage only — a
teacher whose verified lineage never touched CLE), int8-dynamic ONNX.
New Urdu frontier: **3.641% full-split raw CER** (WO37 protocol,
11,940 rows) — below the 0.0377 gate AND below the shipped champion
urd-vocalized-1.0 (3.74%).

The WO92 recovery arc, completed: the CLE-DAPT teacher line failed the
calibrated Clause 16(e) gate on every arm that kept it as label source
(AUC 0.6319 → 0.6475 — memorization transfers through targets with
ZERO corpus-CLE shingle overlap); the clean-room teacher collapses the
signal to chance (0.4933) while *improving* quality. Data validity and
lineage cleanliness were the levers, not training dynamics.

## Metrics (WO37 protocol — greedy, single-row, full-split raw CER)

| benchmark | value |
|---|---|
| full-split raw CER (11,940 rows, row-mean) | **3.641%** (gate 3.77; champion urd-vocalized-1.0 3.74) |
| calibrated Clause 16(e), matched split (urdu-dev#23/#24/#25/#26) | **PASS** — AUC 0.4933 (dev 0.0067 ≤ 0.05), reference self-control 0.5 exact, success-rate 0.5267 ≤ 0.6 |
| extraction / verbatim / WordNet probes | PASS (0 violations across all three) |
| parity, int8-dynamic ONNX vs fp32 ONNX reference (single-row greedy, ORT CPU) | cer_delta **0.0062 pp** on 600 samples (int8 gate 2.0pp); argmax flips 0.171%, confident flips 0.105% |
| frozen fixtures | conformance/urd-vocalized-2.0-vectors.json (600 vectors) + golden/urd-vocalized-2.0-int8-dynamic.jsonl |
| eval slice | conformance/wo20/eval600/urd_eval_600.jsonl (sha256 `a06c8a2dcacec88bec0ad85b4e851a78c72429102e4051d2705b994c48108ca0`) |

## Provenance

- Teacher: `run-066-urd-diac-base/best` (google/byt5-base init +
  data-diacrit public-lineage only — verified CLE-clean, ledger #471).
  The CLE-DAPT teacher (run-092) is retired from the label-source role.
- Relabel: 573,130 public-lineage src rows → 439,786 guarded pairs
  (`relabel_teacher_hf.py`, parse-fixed, semantic-invariant gates,
  GUARD_N 8 regurgitation drops 0; run-096b corpus review gate PASS).
- Student: `train_student_distill_hf.py`, run-096-urd-diac-distill,
  HF Jobs a100-large — google/byt5-small init, 3 epochs, bs 16 ×
  accum 2, lr 3e-4 cosine (200 warmup), bf16, MAXLEN 256, 41,232
  steps, chain_pass true.
- Gate chain: quality 0.03641 ≤ 0.0377 (verdict.json) → calibrated
  16(e) PASS on the matched split → export PASS → conformance fixtures
  → publish guard PASS.
- sha256: recorded in models.yaml and the GH release SHA256SUMS.

## Data attribution

- **urd-dia (data-diacrit)** — the urd-vocalized lineage's corpus
  (573,130 train / 11,940 held-out test rows; rababa-urdu assembly,
  public-lineage, owner license review 2026-10-18). This model derives
  from NO CLE content: the corpus-CLE overlap discriminator measured
  ZERO shared shingles (ledger #475) and the lineage verification
  traced every ancestor to public-lineage data (ledger #471).
- **CLE12T003 / CLE12L001** remain licensed and retained per the CLE
  agreement; this model does not derive from them (the clean-room arm
  dissolves the derivation question entirely).

## License

BSD-3-Clause (code + weights).

## Attribution (Schedule D)

Linguistic resources provided by the Center for Language Engineering
(CLE), Al-Khawarizmi Institute of Computer Science (KICS), University of
Engineering and Technology (UET), Lahore, Pakistan.

> CLE Urdu Digest Corpus 1M (International Package), Catalogue No.
> CLE12T003; CLE Urdu WordNet (International Package), Catalogue No.
> CLE12L001. Center for Language Engineering, Al-Khawarizmi Institute of
> Computer Science, University of Engineering and Technology, Lahore,
> Pakistan.

(The released model derives from no CLE content — zero corpus overlap,
verified lineage; the citation is carried per the CLE license program's
Schedule D placement rules for the certification period. CLE-KICS, UET's
name is used only to give credit and not in a way that suggests
endorsement.)
