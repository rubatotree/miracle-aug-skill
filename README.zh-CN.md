# MiracleAug

**单条示教，多样条件，保持任务一致的数据增强。**

[English](README.md) · 简体中文

MiracleAug 是一个面向 GPT-6 Astra 或具备同等及以上视觉、空间推理和编程能力模型的
agent skill。它从一条机器人示教出发，在 Blender 中重建可编辑场景，再生成带有同步
关节轨迹的增强示教数据。

输入可以是视频、本地机器人数据集，或 Hugging Face 数据集与 episode 编号。多视角
视频、图片和文字参考均可选。模型先保存可检查的场景重建中间结果，再生成指定数量
的有效示教，验证原生数据集，并按授权准备或完成上传。

## 场景重建结果

![MiracleAug 的重建场景、反向视角、玻璃、替换玩具、彩色光照与金属材质](assets/showcase/overview.jpg)

以上是已完成桌面场景的实际 Blender 渲染：标定后的场景、反向相机、玻璃与金属材质、
替换玩具和彩色光照。每格原生分辨率为 640 × 480，Cycles 采样上限为 128。
展示图没有混入原始相机画面或生成式插画。

窗外的遮挡方格是**应本场景用户要求**加入的隐私处理。MiracleAug 默认保留场景外观，
只有用户明确要求时才执行脱敏；相应检查覆盖反射、透射和打包的原始图像。

![静止、搬运、放置完成三个任务阶段](assets/showcase/task-sequence.jpg)

同一条标定示教的第 0、240、427 帧：静止、搬运，以及机械臂收回后物体留在杯内。
这些是经过完整轨迹检查的选定帧，不表示长期数据生成批次已经完成。

![相同相机与任务时刻下的 Cycles 和 Eevee 对比](assets/showcase/renderer-comparison.jpg)

同一相机、同一任务时刻的 Cycles 与 Eevee 渲染，分别使用 128 采样上限和 64 采样。
二者共享场景与轨迹，数据中保留实际渲染设置和质量标签；训练权重可配置，默认均为 1。

渲染设置、隐私范围与第三方资产来源见[展示结果记录](assets/showcase/README.md)。
这些图展示的是场景结果。准备本展示时，独立的 64 条 Cycles、1216 条 Eevee 生产批次
仍在运行，尚不宣称完整数据集上传完成，也不宣称已证明策略泛化收益。

## 管线涵盖的工作

- 米制、分离的场景几何，CAD/URDF 机器人运动学、相机与运动标定，原视角叠图和新视角检查。
- 相机、光照、材质、环境、物体与轨迹的微弱及强增强；影响接触或可达性时重新规划运动。
- 精确的通过数量、确定性候选、同类别补足、不可变检查点和可恢复的远程执行。
- 原生数据集验证、关节轨迹、动作语义、相机/物体变换、渲染器标签、数据来源与明确的局限。

未被拍到的表面会标注为推断。只有视频而没有关节/控制数据时，估计的运动必须标为
推断或合成，不能当作实测动作真值。数据有效性与策略泛化分别验证。

## 使用方式

将本目录放到 `~/.codex/skills/miracleaug`，或兼容 agent 的 skill 目录。入口是
[SKILL.md](SKILL.md)。可以直接使用自己的输入，不需要展示案例的私有数据或场景。

```bash
git clone https://github.com/rubatotree/miracle-aug-skill.git ~/.codex/skills/miracleaug
```

示例请求：

> 使用 $miracleaug，从 HF 的 owner/demo 中 episode 3 重建场景。
> 这段环绕视频作为可选几何参考。保存 Blender 重建检查点后，在我的 Ubuntu GPU 服务器
> 生成 100 条通过检查的新示教，其中 20 条 Cycles、80 条 Eevee。重点增加强光照、
> 材质和相机变化。输出 LeRobot 和关节轨迹，并上传到我指定的私有仓库。

也可以只提供 `demo.mp4`，不附额外参考，或者只要求重建。需要脱敏时，明确补充
“渲染或分享前对窗外打码”等要求；否则不会执行脱敏。模型会先检查现有信息，再询问
必要的缺项。

## 引用

如果在研究中使用 MiracleAug，请引用实际使用的版本。以下引用固定指向
**v0.1.3**，发布日期为 2026 年 9 月 10 日：

> Zhu, Y. (2026). *MiracleAug* (Version 0.1.3) [Computer software]. GitHub.
> https://github.com/rubatotree/miracle-aug-skill/tree/v0.1.3

```bibtex
@software{zhu2026miracleaug,
  author  = {Zhu, Yutian},
  title   = {{MiracleAug}},
  year    = {2026},
  date    = {2026-09-10},
  version = {0.1.3},
  url     = {https://github.com/rubatotree/miracle-aug-skill/tree/v0.1.3}
}
```

可下载 [CITATION.bib](CITATION.bib)，或使用 GitHub 根据
[CITATION.cff](CITATION.cff) 生成的 **Cite this repository** 入口。
复现此版本时请检出 `v0.1.3` 标签。目前使用固定版本的 GitHub 地址作为标识，尚未分配 DOI。

## 工具与验证

包内包含 episode 读取器、有限配额与证据记录工具、逐帧数据检查器、特定平台的
无界面 EGL 支持和合成测试。实际机器人/任务适配器由执行模型实现；本 skill 不是
适用于任意输入的预训练逆渲染或动作恢复模型。

核心辅助工具仅依赖 Python 3.10+ 标准库，读取源数据的可选依赖见
[requirements-source.txt](requirements-source.txt)。Blender 和原生数据集 SDK 按项目
选择版本，并写入运行记录。

```bash
python -m unittest discover -s tests -v
python scripts/package_skill.py --output dist/MiracleAug-skill.zip
```

测试覆盖配额、补足、恢复、不同状态/动作维度、多相机、时间/动作对齐和 LeRobot
v2/v3 episode 定位。具体证据与未验证项见[验证范围](references/validation.md)。
公开 CI 使用合成数据，不需要 GPU、私人数据或令牌。

本目录可直接作为独立 GitHub 仓库。分发包使用明确的文件白名单、相对链接检查和
SHA-256 清单，只有审核过的展示图会随代码提供；不包含原视频、场景文件、缓存或凭据。
MIT 许可覆盖原创代码和文档，第三方资产与展示结果的许可和署名单独记录。
