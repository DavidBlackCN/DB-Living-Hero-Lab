# Asset plan

| Asset | Path | State | Role / replacement rule |
| --- | --- | --- | --- |
| Base Albedo | `public/assets/hero/base/base-albedo.png` | Frozen | Artwork Space 基准，不在代码中破坏性裁切；替换需重新验收全部注册资产。 |
| Blink Closed | `public/assets/hero/blink/blink-closed-eyes-v1.png` | Full-frame rejected / local-eye source candidate | 与 Base 同尺寸，但非逐像素严格注册；整图切换会闪动。双眼造型可作为局部方案来源，详见 [`validation/BLINK_V1_VALIDATION.md`](validation/BLINK_V1_VALIDATION.md)。 |
| Normal | `public/assets/hero/normal/` | Pending | 与 Base 严格同像素坐标。 |
| Leaves | `public/assets/hero/leaves/leaf-01.png`～`leaf-04.png` | Accepted / integrated v1 | 四张独立 1024×1024 RGBA master 已确认可用，并接入第一版 Canvas 2D 落叶覆层；动态观感仍可按场景继续调校。可逐张替换，保持文件名和透明留白规格。 |
| Masks / regions | `public/assets/hero/masks/` | TBD | 若实现需要再设计，同步 Artwork Space。 |

Artwork Space 为 1672×941，UV 原点在左上，`(0,0)` 是图像左上角，`(1,1)` 是右下角。像素坐标同样从左上起算。所有局部资产须记录区域、尺寸和与 Base 的注册关系。目录可为空，表示素材确实待制作。

Debug 面板可静态切换 Base 与闭眼候选图，便于观察注册和背景变化。该开关仅用于查看被拒绝的整图方案，不代表运行时眨眼实现。

落叶是独立前景粒子，不需要与 Base 像素注册。四张 master 的配色、形态、alpha 检查及未来 atlas 注意点见 [`LEAVES_ASSET_NOTES.md`](LEAVES_ASSET_NOTES.md)。运行时 URL 由 `src/config/hero.ts` 统一管理，画面通过独立 Canvas 2D 覆层绘制；master 继续保持分图，不制作 atlas。
