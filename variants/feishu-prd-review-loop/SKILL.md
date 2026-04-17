---
name: feishu-prd-review-loop
description: Run a complete Feishu/Lark PRD review-to-delivery loop: classify the PRD scope, choose the right review chapters, write anchored comments back into the document, parse comment-thread replies as `采纳` or `不采纳`, require PM confirmation of exact planned edits before any document change, maintain a waiver ledger and scoring-based delivery gate, persist the full feedback snapshot into a dedicated Feishu Base, and then ask whether to run `check-prd` again. Use this whenever the user shares a `feishu.cn` or `lark` PRD link and wants review, comment write-back, comment-driven revision, waiver management, PRD 准入判断, or a repeatable PRD review workflow, even if they only say “帮我评估这个 PRD”, “把建议写回飞书”, “按评论改文档”, or “判断这个 PRD 能不能进开发”.
compatibility: Requires `lark-cli` and Feishu user-authenticated access for user-scoped documents.
metadata:
  requires:
    bins: ["lark-cli"]
---

# Feishu PRD Review Loop

This variant is the Feishu Assistant workflow for `check-prd`, but it intentionally keeps the shipped skill id `feishu-prd-review-loop` for backward compatibility.

This skill orchestrates a nine-stage workflow for Feishu PRDs:

1. `Scope Setup` — classify the requirement and choose the review scope
2. `Review` — read the PRD and evaluate it with `check-prd`
3. `Comment Back` — write one issue per Feishu comment, anchored whenever possible
4. `User Reply Collection` — wait for and read user replies in comment threads
5. `Change Confirmation Gate` — turn accepted issues into exact planned edits and ask PM to confirm them
6. `Finalize Loop` — execute only PM-confirmed edits, register waivers, and keep clearing `待澄清`
7. `Feedback Log` — persist the full reply snapshot into a dedicated Feishu Base
8. `Delivery Gate` — decide whether the PRD is ready to hand off to development
9. `Re-check Gate` — ask whether to run `check-prd` again

This skill is a workflow wrapper. It does **not** replace `check-prd`; it should reuse that skill whenever available.

## Default Stance

- Treat Feishu or Lark document links as CLI-first tasks.
- Default to user-authenticated `lark-cli` access for reading, commenting, and editing user-owned or user-accessible PRDs. Record the auth path as `UAT(user)` in logs when that label is required by downstream artifacts.
- For `/wiki/` links, do **not** use the wiki token as a document token. Resolve `wiki -> get_node -> obj_type/obj_token` first.
- Prefer small, local updates over large rewrites.
- Keep all `待澄清` and `待确认修改方案` interactions inside the original issue thread by appending replies.
- Treat full-document comments as legacy repair-only artifacts, not as the normal fallback path in new rounds.
- Never use `overwrite` for document updates in this workflow.
- Persist the latest reply snapshot before applying final PRD edits.
- Never edit the PRD before the PM has confirmed the exact planned change content.
- Do not auto-run the second review. Always ask first.
- Do not assume every PRD needs all chapters. Determine the L level first, then scope the review to the matching chapter set.
- When reporting remaining work to the user, prefer `章节路径 + 锚点原文 + 问题摘要`; use `comment_id` only as secondary debug context.

## Review Policy

Load the default scope and scoring policy from [review-policy.config.json](review-policy.config.json).

The default scope contract is:

- `L1（配置级）`: `ch10-2 / ch10-3 / ch14` + G1
- `L2（规则级）`: `ch01 / ch02 / ch06 / ch10-1 / ch10-2 / ch10-3 / ch14` + G1；触发补检：`ch03 / ch11 / ch12 / ch13`
- `L3（模块级）`: L2 包 + `ch12 / ch13` + G2；`ch11` 可选；触发补检：`ch03 / ch04 / ch05 / ch07 / ch08-09`
- `L4（系统级）`: 全量 `ch01–ch14` + G1 / G2 / G3

`强制补检` means:

- even when the current pass is `L1` or `L2` or `L3`
- if the PRD clearly hits a high-risk change signal
- the linked chapter must be added automatically
- and the user cannot remove it from the actual check scope

