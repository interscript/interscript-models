#!/usr/bin/env bash
# IVRB HF Jobs bootstrap — one job per decode leg.
#
# Usage (inside the job, after the harness is fetched at IVRB_MODELS_SHA):
#   hfjob.sh <model_id> <shard> [<shard> ...]     e.g. hfjob.sh urd-vocalized-1.0 0/2 1/2
#
# Sha pins (identity, never paths):
#   IVRB_MODELS_SHA  this repo's harness commit (set at dispatch time)
#   interscript-py   bf3ac6f66458c18e87ede58848d0aacdee47ef9d (wo20-fix-py)
#   interscript/maps cc67dd3 (= maps release v3.2.0, maps/ byte-identical)
#   model zips       release downloads; ivrb.py sha256-verifies each
#   data             bucket artifact + HF dataset; ivrb.py sha256-verifies each
#
# Records land in the rhtse/jobs-artifacts bucket under ivrb/ and are
# verify-read back after upload. No GPU: these legs are cpu-basic.
set -euo pipefail

MODEL="${1:?model id required}"; shift
SHARDS=("$@")
: "${IVRB_MODELS_SHA:?IVRB_MODELS_SHA must pin the harness commit}"

WORK="${WORK:-/ivrb}"
mkdir -p "$WORK/out"
cd "$WORK"

echo "[job] model=$MODEL shards=${SHARDS[*]} harness=$IVRB_MODELS_SHA"

# ---- pinned sources -------------------------------------------------------
git clone -q --filter=blob:none https://github.com/interscript/interscript-models.git models
git -C models checkout -q "$IVRB_MODELS_SHA"
git clone -q https://github.com/interscript/interscript-py.git ipy
git -C ipy checkout -q bf3ac6f66458c18e87ede58848d0aacdee47ef9d
git clone -q --filter=blob:none https://github.com/interscript/maps.git maps
git -C maps checkout -q cc67dd3

export IVRB_PY_SRC="$WORK/ipy/src"
export PYTHONPATH="$IVRB_PY_SRC${PYTHONPATH:+:$PYTHONPATH}"
export IVRB_MAPS="$WORK/maps/maps"
export IVRB_OUT="$WORK/out"
export IVRB_DATA_URD="$WORK/urd-test.jsonl"
export IVRB_DATA_HEB="$WORK/heb-test.jsonl"

# ---- deps -----------------------------------------------------------------
pip install -q onnxruntime pyyaml numpy "huggingface_hub[cli]"
export HF_TOKEN="${HF_TOKEN:?HF_TOKEN secret required}"

# ---- data (house channels; ivrb.py sha256-verifies both) ------------------
hf buckets cp "hf://buckets/rhtse/jobs-artifacts/rababa-urdu-cc174b96/data-diacrit/test.jsonl" "$IVRB_DATA_URD"
python3 - <<'PY'
from huggingface_hub import hf_hub_download
import os, shutil
p = hf_hub_download("Interscript/hebrew-v4", "test.jsonl", repo_type="dataset",
                    token=os.environ["HF_TOKEN"])
shutil.copyfile(p, os.environ["IVRB_DATA_HEB"])
print("[job] heb data fetched")
PY

# ---- model zip (release channel; harness verifies the pin) ----------------
case "$MODEL" in
  urd-vocalized-1.0)        URL=https://github.com/interscript/interscript-models/releases/download/urd-diac-1.0/urd-diac-1.0-fp32.zip ;;
  urd-vocalized-2.1)        URL=https://github.com/interscript/interscript-models/releases/download/urd-vocalized-2.1/urd-vocalized-2.1-int8-dynamic.zip ;;
  heb-vocalized-1.0)        URL=https://github.com/interscript/interscript-models/releases/download/heb-diac-1.0/heb-diac-1.0-fp32.zip ;;
  heb-vocalized-1.1)        URL=https://github.com/interscript/interscript-models/releases/download/heb-diac-1.1/heb.zip ;;
  heb-vocalized-small-1.0)  URL=https://github.com/interscript/interscript-models/releases/download/heb-diac-small-1.0/heb-diac-small-1.0-fp32.zip ;;
  *) echo "unknown model: $MODEL" >&2; exit 2 ;;
esac
curl -sSLo "$WORK/model.zip" "$URL"
export IVRB_ZIP="$WORK/model.zip"

# ---- decode legs (sequential: bounds RAM on cpu-basic) ---------------------
for s in "${SHARDS[@]}"; do
  echo "[job] === $MODEL shard $s ==="
  python3 models/benchmarks/ivrb/ivrb.py "$MODEL" --shard "$s"
done

# ---- upload + verify-read-back --------------------------------------------
for f in "$WORK"/out/*.json; do
  name="$(basename "$f")"
  dest="hf://buckets/rhtse/jobs-artifacts/ivrb/$MODEL.$name"
  hf buckets cp "$f" "$dest"
  hf buckets cp "$dest" "$WORK/verify-$name"
  cmp "$f" "$WORK/verify-$name" && echo "[job] uploaded + verified $name"
done
echo "[job] DONE $MODEL"
