# CHANGELOG

## v3.1.0（2026-04-18）

将章节级质量框架快照内置到仓库中，并让分发产物保持自包含。

### 可用性升级

- **内置 framework 快照**：新增 `references/framework/`，包含 L1-L4 判定、G1/G2/G3 全局检查和章节质量标准
- **移除外部目录依赖**：`SKILL.md` 从本地 `references/framework/` 加载章节基线，不再依赖外部共享 framework 目录
- **通用 Prompt 重新打包**：`dist/check-prd-universal-prompt.md` 现在包含 SKILL 流程、framework 文件、14 维降级文件和附录，单文件即可运行
- **完整工作流入口**：README 增加 `PRD Productivity Toolkit` 链接，便于获取 create/check/Feishu 协作全套能力

## v3.0.0（2026-04-17）

引入统一章节 × L 级复杂度质量框架（V2），SKILL.md 全面重构。

### 核心架构变化

- **Path A / Path B 分流**：Phase 0 识别 PRD 结构，标准 14 章骨架走 Path A（章节路径），自由格式文档走 Path B（降级维度路径）
- **引入共享 prd-quality-framework**：L1-L4 复杂度分级、G1/G2/G3 全局检查统一从 `references/framework/` 渐进加载，与 `create-prd` 共享同一质量基线
- **渐进加载强制要求**：只在当前阶段加载所需框架文件，不预读整个框架

### Path A（章节路径）— 新增

- Phase 0 三步：L 级判定 → G1 产品类型 → 结构识别分流，显式输出 `评审预设` 块
- 按 L 级裁剪章节（`complexity-assessment.md §3`），跳过不适用章节
- 逐章加载 `prd-quality-framework/chapters/chN-*.md`，评级格式 `Ch{N} - 评级：[优秀/合格/待改进/严重缺失]`
- Ch10.2 强制执行逐页面/弹窗/表单走查
- Phase 6 终局综合：G2 文档结构完整性 + G3 重大风险 R1-R8

### Path B（降级维度路径）— 沿用并升级

- 沿用原 14 维度文件，格式改为 `维度 N - 评级：...`，不使用章节 ID
- Phase 6 G2 降级为"问题/目标/方案链路是否贯通"整体评估
- 报告末尾强制输出迁移建议：使用 `/create-prd` 重写为标准格式
- `appendix-veto.md` 顶部 R1-R8 声明已迁移至 `g3-major-risks.md`

## v2.0.0（2026-03-29）

重构为标准现代 Claude skill 目录。

### 结构升级

- 使用根级 `SKILL.md` 作为唯一入口
- 将 14 个维度与 2 个附录迁入 `references/`
- 删除旧的平铺式 skill 入口设计

### 工程化能力

- 新增 `scripts/build.py` 生成通用 Prompt 与 `.skill` 包
- 新增 `scripts/validate.py` 做结构和生成物校验
- 新增 `scripts/install_skill.py`，以整个目录安装到 `~/.claude/skills/check-prd`
- 新增基础任务 eval 与触发 eval 资产

### 分发变化

- `dist/check-prd-universal-prompt.md` 改为生成物
- 安装方式从“复制多份 Markdown 到全局 skills 目录”改为“安装整个 skill 目录”

## v1.0.0（2026-03-28）

首次发布。

### 包含维度

- 14个检查维度（01-业务分析 至 14-运营方案）
- 2个附录（重大风险项清单 + 检查报告模板）

### 核心特性

- 逐维度即时输出机制：每个维度检查完立即输出详细分析，防止上下文压力导致分析质量下降
- 组件级交互设计分析（维度09新增9.6节）：对PRD中每个界面、弹窗、表单逐一评估
- 企业架构层检查（维度06新增6.5-6.9节）：适用于0-1新系统设计的应用规划、数据架构、集成治理检查
- 运营方案独立为维度14：需求收集、功能推广、用户培训、效果评估、数据埋点、数据迁移
- 产品定型机制：第零步根据商业属性×功能类型动态调整适用维度
- 检查深度标准：强制引用PRD原文定位问题、给出可执行改进示例、推断隐性问题
