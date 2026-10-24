# Target documentation — WO87 evidence (2026-10-24)

`target-documentation.json`: every index id decoded through the
reference loader with a per-language probe — the evidence for
target-accurate naming.

## Verified target families

| family | ids | output sample |
|---|---|---|
| Arab-vocalized (diac) | ara-diac-*, urd-diac-* | 'السَّلَامُ عَلَيْكُمْ' |
| Heb-vocalized (nikud) | heb-diac-* (except plane: load ERROR) | 'שָׁלוֹם' |
| Thai-phonemic (toned, dots) | tha-g2p-* , tha-phonemic-1.0 | 'sa˨˩.wat̚˨˩.diː˧' |
| IPA (narrow, stress) | urd-g2p-* | 'ɪst̪ɪqˈbaːl' |
| Latin-letter phonemic | fas-g2p-1.0 | 'salAm' |
| Latin romanization | khm-latn-1.0 | 'suostei' |

## Defects found by the sweep

1. **ara-diac-news-1.1: artifact LOST** — index/release 404; bytes
   exist nowhere (bucket zip is news-1.0's, sha differs). Withdrawn in
   models.yaml; restore = re-export from run-029 best as a new version.
2. **Plane family non-contract** (ara-diac-plane-1.0,
   ara-diac-plane-large-1.0, heb-diac-plane-1.0/2.0): zips fail the IMF
   v1 file contract ("missing required file: encoder.onnx") — pre-
   standard layout. Re-export or mark legacy-incompatible.
3. **ara-diac-small-1.0-int8 output corruption**: spurious 'F' tokens
   ('...عَلَيْكُمْFمْF') — quantization-era artifact; superseded by the
   2.x line anyway.
