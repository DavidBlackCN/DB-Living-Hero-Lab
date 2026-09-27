# Character Moon direction review

This pass continues the existing Character Lighting Core. It changes only the Night receiving response in `hero.frag.glsl`; the Sun/ Moon direction curves, exposure, ambient, Sky, Post, masks, Base/Normal, and motion systems are unchanged.

## Finding and change

The Night character key already shared one Moon vector, but its receiving value was confined to `0.10–0.70`: broad Normal contributed `0.30 × (band − 0.5)` and the side field only `0.38 × side`. The cool key therefore varied too little across hair, sleeves, vest and skirt, while the separate hair sheen could suggest more direction than the actual body illumination.

The same broad Normal and figure-wide Moon side field now span `0.06–0.86`, with band and side gains of `0.48` and `1.00`. A centered key response keeps average Night brightness close to the prior image while lifting the receiving side and reducing the opposite side. Face and eyes receive **52%** of that shared contrast, without a face-only light, cheek patch or under-eye term. Existing material gains and the narrow hair sheen remain. The change is multiplied by the existing continuous Moon handoff, so there is no new phase switch.

Two visual rounds were captured. Round 1 (`0.75` side gain, `0.62` key slope) was visible mainly in crops. Round 2 (`1.00`, `1.05`) makes the Moon side legible on the full figure while preserving facial expression and dark garment folds. Dawn, Noon and Dusk fixed-time captures are pixel-identical to the initial state. Night remains dark; the strengthened illumination belongs to the character rather than a whole-frame exposure change.

The pale stone/foliage edge to the image-left of the head was checked at 22:00 with Sky, Post and directional shading independently disabled. The stone face and its light edge remain when all three are off; disabling Sky actually reveals a brighter old sky behind the foliage. This is painted architecture/ambient reception, not a bloom halo or a leaking character mask. No local darkening or seam patch was added.

## Review images

- [Four full frames](character-night-direction/final/four-phase-contact.png) and [four head crops](character-night-direction/final/four-head-contact.png)
- [Night figure before/after](character-night-direction/final/night-figure-before-after.png), [Night full frame](character-night-direction/final/night-full.png)
- [Night head-left background](character-night-direction/final/night-head-left-edge.png), [Sky off](character-night-direction/final/night-no-sky-head-left-edge.png), [Post off](character-night-direction/final/night-no-post-head-left-edge.png), [Direction off](character-night-direction/final/night-no-direction-head-left-edge.png)
- [15-minute 24H luminance](character-night-direction/final/luminance-15min.csv) and [hourly contact](character-night-direction/final/hourly-contact.png)

The 15-minute audit passed: the daylight peak remains near Noon; the evening face minimum is `0.03819` versus `0.03779` at 22:00; 00:00 and 24:00 match. Night artwork luminance is `0.02578` at 22:00, `0.02404` at 00:00 and `0.02528` at 02:00, with no whole-frame late-night rebound. `pnpm build`, `pnpm typecheck`, `validate_lighting_detail.py`, and `validate_blink_normal.py` passed. Two older scripts stop at obsolete frozen-image assertions: `validate_post.py` compares current output against an R5 screenshot, and `validate_final_composition.py` compares it against an R2B screenshot. Both fail at Dawn, which this pass leaves pixel-identical to its starting point. The latter script rewrote six historical captures before the assertion; they were restored afterward.

The fixed 2D Normal/painted Base limits exact cast-shadow behavior. The dark vest's far side stays intentionally subdued but its fold structure remains visible. These limits are acceptable for this review; the face is clean and Hair/Clothing carry the stronger Moon direction.
