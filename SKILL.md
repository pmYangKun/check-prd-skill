---
name: check-prd
description: Review B端 PRDs, requirement docs, SaaS or enterprise product specs, and system design documents with a 14-dimension quality framework. Use this whenever the user asks to check, review, critique, improve, or find gaps in a PRD, 需求文档, 产品方案, B端系统设计, SaaS spec, or similar design document, even if they only say “帮我看看这个 PRD/方案/需求”.
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

## Before You Review

1. Read the document in full before judging individual dimensions.
2. Determine and record:
   - 商业属性: 自研内部系统 or 商业化产品
   - 功能类型: 业务型管理软件 / 工具型软件 / 交易型平台 / 基础服务型
   - 文档范围: 0-1 系统级规划 or 迭代 / 模块级需求
   - 是否涉及 AI 功能
3. Mark non-applicable dimensions before starting the ordered review.

### Applicability Rules

| 维度 | 适用条件 | 不适用时处理 |
| --- | --- | --- |
| 07-数据建模 | 仅业务型管理软件和交易型平台 | 标注“不适用”，仅检查关键数据结构 |
| 10-商业分析 | 仅商业化产品 | 自研内部系统只检查投入产出分析 |
| 03-竞品分析子项 | 仅商业化产品 | 自研内部系统改为同类系统参考 |
| 06-企业架构层 6.5-6.9 | 仅 0-1 新系统设计或系统级规划 | 迭代需求只做 6.1-6.4 |
| R8-多租户风险项 | 仅商业化 SaaS 产品 | 标注“不适用” |
| 13-AI 功能 | 仅文档涉及 AI 功能 | 标注“不适用” |

## Output Contract

### Non-negotiable behavior

- Review dimensions in the exact order listed below.
- After each dimension is completed, immediately output that dimension's detailed analysis.
- Do not batch all dimensions and summarize only at the end.
- Every finding must point to a concrete location in the PRD or clearly say the evidence is missing.

### Required per-dimension format

```md
## 维度[编号] - [名称] ｜ 评级：[优秀 / 合格 / 待改进 / 严重缺失]

### 具体发现

**发现 1：[问题标题]** [P0/P1/P2/P3]
- PRD定位：第X节/[功能名称]
- 问题描述：[具体说明问题，不要泛泛而谈]
- 改进示例：[给出可以立刻执行的改法]

### 隐性问题推断
结合产品类型和业务场景，列出 PRD 没写但按道理必须考虑的问题。
```

### Minimum quality bar

- Each dimension must contain at least 3 concrete findings, or 3 explicit justifications for why no issue was found.
- Findings must be anchored to real sections, flows, screens, or fields from the PRD.
- Recommendations must be executable, not vague.
- For dimension 09, inspect each described page, dialog, form, or action one by one and call out missing interaction details explicitly.

## Review Sequence

### Phase 0: Product typing

- Finish the product typing step above before any dimension review.

### Phase 1: Business and positioning

1. [01 业务分析质量](references/dimensions/check-prd-01-business.md)
2. [02 产品类型适配性](references/dimensions/check-prd-02-product-type.md)
3. [03 产品定位合理性](references/dimensions/check-prd-03-positioning.md)

### Phase 2: Scenario and structure

4. [04 场景分析与用户旅程](references/dimensions/check-prd-04-scenario.md)
5. [05 文档结构完整性](references/dimensions/check-prd-05-structure.md)
6. [06 架构设计质量](references/dimensions/check-prd-06-architecture.md)

### Phase 3: Detailed design

7. [07 数据建模质量](references/dimensions/check-prd-07-data.md)
8. [08 流程与角色设计](references/dimensions/check-prd-08-process.md)
9. [09 交互设计质量](references/dimensions/check-prd-09-ux.md)

### Phase 4: Value and evolution

10. [10 商业分析深度](references/dimensions/check-prd-10-commercial.md)
11. [11 MVP 策略与演进蓝图](references/dimensions/check-prd-11-mvp.md)
12. [14 运营方案与效果跟踪](references/dimensions/check-prd-14-operations.md)

### Phase 5: Robustness and forward-looking checks

13. [12 异常处理与健壮性设计](references/dimensions/check-prd-12-exception.md)
14. [13 AI 功能设计质量](references/dimensions/check-prd-13-ai.md)

### Phase 6: Final synthesis

- Apply the major-risk checklist from [重大风险项清单](references/appendices/check-prd-appendix-veto.md)
- Build the final navigation report using [检查报告模板](references/appendices/check-prd-appendix-guide.md)

## Final Report Requirements

After all dimensions have been output in detail, produce a final synthesis that includes:

1. 产品定型说明
2. 各维度发现摘要
3. 重大风险项
4. 按 P0-P3 排序的问题清单
5. 亮点记录
6. Top 10 改进建议

The final report is a navigation layer over the dimension-by-dimension outputs, not a replacement for them.

## Working Style

- The goal is to reveal blind spots and improve the document, not to shame the author.
- Be strict about evidence and specificity.
- Adapt judgments to product type, product stage, and document scope.
- If the document is partial, state what cannot be validated and continue with the evidence available.
