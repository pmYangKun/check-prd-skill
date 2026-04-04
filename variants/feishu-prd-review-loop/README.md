# feishu-prd-review-loop（飞书 CLI 协作版）

> 本变体由 [@Scofy0123](https://github.com/Scofy0123) 基于标准版 `check-prd`（[main 分支](https://github.com/pmYangKun/check-prd-skill/tree/main)）扩展而来。感谢 Scofy0123 的贡献！

`feishu-prd-review-loop` 是一个建立在 `check-prd` 之上的 Feishu/Lark 协作型变体。

它不替代根目录的 `check-prd`，而是把 `check-prd` 的 PRD 评审能力包进飞书文档协作闭环里，补上这些流程能力：

- 飞书 PRD 范围判断与维度裁剪
- 按划词评论把问题写回文档
- 读取评论线程中的 `采纳 / 不采纳`
- 在改正文前追加 `待确认修改方案`
- 仅对已确认项执行最小 diff 写回
- 将反馈、豁免和执行状态沉淀到 Feishu Base
- 用 `Delivery Gate` 判断是否可交付开发

## 适用前提

- 已有可用的 `check-prd`
- 已安装 `lark-cli`
- 具备 Feishu `UAT(user)` 文档访问能力
- 愿意为评论、正文修改和反馈库写入配置相应 scopes

## 维护建议

- 推荐作为独立分支维护，而不是并进主 skill 的默认安装流
- 建议分支名：`check-prd-skill飞书CLI协作版`
- 原因见 [../../docs/feishu-cli-collaboration-proposal.md](../../docs/feishu-cli-collaboration-proposal.md)

## 脱敏说明

这个目录中的 `feedback-log.config.json` 已改为模板值，发布时不应携带真实 Base 绑定。

`scripts/online_integration_test.py` 也已改成占位文档 URL；执行真实联调时请显式传入 `--doc-url`。
