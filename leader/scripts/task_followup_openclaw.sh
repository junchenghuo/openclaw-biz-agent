#!/usr/bin/env bash
set -euo pipefail

OPENCLAW_BIN="${OPENCLAW_BIN:-openclaw}"
TASK_API_BASE="${TASK_API_BASE:-http://127.0.0.1:18080}"
MM_CHANNEL_ID="${MM_CHANNEL_ID:-ycg5rgtpobdoxnrib5ezfgj15o}"
MM_ACCOUNT_ID="${MM_ACCOUNT_ID:-pm}"
MM_TARGET="channel:${MM_CHANNEL_ID}"

LOCK_DIR="${TMPDIR:-/tmp}/openclaw-task-followup.lock"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  exit 0
fi
trap 'rmdir "$LOCK_DIR"' EXIT

payload="$(curl -fsS "${TASK_API_BASE}/api/tasks")"
message="$((printf '%s' "$payload") | python3 - <<'PY'
import datetime
import json
import re
import sys

raw = sys.stdin.read().strip()
if not raw:
    print("")
    raise SystemExit(0)

data = json.loads(raw)
tasks = data.get("data") or []
unfinished = [
    t for t in tasks if str(t.get("status") or "").upper() not in {"COMPLETED", "CANCELLED"}
]

if not unfinished:
    print("")
    raise SystemExit(0)

role_to_handle = {
    "leader": "@bot-leader",
    "pm": "@bot-leader",
    "product": "@bot-product",
    "arch": "@bot-arch",
    "fe": "@bot-fe",
    "be": "@bot-be",
    "qa": "@bot-test",
    "test": "@bot-test",
    "ops": "@bot-ops",
    "ui": "@bot-ui",
    "ai": "@bot-ai",
}

name_to_handle = {
    "郑吒": "@bot-leader",
    "楚轩": "@bot-product",
    "萧宏律": "@bot-arch",
    "罗甘道": "@bot-fe",
    "罗应龙": "@bot-be",
    "詹岚": "@bot-test",
    "张杰": "@bot-ops",
    "铭烟薇": "@bot-ui",
    "赵樱空": "@bot-ai",
}

def resolve_handle(owner_name: str) -> str:
    if not owner_name:
        return "@bot-leader"

    role_match = re.search(r"[（(]([^）)]+)[）)]", owner_name)
    if role_match:
        role = role_match.group(1).strip().lower()
        if role in role_to_handle:
            return role_to_handle[role]

    clean_name = re.sub(r"[（(].*?[）)]", "", owner_name).strip()
    return name_to_handle.get(clean_name, "@bot-leader")

timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
lines = [
    f"@bot-leader [任务巡检 {timestamp}] 当前有 {len(unfinished)} 个未完成任务，请责任人更新进展："
]

max_items = 20
for task in unfinished[:max_items]:
    owner = task.get("ownerName") or "未指派"
    handle = resolve_handle(owner)
    task_code = task.get("taskCode") or "(no-code)"
    status = task.get("status") or "UNKNOWN"
    title = task.get("title") or "(无标题)"
    lines.append(f"- {handle} 跟进 `{task_code}`（{status}）《{title}》")
    lines.append("  有产出请更新 output/detail；若阻塞或失败请记录原因并 @bot-leader。")

if len(unfinished) > max_items:
    lines.append(f"- 其余 {len(unfinished) - max_items} 项请继续在任务中心跟进。")

print("\n".join(lines))
PY
)"

if [ -z "$message" ]; then
  exit 0
fi

"$OPENCLAW_BIN" message send \
  --channel mattermost \
  --account "$MM_ACCOUNT_ID" \
  --target "$MM_TARGET" \
  --message "$message"
