# DB-Living-Hero-Lab — Requirements

## 1. Project Identity

Project name:

**DB-Living-Hero-Lab**

This repository is an isolated R&D sandbox for a dynamic “Living Hero” homepage scene.

The final destination is my personal Blog project, but this repository exists specifically to validate and mature the visual engine before any production Blog integration.

The project should turn one approved anime-style hero illustration into a living, time-aware scene with:

- 24-hour lighting changes;
- directional relighting;
- window-projected sunlight;
- warm local lamp lighting;
- controlled bloom;
- subtle atmospheric motion;
- accepted blink, experimental breathing, optional/deferred hair motion;
- debug tools for visual validation.

The key visual target is not merely:

> “a static wallpaper with some filters”

but:

> “a coherent anime CG scene whose lighting actually changes through the day.”

---

## 2. Reference Direction

Primary technical / visual reference:

https://github.com/buger404/KumengScreen

Reference live result:

https://kumeng-dreamscreen.buger404.chatgpt.site/

Important ideas to learn from the reference project:

- time-driven lighting;
- albedo + normal-map relighting;
- anime-friendly stylized shading;
- face-safe lighting;
- hair-specific lighting treatment;
- subtle micro-motion;
- restrained bloom / tone response;
- technical-art assets separated from runtime code;
- visual QA using multiple time states.

Do NOT copy its character, scene, layout, or exact artistic assets.

The goal is to learn from the technical approach while keeping this project visually and architecturally independent.

---

## 3. Approved Source Assets

### 3.1 Main Hero

The approved hero illustration is:

`public/assets/hero-4k-digital-art.png`

This is the current visual master.

Rules:

- do not overwrite it;
- do not crop or move it;
- do not redesign the character;
- do not silently replace it with a newly generated illustration;
- treat it as the registration reference for all technical textures.

This image is currently a polished CG rather than a clean shadow-free albedo pass.

Therefore it contains baked lighting and shadows.

This limitation must be acknowledged instead of hidden with increasingly complex shader hacks.

---

### 3.2 Character Reference

The project also includes the Black Sister 1.0 standard character reference.

Its purpose is identity validation only.

It may be used when creating technical or animation assets, but it must not replace the approved Hero scene.

---

## 4. Character Identity Constraints

The Hero character is Black Sister 1.0.

Core identity must remain stable:

- cream / ivory beret;
- withered rose on the character’s right side;
- single black ribbon on the left side;
- warm milk-tea brown long hair;
- left-side small tied hair section;
- warm eyes;
- soft small face with rounded jaw;
- gentle, natural, slightly sweet expression;
- light knit inner top;
- pinafore / suspender dress;
- dark flower-shaped buttons.

Do not redesign the character during technical-art generation.

---

## 5. Visual Tone

Target mood:

- quiet;
- warm;
- soft;
- restrained;
- cozy;
- slightly dreamy;
- suitable for a personal Blog homepage.

Avoid:

- aggressive game HUD effects;
- strong neon;
- excessive glow;
- plastic 3D face shading;
- heavy realism that destroys anime CG coherence;
- exaggerated Live2D-style deformation;
- over-animated hair;
- flashy particles.

The best effect should feel subtle when viewed moment-to-moment, while still producing clearly different lighting structures across the day.

---

# 6. Current Project Status

The project is no longer in bootstrap stage.

Current phase: **Micro Animation / Living Scene Convergence**.
Lighting (including Shadow, registered normal v2, masks, window and lamp fields)
is **FROZEN / ACCEPTED**. Bloom and Coffee Steam are **IMPLEMENTED**.
Blink is **IMPLEMENTED / ACCEPTED / FROZEN**, including human desktop acceptance.
Current experiment: **Code-only Breathing Prototype**, default OFF,
**EXPERIMENTAL / awaiting human acceptance**, not an accepted/frozen feature.

Existing systems include:

