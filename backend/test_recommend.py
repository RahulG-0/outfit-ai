"""Tests for the pairing scores. No TensorFlow needed: embeddings are hand-written."""

from recommend import color_harmony, cosine_similarity, is_neutral, recommend, score_pair

NAVY = (30, 40, 120)
RED = (200, 30, 30)
ORANGE = (230, 120, 20)
GREEN = (40, 180, 60)
WHITE = (250, 250, 250)
BLACK = (10, 10, 10)


def item(item_id, category, color, embedding=(1.0, 0.0)):
    return {"id": item_id, "category": category, "color": color, "embedding": list(embedding)}


def test_neutrals():
    assert is_neutral(WHITE) and is_neutral(BLACK)
    assert not is_neutral(RED)


def test_neutral_goes_with_anything():
    assert color_harmony(WHITE, RED) == 0.9
    assert color_harmony(BLACK, GREEN) == 0.9


def test_same_family_beats_clashing_hues():
    assert color_harmony(RED, ORANGE) > color_harmony(RED, GREEN)


def test_harmony_is_symmetric_and_bounded():
    for a in (NAVY, RED, ORANGE, GREEN, WHITE):
        for b in (NAVY, RED, ORANGE, GREEN, BLACK):
            assert color_harmony(a, b) == color_harmony(b, a)
            assert 0.0 <= color_harmony(a, b) <= 1.0


def test_cosine_similarity():
    assert abs(cosine_similarity([1, 0], [1, 0]) - 1.0) < 1e-9
    assert abs(cosine_similarity([1, 0], [0, 1])) < 1e-9
    assert cosine_similarity([0, 0], [1, 1]) == 0.0


def test_same_category_scores_lower():
    top = item("a", "top", NAVY)
    other_top = item("b", "top", WHITE)
    bottom = item("c", "bottom", WHITE)
    assert score_pair(top, bottom)["score"] > score_pair(top, other_top)["score"]
    assert not score_pair(top, other_top)["category_compatible"]


def test_recommend_ranks_and_excludes_the_base_item():
    base = item("base", "top", NAVY)
    wardrobe = [
        base,
        item("clash", "bottom", ORANGE, (0.0, 1.0)),
        item("good", "bottom", WHITE, (1.0, 0.0)),
        item("same", "top", WHITE, (1.0, 0.0)),
    ]
    ranked = recommend(base, wardrobe)
    assert [r["item_id"] for r in ranked] == ["good", "clash", "same"]


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok  ", name)
