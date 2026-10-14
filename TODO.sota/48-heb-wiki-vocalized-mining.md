# WO48 — he-wiki vocalized mining: the unblocked gold-nikud lever

## Why

HE g2p's audio arm converged at 0.4462 — WORSE than our shipped
nikud+rules chain (0.2393), so the g2p frontier runs through nikud
model quality. WO43 (micsell gold speech nikud) is license-blocked.
But Hebrew Wikipedia contains a large fully-vocalized subset
(poetry, religious, children's, linguistic articles) under **CC
BY-SA** — gold nikud at web scale, no permission required.

## Arm

`run-071-heb-vocalized-mine` (cpu-basic, streaming):

1. Stream `wikimedia/wikipedia` config `20231101.he` (HF datasets,
   no local download — no-local-large-data honored: stream in-job,
   write only the mined pairs).
2. Vocalization detector per PARAGRAPH: fraction of Hebrew letters
   carrying niqqud ≥ 0.85 AND ≥ 40 letters (poetry/verse detection
   excluded — line-broken text skipped).
3. Emit (unpointed, pointed) sentence pairs: sentences split on
   ח.!?؛, niqqud stripped from the source side; dedupe; cap by
   count (default 2M sentences) + train/val split.
4. Output: heb-vocalized-{train,val}.jsonl on the bucket.

## Then

Fine-tune the nikud champion lineage (plane-2.0 trainer or the byt5
nikud measurement arm per WO43's stage-2 fallback) on mined pairs +
replay of the original corpus (register-forgetting guard). Gates:
nikud DER ≤ 8.18 on the crown benchmark AND g2p-chain nCER (nikud →
rules) < 0.2393 — i.e., the mined data must beat the shipped chain
before anything ships.

## Cost

Mining ≈ free (cpu, streaming, ~2-4h). Fine-tune ≈ 8-14 GPU-h.

## Result (2026-10-14): he-wiki leg = 1,244 pairs — a DUD at scale

The strict detector (≥0.55 marked-fraction, measured calibration:
fully-vocalized text ≈0.69, plain 0.0) found only 632 vocalized
paragraphs in ALL of he-wiki — wiki prose is simply not pointed.

## Source pivot (spec'd, queued behind the fleet drain)

Hebrew **Wikisource** (he.wikisource.org, CC BY-SA — same family as
he-wiki): Tanakh, mishna, poetry — densely and consistently
vocalized; expected yield 10-50K+ gold pairs. Same miner, MediaWiki
API source, attribution in the dataset card. NOT launched while the
l4/a100 fleet is saturated — and the WO42 filter verdict may
re-weight it (if filtered-retrain clears 0.2393, the mined-nikud
fine-tune downgrades to optional).
