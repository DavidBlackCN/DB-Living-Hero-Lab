# Breathing Visibility Follow-up

Status: EXPERIMENTAL / awaiting human acceptance. Default remains OFF.

The user reported no perceptible motion other than Blink. A real-clock Chromium
run at 1440 x 900 clicked the actual checkbox and sampled seven frames over
5.4 seconds. Phase advanced through 0, .154, .330, .497, .667, .833, .003;
the shader's uBreathingAmount rose to 1.7998 and returned to zero. There was no
reproduced scheduling/checkbox failure on this machine. This does not establish
the user's exact browser state. It demonstrates that the previous safe-pixel
tests were insufficient to establish perceptual effectiveness.

At that viewport the former 1.8 source-pixel peak was only 0.675 CSS pixels;
quadratic radial attenuation made most of the small support even weaker.
The response was too conservative to reliably read as breathing.

Changes:
- Retain the same ellipse, front-lock exclusion, semantic inset, UV registration,
  cycle and lifecycle. No light/Blink/Steam asset or formula changes.
- Replace squared radial attenuation with `1-smoothstep(.15,1,rSquared)`.
  This broadens the participating interior without moving its outer boundary;
  support still smoothly reaches zero before the silhouette.
- Default strength 2 source pixels, configurable 0-3, within the original brief's
  recommended range. At 1440 width the peak is .75 CSS px by default or 1.125 px
  at strength 3. The cycle remains 5.4 seconds and default enable remains false.
- Add explicit Running/Off/blocked state and live source-pixel displacement.
  Diagnostics expose reduced motion, animation off, refinement off, missing mask,
  zero strength, hidden state, lost context and destruction.
- Add a real-clock checkbox test (without Playwright fake time) that confirms
  shader motion and status changes for disabling conditions.

Validation outputs: `docs/screenshots/breathing-visibility/breathing/`.
The existing OFF reference test and protected-region tests remain unweakened.
The historical first-prototype log retains its original parameters and results.

Validation: typecheck and build passed, unit tests 14/14, full visual regression
69/69 (4.4 minutes). The added real-clock checkbox/status test passed. All 84 OFF
time/view comparisons match the accepted shader. At default strength, changed
pixels inside support are dawn 5211 / noon 5245 / dusk 5119 / night 3532;
outside support remains 0 at every time. Bloom-enabled face/neck/hands/book/hair
closeups remain unchanged. Screenshots were inspected for local seams and hair
boundary movement; none were apparent. Perceptual acceptance remains open.

The effect is still intentionally small and limited to garment interior. This is
not full torso/head breathing. No claim of perceptual acceptance is made; review
with Blink/Steam off for one or two cycles, then with them restored. A larger
whole-character movement remains outside scope. WORK.md and work/ are excluded.
