# Normal map generation attempt — 2026-09-16

Built-in image_gen, imagegen skill. Input: `hero-4k-digital-art.png` exported at
identical 3840×2160 dimensions as a quality-97 JPEG for tool transport, with no
crop or geometry change. The original PNG remains unchanged. Tool model ID was
not exposed; no CLI/API fallback was used.

Output saved locally as `docs/screenshots/normal-map-review/normal-ai-candidate.png`.
Actual output size: **1672×941**, despite the 4K instruction. Rejected for runtime:
the book/page geometry and other details were redrawn, so resizing alone would
not establish registration. This is a local reference, excluded from Git.

## Exact prompt

Use case: precise-object-edit. Asset type: a technically usable RGB CAMERA-SPACE SURFACE NORMAL DATA MAP for this exact 3840x2160 hero illustration. The input is the edit target, not a loose style reference. Transform representation only. Output a single 3840x2160 PNG, identical full image framing, no crop, zoom, new geometry or moved objects. Every silhouette, eye, hair lock, garment seam, hand/finger, cup rim/handle, book page contour, window frame must remain registered at its original pixel position. Do not render a beauty image or a blue-tinted illustration.
Encode actual unit surface directions as RGB = (normal XYZ * 0.5 + 0.5)*255: X positive toward image RIGHT, Y positive toward image DOWN, Z positive TOWARD VIEWER. A flat camera-facing surface is RGB(128,128,255). Left-facing slopes have R<128; right-facing slopes R>128; upward-facing surfaces G<128. The upper desk surface therefore has low green. Positive Z throughout.
Reconstruct calm, smooth plausible surface volume: rounded flowing hair bundles (not each painted dark strand becoming a trench), real soft clothing folds and gathered sleeve volumes, smooth face and hands with exceptionally restrained facial depth; eyes/iris color/eyelashes are not embossed craters. Cup is a rounded upright cylinder with a curved handle and rim; open book has gently curved left and right page surfaces rising near spine; tabletop is a consistent flat tilted plane with no wood-grain bump. Vertical glass is flat. Treat distant outdoor sky/foliage and featureless wall as flat camera-facing normal RGB(128,128,255), not cloud-shaped embossed detail. No shadows, lighting gradients, original colors, ambient occlusion, specular highlights, bloom, text, legend or borders in the normal data. This is not a luminance-to-bump conversion. Preserve all original geometry exactly; shape-aware normals only. High-quality soft anime relighting, controlled mid-frequency geometry, no noisy microdetail.

## Selected engineering route

The runtime preview uses a separate deterministic authored-surface candidate:
`docs/normal-surfaces.json` → `scripts/generate-registered-normal.py` →
`public/assets/generated/normal-registered-v1.png`. It does not use generated
pixels from the rejected AI output. See the normal-map review for limitations.
