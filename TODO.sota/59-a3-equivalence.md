# WO59 — A3: system-equivalence checker + distinguishing corpora

Status: MOSTLY DONE (ruby shipped #816 + self-testing CI #819; ts/py port pending)
Goal: mechanically decide/estimate whether two systems coincide, and
produce the minimal test corpus that distinguishes them.
Method:
1. Compose maps as automata over a sampled alphabet (the ruby
   interpreter as oracle); bounded-equivalence search (input-length
   horizon escalation).
2. Distinguishing corpus generator: for near-equivalent systems emit
   the smallest input set that yields differing outputs; use it to
   justify alias/dedup decisions in the corpus.
Acceptance: checker + generator shipped in the runtime toolchain;
every claimed-equivalent map pair in maps/ justified by the checker;
CI uses it to prevent accidental duplicates.
