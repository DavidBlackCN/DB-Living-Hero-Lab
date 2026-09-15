# Blink Tool-Only Evaluation

Date: 2026-09-15

## Environment

- Python 3.13.6
- Pillow 12.3.0
- NumPy 2.2.6
- OpenCV 5.0.0
- ImageMagick: unavailable; `magick` is not on PATH
- Playwright 1.63.0
- Chromium executable available through Playwright

## Method

`scripts/evaluate-blink.py` uses the original `3840x2160` Hero as the only source. It records conservative eye candidates in `docs/blink-regions.json`, extracts an eye debug crop, creates small iris/sclera masks, applies OpenCV Telea inpainting, draws shallow antialiased eyelash arcs with Pillow, and emits source, closed, difference, and transparent overlay previews under `docs/blink-debug/`.

The experiment does not modify the Hero source and does not create `public/assets/generated/blink-closed.png`.

## Result

The geometric diff is mostly local: the experiment reported 4,081 changed pixels inside the candidate masks and 60 pixels outside them above the selected threshold. That is useful for registration, but it is not sufficient for visual acceptance.

Manual inspection rejects the candidate. The inpainted eye regions do not reconstruct the surrounding anime linework consistently: one eye retains distracting original detail while the other reads as a flat fill with a drawn line. The eyelash arcs look like added strokes rather than a natural continuation of the original eye design. This fails the no-sticker and no-face-jump requirements.

## Decision

Pure Pillow/OpenCV editing is useful for coordinate and diff tooling, but this local-only route does not produce a reliable closed-eye asset for the approved illustration. Do not promote the candidate, do not add it to the renderer, and do not implement blink timing yet. A future registered local eye edit or image-editing model is required.
