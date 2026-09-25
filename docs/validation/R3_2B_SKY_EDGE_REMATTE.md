# R3.2b Edge-aware Sky Rematte

Status: implementation complete; **awaiting human visual acceptance**. R3.2's one-pixel color-gated fringe was rejected because its before/after views were nearly indistinguishable.

## Cause and repair

The frozen Base contains antialiased sky mixed with warm leaf, branch, hat, and tower pixels. The R3.2 blue/light gate excluded many of these mixed pixels and some tiny connected sky gaps. The existing gate now supplies only a coarse seed. A 3–5 source-pixel trimap defines definite sky, definite foreground, and an unknown edge band. In that band, the generator projects each source color between its nearest local sky and foreground colors to estimate continuous sky alpha. Final edge alpha is not gated by a global blue/light test. A registered 1672×941, mostly transparent [override matte](../../public/assets/hero/sky/sky-edge-override.png) adds coverage to a few confirmed small sky gaps in upper leaves. It does not touch the rest of the artwork.

Five internal iterations were inspected against the old matte, real Night composite, and magenta Neon audit:

1. Wide trimap and color projection improved leaf edges but spread too far around the hat and spires.
2. Narrower trimap plus automatic hole recovery made a wrong dark patch near the roof; rejected.
3. First fixed override used round brush marks and looked like dots in the leaves; rejected.
4. Bounded, tapered override removed those dots and recovered the selected openings.
5. Kept the previous matte as a floor and applied local continuous alpha plus the bounded override. This prevents reopening a covered seam and is the delivered version.

The four sky RGB planes are byte-identical to `1b1e346`; only their shared alpha changed. All four PNG alphas equal `sky-mask.png`. No WebGL shader, compositing order, time curve, Lighting, Blink, Leaves, or Breathing code changed. The override asset is a fixed registered matte; its nonzero marks occupy only the selected upper-edge details.

## Audit and regression

The following use the **same registered source region at 4×**. The magenta composite makes small uncovered sky pixels and halos easier to see than the real Night plate:

| Region | Night before / after | Neon before / after | Final matte |
| --- | --- | --- | --- |
| Left upper leaves | [before](r3-2b-final/before-night-left-4x.png) / [after](r3-2b-final/after-night-left-4x.png) | [before](r3-2b-final/before-neon-left-4x.png) / [after](r3-2b-final/after-neon-left-4x.png) | [alpha](r3-2b-final/after-matte-left-4x.png) |
| Hat and nearby sky | [before](r3-2b-final/before-night-center-4x.png) / [after](r3-2b-final/after-night-center-4x.png) | [before](r3-2b-final/before-neon-center-4x.png) / [after](r3-2b-final/after-neon-center-4x.png) | [alpha](r3-2b-final/after-matte-center-4x.png) |
| Right upper leaves | [before](r3-2b-final/before-night-right-4x.png) / [after](r3-2b-final/after-night-right-4x.png) | [before](r3-2b-final/before-neon-right-4x.png) / [after](r3-2b-final/after-neon-right-4x.png) | [alpha](r3-2b-final/after-matte-right-4x.png) |
| Spires and roof | [before](r3-2b-final/before-night-spires-4x.png) / [after](r3-2b-final/after-night-spires-4x.png) | [before](r3-2b-final/before-neon-spires-4x.png) / [after](r3-2b-final/after-neon-spires-4x.png) | [alpha](r3-2b-final/after-matte-spires-4x.png) |

Night 22:00 [full WebGL2/Lit frame](r3-2b-final/night.png). Other WebGL2/Lit frames: [Dawn 06:30](r3-2b-final/dawn.png), [Noon 12:00](r3-2b-final/noon.png), [Dusk 17:30](r3-2b-final/dusk.png). The left leaf sky openings and thin contours are more continuous in the 4× Night/Neon comparison. The Noon frame does not show a new gray outline; leaf silhouettes and tower tips remain defined. Isolated pale paint inside the leaves remains part of the frozen Base; the matte does not blindly turn those marks into sky. A combined Lit/Sky/Breathing/Blink/Leaves Night view remained registered [at start](r3-2b-final/night-combined-start.png) and [after 6.5 seconds](r3-2b-final/night-combined-after-6s.png).

`pnpm build` and `pnpm typecheck` passed. Await human review before freezing R3 or starting Hair Motion.
