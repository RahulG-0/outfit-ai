"""
Image features for wardrobe items.

A MobileNetV2 network pretrained on ImageNet is used as a fixed feature
extractor: with the classification head removed and global average pooling,
it turns a photo into a 1280-number embedding that captures texture, pattern
and shape. Nothing is trained here.
"""

from functools import lru_cache
from io import BytesIO

import numpy as np
from PIL import Image

IMAGE_SIZE = (224, 224)


@lru_cache(maxsize=1)
def _network():
    # Imported lazily: TensorFlow takes seconds to load, and the API should
    # start and serve the wardrobe list without paying for it.
    from tensorflow.keras.applications import MobileNetV2

    return MobileNetV2(weights="imagenet", include_top=False, pooling="avg")


def load_image(data: bytes) -> Image.Image:
    return Image.open(BytesIO(data)).convert("RGB")


def embed(image: Image.Image) -> list[float]:
    from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

    pixels = np.asarray(image.resize(IMAGE_SIZE), dtype=np.float32)
    batch = preprocess_input(pixels)[np.newaxis, ...]
    return _network().predict(batch, verbose=0)[0].tolist()


def dominant_color(image: Image.Image) -> tuple[int, int, int]:
    """
    Most common colour in the middle of the photo.

    The centre 60% is used so a plain background around the garment doesn't
    win. Pixels are grouped into coarse colour bins, and the mean of the
    fullest bin is returned.
    """
    w, h = image.size
    box = (int(w * 0.2), int(h * 0.2), int(w * 0.8), int(h * 0.8))
    pixels = np.asarray(image.crop(box).resize((64, 64)), dtype=np.int32).reshape(-1, 3)

    bins = (pixels // 32).astype(np.int32)                 # 8 levels per channel
    keys = bins[:, 0] * 64 + bins[:, 1] * 8 + bins[:, 2]
    fullest = np.bincount(keys, minlength=512).argmax()
    mean = pixels[keys == fullest].mean(axis=0)
    return tuple(int(round(c)) for c in mean)
