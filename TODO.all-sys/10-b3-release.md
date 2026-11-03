# B3 — stage 2 + release

## STAGE 2 VERDICT (2026-11-02): MIXED — no ship, owner decides next

run-087-oracle-student (job 6ae7d86f0e0338d1bb7db20c, a100, 5h44m,
google/byt5-base, 3 epochs, 37,500 steps, final loss 0.017; checkpoints
oepoch-0/1/2 in the run repo). In-job evals, final checkpoint:

| gate | required | measured | verdict |
|---|---|---|---|
| RAW multiref WER | < 17.3794 (r7) | **14.0919** | GREEN (−19% vs r7) |
| stretch multiref WER | ≤ 10.1262 (news-1.0) | 14.0919 | MISSED |
| SadeedDiac DER | ≤ 2.3864 (r7 2.2864 + 0.1) | **7.2471** | MISSED |
| SadeedDiac morph DER | — | 5.1881 | (r7 context: 2.2864) |
| SadeedDiac total WER | — | 15.8028 | — |

multiref row: `{"surface": "wikinews-2024-multiref", "WER": 14.0919,
"DER": 10.1289, "words": 10616, "letters": 47162}`.

Reading: the oracle student BEATS r7 on the multiref surface (the thing
the oracle relabel targeted — the arms disagreed there) but is far
worse than r7 on SadeedDiac-25. The single student regressed the
in-domain surface; a plain average with r7, or a surface-selective
router, or more epochs/lower LR on a Sadeed-weighted mix are the open
options. Per the stage gate (ALL green required): NO IMF export, NO
parity run, NO certify. Version remains the owner's; nothing shipped.

Next-step options for the owner (recorded, not executed):
1. Accept the multiref win as a specialist and ship alongside r7
   (needs owner version + naming decision).
2. Retry stage 2 with a Sadeed-weighted corpus mix or 2-phase LR.
3. Close B3 as negative-target-met-partially and bank the relabel
   corpus (durable in bucket run-086-oracle-relabel/).

Stage 1 artifacts (durable): bucket Interscript/isx-training/
run-086-oracle-relabel/ — oracle-targets.jsonl 76MB, RELABEL_DONE,
relabel_stats.json (oracle CER 6.53 vs arms 6.70/9.37; r6 wins 12,680
rows; 18,274 exact ties skipped).
