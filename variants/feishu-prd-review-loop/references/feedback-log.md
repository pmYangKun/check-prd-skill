# Feedback Log Protocol

This file defines how `feishu-prd-review-loop` persists PRD review feedback into a dedicated Feishu Base.

## Goal

Persist every feedback round as analyzable structured data so future review calibration is based on accumulated evidence instead of one-off memory.

The current goal is broader than simple reply logging:

- persist the review scope for the current round
- persist the user's final decision for each issue
- persist whether the issue is already processed or still pending
- persist active waivers so repeated checks can suppress duplicate findings
- persist PM execution-confirmation state for every accepted edit
- support later product / engineering retrospective on waived risks

## Binding Config

Use the project config file:

`../feedback-log.config.json`

Required keys:

| Key | Meaning |
|---|---|
| `base_name` | fixed Base display name |
| `base_token` | bound Base token |
| `runs_table_name` | fixed name for the run-summary table |
| `runs_table_id` | bound table id for `评审轮次` |
| `suggestions_table_name` | fixed name for the detail table |
| `suggestions_table_id` | bound table id for `建议反馈明细` |
| `waivers_table_name` | fixed name for the waiver ledger table |
| `waivers_table_id` | bound table id for `豁免台账` |
| `time_zone` | fixed time zone |
| `schema_version` | schema contract version |

## Config States

Treat the config in one of these states:

| State | Detection | Required behavior |
|---|---|---|
| `uninitialized` | config file missing, `base_token` is blank, or both run/detail table bindings are blank | create the Base and all required tables, then write the binding |
| `migration-required` | config exists and the Base is accessible, but `schema_version < 2.2`, the waiver table binding is blank, the waiver table is missing, or required reply-tracking fields are missing | migrate the bound Base in place, then update the config |
| `bound-valid` | config exists and Base + all required tables are accessible with the confirmation-enabled schema | reuse directly |
| `bound-invalid` | config exists and binding fields are non-empty, but Base or tables are inaccessible / missing / schema-broken beyond safe migration | stop and log `feedback_base_binding_invalid` |

Never silently create a second feedback Base once the config is bound.

## Runtime Order

The `Feedback Log` stage is a hard gate inside `Finalize Loop`.

Required order:

1. Read comment cards and full reply threads
2. Build the action matrix
3. Ensure the feedback Base binding is ready and migrated
4. Write one `评审轮次` row
5. Write or update all `建议反馈明细` rows
6. Write or update all active `豁免台账` rows
7. Only after steps 4-6 succeed, continue to append confirmation / clarification replies, edit the PRD, or edit the whiteboard
8. After edits complete, update the relevant detail rows with `正文处理结果` and `问题状态`

If steps 3-6 fail, do not edit the PRD.

## Review Metadata Contract

Every issue candidate should already contain:

| Field | Values |
|---|---|
| `severity` | `P0` / `P1` / `P2` / `P3` |
| `dimension_id` | dimension code such as `07` |
| `dimension_name` | review dimension name |
| `scope_origin` | `default_bundle` / `force_check` / `manual_add` |
| `anchor_hint` | source anchor text |
| `problem` | agent problem statement |
| `suggestion` | agent recommendation |
| `stage` | `Review` |
| `finding_class` | `硬缺口` / `待确认` / `优化建议` |
| `evidence_basis` | `正文` / `正文+原型` / `原型附件` / `评论线程` / `推断` |
| `confidence` | `high` / `medium` / `low` |

These fields should flow into the feedback-detail rows.

## Table Schema

### Table 1: `评审轮次`