If the evidence is only suggestive rather than explicit, treat it as `建议补检` instead of `强制补检`.

## Stage Detection

Use the user's latest request to decide which stage to enter.

| Stage | Typical user cues |
|---|---|
| `Scope Setup` + `Review` | “评估这个 PRD”, “review 这个文档”, “帮我看看这个飞书 PRD”, “判断能不能进开发” |
| `Comment Back` | “把建议写回飞书”, “直接在文档里评论”, “按问题回写评论” |
| `User Reply Collection` + `Change Confirmation Gate` | “我已经回复完评论了”, “按评论改文档”, “根据批注做最终修改”, “可以开始收口了” |
| `Finalize Loop` | “这些修改我确认了”, “按确认卡执行修改”, “可以正式改正文了” |
| `Feedback Log` | enter automatically before confirmation-reply creation and before final doc edits |
| `Delivery Gate` | enter automatically after the current pass no longer has `待澄清` and no accepted change is still waiting for confirmation |
| `Re-check Gate` | only after `Delivery Gate` finishes |

If the user asks for the full loop in one request, start at `Scope Setup`, continue through `Review` and `Comment Back`, and stop before `Finalize Loop` until the user explicitly confirms they have replied in the comment threads and any accepted changes have been confirmed for execution.

## Workflow Rules

### 1. Scope Setup

- Resolve the document type and token correctly.
- For wiki links, use `lark-cli wiki spaces get_node` to fetch `node.obj_type` and `node.obj_token`.
- If `obj_type` is not `docx` or `doc`, adapt to the actual resource type instead of pretending it is a text document.
- Fetch the text body before classifying scope.
- Determine the complexity level using the L1-L4 decision tree in `prd-quality-framework/complexity-assessment.md §1`.
- Recommend one of:
  - `L1（配置级）`
  - `L2（规则级）`
  - `L3（模块级）`
  - `L4（系统级）`
- Recommend the actual chapter scope using the review-policy config.
- Apply `强制补检` rules whenever explicit evidence exists in the user prompt, PRD text, prototype, fields, or process flow.
- Track for this round:
  - `review_profile`
  - `checked_chapters`
  - `skipped_chapters`
  - `force_check_hits`
  - `suggested_extra_chapters`

### 2. Review

- Reuse `check-prd` for the review itself.
- Review only the selected chapters from `Scope Setup`.
- Before surfacing new findings, compare them against active waivers in the feedback Base when the waiver ledger is available.
- If a finding matches an active waiver:
  - do not emit it as a new finding
  - do not write it back as a new comment
  - record it as `命中既有豁免`
- Normalize every issue candidate with the full review metadata:
  - `severity`
  - `chapter_id`
  - `chapter_name`
  - `scope_origin`
  - `anchor_hint`
  - `problem`
  - `suggestion`
  - `stage`
  - `finding_class`
  - `evidence_basis`
  - `confidence`
- By default, prioritize `P0` and `P1`. Only continue through `P2/P3` if the user asks for a deeper pass.
- Also compute and present:
  - `已检查维度`
  - `未检查维度`
  - `强制补检命中项`
  - `本轮质量分`

### 3. Comment Back

- Follow the exact template in [references/comment-template.md](references/comment-template.md).
- One issue maps to one comment card.
- By default, only `硬缺口` items enter high-priority comment write-back.
- `待确认` and `优化建议` can stay in the review report unless the user explicitly wants broader comment coverage.
- Prefer local comments with `selection-with-ellipsis`.
- Resolve anchors in this order:
  - exact target text
  - the first locatable content after the target in the same section
  - the nearest section title
- If the actual anchor differs from the true target, include `定位说明` in the comment body.
- Do not use a full-document comment as the normal fallback in new rounds.
- If no stable local anchor can be created even after the section-title fallback, stop comment creation for that issue and write the exception into the issue log.
- Comments must include both:
  - a clear problem statement
  - a directly actionable optimization suggestion
- The user feedback area must keep the structured fields so later stages can parse the thread consistently.

### 4. User Reply Collection

