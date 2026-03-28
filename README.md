# check-prd

`check-prd` 是一个标准现代 Claude skill，用于对 B端 PRD、需求文档、SaaS 产品方案和系统设计说明做系统化质量检查。

检查框架基于《决胜B端（第二版）》《决胜体验设计》《决胜B端PRD模板 v2.0》构建，覆盖 14 个维度，并要求逐维度即时输出分析结果。

## 核心能力

- 14 个检查维度，覆盖业务分析、定位、场景、结构、架构、数据、流程、交互、商业分析、MVP、运营、异常与 AI 功能
- 逐维度即时输出，避免把所有问题堆到最后
- 组件级交互分析，逐个检查界面、弹窗、表单和关键操作
- 产品定型机制，会根据产品类型和商业属性动态调整适用维度
- 汇总导航报告，按 P0-P3 整理问题、亮点、重大风险项和 Top 10 改进建议

## 仓库结构

```text
SKILL.md                         # Skill 入口
references/dimensions/           # 14 个维度的 supporting files
references/appendices/           # 风险清单与报告模板
references/universal-prompt-intro.md
scripts/build.py                 # 生成通用 Prompt 和 .skill 包
scripts/validate.py              # 校验结构和生成物
scripts/install_skill.py         # 同步安装到 ~/.claude/skills/check-prd
evals/evals.json                 # 基础任务 eval 种子
evals/trigger-evals.json         # 触发描述 eval 种子
dist/                            # 生成物输出目录
```

## 安装

### Claude Code

Mac / Linux:

```bash
git clone https://github.com/pmyangkun/check-prd-skill.git
cd check-prd-skill
bash install.sh
```

Windows PowerShell:

```powershell
git clone https://github.com/pmyangkun/check-prd-skill.git
cd check-prd-skill
.\install.ps1
```

安装后，skill 会以整个目录的形式出现在 `~/.claude/skills/check-prd`，而不是把一批 `.md` 文件平铺到 `~/.claude/skills/`。

## 使用

显式调用：

```text
/check-prd path/to/prd.pdf
```

自动触发示例：

- “帮我审一下这个 B 端 PRD”
- “请 review 这份 SaaS 产品方案”
- “看看这个需求文档在流程、权限和异常处理上还有什么漏洞”

建议在复杂文档评审时使用更强的模型，例如：

```text
/model claude-opus-4-6
```

## 通用 Prompt 产物

仓库仍然提供给其他 LLM 使用的单文件 Prompt，但它现在是生成物，不再手工维护。

生成后的位置：

- [dist/check-prd-universal-prompt.md](dist/check-prd-universal-prompt.md)

## 构建与校验

生成通用 Prompt 和 `.skill` 包：

```bash
python3 scripts/build.py
```

运行结构校验并验证生成物：

```bash
python3 scripts/validate.py
```

生成物输出：

- `dist/check-prd-universal-prompt.md`
- `dist/check-prd.skill`

## 理论依据

- **《决胜B端（第二版）》**：业务调研、定位、架构设计、数据建模、流程设计、项目管理
- **《决胜体验设计》**：体验设计方法、交互设计原则、AI 功能设计
- **《决胜B端PRD模板 v2.0》**：标准化 PRD 结构和关键章节

## 关于作者

**杨堃**，《决胜B端》作者，B端产品专家，资深咨询顾问与培训讲师。中国科学院大学 MBA 特聘企业导师，服务客户涵盖华为、京东、宝洁等企业。

## 版本历史

见 [CHANGELOG.md](CHANGELOG.md)
