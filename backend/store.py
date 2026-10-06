"""
Wardrobe storage: one JSON file plus the uploaded images on disk.

Enough for a single-user app. The rest of the backend only uses the four
functions below, so swapping in a database later touches nothing else.
"""

import json
import uuid
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
IMAGES_DIR = DATA_DIR / "images"
DB_PATH = DATA_DIR / "wardrobe.json"

IMAGES_DIR.mkdir(parents=True, exist_ok=True)


def list_items() -> list[dict]:
    if not DB_PATH.exists():
        return []
    return json.loads(DB_PATH.read_text(encoding="utf-8"))


def _save(items: list[dict]) -> None:
    DB_PATH.write_text(json.dumps(items), encoding="utf-8")


def add_item(category: str, color, embedding: list[float], image: bytes, suffix: str) -> dict:
    item_id = uuid.uuid4().hex
    filename = f"{item_id}{suffix}"
    (IMAGES_DIR / filename).write_bytes(image)

    item = {
        "id": item_id,
        "category": category,
        "color": list(color),
        "embedding": embedding,
        "image_url": f"/images/{filename}",
    }
    _save(list_items() + [item])
    return item


def delete_item(item_id: str) -> bool:
    items = list_items()
    kept = [item for item in items if item["id"] != item_id]
    if len(kept) == len(items):
        return False
    for item in items:
        if item["id"] == item_id:
            (IMAGES_DIR / Path(item["image_url"]).name).unlink(missing_ok=True)
    _save(kept)
    return True
