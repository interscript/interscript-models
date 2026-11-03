# WO42 — HE student label-filter arm (conditional lever)

## Position in the decision tree (post-WO40)

Teacher labels are GOOD (true in-domain PER 0.1382). If e12 (+8
epochs) still misses the 0.2393 gate, the residual is hypothesis
domain/quality: the 200h labels are podcast spontaneous speech while
the phonikud benchmark is dictionary/read style, plus noisy segments
(music, hesitation, code-switch) the teacher faithfully transcribed.
This arm filters the label set before any teacher-scale spend
(WO36 stage 3 stays last resort).

## Filter design (run-067-label-filter)

1. **Self-consistency**: decode each of the 136,767 label rows twice
   more with time-stretch ±10% (sox-free: torchaudio resample trick —
   decode at effective 1.1×/0.9× speed); keep a row when the third
   decode's normalized phone error vs the stored label < 0.15.
   Rationale: stable rows have clean audio; warped decodes diverge on
   noise/music/hesitation.
2. **Ratio guard**: drop rows where len(ipa)/len(text) is outside the
   corpus 1st-99th percentile band (phonemization failures).
3. Rebuild the student set from survivors; retrain byt5-base with the
   e12 recipe (same epochs as the best-known-good config); gate:
   phonikud nCER < e12's number, then the standing 0.2393.

## Cost

2 extra decode passes over 200h ≈ 3 GPU-h + student retrain ≈ 7 GPU-h
(l4 or a100 spare slot). Fully resumable (labels.jsonl-style row
offsets; the WO39 completed_lines pattern).

## Gates and abort

- If filtering removes > 40% of rows, the 200h slice is noisier than
  assumed — report to owner before proceeding (scale may beat
  filtering at that point; WO36 stage 3 un-demotes).
- If the filtered-retrain does not beat e12, CLOSE the audio arm at
  its best number, keep rules 0.2393 shipped, and route remaining
  budget to WO43.

## Verdict (2026-10-15): PARKED — smoke data kills the cost-benefit

Batched smoke (2 shards, timed): shard 1 = **3,817s / 1,215 rows**
(~64 min/shard → the full 126-shard filter ≈ 134 GPU-h — not viable).
THE FINDING that matters: **retention = 88%** (1,072/1,215 kept at
0.15 phone-error tolerance) — the labels are largely SELF-CONSISTENT
under ±10% time-stretch, refuting the "lots of noise" hypothesis.
The student's 0.4462 gap is therefore DOMAIN MISMATCH (podcast
acoustics vs citation forms), which no label filter can close.
HE g2p path: WO48b (gold-nikud supply → nikud model → rules chain).
The filter tool remains in the repo if a cheaper formulation
(e.g., single-pass confidence) ever earns it.
