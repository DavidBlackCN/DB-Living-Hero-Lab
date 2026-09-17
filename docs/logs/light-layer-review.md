# Light-layer review — 2026-09-18

## Scope and reference

User requested reference implementation analysis before further edits, then
structural contact/form/occlusion improvements, coherent room response and a
rear-right indoor lamp. Window correction from `1741b31` is accepted and retained.
No blink, UI layout, source illustration, architecture or dependencies changed.
See [source analysis](kumeng-lighting-analysis.md), completed before implementation.

Baseline is `1741b31`. Four baseline times were run and captured before editing.
The reference suggests separating fill and key, with soft normal-driven tones
across the whole scene. It does not provide indoor lamp or contact-shadow code.

## Implementation

`src/engine/light-layers.ts` composes logical ambient/window/projection/lamp/
emission layers inside the existing scene pass. It replaces the final aggregate
darkening stage: visibility removes energy from incident sources individually,
and never dims lamp emission. No additional GPU textures, samples or FBOs.

Environment fill now has soft orientation-dependent cool dark tones, sky access
and low-energy window-color bounce. The same time/direction state reaches walls,
chair/drape and foreground through existing room weights. Direct window and
lamp responses have broad lit/turning/back-facing bands, with face protection.
The shadow slider controls contact and enclosure occlusion; it no longer disables
all form response. Stylized/softness and normal controls govern form response.

Existing registered B-channel contacts (hair/face, chin/neck, straps, hand/page,
book/desk, cup/coaster, sill objects, chair/drape) gain a faint wider penumbra.
`contactPenumbra` is authored in `docs/scene-regions.json`: widthScale 2.2,
feather 4.5 reference pixels, weight .24. Both tight and wider detail bands are
clipped to the same receivers. Book/coaster desktop bands retain their geometry.
Ambient occlusion is capped at .42, direct visibility reduction at .42, and lamp
visibility reduction at .46; these are separate source budgets, not additive
final-image darkness. Face contact input is capped at .045 before weighting.

Lamp position, registered pools, corrected sill and rear visibility remain.
The new normal band modulates these pools: right sleeve/hair and cup show turning
surfaces, with weaker light at contacts. Existing face/chest exclusions prevent
front fill. This is still an authored 2D approximation, not ray-traced transport.

Three options were added to the existing diagnostic selector only: Ambient Fill
Only, Form Light Bands, Contact Visibility. Shadow/Occlusion now reports the
fraction of incident light removed by visibility (zero with zero light), not an
artificial night-darkness floor. Energy statistics run only in that debug view.
Lamp and directional diagnostics show source contributions before final face/
highlight protection. Projected Light Only retains its raw aperture diagnostic.

## Validation and evidence

- `npm run typecheck`, `npm test` (7/7), `npm run build`: passed.
- Full Playwright suite: 49/49 passed. After moving debug-only energy statistics
  behind its view branch, the 5 layer/desk tests were rerun successfully.
- Existing night book illumination minimum was retained. An initial narrow lamp
  band failed it; widening the physical transition restored it.
- One desk diagnostic assertion changed: alpha=255 proves a rendered shadow
  buffer, replacing a minimum gray floor incompatible with the new visibility
  definition. All continuity/contact/no-floating-stripe checks remain.
- All four Base and Exterior Mask before/after images have max pixel difference 0.
- New checks isolate normal-dependent fill, contact vs open cloth, independent
  emission, no-light visibility, room color response and exposure-free form bands.
- Final four-time captures and closeups were inspected; equal-mean Neutral
  comparisons separate form contrast from simply lowering average brightness.

In fixed Neutral ROIs, standard deviation divided by mean at 17:30 changes:
hair .253→.279, cloth .257→.286, cup .187→.233, wall .090→.110,
chair .115→.146. At 23:00 cup .151→.199. These describe lighting coefficients,
not perceived quality scores. Improvement is not uniform: noon cup .137→.126.
Faces deliberately retain a restrained change; foreground remains very subtle.
See [gallery](../screenshots/light-layer-review/README.md).

## Performance and remaining gaps

1440×900 isolated ABBA comparison used baseline source vs current source, default
bloom/animation and DPR 1 / 1.5. Both served the same current public assets
(texture dimensions are unchanged); therefore this isolates runtime shader work,
not old-vs-new contact asset appearance. Renderer was ANGLE Vulkan SwiftShader
software rendering, not hardware GPU. At DPR 1, final medians were baseline
33.3/16.7 ms and current 16.7/16.7 ms; p95 ~50 ms. At DPR 1.5 baseline
49.9/50.0 ms, current 66.6/66.6 ms; p95 83.4 vs 100.1/116.6 ms. GL error=0.
There is a measurable high-DPR software-renderer cost. Debug gating does not
remove it. No claim of smooth hardware performance or zero regression is made;
hardware GPU validation remains outstanding. Existing DPR cap 1.5 is retained.

The illustration has baked lighting; broad authored normals cannot reconstruct
individual hairs, transparent vase transport or true object depth. Contacts are
registered soft strokes, not moving cast shadows. Night cup and hair improve,
but face lighting and some original highlights remain art-directed. The result
does not reach the reference's purpose-made asset coherence. No attempt was made
to hide these limits with stronger bloom or globally crushing the image.

Screenshots and JSON stay local per repository policy. `scripts/summarize-light-layers.py`
regenerates comparison strips/metrics from the before/after captures.
