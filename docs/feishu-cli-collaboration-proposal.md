# `check-prd` Feishu CLI 协作版整合说明

这份说明基于 `variants/feishu-prd-review-loop/` 中的参考实现整理，目标不是替换当前主 skill，而是给作者一个更适合独立分发的协作版方案。

## 建议结论

- 保持 `main` 分支继续作为通用的 `check-prd` 评审 skill
- 将飞书协作工作流单独打包成独立分支
- 建议分支名：`check-prd-skill飞书CLI协作版`

这样做的原因很直接：

- 当前主 skill 的定位非常清晰：读 PRD、按 14 个维度给出严格评审
- 飞书协作版增加了 `lark-cli`、UAT(user)、评论线程、反馈 Base、交付闸门等运行时依赖
- 两者的使用门槛、部署方式、权限要求都明显不同，混在同一个默认安装包里，容易让普通用户误以为必须配置 Feishu 才能用 `check-prd`

## 这个协作版实际补了什么

协作版不是另一套 PRD 评审方法，而是把现有 `check-prd` 包进一个 Feishu/Lark 文档协同闭环：

- `Scope Setup`：先判断小需求 / 中需求 / 大需求，并按规则决定本轮检查维度
- `Review`：复用 `check-prd` 做实际评审
- `Comment Back`：把高优问题按划词评论写回飞书文档
- `User Reply Collection`：读取评论线程中的 `采纳 / 不采纳`
- `Change Confirmation Gate`：先让 PM 确认精确改法，再允许模型改正文
- `Finalize Loop`：只执行已确认的最小 diff，并把不采纳项登记为豁免
- `Feedback Log`：把整轮反馈写入 Feishu Base，沉淀问题、回复、豁免与执行状态
- `Delivery Gate`：判断当前 PRD 是否真的可以交付开发
- `Re-check Gate`：收口后再询问是否重新跑一轮 `check-prd`

## 为什么更适合作为独立分支

从维护角度看，协作版与主 skill 的边界很明显：

- 主 skill 是“评审引擎”
- 协作版是“飞书内工作流编排器”

如果直接并到主入口，后续 README、安装脚本、兼容性说明、出错排查都会复杂很多。独立分支反而更利于分别演进：

- `main` 保持通用、轻依赖、适合所有 Claude skill 用户
- `check-prd-skill飞书CLI协作版` 面向已经在飞书里做 PRD 评审协作的团队

## 建议作者保留的公开内容

在公开仓库里，建议保留这些文件：

- `SKILL.md`
- `references/`
- `review-policy.config.json`
- `evals/evals.json`
- `scripts/online_integration_test.py`
- 一份模板化的 `feedback-log.config.json`

## 建议作者发布前先处理的内容

以下内容建议在独立分支里保持“模板态”，不要带真实绑定：

- `feedback-log.config.json` 中的 `base_token`、`runs_table_id`、`suggestions_table_id`、`waivers_table_id`
- 集成测试脚本里的真实测试文档 URL
- 任何租户内专用 token、表 id、测试记录或用户身份信息

也就是：

- 配置文件可以保留字段结构，但值应为空
- 测试脚本可以保留逻辑，但默认文档 URL 应改成占位示例，并要求使用者显式传参

## 推荐的对外表述

可以把这个变体描述为：

> `check-prd` 的飞书 CLI 协作版。它复用原有 14 维 PRD 评审能力，但进一步支持飞书文档评论回写、线程化反馈收集、PM 确认后最小 diff 改正文、Feishu Base 反馈台账和交付闸门判断。

## 参考实现位置

- 变体目录：[variants/feishu-prd-review-loop/](../variants/feishu-prd-review-loop/)

如果作者认可这个方向，最自然的下一步就是把这个目录单独整理为 `check-prd-skill飞书CLI协作版` 分支，再决定是否额外生成独立 `.skill` 包。
