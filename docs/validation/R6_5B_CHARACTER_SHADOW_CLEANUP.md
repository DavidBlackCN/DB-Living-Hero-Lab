# R6 character shadow cleanup — human review candidate

This is a limited follow-up to R6.5 directional shading. It changes only the **character's Scene Lighting response** at low sun. The existing sun curve, architecture shading, R5 material mask/asset, R6 Post, Sky, motion, Blink, and Leaves remain in place. No left lamps, cast-shadow system, new controls, or later stage work were added.

## Cause and correction

R6.5's broad solar band and horizontal painted falloff were multiplied across the whole frame. They made the architecture's morning/evening direction legible, but on the character they also darkened broad areas of face, sleeves and vest in one sweep. The face looked gray at Dawn and the outfit looked tinted at Dusk. The Base illustration already contains useful occlusion cues in the bangs, chin, collar and fabric folds; the additional light should follow them rather than flatten them.

- Existing registered R5 face mask and source-space garment regions localize the correction. Soft pigment guards identify the white sleeves and brown vest. The wide scene contrast stays at `1.10`; upper garments use `0.66` and the face `0.35` of the centered Normal band, with the composition-wide side tint removed from these surfaces.
- A small neutral skin fill affects only the face's unlit side at low sun. It keeps both eyes and the expression readable without lifting Night or changing the time curve.
- A narrow mask-boundary shadow follows skin immediately below the bangs (`11` source-pixel upward comparison, restricted to upper forehead). A complementary boundary and skin-color guard catches the chin-to-neck contact. Eye/cheek holes in the R5 mask are excluded by source-space height limits.
- White-shirt folds receive a small extra shadow only where the frozen Base already painted a darker crease. No detached oval shadow is drawn across the sleeve. The existing R5 hair sheen and iris reflection remain unchanged.

All additions are scaled by the existing continuous low-sun response. Dawn retains its cool fill, Dusk retains its warm key and stronger lateral read, Noon receives almost none of the correction, and Night receives none. There are no phase switches.

## Four visual iterations

1. Removed the broad side tint from face/upper garments and reduced their band gains. The Dawn face and white sleeves became noticeably cleaner.
2. Added a small unlit-face fill and Base-guided sleeve-fold contrast. This kept fabric shape without restoring the whole-sleeve tint.
3. Used the top edge of the registered face mask for a narrow bang-to-forehead contact shadow; visual inspection found no eye or cheek blotches.
4. Raised that contact shadow slightly and added a guarded chin-to-neck contact. This is the final candidate. [Iteration contact](r6-character-shadow/final/iteration-contact.jpg).

## Review images

| Phase | Final static frame | Character review |
| --- | --- | --- |
| Dawn 06:30 | [Dawn](r6-character-shadow/final/dawn.png) | [Before/after portrait](r6-character-shadow/final/portrait-before-after.jpg) |
| Noon 12:00 | [Noon](r6-character-shadow/final/noon.png) | [Four-phase contact](r6-character-shadow/final/four-phase.jpg) |
| Dusk 17:30 | [Dusk](r6-character-shadow/final/dusk.png) | [Before/after face enlarged](r6-character-shadow/final/face-4x.jpg) |
| Night 22:00 | [Night](r6-character-shadow/final/night.png) | [Full composition](r6-character-shadow/final/combined-contact.jpg) |

The before images in the portrait and face contacts are the committed R6.5 `8f658bb` result. At Dawn, the broad gray face/shirt shadow recedes while a narrow fringe still follows the bangs and chin. At Dusk, the warm receiving side remains directional, while the eye, cheek, shirt and vest no longer take one large tinted shadow. The 4× face crop is the primary manual review target. Remaining painted shadow shape is limited by the frozen 2D Base and Normal; this is a relight polish, not physical cast shadow.

## Regression

- Relative to the R6.5 static frames, mean absolute RGB change in the artwork is `0.55/255` at Dawn and `0.43/255` at Dusk; on the face crop it is `5.67/255` and `4.36/255` respectively. The effect is concentrated on the character rather than the background. Noon artwork change is `0.008/255` and Night is **pixel-identical**.
- The 97-frame [24H audit](r6-character-shadow/24h-audit/hourly-contact.png) passed. Noon artwork luminance is `0.21972` with daylight maximum `0.21975` at 12:45. Night 22:00 remains unchanged; the evening face minimum still exceeds the Night face value.
- Static four-phase and [full composition](r6-character-shadow/final/combined-contact.jpg) previews were checked. `pnpm build`, `pnpm typecheck`, `validate_post.py`, `validate_lighting_detail.py`, `validate_time_controller.py`, `validate_blink_normal.py`, `validate_hair_motion.py`, and `validate_breathing.py` passed. The prior baseline scripts retain their directional-OFF setup where needed.

This candidate is ready for human review. R7 and the left-side lamps have not started.
