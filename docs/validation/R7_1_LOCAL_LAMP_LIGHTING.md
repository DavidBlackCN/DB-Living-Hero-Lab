# R7.1 Local Lamp Lighting — review candidate

R6 at `3241d76` is the frozen visual baseline. This pass adds only the two
existing left-corridor lanterns and their local warm reception. Sun/Moon,
Character Lighting, Sky, Post grading, and motion parameters remain unchanged.

## Registration and lighting

The lantern glass centers are approximately `(52, 146)` and `(159, 262)` in
the 1672×941 top-left Artwork Space. The generated
[`lamp-source-mask.png`](../../public/assets/hero/lighting/lamp-source-mask.png)
uses R/G for their separate glass panes, excluding the dark metal frames.
[`lamp-influence-mask.png`](../../public/assets/hero/lighting/lamp-influence-mask.png)
uses the same channels for two soft corridor reception fields. The second
field reaches the adjacent vine and column; both masks are zero from x=390
rightward and y=548 downward. They cannot reach the figure, Sky, or distant
building. [`generate_lamp_masks.py`](../../scripts/generate_lamp_masks.py)
recreates the registered assets deterministically.

The Lit shader adds three contributions under one weight:

1. Warm amber glass emissive enters the existing linear HDR Scene and Bloom.
   Lantern frame pixels remain dark; the far lamp is slightly dimmer and
   warmer.
2. Nearby stone and ivy receive warm light using the fixed influence channel
   and a lamp-to-pixel vector against the existing broad Normal. This is
   visible with Bloom disabled.
3. A small, tight air-glow term surrounds the glass. It does not illuminate
   the rest of the image.

The Surface term is applied before the existing relight blend; emissive and
glow are then added to the linear Scene. Lamps OFF sets the weight to zero and
restores the frozen R6 Night frame exactly. No runtime image threshold, new
animation loop, character patch, or independent Post pass was added.

## Time and debug

`lampWeightFor()` eases in from 17:15 to 18:30, holds through Night, then
eases out from 05:15 to 06:30. The two lamps share the curve, with fixed small
color/strength differences. The function is continuous at 00:00/24:00.
Debug controls expose Lamps on/off, strength, and source/influence mask views.
The mask view bypasses Post for inspection. Static time continues to use the
current on-demand WebGL draw policy, with no lamp RAF.

## Review images

- [22:00 full frame](r7-1-lamps/final/22h00.png),
  [Lamps OFF/ON](r7-1-lamps/final/22h00-off-on.png),
  [lamp corridor crop OFF](r7-1-lamps/final/22h00-lamps-off-crop.png) /
  [ON](r7-1-lamps/final/22h00-lamps-on-crop.png)
- [Bloom OFF/ON](r7-1-lamps/final/22h00-bloom-comparison.png),
  [source debug](r7-1-lamps/final/lamp-source-debug.png),
  [influence debug](r7-1-lamps/final/lamp-influence-debug.png)
- [Dusk ignition](r7-1-lamps/final/dusk-transition.png),
  [Dawn extinguish](r7-1-lamps/final/dawn-transition.png),
  [12-point timeline](r7-1-lamps/final/timeline-contact.png),
  [24H luminance](r7-1-lamps/final/luminance-15min.csv)
- [Dawn/Noon/Dusk/Night](r7-1-lamps/final/four-phase-contact.png)

At 22:00 the corridor gains 10.48 mean 8-bit RGB levels relative to Lamps
OFF. The selected vine/column region gains about 5.85 levels, while the figure
and distant Sky are pixel identical. Bloom OFF still shows local surface
lighting. All four Lamps OFF anchors are pixel identical to R6 captures;
Noon is identical with Lamps ON as well.

## Verification and performance

`validate_local_lamps.py` checks asset dimensions/bounds, the 12 specified
times, exact four-phase R6 OFF and Noon ON frames, Bloom-independent surface lighting,
figure protection, monotone twilight weights, exact midnight wrap, Play
advancing through lamp fade, and a Blink/Breathing/Hair/Leaves smoke test.
The existing 15-minute 24H audit
passes its brightness and wrap checks. `validate_lighting_detail.py` and
`validate_blink_normal.py` pass. `pnpm typecheck` and `pnpm build` pass.

Two RGBA8 registered textures use roughly 12.0 MiB (12.6 MB) of uncompressed GPU
storage total. The shader uses two extra samplers and two local Normal
receivers; it adds no draw pass, periodic timer, or high-frequency RAF.

Legacy `validate_post.py` still compares Post OFF against R5 screenshots and
fails at Dawn because the accepted R6 lighting differs from R5. The old
Breathing validator likewise compares against R2B pixels; its active torso,
face, and stone locality checks passed before that stale comparison. The
Hair validator passed motion/Normal checks but its one-second Blink visibility
wait timed out. The R7.1 browser regression performs the relevant current R6
OFF, Bloom, and motion checks directly.

Await human visual acceptance before proceeding to R7.2.

## R7.1 source registration correction

The frozen Base shows three distinct glass faces on **each** lantern. The
initial source asset covered only two per lamp and missed the narrow left
face. `generate_lamp_masks.py --source-only` now registers six perspective
polygons in the same 1672×941 artwork coordinates: near lamp in R, far lamp
in G. The metal mullions and lantern caps/base remain outside the source.
The existing influence asset, local surface response, strength, timing,
Bloom, and R6 lighting were left unchanged.

The Debug Panel now has a local Hide/Debug visibility toggle. It keeps the
same mounted controls and renderer; the 22:00 time and Lamps state survive
the toggle, and Play continues while the panel is hidden.

Review: [near Base / source / overlay](r7-1-lamps/source-registration/near-base-source-overlay.png),
[far Base / source / overlay](r7-1-lamps/source-registration/far-base-source-overlay.png),
[source debug](r7-1-lamps/source-registration/lamp-source-debug.png),
[Night 22:00 unobstructed](r7-1-lamps/source-registration/22h00-panel-hidden.png),
[panel visible](r7-1-lamps/source-registration/22h00-panel-visible.png),
[Lamps OFF / ON](r7-1-lamps/source-registration/22h00-off-on.png).
The yellow overlay in the close crops marks the source areas; runtime debug
uses red/green to distinguish the two texture channels.

`validate_local_lamps.py` now asserts three separated panes per lamp and
checks panel visibility, retained renderer/time/Lamps state, and Play while
hidden. `pnpm typecheck`, `pnpm build`, and the lamp validator pass. Lamps OFF
remains pixel identical to frozen R6 at all four anchors, Noon ON is identical,
and 00:00/24:00 remains exact. Await human acceptance; R7.2 has not started.

### Glass-edge correction

The near lamp's right pane still stopped short of its outer and lower glass
edge, while the far lamp's left narrow pane reached into the metal rim. The
registered source polygons now extend the near right face by two to three
source pixels and inset the far left face by three pixels. The other
four faces and the influence mask are unchanged. The validator checks both
specific edges as well as three separated panes on each lantern.

[Near source before/after](r7-1-lamps/source-correction/near-mask-before-after.png),
[far source before/after](r7-1-lamps/source-correction/far-mask-before-after.png),
[22:00 rendered lanterns before/after](r7-1-lamps/source-correction/22h00-lanterns-before-after.png),
and [22:00 full frame](r7-1-lamps/source-correction/22h00-panel-hidden.png)
show the small registration correction. `pnpm typecheck`, `pnpm build`, and
`validate_local_lamps.py` pass again. Lamps OFF and Noon remain pixel identical
to R6; the 24H lamp weight and midnight wrap remain unchanged.
