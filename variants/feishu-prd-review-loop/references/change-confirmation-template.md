# Change Confirmation Template

Use this template when an issue has been accepted but the PM has not yet confirmed the exact planned edit.

## Goal

- make every planned PRD change visible before execution
- prevent silent or over-eager document edits
- let the PM confirm, reject, or adjust the exact wording before the model touches the PRD
- keep the approval signal machine-readable
- keep the whole discussion inside the original issue thread so the PM can locate it in Feishu GUI

## Default rule

- Append one assistant reply in the original issue thread for every accepted issue before any document edit.
- Do not create a new top-level confirmation card in new rounds.
- Reuse the original issue thread. If the thread belongs to a legacy full-document comment that has already been replaced by a local thread, append the reply on the replacement local thread instead.
- Do not edit the PRD until the PM explicitly replies `确认执行`.
- If the PM replies `修改方案：...`, regenerate a new confirmation reply with the updated plan and wait again.

## Required template

```text
🟦【待确认修改方案】
问题位置：[章节路径 / 锚点原文]
问题摘要：[一句话说明当前问题]
定位说明：[仅在实际锚点 != 真正目标时填写]
拟修改位置：[section_or_anchor]
拟修改方式：[replace_range / replace_all / insert_before / insert_after]
拟修改前：[short before preview]
拟修改后：[exact planned wording or rule]

请产品经理直接在本线程下回复：
- `确认执行`
- `确认执行：补充微调说明`
- `修改方案：给出新的口径或文案`
- `取消执行：填写原因`
```

## Rules

- `问题位置` and `问题摘要` must be understandable in the Feishu GUI without relying on `comment_id`.
- `定位说明` is optional and should only appear when the workflow had to relocate the anchor.
- `拟修改前` 和 `拟修改后` 必须足够具体，让 PM 能在不打开 diff 工具的情况下判断是否正确。
- 如果 planned change 涉及多处相同替换，必须在卡片里说明“会同步替换 N 处”。
- 如果模型无法给出足够明确的 `拟修改后` 文案，就不要改文档；改为继续追问。
- `确认执行：...` 可以附带轻微微调；如果该微调会改变 planned wording，本轮仍应在同线程里重新生成一条确认回复再等一次明确确认。
- `取消执行：...` 不等于自动豁免；默认回到 unresolved，需要后续明确走 `不采纳：原因` 或新的确认方案。
