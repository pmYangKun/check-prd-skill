# Clarification Follow-up Template

Use this template when an issue is still `待澄清` during `Finalize Loop`.

## Goal

- append a clarification reply inside the original issue thread
- tell the user exactly what is still missing
- keep the next-pass parsing stable

## Default rule

- At most one follow-up reply per `comment_id + 轮次Key`
- If the same round re-runs, do not repeat the same follow-up
- If a new `轮次Key` starts and the issue is still unresolved, one new follow-up reply may be added again
- New rounds must append the follow-up in the original issue thread instead of creating a new top-level card
- If the original issue was a legacy full-document comment and the workflow already repaired it into a local replacement thread, append the follow-up on the replacement thread

## Required template

```text
🟨【待澄清追问】
问题位置：[章节路径 / 锚点原文]
问题摘要：[一句话说明当前问题]
定位说明：[仅在实际锚点 != 真正目标时填写]

你当前的回复还不能完成收口。

[用一句话说明缺的是什么，例如：你回复了“不采纳”，但还缺豁免原因]

请直接在本线程下补充：
- `采纳`
- `采纳：补充说明你希望模型如何修改`
- `不采纳：填写豁免原因`
```

## Default reasons

### Missing waiver reason

```text
🟨【待澄清追问】
问题位置：[章节路径 / 锚点原文]
问题摘要：[一句话说明当前问题]
定位说明：[仅在实际锚点 != 真正目标时填写]

你当前回复了“不采纳”，但按本流程，不采纳默认按豁免处理，必须补充豁免原因后才能收口。

请直接在本线程下补充：
- `采纳`
- `采纳：补充说明你希望模型如何修改`
- `不采纳：填写豁免原因`
```

### No user reply yet

```text
🟨【待澄清追问】
问题位置：[章节路径 / 锚点原文]
问题摘要：[一句话说明当前问题]
定位说明：[仅在实际锚点 != 真正目标时填写]

这条评论目前还没有收到有效回复，所以我还不能继续收口或判断是否可交付开发。

请直接在本线程下补充：
- `采纳`
- `采纳：补充说明你希望模型如何修改`
- `不采纳：填写豁免原因`
```

### Contradictory reply

```text
🟨【待澄清追问】
问题位置：[章节路径 / 锚点原文]
问题摘要：[一句话说明当前问题]
定位说明：[仅在实际锚点 != 真正目标时填写]

你当前的回复里同时包含了互相冲突的意思，我还不能确定是按“采纳”执行修改，还是按“不采纳”登记豁免。

请直接在本线程下重新明确：
- `采纳`
- `采纳：补充说明你希望模型如何修改`
- `不采纳：填写豁免原因`
```
