# Urdu WO65 — stage 1 + 2 (staged)

Launch after B3 frees the a100s — full command pair recorded in
TODO.sota/65 (arms urd-diac-1.0 + urd-diac-base-1.0 over bucket
rababa-urdu-cc174b96@data-diacrit, D_RUN=run-088-urd-oracle, 200K x
300B subset). Stage 2 = train_oracle_student_hf.py adapted
(google/byt5-base). Gate CER < 3.57, target < 3.
