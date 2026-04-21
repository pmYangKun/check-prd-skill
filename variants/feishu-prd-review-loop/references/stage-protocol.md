# Stage Protocol

This file defines the decision-complete execution contract for each stage of the workflow.

## Stage 0: `Scope Setup`

### Goal

Classify the PRD as `小需求 / 中需求 / 大需求`, choose the actual review dimensions, and apply `强制补检`.

### Input

- Feishu or Lark PRD URL, usually `/wiki/` or `/docx/`
- User request to review, comment, revise, or decide whether the PRD can enter development

### Required flow

1. Confirm this is a Feishu document task.
2. Default to user-authenticated `lark-cli` access. Record the auth path as `UAT(user)` when a run log or Base row needs that fixed label.
3. Resolve the document:
   - `/wiki/` -> `lark-cli wiki spaces get_node --params '{"token":"..."}'`
   - extract `node.obj_type` and `node.obj_token`
4. Read the body:
   - prefer `lark-cli docs +fetch --as user --doc "<url-or-token>"`
5. Load `../review-policy.config.json`.
6. Recommend `review_profile`:
   - `小需求`
   - `中需求`
   - `大需求`
7. Apply the default dimension package.
8. Add `强制补检` dimensions when explicit evidence exists.
9. Produce the scope contract:

| Field | Meaning |
|---|---|
| `review_profile` | `小需求 / 中需求 / 大需求` |
| `checked_dimensions` | dimensions that will be reviewed now |
| `skipped_dimensions` | dimensions intentionally not reviewed now |
| `force_check_hits` | dimensions auto-added because of explicit high-risk signals |
| `suggested_extra_dimensions` | optional extra dimensions when evidence is suggestive but not decisive |

### Output

- a review scope that is explicit enough to drive `check-prd`
- issue-log entries if auth, resolution, or scope detection fails

## Stage 1: `Review`

### Goal

Read the PRD correctly, then produce structured review findings through `check-prd`.

### Required flow

1. Reuse the `Scope Setup` result.
2. If the document includes a file attachment prototype or other relevant artifact, fetch it when it materially affects the review.
3. Reuse `check-prd` for the review itself.
4. Limit the pass to the dimensions from `checked_dimensions`.
5. If the waiver ledger is available:
   - load active waivers
   - compare new findings against `风险指纹`
   - suppress matched waived findings from comment write-back
6. Normalize the review output into a list of issue candidates with these fields:

| Field | Meaning |
|---|---|
| `severity` | `P0` / `P1` / `P2` / `P3` |
| `dimension_id` | review dimension code |
| `dimension_name` | review dimension name |
| `scope_origin` | `default_bundle` / `force_check` / `manual_add` |
| `anchor_hint` | the exact or near-exact text span to comment on |
| `problem` | what is wrong or missing |
| `suggestion` | a directly actionable optimization |
| `stage` | `Review` |
| `finding_class` | `硬缺口` / `待确认` / `优化建议` |
| `evidence_basis` | `正文` / `正文+原型` / `原型附件` / `评论线程` / `推断` |
| `confidence` | `high` / `medium` / `low` |
| `waiver_hit` | `yes` / `no` |

### Output

- structured findings for the user
- issue candidates ready for comment back
- review metadata for scoring and delivery readiness
- issue-log entries if resolution, fetch, scope, or waiver lookup steps fail

## Stage 2: `Comment Back`

### Goal

Write review findings back to the Feishu PRD as anchored comments whenever possible.

### Required flow

1. Take the normalized issue list from `Review`.
2. Skip issue candidates with `waiver_hit = yes`.
3. For each remaining issue:
   - try local comment first with `lark-cli drive +add-comment --selection-with-ellipsis ...`
   - resolve the anchor in this order:
     - exact target text
     - the first locatable content after the target in the same section
     - the nearest section title
   - use the body template from `comment-template.md`
   - if the workflow had to relocate the anchor away from the true target text, add `定位说明`
