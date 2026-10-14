# ara-diac-news-1.1

Base-tier refresh of the news-register specialist (run-040): the
run-029 recipe retrained on the **primary-reading (alternate-stripped)
corpus** — the model no longer emits slash alternates, so every
runtime scores it identically. byt5-base seq2seq, IMF v1 fp32
(2.16 GB, 2 parts).

## Metrics (first-alternate protocol, WikiNews-2024 multiref)

WER **8.85** / DER 2.84 (vs 4.10 / 1.56 first-alt for 1.0 — 1.0 emits
alternates, 1.1's raw output IS the primary reading).

Use when you want the news specialist without the decode-contract
dependency; use ara-diac-news-large-1.0 for the best quality.
