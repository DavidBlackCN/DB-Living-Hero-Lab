# R3.2 Sky edge matte cleanup

Status: ready for human review before the R3 stage freeze.

The Night view exposed a thin light seam where the registered sky meets upper vines, leaves, and distant spires. The four sky images already carry the same alpha as `sky-mask.png`; WebGL composites that alpha once after Lighting. The source matte was generated with a conservative blue/lightness gate, one-pixel dilation, and 0.65-pixel feather. Its partial edge coverage left a little bright Base sky visible next to the deep Night plate. The issue was in the authored matte, not `skyFor()` or shader sampling.

`scripts/generate_sky_assets.py` now adds a **one-source-pixel, color-gated fringe** to the existing matte in the registered upper-sky area. Only cool, sufficiently light Base pixels can receive extra sky alpha. The four RGBA sky files and `sky-mask.png` were regenerated together; all four sky RGB planes are byte-identical to the previous assets, and each PNG alpha still exactly matches the mask. No shader, compositing order, Lighting/Sky timeline, Blink, Leaves, or Breathing code changed. Broader ungated matte trials visibly damaged leaf and spire detail, so they were rejected.

## Regression

- WebGL2/Lit captures: [Dawn 06:30](r3-2-sky-edge/dawn.png), [Noon 12:00](r3-2-sky-edge/noon.png), [Dusk 17:30](r3-2-sky-edge/dusk.png), [Night 22:00](r3-2-sky-edge/night.png). The four sky colors and overall time-of-day looks remain intact; no new white/gray halo or blurred tower tip was found at screenshot scale.
- [Night edge before](r3-2-sky-edge/night-edge-before.png) / [after](r3-2-sky-edge/night-edge-after.png) use the same static WebGL2 state with only old versus new sky assets swapped. The pale contour next to sky is narrower. The change is intentionally confined to the contour: 2,460 screen pixels changed in the 1440×900 Night comparison, with a maximum channel change of 19. Isolated bright flecks painted into the Base leaves were preserved rather than mistaken for sky pinholes.
- In Lit at 22:00, Breathing, Blink, Leaves, Lighting, and Sky stayed enabled for 6.5 seconds. [Later Night frame](r3-2-sky-edge/night-after-6s.png) and [Night closed-eye frame](r3-2-sky-edge/night-blink.png) show that moving leaves, Blink, and Breathing do not shift the registered sky boundary.

`pnpm build` and `pnpm typecheck` passed. The Sky asset/mask dimensions and alpha equality were checked; the four Sky RGB planes match their previous hashes. The old pixel-identical R2B screenshot comparison is not applicable to this intentional matte change.