4. By default, only comment back items whose `finding_class = 硬缺口` and whose severity is within the user-requested depth.
5. `待确认` and `优化建议` stay in the review summary unless the user explicitly wants broader comment coverage.
6. If the exact target cannot be anchored:
   - relocate to the next locatable content or nearest section title
   - create an issue-log row
7. If no stable local anchor can be created even after the section-title fallback:
   - do not create a full-document comment in new rounds
   - log the failure
8. If comment creation fails:
   - log it
   - report it in the run summary

### Comment mode rules

| Situation | Required behavior |
|---|---|
| Exact or unique anchor exists | local comment |
| Exact target unavailable but later text exists in same section | relocate to the first locatable later text + `定位说明` + log |
| Later text also unavailable but section title exists | relocate to the nearest section title + `定位说明` + log |
| Anchor not unique | choose the first stable relocated anchor in the same section; if none exists, stop and log |
| Anchor not found | choose the relocated anchor; if none exists, stop and log |
| Media block nearby | comment on the nearest text, later locatable content, or nearest section title; do not use a full comment as the normal fallback |
| Waiver hit | do not comment again; log only if lookup behavior was degraded |

### Default depth

- By default, comment back `P0` and `P1`.
- Only continue through `P2/P3` if the user asks for a broader pass.

## Stage 3: `User Reply Collection`

### Goal

Treat comment replies as the source of truth before editing the PRD, with the original issue thread as the primary interaction surface.

### Required flow

1. List comment cards:
   - `lark-cli drive file.comments list --params '{"file_token":"...","file_type":"docx"}'`
2. For every comment card:
   - treat the first reply as the original comment body
   - if the card has more replies than returned, continue with `drive file.comment.replys list`
   - classify assistant replies inside the same thread whose body starts with `🟨【待澄清追问】` or `🟦【待确认修改方案】` as control replies, not user decisions
   - for backward compatibility, if a top-level card body starts with `🟨【待澄清追问】` or `🟦【待确认修改方案】` and contains `原问题CommentID：...`, classify it as a legacy clarification / confirmation card and bind it back to the original issue thread
3. Read the latest effective user reply in the original issue thread first.
4. If a legacy bound clarification card has a newer valid user reply than the original thread, use it only as backward-compatible input.
5. Read confirmation-state replies from:
   - the latest in-thread assistant reply whose body starts with `🟦【待确认修改方案】`
   - plus any legacy bound confirmation card, if one exists from older rounds
6. Use the latest valid user confirmation reply only for execution-confirmation state, not to overwrite the original `采纳 / 不采纳` decision itself.
7. Parse the latest effective reply into:
   - `采纳`
   - `不采纳`
   - system-derived `待澄清`
7. Do not edit the PRD yet.
8. Pass the full action matrix into `Feedback Log`.

### Important reply-reading rules

- The user reply is the source of truth.
- Do not rewrite the document based only on the original agent suggestion.
- If the user says they disagree or want a different policy, follow the user.
- If there is no user reply, do not edit. Ask the user to reply in the comment card first.
- Accept the following simple reply shapes by default:
  - `采纳`
  - `采纳：...`
  - `不采纳：...`
- A bare `不采纳` without a reason is still `待澄清`.
- For new rounds, the user should reply in the original issue thread rather than in a separate top-level card.
- If a bound clarification follow-up card has a newer valid user reply than the original issue card, prefer it only for legacy compatibility.
- If a bound change-confirmation card has a newer valid PM reply than the original issue card, use it only for execution-confirmation state, not to overwrite the original `采纳 / 不采纳` decision itself.

## Stage 4: `Change Confirmation Gate`

### Goal

Turn every accepted issue into an exact proposed edit and require explicit PM confirmation before any document change.

### Required flow

1. For each issue whose latest effective decision is `采纳`:
   - derive a minimal-diff proposal
   - record `拟修改位置`
   - record `拟修改方式`
   - record `拟修改前`
   - record `拟修改后`
