# urd-vocalized-2.1

Urdu bare-to-vocalized diacritization, **direct-gold**: ByT5-**small**
trained DIRECTLY on the 573,130 human-verified gold pairs of the
data-diacrit public-lineage corpus — no teacher, no relabel, no
distillation step, no LLM anywhere near the labels — int8-dynamic ONNX.
New Urdu frontier: **3.632% full-split raw CER** (WO37 protocol,
11,940 rows) — below the 0.0377 gate, below the shipped champion
urd-vocalized-1.0 (3.74%), and below the shipped distilled student
urd-vocalized-2.0 (3.641%).

The WO93 finding of record: **human-verified gold labels beat
distilled (teacher-relabel) labels** on the same corpus (0.03632 vs
0.03641), with the cleanest possible lineage — a single hop from the
raw google/byt5-small checkpoint to public-lineage gold, zero CLE
exposure anywhere.

## Metrics (WO37 protocol — greedy, single-row, full-split raw CER)

| benchmark | value |
|---|---|
| full-split raw CER (11,940 rows, row-mean) | **3.632%** (gate 3.77; champion urd-vocalized-1.0 3.74; distilled urd-vocalized-2.0 3.641) |
| calibrated Clause 16(e), matched split (urdu-dev#23/#24/#25/#26) | **PASS** — AUC 0.4816 (dev 0.0184 ≤ 0.05), reference self-control 0.5 exact, success-rate 0.515 ≤ 0.6 |
| extraction / verbatim / WordNet probes | PASS (0 violations across all three) |
| parity, int8-dynamic ONNX vs fp32 ONNX reference (single-row greedy, ORT CPU) | cer_delta **0.0671 pp** on 600 samples (int8 gate 2.0pp); argmax flips 0.539%, confident flips 0.349% |
| frozen fixtures | conformance/urd-vocalized-2.1-vectors.json (600 vectors) + golden/urd-vocalized-2.1-int8-dynamic.jsonl |
| eval slice | conformance/wo20/eval600/urd_eval_600.jsonl (sha256 `a06c8a2dcacec88bec0ad85b4e851a78c72429102e4051d2705b994c48108ca0`) |

## Provenance

- Init: raw `google/byt5-small` checkpoint (no interscript ancestry,
  no CLE) — the urd-vocalized small tier.
- Labels: the gold corpus itself — data-diacrit train split, 573,130
  src/tgt pairs (sha256 95736b0d19e57ada3ce435f28300b8a72a3fec6c761df
  ce34770ed9549331ee2; the sha-pinned public-lineage source the run-066
  lineage trained on; owner license review 2026-10-18, explicitly NOT
  CLE).
- Training: `train_student_distill_hf.py` loader (urdu-dev#27
  DATA_GLOB gold mode), run-097-urd-diac-gold, HF Jobs a100-large —
  3 epochs, bs 16 × accum 2, lr 3e-4 cosine (200 warmup), bf16,
  MAXLEN 256, 53,733 steps, chain_pass true.
- Gate chain: quality 0.03632 ≤ 0.0377 (verdict.json) → calibrated
  16(e) PASS on the matched split (run-066 reference) → export PASS →
  conformance fixtures → publish guard PASS.
- sha256: recorded in models.yaml and the GH release SHA256SUMS.

## Data attribution

- **urd-dia (data-diacrit)** — the urd-vocalized lineage's corpus
  (573,130 train / 11,940 held-out test rows; rababa-urdu assembly,
  public-lineage, owner license review 2026-10-18). This model derives
  from NO CLE content: the corpus-CLE overlap discriminator measured
  ZERO shared shingles (ledger #475/#477) and the lineage is a single
  hop from the raw google checkpoint to this corpus.
- **CLE12T003 / CLE12L001** remain licensed and retained per the CLE
  agreement; this model does not derive from them.

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
single-hop public-lineage gold lineage; the citation is carried per the
CLE license program's Schedule D placement rules for the certification
period. CLE-KICS, UET's name is used only to give credit and not in a
way that suggests endorsement.)
