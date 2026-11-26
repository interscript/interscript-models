# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "torch==2.5.1",
#   "transformers==4.46.3",
#   "accelerate>=1.1.0",
#   "onnx",
#   "onnxruntime",
#   "pyyaml",
# ]
# ///
"""WO95 ship export: multi-vocalized-base-1.0 — export + parity + golden + vectors.

One in-job pass (the WO92 shipgate doctrine) over the run-098 joint
checkpoint (step-80010).

Conditioning folding (the export-contract decision of record, WO95 ship
notes): the joint model is conditioned by atomic language-prefix
sentinel ids (<he: = 384, <ur: = 385) that the IMF byte-table runtime
cannot express (canonical encode tops out at id 258). Each language's
sentinel is folded INTO its encoder graph: the traced encoder embeds
the plain byte-encoded input_ids, concatenates the sentinel embedding
at position 0, and runs the stack — the runtime feeds exactly what it
always feeds, the model sees exactly what it was trained on. Two
materializations of the SAME trained weights:

    multi-vocalized-base-1.0       he fold  (the owner-named base id)
    multi-vocalized-base-1.0-ur    ur fold  (publish --key variant; the
                                   zip's internal metadata keeps the
                                   base id per the ara-diac-small-1.0
                                   -int8 precedent)

Decoders are language-independent: exported once, shared into both
variants. Arms: fp32 ONNX (the parity reference) + int8-DYNAMIC (house
quantize_int8: MatMul/Gemm only, tied head fp32 excluded — the
urd-vocalized-2.1 shipped arm; the T5 bias subgraph is never QDQ'd
because only MatMul/Gemm nodes are candidates).

Parity (urd-vocalized-2.1 ship-round thresholds, per language slice):
- int8 CER-delta <= 2.0pp vs the torch reference (house Parity gate,
  >= 500 samples; write_parity enforces + strict-validates),
- row flip-rate (int8 output != fp32-onnx output) <= 1%,
- fp32-onnx vs torch sanity flips + fp32 CER-delta recorded.
The torch reference is the house module-level decoder math with the
fold applied (embed + prepend sentinel + identical loop) — it matches
training exactly (tok("<he:"+src) == [384] + bytes+3 == the fold).
Slices: the committed eval600 files (sha256 asserted in-job); MAXLEN
512, single-row greedy (the urd-2.1 law; the WO51 law — exports take
only input_ids).

Informational (recorded, never gated here): urd row-mean raw-char CER
per arm (house char_error_rate); heb crown seq2seq_der per arm on the
<=512-src-byte sub-slice (count disclosed).

Golden ({"input","tokens"} from the shipped int8 arm) and conformance
vectors ({src,out,lang}, single-row-greedy, the urd-vocalized-2.1
vectors shape) for both slices.

Outputs -> isx-training:/wo95-ship/ (zips, golden/, vectors json,
SHA256SUMS.txt, verdict.json, EXPORT_DONE). Verdict carries every gate
number; STOP happens at the orchestration level.

Env: REPO_PIN (interscript-models commit — REQUIRED), CKPT (/ckpt).
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO_PIN = os.environ["REPO_PIN"]
REPO_DIR = "/repo"
CKPT = Path(os.environ.get("CKPT", "/ckpt"))
CKPT_DIR = CKPT / "run-098-multi-vocalized" / "step-80010" / "model"
OUT = CKPT / "wo95-ship"
WORK = Path("/work")
MAXLEN = 512
FLIP_GATE = 0.01
SEED = 42

URD_SLICE = "conformance/wo20/eval600/urd_eval_600.jsonl"
HEB_SLICE = "conformance/wo20/eval600/heb_eval_600.jsonl"
URD_SLICE_SHA = "a06c8a2dcacec88bec0ad85b4e851a78c72429102e4051d2705b994c48108ca0"
MODEL_ID = "multi-vocalized-base-1.0"
PREFIX_IDS = {"he": 384, "ur": 385}
PREFIX_STR = {"he": "<he:", "ur": "<ur:"}
RUN = "wo95-ship-export"

SCHEDULE_D = (
    "Hebrew: hebrew-v4 gold (owner-approved crown-lineage license review "
    "record). Urdu: data-diacrit gold, sha256 95736b0d (owner license "
    "review 2026-10-18, weights-dependency note). No restricted corpus "
    "in any lineage."
)


def log(msg: str) -> None:
    print(f"[{RUN}] {msg}", flush=True)


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_slice(repo: Path, rel: str, want_sha: str | None):
    rows = [json.loads(l) for l in (repo / rel).read_text(encoding="utf-8").splitlines()
            if l.strip()]
    got = sha256_file(repo / rel)
    if want_sha:
        assert got == want_sha, f"{rel} sha mismatch: {got} != {want_sha}"
    return [(r["src"].strip(), r["tgt"].strip()) for r in rows], got


def lev(a: str, b: str) -> int:
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


_NIQQUD_MARKS_DER = set("ְֱֲֳִֵֶַָֹֺֻּֽֿׁׂ־")


def seq2seq_der(generated: str, gold: str) -> tuple[float, int]:
    """Crown DER — copied verbatim from interscript-train
    src/rababa/evaluate.py (the metric of record)."""

    def _parse(text):
        units = []
        current_consonant = None
        current_niqqud = []
        for ch in text:
            if ch in _NIQQUD_MARKS_DER:
                current_niqqud.append(ch)
            else:
                if current_consonant is not None:
                    units.append((current_consonant, "".join(current_niqqud)))
                current_consonant = ch
                current_niqqud = []
        if current_consonant is not None:
            units.append((current_consonant, "".join(current_niqqud)))
        return units

    gen_units = _parse(generated)
    gold_units = _parse(gold)
    if not gold_units:
        return 0.0, 0
    wrong = 0
    total = len(gold_units)
    for i in range(total):
        if i >= len(gen_units):
            wrong += 1
            continue
        if gen_units[i] != gold_units[i]:
            wrong += 1
    return wrong / total, total


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "golden").mkdir(parents=True, exist_ok=True)
    WORK.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    # ---------------- pinned ship-chain repo ----------------
    if not Path(REPO_DIR).exists():
        subprocess.run(["git", "clone", "--depth", "1",
                        "https://github.com/interscript/interscript-models.git",
                        REPO_DIR], check=True)
    subprocess.run(["git", "-C", REPO_DIR, "fetch", "--depth", "1", "origin",
                    REPO_PIN], check=True)
    subprocess.run(["git", "-C", REPO_DIR, "checkout", "--detach", "FETCH_HEAD"],
                   check=True)
    head = subprocess.run(["git", "-C", REPO_DIR, "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    log(f"repo pinned {head[:12]}")
    sys.path.insert(0, f"{REPO_DIR}/src")

    # ---------------- checkpoint (copy-then-load law) ----------------
    import torch
    torch.manual_seed(SEED)
    shm = Path("/dev/shm/run-098-model")
    if not shm.exists():
        log("copying checkpoint to /dev/shm (mmap lesson)")
        shutil.copytree(CKPT_DIR, shm)
    from imf.export import (decode_tokens, head_matmul_names,
                            load_byte_seq2seq, quantize_int8)
    model = load_byte_seq2seq(shm)
    model.eval()
    log(f"model loaded vocab={model.config.vocab_size}")

    # ---------------- slices ----------------
    urd_pairs, urd_sha = load_slice(Path(REPO_DIR), URD_SLICE, URD_SLICE_SHA)
    heb_pairs, heb_sha = load_slice(Path(REPO_DIR), HEB_SLICE, None)
    log(f"slices: urd={len(urd_pairs)} sha ok; heb={len(heb_pairs)} sha={heb_sha[:12]}")

    # ---------------- shared decoder graphs (language-independent) ----------------
    import torch.nn as nn
    from imf.export import _decoder_kv, _decoder_plain, _kv_io_names, _sample_pasts
    dec_model = model  # decoders traced from the pristine model (export_graphs
    # deep-copies internally for the encoder; the decoder wrappers read weights
    # at trace time — the model stays eval/frozen throughout)
    graphs_dir = WORK / "graphs"
    graphs_dir.mkdir(parents=True, exist_ok=True)
    with torch.no_grad():
        ids = torch.tensor([[104, 101]])
        hidden = dec_model.get_encoder()(input_ids=ids)[0]
    torch.onnx.export(
        _decoder_plain(dec_model), (torch.tensor([[0]]), hidden),
        graphs_dir / "decoder.onnx",
        input_names=["input_ids", "encoder_hidden_states"],
        output_names=["logits"], opset_version=14, dynamo=False,
        dynamic_axes={"input_ids": {0: "batch", 1: "seq"},
                      "encoder_hidden_states": {0: "batch", 1: "seq"},
                      "logits": {0: "batch", 1: "seq"}})
    num_layers = dec_model.config.num_decoder_layers or dec_model.config.num_layers
    pasts = _sample_pasts(dec_model, hidden)
    kv_inputs = ["input_ids", "encoder_hidden_states"] + _kv_io_names(num_layers)[0]
    kv_outputs = _kv_io_names(num_layers)[1]
    dynamic = {"input_ids": {0: "batch", 1: "cur_seq"},
               "encoder_hidden_states": {0: "batch", 1: "enc_seq"},
               "logits": {0: "batch", 1: "cur_seq"}}
    for name in kv_inputs[2:]:
        dynamic[name] = {0: "batch", 2: "past_seq"}
    for name in kv_outputs[1:]:
        dynamic[name] = {0: "batch", 2: "present_seq"}
    with torch.no_grad():
        torch.onnx.export(
            _decoder_kv(dec_model), (torch.tensor([[0]]), hidden, *pasts),
            graphs_dir / "decoder-kv.onnx", input_names=kv_inputs,
            output_names=kv_outputs, opset_version=14, dynamo=False,
            dynamic_axes=dynamic)
    dec_graphs = {"decoder.onnx": graphs_dir / "decoder.onnx",
                  "decoder-kv.onnx": graphs_dir / "decoder-kv.onnx"}
    log("shared decoder graphs exported (opset 14)")

    # ---------------- folded encoder graphs + zips ----------------
    class FoldedEncoder(nn.Module):
        def __init__(self, enc, prefix_id: int):
            super().__init__()
            self.enc = enc
            self.pid = int(prefix_id)

        def forward(self, input_ids):
            emb = self.enc.embed_tokens(input_ids)
            p = self.enc.embed_tokens(torch.full(
                (input_ids.shape[0], 1), self.pid, dtype=torch.long,
                device=input_ids.device))
            return self.enc(inputs_embeds=torch.cat([p, emb], dim=1))[0]

    from imf.pack import pack_zip
    from imf.schema import ModelMetadata

    def base_meta_for(lang: str, precision: str) -> ModelMetadata:
        return ModelMetadata(
            format="imf-v1",
            id=MODEL_ID,
            task="diacritization",
            source_script="Hebr" if lang == "he" else "Arab",
            target="Hebr" if lang == "he" else "Arab",
            tokenizer="bytes",
            opset=14,
            decoder="kv",
            precision=precision,
            license="BSD-3-Clause",
            trained_from=(
                "run-098-multi-vocalized/step-80010 (job rhtse/6b06d122d91f621b9"
                "3079037): joint ByT5-base, init google/byt5-base, 3 epochs on "
                "heb hebrew-v4 gold (50,433 rows x3 window oversample) + urd "
                "data-diacrit gold (573,130 rows sha256 95736b0d); WO95 ledger "
                "models#490/#495; " + SCHEDULE_D),
            # the of-record quality metrics (the strict validator requires a
            # non-empty metrics block; write_parity adds the parity block on
            # top) — verbatim from the run-098 verdict
            metrics=[
                {
                    "name": "ur_cer_row_mean",
                    "value": 0.03604,
                    "protocol": "WO37 protocol (row-mean raw-char CER, "
                                "11,940 rows, data-diacrit test)",
                    "source": "isx-training:/run-098-multi-vocalized/"
                              "verdict.json (WO95 ledger models#495)",
                },
                {
                    "name": "he_der_corpus",
                    "value": 5.3075,
                    "protocol": "crown protocol (greedy, seq2seq_der, "
                                "1,864 rows / 4,094 windows, hebrew-v4 test)",
                    "source": "isx-training:/run-098-multi-vocalized/"
                              "verdict.json (WO95 ledger models#495)",
                },
            ],
        )

    base_meta = base_meta_for("he", "fp32")  # readme template only
    readme = (
        f"# {MODEL_ID}\n\nJoint cross-abjad vocalization model (WO95): one\n"
        "generative ByT5-base trained on Hebrew niqqud + Urdu haraqat gold,\n"
        "conditioned by language-prefix sentinels folded into the exported\n"
        "encoder graphs. This artifact materializes one language fold; the\n"
        "companion variant rides the same release under its own index key\n"
        "(the ara-diac-small-1.0-int8 variant convention). Consumers\n"
        "resolve by id; see the WO95 ledger (models#490/#495).\n")

    zips: dict[str, dict[str, Path]] = {}
    for lang, pid in PREFIX_IDS.items():
        vdir = WORK / f"enc-{lang}"
        vdir.mkdir(parents=True, exist_ok=True)
        enc = FoldedEncoder(model.get_encoder(), pid).eval()
        ids = torch.tensor([[104, 101]])  # shape probe only
        with torch.no_grad():
            torch.onnx.export(
                enc, (ids,), vdir / "encoder.onnx",
                input_names=["input_ids"], output_names=["last_hidden_state"],
                opset_version=14, dynamo=False,
                dynamic_axes={"input_ids": {0: "batch", 1: "seq"},
                              "last_hidden_state": {0: "batch", 1: "seq"}})
        del enc
        for precision in ("fp32", "int8"):
            pdir = WORK / f"{lang}-{precision}"
            pdir.mkdir(parents=True, exist_ok=True)
            shutil.copy(vdir / "encoder.onnx", pdir / "encoder.onnx")
            for name, src in dec_graphs.items():
                dst = pdir / name
                if precision == "fp32":
                    dst.write_bytes(src.read_bytes())
                else:
                    quantize_int8(src, dst,
                                  nodes_to_exclude=head_matmul_names(src))
            fname = (f"{MODEL_ID}-{precision}.zip" if lang == "he"
                     else f"{MODEL_ID}-ur-{precision}.zip")
            out_zip = OUT / fname
            pack_zip(pdir, base_meta_for(lang, precision), readme, out_zip)
            zips.setdefault(lang, {})[precision] = out_zip
            log(f"exported {lang}/{precision}: {fname} {out_zip.stat().st_size} B")

    # ---------------- folded torch reference (house math + the fold) ----------------
    from imf.export import BYTE_OFFSET, EOS_ID, PAD_ID, encode_bytes
    from imf.text_metrics import char_error_rate

    def _decode_tokens(tokens: list[int]) -> str:
        return bytes((t - BYTE_OFFSET) % 256 for t in tokens).decode(
            "utf-8", errors="replace")

    @torch.no_grad()
    def torch_greedy_folded(model, prefix_id: int, text: str, max_len: int) -> list[int]:
        """The house reference decoder math (imf.parity._torch_greedy_tokens)
        with the language fold applied — identical to training, where the
        tokenizer produced [sentinel] + bytes+3."""
        ids = torch.tensor([encode_bytes(text)], dtype=torch.long)
        if ids.shape[1] == 1:
            return []
        enc_mod = model.get_encoder()
        emb = enc_mod.embed_tokens(ids)
        p = enc_mod.embed_tokens(torch.full(
            (1, 1), int(prefix_id), dtype=torch.long, device=ids.device))
        enc = enc_mod(inputs_embeds=torch.cat([p, emb], dim=1))[0]
        dec_ids = torch.tensor([[PAD_ID]], dtype=torch.long)
        outs: list[int] = []
        for _ in range(max_len):
            hidden = model.get_decoder()(
                input_ids=dec_ids, encoder_hidden_states=enc)[0]
            logits = model.lm_head(hidden * (model.config.d_model ** -0.5))
            nxt = int(logits[0, -1].argmax())
            if nxt == EOS_ID:
                break
            outs.append(nxt)
            dec_ids = torch.cat([dec_ids, torch.tensor([[nxt]], dtype=torch.long)], 1)
        return outs

    def folded_reference_decode(model, prefix_id, sources, max_len, resume_path):
        done: dict[int, list[int]] = {}
        rp = Path(resume_path)
        if rp.exists():
            for line in rp.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    row = json.loads(line)
                    done[row["i"]] = row["tokens"]
        results: list[list[int]] = [[]] * len(sources)
        with rp.open("a", encoding="utf-8") as fh:
            for i, source in enumerate(sources):
                if i in done:
                    results[i] = done[i]
                    continue
                tokens = torch_greedy_folded(model, prefix_id, source, max_len)
                results[i] = tokens
                fh.write(json.dumps({"i": i, "tokens": tokens}) + "\n")
                if i % 25 == 0:
                    fh.flush()
                    log(f"  ref {i + 1}/{len(sources)}")
        return results

    # ---------------- parity + flips + informational per language ----------------
    from imf.export import onnx_greedy_kv
    from imf.parity import ParityReport, _sessions_from_zip, write_parity

    verdict: dict = {"run": RUN, "model_id": MODEL_ID, "repo_pin": head,
                     "maxlen": MAXLEN,
                     "gates": {"cer_delta_pp_max": 2.0,
                               "flip_rate_max": FLIP_GATE,
                               "min_samples": 500},
                     "languages": {}}
    vectors_rows: list[dict] = []
    golden_stats: dict[str, int] = {}
    all_pass = True
    int8_tokens: dict[str, list] = {}

    for lang, pairs in (("ur", urd_pairs), ("he", heb_pairs)):
        pid = PREFIX_IDS[lang]
        srcs = [s for s, _g in pairs]
        log(f"[{lang}] folded torch reference decode ({len(srcs)} rows)")
        refs = folded_reference_decode(model, pid, srcs, MAXLEN,
                                       WORK / f"ref-{lang}.jsonl")
        fp32_zip = zips[lang]["fp32"]
        int8_zip = zips[lang]["int8"]
        enc32, kv32 = _sessions_from_zip(fp32_zip)
        enc8, kv8 = _sessions_from_zip(int8_zip)

        cer_ref_sum = 0.0      # torch vs gold (house metric)
        cer_f32_sum = 0.0      # fp32 zip vs gold
        cer_i8_sum = 0.0       # int8 zip vs gold
        flips = 0
        sanity_flips = 0
        der32 = der8 = 0.0
        der_n = 0
        t8_all: list[list[int]] = []
        t32_all: list[list[int]] = []
        for i, (src, gold) in enumerate(pairs):
            ref = refs[i]
            t32 = onnx_greedy_kv(enc32, kv32, src, MAXLEN)
            t8 = onnx_greedy_kv(enc8, kv8, src, MAXLEN)
            t32_all.append(t32)
            t8_all.append(t8)
            o32 = _decode_tokens(t32)
            o8 = _decode_tokens(t8)
            if t8 != t32:
                flips += 1
            if t32 != ref:
                sanity_flips += 1
            cer_ref_sum += char_error_rate(_decode_tokens(ref), gold)
            cer_f32_sum += char_error_rate(o32, gold)
            cer_i8_sum += char_error_rate(o8, gold)
            if lang == "he" and len(src.encode("utf-8")) <= 512:
                d32, n = seq2seq_der(o32, gold)
                d8, _ = seq2seq_der(o8, gold)
                der32 += d32 * n
                der8 += d8 * n
                der_n += n
            if (i + 1) % 100 == 0:
                log(f"[{lang}] decode pass {i + 1}/{len(pairs)}")
        del enc32, kv32, enc8, kv8
        import gc
        gc.collect()

        n = len(pairs)
        cer_ref_pp = round(100.0 * cer_ref_sum / n, 4)
        cer_f32_pp = round(100.0 * cer_f32_sum / n, 4)
        cer_i8_pp = round(100.0 * cer_i8_sum / n, 4)
        delta_f32 = round(abs(cer_f32_pp - cer_ref_pp), 4)
        delta_i8 = round(abs(cer_i8_pp - cer_ref_pp), 4)
        flip_rate = round(flips / n, 6)
        gate_pass = delta_i8 <= 2.0 and flip_rate <= FLIP_GATE and n >= 500
        all_pass = all_pass and gate_pass
        int8_tokens[lang] = t8_all

        he_block = {}
        if lang == "he":
            he_block = {
                "informational_he_der_pct_fp32": round(der32 / max(1, der_n) * 100, 4),
                "informational_he_der_pct_int8": round(der8 / max(1, der_n) * 100, 4),
                "he_der_subslice_rows": der_n,
                "he_der_subslice_rule": "src <= 512 utf8 bytes (row-full DER on "
                                        "longer rows would measure truncation, "
                                        "not the model)",
            }
        verdict["languages"][lang] = {
            "slice_rows": n,
            "torch_reference_vs_gold_cer_pp": cer_ref_pp,
            "fp32_zip_vs_gold_cer_pp": cer_f32_pp,
            "int8_zip_vs_gold_cer_pp": cer_i8_pp,
            "fp32_parity_sanity_delta_pp": delta_f32,
            "int8_parity_cer_delta_pp": delta_i8,
            "int8_parity_gate_pass": delta_i8 <= 2.0 and n >= 500,
            "row_flips_int8_vs_fp32": flips,
            "row_flip_rate": flip_rate,
            "flip_gate_pass": flip_rate <= FLIP_GATE,
            "fp32onnx_vs_torch_sanity_flips": sanity_flips,
            "gate_pass": gate_pass,
            "informational_int8_row_mean_cer": round(cer_i8_sum / n, 5),
            **he_block,
        }
        log(f"[{lang}] GATE {'PASS' if gate_pass else 'FAIL'} "
            f"int8_delta={delta_i8}pp flips={flip_rate} sanity_flips={sanity_flips}")

        # write the house parity block into the SHIPPED int8 zip (strict gate)
        report = ParityReport(samples=n, cer_reference=cer_ref_pp,
                              cer_onnx=cer_i8_pp, cer_delta=delta_i8,
                              token_mismatches=sum(1 for a, b in zip(refs, t8_all) if a != b),
                              precision="int8")
        try:
            write_parity(int8_zip, report)
            log(f"[{lang}] parity block written + strict validation ok")
        except RuntimeError as e:
            log(f"[{lang}] write_parity FAILED: {e}")
            all_pass = False
            verdict["languages"][lang]["write_parity_error"] = str(e)

        # golden from the shipped int8 arm
        golden_path = OUT / "golden" / f"{MODEL_ID}-int8-{lang}.jsonl"
        with golden_path.open("w", encoding="utf-8") as fh:
            for (src, _g), t8 in zip(pairs, t8_all):
                fh.write(json.dumps({"input": src, "tokens": t8},
                                    ensure_ascii=False) + "\n")
        golden_stats[lang] = len(t8_all)

        # vectors rows from the shipped int8 arm
        for (src, _g), t8 in zip(pairs, t8_all):
            vectors_rows.append({"src": src, "out": _decode_tokens(t8),
                                 "lang": lang})

    # vectors file (the urd-vocalized-2.1 shape + lang tags)
    from imf.validator import validate_zip
    vectors = {
        "model": MODEL_ID,
        "decode": {"mode": "single-row-greedy",
                   "note": "language conditioning folded per exported "
                           "variant; urd rows decode under the "
                           f"{MODEL_ID}-ur key artifact"},
        "source_slice": {
            "files": [
                {"file": URD_SLICE, "sha256": urd_sha, "rows": len(urd_pairs),
                 "lang": "ur"},
                {"file": HEB_SLICE, "sha256": heb_sha, "rows": len(heb_pairs),
                 "lang": "he"},
            ],
        },
        "candidate": {},
        "vectors": vectors_rows,
    }
    cand: dict[str, dict] = {}
    for lang in ("he", "ur"):
        zp = zips[lang]["int8"]
        cand[lang if lang == "he" else "ur_key"] = {
            "zip_file": zp.name,
            "zip_sha256": sha256_file(zp),
        }
    vectors["candidate"] = cand
    vec_path = OUT / f"{MODEL_ID}-vectors.json"
    vec_path.write_text(json.dumps(vectors, indent=1, ensure_ascii=False),
                        encoding="utf-8")

    # strict-validate every shipped zip (the release gate)
    for lang in ("he", "ur"):
        r = validate_zip(zips[lang]["int8"])
        verdict["languages"][lang]["strict_zip_validation"] = bool(r.ok)
        if not r.ok:
            all_pass = False
            log(f"[{lang}] strict validation FAILED: {r.errors}")

    verdict["golden"] = golden_stats
    verdict["vectors_rows"] = len(vectors_rows)
    verdict["all_pass"] = all_pass
    verdict["seconds"] = round(time.time() - t0, 1)
    (OUT / "verdict.json").write_text(json.dumps(verdict, indent=1))
    log("VERDICT " + json.dumps({"all_pass": all_pass,
                                 "languages": {k: v["gate_pass"] for k, v in verdict["languages"].items()}}))

    # SHA256SUMS sidecar over everything shipped to the bucket
    sums = []
    for p in sorted(OUT.rglob("*")):
        if p.is_file() and p.name not in ("SHA256SUMS.txt", "EXPORT_DONE"):
            sums.append(f"{sha256_file(p)}  {p.relative_to(OUT)}")
    (OUT / "SHA256SUMS.txt").write_text("\n".join(sums) + "\n", encoding="utf-8")
    (OUT / "EXPORT_DONE").write_text("ok\n" if all_pass else "GATE FAIL\n")
    log(f"done in {verdict['seconds']}s; artifacts at {OUT}")


if __name__ == "__main__":
    main()
