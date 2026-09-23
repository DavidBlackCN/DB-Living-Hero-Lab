# DB Living Hero 2.0 Lab

独立的 Vue 3 + WebGL2 实验工程，为未来迁入 VuePress 2 / Plume 的 Blog 首页准备。当前显示冻结的 Base Albedo，并接入第一版轻量动态落叶；Normal、Lighting 等后续模块尚未实现。

## 运行

建议 Node 24，使用 pnpm 10.28.2：

```bash
pnpm install
pnpm dev
pnpm typecheck
pnpm build
pnpm preview
```

Debug 面板可切换 Renderer、Leaves、Fit、Quality、Artwork Bounds、UV Grid 和闭眼候选图静态预览，并显示叶子数量。候选图预览只是整张图片切换，不是 Blink 动效。Fit 的 `auto` 在宽屏使用 cover、窄竖屏使用 contain；Quality 的 `auto` 在系统要求 reduced motion 时使用静态 Base，Leaves 则在 reduced motion 时始终关闭。`balanced` 可用于检查 WebGL。其余动画控件为禁用占位。

源码入口是 `src/app/`；可迁移核心在 `src/engine/`、`src/shaders/`、`src/config/`。两张图片位于 `public/assets/hero/`。阶段 1 的需求和验收见 `docs/`，早期草案保存在 `docs/archive/`。