- Vite + TypeScript application;
- WebGL2 renderer;
- framework-separated engine structure;
- 24-hour timeline;
- manual time slider;
- realtime local-time mode;
- Dawn / Noon / Dusk / Night presets;
- ambient light;
- directional daylight;
- stylized anime lighting band;
- face / hair / cloth region control;
- projected window light;
- exterior / window masking;
- night exterior suppression;
- warm lamp contribution;
- bloom;
- coffee steam;
- accepted registered Half/Closed Blink overlays and controller;
- reduced-motion and background-tab pause;
- multiple debug views;
- Playwright visual QA;
- performance / GPU diagnostics;
- WebGL lifecycle handling;
- generated technical textures;
- scene region source definitions.

The project also contains:

- `normal-low-frequency.svg`
- comparison `normal-registered-v1.png`;
- default `normal-registered-v2.png` (accepted and frozen).

The registered normal v1 is a historical comparison, not the current default.

The AI-generated full normal-map attempt was rejected because it changed geometry / registration.

---

# 7. Historical Technical-Art Problem (Completed)

The symptoms and strategies in sections 7 and 9-19 describe completed technical-art
and lighting phases. They are retained as architecture constraints and historical
design background, not current development priorities or requests for recalibration.
The accepted baked-light limitation remains; do not reopen frozen lighting.

The project has proven the runtime architecture, but visual quality is now limited primarily by technical-art assets rather than missing application features.

Current symptoms:

- time-of-day differences still partially read as global brightness / color changes;
- projected light can look like a 2D light band rather than light responding to real form;
- lamp lighting does not yet produce enough form response on hair, cloth, hands, book, cup, etc.;
- existing Hero contains baked daylight / highlights / shadows;
- current registered normal is still too broad and simplified;
- masks have sometimes been overused to compensate for missing surface geometry;
- inaccurate exterior/window masks can create visible night-time boundary artifacts.

The completed technical-art/lighting phase addressed this direction.

---

# 8. Current Priority Phase

## Micro Animation / Living Scene Convergence

Technical Art Alignment and Lighting are complete and frozen; Blink is accepted
and frozen. The only current experiment is Code-only Breathing, default OFF.
Constrain smooth 1-2 source-pixel deformation to upper-torso garment interiors;
keep face, Blink crop, neck, hands, hair, silhouette, book and environment fixed.
Registered pigment/normal/material samples must move together while screen-space
light geometry stays fixed. Reuse the renderer scheduler, respect motion gates,
pause hidden time and add no texture, framebuffer, pass or image asset.
Human A/B acceptance is required before deciding whether to enable it by default.

---

# 9. Technical Art Alignment — Core Strategy

The new approach is:

1. keep the approved Hero image;
2. improve registered technical textures;
3. make all major lights use those textures;
4. reduce reliance on ad-hoc mask/shader compensation;
5. experimentally reduce baked-light interference;
6. recalibrate the 24-hour lighting after the technical assets improve.

The project should move toward:

Hero Base
+
Registered Surface Data
+
Semantic Masks
+
Dynamic Lighting
+
Controlled Correction
+
Post-processing

instead of:

Hero Base
+
Increasingly complex 2D lighting patches.

---

# 10. Registered Normal Map

## 10.1 Goal

Create a significantly improved registered normal v2 / v3.

It must remain strictly aligned to:

`hero-4k-digital-art.png`

Registration quality is more important than visual complexity.

---

## 10.2 Target Areas

Improve at least the following surface groups:

### Character

- major bangs;
- large front hair locks;
- side hair masses;
- long back hair volumes;
- left tied hair section;
- beret;
- rose / large accessory volumes where useful;
- upper-body knit garment;
- gathered sleeves;
- shoulder / torso volume;
- suspender dress;
- flower buttons if useful;
- hands;
- major finger volumes;
- visible leg / skin if relevant.

### Scene

- open book;
- left page;
- right page;
- center spine curvature;
- coffee cup cylinder;
- cup rim;
- cup handle;
- cup saucer / coaster;
- tabletop plane;
- chair;
- books;
- lamp;
- laptop main plane;
- large window-frame planes where useful.

---

## 10.3 Normal Requirements

The normal texture should describe broad and medium-scale geometry.

Avoid converting:

- painted line art;
- wood grain;
- eyelashes;
- eyebrows;
- iris texture;
- individual painted hair strands;
- image noise;

into deep geometric bumps.

Face normals must remain especially restrained.

The face should have:

