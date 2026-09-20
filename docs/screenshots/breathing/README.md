# Breathing Prototype QA

Status: EXPERIMENTAL / awaiting human acceptance, default OFF.
Final full-suite outputs are isolated in `../breathing-regression/breathing/`.
PNG/JSON outputs are local and ignored; this index is versioned.

Regenerate (PowerShell):

```powershell
$env:VISUAL_OUTPUT_ROOT='docs/screenshots/breathing-regression'
npm run test:visual -- --workers=1
```

Files for `dawn`, `noon`, `dusk`, `night`:
- `{time}-off.png`, `{time}-on-peak.png`: identical time/exposure, OFF vs peak lift.
- `{time}-torso-off.png`, `{time}-torso-peak.png`: shoulder/chest/strap closeups.
- `{time}-weight.png`: compact garment-interior support, zero outside.
- `{time}-difference.json`: changed pixels inside/outside the permitted envelope.

Additional 1920 x 1080 Bloom-enabled pairs:
- `large-bloom-off.png`, `large-bloom-on.png`.
- `large-{face,neck,torso,handsBook,hairLeft,hairRight}-{off,on}.png`.
- `off-baseline-hashes.json`: exact accepted-shader comparison, 4 times x 21 views.

Baseline reference is Git commit `e29c635`; no historical screenshots are modified.
The original art and all runtime technical/Blink assets remain unchanged.

Final full run: 68/68 passed. OFF matched all 84 accepted time/view references.
All four isolated ON comparisons had 0 changed pixels outside the garment
envelope; Bloom-enabled protected closeups also remained identical.
