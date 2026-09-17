# Window lower interior stripe correction

The user's red-box screenshot exposed an error missed in the previous review.
Checking only exterior R=0 below the glass was insufficient: Scene G (indoor
receivers) had a misplaced shelf polygon that painted a diagonal light band
through the apron, tool holder and area below the picture frame. This created
the apparent continuation of a window overlay into the room.

Source-grid inspection uses 1200×675 coordinates. `lampSill` previously started
at (871,318) and (1200,373), above the actual shelf. It now follows (884,342) to
(1200,395), with the front edge extending to y=368…428. A separate
`penHolderReceiver` covers the holder body down to y=358…360; the old pen-tip
occluder ended at y=333…336 and was insufficient as an indoor receiver.

Only region data and generated receiver/contact maps changed. The shader,
glass anchors, lights and UI are unchanged. Exterior debug is pixel-identical
at 06:00 / 12:00 / 17:30 / 23:00. The visible correction is the removal of the
false indoor stripe, not a fabricated change to the already-bounded glass R.
Sill-clipped contact strokes regenerate against the corrected shelf.

Validation:

- Typecheck, build, 7 unit tests: PASS.
- Eight lighting-shadow/window visual tests: PASS, including four-time captures.
- Added source-position regression: apron has no shelf receiving G; actual shelf
  receives light; holder coverage remains continuous through its lower body.
- Corrected the old test's mislabeled sill probe (970,341)…(1000,349), which
  actually sampled the holder. New real shelf probe: (1076,385)…(1090,392).
  The original brightness/falloff thresholds are unchanged. Both affected tests
  passed on targeted rerun (nine distinct relevant tests passed overall).
- No runtime passes, textures, shader instructions or dependencies were added.
- As before, test-owned Vite processes needed termination after all tests finished
  for Windows teardown to return the successful summaries.

Review [before/after crop](../screenshots/window-interior-fix/comparison.png) and
[gallery](../screenshots/window-interior-fix/README.md). The original artwork's
baked shadows and the room's natural night shading remain; this fix targets the
misregistered mask boundary identified by the user.
