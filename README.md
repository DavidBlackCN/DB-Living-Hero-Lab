# DB Living Hero 2.0 Lab

独立的 Vite + Vue 3 + TypeScript + WebGL2 实验工程，为未来迁入 VuePress 2 / `vuepress-theme-plume` 的 Blog 首页准备。当前已接入冻结的 Base Albedo、局部 Blink v1、冻结的 Normal v3 和轻量 Leaves v1。正式 24h Runtime Lighting 尚未开始；当前 Normal View / Test Light 是验证视图。

## 运行

建议 Node 24，使用 pnpm 10.28.2：

```bash
pnpm install
pnpm dev
pnpm typecheck
pnpm build
pnpm preview
```

Debug 面板可切换 Renderer、Leaves、局部 Blink、Normal map / Test Light、Fit、Quality、Artwork Bounds 和 UV Grid，并显示叶子数量。Preview Blink 触发一次局部眨眼；整图闭眼切换已废弃。Fit 的 `auto` 在宽屏使用 cover、窄竖屏使用 contain；Quality 的 `auto` 在系统要求 reduced motion 时使用静态 Base，Leaves 和自动 Blink 在 reduced motion 时关闭。`balanced` 可用于检查 WebGL。Breathing、Hair Motion 和 Runtime Lighting 尚未实现。

源码入口是 `src/app/`；可迁移核心在 `src/engine/`、`src/shaders/`、`src/config/`。美术资产位于 `public/assets/hero/`。当前阶段状态与下一步见 [`docs/STAGE_CHECKPOINT.md`](docs/STAGE_CHECKPOINT.md)；早期草案保存在 `docs/archive/`。
