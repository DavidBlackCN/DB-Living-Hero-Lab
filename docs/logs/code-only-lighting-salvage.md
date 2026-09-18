# Code-only Lighting Salvage Pass — 2026-09-18

Baseline: `f941549`. Scope: existing Hero, registered normal v2, scene masks and
current shader; lamp propagation first, then shadow hierarchy/environment.
Window geometry is accepted and retained. No blink, breathing, hair animation,
particles, Blog integration, source repaint, depth reconstruction or new FBO.

## Reference methodology (four transferable points)

Re-read KumengScreen's current source before implementation, without restarting
the earlier investigation. Main-branch links are mutable, not a pinned release.

1. Share time-dependent key direction, key color and sky fill across the image,
   including areas outside local bright patches. [daylight.ts](https://github.com/buger404/KumengScreen/blob/main/lib/daylight.ts)
2. Separate key/fill and form broad soft normal-driven light/dark tones; preserve
   cool fill on the dark side. This is a plausible source of whole-scene coherence
   without depth, not evidence of a hidden shadow solver. [stylized-lighting.ts](https://github.com/buger404/KumengScreen/blob/main/lib/stylized-lighting.ts)
3. Protect face readability and treat hair sheen as a material response tied to
   the same light. Keep our illustration-specific face/hair protection; do not
   transplant its face coordinates or hair ribbons. [scene-shader.ts](https://github.com/buger404/KumengScreen/blob/main/lib/scene-shader.ts)
4. Bloom composites already-lit energy; it does not create missing visibility.
   Preserve our existing restrained bloom rather than importing its HDR/multilevel
   pipeline. [post-shaders.ts](https://github.com/buger404/KumengScreen/blob/main/lib/post-shaders.ts)

The reference still has no indoor lamp or contact-shadow system to copy.

## Lamp propagation

`src/engine/lamp-fields.ts` replaces the sum of unbounded Gaussian pools with
three independently registered receiving fields. Their compact polynomial
falloff is `max(1 - dot(delta/extent, delta/extent), 0)^2`, continuous with zero
slope at its outer boundary. The emitter remains independent Scene B.

| Component | Center / extent (top-left UV) | Receiver and response |
| --- | --- | --- |
| Emitter | Existing registered Scene B | Unshaded emission; independent of AO |
| Near field | (.811,.445) / (.165,.240) | Under shade, tools/frame/sill plus weak continuous pole/apron bounce; character/glass excluded |
| Desk | (.814,.751) / (.235,.170) | Existing receivers; compact cup/right-page core; continuous sleeve/hand boundaries |
| Character | (.747,.515) / (.135,.285) | Hair/cloth and smooth right/back visibility; excludes face |

Near-field response combines broad underside illumination and local bounce,
so flat vertical tool surfaces no longer vanish under the desk's response model.
Desk/character retain normal-driven turning surfaces toward a rear-offset source.
Character material weighting is applied to its field. Normal/form is evaluated
once; the old divide-by-wrapped-response compensation and spatial Gaussian tail
are removed. Existing global lamp control scales reflection and emission together.

Lamp Fields diagnostic: red=near, green=desk, blue=character, white=emitter.
It shows receiving fields before energy/form/contact, not the final lamp color.
Lamp Only shows the actual combined source contribution.

## Three shadow levels

1. Contact: preserve registered, time-stable B strokes; add a narrow cup-to-coaster
   arc inside the existing cup receiver. Existing book/coaster desktop contacts
   and hair/face, neck, straps, hand/page, chair/drape, object/sill contacts remain.
2. Form: preserve the previous soft normal bands and low fill, and evaluate the
   lamp band before field-specific near/desk/character responses. No cel blocks.
3. Scene exclusion: `sceneVisibility` softens direct light separately for front
   torso and shelf recesses, using existing body/G masks and smooth screen-space
   weights. Source budgets differ for window/projected/lamp. Ambient and emitter
   are not globally crushed. This is authored self-occlusion, not a depth solution.

Projected diagnostic now shows the visible projected contribution after contact/
scene exclusion (and light tint luminance), rather than the raw aperture amount.
Shadow/Occlusion remains removed incident energy. No silhouette is translated;
hand/page continuity and detached-book-shadow regressions remain guarded.

## Whole-scene environment and time

Add broad environment orientation derived from the same window direction to the
existing room weights. This redistributes existing fill without raising ambient.
Wall, bookshelf, chair, blanket, foreground, rear table, window objects, character
and desk share the same time state. New room probes cover the previously unchecked
shelf/blanket/rear-table/window-object areas even without projected illumination.

06:00 key shifts from warm to pale cool-neutral while keeping the low-angle
direction. Noon and dusk keys/directions are unchanged; noon remains clean and
dusk stays the strongest window-direction reference. Night retains low ambient,
cool exterior and protected expression, with no direct lamp on front face/chest.

## Baked-light compensation

Reused the existing registered optional correction texture via `?correction=1`.
Compared correction=0 and .25 at 23:00. Mean absolute final change was only .082
on an 8-bit scale; inspection showed negligible benefit to light coherence.
Keep correction=0 by default and do not invest in full albedo regeneration.
The existing baseline night highlight suppression remains unchanged.

## Before / after and validation

[Gallery](../screenshots/code-only-salvage/README.md): before and after at 1920×1080,
DPR 1, default exposure/light settings/bloom, reduced motion and steam off.
Both runs use normal v2, unchanged source art and identical scene/window masks.
Four Final/Neutral/Lamp/Shadow views are retained, plus closeups and field debug.

At 23:00, fixed lower reading/table crop area above Lamp red=.1 changes from
169149 to 133701 pixels (~21% smaller). Near-tool lamp coefficient .149→.523;
front-desk .114→.022. These measure contribution, not final material brightness.
Final image mean absolute changes: dawn 2.27, noon .37, dusk .80, night 2.19 /255.
This supports protected noon/dusk, not a claim that quality is a pixel metric.

Runtime probes: tools .523, near sill .438, far sill .119, cup .369, right page
.632, right hair .283, sleeve .166; face/chest/glass 0 (Lamp red channel).
Near-source energy now reaches tools before the distant reading pool; materials
and normals still legitimately produce unequal final brightness.

Build/typecheck and 7 unit tests passed. The 51 visual checks passed across the
full run plus targeted reruns: the first full run passed 50, with one outdated
left-hand lamp expectation. That sample is now tested as excluded; orientation
response is checked on the illuminated right hand with the same threshold.
The old left-book illumination box similarly moved to the requested right-page
core; independent new checks require weaker left-page/front-desk response.
No window/contact/continuity/face thresholds were loosened.

## Performance

No new texture/sample/FBO or dependency; generated light-shaping dimensions stay
1200×675. Runtime source textures remain 97.24 MiB by existing accounting. Compact
lamp fields replace three exponentials and the obsolete spatial Gaussian tail;
the form ratio/division is removed. This offsets part of the new visibility math.

`scripts/compare-lighting-performance.mjs` compares baseline/current in isolated
ABBA order at 1440×900, DPR 1/1.5, dusk/night, default bloom. Both sources use the
same current public assets to isolate runtime cost. Forced-redraw timings include
RAF scheduling and gl.finish, not GPU execution time alone. A second `--animated`
run uses default existing steam and records RAF timing/draw counts. Software and
hardware results are separate local JSON files in the gallery directory.

Hardware was available: headless installed Edge, ANGLE D3D11 on NVIDIA GeForce
RTX 5070 Ti. Before/after forced-redraw medians were ~6.2–6.3 ms (p95 ~6.4–6.5);
default steam/bloom RAF medians also ~6.2–6.3 ms at both DPRs and both times.
No material regression was detected by this scheduling-limited measurement.
It is evidence for this GPU only, not a low-end-device or pure GPU-time claim.
The hardware night screenshot was inspected alongside the software output.

SwiftShader isolated medians were ~16.5–17.5 ms forced and ~16.7 ms animated,
but high-DPR tail latency remains poor. Animated DPR1.5 dusk p95: baseline
166.7/166.7 ms, current 166.7/216.7 ms; night: baseline 200/199.9 ms, current
116.7/166.6 ms. Parallel full-suite software capture also recorded median100 ms.
Different sampling/concurrency conditions must not be presented as a speedup
over the previous session's 50/67 ms figures. The software path still stutters;
there is no consistent doubling in this isolated comparison, but no claim of
universally solved software performance. All sampled WebGL errors were zero.

## Limits and stage decision

The lamp is more spatially credible: near-field objects respond, the desk tail
recedes and the face is not a lamp key. It remains a stylized 2D approximation;
there is no real light transport through a vase or reliable inter-object shadow.
Some painted highlights still disagree with dynamic light, especially white
cloth, cup rim and hair. The bright right-page core can still read as an authored
local field on close inspection, though the whole-desk orange overlay is reduced.

Code-only remaining gains are small localized calibration/asset-registration
improvements, not another large jump from more shader layers. True depth,
occluders and neutral reflectance cannot be reconstructed reliably this way.
Recommend freezing the current lighting core after human review, keeping defect
fixes open. It has the technical prerequisites for a later blink/breathing phase,
but that should begin only after this visual baseline is accepted. This session
stops at lighting; no next-stage animation is started.
