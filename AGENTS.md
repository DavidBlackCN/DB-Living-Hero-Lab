# Project rules for development agents

- Stack: Vite + Vue 3 + TypeScript + native WebGL2 + **pnpm**. Never npm/yarn. Node version and pnpm version are recorded in `.nvmrc` / `package.json`.
- Current product: standalone single-screen page. VuePress 2 / Plume integration remains a future host task; keep `src/engine/**` independent of Vue and the page layer thin.
- Start with `docs/STAGE_CHECKPOINT.md`. Public interfaces: `docs/VUEPRESS_INTEGRATION.md`; asset registration: `docs/ASSET_PLAN.md`; animation: `docs/ANIMATION_PLAN.md`.
- Artwork Space is **1672×941**, top-left origin. Base, Normal v3, local Blink, registered masks and lighting are frozen. Only change visual logic when the task explicitly requires it. No whole-frame Blink; current Blink is continuous local-eye blending. Leaves v2 is accepted.
- Preserve current Sun/Moon, Atmosphere, Lamp, Motion and time curves during UI/integration/maintenance tasks. Do not add masks, patches or abstractions without a concrete need.
- `public/assets/hero/` contains only runtime assets. Offline inputs belong in `sources/hero/`; do not delete a source merely because the renderer does not load it. Check generators and validators too.
- Put intermediate screenshots, recordings and test reports under ignored `artifacts/`. Only deliberately selected final evidence belongs in `docs/validation/final/` or `motion/`. `baseline/` is a test oracle: never overwrite it just to make a test pass.
- Keep current-state documentation short. Replace superseded instructions instead of appending another stage diary. Git is the historical archive; do not retain old before/after collections indefinitely.
- Before deleting files, inventory callers, script imports, generator inputs and doc links. Verify resolved deletion/move paths stay within the intended repository directory. Do not rewrite Git history or touch unrelated user changes.
- After changes run `pnpm typecheck` and `pnpm build`. Run `python scripts/validate_repository.py` for cleanup/assets/docs changes. Blink/Normal changes also require `python scripts/validate_blink_normal.py`. Other focused commands are in `docs/validation/README.md`.
- Keep generated output out of commits; preserve a concise review record for significant work. Commit locally when requested/authorized; do not push unless explicitly asked.
