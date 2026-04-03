# Media Handling

This workflow must distinguish between plain document text, image or file attachments, and whiteboards.

## 1. Plain document text

Use standard minimal-diff document editing:

- first choice: `lark-cli docs +update --mode replace_range`
- second choice: `insert_before` or `insert_after`
- forbidden: `overwrite`

Always keep the edit range as small as possible.

## 2. Images and file attachments

Images and attachments are **not** forbidden zones in this workflow.

### What is allowed

- Add review comments about the media itself
- Add review comments about missing explanation next to the media
- Suggest replacement or additional explanatory text

### Default behavior

- If the issue is about interpretation, requirements, labeling, or missing explanation, prefer commenting on the surrounding text or the nearest related section.
- If the exact target cannot be anchored, relocate to the next locatable content in the same section; if that still fails, anchor to the nearest section title and explain the true target in `定位说明`.
- Do not use a full-document comment as the normal fallback for media-adjacent issues.

### Replacement policy

Do **not** replace the binary asset by default.

Only attempt asset replacement if the user explicitly provides:

- the desired replacement intent
- the replacement source or file
- confirmation that the asset itself, not just the surrounding text, should change

## 3. Whiteboards

Existing whiteboards can be edited, but not through ordinary `docs +update` text replacement.

### Read path

1. Fetch the doc body.
2. Extract `<whiteboard token="..."/>` from the markdown.
3. Route the edit through `lark-whiteboard` or `lark-cli docs +whiteboard-update`.

### Safety rules

If the target whiteboard already exists, you must dry-run first when using overwrite semantics:

```bash
npx -y @larksuite/whiteboard-cli@^0.1.0 --to openapi -i <input> --format json | \
lark-cli docs +whiteboard-update --whiteboard-token <token> --overwrite --dry-run --as user
```

### Destructive overwrite handling

If dry-run shows existing nodes would be deleted:

- stop immediately
- log `whiteboard_destructive_dry_run`
- ask the user for explicit overwrite confirmation

Without explicit user approval, do not overwrite a non-empty whiteboard.

### Non-destructive preference

Prefer updating a whiteboard without destructive overwrite if the target workflow supports it. Only escalate to overwrite after the dry run and explicit user confirmation.

## 4. Loggable media errors

These media-related issues must go into the issue log:

- could not extract whiteboard token
- attachment or image token parse failed
- dry-run indicates destructive whiteboard overwrite
- whiteboard update command failed
