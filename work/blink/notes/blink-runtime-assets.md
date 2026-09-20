# Blink Runtime Assets

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
