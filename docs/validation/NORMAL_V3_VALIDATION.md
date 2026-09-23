# Normal v3 局部美术修正验收

## 资产与改动边界

`base-normal-v3.png` 以 v2 为基底，输出 1672×941 RGB，与冻结 `base-albedo.png` 使用同一像素网格。脚本为 `scripts/generate_normal_v3.py`；未改动 Base、Blink、Leaves，未生成运行时 Masks。页面配置已指向 v3，v2 保留作历史对照。

本轮 v3 相对 v2 改动 **214,355 像素**。`scripts/validate_blink_normal.py` 检查所有改动都位于发缘、衣物内部、远景建筑或下方石雕的预定源像素范围；以下已通过区域 **0 像素改变**：脸 `[1070,170,1245,310)`、主石柱 `[520,0,870,590)`、左栏杆 `[0,650,900,835)`、右栏杆 `[1400,630,1672,795)`，以及顶端天空的蓝色区域。

## 局部修正结果

| 局部 | v3 处理 | 检查结果 |
| --- | --- | --- |
| 两侧薄发束 | 5 条独立窄路径，各自指定方向；缩短不确定的外缘尾段；背景缝隙趋近 neutral | 右侧曾误入树叶背景的方向带已移除。左外缘缝隙的 R/G neutral 偏离均值由 5.65 降至 1.55，右侧由 2.52 降至 0.94。未追踪的极细发尾保持弱响应。 |
| 袖子、背心、裙摆 | 仅在衣物内部对 v2 再作轻度低通，保留已有宽尺度体积 | 格纹、领带附近线条和色块没有新增方向细节。左袖 R/G 局部梯度均值 0.372→0.320；背心 0.236→0.217；裙摆 0.235→0.226。 |
| 远景塔楼／墙面、栏杆下方石雕 | 低幅、较宽的法线场；主石柱和栏杆上部保持 v2 | 左塔楼局部梯度 0.175→0.152，右墙 0.134→0.085，右下石雕 0.139→0.125。远景响应弱于前景石柱。 |

数字为选定源像素矩形中 Normal R/G 的局部梯度均值（8-bit 值），只用于 v2/v3 对比，不代表视觉评分。输入矩形和生成路径均在脚本中固定。

## 诊断输出

四张局部诊断图均包含 **Base、Normal v2 原图、Normal v3 原图、放大差异、0°／90°／180°／270°／135°／315° Test Light，以及相同六方向的 1.3× stress light**：

- [Hair crop](normal-v3-diagnostic-hair.png)：`[875,90,1480,625)`。
- [Clothing crop](normal-v3-diagnostic-clothing.png)：`[845,335,1410,850)`。
- [Architecture left crop](normal-v3-diagnostic-architecture-left.png)：`[850,0,1060,510)`。
- [Architecture right crop](normal-v3-diagnostic-architecture-right.png)：`[1300,0,1672,941)`。

页面的 Normal View 已显示 v3；WebGL2 Test Light 的六个方向均可切换并正常重绘。`pnpm build` 与 `python scripts/validate_blink_normal.py` 通过。

## 冻结判断

**Normal v3 可以作为当前 Normal 阶段的冻结资产。** 六方向和 1.3× stress 的所列局部中，未观察到明确的反向高光或背景缝隙继承发束方向。未追踪的极细发尾选择近中性，表现较平但不是错误方向；这是本阶段明确接受的取舍。当前没有需要再修正的具体错误方向区域。正式 24h Runtime Lighting 尚未开始，届时若使用超出本次测试的光照模型或强度，须以新场景重新验收，而不是把本次诊断视为其结果。
