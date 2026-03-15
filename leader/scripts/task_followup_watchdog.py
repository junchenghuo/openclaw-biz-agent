#!/usr/bin/env python3
"""任务中心自动巡检：每轮按项目在对应频道@未完成任务责任人。"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


BASE_DIR = Path(__file__).resolve().parents[1]
OPENCLAW_CONFIG_PATH = Path("/Users/imac/.openclaw/openclaw.json")
CONTACTS_PATH = BASE_DIR / "STATE" / "mattermost_contacts.json"
STATE_DIR = BASE_DIR / "STATE"
STATE_PATH = STATE_DIR / "task_followup_state.json"

TASK_CENTER_BASE = os.getenv("TASK_CENTER_BASE_URL", "http://127.0.0.1:18080")
MM_ACCOUNT = os.getenv("MATTERMOST_ALERT_ACCOUNT", "pm")
FOLLOWUP_STATUSES = {
    "PENDING",
    "RUNNING",
    "BLOCKED",
    "FAILED",
    "待处理",
    "进行中",
    "阻塞",
    "失败",
}
BASELINE_ROLES_ENV = os.getenv(
    "MATTERMOST_BASELINE_ROLES", "leader,product,arch,fe,be,qa,ops"
)
OUTBOX_FAIL_STATUSES = {"失败", "已取消"}


@dataclass
class Contact:
    role: str
    username: str
    display_name: str
    user_id: str


def http_get_json(url: str) -> dict[str, Any]:
    req = Request(url, method="GET")
    with urlopen(req, timeout=20) as resp:
        payload = resp.read().decode("utf-8", errors="replace")
    return json.loads(payload)


def load_contacts() -> tuple[dict[str, Contact], dict[str, Contact], str]:
    raw = json.loads(CONTACTS_PATH.read_text(encoding="utf-8"))
    by_role: dict[str, Contact] = {}
    by_name: dict[str, Contact] = {}
    base_url = str(raw.get("baseUrl") or "").strip()
    for item in raw.get("contacts", []):
        c = Contact(
            role=str(item.get("role", "")).strip(),
            username=str(item.get("username", "")).strip(),
            display_name=str(item.get("name", "")).strip(),
            user_id=str(item.get("user_id", "")).strip(),
        )
        if c.role:
            by_role[c.role] = c
        if c.display_name:
            by_name[c.display_name] = c
    return by_role, by_name, base_url


def load_mattermost_bot_token() -> str:
    # 优先环境变量，便于本地临时覆盖
    env_token = (os.getenv("MATTERMOST_BOT_TOKEN") or "").strip()
    if env_token:
        return env_token

    raw = json.loads(OPENCLAW_CONFIG_PATH.read_text(encoding="utf-8"))
    token = (
        raw.get("channels", {})
        .get("mattermost", {})
        .get("accounts", {})
        .get(MM_ACCOUNT, {})
        .get("botToken", "")
    )
    return str(token).strip()


def mm_api_json(
    base_url: str,
    token: str,
    method: str,
    path: str,
    data: dict[str, Any] | None = None,
) -> tuple[int, Any]:
    body = None
    if data is not None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
    req = Request(
        base_url.rstrip("/") + path,
        data=body,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urlopen(req, timeout=20) as resp:
            payload = resp.read().decode("utf-8", errors="replace")
            return resp.status, json.loads(payload) if payload else {}
    except HTTPError as e:
        payload = e.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(payload) if payload else {}
        except Exception:
            parsed = {"message": payload}
        return e.code, parsed


def ensure_member_in_channel(
    base_url: str, token: str, channel_id: str, user_id: str
) -> tuple[bool, str]:
    if not user_id:
        return False, "missing_user_id"

    # 已在群内
    code, _ = mm_api_json(
        base_url,
        token,
        "GET",
        f"/api/v4/channels/{channel_id}/member/{user_id}",
    )
    if code == 200:
        return True, "already_member"

    # 不在群内则尝试拉群
    code, resp = mm_api_json(
        base_url,
        token,
        "POST",
        f"/api/v4/channels/{channel_id}/members",
        {"user_id": user_id},
    )
    if code in (200, 201):
        return True, "invited"

    # 某些场景 API 会返回已是成员，视为成功
    msg = str(resp.get("message") or "").lower()
    if "already" in msg and "member" in msg:
        return True, "already_member"

    detail = str(resp.get("message") or resp.get("id") or "unknown_error")
    return False, f"http_{code}:{detail}"


def should_send_admin_alert(
    prev_project_state: dict[str, Any], failed_users: list[str]
) -> bool:
    if not failed_users:
        return False

    current = set(failed_users)
    prev_users = set(prev_project_state.get("lastAdminAlertUsers") or [])
    if current != prev_users:
        return True

    last_alert_at = str(prev_project_state.get("lastAdminAlertAt") or "").strip()
    if not last_alert_at:
        return True
    try:
        last_dt = datetime.fromisoformat(last_alert_at)
    except ValueError:
        return True

    return datetime.now() - last_dt >= timedelta(minutes=30)


def format_admin_alert_message(
    project_name: str,
    channel_id: str,
    skipped_mentions: list[str],
    failure_reasons: dict[str, str],
) -> str:
    lines = [
        "@admin @bot-leader",
        f"【巡检告警】项目群成员补拉失败：{project_name}",
        f"频道ID：{channel_id}",
        "以下责任人未能成功拉群，已暂不@，请处理权限后重试：",
    ]
    for mention in sorted(skipped_mentions):
        reason = failure_reasons.get(mention, "unknown")
        lines.append(f"- {mention}（原因：{reason}）")
    lines.append("处理完成后请在本频道 @bot-leader 回执：已补拉。")
    return "\n".join(lines)


def parse_owner_role(owner_name: str) -> str | None:
    text = owner_name.strip().lower()
    m = re.search(r"[（(]([a-z]+)[）)]", text)
    if m:
        token = m.group(1)
        if token in {"leader", "product", "arch", "fe", "be", "qa", "ops", "ui", "ai"}:
            return token

    mapping = {
        "产品": "product",
        "架构": "arch",
        "前端": "fe",
        "后端": "be",
        "测试": "qa",
        "运维": "ops",
        "ui": "ui",
        "ai": "ai",
        "leader": "leader",
    }
    for k, v in mapping.items():
        if k in text:
            return v
    return None


def parse_baseline_roles(by_role: dict[str, Contact]) -> list[Contact]:
    roles = [r.strip().lower() for r in BASELINE_ROLES_ENV.split(",") if r.strip()]
    out: list[Contact] = []
    for role in roles:
        c = by_role.get(role)
        if c and c.user_id:
            out.append(c)
    return out


def task_signature(project_id: int, tasks: list[dict[str, Any]]) -> str:
    parts: list[str] = [str(project_id)]
    for t in sorted(tasks, key=lambda x: int(x.get("id", 0))):
        parts.append(
            f"{t.get('id')}:{t.get('status')}:{t.get('ownerName')}:{t.get('updatedAt')}"
        )
    return "|".join(parts)


def load_state() -> dict[str, Any]:
    if not STATE_PATH.exists():
        return {}
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_state(data: dict[str, Any]) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def send_to_channel(channel_id: str, message: str) -> None:
    raise RuntimeError("send_to_channel(channel_id, message) is deprecated")


def send_to_channel_post(
    base_url: str,
    token: str,
    channel_id: str,
    message: str,
    attachments: list[dict[str, Any]] | None = None,
) -> None:
    body: dict[str, Any] = {"channel_id": channel_id, "message": message}
    if attachments:
        body["props"] = {"attachments": attachments}

    code, resp = mm_api_json(base_url, token, "POST", "/api/v4/posts", body)
    if code in (200, 201):
        return

    # 兜底：若直连 API 失败，尝试 openclaw message 发送纯文本。
    cmd = [
        "openclaw",
        "message",
        "send",
        "--channel",
        "mattermost",
        "--account",
        MM_ACCOUNT,
        "--target",
        f"channel:{channel_id}",
        "--message",
        message,
    ]
    cp = subprocess.run(cmd, text=True, capture_output=True, check=False)
    if cp.returncode != 0:
        err = str(resp.get("message") or cp.stderr or cp.stdout).strip()
        raise RuntimeError(f"send failed channel={channel_id}: {err}")


def format_followup_message(
    project_name: str,
    mentions: list[str],
    tasks: list[dict[str, Any]],
    skipped_mentions: list[str],
) -> str:
    head = " ".join(mentions) if mentions else "@bot-leader"
    lines = [
        f"{head}",
        f"任务中心 5 分钟巡检 | 项目：{project_name}",
        f"未完成任务 {len(tasks)} 条，请立即同步进展；已完成请及时更新任务状态为 COMPLETED。",
    ]

    if skipped_mentions:
        lines.append("")
        lines.append(
            "未成功拉群，暂不@："
            + " ".join(sorted(skipped_mentions))
            + "；请 @admin 处理群成员权限后重试。"
        )
    lines.append("")
    lines.append("任务清单（催办必须带任务编码）：")
    for t in tasks[:12]:
        code = str(t.get("taskCode") or f"TASK-{t.get('id')}").strip()
        owner = str(t.get("ownerName") or "未指派").strip()
        status = str(t.get("status") or "未知").strip()
        title = str(t.get("title") or "").replace("\n", " ").strip()
        lines.append(f"- {code} | {owner} | {status} | {title}")
    if len(tasks) > 12:
        lines.append(f"- 其余 {len(tasks) - 12} 条请查看任务中心。")
    lines.append("")
    lines.append("回执格式（强制）：")
    lines.append("- 已接单：@bot-leader 已接单 Txxxx")
    lines.append("- 完成：@bot-leader 已完成 Txxxx 保存绝对路径：<file1>; <file2>")
    lines.append("- 阻塞：@bot-leader 阻塞 Txxxx 原因：... 需协助：...")
    lines.append(
        "- 必须等待 Leader 回执 outboxId/outboxStatus；无 outbox 状态不算系统已闭环。"
    )
    return "\n".join(lines)


def fetch_recent_outbox_failures() -> list[dict[str, Any]]:
    try:
        resp = http_get_json(f"{TASK_CENTER_BASE}/api/outbox?limit=200")
    except Exception:
        return []
    rows = resp.get("data") or []
    out: list[dict[str, Any]] = []
    for x in rows:
        status = str(x.get("status") or "")
        if status in OUTBOX_FAIL_STATUSES:
            out.append(x)
    return out


def format_outbox_blocked_appendix(
    project_id: int, failures: list[dict[str, Any]]
) -> list[str]:
    if not failures:
        return []
    lines = [
        "",
        "【消息投递阻塞】以下任务消息投递失败，请优先补偿：",
    ]
    shown = 0
    for x in failures:
        if int(x.get("projectId") or 0) != project_id:
            continue
        outbox_id = x.get("id")
        task_id = x.get("taskId")
        status = x.get("status")
        err = str(x.get("lastError") or "")
        if len(err) > 140:
            err = err[:140] + "..."
        lines.append(f"- outbox={outbox_id} taskId={task_id} status={status} err={err}")
        shown += 1
        if shown >= 5:
            break
    if shown == 0:
        return []
    lines.append("建议：先修复频道权限/成员，再执行 /api/outbox/{id}/replay 重放。")
    return lines


def format_followup_card(
    project_name: str,
    tasks: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    fields: list[dict[str, Any]] = []
    for t in tasks[:20]:
        code = str(t.get("taskCode") or f"TASK-{t.get('id')}").strip()
        status = str(t.get("status") or "UNKNOWN").strip()
        title = str(t.get("title") or "").replace("\n", " ").strip()
        owner = str(t.get("ownerName") or "未指派").strip()
        fields.append(
            {
                "title": code,
                "value": f"状态：{status}\n负责人：{owner}\n标题：{title}",
                "short": True,
            }
        )

    if len(tasks) > 20:
        fields.append(
            {
                "title": "更多任务",
                "value": f"其余 {len(tasks) - 20} 条请在任务中心查看。",
                "short": False,
            }
        )

    return [
        {
            "color": "#1E88E5",
            "title": "任务中心 5 分钟巡检",
            "text": f"项目：{project_name}\n未完成任务：{len(tasks)} 条",
            "fields": fields,
        }
    ]


def main() -> int:
    by_role, by_name, contacts_base_url = load_contacts()
    mm_base_url = (os.getenv("MATTERMOST_BASE_URL") or contacts_base_url or "").strip()
    mm_token = load_mattermost_bot_token()
    if not mm_base_url or not mm_token:
        print("WATCHDOG_ERROR missing mattermost baseUrl or botToken")
        return 1

    baseline_contacts = parse_baseline_roles(by_role)
    outbox_failures = fetch_recent_outbox_failures()
    state = load_state()
    sent_count = 0

    try:
        projects_resp = http_get_json(f"{TASK_CENTER_BASE}/api/projects")
    except (HTTPError, URLError, TimeoutError) as exc:
        print(f"WATCHDOG_ERROR fetch projects failed: {exc}")
        return 1

    projects = projects_resp.get("data", [])
    next_state: dict[str, Any] = {}

    for p in projects:
        project_id = int(p.get("id", 0))
        channel_id = (p.get("mattermostChannelId") or "").strip()
        project_name = (p.get("projectName") or f"PROJECT-{project_id}").strip()
        if project_id <= 0 or not channel_id:
            continue

        try:
            tasks_resp = http_get_json(
                f"{TASK_CENTER_BASE}/api/tasks?projectId={project_id}"
            )
        except (HTTPError, URLError, TimeoutError) as exc:
            print(f"WATCHDOG_WARN fetch tasks failed project={project_id}: {exc}")
            continue

        tasks = tasks_resp.get("data", [])
        pending = [t for t in tasks if str(t.get("status", "")) in FOLLOWUP_STATUSES]

        signature = task_signature(project_id, pending)
        key = str(project_id)
        prev_project_state = (
            state.get(key, {}) if isinstance(state.get(key), dict) else {}
        )
        next_state[key] = {
            "signature": signature,
            "updatedAt": datetime.now().isoformat(timespec="seconds"),
        }

        # 无未完成任务时不发催办
        if not pending:
            continue

        # 如果签名未变化，仍按每5分钟触发一次提醒（满足用户要求）
        # 保留 state 主要用于审计和后续扩展
        # 先确保基础执行角色在群内，避免后续@无法触达。
        baseline_failures: dict[str, str] = {}
        for c in baseline_contacts:
            ok, reason = ensure_member_in_channel(
                mm_base_url, mm_token, channel_id, c.user_id
            )
            if not ok:
                baseline_failures[f"@{c.username}"] = reason
                print(
                    f"WATCHDOG_WARN baseline invite failed channel={channel_id} user={c.username} reason={reason}"
                )

        mention_contacts: dict[str, Contact] = {}
        for t in pending:
            owner = str(t.get("ownerName") or "").strip()
            contact = by_name.get(owner)
            if not contact:
                role = parse_owner_role(owner)
                if role:
                    contact = by_role.get(role)
            if contact and contact.username:
                mention_contacts[contact.username] = contact

        mentions: list[str] = []
        skipped_mentions: list[str] = []
        failure_reasons: dict[str, str] = dict(baseline_failures)
        for username in sorted(mention_contacts.keys()):
            contact = mention_contacts[username]
            ok, reason = ensure_member_in_channel(
                mm_base_url, mm_token, channel_id, contact.user_id
            )
            if ok:
                mentions.append(f"@{username}")
            else:
                mention = f"@{username}"
                skipped_mentions.append(mention)
                failure_reasons[mention] = reason
                print(
                    f"WATCHDOG_WARN invite/member check failed channel={channel_id} user={username} reason={reason}"
                )

        failure_history: dict[str, Any] = {}
        prev_failures = prev_project_state.get("inviteFailures")
        if isinstance(prev_failures, dict):
            failure_history.update(prev_failures)

        current_failed_users = []
        for mention in sorted(skipped_mentions):
            username = mention.lstrip("@")
            old = failure_history.get(username, {})
            old_count = int(old.get("count", 0)) if isinstance(old, dict) else 0
            failure_history[username] = {
                "count": old_count + 1,
                "lastAt": datetime.now().isoformat(timespec="seconds"),
                "lastError": failure_reasons.get(mention, "unknown"),
            }
            current_failed_users.append(username)

        # 清除已恢复成员的失败历史，避免状态持续污染
        for username in list(failure_history.keys()):
            if username not in current_failed_users:
                failure_history.pop(username, None)

        next_state[key]["inviteFailures"] = failure_history

        msg = format_followup_message(project_name, mentions, pending, skipped_mentions)
        appendix = format_outbox_blocked_appendix(project_id, outbox_failures)
        if appendix:
            msg = msg + "\n" + "\n".join(appendix)
        card = format_followup_card(project_name, pending)
        try:
            send_to_channel_post(
                mm_base_url, mm_token, channel_id, msg, attachments=card
            )
            sent_count += 1
            print(
                f"WATCHDOG_SENT project={project_id} channel={channel_id} pending={len(pending)}"
            )
        except RuntimeError as exc:
            print(f"WATCHDOG_WARN {exc}")

        if should_send_admin_alert(prev_project_state, current_failed_users):
            alert_msg = format_admin_alert_message(
                project_name, channel_id, skipped_mentions, failure_reasons
            )
            try:
                send_to_channel_post(mm_base_url, mm_token, channel_id, alert_msg)
                next_state[key]["lastAdminAlertAt"] = datetime.now().isoformat(
                    timespec="seconds"
                )
                next_state[key]["lastAdminAlertUsers"] = sorted(current_failed_users)
                print(
                    f"WATCHDOG_ALERT project={project_id} channel={channel_id} failed={len(current_failed_users)}"
                )
            except RuntimeError as exc:
                print(f"WATCHDOG_WARN admin alert send failed: {exc}")
        else:
            next_state[key]["lastAdminAlertAt"] = prev_project_state.get(
                "lastAdminAlertAt"
            )
            next_state[key]["lastAdminAlertUsers"] = prev_project_state.get(
                "lastAdminAlertUsers", []
            )

    save_state(next_state)
    print(f"WATCHDOG_DONE sent={sent_count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
