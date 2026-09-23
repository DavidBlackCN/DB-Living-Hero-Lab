# Normal 技术 v1 验收

`public/assets/hero/normal/base-normal-v1.png` 由冻结 Base-4 逐像素生成；两图均为 1672×941 RGB，未裁切、缩放或重绘构图。生成脚本为 `scripts/generate_normal.py`，法线编码约定 R 向右、G 向下、B 朝向观察者。

页面 WebGL2 已能加载第二纹理，并提供 Normal map 与 Test Light 视图。按着色器公式在离线 NumPy 中模拟 315° 与 135° 相反光向，平均 RGB 通道差约 5.89/255；约 846,181 个像素的平均通道差超过 3/255。桌面页面检查见到脸、发、衣物和建筑边缘随光向变化；Base 默认视图不施加测试光照。`pnpm build` 与 `python scripts/validate_blink_normal.py` 通过。

**范围**：通过尺寸、注册、纹理采样和基本光照方向验证。这张由亮度梯度推导的浅浮雕法线会把原画阴影和色块边界解释成几何起伏，尚未通过最终 Runtime Lighting 的材质语义和美术验收。后续需要按脸部、头发、衣物、建筑分别修正法线，再调光照范围、色温、遮挡和强度。
