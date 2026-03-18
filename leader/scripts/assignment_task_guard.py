#!/usr/bin/env python3
"""派单一致性巡检：检测“频道已派单但任务中心未建单/缺任务编码”问题。"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen


BASE_DIR = Path(__file__).resolve().parents[1]
OPENCLAW_CONFIG_PATH = Path("/Users/imac/.openclaw/openclaw.json")
CONTACTS_PATH = BASE_DIR / "STATE" / "mattermost_contacts.json"
STATE_PATH = BASE_DIR / "STATE" / "assignment_task_guard_state.json"
TASK_CENTER_BASE = os.getenv("TASK_CENTER_BASE_URL", "http://127.0.0.1:18080")
MM_ACCOUNT = os.getenv("MATTERMOST_ALERT_ACCOUNT", "pm")

TASK_CODE_RE = re.compile(r"T\d{1,}")
ROLE_MENTION_RE = re.compile(r"@(bot-(?:product|arch|test|ai))")
PROJECT_HINT_RE = re.compile(
    r"projectId\s*[:=]\s*\d+|projectCode\s*[:=]\s*[A-Za-z0-9\-]+|项目[:：]",
    re.IGNORECASE,
)
ENGLISH_SENTENCE_RE = re.compile(r"[A-Za-z]{4,}[^\u4e00-\u9fff]*")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_state() -> dict[str, Any]:
    if not STATE_PATH.exists():
        return {"handledPostIds": []}
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {"handledPostIds": []}


def save_state(state: dict[str, Any]) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(
        json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def http_get_json(url: str) -> dict[str, Any]:
    req = Request(url, method="GET")
    with urlopen(req, timeout=20) as resp:
        payload = resp.read().decode("utf-8", errors="replace")
    return json.loads(payload)


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


def send_text(channel_id: str, message: str) -> None:
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
        err = (cp.stderr or cp.stdout).strip()
        raise RuntimeError(err)


def should_check_message(message: str) -> bool:
    text = (message or "").strip()
    if not text:
        return False
    if "项目启动通知" in text:
        return False
    if "任务中心 5 分钟巡检" in text:
        return False
    if "附件合规拦截" in text:
        return False
    if "派单一致性告警" in text:
        return False
    return bool(ROLE_MENTION_RE.search(text))


def has_project_context(message: str) -> bool:
    text = (message or "").strip()
    if not text:
        return False
    return bool(PROJECT_HINT_RE.search(text))


def has_english_drift(message: str) -> bool:
    text = (message or "").strip()
    if not text:
        return False
    # 放宽：仅当存在较长英文且无中文时才告警
    return bool(
        ENGLISH_SENTENCE_RE.search(text) and not re.search(r"[\u4e00-\u9fff]", text)
    )


def main() -> int:
    oc = read_json(OPENCLAW_CONFIG_PATH)
    contacts = read_json(CONTACTS_PATH)
    base_url = str(contacts.get("baseUrl") or "").strip()
    token = (
        oc.get("channels", {})
        .get("mattermost", {})
        .get("accounts", {})
        .get(MM_ACCOUNT, {})
        .get("botToken", "")
    )
    token = str(token).strip()
    if not base_url or not token:
        print("ASSIGN_GUARD_ERROR missing mattermost baseUrl or botToken")
        return 1

    state = load_state()
    handled = set(state.get("handledPostIds") or [])
    warned = 0

    projects = http_get_json(f"{TASK_CENTER_BASE}/api/projects").get("data", [])
    for p in projects:
        project_id = int(p.get("id") or 0)
        channel_id = str(p.get("mattermostChannelId") or "").strip()
        if project_id <= 0 or not channel_id:
            continue

        tasks = http_get_json(
            f"{TASK_CENTER_BASE}/api/tasks?projectId={project_id}"
        ).get("data", [])
        task_codes = {
            str(t.get("taskCode") or "").strip() for t in tasks if t.get("taskCode")
        }

        code, payload = mm_api_json(
            base_url,
            token,
            "GET",
            f"/api/v4/channels/{channel_id}/posts?page=0&per_page=120",
        )
        if code != 200:
            continue

        order = payload.get("order") or []
        posts = payload.get("posts") or {}
        for post_id in order:
            if post_id in handled:
                continue

            post = posts.get(post_id) or {}
            msg = str(post.get("message") or "")
            if not should_check_message(msg):
                handled.add(post_id)
                continue

            codes = sorted(set(TASK_CODE_RE.findall(msg)))
            if not codes:
                warn_msg = (
                    "@bot-leader\n"
                    "【派单一致性告警】检测到频道内已@角色派单，但未携带任务编码。\n"
                    f"项目ID：{project_id}，消息ID：{post_id}\n"
                    "请先在任务中心创建任务，再按 `@bot-xxx 已接单 <任务编码>` 规范推进。"
                )
                try:
                    send_text(channel_id, warn_msg)
                    warned += 1
                    print(
                        f"ASSIGN_GUARD_WARN missing_code project={project_id} post={post_id}"
                    )
                except RuntimeError as exc:
                    print(f"ASSIGN_GUARD_ERROR send failed channel={channel_id}: {exc}")
                handled.add(post_id)
                continue

            if not has_project_context(msg):
                warn_msg = (
                    "@bot-leader\n"
                    "【派单一致性告警】检测到派单消息缺少项目上下文。\n"
                    f"项目ID：{project_id}，消息ID：{post_id}\n"
                    "请补充：projectId/projectCode/projectName/channelId。"
                )
                try:
                    send_text(channel_id, warn_msg)
                    warned += 1
                except RuntimeError as exc:
                    print(f"ASSIGN_GUARD_ERROR send failed channel={channel_id}: {exc}")

            if has_english_drift(msg):
                warn_msg = (
                    "@bot-leader\n"
                    "【语言合规告警】检测到派单消息可能使用英文。\n"
                    f"项目ID：{project_id}，消息ID：{post_id}\n"
                    "请按规则改为简体中文重发。"
                )
                try:
                    send_text(channel_id, warn_msg)
                    warned += 1
                except RuntimeError as exc:
                    print(f"ASSIGN_GUARD_ERROR send failed channel={channel_id}: {exc}")

            missing_codes = [c for c in codes if c not in task_codes]
            if missing_codes:
                warn_msg = (
                    "@bot-leader\n"
                    "【派单一致性告警】检测到消息中的任务编码未在任务中心落库。\n"
                    f"项目ID：{project_id}，消息ID：{post_id}\n"
                    f"缺失任务编码：{', '.join(missing_codes)}\n"
                    "请立即补建任务并回执 taskId/taskCode。"
                )
                try:
                    send_text(channel_id, warn_msg)
                    warned += 1
                    print(
                        f"ASSIGN_GUARD_WARN missing_task project={project_id} post={post_id}"
                    )
                except RuntimeError as exc:
                    print(f"ASSIGN_GUARD_ERROR send failed channel={channel_id}: {exc}")

            handled.add(post_id)

    state["handledPostIds"] = list(handled)[-5000:]
    state["updatedAt"] = datetime.now().isoformat(timespec="seconds")
    save_state(state)
    print(f"ASSIGN_GUARD_DONE warned={warned}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
