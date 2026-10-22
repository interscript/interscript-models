"""WO81 — valid-reading-rate (VRR), the ambiguity-aware metric.

Undiacritized Arabic is an underspecified input: the skeleton is a
relation over readings, and one-gold DER penalizes every legitimate
alternative. VRR scores a prediction as valid when it matches ANY
dictionary-licensed reading of its skeleton. Reported alongside DER —
never instead of it.
"""

from __future__ import annotations

import re

# Arabic diacritics: tanwin + harakat + shadda/sukun marks (0610-061A),
# honorific/annotation marks (064B-065F), superscript alef (0670).
_HARAKAT = frozenset(
    chr(c) for c in list(range(0x0610, 0x061B)) + list(range(0x064B, 0x0660))
    + [0x0670]
)


def strip_harakat(text: str) -> str:
    """The skeleton: the text with all diacritics removed."""
    return "".join(ch for ch in text if ch not in _HARAKAT)


def build_lexicon(vocalized_forms) -> dict[str, set[str]]:
    """skeleton -> set of licensed fully-vocalized readings.

    A form with no diacritic is not a reading (it is its own skeleton)
    and is excluded — otherwise VRR degenerates to 1.0 for any
    undiacritized prediction.
    """
    lex: dict[str, set[str]] = {}
    for form in vocalized_forms:
        skeleton = strip_harakat(form)
        if form == skeleton:
            continue
        lex.setdefault(skeleton, set()).add(form)
    return lex


def score_predictions_vrr(preds: list[str],
                          licensed: list[set[str]]) -> dict:
    """VRR over rows: valid iff the exact prediction is licensed.

    A skeleton with no known readings can never validate — the row
    still counts in the denominator (absence of evidence is not
    validity).
    """
    if len(preds) != len(licensed):
        raise ValueError(
            f"preds and licensed lengths differ: {len(preds)} vs "
            f"{len(licensed)}")
    valid = sum(1 for p, ls in zip(preds, licensed, strict=False) if p in ls)
    return {
        "vrr": valid / len(preds) if preds else 0.0,
        "valid": valid,
        "total": len(preds),
        "convention": "row-level exact match against licensed readings; "
                      "readings built per build_lexicon (>=1 haraka)",
    }


_WORD_RE = re.compile(r"[؀-ۿ]+")


def score_text_vrr(src: str, pred: str, lexicon: dict[str, set[str]]) -> tuple[int, int]:
    """(valid_words, total_words) for one paragraph row.

    A word is valid iff its exact vocalized form is a licensed reading
    of that word's skeleton. Non-Arabic tokens count as invalid-missing
    evidence: they enter the denominator (the model must vocalize the
    Arabic content words; Latin/numeric tokens carry no readings).
    """
    src_words = _WORD_RE.findall(src)
    pred_words = _WORD_RE.findall(pred)
    if not src_words:
        return 0, 0
    valid = 0
    for sw, pw in zip(src_words, pred_words, strict=False):
        if pw in lexicon.get(strip_harakat(sw), ()):  # exact licensed reading
            valid += 1
    return valid, len(src_words)
