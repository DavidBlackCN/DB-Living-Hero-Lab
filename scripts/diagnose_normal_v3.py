"""Render reproducible local Normal v2/v3 diagnostic contact sheets.

Each crop contains Base, both Normal maps, an amplified map difference,
six test-light directions at app strength, and six at 1.3x stress strength.
Run from the repository root: python scripts/diagnose_normal_v3.py
"""

from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "public/assets/hero"
OUTPUT = ROOT / "docs/validation"
ANGLES = (0, 90, 180, 270, 135, 315)
CROPS = {
    "hair": (875, 90, 1480, 625),
    "clothing": (845, 335, 1410, 850),
    "architecture-left": (850, 0, 1060, 510),
    "architecture-right": (1300, 0, 1672, 941),
}


def test_light(base: np.ndarray, normal: np.ndarray, degrees: int, strength: float) -> Image.Image:
    radians = np.deg2rad(degrees)
    light = np.array([np.cos(radians), np.sin(radians), 0.75], np.float32)
    light /= np.linalg.norm(light)
    response = normal @ light - light[2]
    result = np.clip(base * (1 + response[..., None] * strength), 0, 1)
    return Image.fromarray(np.uint8(np.rint(result * 255)), "RGB")


def main() -> None:
    base_image = Image.open(ASSETS / "base/base-albedo.png").convert("RGB")
    v2_image = Image.open(ASSETS / "normal/base-normal-v2.png").convert("RGB")
    v3_image = Image.open(ASSETS / "normal/base-normal-v3.png").convert("RGB")
    if not (base_image.size == v2_image.size == v3_image.size == (1672, 941)):
        raise ValueError("All inputs must use 1672x941 Artwork Space")
    base = np.asarray(base_image, np.float32) / 255
    encoded = np.asarray(v3_image, np.float32) / 255
    normal = encoded * 2 - 1
    normal /= np.linalg.norm(normal, axis=2, keepdims=True)
    delta = np.asarray(v3_image, np.int16) - np.asarray(v2_image, np.int16)
    diff = Image.fromarray(np.uint8(np.clip(np.abs(delta) * 12, 0, 255)), "RGB")

    for name, box in CROPS.items():
        x0, y0, x1, y1 = box
        tile_w = 320
        tile_h = round((y1 - y0) * tile_w / (x1 - x0))
        label_h = 22
        sheet = Image.new("RGB", (tile_w * 4, (tile_h + label_h) * 4), (30, 30, 30))
        draw = ImageDraw.Draw(sheet)
        panels = [
            ("Base", base_image),
            ("Normal v2", v2_image),
            ("Normal v3", v3_image),
            ("abs(v3-v2) x12", diff),
        ]
        panels += [(f"{angle} deg / 0.65", test_light(base, normal, angle, 0.65)) for angle in ANGLES]
        panels += [(f"{angle} deg / 1.3 stress", test_light(base, normal, angle, 1.3)) for angle in ANGLES]
        for index, (label, image) in enumerate(panels):
            col, row = index % 4, index // 4
            x, y = col * tile_w, row * (tile_h + label_h)
            draw.text((x + 4, y + 4), label, fill="white")
            sheet.paste(image.crop(box).resize((tile_w, tile_h), Image.Resampling.LANCZOS),
                        (x, y + label_h))
        target = OUTPUT / f"normal-v3-diagnostic-{name}.png"
        sheet.save(target, optimize=True)
        print(target.relative_to(ROOT))


if __name__ == "__main__":
    main()
