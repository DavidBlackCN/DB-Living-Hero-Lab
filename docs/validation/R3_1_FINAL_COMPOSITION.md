# R3.1 Final Lit composition

Status: full Lit composition validated; **R3 Breathing v1 frozen**. The approved 5.2-second period, 4.8-source-pixel core displacement, protected regions, Blink timing/assets, LeafField motion/assets, and R2A/R2B Lighting/Sky curves remain unchanged.

## Why Lit previously omitted Blink and Leaves

`LivingHero.vue` mounted `BlinkLayer` and `LeavesLayer` only for `renderView === 'base'`. This was a Debug view restriction from their original integration. Leaves already draw in their own transparent Canvas2D layer and need no WebGL rewrite. Blink could not simply use its Base-view DOM patch above Lit: an unlit, original-color eye patch would bypass the time-of-day lighting and could become bright or lose its Dusk warmth.

## Final composition

1. The Lit WebGL fragment shader samples Base Albedo at the Breathing-deformed source UV.
2. While Blink is closed, it alpha-composites the two unchanged registered local-eye sprites into that Albedo. The approved `BlinkTimeline` still determines open/closed timing. Base inspection retains its existing DOM patch; Normal inspection shows the Normal map alone.
3. The same deformed UV samples frozen Normal v3. The resulting material passes through the existing Runtime Lighting exposure, then the registered Sky composite. The closed eye therefore inherits Dawn/Noon/Dusk/Night color and brightness, using the existing Normal at that position.
4. Leaves v1 remains a separate Canvas2D overlay above the WebGL scene. A small CSS tone bridge from the *same* preview minutes reduces its brightness from 1.0 by day to 0.48 at Night and its saturation from 1.0 to 0.60. Dawn and Dusk transition smoothly. LeafField texture, density, trajectory, wind and frame cap were untouched.

The default Lit view now mounts Blink and Leaves alongside Breathing, Lighting and Sky. All existing toggles work in Lit. Base remains the albedo/Blink registration view; Normal remains a clean map inspection view. The production scene adds no global animation loop: Breathing drives at most 30 WebGL draws/s, Blink requests a redraw at its two state edges, Leaves retains its independent ≤30 FPS Canvas2D loop, and the realtime clock retains its low-frequency tick.

## Four-phase and regression evidence

Edge/WebGL2 ran the full Lit composition for at least 18 seconds at each preview anchor: [Dawn](r3-final-composition/dawn.png), [Noon](r3-final-composition/noon.png), [Dusk](r3-final-composition/dusk.png), [Night](r3-final-composition/night.png). Across the four views, 15 automatic Blink closures were observed while Breathing and Leaves remained active. [Night full-composition clip](r3-final-composition/lit-full-composition.gif) and [Night closed-eye frame](r3-final-composition/night-full-closed.png) show all five modules simultaneously.

For isolated closed-eye checks, the mean RGB change inside the eye region was Dawn 9.02, Noon 9.91, Dusk 8.64, Night 4.94. [Dusk closed](r3-final-composition/dusk-closed.png) retains the warm light; [Night closed](r3-final-composition/night-closed.png) stays dark. Visual inspection found no bright patch seam or eye-position jump. The torso-only Breathing region keeps the head and Blink coordinates still. The Night leaf tone is subdued relative to the original orange overlay without making leaves disappear.

With Breathing, Blink and Leaves OFF, all four Lit artwork screenshots matched the frozen R2B anchors within one RGB level outside the Debug Panel. The repeated 97-frame 24H audit passed unchanged: Noon/12:45 artwork peak 0.22088; evening face minimum 0.01819 remains above Night 22:00 face 0.01793; midnight wraps consistently. Sky assets and timeline were not modified.

Reduced motion keeps Lit/Realtime Lighting and Sky, and disables Breathing, Leaves and automatic Blink. Static quality removes the active animations. Hidden-page testing found a stable frame, open eyes, and a clean resume without accumulated motion. The browser's synchronous CPU WebGL draw reading stayed around 0.5 ms in the headless Edge run; this does not measure GPU time. No permanent global 60 FPS RAF was added.

Commands passed: `pnpm build`, `pnpm typecheck`, `python scripts/validate_blink_normal.py`, `python scripts/validate_time_controller.py`, `python scripts/validate_breathing.py docs/validation/r3-regression-tmp --strength 1.0`, `python scripts/validate_final_composition.py`, and the 97-frame `scripts/audit_lighting_24h.py`. The R2A/R2B static capture scripts now switch all three dynamic modules off before frozen-image comparisons.
