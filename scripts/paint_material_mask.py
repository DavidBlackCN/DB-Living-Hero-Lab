"""Paint registered R5 face, crown-hair, and iris material weights."""

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
SIZE = (1672, 941)
OUTPUT = ROOT / "public/assets/hero/material/material-mask.png"


def polygon(points: list[tuple[int, int]], feather: float) -> np.ndarray:
    image = Image.new("L", SIZE, 0)
    ImageDraw.Draw(image).polygon(points, fill=255)
    return np.asarray(image.filter(ImageFilter.GaussianBlur(feather)), dtype=np.float32) / 255


def ellipse(box: tuple[int, int, int, int], feather: float) -> np.ndarray:
    image = Image.new("L", SIZE, 0)
    ImageDraw.Draw(image).ellipse(box, fill=255)
    return np.asarray(image.filter(ImageFilter.GaussianBlur(feather)), dtype=np.float32) / 255


def ramp(value: np.ndarray, low: float, high: float) -> np.ndarray:
    t = np.clip((value - low) / (high - low), 0, 1)
    return t * t * (3 - 2 * t)


def main() -> None:
    base = np.asarray(Image.open(ROOT / "public/assets/hero/base/base-albedo.png").convert("RGB"), dtype=np.float32)
    red, green, blue = (base[:, :, index] for index in range(3))

    # The jaw/cheek polygon follows this fixed painting, including the small
    # exposed forehead and ear. The narrow feather stays off hair and collar.
    face = polygon([
        (1083, 196), (1091, 184), (1110, 174), (1130, 187),
        (1161, 185), (1180, 194), (1204, 202), (1219, 219),
        (1222, 248), (1212, 265), (1191, 280), (1150, 293),
        (1129, 287), (1109, 272), (1091, 250), (1082, 224),
    ], 2.5)
    face = np.maximum(face, ellipse((1075, 194, 1095, 235), 2.0) * 0.8)
    yy = np.arange(SIZE[1], dtype=np.float32)[:, None]
    # Bangs share the warm hue, so the upper face requires a much lighter
    # pigment than the lower cheek and jaw shadows.
    upper = 1 - ramp(yy, 220, 242)
    brightness_floor = 90 + 65 * upper
    skin_pigment = ramp(red - green, 18, 29) * ramp(green - blue, 3, 9)
    skin_pigment *= ramp(green - brightness_floor, 0, 28)
    face *= skin_pigment

    # Crown only: excludes the white beret, dark rose, ribbon, face and lower
    # falls. The shader draws the curved ribbon inside this material region.
    crown = polygon([
        (1080, 154), (1100, 119), (1134, 97), (1180, 92),
        (1215, 105), (1244, 139), (1263, 182), (1254, 204),
        (1220, 197), (1192, 187), (1163, 174), (1125, 178),
        (1097, 189), (1076, 181),
    ], 3.0)
    hair_pigment = ramp(red - green, 19, 29) * ramp(green - blue, 4, 10)
    hair_pigment *= 1 - ramp(green, 166, 197)
    hair_pigment *= ramp(green, 48, 74)
    crown *= hair_pigment

    # Soft support inside the painted brown irises. Exact glints are smaller
    # procedural ellipses in the shader; lashes and white sclera stay outside.
    irises = np.maximum(ellipse((1116, 205, 1137, 226), 1.2), ellipse((1179, 220, 1200, 243), 1.2))
    iris_pigment = ramp(red - green, 20, 40) * ramp(green - blue, 12, 22)
    iris_pigment *= 1 - ramp(green, 190, 220)
    irises *= iris_pigment

    alpha = np.zeros_like(face)
    channels = [np.uint8(np.rint(np.clip(channel, 0, 1) * 255)) for channel in (face, crown, irises, alpha)]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(np.dstack(channels), "RGBA").save(OUTPUT)


if __name__ == "__main__":
    main()