- soft broad curvature;
- gentle cheek volume;
- gentle forehead volume;
- subtle chin direction;
- minimal nose structure.

Avoid:

- deep eye sockets;
- embossed eyelashes;
- sharp nose ridges;
- plastic doll appearance.

---

## 10.4 Technical Encoding

Normal map encoding must be documented and consistent.

Example convention:

`RGB = normal.xyz * 0.5 + 0.5`

with clearly documented axis orientation.

All runtime shaders and generation scripts must use the same convention.

---

## 10.5 Generation Policy

Preferred order:

1. deterministic registered generation;
2. carefully guided technical-art generation;
3. AI-assisted candidate generation only when strict registration can be preserved.

Any AI-generated normal map must be rejected if it:

- moves geometry;
- redraws hands;
- changes the book;
- changes hair silhouette;
- changes facial alignment;
- changes scene layout;
- changes crop / aspect ratio.

Do not accept visually impressive but misregistered technical maps.

---

# 11. Semantic Masks

Semantic masks remain useful, but their role must be limited.

Masks should answer questions such as:

- where is exterior glass?
- where is the character face?
- where is hair?
- where is cloth?
- where is the desktop receiver?
- where is the lamp emitter?
- where should bloom be suppressed?
- where should night exterior treatment apply?

Masks should NOT be the primary method used to emulate:

- hair volume;
- cloth folds;
- cup curvature;
- hand volume;
- detailed shading geometry.

Those belong primarily to the normal map / surface data.

---

# 12. Window / Exterior Mask

The exterior/window mask must be visually accurate.

Current known issue:

night exterior treatment has previously shown:

- gaps near the window frame;
- incorrect lower-edge coverage;
- spill onto nearby interior objects.

Requirements:

- exterior mask should contain actual visible exterior glass only;
- window frame should remain interior structure;
- sill / table / books / flowers / pen holders must not be treated as exterior;
- borders should match the original Hero;
- avoid hard-coded UV cutoffs used only to hide incorrect geometry.

Source-of-truth region data should be corrected instead.

Debug views should make this easy to inspect.

---

# 13. Dynamic Lighting Architecture

All major light types should eventually respond to surface orientation.

## 13.1 Directional Daylight

Already implemented.

Continue using normal response.

Recalibrate after registered normal improvement.

---

## 13.2 Projected Window Light

Current projected-light system should evolve from:

“screen-space warm band”

toward:

“screen-space sunlight aperture whose intensity is modulated by receiver orientation.”

Projected window light may still use:

- screen-space beam geometry;
- window masks;
- receiver masks;

but final light energy should be affected by surface normal orientation.

Example conceptual model:

ProjectedEnergy
×
ReceiverMask
×
SurfaceResponse(normal, lightDirection)

Do not simply add a colored stripe.

---

## 13.3 Lamp Light

Lamp lighting must become a real local-light approximation.

Instead of only using a Gaussian screen-space pool:

LampEnergy
×
DistanceField
×
ReceiverMask
×
NormalResponse

should influence the result.

The goal is not physically exact point-light rendering.

The goal is believable form lighting.

At night, the following should show meaningful warm form response:

- hair near the lamp;
- right sleeve;
- hands;
- book pages;
- coffee cup;
- table surface;
- nearby objects.

---

# 14. Stylized Anime Shading

The project may continue using stylized broad-band shading.

This is desirable.

However:

- stylized shading should enhance surface lighting;
- it should not compensate for a missing normal map;
- it should not create large arbitrary screen-space bands unrelated to form.

Recommended character-specific treatment:

- face: very soft response;
- hair: stronger broad directional response;
- cloth: moderate response;
- environment: material-dependent response.

---

# 15. Baked Lighting Problem

The current Hero is not a clean albedo pass.

It contains baked:

- highlights;
- shadows;
- warm reflections;
- directional daylight.

These cannot be perfectly removed with runtime shaders.

This must be treated as a technical limitation.

---

# 16. De-light / Intrinsic Correction Experiment

Before considering a full Hero redraw, perform a controlled experiment.

Possible outputs:

- `hero-delight-candidate.*`
- `intrinsic-correction.*`
- `baked-light-correction.*`

The experiment may attempt to reduce:

