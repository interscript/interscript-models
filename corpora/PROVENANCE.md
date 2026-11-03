# Corpus license provenance — the license gate's evidence file

Verified 2026-10-17. The gate blocks on `UNVERIFIED` (terms not read)
and on `LicenseRef-*` (read but restricted). Only verified-open SPDX
licenses clear it.

| corpus | upstream | license | verdict |
|---|---|---|---|
| fas-dia | [MahtaFetrat/HomoRich-G2P-Persian](https://huggingface.co/datasets/MahtaFetrat/HomoRich-G2P-Persian) | **CC0-1.0** (HF cardData, verified via API) | CLEAR |
| urd-g2p-dict | [humair025/urdu-g2p-dictionary](https://huggingface.co/datasets/humair025/urdu-g2p-dictionary) | **non-commercial** (HF card `license_name`, terms at github.com/humair-m/urdu-g2p) | BLOCKED — owner: may weights trained on it ship under the BSD release lane? |
| qcri-wiki | QCRI `Wikipedia_20240420.diac.jsonl`; system repo [kdarwish/Qatara](https://github.com/kdarwish/Qatara) carries **no license file** | default copyright | BLOCKED — owner: contact QCRI for terms |
| urd-dia | mixture of the `mahwizzzz` + `humairmunirawn` corpora (rababa-urdu/docs/paper-urdu/main.pdf) | none found on either source (HF/GitHub search) | BLOCKED — owner: contact authors or replace the corpus |
| tashkeela (classical, r8-mined) | tashkeela-processed via SourceForge/Kaggle (rababa-tashkeela/README.adoc) | **GPLv2** "as per the original datasets" | CLEAR for training; copyleft note for weight redistribution |

## Owner decision queue (what the license gate is holding)

1. **urd-g2p** — non-commercial data: ship weights research-only, or
   retrain on an open replacement before release?
2. **qcri-wiki (ara-diac)** — QCRI has no license on Qatara; their own
   models are published. Ask QCRI for explicit terms, or retrain the
   ara lane on Tashkeela-derived data only (GPLv2 implications then
   apply to weights).
3. **urd-dia** — no licenses found on the mixed sources. Contact the
   paper authors, or rebuild the corpus from licensed sources.

Notes:
- Derived corpora (staged jsonl splits) inherit their upstream license.
- micsell/hebrew_speech_kan_nikud: NO license (WO43) — excluded from
  the registry entirely; owner ask drafted in TODO.sota/43.
