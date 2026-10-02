# DB Living Hero 2.0 Lab

可独立部署的 Vite + Vue 3 + TypeScript + WebGL2 单屏场景页。当前包含已冻结的 24H Runtime Lighting、Character Lighting、Atmosphere、Blink、Breathing、Hair、Leaves 与 Lamp。页面提供实时时钟、昼夜预览、光影调节抽屉、全屏与沉浸模式；没有跳转链接或下滑内容。

## 运行

建议 Node 24，使用 pnpm 10.28.2：

```bash
pnpm install
pnpm dev
pnpm typecheck
pnpm build
pnpm preview
```

## 独立部署

运行 `pnpm build`，将 **dist 目录里的全部内容** 原样上传到静态 HTTP(S) 站点。构建采用相对资源路径，可以部署到根目录或 `/living-hero/` 等子路径；不需要 VuePress、服务器 API 或路由重写。请通过 HTTP(S) 访问，不要直接双击 HTML。`pnpm preview` 用于本地检查产物。

右下方控制台支持 24H 拖动、四时段、播放/暂停、恢复实时与动效开关。“光影调节”打开抽屉，调整曝光补偿、泛光、高亮阈值、方向明暗、边缘柔和与色彩饱和；“恢复昼夜自动”还原冻结参数。大时钟始终显示真实本地时间，控制台显示场景预览时间。`H` 切换沉浸，`Esc` 关闭抽屉或退出沉浸。所有操作留在当前页面。

移动竖屏使用 contain 保留完整构图；低质量档或系统 reduced-motion 会减少/停用动态，WebGL 不可用时显示底图。开发用 DebugPanel 仍可通过组件 `debug` prop 开启，独立页面不展示技术调试面板。接入接口见 [组件文档](docs/VUEPRESS_INTEGRATION.md)，本轮未进行 Plume 联调。

源码入口是 `src/app/`；可迁移核心在 `src/engine/`、`src/shaders/`、`src/config/`。美术资产位于 `public/assets/hero/`。当前阶段状态与下一步见 [`docs/STAGE_CHECKPOINT.md`](docs/STAGE_CHECKPOINT.md)；早期草案保存在 `docs/archive/`。