- fixed strong window highlights;
- fixed warm directional areas;
- fixed daylight contrast.

However:

- the approved Hero remains the master;
- this is an optional runtime technical asset;
- geometry must remain strictly registered;
- identity must remain unchanged.

---

## 16.1 Rejection Criteria

Reject a de-light candidate if it:

- changes character geometry;
- changes face;
- changes hair layout;
- changes hands;
- changes book geometry;
- changes room objects;
- looks blurrier;
- destroys illustration texture;
- introduces AI repaint artifacts.

---

## 16.2 Preferred Fallback

If full AI de-lighting cannot remain registered:

prefer a correction texture.

Concept:

Base Hero
× / +
Registered Intrinsic Correction
→
More Neutral Runtime Base
→
Dynamic Lighting

This may be less theoretically pure than a true albedo pass, but is acceptable if it preserves the approved artwork.

---

# 17. 24-Hour Lighting Targets

The timeline must remain smooth.

Important validation times:

- 06:00
- 08:00
- 12:00
- 17:30
- 23:00

---

## 17.1 Dawn / Early Morning

Target:

- slightly cool / fresh room ambience;
- low-angle daylight;
- subtle but visible directional structure;
- clearly distinguishable from noon even in grayscale.

Avoid:

- simply making noon darker;
- excessive orange sunrise effect.

---

## 17.2 Noon

Target:

- bright;
- clean;
- neutral;
- higher-angle light;
- broad readable lighting;
- preserve illustration quality.

Noon should remain the least dramatic state.

---

## 17.3 Dusk

Target:

- strongest visible projected sunlight state;
- warm low-angle window light;
- visible form response on:
  - hair;
  - cloth;
  - book;
  - cup;
  - table;
- stronger light/shadow separation;
- cinematic but not over-saturated.

---

## 17.4 Night

Target:

three-part structure:

1. cool window / outdoor environment;
2. darker interior ambient;
3. warm lamp-driven local light.

The character must remain readable.

Lamp lighting should create actual form response rather than merely tinting a region.

No daylight beam should remain.

---

# 18. Debug Views

Maintain and extend useful debug views.

At minimum:

- Final
- Base
- Normal
- Character Masks
- Scene Masks
- Overlay
- Directional Lighting
- Neutral Lighting
- Projected Light Only
- Exterior Mask
- Shadow / Occlusion debug if relevant

Recommended new debug views:

- Lamp Contribution Only
- Surface Response Only
- Correction Texture / De-light comparison
- Registered Normal comparison

---

# 19. Visual QA

Every major technical-art iteration should produce fixed screenshots.

Required times:

- 06:00
- 12:00
- 17:30
- 23:00

At minimum compare:

- Final
- Neutral Lighting
- Normal
- Projected Light
- Lamp Contribution where applicable.

---

## 19.1 Grayscale Test

Convert or inspect the main time states without relying on color.

The time states should still differ structurally.

If:

06:00
12:00
17:30

only differ after adding color temperature,

the lighting system is not strong enough.

---

# 20. Current Deferred Features

The following remain optional/deferred:

- hair motion (only consider after Blink + Breathing acceptance if still needed);
- advanced particles;
- complex parallax;
- Blog production integration.

Coffee Steam and Bloom are implemented; Blink is accepted/frozen, not deferred.
Breathing is the current experimental candidate, awaiting human acceptance.

---

# 21. Blink

**IMPLEMENTED / ACCEPTED / FROZEN**, with human desktop acceptance.
Approved Half/Closed straight-alpha overlays are 700 x 470, registered at
x=1940, y=390 in the 3840 x 2160 Hero. They replace pigment before relighting.
Open -> Half -> Closed -> Half -> Open lasts 160 ms, with randomized 2.8-5.5 s idle.
Animation-off/reduced-motion restore Open; hidden tabs pause; destroy cleans up.
Do not regenerate artwork, extract overlays again or change accepted timing.

---

# 22. Performance

Desktop remains the primary target.

Requirements:

- maintain stable modern desktop performance;
- avoid unnecessary full-resolution multi-pass operations;
- use reduced-resolution post-processing where sensible;
- cap DPR when appropriate;
- pause animation in hidden tabs;
- respect `prefers-reduced-motion`.

