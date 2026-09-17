# Enone_ParallaxOcclusionMapping

适用于 Unreal Engine 4.26 的视差遮蔽映射材质函数。根据实际输入 UV 与表面位置的导数重建视线和光照方向，使视差适配物体旋转，以及 UV 旋转和镜像。

## 安装与使用

1. 关闭 Unreal Editor，将本仓库的 `Content` 文件夹合并到项目的 `Content` 文件夹中，保留目录结构。
2. 打开项目，在材质中添加 `Enone_ParallaxOcclusionMapping` 材质函数。
3. 将高度贴图 Texture Object 接入 `Heightmap Texture`，将贴图坐标接入 `UVs`，并设置 `Height Ratio`、`Min Steps` 和 `Max Steps`。
4. 将 `Parallax UVs` 输出连接到需要视差的贴图采样 UV。按需使用其他输出。

资产路径：`/Game/TAcourse_III/Element/BaseElement/Enone_ParallaxOcclusionMapping`

自动 UV 方向计算始终启用；无原版模式切换开关。原函数的 `Use World Coordinates` 和 `Transform To VertexNormal` 输入已移除。Height Ratio 保持原函数的相对深度语义。

## 实现与验证

- 视线与光照使用相同的 UV 坐标基底，保留 UV 镜像方向和非正交坐标轴。
- 对退化 UV 禁用横向视差偏移，对视线掠射角加入除零保护。
- 保留原函数的步进、质量等级回退、Pixel Depth Offset 和其他输出。
- 基于 UE4.26 的内置 ParallaxOcclusionMapping 修改；依赖均为引擎内置资产。
- 已在 UE4.26 中验证资产重新加载、方向节点连接，并完成启用/禁用遮蔽阴影两种配置下所有输出的 PCD3D_SM5 着色器编译，零错误、零警告。
- 尚未完成实际场景中的视觉回归测试；阴影算法本身沿用引擎版本。

## 脚本

`Scripts/create_enone_pom.py` 从引擎内置函数复制并生成资产，目标资产已存在时会停止以避免覆盖。

`Scripts/validate_enone_pom.py` 检查保存后的资产并创建仅存在于内存的编译测试材质。

启用 PythonScriptPlugin 和 EditorScriptingUtilities 后，可通过 UE4Editor-Cmd.exe 的 `-run=pythonscript -script=<脚本绝对路径>` 执行；编译验证使用 `-AllowCommandletRendering -d3d11 -unattended -nosound -nop4`。生成与验证报告写入项目的 `Saved/EnonePOM`。

本仓库包含基于 Unreal Engine 内置资产的修改版本；使用和再分发应遵循适用的 Unreal Engine 许可条款。
