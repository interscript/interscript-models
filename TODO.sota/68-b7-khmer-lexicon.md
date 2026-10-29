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
