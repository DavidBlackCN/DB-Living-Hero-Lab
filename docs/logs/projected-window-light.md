# Projected Window Light

Date: 2026-09-16

## Window mask diagnosis

The former single `window` path was an approximate union whose lower points extended into the sill and desk region. Because the generated SVG feathered that union, shader thresholding could not restore the real frame boundary. The temporary `windowEdge` UV cutoff was removed.

The source now contains two glass-only contours: `windowGlassLeft` and `windowGlassRight`. Their lower edges follow the visible slanted glass/frame boundaries in the approved hero reference. The asset generator renders only these contours as exterior red mask data; frame, sill, desk, vase, books, and indoor objects remain excluded or occluded by the existing scene regions.

## Projected light

Projected Window Light is an independent screen-space art-directed contribution. It uses a rotated soft band with a time-varying axis, origin, reach, and intensity. The contribution is constrained by the corrected exterior mask, scene receiving mask, hair/body regions, and face protection. It is not a physical shadow map or cast-shadow simulation.

Defaults are enabled with intensity `0.42` and softness `0.22`. The effect is active during daylight, broader and cooler in the morning, shorter and more neutral near noon, and lower-angle/warm with stronger separation at dusk. It is zero at night. Debug UI exposes an on/off control, intensity, softness, and `Projected Light Only` view.

## Validation

Playwright captures Final, Neutral, and Projected Light Only at 08:00, 12:00, and 17:30 under `docs/screenshots/projected/`, plus Night Scene, Overlay, and Final captures. These are intended to verify grayscale spatial differences and the corrected lower glass boundary.

The temporary normal remains `normal-low-frequency.svg`; it is not a substitute for a registered high-quality normal. Once that asset arrives, projected contribution should be recalibrated downward rather than removed, and the scene mask should be rechecked against its finer receiver detail.

Blink remains blocked: `Blink renderer implementation: blocked by missing registered closed-eye asset.`
