# B3 — stage 2 + release

The two relabel arms auto-consolidate (monitor armed; RELABEL_DONE +
relabel_stats.json land in bucket run-086-oracle-relabel/). THEN:
launch run-087-oracle-student per task #93 (byt5-base on oracle
targets; gates RAW multiref WER < 17.3794, stretch <= 10.1262, Sadeed
DER within +0.1 of 2.2864). On gates green: export IMF artifact +
parity (>=500 samples single-row greedy) + certify (tools/certify.py);
the RELEASE VERSION IS THE OWNER'S DECISION — prepare, never pick.
