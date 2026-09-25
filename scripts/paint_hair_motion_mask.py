"""Paint the two deliberately bounded hair-motion lobes in Artwork Space."""

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
    channels = [np.uint8(np.rint(channel * 255)) for channel in (left, right)]
    channels += [np.zeros_like(channels[0]), np.full_like(channels[0], 255)]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(np.dstack(channels), "RGBA").save(OUTPUT)


if __name__ == "__main__":
    main()
