---
name: leader-channel-create-invite
description: 在 Mattermost 创建项目频道，并强制邀请 admin、产品、架构三位首批成员。
---

# leader-channel-create-invite

用于 Leader 在立项后执行“创建频道 + 首批必邀三人（admin/product/arch）”的固定动作。

## 适用场景
- 已完成立项三段确认并获得执行副作用同意。
- 需要创建项目频道并落地首批成员到位校验。

## 强制规则
- 必须创建新频道后再邀请成员。
- 首批必邀成员固定为：`admin`、`@bot-product`、`@bot-arch`。
- 回执必须包含：`channelId/channelName`、三位成员邀请状态、项目群首条启动消息证据（`startupPostId/messageId`）。
- 任一邀请失败，必须回执失败原因并停止后续流程。
- 若首条启动消息发送失败或无 `startupPostId`，必须回执 `blocked（项目群首发消息缺证据）` 并停止后续流程。

## 执行命令
```bash
python3 {baseDir}/../../../scripts/project_channel_bootstrap.py \
  --project-code <PROJECT_CODE> \
  --display-name "proj-<PROJECT_CODE>" \
  --project-name "<PROJECT_NAME>" \
  --kickoff-next "<启动会时间/议题>"
```

## 成功判定
- 输出 JSON 中：
  - `ok=true`
  - `required_first_three_present=true`
  - `startup_post.ok=true` 且 `startup_post.post_id` 非空
  - `invite_results` 中 admin/arch/product 均为 `ok=true`

## 失败处理
- 若 `ok=false` 或任一必邀成员失败：
  - 直接回执错误原文（status/resp）。
  - 不得宣称“频道已可用”。
