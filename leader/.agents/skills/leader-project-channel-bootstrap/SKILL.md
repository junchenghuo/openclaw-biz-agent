---
name: leader-project-channel-bootstrap
description: Leader 立项后频道引导技能。用于郑吒（pm/@bot-leader）在收到 admin 已确认立项后，立即创建项目频道并先邀请 @admin，然后细化项目与WBS，再邀请项目成员并按优先级分派任务。
---

# leader-project-channel-bootstrap

仅在“admin 已确认立项”之后执行，按以下顺序不可跳步。

## 1. 立即创建项目频道（强制）
- 调用 Mattermost：`POST /api/v4/channels`。
- 频道建议命名：`proj-<projectCode>-<yyyymmdd>`。
- 频道创建成功后，记录 `channelId/channelName/teamId` 到项目主任务 `detail/input`。

## 2. 先邀请 admin（强制）
- 先邀请 `admin` 入频道，再进行任何WBS派单动作。
- 调用：`POST /api/v4/channels/{channel_id}/members`，body `{"user_id":"<admin_user_id>"}`。
- 若邀请失败，立即回执失败原因并暂停后续流程。

## 3. 细化项目与 WBS（强制）
- 在 `openclaw-task` 中完善项目主任务：目标、范围、里程碑、风险、验收标准。
- 生成 WBS，每条至少包含：优先级、owner、输出、截止时间。

## 4. 邀请项目成员（强制）
- 按 WBS owner 反推出所需成员，邀请进入项目频道。
- 支持批量：`POST /api/v4/channels/{channel_id}/members`，body `{"user_ids":[...]}`。
- 邀请完成后回执“成员到位清单”。

## 5. 频道内按优先级派单（强制）
- 在项目频道 `@` 对应成员，按 `P0 -> P1 -> P2` 顺序分派。
- 派单必须带：任务编号、目标、输入、输出、截止时间、ACK要求。
- 持续跟进直到每个任务有 `done/blocked` 明确状态。

## 6. 失败与回滚
- 任一步失败都要回执：失败点、错误原文、修复动作、是否可重试。
- 创建频道成功但后续失败时，保留频道并标记“待修复”，避免上下文丢失。
