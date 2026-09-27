# Twilight Sun/Moon handoff continuity

## Problem and cause

The 24H preview showed a quick change of character shadow direction during
05:30–07:00 and a short brightness rebound after sunset. The old character
shader combined independent intensity thresholds, a Sky Night weight, and two
`max()` bridge terms. Around 06:05–06:20, the Moon term fell much faster than
the Sun term rose. The morning light-energy curve also met the 06:30 preview
anchor with a slope discontinuity. At dusk, key colors became cool by about
18:00 while the Sky was still predominantly Dusk.

## Correction

- The character Sun contribution now follows Sky twilight and solar readiness.
  The Moon handoff uses its complementary weight, instead of separate bridge
  thresholds. Both still use the existing continuous Sun/Moon directions.
- Light intensity, ambient intensity, and display exposure ease from 05:30 to
  the unchanged 06:30 Dawn anchor. The established small predawn ambient fill
  remains after interpolation.
- Dusk key and ambient colors ease from the unchanged 17:30 Dusk anchor to
  the Night hold over 17:30–20:00, matching the existing Sky transition.
- Sky RGB, `skyFor()`, Moon direction, character materials, Post, and motion
  were not changed. No new local face or shadow patch was introduced.

## Visual audit

The [before contact](twilight-handoff/final/before-contact.png) and
[after contact](twilight-handoff/final/after-contact.png) compare frozen frames
across both transition windows. The [four preview anchors](twilight-handoff/final/four-anchors.png)
show Dawn, Noon, Dusk, and Night after the fix. The
[five-minute data](twilight-handoff/final/twilight-5min.csv) records light,
Sky, direction, luminance, and frame difference for 05:20–07:20 and
16:40–20:20. Motion was disabled for the pixel comparison.

The largest five-minute face-region image change near sunrise fell from 6.96
to 5.09 mean RGB levels. The old evening face luminance rose from 45.3 at
18:50 to 48.7 at 19:10; the corrected sequence declines from 50.2 to 47.7.
The Sky itself was not retimed, so its intended twilight change remains
visible. At the four fixed anchors, Noon/Dusk/Night are pixel identical to
the preceding review candidate; Dawn differs by at most one RGB level due to
the new Sun readiness gate.

The [full-day audit](twilight-handoff/final/full-day-contact.png) also checked
the Night hold and midnight wrap. `00:00` and `24:00` match; the late-night
period does not brighten again.

## Verification

- `pnpm build` — passed
- `pnpm typecheck` — passed
- `python scripts/validate_lighting_detail.py` — passed
- `python scripts/audit_lighting_24h.py` — passed
- `git diff --check` — passed

This is a twilight continuity correction within the current lighting review;
it does not advance to R7.
