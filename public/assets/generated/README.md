# Technical assets

Current Technical Art Alignment assets:

- `normal-registered-v2.png`: default 3840×2160 RGB8 surface normals. Authored
  tapered ribbons, sleeves/fingers, distinct book pages, cup, chair/laptop/lamp.
  `npm run assets:normal` uses `docs/normal-surfaces.json`. Encoding is unchanged.
- `normal-registered-v1.png`: retained comparison; source archived at
  `docs/normal-surfaces-v1.json`; rebuild with `npm run assets:normal -- --version v1`.
- `intrinsic-correction-v1.png`: optional **3840×2160 grayscale data**, uploaded
  as R8. Neutral value 128, EV `(R-128)/254`. Bounded scalar gain before lighting,
  no displacement or source repaint. `npm run assets:correction` builds it from
  v2 normal and source regions. Only `?correction=1` loads it in the demo.

The approved Hero is unchanged. v2 is deterministic authored geometry, not a
recovered ground-truth surface. Correction is an experiment, not albedo recovery.
See [v2 notes](../../../docs/logs/normal-v2-review.md) and
[current review](../../../docs/screenshots/technical-art-alignment/README.md).
Historical v1/low-frequency descriptions below are retained for context.

Latest local correction: [left lower glass softness and pen occlusion](../../../docs/screenshots/left-mask-softness/README.md). The left lower edge now has a source-authored, inward alpha transition matching the illustration's defocus; the right glass remains native hard-edge coverage. This local exception supersedes the general glass-edge description below. It changes the scene texture only, with no runtime shader changes.

The demo loads four registered vector data textures, authored from the original artwork's major contours. These are technical approximations, not AI segmentation or physically reconstructed normals.

| Asset | Data |
| --- | --- |
| `character-masks.svg` | R face, G hair, B upper clothing; hands excluded |
| `scene-masks.svg` | R glass coverage, G indoor receivers (desk/book/cup/books/chair/hands), B lamp emitter; hair/clothing occlude the desk |
| `window-flower-occlusion.png` | Offline grayscale petal coverage, embedded into scene SVG; no additional GPU texture |
| `normal-low-frequency.svg` | RGB-encoded broad surface orientations, renormalized in shader |
| `normal-registered-v1.png` | Optional 3840×2160 authored surface-normal candidate; hair/sleeve curvature, cup cylinder, curved book pages; preview with `?normal=registered` |
| `light-shaping.svg` | R window access, G soft room receiving weights, B book/cup contact occlusion clipped to exposed desktop; 1200×675 |

All SVGs share a 1200×675 viewBox. Character, scene and normal maps rasterize at 3840×2160; light shaping rasterizes at 1200×675. Contours and petal extraction thresholds are in `docs/scene-regions.json`; run `npm run assets:generate` after editing them. Generation requires Python 3, Pillow and NumPy in addition to Node. The local petal extractor reads the Hero's colors, but never changes either approved source image. Petal coverage is constrained to source-colored seeds and their immediate neighborhood, avoiding background-shaped holes. The browser rasterizes SVG once during asset loading; no per-frame vector rendering is used. Material/receiver boundaries use a 1.15 reference-pixel blur. Glass uses native path antialiasing with **no erosion or added blur**; the former inward feather created uncovered seams. The shader uses red coverage directly without UV cutoffs or mask-threshold patches. Independent source-edge probes live in `docs/window-edge-probes.json`.

Light-shaping channels are composed independently with screen blending. B has a 2.2-reference-pixel contact blur, clipped to exposed desktop, and contributes at most 12% darkening. G is never translated or sampled as a caster: that approximation made false hand/page shadows without receiver depth. Lighting Convergence 2 reuses the previously diagnostic G channel for five coarse room weights from `roomParticipation` in the region source. Weights feather by 10 reference pixels and exclude existing character/desk silhouettes. Custom maps should author these weights or set G=0; old diagnostic desktop G has different semantics. R/B retain their meanings. The map still adds 2.32 MiB RGB8, with no added texture or pass. `lightShapingUrl` must retain the artwork aspect ratio and exact spatial registration. See the [room/lamp calibration](../../../docs/logs/lighting-convergence-2.md) and historical [desk correction](../../../docs/logs/desk-light-review.md).

Do not edit generated SVG files directly. Reload the page after regeneration to reload textures. Original Phase 1 ellipses remain available through the debug comparison toggle.

The registered normal candidate is rebuilt separately with `npm run assets:normal`
(Python + Pillow + NumPy), from `docs/normal-surfaces.json` and existing region
contours. Surface gradients are computed **before** applying silhouette masks,
then unit vectors are blended and renormalized. It uses no artwork luminance,
painted shadows or AI-generated pixels as height. It has the same GPU dimensions
as the low-frequency map and replaces that texture only for the opt-in preview.
This authored geometry remains approximate; see the [review](../../../docs/screenshots/normal-map-review/README.md).

Replacement `normalUrl` / `maskUrl` / `sceneMaskUrl` assets must match the hero's 3840 × 2160 dimensions and exact registration.
- Normal: RGB encoded XYZ in [0,1], decoded to [-1,1], +X image right, +Y image down, +Z toward viewer. Flat normal = (128,128,255). Treat as data, not sRGB.
- Mask: linear RGB weights; R face, G hair, B cloth/body. Black elsewhere. Soft boundaries, no geometry shift.
- Both images use top-left image coordinates; do not flip vertically.
- `kuro-standard.png` is identity reference only, never the runtime scene.

Thin flyaway hairs, gaps between curls, indoor flower stems and translucent glass still need finer segmentation. No inverse-lighting reconstruction has been performed. See docs/architecture.md.
