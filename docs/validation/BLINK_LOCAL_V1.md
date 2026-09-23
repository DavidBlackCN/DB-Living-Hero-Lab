# 局部 Blink v1 验收

整图 Blink 已终止；Base 始终常驻。使用旧 v1 闭眼图仅作为离线来源，两个 RGBA 局部图按 Artwork Space 源像素贴回 Base。

## 检查结果

- Base、旧闭眼来源均为 1672×941；两个局部素材分别为 92×73、92×78 RGBA。
- `python scripts/validate_blink_normal.py`：合成后改变 7,125 个像素，全部在双眼局部矩形内；矩形外改变 0 个像素。眼部实际差异 bbox 为 `[1087,180,1241,271)`。
- [闭眼局部放大图](blink-local-composite-detail.png)：闭眼形状可读，羽化接缝在静态放大观察下不明显；未见大范围脸部或背景重绘。
- 页面桌面 WebGL2：Debug 的两个区域对齐眼睛；Preview Blink 进入 `is-closed` 后恢复睁眼，整图 Base 的 URL 和 Renderer 均不切换。Auto 的 4.2–7.6 秒间隔、115 ms 闭眼可在配置中调节。
- 移动端 390×844 contain：眼部贴图保持与 Artwork 同比缩放，两个区域约 21×17 与 21×18 CSS px。

结论：通过最小局部 Blink 验收。尚未补 Half；细微节奏和眼睑形状可在后续真实设备上继续微调。
