"""
OutfitPicker API.

    POST   /wardrobe             add a clothing photo (form fields: category, image)
    GET    /wardrobe             list the wardrobe
    DELETE /wardrobe/{item_id}   remove an item
    GET    /recommend/{item_id}  best pairings for an item

Run with:  uvicorn main:app --port 8000
"""

import os
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import model
import store
from recommend import CATEGORIES, recommend

ALLOWED_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}
MAX_UPLOAD_BYTES = 10 * 1024 * 1024

app = FastAPI(title="OutfitPicker")
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/images", StaticFiles(directory=str(store.IMAGES_DIR)), name="images")


def _public(item: dict) -> dict:
    """An item without its 1280-number embedding, which the browser never needs."""
    return {key: value for key, value in item.items() if key != "embedding"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/wardrobe")
async def add_item(category: str = Form(...), image: UploadFile = File(...)):
    if category not in CATEGORIES:
        raise HTTPException(400, f"category must be one of {list(CATEGORIES)}")
    suffix = Path(image.filename or "").suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(400, f"image must be one of {sorted(ALLOWED_SUFFIXES)}")

    data = await image.read()
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "image is larger than 10 MB")
    try:
        picture = model.load_image(data)
    except Exception:
        raise HTTPException(400, "file is not a readable image")

    item = store.add_item(
        category=category,
        color=model.dominant_color(picture),
        embedding=model.embed(picture),
        image=data,
        suffix=suffix,
    )
    return _public(item)


@app.get("/wardrobe")
def list_wardrobe():
    return [_public(item) for item in store.list_items()]


@app.delete("/wardrobe/{item_id}")
def delete_item(item_id: str):
    if not store.delete_item(item_id):
        raise HTTPException(404, "item not found")
    return {"deleted": item_id}


@app.get("/recommend/{item_id}")
def recommend_for(item_id: str):
    wardrobe = store.list_items()
    by_id = {item["id"]: item for item in wardrobe}
    if item_id not in by_id:
        raise HTTPException(404, "item not found")
    return [
        {**result, "item": _public(by_id[result["item_id"]])}
        for result in recommend(by_id[item_id], wardrobe)
    ]
