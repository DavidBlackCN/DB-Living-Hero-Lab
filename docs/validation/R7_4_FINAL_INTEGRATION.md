# R7.4 — Final Integration

视觉 baseline：`ad18ee5`。本轮为生产组件整理，不修改素材、shader、Lighting/Sky/Post/Atmosphere 参数、动作曲线或 Lamp/Leaves 视觉算法。

## 架构结果

- `src/index.ts` + `src/types.ts`：正式组件、配置入口与宿主接口。
- LivingHero：SSR 安全的生命周期、质量决策、可控时间、资源状态、slot、事件和实例方法。
- HeroCanvas：按需加载；负责 Vue/Canvas 生命周期与合并按需绘制。
- `engine/assets/loadHeroAssets.ts`：独立 16 纹理清单、注册尺寸验证及加载进度；取消原组件内重复校验代码。
- `loadImage.ts`：优先级、匿名 CORS、超时与 Abort；失败、重新初始化、卸载均可终止等待。
- `quality/policy.ts`：High/Medium/Low/Static 与 Auto；DPR/总像素/叶片预算，持续压力降档。
- hero.css 与 Demo main.css 分离，避免移入博客时修改 body/#app；DebugPanel 与 renderer 独立懒加载。

## 清理项目

删除 renderer 的 hairSecondary/hairSheen/skyRepair/blinkAmount 临时 URL 诊断及对应分支；正常值与原默认一致。删除未使用的 heroConfig.lighting / 顶层 dprCap（质量档统一管理），删除无用 debug-future CSS。调试面板保留为显式 debug 可选能力，生产默认关闭。已有接收遮罩属于验收后的视觉实现，未将它们误当作无用 patch 删除。

## 回归

- `pnpm typecheck` / `pnpm build` 通过。
- `python scripts/validate_blink_normal.py` 通过；素材无改动。
- 四时段与 04:43、05:45、00:00，共 7 个 1672×941 固定帧：与改动前 PNG 逐像素完全一致；00:00/24:00 一致。
- 全动效 24H Play 运行 68.47 秒并跨午夜，无 JS/WebGL 错误。时间/视觉算法源码保持 baseline。
- 现有 regression 通过：Blink、Breathing/Head/Hair、Leaves、Lamp、Post、Atmosphere、hidden tab、reduced-motion、Static、context restore、4K/mobile resize、早晚连续性。
- 生产宿主审查通过：默认无 debug、默认 slot、16 项加载进度、三档 DPR、总像素上限、低档按需静止、手动暂停、离屏暂停、API 时间操作、资源子路径、卸载重挂、WebGL 不可用 fallback、纹理失败与 retry、低内存 Auto fallback、reduced motion、初始化期间卸载、Auto 降档事件。
- `node scripts/validate_hero_ssr.mjs`：从公开入口 SSR 输出正确 `/blog/assets/hero` poster，无 window 访问/Canvas 初始化。

## 性能

完整视觉 shader 不变，仍为 10 draw calls/frame。High: DPR≤2 / 8.29M pixels；Medium: ≤1.5 / 3.69M；Low: ≤1 / 2.07M，停动态，时间改变时按需绘制。三档均保留原 Post 参数。

本机 Edge/ANGLE D3D11、RTX 5070 Ti，隔离 WebGL 渲染（Leaves/Blink 暂停、Motion 开启、Atmosphere ON）：1080p GPU 中位 0.242ms，1440p 0.399ms，4K 0.873ms（P95 1.075ms），观察绘制频率 26.67fps，原 cap≤30。此结果不替代低端真机测试；已用设备提示与模拟压力验证降级策略。

构建按需 chunk：HeroCanvas 约 65kB（gzip 17.4kB），DebugPanel 约 17kB（gzip 4.5kB）；生产 Static 模式不请求 renderer chunk。

## 验收资料

- [四时段](r7-4/four-phases.jpg)
- [生产宿主](r7-4/production-host.png) / [WebGL fallback](r7-4/webgl-fallback.png)
- [Play 24H](r7-4/play-24h.jpg)
- [像素回归](r7-4/baseline-stats.json) / [生产接口回归](r7-4/integration-stats.json)
- [生命周期回归](r7-4/regression-stats.json) / [性能](r7-4/performance-stats.json) / [24H 数据](r7-4/play-24h.json)
- [VuePress 接入与完整 API](../VUEPRESS_INTEGRATION.md)

生产组件准备完成，等待最终人工验收。目标 VuePress/Plume 仓库未提供，本轮完成 SSR/独立宿主/路径兼容验证与接入示例，不声称已经在实际博客构建或部署。下一阶段不自动开始。