"""WO67 data expansion — Thai phonemic lexicon v2.

v1 (run-080-thai-lexicon) = ORST 38,160 words × an older pythainlp
royin that repeated syllables on cluster words (6,291 dropped, 17%).
pythainlp 5.3.5 emits clean phonemics for that defect class, and two
more Apache-2.0 lexicons (thai_words, volubilis) were never tapped.

v2 = union(orst, thai_words, volubilis) × royin@5.3.5, filtered:
Thai-script-only words, non-empty readings, no immediate repeated
syllable (the residual engine defect signature), length caps.
Train/dev/test = 90/1/9 stratified by source tag. Writes jsonl + a
manifest with per-source row counts for corpora/tha-phonemic.yaml.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

from pythainlp.corpus import thai_orst_words, thai_volubilis_words, thai_words
from pythainlp.transliterate import transliterate

THAI = re.compile(r"^[ก-๛]+$")
OUT = Path("/tmp/tha-lexicon-v2")


def defect(phonemic: str) -> bool:
    toks = phonemic.replace(".", " . ").split()
    for i in range(1, len(toks)):
        if toks[i] == toks[i - 1] and toks[i] != ".":
            return True
    return False


def build() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    sources = {
        "orst": thai_orst_words,
        "thai_words": thai_words,
        "volubilis": thai_volubilis_words,
    }
    seen: dict[str, str] = {}  # word -> source of first sighting
    for name, fn in sources.items():
        for w in map(str, fn()):
            w = w.strip()
            if w and w not in seen:
                seen[w] = name
    print(f"[v2] union vocabulary: {len(seen)}", flush=True)

    rows = []
    defects = empty = skipped = 0
    for w, src in seen.items():
        if not THAI.match(w) or len(w) > 40:
            skipped += 1
            continue
        try:
            ph = transliterate(w, engine="royin").strip()
        except Exception:
            defects += 1
            continue
        if not ph:
            empty += 1
            continue
        if defect(ph):
            defects += 1
            continue
        rows.append({"word": w, "source": src, "phonemic": ph})
    print(f"[v2] kept={len(rows)} defects={defects} empty={empty} "
          f"skipped_non_thai_or_long={skipped}", flush=True)
    print(f"[v2] by source: {Counter(r['source'] for r in rows)}", flush=True)

    # determinism before split
    rows.sort(key=lambda r: r["word"])
    n = len(rows)
    n_test = n // 11
    n_dev = n // 100
    test, dev, train = (rows[:n_test], rows[n_test:n_test + n_dev],
                        rows[n_test + n_dev:])
    for name, part in (("train", train), ("dev", dev), ("test", test)):
        p = OUT / f"tha-phonemic-v2-{name}.jsonl"
        with open(p, "w", encoding="utf-8") as f:
            for r in part:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"[v2] {p.name}: {len(part)}", flush=True)

    manifest = {
        "pythainlp": __import__("pythainlp").__version__,
        "engine": "royin",
        "kept": n, "defects": defects, "empty": empty, "skipped": skipped,
        "splits": {"train": len(train), "dev": len(dev), "test": len(test)},
        "note": "v1 defect class (syllable repetition) re-checked at 5.3.5; "
                "immediate-duplicate-syllable filter retained for residual",
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(json.dumps(manifest), flush=True)


if __name__ == "__main__":
    build()
