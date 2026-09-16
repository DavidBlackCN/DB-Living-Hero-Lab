# Technical assets

The demo loads four registered vector data textures, authored from the original artwork's major contours. These are technical approximations, not AI segmentation or physically reconstructed normals.

| Asset | Data |
| --- | --- |
| `character-masks.svg` | R face, G hair, B upper clothing; hands excluded |
| `scene-masks.svg` | R glass coverage, G indoor receivers (desk/book/cup/books/chair), B lamp emitter |
| `window-flower-occlusion.png` | Offline grayscale petal coverage, embedded into scene SVG; no additional GPU texture |
| `normal-low-frequency.svg` | RGB-encoded broad surface orientations, renormalized in shader |
| `light-shaping.svg` | R window access, G softened raised-object silhouette, B book/cup contact occlusion; 1200×675 |

All SVGs share a 1200×675 viewBox. Character, scene and normal maps rasterize at 3840×2160; light shaping rasterizes at 1200×675. Contours and petal extraction thresholds are in `docs/scene-regions.json`; run `npm run assets:generate` after editing them. Generation requires Python 3, Pillow and NumPy in addition to Node. The local petal extractor reads the Hero's colors, but never changes either approved source image. Petal coverage is constrained to source-colored seeds and their immediate neighborhood, avoiding background-shaped holes. The browser rasterizes SVG once during asset loading; no per-frame vector rendering is used. Material/receiver boundaries use a 1.15 reference-pixel blur. Glass uses native path antialiasing with **no erosion or added blur**; the former inward feather created uncovered seams. The shader uses red coverage directly without UV cutoffs or mask-threshold patches. Independent source-edge probes live in `docs/window-edge-probes.json`.

Light-shaping channels are composed independently with screen blending. G has a 4.5-reference-pixel penumbra; B has a 2.2-pixel contact blur. G is translated along the current light direction and constrained to indoor receiving areas; this approximates cast shadows without a depth map or extra pass. Its source texture adds 2.32 MiB RGB8. `lightShapingUrl` must retain the artwork aspect ratio and exact spatial registration.

Do not edit generated SVG files directly. Reload the page after regeneration to reload textures. Original Phase 1 ellipses remain available through the debug comparison toggle.

Replacement `normalUrl` / `maskUrl` / `sceneMaskUrl` assets must match the hero's 3840 × 2160 dimensions and exact registration.
- Normal: RGB encoded XYZ in [0,1], decoded to [-1,1], +X image right, +Y image down, +Z toward viewer. Flat normal = (128,128,255). Treat as data, not sRGB.
- Mask: linear RGB weights; R face, G hair, B cloth/body. Black elsewhere. Soft boundaries, no geometry shift.
- Both images use top-left image coordinates; do not flip vertically.
- `kuro-standard.png` is identity reference only, never the runtime scene.

Thin flyaway hairs, gaps between curls, indoor flower stems and translucent glass still need finer segmentation. No inverse-lighting reconstruction has been performed. See docs/architecture.md.
