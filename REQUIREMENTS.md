# REQUIREMENTS.md

## 1. Project name

Black Sister Living Hero Lab

---

## 2. Project goal

Build a standalone prototype for the “Living Hero” homepage background effect of my personal blog.

This prototype is an experimental visual engine project, not the final blog page.

The purpose is:
- to validate whether a single anime illustration can be turned into a high-quality dynamic homepage hero scene
- to reproduce the pleasant “alive scene” feeling inspired by projects like KumengScreen
- to prepare a reusable rendering engine for later integration into the main Blog project

---

## 3. Starting assets

The project starts with only the following local assets:

### 3.1 Main hero image
- File: `public/assets/hero-4k-digital-art.png`
- Type: 4K anime illustration
- Role: main hero background image
- Notes:
  - This is the current approved final hero artwork.
  - This image should be preserved as the base visual source.
  - Runtime effects should build on top of this image.

### 3.2 Character identity reference
- File: `public/assets/kuro-standard.png`
- Role: Black Sister 1.0 identity reference
- Notes:
  - Used only to maintain character identity if derived technical assets are generated.
  - Not intended as runtime scene artwork.

---

## 4. Character / scene constraints

The scene is based on the existing approved hero illustration and must preserve it.

### 4.1 Character identity must remain consistent
The runtime result must still clearly read as Black Sister 1.0:
- soft, warm, approachable anime girl
- cream beret
- withered rose on the character’s right side
- single black ribbon on the left side
- warm milk-tea brown long hair
- signature outfit consistent with the approved hero image

### 4.2 Scene mood
The scene should feel:
- calm
- warm
- soft
- gentle
- slightly dreamy
- suitable for a personal blog homepage hero section

Avoid:
- loud arcade/game HUD energy
- aggressive action effects
- exaggerated 3D puppet motion
- excessive bloom
- harsh realism that breaks the anime illustration feeling

---

## 5. High-level product target

The final prototype should feel closer to:
- a living scene
than to:
- a static wallpaper with text on top

The visual engine should make the image feel alive through:
- relighting
- time-of-day transitions
- subtle motion
- coherent atmosphere

---

## 6. Scope of this repository

This repository should focus only on the isolated prototype.

### In scope
- standalone app
- rendering engine
- debug controls
- technical asset generation / processing
- visual validation

### Out of scope
- final integration into DB-Blog-Plume
- final blog navbar and production content system
- final blog routing / docs / article list
- production deployment polish

---

## 7. Core functional requirements

### 7.1 Basic app behavior
The app must:
- run locally
- render the hero scene full-screen or near full-screen
- provide a debug control panel
- support smooth updates without full reloads during development

### 7.2 Time system
The app must support:
- 24-hour timeline
- manual time scrubbing
- realtime mode using the current local time
- smooth interpolation across time changes

Suggested named states:
- dawn
- morning
- noon
- afternoon
- dusk
- night

At minimum, quality should be reviewed at:
- 06:00
- 12:00
- 17:30
- 23:00

### 7.3 Relighting
The scene should support relighting that changes with time of day.

At minimum, implement:
- ambient light
- primary directional light
- support for scene-aware relighting instead of whole-image filter hacks

Preferred design:
- daylight / window-driven light
- optional lamp-driven warm indoor contribution
- softer face treatment
- controlled hair highlights

The lighting should be anime-friendly, not harshly realistic.

### 7.4 Debug control panel
The prototype must include a debug panel with controls for at least:
- realtime on/off
- time slider
- dawn/noon/dusk/night quick jump
- ambient strength
- main light strength
- main light direction or time-driven direction
- exposure
- normal strength
- animation master toggle
- debug view selector

Optional but recommended:
- lamp light intensity
- face lighting strength
- hair lighting strength
- bloom toggle / intensity
- breathing toggle
- blink toggle
- steam toggle

### 7.5 Debug view modes
The prototype should support some debug views when possible:
- final
- base image
- normal map
- masks
- lighting-only or similar helpful mode

---

