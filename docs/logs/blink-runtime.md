# Blink Integration - 2026-09-20

## Scope and inputs

Only Blink assets, sampling, lifecycle, minimal debug UI and tests are added.
Lighting/Shadow/Bloom/Steam algorithms and settings, normal generation, all scene
maps, hero artwork and approved input pixels remain unchanged. No new framework,
image generation, scene repaint or Blog integration.

Human-approved sources: `work/blink/approved/blink-half-approved.png` and
`blink-closed-approved.png`; Open: `work/blink/source/hero-eye-context-open.png`.
All three are 700 x 470. Open is verified pixel-identical to the runtime hero crop
at (1940,390), within the 3840 x 2160 canvas. Candidate eye boxes are not masks.

## Assets and reconstruction

Run `python scripts/prepare-blink-assets.py` from the repository root (Pillow and
NumPy). This writes `public/assets/generated/blink/blink-{half,closed}-overlay.png`
and `blink-metadata.json`, plus reproducible full/crop previews in
`work/blink/generated/` and `work/blink/notes/blink-runtime-assets.md`.
Preview PNGs stay local; runtime textures and approved inputs are versioned.
Duplicate full hero/reference files supplied under `work/blink/source/` are left
untouched and are not needed for this rebuild; it checks the runtime hero itself.

Alpha comes from max absolute channel difference against Open: 0 -> 0,
1 -> 85, 2 -> 170, >=3 -> 255. RGB is the approved RGB (straight alpha), including
transparent texels to avoid black interpolation fringes. Full replacement of
meaningful edits removes original iris/lash ghosts. There is no geometry warp.
Half covers 27,871 pixels and Closed 27,914 (about 8.5% of the crop); both have
transparent outer borders. CPU reconstruction error is <=1 code value, unchanged
pixels remain identical. Metadata records source hashes and relative filenames.

## Runtime

The optional `blinkMetadataUrl` loads/validates both textures and registration.
The demo enables Blink by default. `setBlink(false)` restores Open;
`triggerBlink()` returns whether a blink started and rejects disabled, hidden,
lost or destroyed states. `getState()` includes `blink` and `blinkPhase`.
Random idle is 2.8-5.5 s; sequence is Half 40 ms, Closed 70 ms, Half 50 ms, Open.
No double blink or frame blending is introduced. There are no independent timers.

Local top-left UV sampling composites straight-alpha sRGB pigment into the base
before correction/linear lighting/postprocessing. Original Base remains unchanged.
Existing pigment-dependent forehead/highlight lighting classifiers use source
RGB, so changed eye pigment cannot alter frozen normal/mask/light diagnostics.
GPU source textures increase by 2.51 MiB (97.24 -> 99.75 MiB; correction mode
105.15 -> 107.66 MiB). No extra render pass or full-canvas blink texture exists.

## Validation and limits

Completed: `npm run typecheck`, `npm test` (11/11), `npm run build`,
`npm run test:visual -- --workers=1` (60/60, including 7 Blink checks), and
`git diff --cached --check`. The full visual run used PowerShell
`$env:VISUAL_OUTPUT_ROOT='docs/screenshots/blink-regression'` to isolate artifacts.
Re-running asset preparation produced identical SHA-256 hashes for all three
runtime outputs. An earlier full run hit Chromium `ERR_NO_BUFFER_SPACE` during
navigation; the final full run completed without retries or failures.

Existing performance probes report no WebGL/page errors; median frames in this
local browser environment were 50 ms at DPR 1 and 100-116.6 ms at DPR 1.5.
These are not a 60 fps hardware acceptance result. Verify short-phase pacing on
the intended desktop GPU before claiming smooth production performance.

Asset preparation validates registration, dimensions, borders, reconstruction and
uncovered pixel equality. Unit tests cover all phase boundaries, randomized idle,
pause/reset, long stalls, invalid metadata and existing time/light behavior.
Playwright uses a controlled clock and synchronous post-draw readPixels; reading
later is invalid with the existing non-preserved WebGL drawing buffer.
Four-time checks require eye-region changes, exact unchanged pixels outside the
registered crop, and exact Open restoration. Further checks cover automatic and
manual triggering, all motion gates, simulated visibility changes, destruction,
unchanged technical diagnostics and no eye emission when lights are zero.
System media-query changes and a nonblank 390 x 844 contain viewport are also
tested. The existing expanded debug panel overlaps much of the artwork on narrow
screens; collapse it for inspection. Mobile UI redesign is outside this change.

Screenshots: `docs/screenshots/blink/`; full regression captures are isolated in
`docs/screenshots/blink-regression/`. See the [capture index](../screenshots/blink/README.md).
The original illustration's baked-light limitation remains. The extraction is
specific to these approved localized edits, not general segmentation. Two discrete
states at low frame rates can skip a short transition; real-device timing and
final artistic acceptance remain human review items. Visibility tests dispatch
the browser lifecycle event with a controlled hidden flag, not OS tab occlusion.
