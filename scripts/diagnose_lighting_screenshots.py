from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image


ANCHORS = ("0630", "1200", "1730", "2200")
SCREENSHOT_SIZE = (1440, 900)
REGIONS = {
    "artwork": [(310, 0, 1440, 900)],
    "face": [(930, 90, 1110, 300)],
    "white_shirt": [(730, 300, 920, 650), (1130, 300, 1245, 670)],
    "background_architecture": [(320, 40, 740, 470)],
}


def luminance_pixels(image: Image.Image, boxes: list[tuple[int, int, int, int]] | None = None) -> np.ndarray:
    rgb = np.asarray(image.convert("RGB"), dtype=np.float32) / 255.0
    if boxes is not None:
        parts = [rgb[y0:y1, x0:x1] for x0, y0, x1, y1 in boxes]
        rgb = np.concatenate([part.reshape(-1, 3) for part in parts], axis=0)
    linear = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    return linear @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)


def stats(image: Image.Image, boxes: list[tuple[int, int, int, int]] | None = None) -> dict[str, float]:
    lum = luminance_pixels(image, boxes)
    rgb = np.asarray(image.convert("RGB"), dtype=np.uint8)
    if boxes is not None:
        rgb = np.concatenate([rgb[y0:y1, x0:x1].reshape(-1, 3) for x0, y0, x1, y1 in boxes], axis=0)
    return {
        "mean": float(lum.mean()),
        "p95": float(np.quantile(lum, 0.95)),
        "p99": float(np.quantile(lum, 0.99)),
        "near_white_pixel_pct": float(np.mean(np.any(rgb >= 254, axis=-1)) * 100.0),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Measure luminance and clipping in R2A lighting screenshots.")
    parser.add_argument("--directory", type=Path, default=Path(tempfile.gettempdir()))
    parser.add_argument("--prefix", default="r2a3")
    args = parser.parse_args()

    result: dict[str, object] = {}
    for minute in ANCHORS:
        path = args.directory / f"{args.prefix}-{minute}.png"
        if not path.is_file():
            raise SystemExit(f"Missing screenshot: {path}")
        with Image.open(path) as source:
            image = source.convert("RGB")
        if image.size != SCREENSHOT_SIZE:
            raise SystemExit(f"Expected {SCREENSHOT_SIZE} screenshot, got {image.size}: {path}")
        report: dict[str, object] = {"size": list(image.size), "full_frame": stats(image)}
        for name, boxes in REGIONS.items():
            report[name] = stats(image, boxes)
        result[minute] = report

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
