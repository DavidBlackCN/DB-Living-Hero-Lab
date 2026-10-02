# 资产与注册

Artwork Space：1672×941，左上原点。实际 URL/眼区唯一入口为 `src/config/hero.ts` 与 `src/config/sky.ts`。冻结的运行资产 SHA-256 清单在 `sources/runtime-assets.sha256.json`，用 `validate_repository.py` 检查，不能为绕过差异随意更新。

| 运行资产 | 作用 / 维护脚本 |
| --- | --- |
| `base/base-albedo.png` | 冻结原画；不可重画或重新裁切 |
| `normal/base-normal-v3.png` | 当前法线；`generate_normal_v3.py` |
| `blink/left-closed-v1.png`、`right-closed-v1.png` | 局部 RGBA 闭眼；`extract_blink_eyes.py` |
| `leaves/leaf-01.png` 至 `leaf-04.png` | 四张已接受的 1024×1024 RGBA 叶片 |
| `sky/sky-{dawn,noon,dusk,night}.png` | 注册的四时段天空 RGBA；`generate_sky_assets.py` |
| `sky/sky-edge-reconstruction.png`、`sky-edge-skyfill.png` | 固定边缘去污染/覆盖重建；`generate_sky_edge_reconstruction.py` |
| `motion/hair-motion-mask.png` | 头部/发束 motion 注册；`paint_hair_motion_mask.py` |
| `material/material-mask.png` | 材质 receive；`paint_material_mask.py` |
| `lighting/tower-receiver-mask.png` | 建筑受光归属；`paint_tower_receiver.py` |
| `lighting/lamp-source-mask.png`、`lamp-influence-mask.png` | R/G 分别近灯与远灯；`generate_lamp_masks.py`，仅改灯体用 `--source-only` |
| `atmosphere/scene-depth.png` | 背景深度层次；`generate_scene_depth.py` |

## 离线输入

`sources/hero/` 保留 v1/v2 Normal、原始全幅闭眼候选和 sky-mask。它们仅供制作/验证，不进入部署包。全幅闭眼候选本身不合格，但它是局部双眼的提取源，不可误当垃圾删除。

Normal 生成链：`generate_normal.py` → `generate_normal_v2.py` → `generate_normal_v3.py`。前两步写入 `sources/hero/`，最后一步才写运行 v3。默认不要运行生成链；维护冻结图时先保存备份并在 `artifacts/` 对照。Python 工具依赖见验收文档。

双眼注册：左 `[1080,177,1172,250)`，右 `[1152,195,1244,273)`。局部纹理与 Base / Normal 使用同一角色变形坐标。

旧 `sky-edge-tone` / `sky-edge-override` 已无运行引用，本次删除；不再使用压暗接缝方案。素材调整后检查 registration、四时段、运动时边界和实际接入 URL。
