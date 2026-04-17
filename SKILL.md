---
name: check-prd
description: Review B端 PRDs, requirement docs, SaaS or enterprise product specs, and system design documents against the shared prd-quality-framework. Use this whenever the user asks to check, review, critique, improve, or find gaps in a PRD, 需求文档, 产品方案, B端系统设计, SaaS spec, or similar design document, even if they only say "帮我看看这个 PRD/方案/需求".
---

# check-prd

Use this skill to produce a rigorous, actionable review of a B端 PRD or system design document.

It supports both explicit invocation such as `/check-prd path/to/prd.pdf` and automatic invocation when the request is clearly about reviewing a PRD, requirement document, product plan, or enterprise system design.

## Inputs

- A file path passed in through `$ARGUMENTS`
- Or pasted PRD / system design content
- Or a partial document when that is all the user has; review based on available evidence and call out the missing context explicitly

If arguments are present, treat them as the preferred input source:

$ARGUMENTS

---

## How the review is organized

This skill uses the **shared prd-quality-framework** (at `references/framework/`) as its quality backbone, with a **fallback path** for PRDs that do not follow the standard chapter structure.

```
┌──────────────────────────┐
│ Phase 0: 全局准备          │  ← 加载 complexity-assessment.md + g1
│  - L 级判定               │
│  - 产品类型 (G1)          │
│  - 结构识别 → Path 分流    │
└────────────┬─────────────┘
             │
      ┌──────┴──────┐
      ▼             ▼
  Path A           Path B
  章节路径         降级维度路径
  (推荐)           (PRD 不按标准写时)
      │             │
      └──────┬──────┘
             ▼
┌──────────────────────────┐
│ Phase 6: 终局综合          │  ← 加载 g2 + g3 + appendix-veto (P0-P3)
│  - G2 文档结构完整性       │
│  - G3 重大风险 R1-R8      │
│  - P0-P3 对照 + Final Report │
└──────────────────────────┘
```

**Progressive loading is mandatory** — only load the framework files relevant to the current phase / chapter / dimension. Do not preload everything.

---

## Phase 0 — 全局准备

读 `references/framework/complexity-assessment.md` 完成以下三步，**不要**此时加载任何章节或维度文件：

### Step 1 — 判定 L 级

按 `complexity-assessment.md §1` 的四步决策法（先用户感知一句话描述变更，再套决策树，再消歧义，再看信号）给出 L1 / L2 / L3 / L4。

### Step 2 — 判定产品类型（G1）

加载 `references/framework/global-checks/g1-product-type-fit.md`，确定：

- 商业属性：自研内部系统 or 商业化产品
- 功能类型：业务管理型 / 工具型 / 交易平台型 / 基础服务型
- 文档范围：0-1 系统级规划 or 迭代 / 模块级
- 是否涉及 AI 功能

### Step 3 — 结构识别并分流（关键判断）

**不用硬阈值**。通读 PRD 整体结构，让模型判断 PRD 是否大致遵循 create-prd 的 14 章骨架：

- **Path A（章节路径 — 推荐）**：PRD 章节划分与标准模板基本一致（即使命名略有差异、部分章节缺失），核心"背景→目标→方案→功能设计→风险/运营"的叙述骨架可识别
- **Path B（降级维度路径）**：PRD 是自由格式、散装文档、PPT 截屏转文字、纯需求清单、或章节组织完全不同于标准模板，无法稳定按章节寻址

判定时参考信号（非硬规则，辅助模型判断）：
- 是否能定位到"功能设计 / 需求详解"段落（类似 Ch10.2）
- 是否能定位到"目标 / 价值 / 收益"段落（类似 Ch4）
- 是否能定位到"背景 / 问题 / 场景"段落（类似 Ch1）
- 章节命名是否接近《决胜B端》PRD 模板

### Phase 0 输出

在评审开头**显式声明**：

```md
## 评审预设

- 文档级别：L{X}（{级别名}）
- 产品类型：{商业属性} × {功能类型}
- 评审路径：Path A 章节路径 / Path B 降级维度路径（并给出一句话理由）
- 不适用的章节/维度：{列表，按 complexity-assessment.md §3 & §5}
- AI 功能：{涉及/不涉及}
```

