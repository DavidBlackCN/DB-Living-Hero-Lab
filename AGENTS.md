# AGENTS.md

## Project identity

## Current phase (2026-09-20)

- Lighting / Shadow / registered normal / masks: FROZEN / ACCEPTED.
- Bloom and Coffee Steam: IMPLEMENTED.
- Blink: IMPLEMENTED / ACCEPTED / FROZEN, including human desktop acceptance.
- Current phase: Micro Animation / Living Scene Convergence.
- Current experiment: Code-only Breathing Prototype, default OFF,
  EXPERIMENTAL / awaiting human acceptance. No new image assets or render passes.
- Hair Motion, Complex Parallax and Advanced particles remain optional/deferred.
  Consider hair only after Blink + Breathing review if the scene still feels stiff.
- Final destination: DB-Blog-Plume only after Living Hero Engine freeze.

The phase-1 deliverables and priority lists below are historical design constraints,
not permission to reopen accepted lighting or Blink. Preserve frozen coefficients,
technical maps, Blink assets/timing and source artwork. This session only synchronizes
current documentation and experiments with internally bounded garment deformation.
Do not stage `WORK.md` or any changes under `work/` in this session's commit.

This repository is an isolated R&D sandbox for a “Living Hero” homepage background system.

Primary goal:
- Build the core real-time visual engine for a single anime-style homepage hero scene.
- Focus on time-of-day relighting, subtle micro-animation, and debug tooling.
- Do NOT integrate into the main Blog project yet.

This repository is NOT the final blog implementation.
This repository is a standalone experimental prototype that will later be migrated into the Blog project after visual and technical validation.

---

## Available source assets

The repository initially provides only two user-supplied image assets:

1. `public/assets/hero-4k-digital-art.png`
   - Final 4K homepage hero illustration.
   - This is the main visual base.
   - Treat it as the visual truth for the scene.
   - Do not redraw or redesign the scene unless specifically required for derived technical assets.

2. `public/assets/kuro-standard.png`
   - Black Sister 1.0 standard reference illustration.
   - Use only as a visual identity/reference asset when generating derived materials.
   - Do not use it as the runtime background.

---

## Core objective

Create a standalone web prototype that makes the hero scene feel alive.

The prototype must support:
- 24-hour time-of-day relighting
- manual time scrubbing
- realtime mode
- subtle anime-friendly relighting
- mild post-processing
- micro-animation such as blink / breathing / light steam

The prototype should feel like a high-quality animated homepage hero scene, not like a static wallpaper with UI over it.

---

## Non-goals

For the current phase, do NOT:
- integrate with VuePress / Plume / the Blog project
- implement final navbar / final homepage content system
- build a large component library
- over-focus on text layout polish
- build a heavy Live2D-style skeletal animation system
- split the image into a complex many-layer puppet rig unless absolutely necessary
- redesign the character identity
- replace the user-provided hero artwork with a new illustration

---

## Development principles

### 1. Keep the engine framework-light
The runtime visual engine should be as framework-independent as practical.

Preferred approach:
- Vite
- TypeScript
- React for debug UI only
- core rendering logic decoupled from React

The rendering engine should be written so that it can later be embedded into another app.

### 2. Prefer WebGL2-based rendering
Use WebGL2 for the core relighting/rendering path unless there is a strong technical reason not to.

Avoid over-engineering with large 3D engines if not needed.

### 3. Preserve the scene composition
Do not change the composition, crop, identity, or overall art direction of the hero image.
Derived technical assets must stay spatially registered to the original hero image.

### 4. Favor subtlety
This scene should feel calm, soft, warm, and refined.
Avoid loud, exaggerated, gamey, or gimmicky effects.

### 5. Visual correctness > effect quantity
A smaller number of convincing effects is better than many distracting effects.

---

## Required deliverables for phase 1

The repository should eventually contain:

### App / engine
- a runnable local dev app
- a rendering engine module
- a simple debug UI panel
- a time-of-day system
- a relighting pipeline
- reduced-motion support
- background-tab animation pause handling

### Assets / generated materials
Generated or processed technical assets may be added, such as:
- normal map
- masks
- blink frames
- steam assets
- debug exports

