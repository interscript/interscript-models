"""Generate an SPDX 3.0-style Model BOM for a shipped or gated-pending model.

Formalizes the org's recorded model provenance into a self-contained JSON
document (model = Package; training data = Dataset dependencies with their
sha256 pins; license + eval metric references carried on the model):

  models.yaml          artifact sha256/size/urls/parts, license, metrics,
                       parity, trained_from (the shipped-model registry)
  corpora/*.yaml       sha-pinned training corpora (sources + splits)
  bom/lineage.yaml     declarative model -> corpora linkage, training-chain
                       notes, and gated-pending model entries

The SPDX 3.0-style graph carries:
  - ``Package``      the model (checksums, license, release asset refs,
                     task/precision/kind, parity, eval metric references)
  - ``Dataset``      one per training corpus (sources, split sha256 pins)
  - ``Relationship`` ``dependsOn`` (model -> training data) and
                     ``descendantOf`` (model -> teacher/base model)
  - ``x-interscript`` extension blocks preserve the registry fields verbatim

Usage::

    python scripts/generate_model_bom.py --model heb-vocalized-plane-3.0
    python scripts/generate_model_bom.py --model urd-vocalized-2.0
    python scripts/generate_model_bom.py --all

Output: bom/<model>.spdx.json (+ <model>.spdx.json.sha256 sidecar, the
house sidecar pattern). Gated-pending models carry no artifact sha256/urls
by owner law (never pre-staged); their document records the recorded gate
verdict and lineage instead.

Exit code 0 on success, 2 on a bad model id, 3 on an inconsistent entry.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
MODELS_YAML = REPO / "models.yaml"
CORPORA_DIR = REPO / "corpora"
LINEAGE_YAML = REPO / "bom" / "lineage.yaml"
OUT_DIR = REPO / "bom"
NAMESPACE_BASE = "https://github.com/interscript/interscript-models/model-bom"


def load_yaml(path: Path):
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def spdx_id(kind: str, name: str) -> str:
    return f"SPDXRef-{kind}-{name}"


def build_model_package(
    model_id: str, model: dict, lineage_entry: dict, status: str
) -> dict:
    x = {
        "status": status,
        "registry": "models.yaml" if status == "shipped" else "bom/lineage.yaml (pending)",
        "task": model.get("task"),
        "scripts": model.get("scripts"),
    }
    for key in ("kind", "precision", "filename", "size"):
        if model.get(key) is not None:
            x[key] = model[key]
    if model.get("parity"):
        x["parity"] = model["parity"]
    if lineage_entry.get("source_refs"):
        x["sourceRefs"] = lineage_entry["source_refs"]
    if lineage_entry.get("lineage"):
        x["lineage"] = lineage_entry["lineage"]
    if model.get("metrics"):
        x["evaluations"] = [
            {
                "name": m["name"],
                "value": m["value"],
                **({"protocol": m["protocol"]} if m.get("protocol") else {}),
                "source": m.get("source"),
            }
            for m in model["metrics"]
        ]
    if model.get("parts"):
        x["releaseAssetParts"] = model["parts"]
    if model.get("trained_from"):
        x["trainedFrom"] = model["trained_from"]

    package = {
        "type": "Package",
        "spdxId": spdx_id("Model", model_id),
        "name": lineage_entry.get("ship_name", model_id),
        "versionInfo": str(lineage_entry.get("version", model_id.rsplit("-", 1)[-1])),
        "downloadLocation": model.get("url") or "NOASSERTION",
        "filesAnalyzed": False,
        "licenseConcluded": model.get("license") or lineage_entry.get("planned_license"),
        "licenseDeclared": model.get("license") or lineage_entry.get("planned_license"),
        "copyrightText": "NOASSERTION",
        "supplier": "Organization: Interscript (interscript.org)",
        "primaryPackagePurpose": "OTHER",
        "packageComment": "Machine-learning model weights (SPDX 3.0 AI profile domain).",
        "externalRefs": [
            {
                "referenceCategory": "PACKAGE-MANAGER",
                "referenceType": "purl",
                "referenceLocator": f"pkg:interscript/model/{model_id}"
                + (f"@{lineage_entry['version']}" if lineage_entry.get("version") else ""),
            }
        ],
        "x-interscript": x,
    }
    if model.get("sha256"):
        package["checksums"] = [{"algorithm": "SHA256", "checksumValue": model["sha256"]}]
    if model.get("license_note"):
        x["licenseNote"] = model["license_note"]
    return package


def build_corpus_dataset(corpus_id: str, corpus: dict) -> dict:
    dataset = {
        "type": "Dataset",
        "spdxId": spdx_id("Corpus", corpus_id),
        "name": corpus.get("id", corpus_id),
        "datasetComment": "Training corpus (SPDX 3.0 Dataset profile).",
        "licenseConcluded": corpus.get("license", "NOASSERTION"),
        "x-interscript-corpus": {
            "registry": f"corpora/{corpus_id}.yaml",
            "task": corpus.get("task"),
            "sources": corpus.get("sources", []),
            "splits": corpus.get("splits", {}),
        },
    }
    split_checksums = [
        {"algorithm": "SHA256", "checksumValue": split["sha256"]}
        for split in (corpus.get("splits") or {}).values()
        if split.get("sha256")
    ]
    if split_checksums:
        dataset["checksums"] = split_checksums
    return dataset


def build_document(model_id: str, graph: list, created: str, status: str) -> dict:
    namespace = f"{NAMESPACE_BASE}/{model_id}@{created}"
    return {
        "spdxVersion": "SPDX-3.0",
        "dataLicense": "CC0-1.0",
        "SPDXID": "SPDXRef-DOCUMENT",
        "documentNamespace": namespace,
        "name": f"model-bom-{model_id}",
        "comment": (
            "SPDX 3.0-style Model BOM generated by "
            "interscript-models/scripts/generate_model_bom.py from models.yaml, "
            "corpora/*.yaml and bom/lineage.yaml. Model = Package; sha-pinned "
            "training corpora = Dataset dependencies; lineage = relationships."
        ),
        "creationInfo": {
            "created": created,
            "creators": [
                "Organization: Interscript (interscript.org)",
                "Tool: interscript-models/scripts/generate_model_bom.py",
            ],
        },
        "x-interscript-status": status,
        "@graph": graph,
    }


def generate(model_id: str, models: dict, corpora: dict, lineage: dict, created: str) -> dict:
    entry = lineage.get(model_id)
    if entry is None:
        raise KeyError(model_id)

    pending = entry.get("status") == "gated-pending"
    model = entry if pending else models.get(model_id)
    if model is None:
        raise KeyError(model_id)
    if pending:
        # Owner law: never pre-stage artifact data for gated-pending models.
        assert not model.get("sha256") and not model.get("url"), (
            f"{model_id}: gated-pending entries must not pre-stage artifact data"
        )

    graph: list = []
    graph.append(build_model_package(model_id, model, entry, entry.get("status", "shipped")))

    corpus_ids = entry.get("corpora", [])
    for cid in corpus_ids:
        if cid not in corpora:
            raise KeyError(f"corpora/{cid}.yaml")
        graph.append(build_corpus_dataset(cid, corpora[cid]))

    rel_n = 0
    if corpus_ids:
        rel_n += 1
        graph.append(
            {
                "type": "Relationship",
                "spdxId": f"SPDXRef-Relationship-{rel_n:02d}",
                "relationshipType": "dependsOn",
                "from": spdx_id("Model", model_id),
                "to": [spdx_id("Corpus", cid) for cid in corpus_ids],
                "comment": "Training data (sha-pinned splits under each Dataset).",
            }
        )
    teachers = [lid for lid in entry.get("descends_from", []) if lid in models]
    if teachers:
        rel_n += 1
        graph.append(
            {
                "type": "Relationship",
                "spdxId": f"SPDXRef-Relationship-{rel_n:02d}",
                "relationshipType": "descendantOf",
                "from": spdx_id("Model", model_id),
                "to": [spdx_id("Model", t) for t in teachers],
                "comment": "trained_from chain (models.yaml lineage).",
            }
        )
    if pending and entry.get("gate"):
        graph.append(
            {
                "type": "Annotation",
                "spdxId": f"SPDXRef-Annotation-Gate-{model_id}",
                "annotationType": "OTHER",
                "subject": spdx_id("Model", model_id),
                "comment": {
                    "gate": entry["gate"].get("name"),
                    "verdict": entry["gate"].get("verdict"),
                    "date": entry["gate"].get("date"),
                    "detail": entry["gate"].get("detail"),
                    "records": entry["gate"].get("records"),
                    "shipRunbookExecuted": entry["gate"].get("ship_runbook_executed"),
                },
            }
        )
    return build_document(model_id, graph, created, entry.get("status", "shipped"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--model", action="append", help="model id (repeatable)")
    parser.add_argument("--all", action="store_true", help="generate for every lineage.yaml entry")
    parser.add_argument(
        "--out-dir", type=Path, default=OUT_DIR, help="output directory (default bom/)"
    )
    args = parser.parse_args(argv)

    models = load_yaml(MODELS_YAML).get("models", {})
    corpora = {
        p.stem: load_yaml(p)
        for p in sorted(CORPORA_DIR.glob("*.yaml"))
    }
    lineage = load_yaml(LINEAGE_YAML)

    targets = sorted(lineage.keys()) if args.all else (args.model or [])
    if not targets:
        parser.error("no models requested: pass --model <id> (repeatable) or --all")

    created = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    out_dir: Path = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    failures = 0
    for model_id in targets:
        try:
            doc = generate(model_id, models, corpora, lineage, created)
        except KeyError as exc:
            print(f"FAIL {model_id}: unknown id or missing source: {exc}", file=sys.stderr)
            failures += 1
            continue
        out_path = out_dir / f"{model_id}.spdx.json"
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        sidecar = out_path.parent / (out_path.name + ".sha256")
        with open(sidecar, "w", encoding="utf-8") as fh:
            fh.write(f"{sha256_file(out_path)}  {out_path.name}\n")
        status = doc["x-interscript-status"]
        print(f"OK {model_id} [{status}] -> {out_path} (+ {sidecar.name})")

    return 3 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
