#!/usr/bin/env python3
"""Direct dispatch via Mattermost + spawn (no bus)."""

from __future__ import annotations

import argparse
import subprocess


ROLE_TO_ACCOUNT = {
    "leader": "pm",
    "product": "product",
    "arch": "arch",
    "fe": "fe",
    "be": "be",
    "qa": "qa",
    "ops": "ops",
    "ui": "ui",
    "ai": "ai",
}
ROLE_TO_USERNAME = {
    "leader": "bot-leader",
    "product": "bot-product",
    "arch": "bot-arch",
    "fe": "bot-fe",
    "be": "bot-be",
    "qa": "bot-test",
    "ops": "bot-ops",
    "ui": "bot-ui",
    "ai": "bot-ai",
}


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, capture_output=True, check=False)


def main() -> int:
    parser = argparse.ArgumentParser(description="Dispatch roles without bus")
    parser.add_argument("--to", action="append", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--body", required=True)
    parser.add_argument("--channel-id", default="4odsfctn8trymycthdk9qafqjr")
    args = parser.parse_args()

    roles: list[str] = []
    for role in args.to:
        r = role.strip().lower()
        if r == "pm":
            r = "leader"
        if r not in ROLE_TO_ACCOUNT:
            raise SystemExit(f"Invalid role: {role}")
        if r not in roles:
            roles.append(r)

    for role in roles:
        cp = run(
            [
                "openclaw",
                "agent",
                "--agent",
                "pm",
                "--message",
                f"请立即 /subagents spawn {role} 处理任务：{args.title}。要求：{args.body}",
            ]
        )
        if cp.returncode != 0:
            raise SystemExit(cp.stderr.strip() or cp.stdout.strip())

    mentions = " ".join(f"@{ROLE_TO_USERNAME[r]}" for r in roles)
    announce = (
        f"【郑吒-Team Leader】已派单 {mentions}\n主题：{args.title}\n要求：{args.body}"
    )
    cp = run(
        [
            "openclaw",
            "message",
            "send",
            "--channel",
            "mattermost",
            "--account",
            "pm",
            "--target",
            f"channel:{args.channel_id}",
            "--message",
            announce,
        ]
    )
    if cp.returncode != 0:
        raise SystemExit(cp.stderr.strip() or cp.stdout.strip())

    print("DISPATCH_OK")
    print(f"ROLES={','.join(roles)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
