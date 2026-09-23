"""Check Blink locality and Normal registration without a browser dependency."""

from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1] / "public/assets/hero"
base = Image.open(ROOT / "base/base-albedo.png").convert("RGB")
normal = Image.open(ROOT / "normal/base-normal-v1.png")
assert base.size == normal.size == (1672, 941)
assert normal.mode == "RGB"

composite = base.convert("RGBA")
allowed = np.zeros((base.height, base.width), dtype=bool)
for name, x, y in (("left-closed-v1.png", 1080, 177), ("right-closed-v1.png", 1152, 195)):
    eye = Image.open(ROOT / "blink" / name)
    assert eye.mode == "RGBA"
    allowed[y:y + eye.height, x:x + eye.width] = True
    composite.alpha_composite(eye, (x, y))

delta = np.asarray(composite.convert("RGB")).astype(np.int16) - np.asarray(base).astype(np.int16)
changed = np.any(delta != 0, axis=2)
assert np.count_nonzero(changed) > 0
assert np.count_nonzero(changed & ~allowed) == 0
print(f"Blink changed pixels: {np.count_nonzero(changed)}; outside eye rectangles: 0")
print(f"Normal: {normal.width}x{normal.height}, {normal.mode}, registered to Base source pixels")
