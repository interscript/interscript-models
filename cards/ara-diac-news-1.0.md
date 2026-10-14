# ara-diac-news-1.0

Arabic **news-register specialist** (run-029): byt5-base seq2seq,
register-pure training — 900K QCRI-silver units (~4.5M words of
Wikipedia news-domain labels, published with EMNLP 2025) + WikiNews
gold upsampling, NO classical tashkeela dilution, 2 epochs, r7-init.
IMF v1 int8, 399 MB.

## Metrics

| benchmark | this model | ara-diac-2.0 (generalist) |
|---|---|---|
| WikiNews-2024 multiref WER/DER (first-alternate protocol) | **4.10 / 1.56** | 17.38 / 11.83 |
| SadeedDiac-25 Total DER | 5.4814 | **2.2864** |

## Decode contract (runtime >= py 0.2.0 / npm 5.8.0 / gem 3.1.0)

This model emits slash-separated alternates on some tokens; the
runtimes above return the primary choice automatically
(`first_alternates`). Artifact bytes are unchanged and the sha256
remains valid. Runtimes older than the versions above require the
caller to strip alternates before scoring.

Use this model for news-domain text; use ara-diac-2.0 for
classical/MSA. Two families, never averaged (RESULTS.md: the
dose-response curve and the output-space oracle both close generalist
blending).

## Provenance

- Training: TODO.sota/25 (run-029, HF Jobs a100-large).
- sha256: `e5a52b1530dfa6d6c7ef8970443206ce33af865d0337a58d145945adab33484e`.
- License: BSD-3-Clause (code + weights).
