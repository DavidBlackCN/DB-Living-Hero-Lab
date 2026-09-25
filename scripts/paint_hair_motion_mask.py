"""Paint lower hair, head mass, and secondary hair weights in Artwork Space."""

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
SIZE = (1672, 941)
OUTPUT = ROOT / "public/assets/hero/motion/hair-motion-mask.png"

# Red: image-left lower hair. Green: image-right long hair. The fixed hat,
# rose, ribbon, face, clothing, and background lie outside these soft cores.
LOBES = (
    ([(1022, 312), (1053, 343), (1054, 399), (1026, 470),
      (994, 544), (942, 568), (907, 564), (918, 520),
      (947, 448), (992, 362)], 12),
    ([(1270, 276), (1290, 301), (1327, 341), (1384, 407),
      (1423, 488), (1441, 540), (1418, 568), (1372, 568),
      (1331, 518), (1292, 432), (1267, 350)], 12),
)

HEAD_OUTLINE = [
    (1048, 98), (1060, 65), (1090, 50), (1130, 40),
    (1195, 42), (1245, 57), (1270, 83), (1283, 120),
    (1280, 155), (1265, 173), (1276, 195), (1283, 218),
    (1302, 255), (1310, 315), (1300, 340), (1272, 335),
    (1240, 345), (1190, 328), (1150, 320), (1090, 335),
    (1045, 345), (1000, 340), (980, 325), (980, 290),
    (1010, 250), (1020, 200), (1020, 170), (1005, 155),
    (1010, 125), (1025, 105),
]

SECONDARY_STRANDS = (
    [(1085, 150), (1150, 139), (1215, 157), (1222, 186),
      (1185, 205), (1130, 210), (1080, 198)],
    [(1038, 175), (1064, 193), (1060, 242), (1084, 300),
      (1091, 352), (1050, 386), (1010, 366), (1013, 291)],
    [(1237, 165), (1265, 182), (1270, 220), (1249, 273),
      (1292, 326), (1312, 389), (1280, 405), (1250, 349),
      (1225, 300)],
)


def lobe(points: list[tuple[int, int]], feather: int) -> np.ndarray:
    image = Image.new("L", SIZE, 0)
    ImageDraw.Draw(image).polygon(points, fill=255)
    return np.asarray(image.filter(ImageFilter.GaussianBlur(feather)), dtype=np.float32) / 255


def main() -> None:
    yy = np.arange(SIZE[1], dtype=np.float32)[:, None]
    base = np.asarray(Image.open(ROOT / "public/assets/hero/base/base-albedo.png").convert("RGB"), dtype=np.float32)
    # Hand-painted lobes are the authority. This gentle material guard only
    # removes the white sleeves where they overlap a feathered lobe.
    sleeve_guard = np.clip((170 - base[:, :, 1]) / 35, 0, 1)
    left = lobe(*LOBES[0]) * np.clip((yy - 315) / 240, 0, 1) ** 1.5 * sleeve_guard
    right = lobe(*LOBES[1]) * np.clip((yy - 280) / 290, 0, 1) ** 1.35 * sleeve_guard
    head = lobe(HEAD_OUTLINE, 7)
    secondary = np.maximum.reduce([lobe(points, 8) for points in SECONDARY_STRANDS])
    # Keep Blink sprites and the ribbon rigid with the head. The pigment guard
    # removes facial skin and pale clothing inside the strand polygons.
    protected = Image.new("L", SIZE, 0)
    draw = ImageDraw.Draw(protected)
    draw.rectangle((1074, 172, 1178, 256), fill=255)
    draw.rectangle((1146, 189, 1250, 279), fill=255)
    draw.polygon([(1244, 219), (1298, 220), (1312, 316), (1272, 336)], fill=255)
    protected_weight = np.asarray(protected.filter(ImageFilter.GaussianBlur(6)), dtype=np.float32) / 255
    hair_pigment = np.clip((164 - base[:, :, 1]) / 34, 0, 1)
    secondary *= hair_pigment * (1 - protected_weight)
    channels = [np.uint8(np.rint(channel * 255)) for channel in (left, right, head, secondary)]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(np.dstack(channels), "RGBA").save(OUTPUT)


if __name__ == "__main__":
    main()