2. Append one assistant confirmation reply in the original issue thread using `change-confirmation-template.md`.
3. If the active thread belongs to a legacy full-document comment that has already been replaced by a local thread, append the reply to the replacement local thread.
4. Persist the proposal summary and confirmation-reply metadata through `Feedback Log`.
5. Do not edit the PRD yet.
6. Wait for the PM to reply in the same thread with one of:
   - `确认执行`
   - `确认执行：...`
   - `修改方案：...`
   - `取消执行：...`
7. If the PM replies `修改方案：...`:
   - update the proposal
   - append a new confirmation reply version in the same thread
   - wait again for `确认执行`
8. If the PM replies `取消执行：...`:
   - do not edit the PRD
   - keep the issue unresolved until the workflow receives either a waiver-style reason or a newly confirmed proposal

## Stage 5: `Finalize Loop`

### Goal

Execute accepted edits, register waivers, and keep clearing unresolved issues until no issue is left in `待澄清`.

### Required flow

1. Build an action matrix with:

| Field | Meaning |
|---|---|
| `comment_id` | source comment |
| `decision` | `采纳` / `不采纳` / `待澄清` |
| `model_assist_instruction` | optional instruction when user chose `采纳` |
| `waiver_reason` | required when user chose `不采纳` |
| `final_policy` | the user's final wording or rule |
| `target_type` | `doc_text` / `image_or_file_context` / `whiteboard` |
| `planned_change_location` | target section or anchor for the proposed edit |
| `planned_change_before` | short before preview |
| `planned_change_after` | exact proposed wording or rule |
| `execution_confirmation_status` | `待确认` / `已确认` / `已取消` / `不涉及正文` |
| `active_thread_comment_id` | comment id of the thread users should reply in |
| `confirmation_prompt_reply_id` | assistant reply id that contains the confirmation prompt |
| `legacy_confirmation_comment_id` | legacy top-level confirmation-card id when applicable |
| `issue_status` | `已处理` / `待澄清` |
| `processing_result` | `已写回正文` / `豁免登记` / `待确认修改` / `待澄清` |
| `clarification_reason` | `未回复` / `缺少豁免原因` / `回复格式不清` / `回复矛盾` / `待执行确认` / `执行失败` |
| `finding_class` | copied from the original issue candidate when available |
| `evidence_basis` | copied from the original issue candidate when available |
| `confidence` | copied from the original issue candidate when available |

2. Persist the snapshot through `Feedback Log` before editing.
3. Then execute:
   - `采纳 + 已确认` -> edit the PRD with a minimal diff; if `model_assist_instruction` is blank, use the original suggestion
   - `采纳 + 待确认` -> do not edit; keep the issue in `待澄清(待执行确认)`
   - `不采纳` -> do not change the PRD for that issue; register or update a waiver
   - `待澄清` -> do not edit; add the issue to the clarification follow-up list
4. Update `issue_status`:
   - successful `采纳 + 已确认` edit -> `已处理`
   - successful waiver registration -> `已处理`
   - missing reply, missing waiver reason, contradictory reply, missing execution confirmation, or failed edit -> `待澄清`
5. For user-resolvable `待澄清` items:
   - append one structured clarification follow-up reply in the active thread
   - use the body template from `clarification-followup-template.md`
   - do this at most once per `comment_id + 轮次Key`
   - if the only available thread is a legacy full-document comment, first create a nearby local replacement thread, record it as the active thread, mark the legacy full-document comment solved, and then append future clarification / confirmation replies there
6. If any item is still `待澄清`, summarize the remaining issues and stop for user follow-up.
7. Only continue to `Delivery Gate` when no `待澄清` item remains.

## Stage 6: `Feedback Log`

### Goal

Persist the full reply snapshot and waiver state into a dedicated Feishu Base before editing the PRD.

