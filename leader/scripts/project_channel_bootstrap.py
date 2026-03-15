#!/usr/bin/env python3
"""Create project channel and invite required members.

Usage:
  python3 leader/scripts/project_channel_bootstrap.py \
    --project-code FLOW_20260314 \
    --display-name "proj-flow-20260314" \
    --project-name "Flow 项目" \
    --kickoff-next "今日 18:00 启动会" \
    --invite-exec fe be qa
"""

from __future__ import annotations

import argparse
import json
import re
import urllib.error
import urllib.request
from pathlib import Path


OPENCLAW_CONFIG = Path("/Users/imac/.openclaw/openclaw.json")
CONTACTS_CONFIG = Path(
    "/Users/imac/midCreate/openclaw-workspaces/ai-team/leader/STATE/mattermost_contacts.json"
)


def slugify(text: str) -> str:
    s = text.strip().lower()
    s = re.sub(r"[^a-z0-9-]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s or "project"


def mm_api(base_url: str, token: str, method: str, path: str, data: dict | None = None):
    body = None
    if data is not None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        base_url.rstrip("/") + path,
        data=body,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            txt = resp.read().decode("utf-8", "ignore")
            return resp.status, json.loads(txt)
    except urllib.error.HTTPError as e:
        txt = e.read().decode("utf-8", "ignore")
        try:
            payload = json.loads(txt)
        except json.JSONDecodeError:
            payload = {"message": txt}
        return e.code, payload


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create project channel and invite members"
    )
    parser.add_argument("--project-code", required=True)
    parser.add_argument("--display-name", required=True)
    parser.add_argument("--project-name", default="")
    parser.add_argument("--kickoff-next", default="请在本频道确认启动会议程与时间")
    parser.add_argument("--purpose", default="项目协作")
    parser.add_argument("--header", default="统一由 @bot-leader 调度")
    parser.add_argument(
        "--invite-exec",
        nargs="*",
        default=[],
        help="Additional roles to invite, e.g. fe be qa ops ai ui",
    )
    args = parser.parse_args()

    oc = json.loads(OPENCLAW_CONFIG.read_text(encoding="utf-8"))
    contacts = json.loads(CONTACTS_CONFIG.read_text(encoding="utf-8"))
    token = oc["channels"]["mattermost"]["accounts"]["pm"]["botToken"]
    base_url = contacts["baseUrl"]
    team_id = contacts["team"]["id"]

    role_to_uid = {c["role"]: c["user_id"] for c in contacts["contacts"]}
    required_roles = ["arch", "product"]
    exec_roles = [r for r in args.invite_exec if r in role_to_uid]

    # admin id via API
    status, admin = mm_api(base_url, token, "GET", "/api/v4/users/username/admin")
    if status != 200:
        print(
            json.dumps(
                {"ok": False, "step": "get_admin", "status": status, "resp": admin},
                ensure_ascii=False,
            )
        )
        return 1

    channel_name = slugify(f"proj-{args.project_code}")
    status, ch = mm_api(
        base_url,
        token,
        "POST",
        "/api/v4/channels",
        {
            "team_id": team_id,
            "name": channel_name,
            "display_name": args.display_name,
            "type": "O",
            "purpose": args.purpose,
            "header": args.header,
        },
    )
    if status not in (200, 201):
        print(
            json.dumps(
                {"ok": False, "step": "create_channel", "status": status, "resp": ch},
                ensure_ascii=False,
            )
        )
        return 2

    channel_id = ch["id"]
    invite_results = []

    invite_targets = [("admin", admin["id"])]
    invite_targets += [(r, role_to_uid[r]) for r in required_roles]
    invite_targets += [(r, role_to_uid[r]) for r in exec_roles]

    for role, uid in invite_targets:
        s, resp = mm_api(
            base_url,
            token,
            "POST",
            f"/api/v4/channels/{channel_id}/members",
            {"user_id": uid},
        )
        invite_results.append(
            {
                "role": role,
                "status": s,
                "ok": s in (200, 201),
                "resp": resp if s not in (200, 201) else None,
            }
        )

    project_name = args.project_name.strip() or args.display_name
    startup_text = (
        f"@admin @bot-product @bot-arch 项目启动通知\n"
        f"项目名称：{project_name}\n"
        f"channelId：{channel_id}\n"
        f"下一步：{args.kickoff_next}"
    )
    startup_status, startup_resp = mm_api(
        base_url,
        token,
        "POST",
        "/api/v4/posts",
        {"channel_id": channel_id, "message": startup_text},
    )

    s, members = mm_api(
        base_url,
        token,
        "GET",
        f"/api/v4/channels/{channel_id}/members?page=0&per_page=200",
    )
    member_ids = (
        {m["user_id"] for m in members}
        if s == 200 and isinstance(members, list)
        else set()
    )
    required_ids = {admin["id"], role_to_uid["arch"], role_to_uid["product"]}

    out = {
        "ok": required_ids.issubset(member_ids) and startup_status in (200, 201),
        "channel": {
            "id": channel_id,
            "name": ch.get("name"),
            "display_name": ch.get("display_name"),
        },
        "required_first_three_present": required_ids.issubset(member_ids),
        "startup_post": {
            "ok": startup_status in (200, 201),
            "status": startup_status,
            "post_id": startup_resp.get("id")
            if isinstance(startup_resp, dict)
            else None,
            "mentions": ["@admin", "@bot-product", "@bot-arch"],
            "resp": None if startup_status in (200, 201) else startup_resp,
        },
        "invite_results": invite_results,
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if out["ok"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
