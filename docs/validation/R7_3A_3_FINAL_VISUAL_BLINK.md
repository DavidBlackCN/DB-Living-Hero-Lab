# R7.3A.3 — Night edge and Blink review

The reported Dawn sky block is **deferred at the user's request** until a reproducible location is supplied. No Dawn compensation layer or sky color adjustment was made. Fixed captures at 05:00, 06:00, 06:30, 07:00, and 08:00 did not reproduce a stable block, so Dawn is not claimed as fixed.

## Night diagnosis and change

Pass isolation showed that turning Sky off exposes the old bright Base sky near the hair and rose. Bloom and the narrow hair sheen contribute very little to the reported halo. The Sky plate and its edge coverage previously sampled the stationary screen UV while Base, reconstruction, and Character Motion sampled the displaced artwork UV. The mismatch is visible around a moving silhouette. All Sky RGB and alpha sampling now follows the same displaced UV. The broad Normal architecture Moon add-on was also reduced from 0.34 to 0.24 to make the tower beside the rose less prominent, without a head-centered mask or display darkening. Night remains directionally lit; no character or time curve was changed.

Review: [Night before](r7-3a-3-final-visual/review/night-before.jpg), [Night after](r7-3a-3-final-visual/review/night-after.jpg), [head A/B](r7-3a-3-final-visual/review/night-head-before-after.jpg), [motion head A/B](r7-3a-3-final-visual/review/night-motion-head-before-after.jpg), [Bloom / sheen / Sky-repair audit](r7-3a-3-final-visual/review/night-pass-audit.jpg), and [Moon response OFF](r7-3a-3-final-visual/review/night-moon-response-off.jpg). The static improvement is subtle. The motion-aligned boundary is the meaningful change; final subjective acceptance remains with the user.

## Blink

The former 115 ms boolean Closed window is replaced by a 320 ms continuous amount:

`amount = sin(π · age / duration)^0.6`

The existing registered local-eye RGBA patches blend into Albedo before the normal lighting path. Iris glint fades with the same amount. The DOM Base-view overlay uses that amount as opacity. The random inter-blink interval, preview, hidden-tab pause, reduced-motion and on-demand rendering rules are retained. The reference envelope was checked against [KumengScreen's scene implementation](https://github.com/buger404/KumengScreen/blob/main/components/dream-scene.tsx).

Review: [rendered envelope](r7-3a-3-final-visual/blink/blink-envelope-contact.jpg), [60 fps slow preview](r7-3a-3-final-visual/blink/blink-envelope-slow-60fps.mp4), [20-second normal-speed capture](r7-3a-3-final-visual/blink/blink-normal-20s.mp4), [4K open frame](r7-3a-3-final-visual/review/blink-4k-open.jpg), and [4K closed frame](r7-3a-3-final-visual/review/blink-4k-closed.jpg). The slow preview drives the actual Vue-to-WebGL amount path through 21 captured stages and holds each stage for slow viewing; it is a rendered frame sequence, not a 60 fps real-time camera recording. The normal-speed clip samples the running page over 20 seconds, with random Blink and Character Motion enabled.

## Verification

- `pnpm typecheck`, `pnpm build`, and `python scripts/validate_blink_normal.py`: passed.
- Hair and Character coherence validators were updated to assert a continuous Blink amount instead of the deleted `.is-closed` class.
- The legacy time-controller and Post validators compare the current scene against R3 frozen screenshots; those pixel-equality checks are stale after R5–R7. Current 00:00/24:00 and twilight continuity are covered by the [Character coherence regression stats](r7-3a-3-final-visual/review/stats.json): 00:00/24:00 maximum RGB delta 0, adjacent ten-minute mean RGB delta under 12 through both twilights.
- No Base, Normal, Sky RGB, lamp, leaf, or motion amplitude asset was changed. R7.3B has not started.