### Required flow

1. Load [feedback-log.config.json](../feedback-log.config.json).
2. Resolve its state:
   - config missing -> treat as `uninitialized`
   - config present but binding fields blank -> treat as `uninitialized`
   - config present, bound to schema `2.1` or earlier, or missing the waiver table / reply-tracking fields -> treat as `migration-required`
   - config present and bound -> validate the Base and all required tables
3. For `uninitialized`:
   - create Base `PRD评审反馈库`
   - create table `评审轮次`
   - create table `建议反馈明细`
   - create table `豁免台账`
   - write binding details back into the config
4. For `migration-required`:
   - reuse the bound Base
   - create the missing table and fields in place
   - update the config to schema `2.2`
5. For `bound-valid`:
   - reuse directly
6. For `bound-invalid`:
   - stop immediately
   - log `feedback_base_binding_invalid`
7. Compute the keys:
   - `轮次Key = sha1(doc_token + sorted(comment_id:latest_user_reply_id_or_none))`
   - `建议Key = 轮次Key + "::" + comment_id`
   - `豁免Key = sha1(risk_fingerprint + effective_scope)`
8. Upsert:
   - one run-summary row into `评审轮次`
   - one detail row per comment into `建议反馈明细`
   - one waiver row per active waiver into `豁免台账`
9. Only after all feedback rows are written successfully may the workflow edit the PRD.
10. After PRD edits finish, update the affected detail rows with `正文处理结果` and `问题状态`.

### Required write content

The run row must include:

- PRD title, URL, tokens, auth path, and document type
- run key and timestamps
- `review_profile`
- checked / skipped / forced dimensions
- quality score
- counts for `采纳 / 不采纳 / 待澄清`
- counts for `已处理 / 待澄清`
- delivery-gate result
- issue-log summary
- a high-level retrospective summary

Each detail row must include:

- comment id and quote
- active thread comment id when legacy full comments have been replaced
- dimension id and risk fingerprint
- severity, finding class, evidence basis
- original problem and suggestion
- user decision, reply raw text, model assist instruction, waiver reason, final policy
- normalized thread snapshot
- clarification reason and follow-up metadata when unresolved
- confirmation-prompt reply id and clarification reply id for new rounds
- legacy top-level confirmation / follow-up comment ids when present from older rounds
- issue status and write-back result
- waiver-hit status

Each waiver row must include:

- waiver key and risk fingerprint
- dimension id
- normalized problem
- effective scope
- waiver reason
- first round / latest round
- hit count
- current status
- follow-up retrospective state

### Failure behavior

- If Base initialization fails: stop and log `feedback_base_init_failed`
- If schema migration fails: stop and log `feedback_base_schema_migration_failed`
- If feedback write fails: stop and log `feedback_log_write_failed`
- If PRD edits later succeed but Base update-back fails: log `feedback_log_update_failed` and report it

## Stage 7: `Delivery Gate`

### Goal

Decide whether the PRD can be handed off to development.

### Required flow

1. Confirm:
   - every issue has a user reply
   - every issue now has `问题状态 = 已处理`
2. Report:
   - `review_profile`
   - `checked_dimensions`
   - `force_check_hits`
   - `quality_score`
   - `delivery_ready`
   - `risk_balance_summary`
3. If any issue remains unresolved:
   - set `delivery_ready = no`
   - log `delivery_gate_blocked`

## Stage 8: `Re-check Gate`

### Goal

Offer the next review pass without running it automatically.

### Required flow

1. Summarize what changed:
   - affected sections
   - solved issues
   - waived issues
   - unresolved items
   - any whiteboards touched
   - feedback-log status
   - delivery-gate result
2. Ask whether to run `check-prd` again.

## Mandatory issue-log events

Log these events with the schema in `issue-log-format.md`:

- `anchor_not_unique`
- `anchor_not_found`
- `comment_create_failed`
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
- `delivery_gate_blocked`
