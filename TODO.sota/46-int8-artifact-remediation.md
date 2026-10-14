# WO46 — shipped-int8 artifact audit + ara-diac-news-1.0 remediation

## Trigger (2026-10-14)

The urd-g2p-base int8 parity catastrophe (0.44 vs 0.16 CER — dynamic
int8 destroys seq2seq decode) put every shipped int8 SEQ2SEQ artifact
under suspicion. Audit result:

| artifact | quant path | verdict |
|---|---|---|
| ara-diac-news-1.0 (int8, 399MB) | ORT dynamic on single-file base graphs | **UNDER TEST — run-029-zipcheck-v3** |
| ara-diac-news-1.2 staged (821MB) | ORT dynamic on a **1MB stub encoder** (external-data split) | broken by construction, never shippable — superseded by WO45 |
| urd-g2p-1.0, tha-g2p-*, fas-g2p-1.0 (fp32 zips) | none | clean |
| heb/ara plane family (int8-static) | static, 3-leg parity GREEN | clean (separate lineage) |

If the zipcheck shows the 1.0 artifact degraded (ONNX WER far off the
4.10 torch number), remediation:

1. Re-export run-029/best as **fp32** (base graphs fit single-file —
   run-040's 1.1 fp32 proves the path), verify shipped-bytes parity
   (same positional-feed harness).
2. Replace the release assets on tag ara-diac-news-1.0 (same weights,
   fixed artifact) + re-stamp models.yaml sha/size.
3. Card note: re-download required; old int8 asset withdrawn.

The 1.1 fp32 base artifact is unaffected (verified fp32 lineage).

## Status

- zipcheck RUNNING; remediation jobs queued behind the l4 wave.
- Exporter for the re-export: export_imf_hf.py EXPORT_PRECISION=fp32
  (one-shot validator-clean metadata: protocols, parity, README — the
  urd publish loop's lessons).
