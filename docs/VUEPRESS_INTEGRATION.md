# Living Hero production integration

当前生产入口为 `src/index.ts`，导出 `LivingHero`、`LivingHeroProps`、`LivingHeroHandle`、`HeroStatus`、质量策略及资产配置工厂。独立 Demo 的 `src/app` 与 `src/styles/main.css` 不属于接入接口。

## VuePress 2 / Plume

目标站点使用 Vite bundler（GLSL 使用 Vite `?raw` 导入）。将 `src/components`、`src/engine`、`src/config`、`src/shaders`、`src/styles/hero.css`、`src/index.ts`、`src/types.ts` 保持目录结构复制到 `.vuepress/components/living-hero/`；将冻结的 `public/assets/hero/` 原样复制到站点 `.vuepress/public/assets/hero/`。

在 `.vuepress/client.ts` 注册：

```ts
import { defineClientConfig } from 'vuepress/client'
import { LivingHero } from './components/living-hero'

export default defineClientConfig({
  enhance({ app }) {
    app.component('LivingHero', LivingHero)
  },
})
```

在首页自定义组件/模板中使用，明确提供容器高度。假设站点部署 base 为 `/blog/`：

```vue
<LivingHero
  asset-root="/blog/assets/hero"
  quality="auto"
  style="height: 80vh; min-height: 420px;"
>
  <div class="homepage-title">My Blog</div>
</LivingHero>
```

`asset-root` 指向包含 base/normal/sky 等子目录的根；不会二次拼接站点 base。根路径部署可用 `/assets/hero`。也可提供允许匿名 CORS 的 CDN URL。默认值取 Vite `BASE_URL + assets/hero`，建议 VuePress 显式传入站点路径。

SSR 已实测：服务端只输出注册底图、slot 和加载状态，不读取 window/创建 Canvas。客户端 mounted 后启动渲染，无需用 ClientOnly 丢弃首屏底图。组件只使用自身样式，不导入 Demo 对 html/body/#app 的全屏 reset。

注册方式参照 [VuePress 官方 client config 文档](https://v2.vuepress.vuejs.org/guide/configuration.html#client-config-file)。本仓库没有目标 Plume 站点；已验证独立宿主、SSR 和 `/blog/` 资源路径，最终首页槽位与主题布局需在目标仓库实际接入验证。

## Props / events / exposed API

| Prop | 默认 | 含义 |
| --- | --- | --- |
| assetRoot | Vite base 下 assets/hero | 全部冻结素材路径；改变时重新加载 renderer |
| quality | auto | high / medium / low / static / auto；balanced 为旧 medium 别名 |
| fit | auto | auto / cover / contain，保留原 Artwork Space 计算 |
| minutes | undefined | undefined 使用实时本地时间；传数值切换 Manual（0–1440），后续变化继续选择时间 |
| paused | false | 暂停时间推进与动态驱动，保留当前成图 |
| adaptive | true | Auto 下持续帧间隔压力可逐级降至 Low；显式 quality 不自动降档 |
| debug | false | 提供调试抽屉入口；抽屉默认关闭，生产默认不加载 |
| entrance | false | 可选底图→Lit 入场：底图至少 550ms，Lit 就绪后 650ms 淡入；reduced-motion 取消过渡 |
| alt | 场景描述 | 静态底图替代文本；纯装饰场景可传空字符串 |

事件：`ready`（每次 renderer 成功初始化）、`error(reason)`、`status({ mode, loaded, total, quality })`、`time-change({ mode, minutes })`。mode 为 loading / WebGL2 / fallback / static；资源进度统计 16 个关键注册纹理，不包含稍后加载的可选叶片。

组件 ref 类型 `LivingHeroHandle`：`setTime(minutes)`、`backToNow()`、`play()`、`pause()`、`retry()`。reduced-motion 下 `play()` 不启动。`paused` 与离屏/hidden 会暂停驱动，恢复后沿用原时间生命周期。`minutes` 是外部选择入口，若要双向同步可监听 time-change；它不是默认 v-model。

Slots：默认 slot 放首页内容；`loading` 接收 loaded/total；`fallback` 接收 reason/retry，可提供重试按钮。底图始终在底层，加载错误不会留下空白画布。

## 质量与性能预算

| 档位 | DPR 上限 | 总像素上限 | Leaves 桌面/移动 | 动效 | Post |
| --- | ---: | ---: | ---: | --- | --- |
| High | 2 | 8,294,400 | 18 / 10 | 完整，原节奏 | 全部原参数 |
| Medium | 1.5 | 3,686,400 | 12 / 8 | 完整，原节奏 | 全部原参数 |
| Low | 1 | 2,073,600 | 0 / 0 | 关闭，保留随时间按需绘制 | 全部原参数 |
| Static | 无 Canvas | 无 | 0 / 0 | 关闭 | 原始 Base poster |

High 为冻结视觉基线。中低档只改变成本预算，不改光照、曲线、材质或 Post 强度。Medium 的叶片 DPR 为 1（High 1.5），叶片尺寸/轨迹算法不变。

Auto：saveData 或已知内存 ≤2GB 选 Static；CPU ≤2 核选 Low；内存 ≤4GB 或 CPU ≤4 核选 Medium；其余/未知选 High。设备提示属于粗略初选，可由 quality 覆盖。连续超过约 8 秒、至少 40 个慢 RAF 间隔（>80ms）时，Auto 从 High→Medium→Low 单向降级，避免反复切换。不是 GPU 基准，不承诺所有硬件 30fps。

Motion / Leaves 保持原 ≤30fps cap。hidden、离屏、paused 会暂停现有驱动；低档与 reduced-motion 的多项时间输入合并成一次按需 draw。像素预算还受 GPU 最大纹理/Renderbuffer 尺寸限制。

## 加载与降级

1. 首屏 HTML 底图高优先级，保持固定容器尺寸。
2. 仅需 WebGL 时懒加载 HeroCanvas/renderer chunk，Static 无需该代码与 16 个纹理。
3. 先检测 WebGL2 / 16 texture units，再并行加载注册资源，按实际完成数量报告进度、校验尺寸。
4. 每张资源 20 秒超时；初始化被替换/卸载会 Abort，过期 generation 不可重新挂载 renderer。
5. WebGL/关键素材失败：显示 Base；error/status 通知宿主，retry 可重建。context restore 自动重建；可选叶片失败只停叶片。
6. reduced-motion 保留完整静态时段光照，停 Blink/Breath/Hair/Leaves 与 Play；Static fallback 是原始 Base，不宣称保留动态 Night 光照。

不要传入实验用 URL 开关：hairSecondary、hairSheen、skyRepair、blinkAmount 已从 renderer 删除。正式开关使用公开接口；素材/光照参数保持冻结。
