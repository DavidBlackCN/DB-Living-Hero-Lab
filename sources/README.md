# Offline artwork inputs

These files are not runtime assets and are not deployed:

- `hero/base-normal-v1.png` → `base-normal-v2.png` → runtime Normal v3: preserved generator chain and protected-region oracle.
- `hero/blink-closed-eyes-v1.png`: extraction source for the two accepted local eyes; never use full-frame Blink.
- `hero/sky-mask.png`: matte used to generate registered sky/reconstruction plates.
- `runtime-assets.sha256.json`: frozen runtime asset byte manifest. Deliberate artwork changes require explicit review before updating it.

See [asset maintenance](../docs/ASSET_PLAN.md). Do not run generators during routine builds.
