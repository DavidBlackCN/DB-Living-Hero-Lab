# Stage 1 acceptance checklist

- [x] `pnpm install` 成功且生成 `pnpm-lock.yaml`
- [x] `pnpm typecheck` 成功（由 `pnpm build` 内执行；单独命令也执行）
- [x] `pnpm build` 成功
- [x] `pnpm dev` 页面可打开，Base 无黑屏
- [x] WebGL2 Canvas 正确显示 Base
- [x] 宽屏 cover、contain 与 390×844 竖屏 Auto 适配已在浏览器检查
- [x] Renderer 关闭与 Static preset 均显示 `<img>`
- [ ] reduced motion、WebGL 不可用和 context lost 的真实设备路径仍需专项验证；代码已接入静态回退
- [x] Debug 控件、Artwork Bounds、UV Grid 可用；未实现模块标明禁用
- [x] 不存在 `package-lock.json` / `yarn.lock`
- [x] 人工视觉检查图像方向、裁切与构图
