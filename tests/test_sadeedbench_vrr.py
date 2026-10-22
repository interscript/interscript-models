"""WO81 — valid-reading-rate (VRR): a prediction counts when it matches
ANY dictionary-licensed reading of its skeleton. Single-gold DER
undercounts legitimate ambiguity; VRR is the ambiguity-aware complement.
"""

from __future__ import annotations

from sadeedbench.vrr import build_lexicon, score_predictions_vrr, strip_harakat

# skeleton of "بِكَتاب" (kitab, "with a book")
VOCALIZED = "بِكِتَاب"
SKELETON = "بكتاب"


def test_strip_harakat_removes_only_diacritics() -> None:
    assert strip_harakat(VOCALIZED) == SKELETON
    assert strip_harakat(SKELETON) == SKELETON
    # letters, spaces, punctuation survive
    assert strip_harakat("مَدرسة، جامعة") == "مدرسة، جامعة"


def test_build_lexicon_groups_by_skeleton_and_needs_a_reading() -> None:
    lex = build_lexicon([
        VOCALIZED,          # بِكِتَاب — licensed reading of بكتاب
        "بُكْتَاب",          # another licensed reading
        SKELETON,           # bare form — not a reading, excluded
        "مَدرسة",
    ])
    assert lex[SKELETON] == {VOCALIZED, "بُكْتَاب"}
    assert lex["مدرسة"] == {"مَدرسة"}
    assert SKELETON not in lex["مدرسة"]


def test_vrr_scores_any_licensed_reading() -> None:
    lex = build_lexicon([VOCALIZED, "بُكْتَاب"])
    rows = [
        (SKELETON, VOCALIZED),        # exact licensed reading -> valid
        (SKELETON, "بُكْتَاب"),          # alternative reading   -> valid
        (SKELETON, "بَكَاتِيب"),        # hallucinated          -> invalid
    ]
    preds = [p for _, p in rows]
    result = score_predictions_vrr(preds, [lex[_s] for _s, _ in rows])
    assert result["vrr"] == 2 / 3
    assert result["valid"] == 2
    assert result["total"] == 3


def test_vrr_with_empty_licensed_set_is_never_valid() -> None:
    result = score_predictions_vrr(["مَدرسة"], [set()])
    assert result["vrr"] == 0.0
    assert result["total"] == 1


def test_vrr_mismatched_lengths_raise() -> None:
    try:
        score_predictions_vrr(["x"], [set(), set()])
    except ValueError as e:
        assert "length" in str(e)
    else:
        raise AssertionError("expected ValueError")


def test_score_text_vrr_word_level() -> None:
    from sadeedbench.vrr import score_text_vrr

    lex = build_lexicon([VOCALIZED, "مَدرسة"])
    # two Arabic words: one licensed reading, one hallucination; a Latin
    # token in the source pairs with pred text but carries no readings
    v, t = score_text_vrr("بكتاب مدرسة x", f"{VOCALIZED} بَكَاتِيب yy", lex)
    assert (v, t) == (1, 2)
