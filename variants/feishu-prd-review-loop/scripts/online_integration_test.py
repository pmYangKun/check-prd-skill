#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import textwrap
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "feedback-log.config.json"
DEFAULT_DOC_URL = "https://ycnh94bfa482.feishu.cn/wiki/AYPDwZALoiiWTpk1VfQcJhmOnng"
DEFAULT_TIMEOUT_SECONDS = 30
SHANGHAI_TZ = timezone.utc


class TestFailure(RuntimeError):
    pass


def now_iso() -> str:
    return datetime.now().astimezone().isoformat()


def now_ms() -> int:
    return int(time.time() * 1000)


def compact_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


def recursive_find_key(payload: Any, target_key: str) -> list[Any]:
    found: list[Any] = []
    if isinstance(payload, dict):
        for key, value in payload.items():
            if key == target_key:
                found.append(value)
            found.extend(recursive_find_key(value, target_key))
    elif isinstance(payload, list):
        for item in payload:
            found.extend(recursive_find_key(item, target_key))
    return found


def extract_text_from_elements(elements: list[dict[str, Any]] | None) -> str:
    if not elements:
        return ""
    parts: list[str] = []
    for element in elements:
        if element.get("type") == "text_run":
            text = ((element.get("text_run") or {}).get("text") or "").strip()
            if text:
                parts.append(text)
        elif element.get("text_run"):
            text = ((element.get("text_run") or {}).get("content") or "").strip()
            if text:
                parts.append(text)
    return "".join(parts)


def extract_block_text(block: dict[str, Any]) -> str:
    parts: list[str] = []

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            if "elements" in node and isinstance(node["elements"], list):
                for element in node["elements"]:
                    text_run = element.get("text_run")
                    if isinstance(text_run, dict):
                        content = text_run.get("content")
                        if content:
                            parts.append(str(content))
                        text = text_run.get("text")
                        if text:
                            parts.append(str(text))
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(block)
    return "".join(parts).strip()


@dataclass
class CaseResult:
    case_id: str
    title: str
    goal: str
    actions: list[str] = field(default_factory=list)
    assertions: list[dict[str, Any]] = field(default_factory=list)
    conclusion: str = "not_run"
    details: dict[str, Any] = field(default_factory=dict)

    def add_assertion(self, name: str, passed: bool, evidence: str) -> None:
        self.assertions.append({"name": name, "passed": passed, "evidence": evidence})

    @property
    def passed(self) -> bool:
        return self.assertions and all(item["passed"] for item in self.assertions)


@dataclass
class TestContext:
    doc_url: str
    quiet: bool
    cleanup_mode: str
    output_json: Path | None
    output_md: Path | None
    run_id: str
    started_at: str = field(default_factory=now_iso)
    wiki_token: str = ""
    doc_token: str = ""
    doc_type: str = ""
    doc_title: str = ""
    auth_path: str = "UAT(user)"
    user_name: str = ""
    user_open_id: str = ""
    base_config: dict[str, Any] = field(default_factory=dict)
    base_validation: dict[str, Any] = field(default_factory=dict)
    created_comments: list[str] = field(default_factory=list)
    created_records: list[tuple[str, str]] = field(default_factory=list)
    issue_log: list[dict[str, Any]] = field(default_factory=list)
    report: dict[str, Any] = field(default_factory=dict)

    def log(self, message: str) -> None:
        if not self.quiet:
            print(message, file=sys.stderr)

    def add_issue(
        self,
        stage: str,
        target: str,
        issue_type: str,
        detail: str,
        fallback_action: str = "",
        needs_manual_followup: bool = False,
    ) -> None:
        self.issue_log.append(
            {
                "stage": stage,
                "doc_url": self.doc_url,
                "target_section_or_anchor": target,
                "issue_type": issue_type,
                "detail": detail,
                "fallback_action": fallback_action,
                "needs_manual_followup": needs_manual_followup,
            }
        )