- Only enter this stage after the user explicitly says they have reviewed or replied to the suggestions.
- Read comment cards and all replies. If a comment card has more replies than the first page, continue fetching the reply pages.
- Treat the user's latest effective reply in the original issue thread as the source of truth by default.
- For backward compatibility, if an older round already created bound clarification follow-up cards or change-confirmation cards, still read and bind them.
- Do not treat the earlier agent suggestion as final policy.
- A thread is considered `待澄清` when:
  - there is no user reply
  - the reply does not clearly choose `采纳` or `不采纳`
  - the reply chooses `不采纳` but gives no reason
  - the reply is internally contradictory
- The default accepted reply shapes are:
  - `采纳`
  - `采纳：...`
  - `不采纳：...`
- An in-thread clarification reply is identified by the marker:
  - `🟨【待澄清追问】`
- An in-thread change-confirmation reply is identified by the marker:
  - `🟦【待确认修改方案】`
- Legacy top-level clarification / confirmation cards that contain `原问题CommentID：<original_comment_id>` must still be recognized for backward compatibility.

### 5. Change Confirmation Gate

- For every issue whose latest effective decision is `采纳`, first generate the exact planned edit before touching the PRD.
- Build a minimal-diff proposal that is specific enough for PM review:
  - target section or anchor
  - planned change mode
  - short before/after preview
  - exact rule or wording to be written
- Append one assistant confirmation reply in the original issue thread using [references/change-confirmation-template.md](references/change-confirmation-template.md).
- Do not create a new top-level confirmation card in new rounds.
- Do not edit the PRD while any accepted issue is still missing PM execution confirmation.
- The only valid confirmation replies are:
  - `确认执行`
  - `确认执行：...`
  - `修改方案：...`
  - `取消执行：...`
- If the PM replies `修改方案：...`, regenerate a new exact proposal in the same thread and wait for another explicit `确认执行`.
- If the PM replies `取消执行：...`, do not edit the PRD for that issue; treat it as a PM override and keep the issue unresolved until the workflow either receives a waiver-style reason or a new confirmed proposal.

### 6. Finalize Loop

- Parse the user's latest effective reply into one of:
  - `采纳`
  - `不采纳`
  - system-derived `待澄清`
- Build an action matrix for each issue:
  - `comment_id`
  - `decision`
  - `model_assist_instruction`
  - `waiver_reason`
  - `final_policy`
  - `target_type`
  - `issue_status`
  - `processing_result`
  - `finding_class`
  - `evidence_basis`
  - `confidence`
- For `采纳`:
  - `模型协助说明` is optional
  - if omitted, derive a minimal-diff planned edit from the original suggestion
  - do not edit immediately; wait until the PM explicitly replies `确认执行` in the same issue thread
- For `不采纳`:
  - `豁免原因` is required
  - if the reason is missing, keep the issue in `待澄清`
  - if the reason is present, register the waiver and do not modify the PRD for that issue
- The only issue statuses are:
  - `已处理`
  - `待澄清`
- `Finalize Loop` does **not** end until:
  - every issue has a user reply
  - every accepted issue has an explicit PM execution confirmation
  - every issue status is `已处理`
- If any issue remains `待澄清`:
  - append one structured clarification follow-up reply in the original issue thread for the current `轮次Key`
  - if the original issue is a legacy full-document comment and still needs user follow-up, first create a nearby local replacement thread, mark the old full-document comment solved, then continue future replies in the replacement thread
  - summarize the unresolved issues
  - ask the user to reply in the original issue thread before continuing

### 7. Feedback Log

- Before editing the PRD, persist the full feedback snapshot into the dedicated Feishu Base described in [references/feedback-log.md](references/feedback-log.md).
- Use the binding config at [feedback-log.config.json](feedback-log.config.json).
- Use the policy config at [review-policy.config.json](review-policy.config.json) for scope and scoring metadata.
- If the feedback config is missing or intentionally uninitialized, create the feedback Base and bind it.
- If the config is bound to schema `2.1` or earlier, or the reply-tracking / waiver fields are missing, migrate the existing Base in place.
- If the config is already bound but invalid, inaccessible, or schema-incompatible beyond safe migration, stop and log `feedback_base_binding_invalid`.
- Write:
  - one run summary row into `评审轮次`
  - one detail row per comment into `建议反馈明细`
  - one waiver row per active waiver into `豁免台账`
