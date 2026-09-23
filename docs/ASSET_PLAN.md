# Asset plan

| Asset | Path | State | Role / replacement rule |
| --- | --- | --- | --- |
| Base Albedo | `public/assets/hero/base/base-albedo.png` | Frozen | Artwork Space 基准，不在代码中破坏性裁切；替换需重新验收全部注册资产。 |
| Blink Closed source | `public/assets/hero/blink/blink-closed-eyes-v1.png` | Full-frame rejected / extraction source only | v1 与 v2 均不用于整图切换；v2 失败原图仅归档于 `docs/validation/`。 |
| Blink local eyes | `public/assets/hero/blink/left-closed-v1.png`、`right-closed-v1.png` | Accepted / Integrated v1 | 从 v1 闭眼候选提取的独立透明 RGBA 双眼图。区域和羽化参数见 `scripts/extract_blink_eyes.py`；页面只叠加双眼，Base 常驻。Half 可选、后续独立处理。 |
| Normal v1 | `public/assets/hero/normal/base-normal-v1.png` | Archived technical baseline | 亮度梯度技术验证版，保留用于对照，不再由页面加载。详见 [`validation/NORMAL_V1_VALIDATION.md`](validation/NORMAL_V1_VALIDATION.md)。 |
| Normal v2 | `public/assets/hero/normal/base-normal-v2.png` | Archived semantic baseline | 保留逐像素对照，不再由页面加载。详见 [`validation/NORMAL_V2_VALIDATION.md`](validation/NORMAL_V2_VALIDATION.md)。 |
| Normal v3 | `public/assets/hero/normal/base-normal-v3.png` | **Frozen for current Normal stage** | 在 v2 上仅修正薄发束、衣物内部和远景建筑／石雕；1672×941 RGB，与 Base 逐像素注册。脸、天空、主石柱和栏杆保持 v2 原像素；六方向和 1.3× stress 诊断已通过。见 [`validation/NORMAL_V3_VALIDATION.md`](validation/NORMAL_V3_VALIDATION.md)。 |
| Leaves | `public/assets/hero/leaves/leaf-01.png`～`leaf-04.png` | Accepted / Integrated v1 | 四张独立 1024×1024 RGBA master 已确认可用，并接入第一版 Canvas 2D 落叶覆层；尺寸与轨迹后续独立调优。可逐张替换，保持文件名和透明留白规格。 |
| Masks / regions | `public/assets/hero/masks/` | TBD | 仅在 Runtime Lighting / 动效实现确有需要时增加，同步 Artwork Space。 |

Artwork Space 为 1672×941，UV 原点在左上，`(0,0)` 是图像左上角，`(1,1)` 是右下角。像素坐标同样从左上起算。所有局部资产须记录区域、尺寸和与 Base 的注册关系。目录可为空，表示素材确实待制作。

Debug 面板不再提供整图闭眼候选切换。运行时只加载局部双眼 PNG；坐标以 Base 源图左上角为原点，左眼 `[1080,177,1172,250)`、右眼 `[1152,195,1244,273)`。当前 Normal v3 资源 URL 在 `src/config/hero.ts`，可独立替换并按 Base 尺寸重新验收。v2/v3 的语义区域只存在于离线生成脚本，没有新增运行时 Mask 图集。

落叶是独立前景粒子，不需要与 Base 像素注册。四张 master 的配色、形态、alpha 检查及未来 atlas 注意点见 [`LEAVES_ASSET_NOTES.md`](LEAVES_ASSET_NOTES.md)。运行时 URL 由 `src/config/hero.ts` 统一管理，画面通过独立 Canvas 2D 覆层绘制；master 继续保持分图，不制作 atlas。
