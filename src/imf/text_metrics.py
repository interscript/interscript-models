"""Character-level edit metrics for the IMF parity gate.

Inlined from the retired framework module (WO56 attic move): the gate
needs CER and nothing else. Same definitions, one dependency-free
home.
"""

from __future__ import annotations

from collections.abc import Sequence


def edit_distance(a: Sequence[object], b: Sequence[object]) -> int:
    """Levenshtein distance."""
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def char_error_rate(pred: str, gold: str) -> float:
    """CER = edit_distance / len(gold)."""
    if not gold:
        return 0.0 if not pred else 1.0
    return edit_distance(list(pred), list(gold)) / len(gold)
