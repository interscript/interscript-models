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