## 8. Visual feature requirements

### 8.1 Time-of-day visual targets

#### Dawn / morning
- fresh, soft, slightly cool-to-neutral light
- gentle overall atmosphere
- no harsh contrast

#### Noon
- brighter, clearer, balanced neutral light
- scene should feel clean and readable
- avoid washed-out flatness

#### Dusk
- warm window light should become more noticeable
- hair edges and some surfaces may receive soft rim light
- scene should feel especially beautiful here

#### Night
- cooler outside ambience
- warmer interior lamp contribution
- maintain readability of character face
- avoid crushing the image into darkness

### 8.2 Post-processing
Recommended but should remain subtle:
- exposure
- tone mapping
- mild bloom
- gentle color grading

Do NOT overdo post-processing.

### 8.3 Micro-animation
Target micro-animation features:
- blinking
- subtle breathing
- very slight hair motion
- coffee steam

These must remain understated and elegant.

---

## 9. Asset generation / processing requirements

The project may generate technical assets derived from the main hero image.

Potential assets include:
- normal map
- region masks
- blink frames / blink overlays
- steam sprite(s)
- helper textures

These should be placed under a generated-assets directory.

### Important asset rules
- preserve registration where applicable
- do not change character identity
- do not redesign the scene
- document generated assets and their purpose

For MVP, it is acceptable to start with approximations and improve later.

---

## 10. Rendering / architecture expectations

Preferred technical direction:
- Vite
- TypeScript
- React only for debug UI if desired
- rendering engine separated from app framework
- WebGL2-based rendering preferred

The renderer should eventually be portable.

A desirable later API shape:
- `createLivingHero(canvas, options)`
- `setTime(minutes)`
- `setRealtime(enabled)`
- `setDebugView(mode)`
- `setReducedMotion(enabled)`
- `destroy()`

---

## 11. Quality constraints

### 11.1 Aesthetic constraints
Must preserve:
- softness
- calmness
- elegance
- anime illustration coherence

Avoid:
- plastic-looking face lighting
- hard-edged incorrect shading on eyelids
- exaggerated fake 3D motion
- noisy artifacts
- visual clutter

### 11.2 Performance constraints
Desktop-first.
Should remain reasonably smooth on a modern desktop machine.

Recommended:
- avoid excessive render passes
- consider DPR capping if needed
- pause or reduce work when tab is hidden
- respect `prefers-reduced-motion`

---

## 12. Documentation requirements

Maintain basic documentation during development:
- architecture notes
- asset notes
- generation or prompt logs
- validation screenshots
- known issues / next steps

Suggested folders:
- `docs/prompts/`
- `docs/logs/`
- `docs/screenshots/`

---

## 13. Acceptance criteria

This phase is considered successful if all of the following are true:

1. The prototype runs locally.
2. The hero image is displayed correctly.
3. Manual time scrubbing works.
4. Realtime mode works.
5. The scene visually changes across the day in a smooth and convincing way.
6. The result feels more like a living scene than a static wallpaper.
7. The character still feels like Black Sister 1.0.
8. The visual quality at dawn / noon / dusk / night is acceptable.
9. The implementation is documented well enough to continue development or later migrate into the Blog project.
10. The core rendering logic is not tightly bound to the final Blog app.

---

## 14. Recommended implementation phases

### Phase 0
Project bootstrap and minimal full-screen display of the base hero image.

### Phase 1
Time system + debug panel + first relighting MVP.

### Phase 2
Improve anime-friendly relighting behavior.

### Phase 3
Add controlled post-processing.

### Phase 4
Add subtle micro-animation.

### Phase 5
Visual QA, screenshots, cleanup, and extraction readiness.

---

## 15. Reference inspiration

This project is inspired by the workflow idea seen in KumengScreen:
- separate requirement doc
- separate normal/blink prompt assets
- 24h light-change target
- base image + normal-map relighting pipeline
- subtle character motion

However, this project must use my own character and my own approved hero artwork, and it should be implemented as an independent experimental project first.