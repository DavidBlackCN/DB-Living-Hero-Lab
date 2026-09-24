# R2A.5e Day-arc brightness correction

Status: the morning and afternoon brightness peaks reported during human review have been corrected. The four existing preview anchors and the Sky Timeline are unchanged.

## Cause

The solar-elevation `warmth` curve peaks between the 06:30 / 12:00 and 12:00 / 17:30 preview anchors. It was also multiplying dawn/dusk Key and Ambient boosts and affecting exposure. This made the intermediate frames brighter than the accepted Noon frame even though the anchor frames themselves looked correct.

At 07:32 the previous effective Key / Ambient were `0.795 / 0.601`; at 16:30 they were `1.184 / 0.581`. Noon is `0.640 / 0.380`. The previous artwork mean linear luminance was `0.2606` at 07:32 and `0.2794` at 16:30, compared with `0.2209` at Noon. See the [morning before sheet](r2a5e-before-morning/contact.png) and [afternoon before sheet](r2a5e-before-afternoon/contact.png).

## Correction

The solar model still controls direction, color, diffuse band, daylight, and Sky. The energy scalars—Key intensity, Ambient intensity, and exposure—now use smooth endpoint interpolation only through the two problematic intervals:

- 06:30–10:00: from the existing 06:30 solar state to the existing 10:00 solar state.
- 15:00–17:30: from the existing 15:00 solar state to the existing 17:30 solar state.

The endpoint states are sampled from the existing model, so there is no duplicated calibration value. Each interval meets the unmodified solar model at both ends, without a phase cut. Noon and the four preview anchors remain pixel-identical to R2A.5d. Sky hold/transition windows are unchanged.

An initial boost-fade experiment removed the high peaks but created visible mid-morning and afternoon dips. It was discarded in favor of the endpoint energy interpolation above.

## Verification

The running Edge/WebGL2 Lit/Sky-on page was captured at 06:30, 07:00, 07:32, 08:00, 08:30, 09:00, 12:00 and at 12:00, 13:00, 14:00, 15:00, 16:00, 16:30, 17:00, 17:30. The [final morning sheet](r2a5e-final-morning/contact.png) and [final afternoon sheet](r2a5e-final-afternoon/contact.png) show controlled, continuous changes. Detailed frames: [07:32 before](r2a5e-before-morning/0732.png) / [after](r2a5e-final-morning/0732.png); [16:30 before](r2a5e-before-afternoon/1630.png) / [after](r2a5e-final-afternoon/1630.png).

| Time | Before mean linear luminance | Final mean linear luminance |
| --- | ---: | ---: |
| 07:32 | 0.2606 | 0.1896 |
| 16:30 | 0.2794 | 0.2056 |
| 12:00 | 0.2209 | 0.2209 |

A separate browser sweep rendered every 15 minutes from 06:30 through 17:30. The maximum morning and afternoon artwork means were both `0.22088`, at 11:45 and 12:45 respectively, equal to Noon within measurement precision. `pnpm build` and `pnpm typecheck` passed. Await human review; do not enter R2B.
