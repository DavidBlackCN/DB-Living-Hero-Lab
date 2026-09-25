"""Rasterize the hand-placed R3.2c edge correction in Artwork Space.

This is an authored foreground material, not a new sky segmentation pass.
Edit the polygons to retouch the fixed composition. The existing sky matte
protects open sky; no source-color test is involved.
"""

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
SKY = ROOT / "public/assets/hero/sky"
SIZE = (1672, 941)

# Artwork-space polygons, maximum correction opacity, and source-pixel feather.
# The strongest patch follows the pale distant canopy and roof below the
# right spires. The lighter patches keep leaf and spire detail intact.
PATCHES = [
    ([(1542, 0), (1672, 0), (1672, 140), (1640, 139),
      (1600, 132), (1572, 99)], 42, 11),
    ([(1479, 145), (1505, 152), (1521, 147), (1548, 160),
      (1569, 153), (1591, 168), (1625, 157), (1672, 155),
      (1672, 277), (1604, 254), (1540, 234), (1480, 221)], 96, 9),
    ([(1372, 180), (1437, 168), (1493, 178), (1517, 199),
      (1510, 240), (1380, 242)], 65, 10),
    ([(1512, 116), (1538, 116), (1550, 211), (1505, 211)], 31, 5),
]


def main() -> None:
    sky_alpha = np.asarray(Image.open(SKY / "sky-mask.png").convert("L"), dtype=np.float32) / 255
    if sky_alpha.shape != (SIZE[1], SIZE[0]):
        raise ValueError("Sky matte does not match Artwork Space")
    paint = np.zeros_like(sky_alpha)
    for polygon, opacity, feather in PATCHES:
        patch = Image.new("L", SIZE, 0)
        ImageDraw.Draw(patch).polygon(polygon, fill=opacity)
        paint = np.maximum(paint, np.asarray(patch.filter(ImageFilter.GaussianBlur(feather)), dtype=np.float32))
    opacity = np.uint8(np.rint(paint * (1 - sky_alpha)))
    rgba = np.dstack([np.full_like(opacity, 255)] * 3 + [opacity])
    Image.fromarray(rgba, "RGBA").save(SKY / "sky-edge-tone.png")


if __name__ == "__main__":
    main()
