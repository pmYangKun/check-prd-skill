# check-prd — B端PRD质量检查工具

基于《决胜B端（第二版）》《决胜体验设计》《决胜B端PRD模板 v2.0》构建，从14个维度对B端产品PRD进行系统化质量检查。

支持两种使用方式：**Claude Code Skill**（推荐）和**通用 Prompt**（适用于 ChatGPT、Gemini 等任意 LLM）。

## 功能特性

- **14个检查维度**：业务分析、产品定位、场景描述、文档结构、架构设计、数据建模、流程角色、交互设计、商业分析、MVP策略、运营方案、异常处理等
- **逐维度深度输出**：每个维度检查完立即输出详细发现，引用PRD原文，给出具体可执行的改进示例
- **组件级交互分析**：对PRD中每个界面、弹窗、表单逐一做交互设计评估
- **结构化问题清单**：按 P0/P1/P2/P3 优先级输出问题，并附改进建议和方法论依据
- **智能适配**：根据产品类型（自研/商业化、业务型/工具型等）自动调整检查侧重

---

## 方式一：Claude Code Skill（推荐）

适合 Claude Code 用户，安装后用斜杠命令一键调用，体验最好。

### 安装要求

- [Claude Code](https://claude.ai/code) 已安装
- 推荐使用 **Opus 模型**（分析深度明显优于 Sonnet/Haiku）

### 安装方法

**Mac / Linux：**

```bash
git clone https://github.com/pmyangkun/check-prd-skill.git
cd check-prd-skill
bash install.sh
```

**Windows（PowerShell）：**

```powershell
git clone https://github.com/pmyangkun/check-prd-skill.git
cd check-prd-skill
.\install.ps1
```

> 不熟悉 git？直接[下载 ZIP](https://github.com/pmyangkun/check-prd-skill/archive/refs/heads/main.zip)，解压后运行安装脚本即可。

### 使用方法

```
# 1. 切换到 Opus 模型（推荐）
/model claude-opus-4-6

# 2. 执行检查（提供 PRD 文件路径，或粘贴 PRD 内容后调用）
/check-prd 你的PRD文件路径.pdf
```

### 更新方法

```bash
cd check-prd-skill
git pull
bash install.sh   # 或 .\install.ps1（Windows）
```

---

## 方式二：通用 Prompt（ChatGPT / Gemini / 其他 LLM）

不使用 Claude Code 的用户，可以直接使用合并好的单文件 Prompt，适用于任意 LLM。

### 使用步骤

1. 下载 [`check-prd-universal-prompt.md`](./check-prd-universal-prompt.md)，用任意文本编辑器打开
2. 全选复制文件全部内容
3. 打开 ChatGPT / Gemini / 其他 LLM 的对话界面
4. 新建一个对话，**先粘贴 Prompt 内容**，再粘贴 PRD 内容，一起发送

> **提示：** 文件较长（约 150KB），建议使用支持长上下文的模型，如 ChatGPT-4o、Gemini 1.5 Pro、Claude 等。模型上下文窗口越大，分析质量越好。

### 两种方式的对比

| | Claude Code Skill | 通用 Prompt |
|---|---|---|
| 适用平台 | Claude Code | 任意 LLM |
| 安装步骤 | 需要一次性安装 | 无需安装，复制粘贴 |
| 调用方式 | `/check-prd` 一键调用 | 每次手动粘贴 |
| 分析质量 | 最佳（逐维度独立加载） | 良好 |
| 更新方式 | `git pull` | 重新下载文件 |

---

## 文件说明

```
check-prd.md                    # Claude Code 主入口
check-prd-universal-prompt.md   # 通用 Prompt（其他 LLM 使用）
check-prd-01-business.md        # 维度01：业务分析质量
check-prd-02-product-type.md    # 维度02：产品类型适配性
check-prd-03-positioning.md     # 维度03：产品定位合理性
check-prd-04-scenario.md        # 维度04：场景分析与用户旅程
check-prd-05-structure.md       # 维度05：文档结构完整性
check-prd-06-architecture.md    # 维度06：架构设计质量（含企业架构层）
check-prd-07-data.md            # 维度07：数据建模质量
check-prd-08-process.md         # 维度08：流程与角色设计
check-prd-09-ux.md              # 维度09：交互设计质量（含组件级分析）
check-prd-10-commercial.md      # 维度10：商业分析深度
check-prd-11-mvp.md             # 维度11：MVP策略与演进蓝图
check-prd-12-exception.md       # 维度12：异常处理与健壮性设计
check-prd-13-ai.md              # 维度13：AI功能设计质量
check-prd-14-operations.md      # 维度14：运营方案与效果跟踪
check-prd-appendix-veto.md      # 附录：重大风险项清单
check-prd-appendix-guide.md     # 附录：检查报告模板与执行指南
install.sh                      # 安装脚本（Mac/Linux）
install.ps1                     # 安装脚本（Windows）
```

---

## 理论依据

本工具的检查标准基于以下三本书：

- **《决胜B端（第二版）》**：B端产品设计方法论全书，涵盖业务调研、产品定位、架构设计、数据建模、流程设计、项目管理等全流程
- **《决胜体验设计》**：B端用户体验设计方法论，涵盖体验四层模型、交互设计原则、AI功能设计六脉神剑等
- **《决胜B端PRD模板 v2.0》**：标准化PRD文档模板，定义了从项目背景到运营计划的完整文档结构

---

## 关于作者

**杨堃**，《决胜B端》作者，B端产品专家，资深咨询顾问与培训讲师。中国科学院大学MBA特聘企业导师，开设产品经理课程。

担任多家上市公司、SaaS独角兽公司数字化转型顾问、产品顾问，服务客户涵盖华为、京东、宝洁等知名企业。

"36Kr"专栏作家，InfoQ-PCon 出品人，中国产品经理大会、全球产品经理大会、HiPM产品创新力峰会、中国软件技术大会特邀演讲嘉宾。

曾任职百度、慢酷科技等互联网科技公司，在企业数字化转型、应用架构设计、业务中台建设、CRM建设、数据仓库与BI建设领域均有丰富实践经验。

---

## 版本历史

见 [CHANGELOG.md](./CHANGELOG.md)
