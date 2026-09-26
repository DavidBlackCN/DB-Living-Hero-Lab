# Character Lighting Core — human review candidate

The previous R6.5 and R6 Final notes describe superseded local face fixes. This pass replaces those shader branches with a shared Sun/Moon field for the figure. It does not change the frozen Base, Normal v3, R5 material asset, sky plates, `lightingFor`, `moonDirectionFor`, 24H controller, Post, Blink, Breathing, Hair Motion, or Leaves.

## Cause and replacement

The old Dawn path independently altered the face plane, both eyes, skin below each iris, left hair, garment shadows, bang boundary, chin, and shirt folds. Night separately added face, eyes, under-eye, and hair fills. Those local terms accumulated over the broad Normal band and produced inconsistent face and clothing light.

The new Scene Lighting path uses the existing solar vector, independent Moon vector, key/ambient colors and strengths, broad Normal, and continuous twilight weights. All character regions share that directional field:

- **Face and eyes:** one broad, soft receiving plane. The registered skin mask and two soft eye material regions select the same face response. There is no eye or under-eye light source. The frozen painted fringe and facial details provide contact cues; low-Sun face contrast is kept gentle.
- **Hair:** the same Sun/Moon receiving side with stronger broad volume than skin. The R5 daylight crown sheen and a narrow, flow-aligned lunar edge remain, at lower Night energy. There is no Dawn left-hair lift.
- **Clothing:** white sleeves, vest, and skirt use the same key direction with stronger structural response. The dark vest receives a little more lunar key while white fabric retains its Base folds. No separate shirt-fold multiplier remains.
- **Accessories:** the registered head-mass region covers the hat, flower, and ribbon outside face/hair; it receives the same field with a restrained gain. The book and smaller details retain the shared scene key.

Solar character contrast gains are `0.25` face, up to `0.76` hair, `0.58` clothing, and `0.50` head accessories. Dawn scales this directional separation to `0.54` and blends all character materials toward a softer key; the face blends farther toward `0.53` diffuse. Noon receives essentially the original response. Dusk keeps a stronger warm side and compresses bright iris glints across both eyes, without the prior screen-left white-eye patch.

Night replaces the character's residual solar key with a single cool Moon key. Its normalized receiving value is `0.34 + 0.30 × (Moon band − 0.5) + 0.38 × lateral side`, with soft limits. Material gains are `1.00` face, `1.08` hair, `1.12` general clothing, `1.30` vest, and `0.78` head accessories. The Moon's direction moves across the figure; normalizing its receiving mean prevents the face from brightening strongly after 22:00. Continuous Sun-energy handoffs fill the evening and pre-dawn gaps without changing the global lighting or sky curves.

## Iteration and review

Seven internal rounds were used: (1) remove local patches and install the common field; (2) soften morning reception and raise the lunar plane; (3) improve face/vest Night readability; (4) bridge the pre-dawn energy dip; (5) normalize the moving lunar response; (6) bridge the evening dip; (7) include the full registered head-hair mass in the Hair response. The final review images are:

- [Four full frames](character-lighting-core/final/four-full-contact.png) and [four head crops](character-lighting-core/final/four-head-contact.png)
- [Dawn before/after](character-lighting-core/final/dawn-before-after.png), [Noon before/after](character-lighting-core/final/noon-before-after.png), [Dusk before/after](character-lighting-core/final/dusk-before-after.png), [Night before/after](character-lighting-core/final/night-before-after.png)
- [Eyes and under-eye, 2×](character-lighting-core/final/eye-detail-before-after-2x.png) and [twilight head contact](character-lighting-core/final/transition-contact.png)

Individual clean full and head PNGs for 06:30, 12:00, 17:30, and 22:00 are in [`character-lighting-core/final/`](character-lighting-core/final/). The captures hide only the debug panel and disable motion so the lighting can be compared without changing the production UI or animation implementation.

The 15-minute [24H audit](character-lighting-core/round7-24h/luminance-15min.csv) and [hourly contact](character-lighting-core/round7-24h/hourly-contact.png) show no new phase discontinuity. Evening face minimum is `0.03817` linear luminance versus `0.03884` at 22:00. The daylight artwork maximum (`0.21973` at 12:45) remains within `0.00003` of Noon. The [00:00](character-lighting-core/final/00h-head.png) and [24:00](character-lighting-core/final/24h-head.png) head captures are pixel-identical. Minute-step captures around Dawn, Dusk, 20:00, and 22:00 show no hard cut.

At Night the full artwork luminance is `0.02462` at 22:00 and `0.02484` at 02:00; the slowly moving Moon changes the face's receiving side without a visible whole-scene late-night rebound. Final checks passed: `pnpm build`, `pnpm typecheck`, `python scripts/validate_post.py`, `python scripts/validate_lighting_detail.py`, `python scripts/validate_hair_motion.py`, and `python scripts/validate_blink_normal.py`. The motion check includes Base/Lit Blink, shared Normal UV, background protection, and visibility/reduced-motion behavior. No GPU timing claim is made.

Remaining limits are the painted 2D Base under-eye color and fixed Normal v3: neither can produce truly projected fringe shadows or physical cast shadows. The small frozen Sky edge residual also remains. These are visible at close zoom but do not create a new local lighting patch. R7 and left-side lamps are outside this pass.
