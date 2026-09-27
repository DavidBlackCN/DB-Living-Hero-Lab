"""Rasterize registered, hand-placed Night seam repairs in Artwork Space.

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
# These are fixed scene features: pale distant foliage next to Night sky, the
# left vine corridor, and the small background opening beside the ribbon.
# Sky alpha protects the openings; the repair never paints across the sky.
PATCHES = [
    ([(841, 0), (929, 0), (932, 108), (925, 204),
      (949, 299), (911, 350), (858, 331), (850, 159)], 148, 15),
    ([(1299, 228), (1360, 219), (1373, 309), (1330, 347),
      (1302, 314)], 137, 14),
    ([(1420, 0), (1672, 0), (1672, 101), (1630, 91),
      (1592, 66), (1539, 46), (1482, 27)], 112, 13),
    ([(1542, 0), (1672, 0), (1672, 140), (1640, 139),
      (1600, 132), (1572, 99)], 112, 12),
    ([(1479, 145), (1505, 152), (1521, 147), (1548, 160),
      (1569, 153), (1591, 168), (1625, 157), (1672, 155),
      (1672, 277), (1604, 254), (1540, 234), (1480, 221)], 168, 13),
    ([(1372, 180), (1437, 168), (1493, 178), (1517, 199),
      (1510, 240), (1380, 242)], 145, 12),
    ([(1392, 186), (1442, 170), (1485, 183), (1510, 197),
      (1508, 219), (1393, 222)], 194, 11),
    ([(1545, 166), (1588, 153), (1627, 162), (1672, 156),
      (1672, 210), (1611, 198), (1547, 201)], 194, 11),
    ([(1512, 116), (1538, 116), (1550, 211), (1505, 211)], 78, 7),
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
    # RGB is the per-channel absorption for a cool Night material response.
    # Red falls furthest, then green; retaining blue preserves leaf and masonry
    # detail without a hard black silhouette or a bright warm edge.
    absorption = [np.full_like(opacity, channel) for channel in (255, 204, 163)]
    rgba = np.dstack(absorption + [opacity])
    Image.fromarray(rgba, "RGBA").save(SKY / "sky-edge-tone.png")


if __name__ == "__main__":
    main()
