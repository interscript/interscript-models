# Corpus license provenance — the license gate's evidence file

Verified with source links on 2026-10-17. `UNVERIFIED` below is a
blocking state: `isxml gate` refuses to publish any model trained on
that corpus until the terms are read and recorded here.

| corpus | upstream | license | status |
|---|---|---|---|
| fas-dia | [MahtaFetrat/HomoRich-G2P-Persian](https://huggingface.co/datasets/MahtaFetrat/HomoRich-G2P-Persian) | **CC0-1.0** (HF cardData, verified via API) | CLEAR |
| urd-dia | paper-derived dataset (rababa-urdu/docs/paper-urdu/main.pdf; uploaded from /opt/urdu/data per rababa-urdu/modal_app_diacrit.py) | unknown | UNVERIFIED — read the paper's dataset terms |
| urd-g2p-dict | [humair025/urdu-g2p-dictionary](https://huggingface.co/datasets/humair025/urdu-g2p-dictionary) | HF card says `other` (custom terms) | UNVERIFIED — read card text |
| qcri-wiki | QCRI published Wikipedia_20240420.diac.jsonl (WO17: "provenance + license recorded in the dataset repo") | not yet read | UNVERIFIED — locate QCRI's dataset repo and read terms |
| tashkeela (classical, r8-mined) | tashkeela-processed via SourceForge/Kaggle (rababa-tashkeela/README.adoc) | **GPLv2** "as per the original datasets" | CLEAR (copyleft — note for weights distribution review) |

Notes:
- Derived corpora (staged jsonl splits) inherit their upstream license.
- GPLv2 tashkeela: training-usage vs weight-redistribution implications
  are an owner decision — recorded here so the question is visible.
- micsell/hebrew_speech_kan_nikud: NO license (WO43) — excluded from
  the registry entirely; owner ask drafted in TODO.sota/43.
