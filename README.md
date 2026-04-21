# check-prd — B端 PRD 质量审查

> **让 AI 用行业经典方法论帮你审 PRD。**

写 PRD 的人很多，能系统审 PRD 的人很少。审一份 PRD 需要同时具备业务理解、产品架构、数据建模、交互设计、商业分析等多个维度的判断力——这种能力通常需要十年以上的实战经验。

check-prd 把这种审查能力工具化了。它基于《决胜B端》系列方法论，用 **14 个维度**逐项检查你的 PRD，指出遗漏、矛盾和风险，给出具体的改进建议。

## 为什么这套审查框架有效

因为它不是凭空编出来的 checklist，而是从两本经过市场验证的方法论著作中提炼的：

- **《决胜B端（第二版）》** — 豆瓣 8.6 分，重印 13 次，B端从业者经典案头参考书。覆盖业务调研、产品定位、架构设计、数据建模、流程设计、需求管理的完整方法论
- **《决胜体验设计》** — 聚焦 B端体验设计，从交互原则到用户旅程到 AI 交互模式的系统框架

这两本书的方法论已经在华为、京东、宝洁、工商银行等上百家企业的培训和咨询中验证过。check-prd 做的事情，就是**让 AI 用这套方法论帮你审文档**。

## 14 个检查维度

| # | 维度 | 检查什么 |
|---|------|---------|
| 1 | 业务调研 | 业务背景是否清晰、利益方是否识别完整、业务流程是否梳理到位 |
| 2 | 产品定型 | 产品类型判断是否准确、商业属性是否明确 |
| 3 | 产品定位 | 价值主张是否清晰、目标客群是否聚焦、竞争差异是否成立 |
| 4 | 场景分析 | 核心场景是否覆盖、用户旅程是否完整、痛点是否识别到位 |
| 5 | 文档结构 | PRD 结构是否完整、章节逻辑是否自洽 |
| 6 | 产品架构 | 应用架构是否合理、模块划分是否清晰、系统边界是否明确 |
| 7 | 数据模型 | ER 模型是否完整、实体关系是否正确、关键字段是否定义 |
| 8 | 流程设计 | 业务流程是否完整、状态机是否覆盖、异常路径是否考虑 |
| 9 | 交互体验 | 页面设计是否合理、操作路径是否高效、反馈机制是否完善 |
| 10 | 商业分析 | 盈利模式是否可行、ROI 是否测算、市场定位是否合理 |
| 11 | MVP 策略 | 最小可行产品范围是否合理、验证假设是否明确 |
| 12 | 异常处理 | 边界条件是否考虑、错误处理是否完善、降级方案是否设计 |
| 13 | AI 功能 | AI 功能设计是否合理、人机协同边界是否清晰（有 AI 功能时适用） |
| 14 | 运营计划 | 上线推广方案是否完整、监控指标是否定义、迭代策略是否明确 |

每个维度独立输出检查结论，最后汇总为 P0-P3 分级的问题清单和 Top 10 改进建议。

### 区分产品类型，针对性审查

B端自研系统和商业化软件的设计逻辑差异很大——自研系统关注流程效率和内部协同，商业化产品关注市场定位和盈利模式。用同一套标准审两类 PRD，要么漏检、要么误判。

check-prd 在审查开始前会先做**产品定型**（商业化产品 or 企业自研 × 业务型/工具型/交易型/基础服务型），然后自动调整每个维度的检查重点和适用性：

- **商业化产品**：加重商业分析、竞品定位、MVP 策略、定价模式的检查力度
- **企业自研系统**：加重业务流程覆盖度、权限模型、数据集成、异常处理的检查力度
- 不适用的维度自动标记跳过，不会用商业化标准去审自研系统

## 快速开始

### 方式一：任意大模型（不需要安装任何工具）

1. 下载 [`dist/check-prd-universal-prompt.md`](dist/check-prd-universal-prompt.md)
2. 打开你常用的大模型（ChatGPT、Gemini、DeepSeek、Kimi、通义千问等均可）
3. 先上传或粘贴你的 PRD
4. 再把 `check-prd-universal-prompt.md` 的内容粘贴进去，发送