---

## Path A — 章节路径评审

### 加载规则（渐进式）

当评审第 N 章时，**按需**加载：
`references/framework/chapters/chN-*.md`

评审完毕该章节后不必保留在上下文。

### 章节顺序

按 PRD 标准章节顺序逐章节评审，跳过 L 级不适用的章节（见 `complexity-assessment.md §3`）：

| # | 章节 | 质量标准文件 |
|---|------|-------------|
| 1 | Ch1 项目背景 | `chapters/ch01-background.md` |
| 2 | Ch2 需求基本情况 | `chapters/ch02-basic.md` |
| 3 | Ch3 商业分析 | `chapters/ch03-commercial.md` |
| 4 | Ch4 项目目标 | `chapters/ch04-goals.md` |
| 5 | Ch5 方案概述 | `chapters/ch05-overview.md` |
| 6 | Ch6 项目范围 | `chapters/ch06-scope.md` |
| 7 | Ch7 项目风险 | `chapters/ch07-risks.md` |
| 8 | Ch8-9 术语与参考文献 | `chapters/ch08-09-terms.md` |
| 9 | Ch10.1 产品框架 | `chapters/ch10-1-framework.md` |
| 10 | Ch10.2 需求详解 | `chapters/ch10-2-detail.md` |
| 11 | Ch10.3 异常处理 | `chapters/ch10-3-exception.md` |
| 12 | Ch11 数据埋点 | `chapters/ch11-tracking.md` |
| 13 | Ch12 角色和权限 | `chapters/ch12-permissions.md` |
| 14 | Ch13 运营方案 | `chapters/ch13-operations.md` |
| 15 | Ch14 待决事项 | `chapters/ch14-tbd.md` |

### Path A 每章节输出格式

```md
## Ch{X} - {章节名} ｜ L{N} 适用 ｜ 评级：[优秀 / 合格 / 待改进 / 严重缺失]

### 具体发现

**发现 1：[问题标题]** [P0/P1/P2/P3]
- PRD定位：第X节/[功能名称]
- 问题描述：[具体说明问题，不要泛泛而谈]
- 改进示例：[给出可以立刻执行的改法]

**发现 2：...**
**发现 3：...**

### 隐性问题推断
结合产品类型、L 级、章节前后文，列出 PRD 没写但按本章节质量标准必须考虑的问题。
```

> Ch10.2 的评审必须**逐页面/弹窗/表单专项走查**（继承原 D09 的组件级交互设计分析方法），不要只做合规勾选。

---

## Path B — 降级维度路径评审

### 何时使用

Phase 0 Step 3 判定走 Path B 时采用。原因通常是 PRD 未按 create-prd 14 章结构书写，无法稳定按章节寻址。

### 加载规则（渐进式）

**按需**加载 `references/dimensions/check-prd-NN-*.md`，一次加载一个，评审完不再保留在上下文。

### 维度顺序（沿用原 14 维度）

#### Phase 1: Business and positioning
1. [01 业务分析质量](references/dimensions/check-prd-01-business.md)
2. [02 产品类型适配性](references/dimensions/check-prd-02-product-type.md)
3. [03 产品定位合理性](references/dimensions/check-prd-03-positioning.md)

#### Phase 2: Scenario and structure
4. [04 场景分析与用户旅程](references/dimensions/check-prd-04-scenario.md)
5. [05 文档结构完整性](references/dimensions/check-prd-05-structure.md)
6. [06 架构设计质量](references/dimensions/check-prd-06-architecture.md)

#### Phase 3: Detailed design
7. [07 数据建模质量](references/dimensions/check-prd-07-data.md)
8. [08 流程与角色设计](references/dimensions/check-prd-08-process.md)
9. [09 交互设计质量](references/dimensions/check-prd-09-ux.md)

#### Phase 4: Value and evolution
10. [10 商业分析深度](references/dimensions/check-prd-10-commercial.md)
11. [11 MVP 策略与演进蓝图](references/dimensions/check-prd-11-mvp.md)
12. [14 运营方案与效果跟踪](references/dimensions/check-prd-14-operations.md)

