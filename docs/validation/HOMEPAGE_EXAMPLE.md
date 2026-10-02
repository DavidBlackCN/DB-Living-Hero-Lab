# R7.4 follow-up — 示例主页

基线 `6ac9692`。只整理页面与入场呈现；未进入 Plume 联调，未修改引擎、shader、素材、光照或动效曲线。

## 参考与页面

- [KumengScreen 页面](https://github.com/buger404/KumengScreen/blob/main/app/page.tsx)：借鉴全屏场景、留白文字、轻量时间控制的组织方式。
- [参考项目入场](https://github.com/buger404/KumengScreen/blob/main/components/dream-scene.tsx)：底图先展示，Canvas 就绪后呈现。
- [v1-legacy](https://github.com/DavidBlackCN/DB-Living-Hero-Lab/tree/v1-legacy)：核对实际源码与 Requirements，沿用 Black Sister / Living Hero 身份及安静温暖的方向。v1 本身是实验页，没有完整博客栏目，因此当前文案明确为示例；没有编造文章、履历或统计。

桌面：全屏 Hero、左侧标题介绍、顶部导航、底部四时段/实时切换；下方为项目/旧版/文档入口与关于区。手机：完整横幅场景、下方独立文字，避免裁掉人物或在大面积黑边上堆界面。真实链接集中在 `src/app/homepage.ts`，布局与样式在 `src/app/App.vue` / `homepage.css`。

## 抽屉与入场

- DebugPanel 改为默认关闭的右侧原生 dialog；Esc、关闭按钮、点击外侧关闭；Tab 焦点限制在抽屉中，关闭后焦点回到入口。开关只影响本地 UI，不重建 Canvas，不改变时间、Play 或视觉参数。
- 新增可选 `entrance` prop，默认关闭、示例首页开启。底图 load 后至少显示 550ms，且必须等第一帧 Lit ready，随后以 650ms opacity 过渡显示 Canvas/Leaves。没有闪白层、额外曝光或 shader 修改。
- reduced-motion 直接显示就绪的 Lit，取消淡入；失败仍显示底图；卸载清理定时器。无新增高频 RAF。

## 验证结果

- `pnpm typecheck` / `pnpm build`、公开入口 SSR 通过。
- `python scripts/validate_homepage.py`：首屏底图→Lit、抽屉焦点/Esc、Canvas 身份与时间保留、关闭后 Play 继续、手机无横向溢出、页面锚点、reduced-motion 通过，JS 错误为 0。
- `python scripts/validate_homepage.py --visual`：四时段与 R7.4 golden 全部像素一致，仅排除旧截图中位于 (16,16)–(65,39) 的旧 Debug 按钮矩形。新截图隐藏抽屉入口；不是扩大容差掩盖视觉变化。
- 无引擎或资产改动；仅首屏呈现过渡暂时混合 Base/Lit，完成后与原 Lit 相同。

## 验收素材

- [桌面完整主页](homepage/desktop.png) / [手机完整主页](homepage/mobile.png)
- [四时段](homepage/four-phases.jpg)
- [桌面抽屉](homepage/drawer.png) / [手机抽屉](homepage/mobile-drawer.png)
- [入场连续帧 GIF](homepage/entrance.gif)（采样预览，非精确帧率性能记录）
- [底图](homepage/entrance-base.png) / [Lit](homepage/entrance-lit.png)
- [交互结果](homepage/checks.json) / [冻结视觉回归](homepage/visual-regression.json)

本轮是可运行示例主页；文章入口暂指向真实项目资料，最终博客内容与主题集成仍留待后续确认。
