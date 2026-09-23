"""Extract registered, feathered eye patches from the rejected full-frame v1.

Run from the repository root: python scripts/extract_blink_eyes.py
The full-frame candidate is only a source; the runtime loads the two RGBA patches.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "public/assets/hero/blink/blink-closed-eyes-v1.png"
OUTPUT = SOURCE.parent
ARTWORK_SIZE = (1672, 941)

# Pixel rectangles are half-open. Keep these in sync with src/config/hero.ts.
EYES = (
    ("left-closed-v1.png", (1080, 177, 1172, 250), (1094, 191, 1158, 236)),
    ("right-closed-v1.png", (1152, 195, 1244, 273), (1166, 211, 1230, 259)),
)


def main() -> None:
    source = Image.open(SOURCE).convert("RGB")
    if source.size != ARTWORK_SIZE:
        raise ValueError(f"Expected {ARTWORK_SIZE}, got {source.size}")
    for name, crop, ellipse in EYES:
        mask = Image.new("L", ARTWORK_SIZE, 0)
        ImageDraw.Draw(mask).ellipse(ellipse, fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(5))
        rgba = source.crop(crop).convert("RGBA")
        rgba.putalpha(mask.crop(crop))
        rgba.save(OUTPUT / name)
        print(f"{name}: {rgba.size}, artwork rect {crop}")


if __name__ == "__main__":
    main()
