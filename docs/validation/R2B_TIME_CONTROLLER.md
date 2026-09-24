# R2B 24H Runtime Timeline and Time Controller

Status: engineering and browser validation complete; ready for human acceptance. R2A Runtime Lighting and Sky artwork/curves are frozen and unchanged.

## Model and interaction

`src/engine/time/TimeController.ts` owns one `TimeSnapshot` (`realtime`, `manual`, or `playing`; minutes). It has no Vue dependency. `LivingHero.vue` bridges that one minutes value to both `createLightingStateForTime(minutes)` and `skyFor(minutes)`, preserving the Debug Sky toggle. The default view is Lit, and the controller reads the device's local `Date` on startup.

| Action | Result |
| --- | --- |
| Drag 0–1440 minute slider or choose Dawn 06:30 / Noon 12:00 / Dusk 17:30 / Night 22:00 | Enter Manual and freeze at the selected time. |
| Back to now | Enter Realtime, immediately reread local device time, and resume low-frequency updates. |
| Play | Start from the displayed time; one 24-hour cycle takes 60 real seconds. |
| Pause or drag while playing | Cancel playback RAF and remain at the displayed time in Manual. |
| Cross 24:00 during playback | Wrap to 00:00 and continue. Manual slider can still show 24:00 as an endpoint. |

Realtime uses one 1000 ms interval, not a permanent RAF. `clockMinutes()` includes seconds and milliseconds for smooth lighting between ticks; `HH:mm` and the slider display whole minutes. Playback uses RAF timestamp delta at `1440 / 60000 = 0.024` simulated minutes per millisecond, independent of refresh rate. The controller cancels its previous driver before any mode transition, so interval and playback RAF do not coexist.

When the document becomes hidden, the active driver stops. On return, Realtime rereads the current device time; Playing resumes from its held preview time without accumulating hidden elapsed time. Reduced motion retains Realtime and Manual Lit/Sky rendering, disables the Play control, and pauses playback if the preference changes while it is running. Blink and Leaves retain their existing reduced-motion behavior. Explicit Static quality still shows the static Base.

## Verification

`python scripts/validate_time_controller.py` ran in Edge/WebGL2. It checked startup at mocked local 23:30, Realtime mode, all four preview buttons and Manual freeze, Back to now, playback from 00:00/06:30/17:30/22:00 at 60 seconds per day, Pause freeze, playback wrap, manual 00:00 = 24:00, hidden playback pause/resume, hidden Realtime refresh, and reduced-motion Play disable with Lit renderer retained. Four [current anchor captures](r2b-time-controller/) matched the frozen [R2A anchors](r2a5d-final/) pixel-for-pixel outside the changed Debug Panel.

The [97-frame 15-minute audit](r2b-time-controller/24h-audit/hourly-contact.png) passed: Noon artwork luminance `0.22088`; day peak at 12:45 also `0.22088`; evening face minimum `0.01819` stays above Night 22:00 `0.01793`. Artwork luminance stays near `0.0167–0.0169` at 20:00, 22:00, 00:00, 02:00, 04:30, and 05:00, without renewed brightening. The 00:00 and 24:00 image measurements are identical. Data: [15-minute CSV](r2b-time-controller/24h-audit/luminance-15min.csv).

`pnpm build` and `pnpm typecheck` passed. No R2A aesthetic parameters or frozen assets changed.
