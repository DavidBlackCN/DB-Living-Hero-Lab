"""Extract registered, straight-alpha blink overlays. Requires Pillow and NumPy."""

import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
CROP = {"x": 1940, "y": 390, "width": 700, "height": 470}
CANVAS = {"width": 3840, "height": 2160}


def main():
    source = ROOT / "work/blink/source/hero-eye-context-open.png"
    hero = Image.open(ROOT / "public/assets/hero-4k-digital-art.png").convert("RGB")
    opened = Image.open(source).convert("RGB")
    box = (1940, 390, 2640, 860)
    if hero.size != (3840, 2160) or opened.size != (700, 470):
        raise ValueError("Unexpected canvas/crop dimensions; no resizing is permitted")
    if opened.tobytes() != hero.crop(box).tobytes():
        raise ValueError("Open crop does not exactly match the runtime hero registration")
    runtime = ROOT / "public/assets/generated/blink"
    previews = ROOT / "work/blink/generated"
    notes = ROOT / "work/blink/notes/blink-runtime-assets.md"
    for directory in (runtime, previews, notes.parent):
        directory.mkdir(parents=True, exist_ok=True)
    metadata = {
        "version": 1, "canvas": CANVAS, "crop": CROP,
        "alpha": "straight", "colorSpace": "srgb",
        "semantics": "Replace base RGB using coverage alpha before relighting; zero alpha preserves source.",
        "states": {}, "sources": {source.relative_to(ROOT).as_posix(): hashlib.sha256(source.read_bytes()).hexdigest()},
    }
    original = np.asarray(opened).astype(np.int16)
    for state in ("half", "closed"):
        path = ROOT / f"work/blink/approved/blink-{state}-approved.png"
        approved = Image.open(path).convert("RGB")
        if approved.size != opened.size:
            raise ValueError(f"{path.name}: expected exact 700 x 470 registration")
        rgb = np.asarray(approved)
        difference = np.max(np.abs(rgb.astype(np.int16) - original), axis=2)
        # Tiny (1-2 code-value) differences feather; meaningful edits fully
        # replace the source, avoiding ghosted original irises/lashes.
        alpha = np.minimum(difference * 85, 255).astype(np.uint8)
        if not np.any(alpha) or np.any(alpha[[0, -1], :]) or np.any(alpha[:, [0, -1]]):
            raise ValueError(f"{path.name}: empty edit or edit touches crop boundary")
        overlay = Image.fromarray(np.dstack((rgb, alpha)))
        filename = f"blink-{state}-overlay.png"
        overlay.save(runtime / filename)
        with Image.open(runtime / filename) as saved:
            assert saved.mode == "RGBA" and saved.tobytes() == overlay.tobytes()
        composite = Image.alpha_composite(opened.convert("RGBA"), overlay).convert("RGB")
        error = np.abs(np.asarray(composite).astype(np.int16) - rgb.astype(np.int16))
        assert error.max() <= 1, "Composite must reproduce approved artwork within one code value"
        assert np.all(np.asarray(composite)[alpha == 0] == original[alpha == 0])
        preview = hero.copy()
        preview.paste(composite, (CROP["x"], CROP["y"]))
        preview.save(previews / f"blink-{state}-preview-full.png")
        composite.save(previews / f"blink-{state}-preview-crop.png")
        metadata["states"][state] = filename
        metadata["sources"][path.relative_to(ROOT).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
        print(f"{state}: {np.count_nonzero(alpha)} covered pixels; bounds {overlay.getbbox()}; max reconstruction error {error.max()}")
    (runtime / "blink-metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    notes.write_text("""# Blink Runtime Assets

Inputs: `work/blink/source/hero-eye-context-open.png`,
`work/blink/approved/blink-half-approved.png`, and
`work/blink/approved/blink-closed-approved.png` (human-approved, unchanged).
Registration is checked against `public/assets/hero-4k-digital-art.png`.
The identity reference is not processed or loaded at runtime.

Outputs: `public/assets/generated/blink/blink-half-overlay.png`,
`blink-closed-overlay.png`, and `blink-metadata.json` in the same directory.
Full-canvas review composites and local crop previews are written to
`work/blink/generated/blink-{half,closed}-preview-{full,crop}.png`.
These review images are not runtime textures.

Canvas: 3840 x 2160. Crop: x=1940, y=390, width=700, height=470,
top-left origin, exclusive right/bottom edges. No resampling, alignment warp,
color correction, repainting, or use of candidate eye boxes as coverage masks.

Coverage derives from max absolute RGB difference against Open. Identical
pixels have alpha 0; differences of 1/2 have alpha 85/170; differences >=3
have alpha 255. Thus original lashes/irises are completely replaced where
needed, while sub-visible boundary differences taper. Straight-alpha sRGB RGB
retains approved pixel values even under transparency, avoiding black fringes.
The script verifies exact registration, transparent crop borders, unchanged
uncovered pixels, and reconstruction within one 8-bit code value of approval.
SHA-256 input hashes are recorded in metadata. This extraction assumes the
approved edits remain localized; it is not a general eye-segmentation tool.

Rebuild from repository root: `python scripts/prepare-blink-assets.py`.
Dependencies: `python -m pip install Pillow numpy`.
Re-running overwrites only these generated assets, previews and this note.
""", encoding="utf-8")


if __name__ == "__main__":
    main()
