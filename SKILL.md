---
name: check-prd
description: Review B端 PRDs, requirement docs, SaaS or enterprise product specs, and system design documents with a 14-dimension quality framework. Use this whenever the user asks to check, review, critique, improve, or find gaps in a PRD, 需求文档, 产品方案, B端系统设计, SaaS spec, or similar design document, even if they only say "帮我看看这个 PRD/方案/需求".
---

# check-prd

对 B端 PRD 或系统设计文档进行严格、可执行的质量审查。

支持显式调用（如 `/check-prd path/to/prd.pdf`）和自动触发（当用户明确要求审查 PRD、需求文档、产品方案或企业系统设计时）。

## 输入

- 通过 `$ARGUMENTS` 传入的文件路径
- 或用户粘贴的 PRD / 系统设计文档内容
- 或不完整的文档（基于现有内容审查，并明确指出缺失的上下文）

如有参数传入，优先作为输入源：

$ARGUMENTS

## 审查前的准备

1. 完整阅读文档后再对各维度进行评判。
2. 确定并记录：
   - 商业属性：自研内部系统 or 商业化产品
   - 功能类型：业务型管理软件 / 工具型软件 / 交易型平台 / 基础服务型
   - 文档范围：0-1 系统级规划 or 迭代 / 模块级需求
   - 是否涉及 AI 功能
3. 在开始逐维度审查前，标记不适用的维度。

### 适用性规则

| 维度 | 适用条件 | 不适用时处理 |
| --- | --- | --- |
| 07-数据建模 | 仅业务型管理软件和交易型平台 | 标注"不适用"，仅检查关键数据结构 |
| 10-商业分析 | 仅商业化产品 | 自研内部系统只检查投入产出分析 |
| 03-竞品分析子项 | 仅商业化产品 | 自研内部系统改为同类系统参考 |
| 06-企业架构层 6.5-6.9 | 仅 0-1 新系统设计或系统级规划 | 迭代需求只做 6.1-6.4 |
| R8-多租户风险项 | 仅商业化 SaaS 产品 | 标注"不适用" |
| 13-AI 功能 | 仅文档涉及 AI 功能 | 标注"不适用" |

## 输出规范

### 不可违反的行为规则

- 严格按照下方列出的顺序逐维度审查。
- 每完成一个维度，立即输出该维度的详细分析。
- 不得将所有维度攒到最后一起总结输出。
- 每条发现必须指向 PRD 中的具体位置，或明确说明缺少相关证据。

### 每个维度的输出格式

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

### 最低质量标准

- 每个维度至少包含 3 条具体发现，或 3 条对"为何没有问题"的明确说明。
- 发现必须锚定到 PRD 中的真实章节、流程、页面或字段。
- 建议必须可执行，不得笼统模糊。
- 对于维度 09（交互设计），逐一检查文档中描述的每个页面、弹窗、表单和关键操作，明确指出缺失的交互细节。

## 审查顺序

### 阶段 0：产品定型

- 在审查任何维度之前，先完成上述产品定型步骤。

### 阶段 1：业务与定位

1. [01 业务分析质量](references/dimensions/check-prd-01-business.md)
2. [02 产品类型适配性](references/dimensions/check-prd-02-product-type.md)
3. [03 产品定位合理性](references/dimensions/check-prd-03-positioning.md)

### 阶段 2：场景与结构

4. [04 场景分析与用户旅程](references/dimensions/check-prd-04-scenario.md)
5. [05 文档结构完整性](references/dimensions/check-prd-05-structure.md)
6. [06 架构设计质量](references/dimensions/check-prd-06-architecture.md)

### 阶段 3：详细设计

7. [07 数据建模质量](references/dimensions/check-prd-07-data.md)
8. [08 流程与角色设计](references/dimensions/check-prd-08-process.md)
9. [09 交互设计质量](references/dimensions/check-prd-09-ux.md)

### 阶段 4：价值与演进

10. [10 商业分析深度](references/dimensions/check-prd-10-commercial.md)
11. [11 MVP 策略与演进蓝图](references/dimensions/check-prd-11-mvp.md)
12. [14 运营方案与效果跟踪](references/dimensions/check-prd-14-operations.md)

### 阶段 5：健壮性与前瞻性检查

13. [12 异常处理与健壮性设计](references/dimensions/check-prd-12-exception.md)
14. [13 AI 功能设计质量](references/dimensions/check-prd-13-ai.md)

### 阶段 6：最终汇总

- 执行[重大风险项清单](references/appendices/check-prd-appendix-veto.md)检查
- 按照[检查报告模板](references/appendices/check-prd-appendix-guide.md)生成最终报告

## 最终报告要求

所有维度逐一输出完毕后，生成一份最终汇总报告，包含：

1. 产品定型说明
2. 各维度发现摘要
3. 重大风险项
4. 按 P0-P3 排序的问题清单
5. 亮点记录
6. Top 10 改进建议

最终报告是对各维度详细输出的导航索引，不是替代。

## 工作风格

- 目标是发现盲区、改进文档，不是给作者难堪。
- 对证据和具体性保持严格要求。
- 根据产品类型、产品阶段和文档范围调整判断标准。
- 如果文档不完整，说明哪些内容无法验证，然后基于现有证据继续审查。
