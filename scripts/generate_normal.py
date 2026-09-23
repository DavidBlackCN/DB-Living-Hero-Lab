"""Generate a registered, conservative bas-relief normal test map from Base-4.

This is a deterministic v1 lighting-test asset, not a hand-authored semantic
surface normal. Run from the repository root: python scripts/generate_normal.py
"""

from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "public/assets/hero/base/base-albedo.png"
OUTPUT = ROOT / "public/assets/hero/normal/base-normal-v1.png"
EXPECTED_SIZE = (1672, 941)


def main() -> None:
    base = Image.open(SOURCE).convert("RGB")
    if base.size != EXPECTED_SIZE:
        raise ValueError(f"Expected {EXPECTED_SIZE}, got {base.size}")
    luminance = base.convert("L")
    fine = np.asarray(luminance.filter(ImageFilter.GaussianBlur(3)), dtype=np.float32) / 255
    broad = np.asarray(luminance.filter(ImageFilter.GaussianBlur(16)), dtype=np.float32) / 255
    height = 0.6 * fine + 0.4 * broad
    dy, dx = np.gradient(height)
    vectors = np.stack((-dx * 13, -dy * 13, np.ones_like(height)), axis=-1)
    vectors /= np.linalg.norm(vectors, axis=-1, keepdims=True)
    rgb = np.clip(np.rint((vectors * 0.5 + 0.5) * 255), 0, 255).astype(np.uint8)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(rgb, "RGB").save(OUTPUT, optimize=True)
    print(f"{OUTPUT.relative_to(ROOT)}: {base.size}, RGB, registered source pixels")


if __name__ == "__main__":
    main()
