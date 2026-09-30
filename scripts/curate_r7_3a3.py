"""Export compact fixed-frame review images from the pass-isolation captures."""

from pathlib import Path

from PIL import Image


ROOT = Path("docs/validation/r7-3a-3-final-visual")
OUT = ROOT / "review"
OUT.mkdir(parents=True, exist_ok=True)

SOURCES = {
    "night-before.jpg": "before/22h00-final.png",
    "night-after.jpg": "after/22h00-final.png",
    "night-bloom-off.jpg": "after/22h00-bloom-off.png",
    "night-sheen-off.jpg": "hair-sheen-off/22h00-final.png",
    "night-sky-repair-off.jpg": "sky-repair-off/22h00-final.png",
    "night-moon-response-off.jpg": "after/22h00-directional-off.png",
    "blink-4k-open.jpg": "blink/blink-4k-open.png",
    "blink-4k-closed.jpg": "blink/blink-4k-closed.png",
}

for output, source in SOURCES.items():
    with Image.open(ROOT / source) as image:
        image.convert("RGB").save(OUT / output, quality=88, optimize=True)

for output, source in {
    "night-head-before-after.jpg": "night-before-after-head.png",
    "night-motion-head-before-after.jpg": "night-motion-before-after-head.png",
    "night-pass-audit.jpg": "night-repair-sheen-audit.jpg",
}.items():
    with Image.open(ROOT / source) as image:
        image.convert("RGB").save(OUT / output, quality=90, optimize=True)

print(f"Exported {len(SOURCES) + 3} review images to {OUT}")
