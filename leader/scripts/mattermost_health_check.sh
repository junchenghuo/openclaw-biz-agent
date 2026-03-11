#!/usr/bin/env bash
set -euo pipefail

CHANNEL_ID="${MATTERMOST_TEAM_CHANNEL_ID:-4odsfctn8trymycthdk9qafqjr}"
ALERT_ACCOUNT="${MATTERMOST_ALERT_ACCOUNT:-pm}"

STATUS_OUT="$(openclaw channels status --probe 2>&1 || true)"
MM_LINES="$(printf '%s\n' "$STATUS_OUT" | rg '^- Mattermost ' || true)"

if [ -z "$MM_LINES" ]; then
  MSG="【郑吒-Team Leader】Mattermost 巡检异常：未发现 Mattermost 账号状态。请检查 gateway/mattermost 配置。"
  openclaw message send --channel mattermost --account "$ALERT_ACCOUNT" --target "channel:${CHANNEL_ID}" --message "@admin ${MSG}" >/dev/null 2>&1 || true
  echo "ALERT_NO_MATTERMOST_LINES"
  exit 1
fi

BAD_LINES="$(printf '%s\n' "$MM_LINES" | rg -v 'works$' || true)"
if [ -n "$BAD_LINES" ]; then
  MSG="【郑吒-Team Leader】Mattermost 巡检异常：\n${BAD_LINES}\n请立即处理连接异常（token/baseUrl/账号成员关系）。"
  openclaw message send --channel mattermost --account "$ALERT_ACCOUNT" --target "channel:${CHANNEL_ID}" --message "@admin ${MSG}" >/dev/null 2>&1 || true
  echo "ALERT_MATTERMOST_ACCOUNTS"
  exit 1
fi

echo "NO_REPLY"
