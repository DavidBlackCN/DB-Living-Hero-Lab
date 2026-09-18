# Hand-safe lighting and engine freeze — 2026-09-18

Baseline: `f80e79f`. Scope: only the anatomical left hand at screen right,
its contact edge and local lamp response. Whole-scene lighting, window masks,
face/fringe treatment, lamp field geometry and desk-pool size are unchanged.

## Root cause

The 23:00 artifact is normal-driven, not a broad occlusion patch.

- `docs/normal-surfaces.json` layer `hand-right` combined an ellipsoid
  (`strength [0.18,0.11]`) with three finger ribbons:
  - `[896,472]…[908,510]`, width 6, strength .22
  - `[907,478]…[919,515]`, width 5.5, strength .21
  - `[917,485]…[931,513]`, width 4.5, strength .18
- The registered-v2 normal debug exposes those ribbon cross-sections. The rear
  lamp's stylized form response turned them into regular internal dark facets.
- Shadow/occlusion and contact diagnostics contain no matching interior patch.
  `right-hand-page` is clipped to the receiving book and stays at its narrow edge.
- The source illustration contains a painted finger cavity. It remains, but the
  engine no longer reinforces it with authored polygon-like normal divisions.

## Local repair

- Rebuilt only registered-v2 `hand-right`: removed the three per-finger ribbons;
  retained a wider, weaker ellipsoid (`[0.09,0.05]`) and broad palm orientation.
- Packed screen-right hand semantics as white in `character-masks.svg`; shader
  derives a feathered `hand` weight without changing face/hair/cloth channels.
- Blended the effective hand normal 82% toward a broad analytic palm normal.
- Replaced the hand portion of lamp form shading with a wider, lower-contrast
  turning response. It retains directional volume without a hard terminator.
- Contact feather is capped only where it touches hand skin; the receiving page
  keeps its narrow authored contact line.
- Local warm bounce now prioritizes the hand semantic mask, remains bounded to
  the existing 76×57 artwork-space field, and still follows lamp/night strength.

No new render pass, dependency, runtime texture, global light coefficient or
UI control was introduced.

## Validation

- `npm run build`: passed (includes TypeScript check).
- Timeline tests: 7/7 passed.
- Dedicated semantic/contact/capture test: passed.
- Full Playwright visual suite: 53/53 passed.
- Required actual-browser 23:00 outputs: Final, effective Normal, Form,
  Shadow/Occlusion, Contact and Lamp Contribution.
- Identical 1920×1080 screenshots and x1280–1550/y680–860 hand crops were used
  for before/after comparison.
- 12:00 and 17:30 inspections retain finger linework and broad hand volume.
  Their local mean absolute changes are .13 and .90 RGB levels respectively.
- Differences outside the conservative hand crop are at most 3 levels at noon,
  2 at 17:30 and 5 at 23:00, caused by the existing bloom kernel at the boundary.

The regular polygon hand-shadow artifact is removed. Remaining painted finger
cavity and baked source illumination cannot be separated from albedo without
repainting the supplied illustration.

Status: **FROZEN — accepted with baked-light limitation**.

See the [visual acceptance gallery](../screenshots/hand-safe-freeze/README.md).
