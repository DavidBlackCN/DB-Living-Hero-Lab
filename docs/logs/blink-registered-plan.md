# Registered closed-eye asset — feasibility, 2026-09-16

## Can this session do it?

**Can produce an edited candidate; cannot guarantee a production-ready registered
asset without alignment and visual QA.** The session exposes the built-in
`image_gen` editing tool, so an API key or external artist is not a prerequisite
for attempting a candidate. No image call was made in this review.

OpenAI's official guide documents image editing, but explicitly says masks guide
the model rather than guaranteeing exact shape adherence. This is why generation
and registration must be separate gates. [Official image generation guide](https://developers.openai.com/api/docs/guides/image-generation#edit-an-image-using-a-mask).

## Minimum workflow proposed for a later task

1. Verify the approved Hero hash. Recheck both eye boxes from the original;
   `docs/blink-regions.json` holds experimental candidates, not approved eyelid
   contours. Make a crop with both eyes, brows, nose bridge and nearby hair as
   alignment context; record its exact pixel rectangle and source dimensions.
2. Inspect that local crop, then submit it to the built-in image editor as the
   edit target. Request a natural relaxed closure of both eyes, preserving eye
   corners, perspective, eyelash character, brows, face contour, hair and lighting.
   Do not regenerate the entire Hero or use kuro-standard as the edit target.
3. Save the returned crop as an unapproved candidate. Compare unedited landmarks
   and edge overlays. Reject changed identity, gaze geometry, head position or
   local scale; do not warp the original face to make the result fit.
4. Composite only the approved eyelid region onto the original crop using a
   separately authored coverage mask. Coverage must fully replace the original
   iris/sclera in the interior, with a short seam transition outside eye linework.
   Do not use color-difference magnitude as alpha (the old experiment did this).
   Pixels outside the edit ROI must match the original exactly.
5. Export a registered 3840×2160 RGBA overlay, transparent outside both eye ROIs,
   with top-left registration metadata, source hash and straight-alpha semantics.
   Keep the generation output and final composite distinct. Inspect open/closed
   A/B and alternating frames at 1× and 2×, then at 08:00/12:00/17:30/23:00.
6. Only after manual acceptance, add timing and runtime loading. If candidates
   keep changing identity/linework, obtain an artist-authored closed-eye local
   repaint of this exact Hero crop. A generic closed-eye reference is insufficient.

## Engineering seam, without a current renderer branch

Keep `BlinkAsset` / `BlinkOptions` in `src/engine/animation.ts` as the dormant
contract. Its current validator checks dimensions/positive ROI size only; before
activation add finite/in-bounds ROI, decoded image size and source-hash checks.
No dummy texture, timing loop, UI toggle or fake eyelid line is needed now.

Later, an isolated blink controller should expose `sample(timeMs): closure` and
`reset()`. The renderer owns the accepted optional texture; it applies ROI alpha
and closure when sampling base color **before relighting**, in linear color space,
using the same UV/face protection as the Hero. This prevents a bright sticker
over the night face. Restore the open eye when disabled, hidden or reduced-motion
is active. Optional closed-eye normal refinement can follow if visibly needed.

This document is a proposal, not an implemented Blink API or an accepted asset.
