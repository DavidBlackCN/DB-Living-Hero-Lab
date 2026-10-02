# 动画与渲染维护地图

这些系统均已完成视觉验收；当前数值以 `src/config/` 为准，文档不复制整套参数。

| 系统 | 当前行为 | 入口 |
| --- | --- | --- |
| Blink | 320ms 连续 0..1 权重，随机 4.2–7.6s 间隔；局部双眼参与 Lit | `BlinkTimeline`、`BlinkLayer.vue`、hero config |
| Breathing / Head / Hair | 统一角色坐标链与克制的相位差，闭眼贴片随同一变形 | engine animation、breathing/hair config、fragment shader |
| Leaves v2 | Canvas2D 三层、独立轨迹/确定性随机、柔性脸部保护；桌面18/移动10上限 | `LeafField`、`LeavesLayer.vue`、hero config |
| Time | 实时/手动/播放共用连续日循环，午夜闭合 | `TimeController`、lighting/sky config |
| Lamps | 局部 emissive + surface + glow，共用连续权重；不随机闪烁 | lamps config、lamp source/influence masks |
| Atmosphere / Post | 场景深度和现有 HDR/Post 链收口；与角色动画分离 | atmosphere/post config、post shader |

## 生命周期约束

不增加第二套高频 RAF。hidden、离屏、paused、卸载和 reduced-motion 由现有组件生命周期处理。Low/Static 降低动态成本；静止画面按需绘制。公开 props 与质量档位详见 [接入文档](VUEPRESS_INTEGRATION.md)。

## 验收重点

- Blink 时 lighting 不跳，头部运动下眼片不漂移。
- Breath → Head → Hair 协同，人物与天空边缘不出现新 seam。
- Leaves 不连续挡眼，夜间不发光；灯区暖响应克制。
- 时间播放跨午夜、晨昏均连续，隐藏页面不继续高频绘制。
- 页面菜单不重初始化 renderer，也不改已选时间/动效参数。

[精选动效记录与回归命令](validation/README.md)。旧动态视频只证明冻结的运动方式，不作为最新页面/色彩截图。
