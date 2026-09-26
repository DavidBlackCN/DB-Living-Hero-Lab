# R6 Final — Head Lighting Polish

Status: local implementation and visual review complete; awaiting human acceptance. No R7 work.

## Scope and result

Only the head lighting branch in `hero.frag.glsl` changed. Base, Normal, masks, lighting curves, Sky RGB/timeline, body lighting, background, motion and R6 Post remain unchanged. The reference screenshots informed face/eye readability and shadow softness; their Moon direction was not copied.

- **Dawn:** the low-sun face Normal's dark receiving plane blends toward a soft local key only on the shadow side. Both eyes receive restrained painted-eye fill. Two feathered skin regions immediately below the irises soften the dark-circle effect without lifting lashes or the fringe. The existing forehead contact edge remains.
- **Noon:** no active shader branch changed. The before/after artwork is pixel-identical.
- **Dusk:** the generated iris glint is reduced at low sunset angles. A small local response compresses the brightest painted iris and screen-left eye white while leaving dark pupils, eyelids and warm facial side light intact. Pixels with red channel above 230 in the left-eye review crop fell from 588 to 457. The response is tied to the Directional Shading control, so disabling that layer still restores the R6 Post baseline.
- **Night:** a modest Moon-facing fill now clarifies the face planes. Painted eyes and the skin below each iris receive separate soft support, with the under-eye fill blended into the broader cheek/bridge fill rather than a bright oval. Nearby crown and face-side hair ribbons were reduced; lower long-hair motion and its lighting path were not changed.

All new weights use the existing continuous `dawnEase`, Moon envelope, solar angle and Directional Shading gain. No time anchors or global exposure changed. In the 1440×900 static WebGL2 captures, changed artwork pixels stayed inside the head review bounds; the rest of the artwork was pixel-identical. The full artwork mean changed only 85.690→85.763 at Dawn and 35.134→35.271 at Night.

## Review images

- [Final four-head contact sheet](r6-final-head/review/four-head-contact.png)
- [Dawn head before/after](r6-final-head/review/dawn-before-after.png)
- [Dusk head before/after](r6-final-head/review/dusk-before-after.png) and [eye 4×](r6-final-head/review/dusk-eyes-4x.png)
- [Night head before/after](r6-final-head/review/night-before-after.png)
- [Dawn/Night under-eye 4×](r6-final-head/review/dawn-night-under-eye-4x.png)
- [Morning and evening head transitions](r6-final-head/review/head-transition-contact.png)

Raw final head crops, four full frames and near-boundary captures are in [`r6-final-head/final/`](r6-final-head/final/). Static captures disabled Blink, Breathing, Hair Motion and Leaves to isolate the shading response.

## Continuity and regressions

The 06:29/06:30/06:31, 17:29/17:30/17:31, 19:59/20:00/20:01 and 21:59/22:00/22:01 head captures showed continuous changes, with no introduced step. 00:00 and 24:00 head crops were pixel-identical. The Night full-frame mean stayed within 0.14 RGB code values of the previous version, preserving the dark setting.

`pnpm build`, `pnpm typecheck`, `validate_post.py`, `validate_lighting_detail.py` and `validate_blink_normal.py` passed. The existing `validate_hair_motion.py` passed its mask/head motion/Normal assertions but twice missed a 115 ms Blink closure with a 1000 ms visible-locator wait. A separate mutation-observer check confirmed Lit + Hair + Blink closures at Dawn and Night. This is a short-window test timing limitation, not a detected rendering failure.