- Only after feedback logging succeeds may the workflow continue to append confirmation / clarification replies or edit the PRD.
- After the PRD edits finish, update the matching detail rows with `正文处理结果` and the final `问题状态`.

### 8. Delivery Gate

- The PRD is `可交付开发` only when both are true:
  - all issues have received a user reply
  - all accepted changes have been explicitly confirmed by PM and then executed
  - all issues currently have `问题状态 = 已处理`
- Score supports visibility and triage, but does **not** override the gate.
- If the score is high but there is still any `待澄清`, the PRD is **not** ready for development.
- When reporting the gate, always include:
  - `review_profile`
  - `checked_chapters`
  - `force_check_hits`
  - `quality_score`
  - `delivery_ready`
  - `risk_balance_summary`

### 9. Re-check Gate

- After all agreed edits are done and `Delivery Gate` has been evaluated, ask the user whether to run `check-prd` again.
- Do not automatically start another review pass.

## Scoring Rules

Use the mapping from [review-policy.config.json](review-policy.config.json):

- `优秀 = 100`
- `合格 = 80`
- `待改进 = 60`
- `严重缺失 = 30`

The score should be computed only over the chapters actually checked in the current round.

## Non-Negotiable Editing Rules

- Use minimal-diff document edits.
- Prefer `replace_range`, then `insert_before` or `insert_after`.
- Never use `overwrite`.
- Never edit the PRD before the latest feedback snapshot has been persisted successfully.
- Never edit the PRD before a visible in-thread `🟦【待确认修改方案】` reply exists and the PM has explicitly replied `确认执行`.
- Do not guess unresolved business policy if the user reply is ambiguous.
- If the user has not replied in a thread yet, remind them and stop instead of silently editing.
- Keep a structured issue log for all important failures, fallbacks, migrations, and manual follow-ups.

## Media Rules

- Images and file attachments can still receive review comments and optimization suggestions.
- Do not treat image or attachment blocks as forbidden zones.
- Existing whiteboards can be edited, but only through the whiteboard workflow described in [references/media-handling.md](references/media-handling.md).
- If a whiteboard dry run shows destructive overwrite behavior, stop and get explicit user confirmation before continuing.

## Issue Log

Always produce an issue log for the run. If there are no issues, explicitly say `问题日志：无`.

Use the schema in [references/issue-log-format.md](references/issue-log-format.md).

You must log at least these cases:

- anchor not unique
- anchor not found and the workflow had to relocate to a later anchor or section title
- comment creation failed
- legacy full-document comment replaced by a local thread
- document update matched multiple ranges unexpectedly
- media token parsing failed
- whiteboard dry run shows existing nodes would be deleted
- missing scope, permission, or authentication
- feedback Base config missing or uninitialized
- feedback Base initialization failed
- feedback Base schema migration failed
- feedback Base binding invalid
- feedback log write failed
- feedback log update failed
- waiver lookup failed
- waiver_reason_missing
- followup_reply_create_failed
- change_confirmation_missing
- confirmation_reply_create_failed
- delivery gate blocked by unresolved issues

## References

- [review-policy.config.json](review-policy.config.json) — default scope packages, force-check rules, and scoring policy
- [references/stage-protocol.md](references/stage-protocol.md) — the command-level workflow and phase contract
- [references/comment-template.md](references/comment-template.md) — the exact initial comment body format
- [references/change-confirmation-template.md](references/change-confirmation-template.md) — the exact in-thread PM confirmation reply format used before any PRD edit
- [references/clarification-followup-template.md](references/clarification-followup-template.md) — the structured in-thread follow-up reply format for `待澄清`
- [references/feedback-log.md](references/feedback-log.md) — the feedback Base schema, migration rules, and logging protocol
- [references/media-handling.md](references/media-handling.md) — rules for text, images, files, and whiteboards
- [references/issue-log-format.md](references/issue-log-format.md) — the issue log schema and examples
