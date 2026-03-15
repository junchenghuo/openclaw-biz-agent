---
name: leader-project-channel-bootstrap
description: Leader 立项后频道引导技能。用于郑吒（pm/@bot-leader）在收到 admin 已确认立项后，立即创建项目频道并先邀请 @admin，然后细化项目与WBS，再邀请项目成员并按优先级分派任务。
---

# leader-project-channel-bootstrap

仅在“admin 已确认立项”之后执行，按以下顺序不可跳步。

执行前置：
- 创建频道与首批必邀 3 人必须先调用 `leader-channel-create-invite` 技能。
- 若未调用该技能，不得进入本技能后续步骤。

固定流程要求（强制）：
- 首批成员必须是：`@admin`、`@bot-arch`、`@bot-product`。
- 频道创建后，需求沟通与启动会必须在新频道内进行，不得继续在原频道推进需求细化。
- 在 leader+架构师+产品经理完成项目启动会并确认参与角色前，禁止邀请执行层成员。
- 在 PRD 完成前，禁止派发开发执行任务。
- 在架构设计书完成前，禁止全量下发 WBS。

## 1. 立即创建项目频道（强制）
- 调用 Mattermost：`POST /api/v4/channels`。
- 频道建议命名：`proj-<projectCode>-<yyyymmdd>`。
- 频道创建成功后，记录 `channelId/channelName/teamId` 到项目主任务 `detail/input`。
- 同步校验项目目录根路径必须是 `/Users/imac/midCreate/openclaw-workspaces/ai-team/projects/`；越界即停止后续步骤。
- 未返回 `channelId` 视为创建失败，不得进入后续步骤。

频道创建后首发消息（强制）：
- 必须在新频道立即发送启动消息并 `@admin @bot-product @bot-arch`。
- 启动消息至少包含：项目名称、channelId、下一步（启动会时间/议题）。
- 发送后必须回写可核对证据：`startupPostId`（或 messageId）+ `channelId` + `@提及名单`。
- 若未拿到 `startupPostId`，流程状态必须标记为 `blocked（项目群首发消息缺证据）`，禁止进入后续派单。

## 2. 首批必邀 3 人（强制）
- 必须先邀请：`admin`、`@bot-arch`、`@bot-product`。
- 三者全部到位前，不得进入任何执行派单动作。
- 调用：`POST /api/v4/channels/{channel_id}/members`，body `{"user_id":"<admin_user_id>"}`。
- 若邀请失败，立即回执失败原因并暂停后续流程。
- 回执必须包含每个邀请对象的执行结果（status code）。

## 3. 项目启动会与参与角色确认（强制）
- 由 `@bot-leader` + `@bot-arch` + `@bot-product` 发起项目启动会。
- 在会议中确认：项目参与角色清单、阶段目标、依赖边界。
- 启动会结论必须落会议纪要并写回任务中台。
- 启动会后第一个执行任务必须派给 `@bot-product`（PRD+原型图），不得派给 `admin`。
- 启动会前置门禁：必须先校验“项目群首发消息证据”存在（`startupPostId` 可查），否则会议与派单均不得开始。

## 4. 文档先行（强制）
- 第一步：产品经理先输出 PRD + 产品原型图（两项必需）。
- 第二步：架构师基于 PRD+原型图输出架构四件套：
  - 技术架构说明书
  - 整体架构流程图
  - API 接口协议
  - 中间件与数据库使用说明
- 文档未完成前不得推进执行层派单。

## 5. 邀请项目成员（强制）
- 按 WBS owner 反推出所需成员，邀请进入项目频道。
- 支持批量：`POST /api/v4/channels/{channel_id}/members`，body `{"user_ids":[...]}`。
- 邀请完成后回执“成员到位清单”。

成员到位校验（强制门禁）：
- 派单前必须执行 `GET /api/v4/channels/{channel_id}/members` 并核对 required list。
- required list 至少包含：`@admin` + 本轮 WBS 对应 owner 机器人。
- 若存在未到位成员，流程必须停在“待补齐成员”状态，禁止进入第 5 步派单。
- 未到位回执模板：`成员未到位，暂停派单。缺失：@bot-fe/@bot-be...；已执行补邀。`

## 6. 频道内按优先级派单（强制）
- 在项目频道 `@` 对应成员，按 `P0 -> P1 -> P2` 顺序分派。
- 派单必须带：任务编号、目标、输入、输出、截止时间、ACK要求。
- 持续跟进直到每个任务有 `done/blocked` 明确状态。
- 仅在第 4 步校验通过（成员全部在频道）后才允许执行。
- 若入口来自私聊，执行派单前必须确认“已在项目频道首发启动消息”；否则禁止派单。
- 首个执行任务门禁：创建任务后必须立即核对首条执行任务 owner=`楚轩（product）`/`@bot-product`，不符合则立即修正并回执。

多人任务约束：
- WBS 涉及多个责任人时，必须逐人建任务，禁止只创建 1 条总任务。
- 派单消息需附任务编号清单，确保 owner 与任务一一对应。

## 7. 失败与回滚
- 任一步失败都要回执：失败点、错误原文、修复动作、是否可重试。
- 创建频道成功但后续失败时，保留频道并标记“待修复”，避免上下文丢失。
- 禁止无证据回复“Mattermost 插件禁用”；必须附 `openclaw health` 结果或接口报错原文。