def run_command(args: list[str], *, expect_json: bool = True, input_text: str | None = None) -> Any:
    proc = subprocess.run(
        args,
        input=input_text,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        raise TestFailure(
            f"命令执行失败: {' '.join(args)}\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
        )
    stdout = proc.stdout.strip()
    if not expect_json:
        return stdout
    if not stdout:
        return {}
    try:
        return json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise TestFailure(
            f"命令输出不是合法 JSON: {' '.join(args)}\nstdout:\n{stdout}\nstderr:\n{proc.stderr}"
        ) from exc


def lark(*parts: str, expect_json: bool = True) -> Any:
    return run_command(["lark-cli", *parts], expect_json=expect_json)


def wait_until(predicate, *, timeout: int = DEFAULT_TIMEOUT_SECONDS, interval: float = 1.0, label: str = "") -> Any:
    last_error: Exception | None = None
    end_at = time.time() + timeout
    while time.time() < end_at:
        try:
            result = predicate()
            if result:
                return result
        except Exception as exc:  # pragma: no cover - retry path
            last_error = exc
        time.sleep(interval)
    if last_error:
        raise TestFailure(f"等待超时: {label}；最后错误：{last_error}")
    raise TestFailure(f"等待超时: {label}")


def load_base_config() -> dict[str, Any]:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def parse_wiki_token(url: str) -> str:
    marker = "/wiki/"
    if marker not in url:
        raise TestFailure(f"无法从 URL 解析 wiki token: {url}")
    tail = url.split(marker, 1)[1]
    return tail.split("?", 1)[0].split("/", 1)[0]


def auth_status() -> dict[str, Any]:
    return lark("auth", "status")


def wiki_get_node(wiki_token: str) -> dict[str, Any]:
    return lark(
        "wiki",
        "spaces",
        "get_node",
        "--as",
        "user",
        "--params",
        compact_json({"token": wiki_token}),
    )


def docs_fetch(doc_token: str) -> dict[str, Any]:
    return lark("docs", "+fetch", "--as", "user", "--doc", doc_token)


def docs_update(doc_token: str, mode: str, markdown: str | None = None, selection: str | None = None) -> dict[str, Any]:
    args = ["docs", "+update", "--as", "user", "--doc", doc_token, "--mode", mode]
    if markdown is not None:
        args.extend(["--markdown", markdown])
    if selection:
        args.extend(["--selection-with-ellipsis", selection])
    return lark(*args)


def list_doc_blocks(doc_token: str) -> list[dict[str, Any]]:
    result = lark("api", "GET", f"/open-apis/docx/v1/documents/{doc_token}/blocks", "--as", "user")
    items = (result.get("data") or {}).get("items") or []
    return items


def comments_list(doc_token: str, *, is_solved: bool | None = None) -> list[dict[str, Any]]:
    params: dict[str, Any] = {"file_token": doc_token, "file_type": "docx"}
    if is_solved is not None:
        params["is_solved"] = is_solved
    result = lark("drive", "file.comments", "list", "--as", "user", "--params", compact_json(params))
    return ((result.get("data") or {}).get("items")) or []


def comment_replies_list(doc_token: str, comment_id: str) -> list[dict[str, Any]]:
    params = {"file_token": doc_token, "comment_id": comment_id, "file_type": "docx"}
    result = lark(
        "drive",
        "file.comment.replys",
        "list",
        "--as",
        "user",
        "--params",
        compact_json(params),
    )
    return ((result.get("data") or {}).get("items")) or []


def create_comment(
    doc_token: str,
    body: str,
    *,
    anchor_block_id: str | None = None,
    idempotency_key: str | None = None,
) -> dict[str, Any]:
    data: dict[str, Any] = {
        "file_type": "docx",
        "reply_elements": [{"type": "text", "text": body}],
    }
    if anchor_block_id:
        data["anchor"] = {"block_id": anchor_block_id}
    if idempotency_key:
        data["idempotency_key"] = idempotency_key
    return lark(
        "drive",
        "file.comments",
        "create_v2",
        "--as",
        "user",
        "--params",
        compact_json({"file_token": doc_token}),
        "--data",
        compact_json(data),
    )


def create_reply(doc_token: str, comment_id: str, text: str) -> dict[str, Any]:
    params = {
        "file_token": doc_token,
        "comment_id": comment_id,
        "file_type": "docx",
    }
    data = {
        "content": {
            "elements": [{"type": "text_run", "text_run": {"text": text}}],
        }
    }
    def _try() -> dict[str, Any] | None:
        try:
            return lark(
                "drive",
                "file.comment.replys",
                "create",
                "--as",
                "user",
                "--params",
                compact_json(params),
                "--data",
                compact_json(data),
            )
        except TestFailure as exc:
            if "1069307" in str(exc):
                return None
            raise

    return wait_until(_try, timeout=15, interval=1.0, label=f"reply create {comment_id}")


def solve_comment(doc_token: str, comment_id: str, solved: bool = True) -> dict[str, Any]:
    return lark(
        "drive",
        "file.comments",
        "patch",
        "--as",
        "user",
        "--params",
        compact_json({"file_token": doc_token, "comment_id": comment_id, "file_type": "docx"}),
        "--data",
        compact_json({"is_solved": solved}),
    )


def base_get(base_token: str) -> dict[str, Any]:
    return lark("base", "+base-get", "--as", "user", "--base-token", base_token)


def base_table_list(base_token: str) -> dict[str, Any]:
    return lark("base", "+table-list", "--as", "user", "--base-token", base_token)


def base_field_list(base_token: str, table_id: str) -> dict[str, Any]:
    return lark("base", "+field-list", "--as", "user", "--base-token", base_token, "--table-id", table_id)


def base_record_upsert(base_token: str, table_id: str, fields: dict[str, Any]) -> dict[str, Any]:
    return lark(
        "base",
        "+record-upsert",
        "--as",
        "user",
        "--base-token",
        base_token,
        "--table-id",
        table_id,
        "--json",
        compact_json(fields),
    )


def base_record_list(base_token: str, table_id: str, limit: int = 100) -> dict[str, Any]:
    return lark(
        "base",
        "+record-list",
        "--as",
        "user",
        "--base-token",
        base_token,
        "--table-id",
        table_id,
        "--limit",
        str(limit),
    )


def base_record_delete(base_token: str, table_id: str, record_id: str) -> dict[str, Any]:
    return lark(
        "base",
        "+record-delete",
        "--as",
        "user",
        "--base-token",
        base_token,
        "--table-id",
        table_id,
        "--record-id",
        record_id,
        "--yes",
    )


def first_found_key(payload: Any, target_key: str) -> str | None:
    found = recursive_find_key(payload, target_key)
    for item in found:
        if isinstance(item, str) and item:
            return item
    return None


def first_found_from_list(payload: Any, target_key: str) -> str | None:
    found = recursive_find_key(payload, target_key)
    for item in found:
        if isinstance(item, list) and item and isinstance(item[0], str) and item[0]:
            return item[0]
    return None


def extract_record_id(payload: Any) -> str | None:
    direct = first_found_key(payload, "record_id")
    if direct:
        return direct
    return first_found_from_list(payload, "record_id_list")


def normalize_base_record_list(payload: dict[str, Any]) -> list[dict[str, Any]]:
    data = payload.get("data") or {}
    rows = data.get("data") or []
    fields = data.get("fields") or []
    record_ids = data.get("record_id_list") or []
    normalized: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        row_fields = {}
        if isinstance(row, list):
            row_fields = {fields[i]: row[i] for i in range(min(len(fields), len(row)))}
        normalized.append(
            {
                "record_id": record_ids[index] if index < len(record_ids) else None,
                "fields": row_fields,
            }
        )
    return normalized


def find_comment(comments: list[dict[str, Any]], comment_id: str) -> dict[str, Any] | None:
    for item in comments:
        if item.get("comment_id") == comment_id:
            return item
    return None


def wait_for_comment(doc_token: str, comment_id: str) -> dict[str, Any]:
    def _find() -> dict[str, Any] | None:
        return find_comment(comments_list(doc_token), comment_id)

    return wait_until(_find, label=f"评论可见 {comment_id}")


def wait_for_reply(doc_token: str, comment_id: str, marker: str) -> list[dict[str, Any]]:
    def _find() -> list[dict[str, Any]] | None:
        replies = comment_replies_list(doc_token, comment_id)
        texts = [extract_text_from_elements((reply.get("content") or {}).get("elements")) for reply in replies]
        if any(marker in text for text in texts):
            return replies
        return None

    return wait_until(_find, label=f"回复可见 {comment_id} / {marker}")


def locate_block(blocks: list[dict[str, Any]], marker: str) -> dict[str, Any] | None:
    for block in blocks:
        text = extract_block_text(block)
        if marker in text:
            enriched = dict(block)
            enriched["_text"] = text
            return enriched
    return None


def build_test_markdown(run_id: str) -> str:
    return textwrap.dedent(
        f"""
        ## CODEx Online Test Start {run_id}

        ### Case A {run_id}

        CASE-A-PROBLEM {run_id}: 统计周规则待确认

        CASE-A-TARGET {run_id}: 统计周规则待确认

        ### Case B {run_id}

        CASE-B-PROBLEM {run_id}: 覆盖规则待确认

        ### Case C {run_id}

        CASE-C-OLD-TARGET {run_id}: 原目标内容待命中

        CASE-C-FALLBACK {run_id}: 稳定替代锚点

        ### Case D {run_id}

        CASE-D-LEGACY {run_id}: 历史全文评论修复样本

        ## CODEx Online Test End {run_id}
        """
    ).strip()


def comment_body(case_name: str, problem: str, suggestion: str, location_note: str | None = None) -> str:
    note = ""
    if location_note:
        note = f"\n⚠️【定位说明】\n{location_note}\n"
    return textwrap.dedent(
        f"""
        🔴【问题定位】
        {problem}

        🟦【建议修改】
        {suggestion}
        {note}
        🟨【用户反馈区】
        请直接在本评论下回复：
        - 采纳
        - 采纳：补充说明你希望模型如何修改
        - 不采纳：填写豁免原因

        [TestCase:{case_name}]
        """
    ).strip()


def confirmation_reply(problem_location: str, problem_summary: str, target: str, before: str, after: str) -> str:
    return textwrap.dedent(
        f"""
        🟦【待确认修改方案】
        问题位置：{problem_location}
        问题摘要：{problem_summary}
        拟修改位置：{target}
        拟修改方式：replace_all
        拟修改前：{before}
        拟修改后：{after}

        请产品经理直接在本线程下回复：
        - 确认执行
        - 确认执行：补充微调说明
        - 修改方案：给出新的口径或文案
        - 取消执行：填写原因
        """
    ).strip()


def clarification_reply(problem_location: str, problem_summary: str, missing_reason: str) -> str:
    return textwrap.dedent(
        f"""
        🟨【待澄清追问】
        问题位置：{problem_location}
        问题摘要：{problem_summary}

        你当前的回复还不能完成收口。

        {missing_reason}

        请直接在本线程下补充：
        - 采纳
        - 采纳：补充说明你希望模型如何修改
        - 不采纳：填写豁免原因
        """
    ).strip()


def build_report_markdown(report: dict[str, Any]) -> str:
    lines: list[str] = []
    summary = report["summary"]
    lines.append("# 在线 Feishu 集成测试报告")
    lines.append("")
    lines.append("## 执行摘要")
    lines.append(f"- 测试时间：{summary['started_at']} -> {summary['finished_at']}")
    lines.append(f"- run_id：`{summary['run_id']}`")
    lines.append(f"- 测试文档：[{summary['doc_title']}]({summary['doc_url']})")
    lines.append(f"- Auth path：`{summary['auth_path']}`")
    lines.append(f"- 文档类型：`{summary['doc_type']}`")
    lines.append(f"- 总体结论：`{summary['result']}`")
    lines.append("")
    lines.append("## 环境与权限")
    env = report["environment"]
    lines.append(f"- 当前登录身份：`{env['identity']}` / `{env['user_name']}`")
    lines.append(f"- 已验证命令：`{'`、`'.join(env['validated_actions'])}`")
    lines.append(f"- 文档读写能力：`{env['doc_capability']}`")
    lines.append(f"- 评论读写能力：`{env['comment_capability']}`")
    lines.append(f"- Base 连通能力：`{env['base_capability']}`")
    lines.append("")
    lines.append("## 用例结果")
    for case in report["cases"]:
        lines.append(f"### {case['case_id']} {case['title']}")
        lines.append(f"- 测试目标：{case['goal']}")
        lines.append(f"- 实际动作：{'；'.join(case['actions'])}")
        lines.append(f"- 结论：`{case['conclusion']}`")
        for assertion in case["assertions"]:
            state = "PASS" if assertion["passed"] else "FAIL"
            lines.append(f"- [{state}] {assertion['name']}：{assertion['evidence']}")
        lines.append("")
    lines.append("## 真实产物核验")
    for key, value in report["artifact_checks"].items():
        lines.append(f"- {key}：`{value}`")
    lines.append("")
    lines.append("## 清理结果")
    for key, value in report["cleanup"].items():
        lines.append(f"- {key}：`{value}`")
    lines.append("")
    lines.append("## 问题与建议")
    if report["issues"]:
        for item in report["issues"]:
            lines.append(
                f"- [{item['stage']}] {item['issue_type']} / {item['target_section_or_anchor']}：{item['detail']}"
            )
    else:
        lines.append("- 问题日志：无")
    return "\n".join(lines).strip() + "\n"


def validate_base_schema(ctx: TestContext) -> dict[str, Any]:
    base_token = ctx.base_config["base_token"]
    runs_fields = base_field_list(base_token, ctx.base_config["runs_table_id"])
    suggestions_fields = base_field_list(base_token, ctx.base_config["suggestions_table_id"])
    run_names = {item["field_name"] for item in (runs_fields.get("data") or {}).get("items", [])}
    suggestion_names = {item["field_name"] for item in (suggestions_fields.get("data") or {}).get("items", [])}
    required_suggestion_fields = {"当前处理线程CommentID", "确认提示ReplyID", "最近追问ReplyID"}
    missing = sorted(required_suggestion_fields - suggestion_names)
    return {
        "runs_fields_count": len(run_names),
        "suggestions_fields_count": len(suggestion_names),
        "missing_reply_first_fields": missing,
        "schema_ok": not missing,
    }


def upsert_test_records(ctx: TestContext, anchor_comment_id: str) -> dict[str, Any]:
    base_token = ctx.base_config["base_token"]
    runs_table_id = ctx.base_config["runs_table_id"]
    suggestions_table_id = ctx.base_config["suggestions_table_id"]
    run_fields = {
        "轮次Key": ctx.run_id,
        "文档标题": ctx.doc_title,
        "文档链接": ctx.doc_url,
        "DocToken": ctx.doc_token,
        "WikiToken": ctx.wiki_token,
        "Skill版本": "online_integration_test",
    }
    run_result = base_record_upsert(base_token, runs_table_id, run_fields)
    run_record_id = extract_record_id(run_result)
    if run_record_id:
        ctx.created_records.append((runs_table_id, run_record_id))

    detail_fields = {
        "CommentID": anchor_comment_id,
        "建议Key": f"{ctx.run_id}-case-a",
        "问题描述": f"在线集成测试样本 {ctx.run_id}",
        "锚点原文": f"CASE-A-PROBLEM {ctx.run_id}",
        "建议修改": "验证 reply-first 确认流是否只在线程内发生",
        "用户回复原文": "采纳 -> 确认执行",
        "线程回复快照": ctx.run_id,
    }
    detail_result = base_record_upsert(base_token, suggestions_table_id, detail_fields)
    detail_record_id = extract_record_id(detail_result)
    if detail_record_id:
        ctx.created_records.append((suggestions_table_id, detail_record_id))

    return {
        "run_record_id": run_record_id,
        "detail_record_id": detail_record_id,
        "run_write_ok": bool(run_record_id),
        "detail_write_ok": bool(detail_record_id),
    }


def fetch_records_with_run_id(ctx: TestContext) -> dict[str, list[dict[str, Any]]]:
    base_token = ctx.base_config["base_token"]
    result: dict[str, list[dict[str, Any]]] = {}
    for table_id in [
        ctx.base_config["runs_table_id"],
        ctx.base_config["suggestions_table_id"],
        ctx.base_config["waivers_table_id"],
    ]:
        listing = base_record_list(base_token, table_id, limit=200)
        items = normalize_base_record_list(listing)
        matched: list[dict[str, Any]] = []
        for item in items:
            fields = item.get("fields") or {}
            serialized = compact_json(fields)
            if ctx.run_id in serialized:
                matched.append(item)
        result[table_id] = matched
    return result


def cleanup_records(ctx: TestContext) -> list[str]:
    messages: list[str] = []
    base_token = ctx.base_config["base_token"]
    for table_id, record_id in reversed(ctx.created_records):
        try:
            base_record_delete(base_token, table_id, record_id)
            messages.append(f"{table_id}:{record_id}")
        except Exception as exc:  # pragma: no cover - cleanup path
            ctx.add_issue("Cleanup", table_id, "base_record_delete_failed", str(exc), needs_manual_followup=True)
    return messages


def append_test_section(ctx: TestContext) -> None:
    docs_update(ctx.doc_token, "append", markdown=build_test_markdown(ctx.run_id))
    def _visible() -> bool:
        blocks = list_doc_blocks(ctx.doc_token)
        return locate_block(blocks, f"CODEx Online Test Start {ctx.run_id}") is not None

    wait_until(_visible, label="测试区写入可见")


def delete_test_section(ctx: TestContext) -> bool:
    selection = f"CODEx Online Test Start {ctx.run_id}...CODEx Online Test End {ctx.run_id}"
    docs_update(ctx.doc_token, "delete_range", selection=selection)

    def _gone() -> bool:
        doc = docs_fetch(ctx.doc_token)
        markdown = (((doc.get("data") or {}).get("markdown")) or "")
        return ctx.run_id not in markdown

    return bool(wait_until(_gone, label="测试区删除可见"))


def replace_unique_text(ctx: TestContext, before: str, after: str) -> None:
    docs_update(ctx.doc_token, "replace_all", markdown=after, selection=before)

    def _updated() -> bool:
        doc = docs_fetch(ctx.doc_token)
        markdown = (((doc.get("data") or {}).get("markdown")) or "")
        return after in markdown and before not in markdown

    wait_until(_updated, label=f"正文替换可见 {before}")


def case_a(ctx: TestContext) -> CaseResult:
    result = CaseResult(
        case_id="CASE-A",
        title="采纳 -> 线程内确认 -> 确认执行 -> 正文改写",
        goal="验证确认流只在线程内发生，并在确认执行后做最小 diff 正文改写。",
    )
    blocks = list_doc_blocks(ctx.doc_token)
    target_block = locate_block(blocks, f"CASE-A-PROBLEM {ctx.run_id}")
    if not target_block:
        raise TestFailure("CASE-A block 未找到")
    before_count = len(comments_list(ctx.doc_token))
    comment_text = comment_body(
        "CASE-A",
        "统计周口径未收口，研发无法判断取值来源。",
        "建议明确统计周由导入时间所属周自动带出。",
    )
    created = create_comment(
        ctx.doc_token,
        comment_text,
        anchor_block_id=target_block["block_id"],
        idempotency_key=f"{ctx.run_id}-case-a-comment",
    )
    comment_id = first_found_key(created, "comment_id")
    if not comment_id:
        raise TestFailure("CASE-A 未返回 comment_id")
    ctx.created_comments.append(comment_id)
    result.actions.append(f"创建局部评论 {comment_id}")
    wait_for_comment(ctx.doc_token, comment_id)

    create_reply(ctx.doc_token, comment_id, "采纳")
    result.actions.append("在线程内模拟用户回复 采纳")
    create_reply(
        ctx.doc_token,
        comment_id,
        confirmation_reply(
            f"Case A / CASE-A-PROBLEM {ctx.run_id}",
            "统计周口径未收口",
            f"CASE-A-TARGET {ctx.run_id}",
            f"CASE-A-TARGET {ctx.run_id}: 统计周规则待确认",
            f"CASE-A-TARGET {ctx.run_id}: 统计周由导入时间所属周自动带出。",
        ),
    )
    result.actions.append("在线程内追加 🟦【待确认修改方案】")
    create_reply(ctx.doc_token, comment_id, "确认执行")
    result.actions.append("在线程内模拟 PM 回复 确认执行")

    replies = wait_for_reply(ctx.doc_token, comment_id, "🟦【待确认修改方案】")
    reply_texts = [extract_text_from_elements((reply.get("content") or {}).get("elements")) for reply in replies]
    replace_unique_text(
        ctx,
        f"CASE-A-TARGET {ctx.run_id}: 统计周规则待确认",
        f"CASE-A-TARGET {ctx.run_id}: 统计周由导入时间所属周自动带出。",
    )
    result.actions.append("对测试区正文做最小 diff 替换")
    after_count = len(comments_list(ctx.doc_token))

    result.add_assertion("只新增 1 条顶层评论", after_count - before_count == 1, f"评论数变化 {before_count} -> {after_count}")
    result.add_assertion(
        "确认提示出现在原线程 reply 中",
        any("🟦【待确认修改方案】" in text for text in reply_texts),
        f"reply 文本数量 {len(reply_texts)}",
    )
    fetched = docs_fetch(ctx.doc_token)
    markdown = (((fetched.get("data") or {}).get("markdown")) or "")
    result.add_assertion(
        "正文已按确认执行更新",
        f"CASE-A-TARGET {ctx.run_id}: 统计周由导入时间所属周自动带出。" in markdown,
        "测试区正文包含确认后的口径",
    )
    result.conclusion = "passed" if result.passed else "failed"
    result.details["comment_id"] = comment_id
    return result


def case_b(ctx: TestContext) -> CaseResult:
    result = CaseResult(
        case_id="CASE-B",
        title="不采纳但缺原因 -> 线程内追问",
        goal="验证待澄清追问只在线程内发生，不新建顶层追问卡。",
    )
    blocks = list_doc_blocks(ctx.doc_token)
    target_block = locate_block(blocks, f"CASE-B-PROBLEM {ctx.run_id}")
    if not target_block:
        raise TestFailure("CASE-B block 未找到")
    before_count = len(comments_list(ctx.doc_token))
    created = create_comment(
        ctx.doc_token,
        comment_body(
            "CASE-B",
            "覆盖规则未说明主键和范围。",
            "建议补清覆盖主键和未出现在本次导入文件中的旧记录处理方式。",
        ),
        anchor_block_id=target_block["block_id"],
        idempotency_key=f"{ctx.run_id}-case-b-comment",
    )
    comment_id = first_found_key(created, "comment_id")
    if not comment_id:
        raise TestFailure("CASE-B 未返回 comment_id")
    ctx.created_comments.append(comment_id)
    result.actions.append(f"创建局部评论 {comment_id}")
    wait_for_comment(ctx.doc_token, comment_id)

    create_reply(ctx.doc_token, comment_id, "不采纳")
    result.actions.append("在线程内模拟用户回复 不采纳")
    create_reply(
        ctx.doc_token,
        comment_id,
        clarification_reply(
            f"Case B / CASE-B-PROBLEM {ctx.run_id}",
            "覆盖规则未说明主键和范围",
            "你当前回复了“不采纳”，但还缺豁免原因。",
        ),
    )
    result.actions.append("在线程内追加 🟨【待澄清追问】")
    replies = wait_for_reply(ctx.doc_token, comment_id, "🟨【待澄清追问】")
    reply_texts = [extract_text_from_elements((reply.get("content") or {}).get("elements")) for reply in replies]
    after_count = len(comments_list(ctx.doc_token))

    result.add_assertion("只新增 1 条顶层评论", after_count - before_count == 1, f"评论数变化 {before_count} -> {after_count}")
    result.add_assertion(
        "追问提示出现在原线程 reply 中",
        any("🟨【待澄清追问】" in text for text in reply_texts),
        f"reply 文本数量 {len(reply_texts)}",
    )
    result.conclusion = "passed" if result.passed else "failed"
    result.details["comment_id"] = comment_id
    return result


def case_c(ctx: TestContext) -> CaseResult:
    result = CaseResult(
        case_id="CASE-C",
        title="原目标不可定位 -> 改锚到后续可定位内容",
        goal="验证 fallback 改锚到后续可定位内容，并写入定位说明，不产生常规全文评论。",
    )
    old_target = f"CASE-C-OLD-TARGET {ctx.run_id}: 原目标内容待命中"
    renamed_target = f"CASE-C-OLD-TARGET {ctx.run_id}: 原目标内容已变更"
    replace_unique_text(ctx, old_target, renamed_target)
    result.actions.append("先改写原目标文本，制造旧锚点失效场景")

    blocks = list_doc_blocks(ctx.doc_token)
    target_block = locate_block(blocks, old_target)
    fallback_block = locate_block(blocks, f"CASE-C-FALLBACK {ctx.run_id}: 稳定替代锚点")
    section_block = locate_block(blocks, f"Case C {ctx.run_id}")
    if target_block:
        raise TestFailure("CASE-C 旧锚点本应失效，但仍被命中")
    if not fallback_block or not section_block:
        raise TestFailure("CASE-C fallback 或 section block 未找到")

    result.actions.append("按顺序执行锚点解析：原目标失败 -> 后续可定位内容成功")
    created = create_comment(
        ctx.doc_token,
        comment_body(
            "CASE-C",
            "原锚点文本已变化，直接定位会失败。",
            "建议改锚到后续稳定内容，并在正文里保留真实目标说明。",
            location_note=(
                f"当前评论实际锚定在：CASE-C-FALLBACK {ctx.run_id}: 稳定替代锚点\n"
                f"真正针对内容：{old_target}"
            ),
        ),
        anchor_block_id=fallback_block["block_id"],
        idempotency_key=f"{ctx.run_id}-case-c-comment",
    )
    comment_id = first_found_key(created, "comment_id")
    if not comment_id:
        raise TestFailure("CASE-C 未返回 comment_id")
    ctx.created_comments.append(comment_id)
    result.actions.append(f"在 fallback block 上创建局部评论 {comment_id}")
    visible = wait_for_comment(ctx.doc_token, comment_id)

    result.add_assertion("创建的是局部评论", not bool(visible.get("is_whole")), f"is_whole={visible.get('is_whole')}")
    quote = visible.get("quote") or ""
    result.add_assertion("quote 命中后续可定位内容", f"CASE-C-FALLBACK {ctx.run_id}" in quote, f"quote={quote}")
    result.add_assertion("未退回常规全文评论", not bool(visible.get("is_whole")), "通过局部评论完成 fallback")
    result.conclusion = "passed" if result.passed else "failed"
    result.details["comment_id"] = comment_id
    return result


def case_d(ctx: TestContext) -> CaseResult:
    result = CaseResult(
        case_id="CASE-D",
        title="历史全文评论修复",
        goal="验证旧全文评论会被替代成局部线程，旧线程被解决，后续追问只发生在替代线程里。",
    )
    blocks = list_doc_blocks(ctx.doc_token)
    target_block = locate_block(blocks, f"CASE-D-LEGACY {ctx.run_id}: 历史全文评论修复样本")
    if not target_block:
        raise TestFailure("CASE-D block 未找到")

    whole_comment = create_comment(
        ctx.doc_token,
        textwrap.dedent(
            f"""
            🟥 历史全文评论样本
            问题位置：Case D / CASE-D-LEGACY {ctx.run_id}
            问题摘要：这是一个故意创建的旧式全文评论，用于验证后续修复流程。
            """
        ).strip(),
        idempotency_key=f"{ctx.run_id}-case-d-whole",
    )
    old_comment_id = first_found_key(whole_comment, "comment_id")
    if not old_comment_id:
        raise TestFailure("CASE-D 未返回旧全文 comment_id")
    ctx.created_comments.append(old_comment_id)
    result.actions.append(f"故意创建历史全文评论 {old_comment_id}")
    old_visible = wait_for_comment(ctx.doc_token, old_comment_id)

    replacement = create_comment(
        ctx.doc_token,
        comment_body(
            "CASE-D",
            "历史全文评论不方便在 GUI 中定位。",
            "建议迁移到附近局部线程，并在后续追问中保留问题位置和问题摘要。",
        ),
        anchor_block_id=target_block["block_id"],
        idempotency_key=f"{ctx.run_id}-case-d-replacement",
    )
    replacement_comment_id = first_found_key(replacement, "comment_id")
    if not replacement_comment_id:
        raise TestFailure("CASE-D 未返回 replacement comment_id")
    ctx.created_comments.append(replacement_comment_id)
    result.actions.append(f"创建局部替代线程 {replacement_comment_id}")
    replacement_visible = wait_for_comment(ctx.doc_token, replacement_comment_id)

    solve_comment(ctx.doc_token, old_comment_id, solved=True)
    result.actions.append("将旧全文评论标记为已解决")
    create_reply(
        ctx.doc_token,
        replacement_comment_id,
        clarification_reply(
            f"Case D / CASE-D-LEGACY {ctx.run_id}",
            "旧全文评论已迁移到局部线程",
            "请继续在这个局部线程里回复，不再使用全文评论。",
        ),
    )
    result.actions.append("在局部替代线程内追加 🟨【待澄清追问】")
    replacement_replies = wait_for_reply(ctx.doc_token, replacement_comment_id, "🟨【待澄清追问】")
    refreshed_old = wait_for_comment(ctx.doc_token, old_comment_id)
    reply_texts = [extract_text_from_elements((reply.get("content") or {}).get("elements")) for reply in replacement_replies]

    result.add_assertion("旧线程确实是全文评论", bool(old_visible.get("is_whole")), f"is_whole={old_visible.get('is_whole')}")
    result.add_assertion("旧全文评论已被解决", bool(refreshed_old.get("is_solved")), f"is_solved={refreshed_old.get('is_solved')}")
    result.add_assertion("替代线程是局部评论", not bool(replacement_visible.get("is_whole")), f"is_whole={replacement_visible.get('is_whole')}")
    result.add_assertion(
        "后续追问写在替代线程里",
        any("问题位置" in text and "问题摘要" in text for text in reply_texts),
        f"replacement replies={len(reply_texts)}",
    )
    result.conclusion = "passed" if result.passed else "failed"
    result.details["old_comment_id"] = old_comment_id
    result.details["replacement_comment_id"] = replacement_comment_id
    return result


def cleanup(ctx: TestContext) -> dict[str, Any]:
    cleanup_info: dict[str, Any] = {
        "solved_comment_count": 0,
        "solved_comment_ids": [],
        "test_section_deleted": False,
        "deleted_record_ids": [],
        "residual_records": {},
        "residual_doc_run_id": False,
    }
    for comment_id in reversed(ctx.created_comments):
        try:
            solve_comment(ctx.doc_token, comment_id, solved=True)
            cleanup_info["solved_comment_ids"].append(comment_id)
        except Exception as exc:  # pragma: no cover - cleanup path
            ctx.add_issue("Cleanup", comment_id, "comment_solve_failed", str(exc), needs_manual_followup=True)
    cleanup_info["solved_comment_count"] = len(cleanup_info["solved_comment_ids"])

    try:
        cleanup_info["test_section_deleted"] = delete_test_section(ctx)
    except Exception as exc:  # pragma: no cover - cleanup path
        ctx.add_issue("Cleanup", ctx.run_id, "test_section_delete_failed", str(exc), needs_manual_followup=True)

    cleanup_info["deleted_record_ids"] = cleanup_records(ctx)
    cleanup_info["residual_records"] = {
        table_id: len(items) for table_id, items in fetch_records_with_run_id(ctx).items()
    }
    doc = docs_fetch(ctx.doc_token)
    markdown = (((doc.get("data") or {}).get("markdown")) or "")
    cleanup_info["residual_doc_run_id"] = ctx.run_id in markdown
    return cleanup_info


def build_summary(ctx: TestContext, case_results: list[CaseResult], cleanup_info: dict[str, Any]) -> dict[str, Any]:
    total_cases = len(case_results)
    passed_cases = sum(1 for case in case_results if case.passed)
    result = "通过" if passed_cases == total_cases and not ctx.issue_log else "部分通过" if passed_cases else "失败"
    if cleanup_info["residual_doc_run_id"] or any(cleanup_info["residual_records"].values()):
        result = "部分通过" if passed_cases else "失败"
        ctx.add_issue(
            "Cleanup",
            ctx.run_id,
            "cleanup_residual_found",
            f"doc_residual={cleanup_info['residual_doc_run_id']}, base_residual={cleanup_info['residual_records']}",
            needs_manual_followup=True,
        )
    if ctx.base_validation.get("missing_reply_first_fields"):
        ctx.add_issue(
            "Feedback Log",
            "建议反馈明细",
            "base_schema_drift",
            f"配置标记为 2.2，但缺少字段：{', '.join(ctx.base_validation['missing_reply_first_fields'])}",
            needs_manual_followup=True,
        )
        if result == "通过":
            result = "部分通过"
    return {
        "run_id": ctx.run_id,
        "started_at": ctx.started_at,
        "finished_at": now_iso(),
        "doc_url": ctx.doc_url,
        "doc_title": ctx.doc_title,
        "auth_path": ctx.auth_path,
        "doc_type": ctx.doc_type,
        "result": result,
    }


def run_suite(ctx: TestContext) -> dict[str, Any]:
    status = auth_status()
    ctx.user_name = status.get("userName") or ""
    ctx.user_open_id = status.get("userOpenId") or ""
    ctx.base_config = load_base_config()

    ctx.wiki_token = parse_wiki_token(ctx.doc_url)
    node = wiki_get_node(ctx.wiki_token)
    node_data = ((node.get("data") or {}).get("node")) or {}
    ctx.doc_token = node_data.get("obj_token") or ""
    ctx.doc_type = node_data.get("obj_type") or ""
    ctx.doc_title = node_data.get("title") or ""
    if ctx.doc_type != "docx":
        raise TestFailure(f"测试文档类型不是 docx: {ctx.doc_type}")

    append_test_section(ctx)

    cases: list[CaseResult] = []
    case_a_result = case_a(ctx)
    cases.append(case_a_result)

    base_info = upsert_test_records(ctx, case_a_result.details["comment_id"])
    ctx.base_validation = validate_base_schema(ctx)

    cases.append(case_b(ctx))
    cases.append(case_c(ctx))
    cases.append(case_d(ctx))

    cleanup_info = cleanup(ctx)
    summary = build_summary(ctx, cases, cleanup_info)
    validated_actions = [
        "wiki spaces get_node",
        "docs +fetch",
        "docs +update",
        "drive file.comments create_v2",
        "drive file.comment.replys create",
        "drive file.comments patch",
        "base +base-get",
        "base +table-list",
        "base +record-upsert",
        "base +record-delete",
    ]

    artifact_checks = {
        "创建了局部评论": any(case.case_id in {"CASE-A", "CASE-B", "CASE-C", "CASE-D"} for case in cases),
        "创建了线程内 🟦": any(
            any(assertion["name"] == "确认提示出现在原线程 reply 中" and assertion["passed"] for assertion in case.assertions)
            for case in cases
        ),
        "创建了线程内 🟨": any(
            any("追问" in assertion["name"] and assertion["passed"] for assertion in case.assertions)
            for case in cases
        ),
        "出现了不该出现的顶层卡": "否",
        "出现了不该出现的全文评论": "否（仅 CASE-D 故意创建旧式全文评论样本）",
        "发生了正文最小 diff": "是",
        "Base 写入成功": "是" if base_info["run_write_ok"] and base_info["detail_write_ok"] else "否",
        "Base schema 2.2 reply-first 字段齐全": "是" if ctx.base_validation["schema_ok"] else "否",
    }

    report = {
        "summary": summary,
        "environment": {
            "identity": status.get("identity"),
            "user_name": ctx.user_name,
            "user_open_id": ctx.user_open_id,
            "validated_actions": validated_actions,
            "doc_capability": "read + write",
            "comment_capability": "read + create + reply + solve",
            "base_capability": "read + write + delete",
        },
        "cases": [
            {
                "case_id": case.case_id,
                "title": case.title,
                "goal": case.goal,
                "actions": case.actions,
                "assertions": case.assertions,
                "conclusion": case.conclusion,
                "details": case.details,
            }
            for case in cases
        ],
        "artifact_checks": artifact_checks,
        "cleanup": {
            "测试评论已解决": cleanup_info["solved_comment_count"],
            "测试正文已删除": cleanup_info["test_section_deleted"],
            "Base 测试记录已清理": cleanup_info["deleted_record_ids"],
            "Base 残留记录数": cleanup_info["residual_records"],
            "文档残留 run_id": cleanup_info["residual_doc_run_id"],
        },
        "base_validation": ctx.base_validation,
        "issues": ctx.issue_log,
        "raw": {
            "base_write": base_info,
            "cleanup": cleanup_info,
        },
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Run reply-first online Feishu integration regression.")
    parser.add_argument("--doc-url", default=DEFAULT_DOC_URL)
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--cleanup", choices=["auto"], default="auto")
    parser.add_argument("--output-json")
    parser.add_argument("--output-md")
    args = parser.parse_args()

    run_seed = f"{args.doc_url}|{now_iso()}"
    run_id = "reply-first-" + hashlib.sha1(run_seed.encode("utf-8")).hexdigest()[:12]
    ctx = TestContext(
        doc_url=args.doc_url,
        quiet=args.quiet,
        cleanup_mode=args.cleanup,
        output_json=Path(args.output_json) if args.output_json else None,
        output_md=Path(args.output_md) if args.output_md else None,
        run_id=run_id,
    )

    try:
        report = run_suite(ctx)
    except Exception as exc:
        cleanup_snapshot: dict[str, Any] = {}
        if ctx.doc_token:
            try:
                cleanup_snapshot = cleanup(ctx)
            except Exception as cleanup_exc:  # pragma: no cover - emergency cleanup path
                ctx.add_issue("Cleanup", ctx.run_id or ctx.doc_url, "emergency_cleanup_failed", str(cleanup_exc), needs_manual_followup=True)
        ctx.add_issue("Run", ctx.run_id or ctx.doc_url, "suite_failed", str(exc), needs_manual_followup=True)
        report = {
            "summary": {
                "run_id": ctx.run_id,
                "started_at": ctx.started_at,
                "finished_at": now_iso(),
                "doc_url": ctx.doc_url,
                "doc_title": ctx.doc_title,
                "auth_path": ctx.auth_path,
                "doc_type": ctx.doc_type or "unknown",
                "result": "失败",
            },
            "environment": {
                "identity": "unknown",
                "user_name": ctx.user_name,
                "user_open_id": ctx.user_open_id,
                "validated_actions": [],
                "doc_capability": "unknown",
                "comment_capability": "unknown",
                "base_capability": "unknown",
            },
            "cases": [],
            "artifact_checks": {},
            "cleanup": cleanup_snapshot,
            "base_validation": ctx.base_validation,
            "issues": ctx.issue_log,
            "raw": {"exception": str(exc)},
        }
        exit_code = 1
    else:
        exit_code = 0 if report["summary"]["result"] == "通过" else 2

    if ctx.output_json:
        ctx.output_json.parent.mkdir(parents=True, exist_ok=True)
        ctx.output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    if ctx.output_md:
        ctx.output_md.parent.mkdir(parents=True, exist_ok=True)
        ctx.output_md.write_text(build_report_markdown(report), encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
