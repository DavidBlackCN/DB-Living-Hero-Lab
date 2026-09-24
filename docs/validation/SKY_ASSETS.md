# Registered sky assets — art handoff

The frozen Base remains `public/assets/hero/base/base-albedo.png`. The five deliverables in `public/assets/hero/sky/` use its exact 1672×941 pixel grid:

| File | Format | Purpose |
| --- | --- | --- |
| `sky-mask.png` | 8-bit grayscale | White is replaceable open sky; black protects all foreground and architecture. Boundary pixels carry a narrow soft transition. |
| `sky-dawn.png` | RGBA | Cool light gray-blue morning with faint warm haze low in the openings. |
| `sky-noon.png` | RGBA | Pale restrained blue-gray afternoon sky. |
| `sky-dusk.png` | RGBA | Gray-blue above, muted rose-apricot close to the visible lower sky. |
| `sky-night.png` | RGBA | Stable deep charcoal blue-gray with no daytime clouds, stars, or moon. |

The PNG alpha of each sky image already equals `sky-mask.png`. Composite the sky image once over the frozen Base or the relit scene; do not multiply its alpha by the mask again. The mask is also available as a separate region control for a future shader. Keep UV origin at the artwork's upper left. The Base remains the structural source of truth, including buildings, distant campus towers, the character, vines, leaves, and balustrade. Night's bright architecture in the Base-only preview will be handled by the existing scene lighting during runtime integration.

## Production and review

The reproducible source is `scripts/generate_sky_assets.py`. The first pass identified open sky with color and GrabCut but leaked onto the character at the lower edge. The second pass restricted the selection to the actual light cool sky range, removed tiny isolated picks, and adjusted the four palettes. A final pass widened the boundary by one pixel, softened it by 0.65 px, and made Dawn cooler and Dusk's lower sky warmer. This conservative contour protects thin leaves, tower spires, the hat, hair, and masonry, while letting the new sky cover the Base's antialiased sky edge.

Review images are in `docs/validation/sky-assets/`: `mask-overlay.png`, the four `sky-*-on-base.png` images, and `four-sky-comparison.png`. They use the unlit Base to isolate the artwork change; they do not represent the final runtime lighting.

Visual review result: Dawn and Noon remain pale and distinct; Dusk reads as a gentle autumn evening without saturated clouds; Night is a smooth dark atmosphere without the original bright blue sky pattern. All four preserve the fixed scene geometry. Human acceptance is still required before freezing this sky set or connecting it to the 24-hour runtime.

## Night refinement

After review, Night received one small follow-up pass. Its original dark gray-blue vertical gradient is unchanged; a deterministic, heavily blurred atmospheric field adds only a few RGB levels of broad luminance variation. This keeps the sky quiet and visibly nighttime without creating cloud silhouettes, stars, or color bands. `sky-night-before-refinement.png` and the updated `sky-night-on-base.png` provide the before/after comparison. The Dawn, Noon, Dusk, and mask files are byte-for-byte unchanged, and the updated four-sky comparison remains visually coherent.
