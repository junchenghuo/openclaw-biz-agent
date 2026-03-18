#!/usr/bin/env python3
"""巡检频道消息：出现绝对路径但无附件时自动告警并要求重发。"""

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
STATE_PATH = BASE_DIR / "STATE" / "attachment_compliance_state.json"
TASK_CENTER_BASE = os.getenv("TASK_CENTER_BASE_URL", "http://127.0.0.1:18080")
MM_ACCOUNT = os.getenv("MATTERMOST_ALERT_ACCOUNT", "pm")

ABS_PATH_RE = re.compile(r"/Users/[\w\-./\u4e00-\u9fff]+")
TASK_CODE_RE = re.compile(r"T\d{1,}")
DONE_TOKEN_RE = re.compile(r"\bDONE\b|\bdone\b|已完成|完成回执", re.IGNORECASE)
DELIVERY_TOKEN_RE = re.compile(r"交付|已提交|提交产物|产出完成|已交付")
PROJECT_ROOT = "/Users/imac/midCreate/openclaw-workspaces/ai-team/projects/"
IMAGE_EXT_RE = re.compile(r"\.(png|jpg|jpeg|webp|gif)$", re.IGNORECASE)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


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


def should_flag_message(message: str, file_ids: list[str]) -> tuple[bool, str]:
    if file_ids:
        return False, ""
    text = (message or "").strip()
    if not text:
        return False, ""

    has_abs = bool(ABS_PATH_RE.search(text))
    has_path_label = "保存绝对路径" in text
    has_deliverables = "deliverables/" in text
    if has_abs or has_path_label or has_deliverables:
        return True, "仅路径无附件"

    has_done_with_task = bool(DONE_TOKEN_RE.search(text) and TASK_CODE_RE.search(text))
    if has_done_with_task:
        return True, "已完成回执无附件"

    has_delivery_intent = bool(
        ("@bot-leader" in text and DONE_TOKEN_RE.search(text))
        or DELIVERY_TOKEN_RE.search(text)
    )
    if has_delivery_intent:
        return True, "交付类消息无附件"

    return False, ""


def path_scope_invalid(message: str) -> bool:
    text = message or ""
    paths = ABS_PATH_RE.findall(text)
    for p in paths:
        if p.startswith("/Users/") and not p.startswith(PROJECT_ROOT):
            return True
    return False


def prototype_path_not_image(message: str) -> bool:
    text = message or ""
    if "原型图" not in text:
        return False
    paths = ABS_PATH_RE.findall(text)
    for p in paths:
        if "原型图" in p and not IMAGE_EXT_RE.search(p):
            return True
    return False


def extract_task_codes(message: str) -> list[str]:
    return sorted(set(TASK_CODE_RE.findall(message or "")))


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
        print("COMPLIANCE_ERROR missing mattermost baseUrl or botToken")
        return 1

    state = load_state()
    handled = set(state.get("handledPostIds") or [])

    status, me = mm_api_json(base_url, token, "GET", "/api/v4/users/me")
    if status != 200:
        print("COMPLIANCE_ERROR cannot read bot user")
        return 1
    leader_uid = me.get("id")

    projects = http_get_json(f"{TASK_CENTER_BASE}/api/projects").get("data", [])
    warned = 0

    for p in projects:
        channel_id = str(p.get("mattermostChannelId") or "").strip()
        if not channel_id:
            continue

        code, payload = mm_api_json(
            base_url,
            token,
            "GET",
            f"/api/v4/channels/{channel_id}/posts?page=0&per_page=80",
        )
        if code != 200:
            continue

        order = payload.get("order") or []
        posts = payload.get("posts") or {}
        for post_id in order:
            if post_id in handled:
                continue
            post = posts.get(post_id) or {}
            user_id = str(post.get("user_id") or "")
            if not user_id or user_id == leader_uid:
                handled.add(post_id)
                continue

            msg = str(post.get("message") or "")
            file_ids = post.get("file_ids") or []
            should_flag, reason = should_flag_message(msg, file_ids)
            if not should_flag:
                if path_scope_invalid(msg):
                    should_flag, reason = True, "路径越界（不在 projects 根目录）"
                elif prototype_path_not_image(msg):
                    should_flag, reason = True, "原型图路径不是图片文件"
                else:
                    handled.add(post_id)
                    continue

            u_code, u = mm_api_json(base_url, token, "GET", f"/api/v4/users/{user_id}")
            username = u.get("username") if u_code == 200 else "unknown"
            mention = (
                f"@{username}" if username and username != "unknown" else "该责任人"
            )
            task_codes = extract_task_codes(msg)
            task_hint = f"任务：{'/'.join(task_codes)}。" if task_codes else ""

            warn_msg = (
                f"{mention} @bot-leader\n"
                f"【附件合规拦截】检测到{reason}。{task_hint}\n"
                "闭环规则：仅文本路径 = 未交付；必须同条消息附真实文件。\n"
                f"路径规则：所有绝对路径必须位于 {PROJECT_ROOT}\n"
                "请按以下格式重发（必须含真实附件）：\n"
                "- @bot-leader 已完成 <任务编码> 保存绝对路径：<file1>; <file2>\n"
                "  示例：@bot-leader 已完成 T291471526719524864 保存绝对路径：/Users/.../deliverables/ui/稿件-01.png; /Users/.../deliverables/ui/规范.docx\n"
                "- 使用 mattermost-openclaw-media 或 message 工具发送附件后再回执。\n"
                "当前状态：阻塞（仅路径未附文件）。"
            )
            try:
                send_text(channel_id, warn_msg)
                warned += 1
                print(
                    f"COMPLIANCE_WARN channel={channel_id} post={post_id} user={username}"
                )
            except RuntimeError as exc:
                print(f"COMPLIANCE_ERROR send failed channel={channel_id}: {exc}")

            handled.add(post_id)

    # 限制 state 体积
    state["handledPostIds"] = list(handled)[-5000:]
    state["updatedAt"] = datetime.now().isoformat(timespec="seconds")
    save_state(state)
    print(f"COMPLIANCE_DONE warned={warned}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
