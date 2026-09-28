"""Generate fixed 1672x941 two-lamp source and corridor influence masks."""

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
    OUT.mkdir(parents=True, exist_ok=True)
    near = source_channel([
        [(40, 121), (49, 123), (49, 163), (40, 160)],
        [(53, 123), (62, 121), (62, 160), (53, 163)],
    ])
    far = source_channel([
        [(151, 244), (157, 246), (157, 276), (151, 273)],
        [(161, 246), (167, 244), (167, 273), (161, 276)],
    ])
    zero = Image.new("L", SIZE)
    opaque = Image.new("L", SIZE, 255)
    Image.merge("RGBA", (near, far, zero, opaque)).save(OUT / "lamp-source-mask.png")

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
