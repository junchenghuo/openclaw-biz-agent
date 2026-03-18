#!/usr/bin/env python3
"""根据频道 DONE 回执自动推进任务状态（附件为必需门禁）。"""

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
STATE_PATH = BASE_DIR / "STATE" / "task_done_reconcile_state.json"
TASK_CENTER_BASE = os.getenv("TASK_CENTER_BASE_URL", "http://127.0.0.1:18080")
MM_ACCOUNT = os.getenv("MATTERMOST_ALERT_ACCOUNT", "pm")

TASK_CODE_RE = re.compile(r"T\d{1,}")
PATH_RE = re.compile(r"/Users/[\w\-./\u4e00-\u9fff]+")
DONE_TOKEN_RE = re.compile(r"\bDONE\b|\bdone\b|已完成", re.IGNORECASE)
PROJECT_ROOT = "/Users/imac/midCreate/openclaw-workspaces/ai-team/projects/"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def http_json(
    method: str, url: str, data: dict[str, Any] | None = None
) -> dict[str, Any]:
    body = None
    headers = {"Content-Type": "application/json"}
    if data is not None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
    req = Request(url, method=method, data=body, headers=headers)
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


def extract_task_codes(message: str) -> list[str]:
    return sorted(set(TASK_CODE_RE.findall(message or "")))


def extract_paths(message: str) -> list[str]:
    return sorted(set(PATH_RE.findall(message or "")))


def should_parse_done(message: str) -> bool:
    text = (message or "").strip()
    if not text:
        return False
    return bool(DONE_TOKEN_RE.search(text) and TASK_CODE_RE.search(text))


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
        print("RECONCILE_ERROR missing mattermost baseUrl or botToken")
        return 1

    state = load_state()
    handled = set(state.get("handledPostIds") or [])
    auto_completed = 0
    blocked_count = 0

    projects_resp = http_json("GET", f"{TASK_CENTER_BASE}/api/projects")
    projects = projects_resp.get("data") or []

    for p in projects:
        project_id = int(p.get("id") or 0)
        channel_id = str(p.get("mattermostChannelId") or "").strip()
        if project_id <= 0 or not channel_id:
            continue

        tasks_resp = http_json(
            "GET", f"{TASK_CENTER_BASE}/api/tasks?projectId={project_id}"
        )
        tasks = tasks_resp.get("data") or []
        task_by_code = {
            str(t.get("taskCode") or "").strip(): t for t in tasks if t.get("taskCode")
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
            if not should_parse_done(msg):
                continue

            task_codes = extract_task_codes(msg)
            if not task_codes:
                continue

            file_ids = post.get("file_ids") or []
            if not file_ids:
                blocked_count += 1
                try:
                    send_text(
                        channel_id,
                        "@bot-leader 检测到已完成回执未附附件，状态不流转。请按附件规范重发："
                        "@bot-leader 已完成 <任务编码> 保存绝对路径：<file1>; <file2>（同一条消息必须含真实附件）。",
                    )
                except RuntimeError:
                    pass
                handled.add(post_id)
                continue

            # 强门禁：同条消息必须同时包含任务编码 + 绝对路径 + 附件
            paths = extract_paths(msg)
            if not paths:
                blocked_count += 1
                try:
                    send_text(
                        channel_id,
                        "@bot-leader 检测到已完成回执缺少保存绝对路径，状态不流转。请重发："
                        "@bot-leader 已完成 <任务编码> 保存绝对路径：<file1>; <file2>（同一条消息必须含真实附件）。",
                    )
                except RuntimeError:
                    pass
                handled.add(post_id)
                continue

            if any(
                p.startswith("/Users/") and not p.startswith(PROJECT_ROOT)
                for p in paths
            ):
                blocked_count += 1
                try:
                    send_text(
                        channel_id,
                        "@bot-leader 检测到交付路径不在项目根目录，状态不流转。"
                        f"请改为 {PROJECT_ROOT} 下路径并同条消息附真实附件。",
                    )
                except RuntimeError:
                    pass
                handled.add(post_id)
                continue

            for task_code in task_codes:
                task = task_by_code.get(task_code)
                if not task:
                    continue
                task_id = int(task.get("id"))
                status = str(task.get("status") or "")
                if status in {"COMPLETED", "CANCELLED", "已完成", "已取消"}:
                    continue

                if status in {"PENDING", "BLOCKED", "FAILED", "待处理", "阻塞", "失败"}:
                    http_json(
                        "POST",
                        f"{TASK_CENTER_BASE}/api/tasks/{task_id}/start",
                        {"operatorName": "郑吒（leader）"},
                    )

                output = {
                    "summary": "基于频道已完成+附件回执自动闭环",
                    "sourcePostId": post_id,
                    "paths": paths,
                    "attachmentCount": len(file_ids),
                }
                http_json(
                    "POST",
                    f"{TASK_CENTER_BASE}/api/tasks/{task_id}/complete",
                    {"operatorName": "郑吒（leader）", "output": output},
                )
                auto_completed += 1
                print(f"RECONCILE_COMPLETED task={task_code} post={post_id}")

            handled.add(post_id)

    state["handledPostIds"] = list(handled)[-5000:]
    state["updatedAt"] = datetime.now().isoformat(timespec="seconds")
    save_state(state)
    print(f"RECONCILE_DONE auto_completed={auto_completed} blocked={blocked_count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
