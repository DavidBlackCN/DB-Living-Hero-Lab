# Normal v2 语义精修验收

## 输入、生成与注册

- 冻结 Base：`public/assets/hero/base/base-albedo.png`；技术基准：`public/assets/hero/normal/base-normal-v1.png`。
- 新候选：`public/assets/hero/normal/base-normal-v2.png`，1672×941 RGB，与 Base 使用同一像素网格；未裁切、移动或重绘 Base。脚本：`python scripts/generate_normal_v2.py`。
- 少量语义提示只在生成脚本内：脸与皮肤用平滑低幅曲面；两侧头发加入跨发束的体积方向；衣物用较大尺度褶皱并压低格纹／色块响应；石柱、栏杆保留宽面方向；天空接近 neutral。没有新增运行时 Mask 资产。
- `src/config/hero.ts` 的 Normal URL 已指向 v2；v1 保留作历史对照。

## 差异与多方向检查

以下是源图坐标内固定采样矩形的 Normal R/G 局部梯度平均幅度（8-bit 值，越低表示细碎方向变化越少），仅用于比较 v1/v2，不是美术质量评分：

| 区域 | v1 | v2 |
| --- | ---: | ---: |
| 脸部 | 3.80 | 0.47 |
| 左侧发束 | 3.79 | 0.25 |
| 背心 | 1.59 | 0.28 |
| 格纹裙 | 3.27 | 0.22 |
| 石柱正面 | 1.77 | 0.24 |
| 天空 | 2.45 | 0.11 |

石柱正面 R/G 相对 neutral 的平均偏离由 2.43 升至 5.21，说明细纹减少后仍保留大尺度面方向；天空偏离由 5.14 降至 0.62。页面 WebGL2 的 Normal View 能加载 v2；Test Light 已在 0°、90°、180°、270°、135°、315° 检查，光向响应平顺，未见明显区域硬接缝或眼鼻线条假凸起。另用强于页面的 1.3 倍诊断光照制作了[脸部对照](normal-v2-stress-face.png)和[石材对照](normal-v2-stress-stone.png)，便于检查细节。页面正常测试强度仍为 `hero.ts` 中的 0.65。

`python scripts/validate_blink_normal.py` 检查 v1、v2 均为 1672×941 RGB，并复核 Blink 的眼外像素不变；`pnpm build` 通过。

## 冻结判断

**Normal v2 暂不冻结为最终 Runtime Lighting 法线。** 它解决了 v1 最突出的浮雕脸、格纹和天空假法线，适合作为下一轮美术校正基底；但目前的发束识别依赖大区域与颜色条件，薄发丝、人物与背景交叠处可能被赋予错误方向。远景建筑的深度层次和局部石雕仍以近似的宽尺度场表示；衣褶也尚未逐处人工审核。这些问题会在更强、移动范围更大的正式光照下暴露，阻碍最终冻结。下一轮应集中修正这些局部并重复多光向实机验收；本阶段不启动 24h Runtime Lighting。