> 建议使用能力较强的模型（如 GPT-4o、Claude、Gemini Pro、DeepSeek-R1）以获得更好的检查效果。

### 方式二：Claude Code 集成

```bash
git clone https://github.com/pmyangkun/check-prd-skill.git
cd check-prd-skill
bash scripts/install.sh          # Mac/Linux
# .\scripts\install.ps1          # Windows PowerShell
```

安装后直接使用：

```text
/check-prd path/to/prd.pdf
```

或者自然语言触发：
- "帮我审一下这个 B端 PRD"
- "看看这份需求文档还有什么漏洞"
- "评一下这个 SaaS 产品方案"

## 与 create-prd 形成闭环

| 环节 | 工具 | 作用 |
|------|------|------|
| 创建 | [create-prd](https://github.com/pmyangkun/create-prd-skill) | 从业务描述生成 14 章结构化 PRD 初稿 |
| 审查 | **check-prd** | 用 14 维度逐项检查，输出问题清单和改进建议 |

先 create，再 check，迭代优化。

## 社区贡献

感谢 [@Scofy0123](https://github.com/Scofy0123) 的持续贡献！除了 main 分支的标准版本外，仓库还提供两个**社区扩展分支**供有不同需求的用户选用：

| 分支 | 作者 | 特色 |
|------|------|------|
| `main` | 杨堃 | 标准版——固定 14 维度 PRD 审查 |
| [`community/complexity-aware`](https://github.com/pmYangKun/check-prd-skill/tree/community/complexity-aware) | @Scofy0123 扩展 | 复杂度感知版——先判 L1-L4 需求等级，规范 PRD 走章节路径，非规范文档降级到 14 维度路径 |
| [`飞书 CLI 协作版`](https://github.com/pmYangKun/check-prd-skill/tree/check-prd-skill飞书CLI协作版(Special-tks-to-Scofy)) | @Scofy0123 扩展 | 飞书协作版——将 PRD 审查接入飞书文档协作闭环，支持评论回写、反馈收集、确认修改、交付判断 |

### 复杂度感知版（community/complexity-aware）

不再一律按 14 维度硬查。先识别 PRD 结构：
- **Path A：章节路径**——当 PRD 按标准 14 章组织时，按章节质量基线逐章审查
- **Path B：降级维度路径**——当文档是自由格式、散装需求、PPT 转写时，回退到经典 14 维审查

并引入 **L1-L4 复杂度分级**——L1 配置级、L2 规则级、L3 模块级、L4 系统级，按等级裁剪评审深度，避免用 L4 标准去评 L1 配置卡。

切换使用：
```bash
git checkout community/complexity-aware
```

### 飞书 CLI 协作版

将 PRD 审查接入飞书文档协作闭环：自动将审查意见作为评论回写到飞书文档、按规则收集修改反馈、支持 L1-L4 章节化审查范围选择。适合团队已在飞书协作场景下使用。

如果你想直接拿到**生成 + 审查 + 飞书协作闭环**的完整工作流，可以看 @Scofy0123 的独立仓库：
- [`PRD Productivity Toolkit`](https://github.com/Scofy0123/prd-productivity-toolkit)

## 仓库结构

```text
SKILL.md                             # Claude Code skill 入口
references/dimensions/               # 14 个维度的源文件
references/appendices/               # 风险清单与报告模板
dist/check-prd-universal-prompt.md   # 通用 Prompt（直接拿去用）
scripts/
  install.sh / install.ps1           # 安装脚本（Mac/Linux / Windows）
  install_skill.py                   # 安装核心逻辑
  build.py                           # 重新生成通用 Prompt
  validate.py                        # 校验结构和生成物
evals/                               # eval 种子
```

## 关于作者

**杨堃**，《决胜B端》（豆瓣 8.6 分，重印 13 次）作者，B端产品专家。中国科学院大学 MBA 特聘企业导师，服务客户涵盖华为、京东、百度、宝洁、工商银行等上百家企业。

## 版本历史

见 [CHANGELOG.md](CHANGELOG.md)
