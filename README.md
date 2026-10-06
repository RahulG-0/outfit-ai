# OutfitPicker

Upload photos of your clothes, pick one, and get ranked suggestions for what to wear with it.

## How it works

1. **Add an item.** You upload a photo and choose its category (top, bottom, outerwear, shoes or accessory).
2. **The backend analyses it.**
   - A MobileNetV2 network pretrained on ImageNet turns the photo into a 1280-number embedding that captures texture, pattern and shape. The network is used as a fixed feature extractor; nothing is trained here.
   - The dominant colour is taken from the centre of the photo, so a plain background doesn't win.
3. **Pick an item** and every other item is scored against it:

| Signal | Weight | Rule |
|---|---|---|
| Category | 0.50 | The pairing must complete the outfit: a top needs a bottom, not another top. |
| Colour harmony | 0.35 | Neutrals go with anything. Close hues and opposite hues score well. Hues a quarter of the colour wheel apart score worst. |
| Style similarity | 0.15 | Cosine similarity between the two embeddings. |

The weights live in one place, `backend/recommend.py`.

## Project layout

```
app/                    Next.js front end
  page.tsx              wardrobe page
  components/           upload form, wardrobe grid, pairings
  lib/api.ts            typed client for the backend
backend/                FastAPI service
  main.py               routes
  model.py              embedding and dominant colour
  recommend.py          pairing scores
  store.py              JSON and image storage
  test_recommend.py     tests for the scoring
```

## Run it

Backend (Python 3.10 to 3.12):

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --port 8000
```

The first upload downloads the MobileNetV2 weights (about 14 MB).

Front end:

```bash
npm install
cp .env.local.example .env.local
npm run dev
```

Then open http://localhost:3000.

## API

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/wardrobe` | Add an item (form fields `category` and `image`) |
| `GET` | `/wardrobe` | List items |
| `DELETE` | `/wardrobe/{id}` | Remove an item |
| `GET` | `/recommend/{id}` | Ranked pairings for an item, with the score breakdown |

## Tests

```bash
cd backend
python test_recommend.py
```

The scoring tests use hand-written embeddings, so they run without TensorFlow.

## Limitations

- The category is chosen by the user, not predicted from the photo.
- The scoring weights are set by hand; they have not been fitted to labelled outfits.
- Storage is a single JSON file, which suits one user on one machine.

## Stack

Next.js, TypeScript, Tailwind CSS, Python, FastAPI, TensorFlow/Keras (MobileNetV2), NumPy, Pillow.
