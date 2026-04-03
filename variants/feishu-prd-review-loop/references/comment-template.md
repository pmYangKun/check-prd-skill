# Comment Template

Use this template for every issue comment written back into the Feishu PRD.

## Why this format exists

The Feishu comment API does not support true color styling in comment text. To keep the content visually obvious and machine-readable, use structured markers instead of real colored text.

The v2 workflow also simplifies user replies. The user should only need to choose `采纳` or `不采纳`, and later stages should be able to parse that without guessing.

## Required template

```text
🔴【问题定位】
[一句话指出当前问题和风险]

🟦【建议修改】
[给出可直接执行的优化写法、规则补充、口径收敛方案，尽量具体]

⚠️【定位说明】（仅在实际锚点 != 真正目标时填写）
当前评论实际锚定在：[实际锚点文本或章节标题]
真正针对内容：[原目标内容]

🟨【用户反馈区】
请直接在本评论下回复：
- `采纳`
- `采纳：补充说明你希望模型如何修改`
- `不采纳：填写豁免原因`
```

## Rules

- One issue maps to one comment card.
- `【问题定位】` must describe the actual problem, not a vague opinion.
- `【建议修改】` must contain an actionable suggestion, not only “建议补充说明”.
- Only include `⚠️【定位说明】` when the workflow had to relocate the anchor away from the true target text.
- Do not use full-document comments as the normal fallback path. If the original target cannot be anchored, relocate to the next locatable content or nearest section title and explain the real target in `定位说明`.
- `【用户反馈区】` must always stay in the comment body so later agents can look for the same fields.
- Do not remove the reply prompt even if the suggestion feels obvious.
- Do not ask the user to choose `部分采纳` or `待澄清` manually. Those are no longer user-facing options in this workflow.
- `采纳` without extra text means the model should derive a minimal-diff proposal, but it still must wait for a later PM confirmation reply in the same thread before editing the PRD.
- `不采纳` means the issue will be treated as a waiver candidate, so the user must give a waiver reason.

## Good patterns

### Good

```text
🔴【问题定位】
这里写了“按周维度更新”，但模板和校验规则都没有“统计周”字段，研发无法确定落库主键。

🟦【建议修改】
建议补一条明确规则：导入模板新增“统计周”字段，主键按“产品组 + 组织 + 合伙人 + 统计周”定义；同时说明历史周数据是否保留。

🟨【用户反馈区】
请直接在本评论下回复：
- `采纳`
- `采纳：补充说明你希望模型如何修改`
- `不采纳：填写豁免原因`
```

### Bad

```text
这里不太清楚，建议优化一下。
```

That is too vague, not anchored to a real implementation risk, and leaves no structured feedback area.