Place generated assets under clear directories, for example:
- `public/assets/generated/`
- `docs/prompts/`
- `docs/logs/`
- `docs/screenshots/`

### Documentation
Maintain:
- setup instructions
- architecture notes
- asset notes
- prompt logs or generation notes
- test and validation notes

---

## Suggested architecture

Prefer a structure similar to:

- `src/engine/`
  - renderer
  - shaders
  - timeline
  - lighting
  - animation
  - assets
  - postprocessing
- `src/debug-ui/`
- `src/app/`

The engine should later be portable into another project.

It is desirable to expose a clean API such as:

- `createLivingHero(canvas, options)`
- `setTime(minutes)`
- `setRealtime(enabled)`
- `setReducedMotion(enabled)`
- `setDebugView(mode)`
- `destroy()`

---

## Visual feature priorities

Implement in this rough order:

### Priority A — essential
1. Display the hero image properly
2. Debug panel
3. Time slider (0–24h)
4. Realtime mode
5. Directional + ambient relighting
6. Smooth day-night interpolation

### Priority B — scene quality
7. Anime-friendly relighting behavior
8. Face-safe lighting correction
9. Hair-friendly highlight behavior
10. Window light / lamp light separation
11. Mild bloom / exposure / tone mapping

### Priority C — subtle life
12. Blink
13. Breathing
14. Very light hair motion
15. Very subtle coffee steam

---

## Constraints for derived assets

If you generate technical assets such as normal maps, masks, blink overlays, etc.:

- keep exact registration to the original image whenever needed
- do not shift geometry
- do not alter character identity
- do not repaint the whole scene unless the asset specifically requires a transformed representation
- document what was generated and how

If image generation is available, it may be used for technical assets.
If not, procedural or programmatic approximations are acceptable for MVP.

---

## Testing and validation

You must validate your work continuously.

At minimum:
- `npm run build`
- `npm run typecheck`

If tests are added, keep them working.

Create visual validation outputs:
- screenshots for multiple times of day
- preferably dawn / noon / dusk / night

Store them under:
- `docs/screenshots/`

Whenever a major shader or visual change is made, update screenshots.

---

## Performance expectations

The prototype targets desktop first.

Requirements:
- smooth interaction on a typical modern desktop
- avoid unnecessary heavy passes
- cap DPR if necessary
- pause or reduce work in background tabs
- respect `prefers-reduced-motion`

---

## Debug UX expectations

A debug panel is required in the prototype stage.

It should expose at least:
- realtime toggle
- manual time slider
- preset jumps (dawn / noon / dusk / night)
- exposure
- ambient light
- sun strength
- lamp strength
- normal strength
- face / hair / cloth lighting balance if implemented
- bloom toggle and intensity if implemented
- animation toggles
- debug view selector

---

## Work style

When implementing:
1. inspect the current repo state
2. propose or create the minimal working structure
3. build incrementally
4. verify often
5. document decisions
6. avoid giant speculative rewrites

Prefer many small correct steps over one huge uncontrolled step.

### End-of-session commits

At the user's standing request, commit each session's completed repository changes
after the relevant validation and documentation are finished. Review the diff and
stage only work belonging to that session; preserve unrelated user changes. Include
updated user requirements when they are part of the delivered work. Do not create
empty commits when there are no changes. Report the commit hash and validation
status in the final response. Commit locally; push only when explicitly requested.

---

## Important “do not do this” rules

Do NOT:
- immediately couple the renderer to the Blog theme
- immediately optimize for mobile-first if desktop MVP is not working
- hide technical complexity inside undocumented code
- add random visual gimmicks not tied to the project goals
- replace the main hero image with unrelated art
- introduce NSFW or inappropriate content
- produce a final polished landing page instead of the requested prototype engine

---

## Completion criteria for the prototype phase

The prototype phase is successful when:
- the page runs locally
- the hero image can be relit across the day
- the time slider works smoothly
- the scene looks noticeably more alive than a static wallpaper
- the effect is subtle and aesthetically coherent
- screenshots for key times look acceptable
- the core engine can later be extracted into the Blog project
