# check-prd — B端 PRD 质量检查

一套系统化的 B端 PRD / 需求文档 / SaaS 产品方案质量检查框架，覆盖 14 个维度。

基于《决胜B端（第二版）》《决胜体验设计》《决胜B端PRD模板 v2.0》构建。

## 快速开始（任意大模型均可使用）

**不需要安装任何工具。** 只需一个文件，适用于 ChatGPT、Gemini、DeepSeek、Kimi、通义千问等任意大模型：

1. 下载 [`dist/check-prd-universal-prompt.md`](dist/check-prd-universal-prompt.md)
2. 打开你常用的大模型对话界面
3. 先上传或粘贴你的 PRD / 需求文档
4. 再把 `check-prd-universal-prompt.md` 的内容粘贴进去，发送即可

模型会自动完成产品定型，逐维度输出检查分析，最后给出汇总报告。

> 建议使用能力较强的模型（如 GPT-4o、Gemini Pro、DeepSeek-R1 等）以获得更好的检查效果。

## 核心能力

- 14 个检查维度，覆盖业务分析、定位、场景、结构、架构、数据、流程、交互、商业分析、MVP、运营、异常与 AI 功能
- 逐维度即时输出，避免把所有问题堆到最后
- 组件级交互分析，逐个检查界面、弹窗、表单和关键操作
- 产品定型机制，根据产品类型和商业属性动态调整适用维度
- 汇总导航报告，按 P0-P3 整理问题、亮点、重大风险项和 Top 10 改进建议

---

## Claude Code 用户

如果你使用 Claude Code，可以将本仓库安装为 skill，获得更好的集成体验。

### 安装

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

安装后，skill 会以整个目录的形式出现在 `~/.claude/skills/check-prd`。

### 使用

显式调用：

```text
/check-prd path/to/prd.pdf
```

自动触发示例：

- “帮我审一下这个 B 端 PRD”
- “请 review 这份 SaaS 产品方案”
- “看看这个需求文档在流程、权限和异常处理上还有什么漏洞”

---

## 仓库结构

```text
dist/check-prd-universal-prompt.md   # 通用 Prompt（直接拿去用）
SKILL.md                             # Claude Code skill 入口
references/dimensions/               # 14 个维度的源文件
references/appendices/               # 风险清单与报告模板
scripts/build.py                     # 重新生成通用 Prompt 和 .skill 包
scripts/validate.py                  # 校验结构和生成物
scripts/install_skill.py             # 安装到 ~/.claude/skills/check-prd
evals/                               # eval 种子
```

## 构建与校验

如果修改了维度源文件，需要重新生成通用 Prompt：

```bash
python3 scripts/build.py     # 生成 dist/check-prd-universal-prompt.md 和 dist/check-prd.skill
python3 scripts/validate.py  # 校验结构
```

## 理论依据

- **《决胜B端（第二版）》**：业务调研、定位、架构设计、数据建模、流程设计、项目管理
- **《决胜体验设计》**：体验设计方法、交互设计原则、AI 功能设计
- **《决胜B端PRD模板 v2.0》**：标准化 PRD 结构和关键章节

## 关于作者

**杨堃**，《决胜B端》作者，B端产品专家，资深咨询顾问与培训讲师。中国科学院大学 MBA 特聘企业导师，服务客户涵盖华为、京东、宝洁等企业。

## 版本历史

见 [CHANGELOG.md](CHANGELOG.md)