| Field | Type | Notes |
|---|---|---|
| `轮次Key` | text | unique key for the reply snapshot |
| `文档标题` | text | current PRD title |
| `文档链接` | text | original wiki/docx URL |
| `WikiToken` | text | wiki token if source was `/wiki/` |
| `DocToken` | text | resolved doc token |
| `文档类型` | select | `wiki->docx` / `docx` / `doc` / `other` |
| `Auth路径` | select | fixed to `UAT(user)` |
| `Skill版本` | text | skill protocol version |
| `反馈记录时间` | datetime | current write time |
| `用户最后回复时间` | datetime | latest user reply timestamp |
| `需求级别` | select | `小需求` / `中需求` / `大需求` |
| `已检查维度` | text | normalized dimension list |
| `未检查维度` | text | normalized dimension list |
| `强制补检命中项` | text | normalized dimension list |
| `本轮质量分` | number | score over checked dimensions only |
| `评论卡片总数` | number | total scanned comment cards |
| `有用户回复卡片数` | number | cards with an actual user reply |
| `采纳数` | number | count of `采纳` |
| `不采纳数` | number | count of `不采纳` |
| `待澄清数` | number | count of unresolved items |
| `待执行确认数` | number | accepted issues still waiting for PM confirmation |
| `已处理数` | number | count of `问题状态 = 已处理` |
| `活跃豁免数` | number | count of active waivers linked to this round |
| `当前是否可交付开发` | select | `是` / `否` |
| `风险余额摘要` | text | compressed risk summary for development handoff |
| `问题日志摘要` | text | compressed issue-log summary |
| `复盘摘要` | text | high-level run summary |

### Table 2: `建议反馈明细`

| Field | Type | Notes |
|---|---|---|
| `建议Key` | text | unique per round + comment |
| `轮次` | link | link to `评审轮次` |
| `CommentID` | text | original issue thread comment id |
| `当前处理线程CommentID` | text | active thread comment id; equals `CommentID` for normal issues and only differs when a legacy full-document comment has been replaced by a local thread |
| `锚点原文` | text | quote or anchor text |
| `维度编号` | text | source review dimension |
| `风险指纹` | text | normalized risk identity |
| `严重级别` | select | `P0` / `P1` / `P2` / `P3` |
| `建议类别` | select | `硬缺口` / `待确认` / `优化建议` |
| `证据来源` | select | `正文` / `正文+原型` / `原型附件` / `评论线程` / `推断` |
| `问题描述` | text | agent problem statement |
| `建议修改` | text | agent recommendation |
| `用户回复结论` | select | `采纳` / `不采纳` / `待澄清` |
| `用户回复原文` | text | latest effective user reply |
| `模型协助说明` | text | optional instruction when accepted |
| `豁免原因` | text | required for `不采纳` |
| `最终口径` | text | final user-approved policy or wording |
| `拟修改位置` | text | target section or anchor of the planned edit |
| `拟修改前` | text | short before preview shown to PM |
| `拟修改后` | text | exact proposed wording or rule shown to PM |
| `执行确认状态` | select | `待确认` / `已确认` / `已取消` / `不涉及正文` |
| `确认提示ReplyID` | text | assistant reply id that carries the in-thread confirmation prompt in new rounds |
| `确认卡片ID` | text | legacy top-level confirmation-card id from older rounds |
| `确认回复原文` | text | latest PM confirmation reply |
| `最近确认时间` | datetime | last confirmation reply time |
| `问题状态` | select | `已处理` / `待澄清` |
| `正文处理结果` | select | `已写回正文` / `豁免登记` / `待确认修改` / `待澄清` / `仅记录` |
| `待澄清原因` | select | `未回复` / `缺少豁免原因` / `回复格式不清` / `回复矛盾` / `待执行确认` / `执行失败` |
| `最近追问时间` | datetime | last clarification follow-up time |
| `最近追问轮次Key` | text | last round key that already emitted a follow-up |
| `最近追问ReplyID` | text | assistant reply id that carries the in-thread clarification prompt in new rounds |
| `最近追问卡片ID` | text | legacy top-level clarification follow-up comment id from older rounds |
| `线程回复快照` | text | normalized thread transcript |
| `是否命中既有豁免` | select | `是` / `否` |
| `误差标签` | select | `命中` / `方案过度` / `证据错位` / `超出范围` / `误判` / `未判定` |
| `记录时间` | datetime | write time |

### Table 3: `豁免台账`

