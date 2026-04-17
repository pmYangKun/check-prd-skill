# prd-quality-framework

> **B 端 PRD 质量统一框架** — create-prd 和 check-prd 两个 skill 的共享知识基础。

## 这是什么

一套以**章节**为骨架、以 **L1-L4 复杂度分级**为深度标尺的 B 端 PRD 质量标准：

- **create-prd 按本框架写作** → 写到 L 级对应的深度即可，不过度设计
- **check-prd 按本框架审查** → 按 PRD 当前 L 级评判，避免用 L4 标准要求 L1 配置卡

两个 skill 共用同一套质量标准，形成"写-查"闭环。

## 核心设计

### 1. 四个复杂度级别

| L 级 | 定义 | 典型产出物 |
|------|------|-----------|
| L1 | 配置级 / 规则微调 | 1 页配置卡 |
| L2 | 规则级 / 轻量功能 | 2-3 页规则说明 |
| L3 | 模块级 / 完整功能块 | 5-8 页模块 PRD |
| L4 | 系统级 / 0-1 新系统 | 完整 14 章 PRD |

### 2. 十四个章节骨架

按《决胜B端》B 端 PRD 模板组织，每个章节有独立的 L1-L4 质量标准：

```
Ch1  项目背景          Ch8   术语定义
Ch2  需求基本情况      Ch9   参考文献
Ch3  商业分析          Ch10  功能需求（Ch10 分三块 10.1/10.2/10.3）
Ch4  项目目标          Ch11  数据埋点
Ch5  方案概述          Ch12  角色和权限
Ch6  项目范围          Ch13  运营方案
Ch7  项目风险          Ch14  待决事项
```

### 3. 三个全局检查

不属于任何单一章节的跨章节检查项：

- **G1 产品类型契合度**（Phase 0）：确认产品类型与方法论一致
- **G2 文档结构完整性**（Final）：章节覆盖 + 逻辑贯通 + 术语一致
- **G3 重大风险综合判断**（Final）：R1-R8 八类整体风险扫描

## 目录结构

```
prd-quality-framework/
├── README.md                        ← 本文件
├── complexity-assessment.md         ← 核心：L 级判定 + 章节适用表 + 产品类型叠加 + check 层级验证
├── chapters/                        ← 按章节的质量标准
│   ├── ch01-background.md
│   ├── ch02-basic.md
│   ├── ch03-commercial.md
│   ├── ch04-goals.md
│   ├── ch05-overview.md
│   ├── ch06-scope.md
│   ├── ch07-risks.md
│   ├── ch08-09-terms.md             ← Ch8 + Ch9 合并（都属轻量章节）
│   ├── ch10-1-framework.md          ← Ch10.1 产品框架
│   ├── ch10-2-detail.md             ← Ch10.2 需求详解
│   ├── ch10-3-exception.md          ← Ch10.3 异常处理
│   ├── ch11-tracking.md
│   ├── ch12-permissions.md
│   ├── ch13-operations.md
│   └── ch14-tbd.md
└── global-checks/                   ← 跨章节全局检查
    ├── g1-product-type-fit.md
    ├── g2-document-structure.md
    └── g3-major-risks.md
```

## 使用规则（渐进式加载）

为避免污染上下文，两个 skill 都应按需加载本框架文件，**绝不一次全读**：

### create-prd 的加载路径

1. **启动阶段**：读 `complexity-assessment.md`（判定 L 级 + 产品类型）+ `global-checks/g1-product-type-fit.md`
2. **写作章节 N 时**：加载 `chapters/chN-*.md`（只读当前写的那章）
3. **自检阶段**：读 `global-checks/g2-document-structure.md`

### check-prd 的加载路径

1. **Phase 0**：读 `complexity-assessment.md` + `global-checks/g1-product-type-fit.md`
2. **章节检查阶段**：按 PRD 实际存在的章节逐个加载对应 `chapters/chN-*.md`
3. **综合判断阶段**：读 `global-checks/g2-document-structure.md` + `global-checks/g3-major-risks.md`

## 与 check-prd 原 14 维度的关系

check-prd 仍保留原 14 个维度文件（`.agents/skills/check-prd/references/dimensions/check-prd-01~14.md`）作为**降级方案**：

- 针对不按 create-prd 格式编写的 PRD（自由格式、散装文档），无法按章节检查时
- check-prd SKILL 通过判断 PRD 结构决定走"章节路径"还是"维度路径"
- 降级路径也遵循渐进加载原则，只读与检查维度直接相关的文件

原 14 维度 → 章节的映射关系见 `complexity-assessment.md` 注释或 `lovely-bubbling-oasis.md` 计划文件。

## 章节质量标准文件格式

每个 `chapters/chN-*.md` 统一结构：

```
# ChN XXX — 质量标准

> 章节来源说明（create-prd 对应章节 + check-prd 维度来源）

## 章节目标

## 各层级质量标准
### L1（配置级）
### L2（规则级）
### L3（模块级）
### L4（系统级）

## 校验规则
（阻断项 / Warning）

## 常见问题
| 问题现象 | 根本原因 | 改进方向 |
```

这样 create 的写作要求和 check 的检查点自然合一。

## 维护规则

- 修改任何 `chapters/*` 或 `global-checks/*` 文件前，先在 `complexity-assessment.md §3` 检查该章节的 L 级适用表是否需要同步更新
- 新增章节/全局检查项时，更新本 README 目录结构
- 变更后两个 skill（create-prd、check-prd）的相关测试用例都需要回归一次
