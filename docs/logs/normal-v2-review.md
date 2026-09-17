# Registered Normal v2

The approved 3840×2160 Hero remains the registration master. Coordinates in
`docs/normal-surfaces.json` are the existing 1200×675 reference scaled by 3.2.
v1 definitions are archived in `docs/normal-surfaces-v1.json`; v1 PNG is retained.

`npm run assets:normal` builds v2; `npm run assets:normal -- --version v1`
rebuilds v1 explicitly. Both use the same scene contour source. There is no AI
generation in this revision, source-luminance height extraction, image warp,
repainting or noisy high-frequency bump.

## Changes

- Hair: tapered curved cross-sections for bangs, front/side locks, long masses
  and the character-left tied section (image right). Compact support prevents
  additive Gaussian heights forming piles of spherical bumps; end taper removes
  round ridge caps. Hat occlusion prevents the hair field extending into the hat.
- Cloth: sleeve cylinders, body curvature, restrained cuff folds; retained
  medium folds have reduced height. Pinafore gets stronger broad body curvature.
- Hands: small curved finger cross-sections on top of broad palm volume. Face
  stays at v1's gentle ellipsoid: no eye/nose/eyelash relief.
- Book: separate tilted page surfaces and retained gentle page curvature;
  underlying page block has its own normal instead of inheriting the desk.
- Cup: cylinder, rim/top plane, curved handle, coaster plane.
- Scene: desk, chair, laptop, stacked books, lamp shade and beret have explicit
  surfaces. The laptop no longer inherits the desk normal.

Normals are differentiated before masking, then blended and normalized. RGB8
encodes XYZ from [-1,1] to [0,1]; +X right, +Y down, +Z toward viewer. Sampling is
linear data, with no sRGB conversion. Runtime dimensions and normal texture slot
are unchanged. These are authored approximations, not recovered ground truth.

The geometry guides and Normal/Directional-only captures must be inspected
against the source in addition to unit-vector/probe checks. A unit normal and
correct dimensions alone cannot prove registration or artistic quality.

Final validation: 3840×2160, sampled max vector-length error .00566, minimum Z
.639 after 8-bit encoding. Face center remains `(127,128,255)`, wall/glass
`(128,128,255)`. Cup left/right X values 72/190 and page X values 106/147 confirm
opposite broad orientations. All three maps produce identical Final pixels with
normal strength zero. The v2 hand/wrist continuity and page-contact regressions
pass the unchanged legacy thresholds. Same-light v1/v2 screenshots live under
`technical-art-alignment/final/normals/`; v2 source guides are in `calibrated/`.
