# 单屏独立场景页

替代 `1ff80bc` 的滚动博客示例。按用户提供的 KumengScreen 截图组织页面：左上品牌、左侧实时时钟/日期/短句、右侧竖排场景名、右下控制台与光影抽屉。删除项目卡片、关于区、页面锚点及外部跳转链接。品牌按钮无导航行为，其余控制在本页真实生效。

## 控制

- 大时钟显示本地时间，单独的场景控制台显示 24H 预览时间。复用 TimeController，不创建第二个昼夜动画时钟；实时时钟 1s 更新，hidden 时停止。
- 拖动时间、四时段、Play/Pause、回到此刻、动效总开关、Base/Normal/Lit 视图、浏览器全屏、沉浸模式。
- 光影抽屉：曝光补偿、泛光强度、阈值、方向明暗、边缘柔和、饱和度及质量档。手动保留覆盖值；恢复自动移除覆盖并使用冻结时段曲线。曝光是相对时段的 EV 补偿。
- 沿用参考的信息组织，选项映射本引擎已有参数。没有伪造本引擎不支持的泛光半径控件，也没有改写头发材质逻辑。
- 新增组件可选 `motion`、`view`、`adjustments` props；默认值不改变现有成图。没有 shader、素材、运动曲线或时段曲线变更。
- 原底图→Lit 入场继续保留。抽屉支持原生焦点限制、Esc、外侧点击与返回按钮焦点。reduced-motion 禁用动画/Play；抽屉取消入场运动。

## 部署

`vite.config.ts` 使用 `base: './'`。`pnpm build` 后部署整个 `dist/` 内容到静态 HTTP(S) 服务即可。实际用 `http://127.0.0.1:4174/dist/` 检查了子目录部署，资源、动态 chunk、WebGL 初始化均成功。没有外部字体、接口或 CDN 依赖；无需路由重写或 Plume。未发布到远端。

## 验证

- `pnpm typecheck`、`pnpm build`、公开组件 SSR 通过。
- `python scripts/validate_standalone.py`：构建产物子路径加载、无跳转/无纵向滚动、六项实际渲染调节、自动恢复像素一致、Canvas 无重建、时间/Play/实时、Fullscreen/沉浸、手机布局、reduced-motion 全部通过；JS 错误为 0。
- `python scripts/validate_homepage.py --visual`：新组件默认参数的四时段与 R7.4 冻结图一致（仅排除历史图里旧 Debug 按钮的 50×24px）。
- 桌面人工查看了四时段与抽屉，标题/大时钟没有覆盖人物。手机使用上下留白容纳时钟与控制台，中间完整横幅，不裁掉人物；抽屉内部可滚动，页面本体不滚动。

## 素材

- [四时段](standalone/four-phases.jpg) / [Night](standalone/night.png)
- [光影抽屉](standalone/lighting-drawer.png)
- [沉浸模式](standalone/immersive.png)
- [手机](standalone/mobile.png) / [手机抽屉](standalone/mobile-drawer.png)
- [实际交互检查数据](standalone/checks.json)

完成后等待人工验收，不进入下一视觉阶段。
