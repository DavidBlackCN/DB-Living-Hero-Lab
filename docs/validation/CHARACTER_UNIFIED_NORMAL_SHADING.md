# Unified character shading — four-phase review

This review builds on the Character Lighting Core. The Sun/Moon vectors, color and time curves, frozen Base/Normal, Sky repair assets, Post, Blink, Breathing, Hair Motion and Leaves are unchanged. Only the Scene Lighting response was adjusted.

## Diagnosis and correction

The previous Night character receiving term used a `1.00 × characterPixel.x` side field but only `0.48 × broad-Normal band`. This made broad left/right placement dominate hair and garments. An initial attempt to use full XYZ Normal produced dark, hard lower-face and sleeve patches; that trial was rejected. The final response uses the same Moon vector with the broad Normal **XY slope**, a wide soft band, and an `0.08 ×` position bias. Across its bounded range, the band can contribute roughly `±0.41` to receiving strength while the position bias contributes at most `±0.036`. The normal field therefore controls local strands and folds.

Face remains in that shared field. It reduces the vertical Normal response and uses a wider band plus 25% of the full character contrast around a readable midpoint. No eye, cheek, under-eye or face-only Moon light was added. Hair, sleeves, vest, skirt and accessories use the same Moon direction with material gains; the narrow hair sheen remains an additive accent after the main key. The floor on the Moon diffuse term prevents away-facing dark fabric from collapsing to pure black.

For low Sun, Hair and Clothing broad-Normal band gains rose from `0.76/0.58` to `0.90/0.72`. Dawn retains its existing `0.54` softening and shared morning fill; Dusk keeps the stronger warm direction; Noon is effectively unchanged. The existing Dusk iris highlight compression remains. No historical face patches were reintroduced. The superseded dominant Night side field was removed from the character response. The separate small scene bias remains only for flat architecture.

## Head-left background

At the black rose, the pale vertical edge persists with Sky and Post disabled but weakens clearly when Directional Shading is disabled. It is a Moon-facing painted building surface, not a sky seam, bloom halo or character-mask spill. The architecture Moon key was reduced from `0.45` to `0.34` globally, retaining the building's directional response while quieting this edge. No local dark patch was applied.

## Review images

- Full frames: [Dawn](character-unified-normal/final2/dawn-full.png), [Noon](character-unified-normal/final2/noon-full.png), [Dusk](character-unified-normal/final2/dusk-full.png), [Night](character-unified-normal/final2/night-full.png)
- Head crops: [Dawn](character-unified-normal/final2/dawn-head.png), [Noon](character-unified-normal/final2/noon-head.png), [Dusk](character-unified-normal/final2/dusk-head.png), [Night](character-unified-normal/final2/night-head.png), [four-head contact](character-unified-normal/final2/four-head-contact.png)
- [Night figure before/after](character-unified-normal/final2/night-figure-before-after.png), [Night head before/after](character-unified-normal/final2/night-head-before-after.png), [rose-side building before/after](character-unified-normal/final2/night-rose-background-before-after.png), [directional off diagnostic](character-unified-normal/final2/night-no-direction-rose-background.png)
- [24H luminance, 15-minute steps](character-unified-normal/final2-24h/luminance-15min.csv), [hourly contact](character-unified-normal/final2-24h/hourly-contact.png)

Eight capture rounds were used to reject the XYZ hard-shadow trial, soften face response and balance material gains. Compared with the starting captures, full-frame mean absolute pixel differences are `0.075` Dawn, `0.003` Noon, `0.141` Dusk, and `3.198` Night. The daytime changes are confined to low-Sun character response; the Night improvement comes from Normal-driven key reception, not exposure or Sky changes.

The final 24H scan passes the existing daylight-peak, evening minimum and 00:00/24:00 checks. Night face luminance is `0.04361` at 22:00 versus an evening minimum of `0.04411`; there is no discrete twilight switch. `pnpm build`, `pnpm typecheck`, and `validate_lighting_detail.py` passed. The fixed 2D Normal limits true cast shadows; dark hair and vest retain their painted base contrast. At normal viewing size the figure reads as one light field, with the face deliberately softer than garments.
