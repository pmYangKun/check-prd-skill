# Issue Log Format

Every run must output an issue log. If nothing went wrong, explicitly output:

```text
问题日志：无
```

## Required columns

| Column | Meaning |
|---|---|
| `stage` | `Scope Setup` / `Review` / `Comment Back` / `User Reply Collection` / `Change Confirmation Gate` / `Finalize Loop` / `Feedback Log` / `Delivery Gate` / `Re-check Gate` |
| `doc_url` | the active Feishu doc or wiki URL |
| `target_section_or_anchor` | prefer GUI-visible section title, anchor text, or issue summary; use raw comment id only as secondary debug context |
| `issue_type` | normalized issue type |
| `detail` | concise description of what failed or fell back |
| `fallback_action` | what the workflow did instead |
| `needs_manual_followup` | `yes` or `no` |

## Recommended issue types

- `anchor_not_unique`
- `anchor_not_found`
- `anchor_relocated`
- `comment_create_failed`
- `legacy_full_comment_replaced`
- `doc_update_multi_match`
- `media_token_parse_failed`
- `whiteboard_destructive_dry_run`
- `missing_scope`
- `permission_denied`
- `auth_not_ready`
- `feedback_base_config_missing`
- `feedback_base_init_failed`
- `feedback_base_schema_migration_failed`
- `feedback_base_binding_invalid`
- `feedback_log_write_failed`
- `feedback_log_update_failed`
- `waiver_lookup_failed`
- `waiver_reason_missing`
- `followup_reply_create_failed`
- `change_confirmation_missing`
- `confirmation_reply_create_failed`
- `delivery_gate_blocked`

## Markdown output format

Use a Markdown table like this:

```md
| stage | doc_url | target_section_or_anchor | issue_type | detail | fallback_action | needs_manual_followup |
|---|---|---|---|---|---|---|
| Comment Back | https://example.feishu.cn/wiki/xxx | 需求描述 > 导入规则 / 锚点“每次导入覆盖之前的数据” | anchor_relocated | exact target text could not be anchored because the rendered block changed | anchored the comment to the next locatable sentence and added 定位说明 | no |
| Change Confirmation Gate | https://example.feishu.cn/wiki/xxx | 需求描述 > 打卡规则 / 锚点“活动点位地址 1 公里内” | change_confirmation_missing | accepted issue has a planned edit but PM has not confirmed the exact change yet | appended a 待确认修改方案 reply in the original thread and paused before editing | yes |
| Finalize Loop | https://example.feishu.cn/wiki/xxx | APP 长促页面调整 / 打卡要求异常状态 | waiver_reason_missing | user selected 不采纳 but left the reason blank | kept issue in 待澄清 and appended a clarification reply in the same thread | yes |
| Delivery Gate | https://example.feishu.cn/wiki/xxx | 本轮交付判断 | delivery_gate_blocked | 2 issues still remain in 待澄清 | stopped before declaring ready for development | yes |
```

## When to show the issue log

- Show it at the end of each run.
- If the workflow contains no issues, say `问题日志：无`.
- If there are issues, show the full table even if the main task still succeeded.