Technical-art improvements should not automatically justify large rendering-cost increases.

---

# 23. Architecture

Keep the rendering engine framework-independent.

Preferred conceptual API remains similar to:

- `createLivingHero(canvas, options)`
- `setTime(minutes)`
- `setRealtime(enabled)`
- `setDebugView(mode)`
- `setReducedMotion(enabled)`
- `setBreathing(enabled)` (experimental, default false)
- `destroy()`

Do not tightly bind core rendering logic to React or future Blog components.

---

# 24. Blog Integration

Do NOT integrate this repository into the production Blog yet.

The final destination is **DB-Blog-Plume**, after Living Hero Engine freeze.

Blog integration starts only after:

- the technical-art pipeline is accepted;
- the four main time states are visually accepted;
- the runtime engine is considered stable enough.

---

# 25. Engineering Quality

After meaningful changes run:

- typecheck;
- unit tests;
- build;
- visual tests;
- relevant performance tests.

Do not lower test thresholds merely to make a change pass.

Do not accept a visual change only because automated tests pass.

Human visual review remains mandatory.

---

# 26. Documentation

Keep technical decisions documented.

Recommended logs:

- technical-art-alignment.md
- normal-v2-review.md
- lighting-normal-integration.md
- delight-experiment.md
- final-lighting-review.md

Record:

- what changed;
- why;
- what screenshots were compared;
- rejected candidates;
- known limitations.

---

# 27. Historical Technical-Art Acceptance Criteria

This phase is completed/frozen. Retain these requirements as regression constraints.

The Technical Art Alignment phase is considered successful only if:

1. a higher-quality registered normal map exists;
2. the normal remains strictly aligned with the approved Hero;
3. directional sunlight shows clearer surface response;
4. projected window light responds to surface orientation;
5. lamp light responds to surface orientation;
6. night exterior mask no longer shows obvious boundary mistakes;
7. 06:00 / 12:00 / 17:30 remain distinguishable in grayscale;
8. 23:00 reads as a coherent cold-window / warm-lamp scene;
9. the character does not look plastic or over-shaded;
10. the result feels clearly closer to a relit anime CG rather than a static image with overlays.

---

# 28. Decision Gate After This Phase

Review the default-OFF Breathing prototype alongside accepted Blink on real hardware.
Keep it optional or reject it if the movement is distracting or breaks registration.
Do not mark Breathing ACCEPTED/FROZEN before human approval. Hair Motion remains
optional/deferred and is not part of this experiment. After Living Scene acceptance,
freeze the engine, then plan migration into DB-Blog-Plume as a separate task.
The baked-light limitation is accepted; no albedo redraw is authorized here.

---

# 29. Final Principle

The approved Hero image remains the artistic master.

The goal is not to chase theoretical rendering purity.

The goal is:

> preserve the artwork while giving it convincing, controllable, anime-friendly dynamic lighting.

Prefer a stable, registered, visually coherent solution over a technically impressive but fragile or misregistered one.

## 30. Historical session scope — 2026-09-17

Converge only the Hero lighting foundation: independently maintainable hand-authored
glass bounds; contact/form shadows; rear-right lamp visibility, sill and right-desk
pools with attenuation; restrained left-wall/chair/foreground participation.
Inspect the running baseline before changes and deliver 06:00 / 12:00 / 17:30 /
23:00 captures, explicit self-checks and remaining limitations. No blink rendering,
new character animation, UI rearrangement, base replacement, architecture rewrite
or large dependencies. Keep runtime cost controlled and commit validated work locally.

## 31. Current session scope - 2026-09-20

Synchronize current-status documents, then implement only the low-risk Code-only
Breathing Prototype described above. Preserve historical logs/captures. Verify
OFF against the accepted shader at dawn/noon/dusk/night, region isolation, registered
sampling, Blink compatibility and all motion/lifecycle gates. Run typecheck, unit
tests, build and a full visual regression before a scoped local commit. Exclude
the temporary WORK.md and all work/ changes from this session's commit. Stop at
EXPERIMENTAL / awaiting human acceptance; no Hair Motion or Blog migration.
