"""
Outfit pairing scores.

Given a base item, every other wardrobe item is scored on three signals:

  category  - does it complete the outfit? A top needs a bottom, not another top.
  colour    - neutrals go with anything; close hues and opposite hues look
              deliberate; hues roughly a quarter of the wheel apart tend to clash.
  style     - cosine similarity of the CNN embeddings, so pieces with a similar
              look (texture, pattern, formality) are preferred.

The weights below are the single place to tune the balance between them.
"""

import colorsys
import math

CATEGORIES = ("top", "bottom", "outerwear", "shoes", "accessory")

WEIGHTS = {"category": 0.5, "color": 0.35, "style": 0.15}

NEUTRAL_SATURATION = 0.15  # below this a colour reads as white/grey/beige
NEUTRAL_VALUE = 0.15       # very dark colours read as black whatever their hue


def _hsv(rgb):
    return colorsys.rgb_to_hsv(*(c / 255.0 for c in rgb))


def is_neutral(rgb) -> bool:
    _, s, v = _hsv(rgb)
    return s < NEUTRAL_SATURATION or v < NEUTRAL_VALUE


def color_harmony(rgb_a, rgb_b) -> float:
    """0..1 score for how well two colours sit together in an outfit."""
    if is_neutral(rgb_a) or is_neutral(rgb_b):
        return 0.9

    distance = abs(_hsv(rgb_a)[0] - _hsv(rgb_b)[0])
    distance = min(distance, 1.0 - distance)  # hue is circular; max distance is 0.5

    if distance <= 0.08:   # analogous: same colour family
        return 0.85
    if distance >= 0.42:   # complementary: opposite sides of the wheel
        return 0.75
    # In between, the worst case is a quarter of the wheel apart.
    return 0.2 + 0.4 * abs(distance - 0.25) / 0.17


def cosine_similarity(a, b) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm = math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))
    return dot / norm if norm else 0.0


def score_pair(base: dict, candidate: dict) -> dict:
    category_ok = candidate["category"] != base["category"]
    color = color_harmony(base["color"], candidate["color"])
    style = max(0.0, cosine_similarity(base["embedding"], candidate["embedding"]))

    total = (
        WEIGHTS["category"] * (1.0 if category_ok else 0.0)
        + WEIGHTS["color"] * color
        + WEIGHTS["style"] * style
    )
    return {
        "item_id": candidate["id"],
        "score": round(total, 4),
        "category_compatible": category_ok,
        "color_harmony": round(color, 4),
        "style_similarity": round(style, 4),
    }


def recommend(base: dict, wardrobe: list[dict], top_n: int = 5) -> list[dict]:
    """Rank the rest of the wardrobe as pairings for `base`, best first."""
    scored = [score_pair(base, item) for item in wardrobe if item["id"] != base["id"]]
    scored.sort(key=lambda s: s["score"], reverse=True)
    return scored[:top_n]
