# Night architecture Moon-direction correction

Baseline: `55d995c`, branch `v2`. This follow-up changes only the scene shader's Night architecture receiving logic. Await human visual review.

## Root cause

The strip beside the black rose was not a dedicated static brightening asset. The blue channel of `hair-motion-mask.png` deliberately includes a little background to keep whole-head UV deformation continuous. The shader also reused that channel as **accessory material coverage**. Pale tower pixels at artwork `(1035,180)` and `(1035,250)` have B values 252 and 255 respectively: these building pixels therefore received the character/accessory Moon fill instead of the building key. That incorrect ownership explains the head-adjacent illumination.

The remaining architecture chain compounded it: solar-direction diffuse remained active underneath a small additive Moon contribution, with a screen-position `moonSide` bias. Frozen Normal v3 is nearly neutral on the distant tower planes, so the Moon contribution alone could not clearly reverse the painted sides.

Post, Sky and Lamps OFF comparisons did not remove the strip. Directional OFF reduced it. [Initial pass isolation](night-architecture-moon/diagnostics.jpg), [Base crop](night-architecture-moon/base-column.png), [Normal crop](night-architecture-moon/normal-column.png).

## Changes

- Registered pale masonry inside the head-motion envelope is excluded from **Night character material receiving**. The motion texture and UV deformation are unchanged; dark rose/ribbon and brown hair remain in their existing character path.
- Removed the architecture `moonSide`, old XY-only `moonBand`, and constant additive Moon term.
- Architecture now hands direct illumination from Sun to Moon through the existing continuous Night/twilight weight. It uses `dot(receiverNormal, moonDirection)` and Moon elevation gain. No head-centered brightness or darkening layer is added.
- Four distant towers use registered visible-plane orientations, sharing the same receiving rule. This supplements their almost-flat frozen normals without editing Normal v3. Other architecture uses its broad painted Normal; russet foliage is excluded from the stone-plane correction.
- A uniform, quiet Night sky ambient remains: existing ambient × 0.88. The cool directional key is × 0.22, with elevation gain 0.55–1 and a soft receive band. This is scene illumination before Post, not a local suppression patch.

The geometry registration describes **surface orientation**, not a fixed bright strip. All four towers obey the same moving Moon vector. The original Base's stone reflectance and painted value differences are retained.

## Direction and time

`moonDirectionFor()` and all time curves are unchanged. Positive Moon X means a source on image-right; negative X means image-left. As requested, when the Moon is on image-left the left-facing tower plane receives more light and the right-facing plane retreats.

| Time | Moon azimuth / elevation | Source side | Left/front to right/side RGB ratio* |
| --- | --- | --- | --- |
| 20:00 | 35° / 12° | Right, low | 0.766 |
| 22:00 | 49° / 40° | Right, higher | 0.905 |
| 00:00 | 81° / 54° | High, near center | 1.080 |
| 02:00 | 116° / 49° | Left | 1.321 |
| 04:30 | 144° / 19° | Left, low | 1.326 |

*Fixed stone samples at artwork y=130–280, x=950–980 versus x=1025–1045, after the normal display chain. These include Base pigment and atmosphere, so they are comparative display values, not physical illuminance. Right side is brighter early; left side becomes brighter late.

At fixed 22:00, reversing **only architecture Moon X** switches the illuminated plane with mean crop RGB difference 15.17. Character Moon, exposure, Sky and time stay fixed in this audit. The reversal is a test-only shader interception, not a runtime feature.

## Review images

- [Three-time plane direction comparison](night-architecture-moon/night-plane-directions.jpg)
- [Five Night times, full-frame contact](night-architecture-moon/night-moon-contact.jpg)
- Full frames with Moon directions: [20:00](night-architecture-moon/20h-labelled.png), [22:00](night-architecture-moon/22h-labelled.png), [00:00](night-architecture-moon/00h-labelled.png), [02:00](night-architecture-moon/02h-labelled.png), [04:30](night-architecture-moon/04h30-labelled.png)
- [22:00 full before / after](night-architecture-moon/22h-full-ab.jpg)
- [Tower before / after at all five times](night-architecture-moon/column-before-after.jpg)
- [Direction-only isolation](night-architecture-moon/direction-isolation-ab.jpg)

## Verification

Commands: `pnpm typecheck`, `pnpm build`, `python scripts/audit_architecture_moon.py`, `python scripts/validate_atmosphere.py docs/validation/night-architecture-moon --mode regression` — passed.

- Dawn 06:30, Noon 12:00 and Dusk 17:30: exact full-frame equality against baseline (maximum RGB difference 0).
- 00:00 / 24:00: exact equality.
- Face material core: maximum RGB difference 1 at Night, including the existing Post chain; no face-light model or material asset change.
- Blink, Head/Hair/Breath motion, Lamps, Leaves, Post, hidden tab, reduced motion, static quality, context restore and resize checks passed.
- Actual WebGL2 renders at 1080p, 1440p, 4K and mobile: no GL errors; DPR=3 mobile retains the existing cap of 2.
- Existing 10-minute transition audit: max mean RGB change 11.129 for 04:30–07:00 and 5.032 for 16:30–20:00. These values report ordinary continuous time variation, not a proof of perceptual acceptance. The new handoff uses existing smooth twilight scalars and adds no time threshold.
- No new texture, framebuffer, sampler, animation loop or draw pass. Four small receiver-geometry calculations are added within the existing fragment pass. This round did not run a separate GPU timing benchmark.

Results: [render audit](night-architecture-moon/audit-stats.json), [lifecycle / continuity](night-architecture-moon/regression-stats.json).

Known limit: this remains painted 2D broad directional lighting, not cast-shadow simulation. The frozen Base's inherent light/dark stone paint remains visible; it is no longer reinforced by head-motion material spill or a fixed Moon-side contribution. Stop for human review; no further stage begins.