| Field | Type | Notes |
|---|---|---|
| `豁免Key` | text | unique waiver key |
| `风险指纹` | text | normalized repeated-risk identity |
| `维度编号` | text | source review dimension |
| `问题描述归一化` | text | normalized problem statement |
| `适用范围` | text | module / scope / version where the waiver applies |
| `豁免原因` | text | business reason for waiving the issue |
| `首次登记轮次` | text | first `轮次Key` that created the waiver |
| `最近命中轮次` | text | latest `轮次Key` that matched the waiver |
| `累计命中次数` | number | total times the waiver was matched |
| `当前状态` | select | `有效` / `已触发复盘` / `已失效` |
| `后续研发复盘状态` | select | `未触发` / `待复盘` / `已复盘` |
| `复盘结论` | text | retrospective conclusion |
| `最近更新时间` | datetime | last update time |

## Select Option Contract

To keep the Base analyzable across runs, all select fields must use these exact option sets.

| Field | Allowed values |
|---|---|
| `文档类型` | `wiki->docx` / `docx` / `doc` / `other` |
| `Auth路径` | `UAT(user)` |
| `需求级别` | `小需求` / `中需求` / `大需求` |
| `当前是否可交付开发` | `是` / `否` |
| `严重级别` | `P0` / `P1` / `P2` / `P3` |
| `建议类别` | `硬缺口` / `待确认` / `优化建议` |
| `证据来源` | `正文` / `正文+原型` / `原型附件` / `评论线程` / `推断` |
| `用户回复结论` | `采纳` / `不采纳` / `待澄清` |
| `问题状态` | `已处理` / `待澄清` |
| `执行确认状态` | `待确认` / `已确认` / `已取消` / `不涉及正文` |
| `正文处理结果` | `已写回正文` / `豁免登记` / `待确认修改` / `待澄清` / `仅记录` |
| `待澄清原因` | `未回复` / `缺少豁免原因` / `回复格式不清` / `回复矛盾` / `待执行确认` / `执行失败` |
| `是否命中既有豁免` | `是` / `否` |
| `误差标签` | `命中` / `方案过度` / `证据错位` / `超出范围` / `误判` / `未判定` |
| `当前状态` | `有效` / `已触发复盘` / `已失效` |
| `后续研发复盘状态` | `未触发` / `待复盘` / `已复盘` |

## First-Run Initialization

Required tool path:

1. Read `lark-shared`
2. Read `lark-base`
3. Create the Base:
   - `lark-cli base +base-create --name "PRD评审反馈库" --time-zone "Asia/Shanghai" --as user`
4. Create table `评审轮次`
5. Create table `建议反馈明细`
6. Create table `豁免台账`
7. Validate all tables
8. Write the bound tokens and table ids back into `feedback-log.config.json`

Field creation must use `lark-cli base +table-create` with field JSON when practical, or `+field-create` if a second pass is clearer.

## Migration Rules

If the config is bound to an existing Base but the schema is older than `2.2`:

1. Reuse the current Base token
2. Validate the existing `评审轮次` and `建议反馈明细` tables
3. Create the missing `豁免台账` table if needed
4. Add any missing reply-tracking fields to the existing tables
5. If the old schema still uses `不采纳豁免数` or `用户回复结论 = 不采纳豁免`, migrate them to `不采纳数` and `不采纳`
6. Keep `确认卡片ID` / `最近追问卡片ID` for historical read compatibility
7. Add `当前处理线程CommentID`, `确认提示ReplyID`, and `最近追问ReplyID`
8. Update `feedback-log.config.json` to `schema_version = 2.2`

If any migration step fails, stop and log `feedback_base_schema_migration_failed`.

## Idempotency Rules

Use these exact keys:

- `轮次Key = sha1(doc_token + sorted(comment_id:latest_user_reply_id_or_none))`
- `建议Key = 轮次Key + "::" + comment_id`
- `豁免Key = sha1(risk_fingerprint + effective_scope)`

Behavior:

| Situation | Required behavior |
|---|---|
| same `轮次Key` already exists | update existing run/detail records; do not create duplicates |
| new `轮次Key` | create a new run row and matching detail rows |
| comment has no user reply | still create a detail row with `用户回复结论 = 待澄清` |
| same waiver already exists | update hit count, latest round, and latest time instead of creating a duplicate waiver row |

