"""WO79 — normalize fp16 IMF graphs to fp32 graph IO (weights stay fp16).

The fp16 export left last_hidden_state / encoder_hidden_states / logits
in float16. Python ORT transparently widens fp16->fp32 (the reference
path); every other runtime breaks. This tool wraps fp16 graph outputs
in Cast(to=FLOAT) and feeds fp32 decoder inputs through an internal
Cast(to=FLOAT16), so all graph IO is fp32 while the math stays the
reference math. Member digests in metadata.yaml are recomputed.

Usage: python tools/normalize_fp16_io.py model.zip   # in place
"""
from __future__ import annotations

import hashlib
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

import onnx
import yaml
from onnx import TensorProto, helper

IO_TYPES = {TensorProto.FLOAT: "fp32", TensorProto.FLOAT16: "fp16"}


def _dims(t) -> list:
    return [d.dim_value if d.HasField("dim_value") else d.dim_param
            for d in t.shape.dim]


def widen_outputs(model: onnx.ModelProto) -> bool:
    g = model.graph
    changed = False
    for out in list(g.output):
        t = out.type.tensor_type
        if t.elem_type != TensorProto.FLOAT16:
            continue
        orig = out.name
        raw = orig + "__raw"
        out.name = raw
        for n in g.node:
            for i, x in enumerate(n.output):
                if x == orig:
                    n.output[i] = raw
        g.output.append(helper.make_tensor_value_info(
            orig, TensorProto.FLOAT, _dims(t)))
        g.node.append(helper.make_node("Cast", [raw], [orig],
                                       to=TensorProto.FLOAT))
        # keep the raw fp16 tensor internal: the graph exposes exactly
        # one fp32 output per original output
        g.output.remove(out)
        changed = True
    return changed


def narrow_input(model: onnx.ModelProto, name: str) -> bool:
    """Declare `name` as fp32 IO; cast to fp16 for the internal ops."""
    g = model.graph
    inp = next((i for i in g.input if i.name == name), None)
    if inp is None or inp.type.tensor_type.elem_type != TensorProto.FLOAT16:
        return False
    internal = name + "__f16"
    inp.type.tensor_type.elem_type = TensorProto.FLOAT
    consumers = [n for n in g.node if name in n.input]
    for n in consumers:
        for i, x in enumerate(n.input):
            if x == name:
                n.input[i] = internal
    g.node.insert(0, helper.make_node("Cast", [name], [internal],
                                      to=TensorProto.FLOAT16))
    return True


def normalize_zip(path: Path) -> None:
    tmp = Path(tempfile.mkdtemp())
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        meta = yaml.safe_load(z.read("metadata.yaml"))
        graphs = {}
        for member, digest in list((meta.get("sha256") or {}).items()):
            model = onnx.load_model_from_string(z.read(member))
            touched = widen_outputs(model)
            touched |= narrow_input(model, "encoder_hidden_states")
            if touched:
                onnx.checker.check_model(model)
                graphs[member] = model.SerializeToString()
                print(f"{member}: IO normalized to fp32")
            else:
                print(f"{member}: already fp32 IO")
        members = {n: z.read(n) for n in names}

    for member, blob in graphs.items():
        members[member] = blob
        meta["sha256"][member] = hashlib.sha256(blob).hexdigest()

    buf = io_bytes(members, meta)
    digest = hashlib.sha256(buf).hexdigest()
    shutil.copyfile(path, path.with_suffix(".zip.bak"))
    path.write_bytes(buf)
    print(f"rewrote {path}: zip sha256 {digest} (prior digest backed up "
          f"as {path.with_suffix('.zip.bak').name})")


def io_bytes(members: dict, meta: dict) -> bytes:
    import io
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for name, blob in members.items():
            if name == "metadata.yaml":
                z.writestr(name, yaml.safe_dump(
                    meta, allow_unicode=True, sort_keys=False))
            else:
                z.writestr(name, blob)
    return buf.getvalue()


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        normalize_zip(Path(arg))
