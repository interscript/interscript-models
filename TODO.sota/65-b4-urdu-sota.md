# WO65 — B4: Urdu — diac CER < 3; G2P license path

Status: IN_PROGRESS · G2P half BLOCKED-OWNER (commercial-license data); diac push 3.57 → < 3 pending
Goal: urd-diac 3.57 → CER < 3; urd-g2p research-only → commercial-
usable data lineage.
Method: diac — oracle relabel arms only if teachers decorrelate (banked
negative: correlated arms transfer nothing); morph/lexicon features;
VRR. G2P — owner selects licensed corpus (option drafts in WO50);
retrain; relabel artifacts non-research-only.
Acceptance: external protocol numbers; license gate green on G2P.


## CLE corpus acquisition (2026-10-29, owner-reported)

The owner is waiting for an Urdu corpus from CLE (Center for Language
Engineering, UET Lahore). Owner-side steps enumerated for the record:

1. Written license terms from CLE covering (a) research vs commercial use,
   (b) redistribution of DERIVED WEIGHTS (the clause our gate blocks on),
   (c) required attribution wording, (d) corpus version and checksum.
2. The license_review record filed by the owner (law: UNVERIFIED/LicenseRef-*
   blocks publish; waivers are license_review records). Until then urd-g2p
   stays GATED-1 ready-pending-license (weights done, 0.16 CER, parity
   cleared, fixtures built — 53-ship-set).
3. Data channel decision: GitHub Releases re-release if the license permits
   corpus redistribution; gated store + weights-only otherwise.
4. Fallback if CLE stalls: ship urd-g2p research-only, or retrain on an open
   Urdu dictionary (pre-recorded ship-set options).
5. On license-green: retrain urd-g2p on the licensed corpus, re-run WO51
   gates, flip card/index from research-only, ship. Separately: whether the
   CLE corpus also feeds the urd-diac 3.57 -> < 3 push is its own WO.


### WO65 stage-1 staged (2026-10-31): launch command ready

The B3 oracle machinery generalizes to Urdu (oracle_relabel_onnx.py:
D_ARM1_* env primary arm + D_ROWS_JSONL pre-paired corpus mode, PR'd in
interscript-train #141). Launch after the B3 arms free the a100s:

- Arms (both SHIPPED, stable): urd-diac-1.0 (urd-diac-1.0-fp32.zip,
  release tag urd-diac-1.0, 1.42GB fp32) + urd-diac-base-1.0
  (urd-diac-base-1.0-fp16.zip, tag urd-diac-base-1.0, 1.35GB fp16,
  different lineage = decorrelated). Stage both zips to bucket
  urd-arms/ first (sha256 from models.yaml).
- Corpus: bucket rhtse/jobs-artifacts/rababa-urdu-cc174b96 revision
  data-diacrit -> mount /data-dia; rows = data-diacrit/train.jsonl
  (573,130 rows, sha256 in corpora/urd-dia.yaml, owner-approved
  license review 2026-10-18). D_ROWS_JSONL=/data-dia/data-diacrit/
  train.jsonl D_SUBSET=200000 D_MAXB=300 D_BS=48.
- Run dir: D_RUN=run-088-urd-oracle; two parallel D_ARM_ONLY jobs as
  in B3. Then stage 2 = train_oracle_student_hf.py adapted (O_INIT
  google/byt5-base; corpus mounts change) -> gate CER < 3.57 baseline,
  target CER < 3 (WO65 method: decorrelated teacher arms only).
