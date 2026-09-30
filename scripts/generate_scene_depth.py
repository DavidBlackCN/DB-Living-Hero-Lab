"""Registered, conservative background depth for R7.3B. No color thresholding."""

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SIZE = (1672, 941)
ROOT = Path(__file__).resolve().parents[1]


def polygon(points, value=255, feather=12):
    image = Image.new("L", SIZE)
    ImageDraw.Draw(image).polygon(points, fill=value)
    return np.asarray(image.filter(ImageFilter.GaussianBlur(feather)), dtype=np.float32) / 255


# Background plate: distant school, tower behind the hat, and distant trees.
# Sky is excluded by its actual runtime alpha, not by this broad depth plate.
far = polygon([(910, 0), (1672, 0), (1672, 630), (1450, 650),
               (1330, 640), (860, 620), (870, 345), (920, 290)], feather=18)
# Protect the complete character envelope, including moving hair tips. This is
# deliberately conservative; it is not a character lighting/material mask.
figure = polygon([(1030, 25), (1160, 15), (1270, 60), (1302, 135),
                  (1302, 225), (1350, 270), (1380, 353), (1414, 418),
                  (1444, 488), (1446, 570), (1426, 649), (1450, 941),
                  (950, 941), (950, 718), (755, 713), (739, 668),
                  (843, 622), (862, 562), (864, 495), (874, 419),
                  (930, 345), (972, 268), (1008, 200), (1007, 130),
                  (1022, 86)], feather=6)
# Column/vine nearest the camera and the foreground frame of the artwork.
near_column = polygon([(0, 0), (909, 0), (920, 170), (905, 310),
                       (877, 435), (889, 570), (895, 650), (0, 650)], feather=8)
right_vines = polygon([(1555, 0), (1672, 0), (1672, 941), (1608, 941),
                       (1627, 520), (1590, 390), (1600, 265), (1580, 150)], feather=14)
top_leaves = polygon([(1050, 0), (1410, 0), (1390, 65), (1305, 88),
                      (1180, 72), (1060, 60)], feather=9)
# A small, lower-opacity recess in the deep corridor. Nearby lamp pools and
# masonry stay outside it; it fades before reaching the foreground balustrade.
corridor = polygon([(18, 278), (93, 230), (137, 270), (167, 408),
                    (189, 523), (220, 617), (206, 676), (12, 685)], value=96, feather=16)
depth = far * (1 - figure) * (1 - near_column) * (1 - right_vines) * (1 - top_leaves)
depth = np.maximum(depth, corridor)
# No aerial veil is allowed on the foreground rail, hands, cup or lower scene.
y = np.arange(SIZE[1])[:, None]
depth *= np.clip((700 - y) / 65, 0, 1)
out = ROOT / "public/assets/hero/atmosphere/scene-depth.png"
out.parent.mkdir(parents=True, exist_ok=True)
Image.fromarray(np.round(depth * 255).astype(np.uint8)).save(out)
print(f"{out}: {SIZE}, fixed background-only depth")
