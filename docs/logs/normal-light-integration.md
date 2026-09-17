# Normal/light integration

All three light types now use the same decoded, normalized texture and normal
strength. No depth buffer, translated caster mask, additional pass or normal
texture is introduced.

- Directional retains the existing soft stylized diffuse band.
- Projection retains the two screen-space aperture lobes, reach and receiver
  coverage. Its final scalar energy is multiplied by wrapped N·L, using the
  same time-driven direction as directional sunlight. Aperture means light
  access; normal means surface orientation. They are not interchangeable.
- Lamp retains the local receiving field, but computes a direction toward the
  source lamp in aspect-correct artwork coordinates: `(0.797, 0.327, 0.28)`.
  Z is a fixed artistic forward distance, not recovered scene depth. The field
  is multiplied by normal response and hair/cloth material response. The lamp's
  emission is separate from reflected light and never multiplied by N·L.
- The shared reflected response is `.18 + .82 * max(dot(N,L),0)`. Its floor
  softens terminators without adding specular/plastic shading. Face response is
  blended toward the front-facing response; the existing face readability
  correction is retained. Lamp field gain is recalibrated from 1.10 to 1.45 to
  account for the orientation attenuation.

New diagnostics: `lamp` (raw linear RGB lamp coefficient before global face,
contact and baked-highlight corrections) and `directional` (directional-only
Rec.709 luminance ×0.6). `projected` now shows aperture × receiving coverage ×
energy × surface response. `neutral` remains the complete lighting coefficient
luminance ×0.6; it is not a gray conversion of Final.

Tests compare normal=0 and normal=1 in each isolated light, require nonzero
surface changes, verify zero night projection, zero lamp when disabled, exact
glass exclusion and orientation-independent lamp emission. Cup-side response is
normalized by the flat-normal local field: the lamp is LEFT of the cup in the
actual artwork, so the left side must receive more than the right.
