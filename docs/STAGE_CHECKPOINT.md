# 当前状态

更新：2026-10-03。当前分支 `v2`，可独立静态部署；VuePress / Plume 实仓联调尚未开始。

## 已完成并冻结的视觉系统

- R6：24H Sun/Moon、统一 Character Lighting、建筑方向受光与连续晨昏过渡。
- R7.1：两盏局部暖灯，每盏 3 个玻璃面，连续启停。
- R7.2：三层 Leaves、脸部保护、轻微灯区响应。
- R7.3：角色协同 Motion、320ms 连续局部 Blink、Atmosphere、天空接缝和塔身收口。
- R7.4：生产组件 API、加载/降级/质量/生命周期及独立主页。最后页面微调基线：`cd7bea5`。

主页当前支持大时钟、随本地时间问候、介绍/单行签名、占位社交按钮、两级上拉光影菜单、主题化画面选择、全屏和保留主体文字的沉浸模式。底图→Lit 入场保持。

## 本次整理

只清理文件与文档，没有修改 `src/` 渲染或页面代码。运行资产从离线输入中分离；旧迭代记录改由 Git 保管；生成测试输出统一进入 `artifacts/`。

入口：[README](../README.md) · [素材](ASSET_PLAN.md) · [动画](ANIMATION_PLAN.md) · [接入](VUEPRESS_INTEGRATION.md) · [验收](validation/README.md) · [维护](MAINTENANCE.md)

## 下一步

等待最终人工验收与部署选择。后续如接入 Blog/Plume，使用公开组件接口单独做宿主生命周期、资源路径和页面布局联调；本轮未开展该任务。
