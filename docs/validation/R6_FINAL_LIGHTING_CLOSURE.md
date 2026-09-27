# R6 final lighting closure — review candidate

This pass makes a small Scene Lighting adjustment on the existing Character
Lighting Core. It does not change the Sun/Moon directions, light or Sky time
curves, frozen artwork/Normal, Post, or motion systems.

## Diagnosis and changes

The pale building plane beside the black rose weakens when directional shading
is disabled. It is a broad-Normal architectural Moon response, not a Sky seam
or Bloom halo. Its cool Moon addition was too strong beside the character.
The shared architectural Moon coefficient was reduced from
`(0.34, 0.51, 0.88)` to `(0.22, 0.33, 0.57)`. This changes the Scene Lighting
contribution before Post; it adds no local darkening mask. The building's
painted light plane remains, but it no longer competes as strongly with the
figure. The rose-side building crop averages about 1.7 display RGB levels
lower; the prominent adjacent column is about 8.4 levels lower.

Night character reception stays on the same broad Normal and independent Moon
vector. The receiving-band contrast rose from `0.82` to `0.88`; face inherits
`0.32` rather than `0.25` of that contrast around its soft midpoint. Clothing,
vest, and hair material gains rose from `1.20/1.45/1.35` to
`1.26/1.50/1.40`. These are small shared-key changes, with no cheek, eye, or
other local fill. Hair sheen is unchanged.

At Dawn the existing face-wide morning blend rose from `0.76` to `0.80`, and
the face solar-band gain eases from `0.25` to `0.21` only as the continuous
morning weight rises. This softens bangs-to-face direction without adding an
eye patch or lifting the whole frame. Noon and Dusk are pixel identical to
the preceding candidate; Dawn full-frame mean absolute difference is 0.006
8-bit RGB level.

## Visual review

- [Four phases](r6-final-closure/final/four-phase-contact.png):
  [Dawn](r6-final-closure/final/dawn-full.png),
  [Noon](r6-final-closure/final/noon-full.png),
  [Dusk](r6-final-closure/final/dusk-full.png),
  [Night](r6-final-closure/final/night-full.png)
- [Night figure before/after](r6-final-closure/final/night-figure-before-after.png)
- [Rose-side building before/after](r6-final-closure/final/night-rose-background-before-after.png)
- [Dawn head before/after](r6-final-closure/final/dawn-head-before-after.png)

The Night building still carries some bright pigment from the frozen Base, and
the 2D Normal cannot create true cast shadows. At normal Hero size neither
reads as a separate character-local light. The face and sleeve remain readable
without a new grey/dark overlay.

## Continuity and checks

The 15-minute 24H audit passed its daylight peak, evening minimum, and
midnight wrap checks. The five-minute Dawn/Dusk audit retained the smooth
handoff from the preceding twilight correction (largest face-region steps
near sunrise: 5.13 and 4.95 mean RGB levels). Night 22:00 face luminance is
0.04351; the evening minimum is 0.04419. Noon/Dusk fixed frames are exact
pixel matches to the previous candidate. `pnpm build`, `pnpm typecheck`, and
the focused Lighting Detail regression passed.

Audit data: [24H, 15-minute steps](r6-final-closure/final/luminance-15min.csv)
and [Dawn/Dusk, five-minute steps](r6-final-closure/final/twilight-5min.csv).

R6 is ready for human freeze review. No R7 work was started.
