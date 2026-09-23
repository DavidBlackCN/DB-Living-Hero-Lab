# KumengScreen Lighting Notes

Reference reviewed at `buger404/KumengScreen` HEAD `fb34a2e` (2026-09-23): `lib/daylight.ts`, `app/page.tsx`, `lib/scene-shader.ts`, `lib/stylized-lighting.ts`, `lib/post-settings.ts`, and `lib/post-shaders.ts`.

## Borrow

- `lightingFor(minutes)` is a stateless 0-1440-minute model. A sinusoidal solar elevation drives daylight; separate smooth curves derive twilight warmth and dusk-side color. Direction, key/fill color, and intensity change continuously rather than switching between four looks.
- Treat the sun direction as a continuous arc from sunrise through noon to sunset. Keep a nonzero apparent light elevation at night to avoid an unstable horizon direction, while the diffuse response and key contribution remain weaker.
- Decode the sRGB Base Albedo into linear reflectance before combining ambient/sky fill and Normal-driven key diffuse. Convert back to sRGB for display. The Normal texture remains linear data and is never gamma-decoded.
- Use a low-frequency filtered Normal response for a broad painted light band, separate from fine Normal-driven diffuse. This can give anime CG forms a readable large-scale light grouping without adding specular highlights.
- Keep exposure/tone mapping conceptually downstream of scene illumination. This phase only uses a bounded scene exposure in the lighting result; Bloom and post-processing are explicitly deferred.
- A minute-resolution slider with time labels and shortcut points is a useful calibration surface. It should call the same pure lighting function as any future clock or playback driver.

## Do Not Copy

- Do not port the React/Next page, its system-clock synchronization, playback loop, fullscreen shell, or Bloom/post-processing pipeline into this calibration phase.
- Do not copy KumengScreen's numerical curves unchanged. Its scene, display transform, and authored Normal map differ from DB Living Hero.
- Do not copy face, iris, hair, or other hand-authored region masks and UVs from `scene-shader.ts`. Use frozen Normal v3 globally and protect facial readability through conservative broad-band strength and manual visual validation.
- Do not add its specular/iris glints, hair ribbons, emission-like motes, real shadows, or PBR terms here.
- Do not darken and tint the Base as a substitute for relighting. Night must still have a distinct Normal-driven direction and diffuse structure.

## DB Living Hero Adaptation

R2A.1 keeps the existing Vue-independent renderer boundary. `src/config/lighting.ts` owns the time model and tunable curve parameters; Vue only supplies selected minutes. The shader blends original Base and the fully relit linear-space result via `relightStrength`, so the calibration can increase structural separation without altering the frozen Base or Normal v3 assets.
