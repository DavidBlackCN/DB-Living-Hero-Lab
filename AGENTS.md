# Project rules for development agents

- Stack: Vite + Vue 3 + TypeScript + native WebGL2 + pnpm. Use **pnpm**, never npm or yarn.
- Final destination: VuePress 2 / `vuepress-theme-plume`. Keep `src/engine/**` as independent from Vue as practical; keep the Vue page layer thin.
- Artwork Space is **1672×941**, origin at the top left. Base, Normal, and local Blink assets use this coordinate system. Every registered asset must align pixel-for-pixel with Base.
- Base Albedo and Normal v3 are frozen. Do not remake frozen art without a concrete defect. Whole-frame Blink is abandoned; use the integrated local-eye Blink.
- Add Masks / Regions only when an implementation requires them. Avoid unnecessary abstraction and overengineering.
- Visual motion should stay restrained, natural, and low-distraction. Leaves v1 and local Blink v1 are accepted; Half Blink is optional.
- After changes, run `pnpm build`. For Blink or Normal changes, also run `python scripts/validate_blink_normal.py`.
- Update `docs/` for significant phase changes. Start with [`docs/STAGE_CHECKPOINT.md`](docs/STAGE_CHECKPOINT.md); detailed asset and animation status lives in `docs/ASSET_PLAN.md` and `docs/ANIMATION_PLAN.md`.
