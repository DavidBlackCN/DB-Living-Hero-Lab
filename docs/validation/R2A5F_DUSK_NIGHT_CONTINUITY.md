# R2A.5f Dusk-to-Night continuity and full 24H audit

Status: the post-Dusk dark dip reported during human review has been corrected. The four preview anchors and the Sky Timeline are unchanged; await human review before R2B.

## Cause and correction

The 17:30 Dusk Key/Ambient boosts were falling away by 18:30, before the deep-night blue-gray fill reached its stable level. The 18:30 face and white sleeves therefore became darker than the later Night state, then brightened again. In the before capture, face mean linear luminance was `0.01342` at 18:30 versus `0.01793` at 22:00.

The Runtime Lighting energy scalars—Key intensity, Ambient intensity, and exposure—now interpolate smoothly from the existing 17:30 Dusk state to the existing 20:00 Night-hold state. This matches the Sky Layer's Dusk → Night transition window. Solar direction, colors, diffuse band, Sky assets and shader remain on their existing curves. The endpoint states are sampled from the model, so all four preview anchor frames remain pixel-identical to R2A.5e.

## Visual comparison

- [Before: 17:30–22:00](r2a5f-before-evening/contact.png) · [After: 17:30–22:00](r2a5f-final-evening/contact.png)
- [18:30 before](r2a5f-before-evening/1830.png) · [18:30 after](r2a5f-final-evening/1830.png)

| Time | Face before | Face final | White shirt final |
| --- | ---: | ---: | ---: |
| 17:30 | 0.10985 | 0.10985 | 0.16902 |
| 18:00 | 0.02717 | 0.06555 | 0.10062 |
| 18:30 | 0.01342 | 0.04202 | 0.06419 |
| 19:00 | 0.01805 | 0.03427 | 0.05275 |
| 19:30 | 0.01824 | 0.02263 | 0.03492 |
| 20:00 | 0.01819 | 0.01819 | 0.02815 |
| 22:00 | 0.01793 | 0.01793 | 0.02796 |

Values are mean linear luminance in the existing diagnostic face and shirt regions. The final evening progression no longer drops below Night before recovering.

## Complete 24H check

The Edge/WebGL2 Lit/Sky-on page was rendered at every 15-minute step from 00:00 through 24:00 inclusive: 97 frames. The [hourly visual contact sheet](r2a5f-24h-audit/hourly-contact.png) and [15-minute luminance data](r2a5f-24h-audit/luminance-15min.csv) are archived.

- The brightest artwork frame from 06:30–17:30 was 12:45 at `0.22088`, equal to Noon within measurement precision; the morning and afternoon overbright peaks remain fixed.
- The minimum face luminance from 17:30–20:00 was `0.01819`, still above the 22:00 Night value `0.01793`; the evening dark dip is fixed.
- Night holds from 20:00 through 05:00. The 00:00 and 24:00 artwork measurements match, and the Sky and Lighting models still wrap to the same state.
- The hourly frames show continuous dawn brightening, controlled Noon, warm Dusk, and a gradual descent into deep blue-gray Night without a phase cut.

`pnpm build` and `pnpm typecheck` passed. No new animation or later-stage feature was added.