#### Phase 5: Robustness and forward-looking checks
13. [12 异常处理与健壮性设计](references/dimensions/check-prd-12-exception.md)
14. [13 AI 功能设计质量](references/dimensions/check-prd-13-ai.md)

### Path B 每维度输出格式

```md
## 维度[编号] - [名称] ｜ L{N} 适用 ｜ 评级：[优秀 / 合格 / 待改进 / 严重缺失]

### 具体发现
**发现 1：...** [P0/P1/P2/P3]
...

### 隐性问题推断
...
```

维度 09（交互设计）必须执行逐页面/弹窗/表单/操作的专项走查，方法见该维度文件 §9.6。

### Path B 的 L 级裁剪（原表）

| L 级 | 跳过维度 |
|------|---------|
| L1 | 06、07、08（完整版）、10、11、14 |
| L2 | 06、07、10、11 |
| L3 | 10（可选）、11（完整版）；06 只做 6.1-6.4 |
| L4 | 全量 |

产品类型裁剪（07 仅业务型/交易型，10 仅商业化，R8 仅 SaaS，13 仅涉及 AI）照常应用。

---

## 通用 Output Contract（两条路径都遵守）

### Non-negotiable behavior

- 按上面约定的顺序评审，**不要跳跃**。
- 每完成一个章节（Path A）或一个维度（Path B）就立即输出该章节/维度的详细分析，**不要批量累积到最后**。
- 每条 finding 必须指向 PRD 中具体位置（章节号、页面名、功能名），或明确声明证据缺失。
- 对没有问题的章节/维度，也要列出 **≥ 3 条显式理由**说明"为什么无需整改"。

### Minimum quality bar

- 每个章节/维度 ≥ 3 条 concrete findings，或 3 条"为何无问题"的明确依据。
- findings 必须锚定到真实的章节、流程、页面、字段。
- 改进建议必须可立刻执行，不写"应加强""应完善"等空话。
- Ch10.2（Path A）或维度 09（Path B）必须逐页面/弹窗/表单走查。

---

## Phase 6 — 终局综合（两条路径合流）

评审完所有章节/维度后，按顺序加载以下文件并生成最终报告：

### Step 1 — G2 文档结构完整性

加载 `references/framework/global-checks/g2-document-structure.md`。

执行整体评估：
- 结构完整性（L 级覆盖、标题层级）
- **逻辑贯通性（最核心）**：Ch1→Ch4→Ch10 链路、Ch10 内部三块对齐、Ch4→Ch11 目标可度量、Ch6→Ch12 自洽
- 可读性、术语一致性

Path B 降级时，以上检查改为"PRD 整体的问题/目标/方案链路是否贯通"，不要求严格章节号对应。

### Step 2 — G3 重大风险 R1-R8

加载 `references/framework/global-checks/g3-major-risks.md`。

扫描 R1-R8 重大风险：方向 / 商业 / 资源 / 架构 / 执行 / 数据合规 / AI / 集成上游。每条命中的风险必须引用 PRD 具体位置并给出下一步建议。

### Step 3 — P0-P3 常见问题对照

加载 `references/appendices/check-prd-appendix-veto.md` 的"常见问题对照表"部分，用于对 findings 做 P0-P3 归档参考（注：该文件顶部的"重大风险清单 R1-R8"已被 G3 接管，不再从此处读取 R 判断）。

### Step 4 — Final Report

按 `references/appendices/check-prd-appendix-guide.md` 的模板生成最终综合报告，必须包含：

1. **产品定型说明**（Phase 0 输出的 L 级 + 产品类型 + 评审路径）
2. **各章节/维度发现摘要**（Path A 或 Path B 的逐节输出汇总）
3. **重大风险项**（G3 命中的 R 项）
4. **按 P0-P3 排序的问题清单**
5. **亮点记录**
6. **Top 10 改进建议**

Final Report 是在逐节详细输出之上的**导航层**，不替代 Phase 1-5 的详细输出。

---

## Working Style

- The goal is to reveal blind spots and improve the document, not to shame the author.
- Be strict about evidence and specificity.
- Adapt judgments to product type, L 级, and document scope.
- If the document is partial, state what cannot be validated and continue with the evidence available.
- **Respect progressive loading** — never read more framework files than the current phase needs.
