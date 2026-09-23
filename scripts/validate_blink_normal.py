"""Check Blink locality and Normal registration without a browser dependency."""

from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1] / "public/assets/hero"
base = Image.open(ROOT / "base/base-albedo.png").convert("RGB")
normal_v1 = Image.open(ROOT / "normal/base-normal-v1.png")
normal_v2 = Image.open(ROOT / "normal/base-normal-v2.png")
normal = Image.open(ROOT / "normal/base-normal-v3.png")
assert base.size == normal.size == (1672, 941)
assert normal.mode == "RGB"
assert normal_v1.size == normal.size and normal_v1.mode == "RGB"
assert normal_v2.size == normal.size and normal_v2.mode == "RGB"

# V3 is a local edit of v2. Accepted regions must remain byte-for-byte equal.
v2_pixels = np.asarray(normal_v2)
v3_pixels = np.asarray(normal)
normal_changed = np.any(v2_pixels != v3_pixels, axis=2)
protected = np.zeros((base.height, base.width), dtype=bool)
protected[170:310, 1070:1245] = True
protected[0:590, 520:870] = True
protected[650:835, 0:900] = True
protected[630:795, 1400:1672] = True
base_pixels = np.asarray(base)
yy, xx = np.mgrid[0:base.height, 0:base.width]
protected |= ((base_pixels[..., 2] > base_pixels[..., 0].astype(np.int16) + 7) &
              (base_pixels[..., 2] > base_pixels[..., 1].astype(np.int16) + 4) &
              (base_pixels[..., 1] > 120) & (yy < 235) & (xx > 840))
assert np.count_nonzero(normal_changed & protected) == 0
allowed = np.zeros_like(protected)
for x0, y0, x1, y1 in ((870, 215, 1480, 625), (840, 325, 1415, 855),
                       (845, 0, 1065, 370), (1270, 0, 1672, 660),
                       (0, 815, 980, 941), (1410, 780, 1672, 941)):
    allowed[y0:y1, x0:x1] = True
assert np.count_nonzero(normal_changed & ~allowed) == 0

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
print(f"Normal v1/v2/v3: {normal.width}x{normal.height}, {normal.mode}, registered to Base source pixels")
print(f"Normal v3 changed pixels: {np.count_nonzero(normal_changed)}; protected/outside local bounds: 0")
