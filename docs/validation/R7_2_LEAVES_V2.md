# R7.2 — Leaves v2 review candidate

## Scope and result

The four accepted transparent leaf masters and the Canvas2D overlay remain in place. Desktop and mobile counts remain **18** and **10**. R6 lighting, Sky, Post, R7.1 lamp masks/timing/surface light, and Blink/Breathing/Hair were not changed. The existing time-of-day CSS grade remains the outer leaf tone adjustment.

| Depth | Desktop / mobile | Visible size | Fall speed | Opacity multiplier |
| --- | ---: | ---: | ---: | ---: |
| Background | 3 / 2 | 18.2–27.3 CSS px | 7.7–15.4 CSS px/s | 0.66 |
| Midground | 13 / 7 | 26–46 CSS px | 11–22 CSS px/s | 1.00 |
| Foreground | 2 / 1 | 51.6–60 CSS px | 14.9–29.7 CSS px/s | 0.83 |

Size follow-up: the original midground average of 22.5 CSS px looked smaller than the distinct single leaves painted on the railing and nearby vines (roughly 35–45 artwork pixels). Midground now averages 36 CSS px; with the normal desktop artwork scale this is close to those painted leaves. A few background leaves remain smaller and two foreground leaves may be larger. Counts, speed, and opacity were not raised.

Every leaf has an independent phase, drift, sway rate, turbulence, lift pulse, rotation rate, and lifespan. A fixed seeded random stream makes runs reproducible; each respawn consumes new values rather than replaying a synchronized batch. The common gust is weaker than v1. Short lift pulses and oscillating fall speed break up a constant diagonal path without creating strong wind.

The face guard is a **soft artwork-space ellipse**, centered at source `(1150, 242)` with radii `(112, 98)`. Leaves approaching it are steered gently sideways and fade continuously toward its center. Large foreground leaves also reject births likely to cross the face. The guard leaves the hat and surrounding hair available for occasional small leaves; it does not clip at a rectangle.

At Night, a leaf inside the left corridor receives a very small warm blend weighted by the existing `lampWeight` and a fixed artwork-space approximation of the two lamp influence fields. It cannot reach the figure or distant Sky. Normal/night leaf color still comes from the accepted outer time-of-day grade. The warm sprite is generated once on load from each unchanged master; no Canvas filter runs in the animation loop. The runtime draws the 256px downsampled sprites at their existing on-screen sizes.

## Visual review

Four full frames: [Dawn](r7-2-leaves/final/dawn.png) · [Noon](r7-2-leaves/final/noon.png) · [Dusk](r7-2-leaves/final/dusk.png) · [Night](r7-2-leaves/final/night.png)

Size A/B at identical seeded positions: [Noon before](r7-2-leaves/final/size-before-noon.png) · [Noon after](r7-2-leaves/final/noon.png) · [Night before](r7-2-leaves/final/size-before-night.png) · [Night after](r7-2-leaves/final/night.png).

25-second normal-speed captures: [Noon MP4](r7-2-leaves/final/noon-25s.mp4) · [Dusk MP4](r7-2-leaves/final/dusk-25s.mp4) · [Night MP4](r7-2-leaves/final/night-25s.mp4)

Six-frame motion contacts: [Noon](r7-2-leaves/final/noon-motion-contact.png) · [Dusk](r7-2-leaves/final/dusk-motion-contact.png) · [Night](r7-2-leaves/final/night-motion-contact.png)

[Depth and face debug](r7-2-leaves/final/depth-face-debug.png) uses blue/green/orange boxes for background/midground/foreground and shows the soft face region boundary. Lamp A/B is captured on the same paused frame: [tint off](r7-2-leaves/final/night-leaf-lamp-tint-off-4x.png) · [tint on](r7-2-leaves/final/night-leaf-lamp-tint-on-4x.png) · [amplified difference audit](r7-2-leaves/final/night-leaf-lamp-tint-audit-32x.png). The 32× audit deliberately exaggerates a subtle effect; it is not the actual display strength.

## Verification

`python scripts/validate_leaves_v2.py docs/validation/r7-2-leaves/final --seconds 25` captured the Lit composition at 960×540 for motion and 1440×900 for fixed frames. After the size adjustment, the instrumented leaf layer used **27.2 / 27.2 / 27.2 FPS** in Noon / Dusk / Night under headless Edge software WebGL, below the 30 FPS cap. In each 27-second measured window, bright leaf coverage at the eye center produced **0 obvious overlap events**. The six-frame contacts and full videos show independent positions and rotations, with no visible whole-field reset. Draw count remains 18 on desktop and 10 after mobile resize. Hidden-tab RAF pause, reduced motion, Static quality, resize, integrated Blink preview, and Breathing/Hair re-enable checks passed in the same validator.

The lamp leaf response is intentionally difficult to see at normal size: the stationary A/B changed 495 pixels, by at most 3 RGB levels, in the left corridor. It adds a mild tint to passing leaves without making them emissive. The four original leaf PNGs are unchanged.

`pnpm typecheck`, `pnpm build`, and `git diff --check` passed.

## Known limits

The leaf field is still a 2D overlay, so a rare leaf can cross a shoulder, hand, hat, or book. The face guard prioritizes the eyes and expression rather than forbidding every character overlap. A fixed-seed page reload starts at the same initial arrangement; respawns and noncommensurate leaf rhythms prevent short-loop repetition during a continuous viewing session. Software-rendered headless FPS is a reproducible regression metric, not a hardware-wide guarantee.
