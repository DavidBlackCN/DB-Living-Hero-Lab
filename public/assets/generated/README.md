# Technical assets

Phase 2 loads three registered vector data textures, authored from the original artwork's major contours. These are technical approximations, not AI segmentation or physically reconstructed normals.

| Asset | Data |
| --- | --- |
| `character-masks.svg` | R face, G hair, B upper clothing; hands excluded |
| `scene-masks.svg` | R glass coverage, G indoor receivers (desk/book/cup/books/chair), B lamp emitter |
| `window-flower-occlusion.png` | Offline grayscale petal coverage, embedded into scene SVG; no additional GPU texture |
| `normal-low-frequency.svg` | RGB-encoded broad surface orientations, renormalized in shader |

Each SVG has intrinsic dimensions 3840×2160 and a 1200×675 viewBox. Contours and petal extraction thresholds are in `docs/scene-regions.json`; run `npm run assets:generate` after editing them. Generation requires Python 3, Pillow and NumPy in addition to Node. The local petal extractor reads the Hero's colors, but never changes either approved source image. The browser rasterizes SVG once during asset loading; no per-frame vector rendering is used. Material/receiver boundaries use a 1.15 reference-pixel blur. Glass uses a separate inward feather (0.65 erosion, 0.45 blur, intersection with original coverage) to keep exterior treatment off the frame/sill. The shader uses red coverage directly without UV cutoffs or mask-threshold patches.

Do not edit generated SVG files directly. Reload the page after regeneration to reload textures. Original Phase 1 ellipses remain available through the debug comparison toggle.

Replacement `normalUrl` / `maskUrl` / `sceneMaskUrl` assets must match the hero's 3840 × 2160 dimensions and exact registration.
- Normal: RGB encoded XYZ in [0,1], decoded to [-1,1], +X image right, +Y image down, +Z toward viewer. Flat normal = (128,128,255). Treat as data, not sRGB.
- Mask: linear RGB weights; R face, G hair, B cloth/body. Black elsewhere. Soft boundaries, no geometry shift.
- Both images use top-left image coordinates; do not flip vertically.
- `kuro-standard.png` is identity reference only, never the runtime scene.

Thin flyaway hairs, gaps between curls, indoor flower stems and translucent glass still need finer segmentation. No inverse-lighting reconstruction has been performed. See docs/architecture.md.
