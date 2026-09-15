# Directional Lighting Upgrade

Date: 2026-09-15

## Diagnosis

The previous renderer mostly read as global brightness and color temperature. Its light direction was effectively fixed at approximately `[0.65, y, 0.72]`, with only a small vertical oscillation. The temporary low-frequency normal is also broad and often close to a forward-facing normal, so Lambert response had limited spatial separation. Ambient contribution and face protection further reduced directional contrast; dusk and night were therefore carried mainly by tint and suppression.

## Changes

- Replaced the nearly fixed direction with an art-directed solar sweep. Morning is a lower right-side light, noon is higher and more frontal, dusk is lower and strongly window-side, and night retains negligible sun energy.
- Added a soft anime broad-light band controlled by `stylized` strength and `softness`. It is normal-based and does not claim to be a cast shadow.
- Added `Neutral Lighting` debug view, which removes time color and shows the resulting lighting structure in grayscale.
- Kept face protection, but directional response now reaches the protected face as a broad, softened value change rather than a hard facial shadow.
- Hair and scene regions continue to use the existing masks and low-frequency normal. No source hero pixels were changed.

## Validation

Playwright captures fixed Morning 08:00, Noon 12:00, Dusk 17:30, and Night 23:00 Final and Neutral views under `docs/screenshots/phase-next/`. The Neutral captures are intended to judge moving light structure independently from tint. Existing Bloom, Steam, mask, scene, overlay, DPR, and performance coverage remains enabled.

The current low-frequency normal remains the principal visual limitation: it can demonstrate broad directional movement, but it cannot produce fine hair-strand, cloth-fold, or object-edge transitions. A future registered high-quality normal should be recalibrated against the default `stylized=0.42`, `softness=0.18`, `face=0.8`, and `normal=1` settings rather than forcing this temporary map into fine detail.

Blink status remains: Blink renderer implementation: blocked by missing registered closed-eye asset.

## Next step

Pause here for visual review. Do not begin breathing, hair motion, or Blink implementation automatically.
