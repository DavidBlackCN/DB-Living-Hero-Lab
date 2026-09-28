"""Generate fixed 1672x941 two-lamp source and corridor influence masks."""

import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


SIZE = (1672, 941)
OUT = Path(__file__).resolve().parents[1] / "public/assets/hero/lighting"


def source_channel(panes: list[list[tuple[int, int]]]) -> Image.Image:
    scale = 4
    image = Image.new("L", (SIZE[0] * scale, SIZE[1] * scale))
    pen = ImageDraw.Draw(image)
    for pane in panes:
        pen.polygon([(x * scale, y * scale) for x, y in pane], fill=255)
    return image.resize(SIZE, Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(0.45))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-only", action="store_true", help="Leave the frozen influence asset untouched")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    # Each lantern has three separate glass faces. The dark vertical mullions
    # and the roof/base remain outside the source mask.
    near = source_channel([
        [(35, 132), (39, 130), (39, 167), (36, 168)],  # left, narrow
        [(43, 129), (51, 129), (51, 168), (44, 168)],  # front
        [(56, 131), (65, 133), (64, 169), (56, 169)],  # right: reach the outer and lower glass edges
    ])
    far = source_channel([
        [(149, 249), (152, 248), (152, 273), (150, 273)],  # left: stay inside the metal rim
        [(153, 247), (160, 247), (160, 275), (153, 275)],  # front
        [(164, 248), (168, 249), (168, 274), (165, 275)],  # right
    ])
    zero = Image.new("L", SIZE)
    opaque = Image.new("L", SIZE, 255)
    Image.merge("RGBA", (near, far, zero, opaque)).save(OUT / "lamp-source-mask.png")

    if args.source_only:
        return

    y, x = np.ogrid[:SIZE[1], :SIZE[0]]
    influence = []
    for cx, cy, rx, ry, gain in ((52, 146, 151, 177, 1.0), (159, 262, 165, 180, 0.94)):
        radius2 = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
        field = gain * np.exp(-2.0 * radius2)
        # Corridors only: there is no influence in the open Sky or on the figure.
        field *= np.clip((390 - x) / 48, 0, 1)
        field *= np.clip((548 - y) / 60, 0, 1)
        influence.append(Image.fromarray(np.uint8(np.clip(field * 255, 0, 255)), "L"))
    Image.merge("RGBA", (*influence, zero, opaque)).save(OUT / "lamp-influence-mask.png")


if __name__ == "__main__":
    main()