## Decision Parsing

The user-facing reply model is intentionally simple:

- `采纳`
- `不采纳`

The storage layer may also use:

- `待澄清`

`待澄清` is system-derived and should only be used when:

- the user has not replied
- the reply is incomplete or contradictory
- the waiver reason is missing

`不采纳` means the issue will be treated as a waiver candidate. If the reason is present, register the waiver and mark the issue as `已处理`; otherwise keep it in `待澄清`.

`最终口径` must come from the user's latest reply, not the agent's original suggestion.

`采纳` does not authorize immediate document editing. It only authorizes the workflow to draft a proposed edit and request PM execution confirmation.

## Risk Fingerprint

Generate `风险指纹` from:

- `维度编号`
- normalized problem statement
- module / effective scope

The fingerprint should be stable enough that future review passes can match repeated findings against the waiver ledger.

## Error-Tag Attribution

Use these rules:

| Situation | `误差标签` |
|---|---|
| user accepts and final PRD change matches the issue intent | `命中` |
| user agrees with the problem but narrows or simplifies the fix | `方案过度` |
| user says the evidence is from an outdated prototype, old screenshot, hallucinated context, or not the current source of truth | `证据错位` |
| user says the point is merely background, not in scope, or a process-state vs filter-enum mismatch | `超出范围` |
| user rejects the issue itself and the current PRD body does not support the agent claim | `误判` |
| attribution remains ambiguous | `未判定` |

## Clarification Follow-up Idempotency

When a comment remains `待澄清` for a user-resolvable reason:

- append one clarification reply in the active thread at most once per `comment_id + 当前处理线程CommentID + 轮次Key`
- persist `最近追问时间`, `最近追问轮次Key`, and `最近追问ReplyID` into the detail row
- if the same `轮次Key` re-runs, do not repeat the same follow-up reply
- if a later run creates a new `轮次Key` and the issue is still unresolved, one new follow-up reply may be added again
- if the unresolved issue only exists on a legacy full-document comment, first create a local replacement thread, set `当前处理线程CommentID` to that replacement thread, and then write future follow-up replies there
- when reading older rounds, `最近追问卡片ID` remains valid as a legacy source of truth

## Change Confirmation Idempotency

When a comment has `用户回复结论 = 采纳` and the workflow has derived a concrete planned edit:

- append one confirmation reply in the active thread at most once per `comment_id + 当前处理线程CommentID + normalized_planned_change`
- persist `确认提示ReplyID`, `确认回复原文`, and `最近确认时间` into the detail row
- if the same planned change re-runs, do not repeat the same confirmation reply
- if the planned change content changes materially, append a new confirmation reply version in the same thread and wait for a fresh `确认执行`
- when reading older rounds, `确认卡片ID` remains valid as a legacy source of truth

## Update-Back Rules

After PRD edits finish:

- update the affected detail rows with `正文处理结果`
- update the affected detail rows with `问题状态`
- update the run row with:
  - `已处理数`
  - `待澄清数`
  - `当前是否可交付开发`
  - `风险余额摘要`

If the PRD edit succeeded but the Base update-back failed:

- keep the PRD edit
- log `feedback_log_update_failed`
- report the mismatch in the final run summary

## Required Issue Types

Always log these when applicable:

- `feedback_base_config_missing`
- `feedback_base_init_failed`
- `feedback_base_schema_migration_failed`
- `feedback_base_binding_invalid`
- `feedback_log_write_failed`
- `feedback_log_update_failed`

## Reply-First Read Rules

- New rounds should treat the original issue thread as the default write and read surface for `待澄清` and `待确认修改方案`.
- `CommentID` should remain stable as the original issue thread id even if a legacy full-document thread is later replaced.
- `当前处理线程CommentID` tells the workflow where new assistant replies and user replies should happen.
- Legacy top-level clarification / confirmation cards remain readable, but new rounds should not create them again.
