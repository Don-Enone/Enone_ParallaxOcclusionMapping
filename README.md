# Enone_ParallaxOcclusionMapping

适用于 **Unreal Engine 5.8** 的视差遮蔽映射材质函数。根据实际输入 UV 与表面位置的导数重建视线和光照方向，使视差适配物体旋转，以及 UV 旋转和镜像；也可用于延迟贴花（Deferred Decal）。

> **UE 版本说明：** 自 v2.0 起，资产以 UE 5.8 保存，无法在 UE 4.x 中打开。需要 UE 4.26 版本请使用 [`v1.0-ue4.26`](https://github.com/Don-Enone/Enone_ParallaxOcclusionMapping/tree/v1.0-ue4.26) 标签。

## 版本更新

### v2.0（UE 5.8）

- 资产升级到 UE 5.8，路径改为 `/Game/Material/Enone_ParallaxOcclusionMapping`。
- **贴花支持**：方向计算的 Custom 节点在 `DECAL_PRIMITIVE` 下改用贴花自身的坐标轴（`DecalToWorld`）构建 UV 坐标基底，不再依赖顶点法线。延迟贴花中没有切线空间，顶点法线恒为 (0,0,1)，旧做法只在地面上正确，在墙面上会出错。视线 z 分量取绝对值并限制最小值 0.15，高度采样使用 `ComputeDecalDDX/DDY`。
- **节点布局重排**：按数据流从左到右分为三段（输入与方向计算 → 光线步进 → 输出），并用 9 个带中文标题的彩色注释框分区：步数插值、UV 坐标系方向重建、视差偏移、光照向量、光线步进、输出（含质量与平台回退）、像素深度偏移、世界位置、步数复杂度调试。移除了原函数遗留、已错位的英文注释。

### v1.0（UE 4.26）

- 基于 UE4.26 内置 ParallaxOcclusionMapping 修改，加入自动 UV 方向计算。详见 `v1.0-ue4.26` 标签下的说明。

## 安装与使用

1. 关闭 Unreal Editor，将本仓库的 `Content` 文件夹合并到 UE 5.8 项目的 `Content` 文件夹中，保留目录结构。
2. 打开项目，在材质中添加 `Enone_ParallaxOcclusionMapping` 材质函数。
3. 将高度贴图 Texture Object 接入 `Heightmap Texture`，将贴图坐标接入 `UVs`，并设置 `Height Ratio`、`Min Steps` 和 `Max Steps`。
4. 将 `Parallax UVs` 输出连接到需要视差的贴图采样 UV。按需使用其他输出。

资产路径：`/Game/Material/Enone_ParallaxOcclusionMapping`

在贴花材质中使用时：高度采样的梯度来自 `TexCoord[0]`，若给 `UVs` 输入接的是缩放过的 UV，需要在函数内部的梯度计算中使用相同的缩放。

自动 UV 方向计算始终启用；无原版模式切换开关。原函数的 `Use World Coordinates` 和 `Transform To VertexNormal` 输入已移除。Height Ratio 保持原函数的相对深度语义。

## 实现与验证

- 视线与光照使用相同的 UV 坐标基底，保留 UV 镜像方向和非正交坐标轴。
- 通过代数约简合并退化检查，省去重复的投影与归一化计算，保留旋转、镜像和斜切 UV 支持。
- 独立视线 UV 方向计算在 FXC `ps_5_0`、O3 条件下由 **59 → 37 条指令**，减少约 **37%**（v1.0 在 UE4.26 下的统计）。这不是整个材质 Base Pass 的统计；完整开销以实际材质重新编译结果为准。
- 对退化 UV 禁用横向视差偏移，对视线掠射角加入除零保护。
- 保留原函数的步进、质量等级回退、Pixel Depth Offset 和其他输出。
- 依赖均为引擎内置资产（`VectorLength`、`CameraDirectionVector` 等）。
- `Validation/` 中的报告来自 v1.0（UE4.26）：资产重载、着色器编译（零错误、零警告）、12,000 组 CPU 双精度数学等价回归、退化 UV 和物体绕法线旋转 90 度检查。v2.0 在 UE 5.8 的实际项目（表面材质与贴花材质）中使用，尚未重新生成这些报告。

## 脚本

`Scripts/` 下的脚本属于 v1.0，针对 UE 4.26 和旧资产路径 `/Game/TAcourse_III/Element/BaseElement/`，用于从引擎内置函数生成资产并验证。v2.0 资产直接在 UE 5.8 编辑器中修改，不由这些脚本生成。

`Scripts/create_enone_pom.py` 从引擎内置函数复制并生成资产，目标资产已存在时会停止以避免覆盖。

`Scripts/frame_optimized.hlsl` 是生成脚本使用的优化方向计算模板；保留 `RETURN_RESULT` 占位符，由脚本分别填入视线与光照的返回逻辑。

`Scripts/validate_enone_pom.py` 检查保存后的资产并创建仅存在于内存的编译测试材质。

`Scripts/test_frame_math.py` 可用普通 Python 执行数学回归检查，不需要启动 Unreal Editor。

## 许可证

项目自有 Python / HLSL 代码、文档与验证材料采用 [MIT License](LICENSE)。你可以在保留版权和许可声明的条件下使用、修改和分发这些内容，包括商业使用。

`.uasset` 基于 Unreal Engine 内置材质函数，包含 Epic 提供的节点与代码；MIT 不覆盖这些第三方内容，也不改变 Unreal Engine 的授权条件。组合资产的使用和分发仍受适用的 Unreal Engine 许可约束，详见 [NOTICE.md](NOTICE.md) 和 [Unreal Engine EULA](https://www.unrealengine.com/eula/unreal)。
