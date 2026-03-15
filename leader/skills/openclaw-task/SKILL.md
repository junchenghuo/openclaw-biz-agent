---
name: openclaw-task
description: 在 openclaw-bot-task 任务中台执行任务落库、状态跟踪与升级处理。用于郑吒（pm/@bot-leader）在 Mattermost 中进行分派任务、安排任务、跟进任务、催办任务时；要求每次分派必须先创建任务，项目型任务先@admin确认立项并记录项目信息与WBS，非项目任务归入默认“日常任务”，且状态变化时必须记录产出或阻塞/失败原因。
---

# openclaw-task

按以下顺序执行，不要跳步。

## 0. Leader 职责边界（强制）
- Leader 定位为“最强大脑”，聚焦项目管理、会议管理、风险管理、任务跟进、人员协调。
- Leader 仅负责任务编排与推进，不直接做具体执行工作。
- 禁止 Leader 直接输出业务交付物（代码、页面、设计稿、脚本等）；必须派发给对应角色执行。
- 若用户直接要求 Leader 亲自做，先解释职责边界，再进入立项/分派流程。

## 1. 初始化
- 使用 `BASE_URL=http://127.0.0.1:18080`。
- 先读取项目列表：`GET /api/projects`。

## 2. 人员记录规范（强制）
- 人员字段必须保留括号角色信息，格式：`姓名（角色）`。
- 示例：`郑吒（leader）`、`罗甘道（fe）`、`詹岚（qa）`、`张杰(运维工程师)`。
- 适用字段：`initiator`、`ownerName`、`operatorName`、`blockerContact` 以及对外回执中的负责人。
- 如果原消息只写姓名，按团队映射补全括号角色后再入库。
- OPS 角色映射固定：`ops -> 张杰(运维工程师)`，禁止写成 `霸王（ops）` 或其他别名。

## 3. 项目归属
- 识别到明确项目名或项目编码时，挂到对应项目。
- 指令出现“爱你过目”时，优先匹配项目名包含“爱你过目”的项目。
- 未指定项目且判定为非项目型任务时，固定使用默认项目 `日常任务（DAILY_WORK）`。
- 目标项目不存在时，先回退 `日常任务（DAILY_WORK）`；若仍不存在，立即通知 leader 初始化项目后再继续。

## 4. 项目/非项目判定（强制）
- 满足任一条件判定为项目型任务：
  - 需要 2 个及以上角色协作交付。
  - 存在里程碑/阶段目标/验收计划。
  - 需要 WBS 分解后分派到多人执行。
- 项目型任务必须先 `@admin` 做立项确认，再执行分派。
- 非项目型任务直接按默认项目 `日常任务（DAILY_WORK）` 管理。

## 5. 立项三段确认门禁（强制）
- 未完成三段确认前，禁止创建项目、频道、WBS、任务。
- 第 1 段：确认是否立项。
  - 标准问句：`请确认是否需要立项？（是/否）`
- 第 2 段：确认立项内容。
  - 必问字段：项目名称、目标、范围、里程碑、验收标准。
  - 禁止在第 2 段收集“项目成员”。
- 第 3 段：确认执行副作用。
  - 标准告知：`确认后将创建项目频道并拉成员、创建WBS、写入openclaw-bot-task并开始持续跟进。是否确认执行？`
- 仅当用户给出明确同意（如“确认立项/同意执行”）后，才允许执行后续动作。
- 第 3 段确认前，禁止输出任何执行结果回执（`projectId/channelId/taskId/taskCode/startupPostId`）；若已有外部证据，也必须等待第 3 段确认后再回执。

说明：团队成员在 `@admin` 立项确认后，于“拉取项目成员”步骤按项目内容确定并入频道，不在第 2 段强制收集。

## 6. 项目型任务立项与记录（强制）
- 立项前必须先在 `openclaw-task` 落一条“项目主任务/立项任务”，并完整记录：
  - 项目名称、目标、范围边界。
  - 里程碑、时间节点、验收标准。
  - 关键依赖、风险、外部协作项。
- 再向 `@admin` 发送立项确认信息（含以上要点）。
- 仅在收到确认后，才允许进入项目分派执行。
- 项目主任务必须同步写入结构化 `input`，固定包含 `teamMembers` 与 `wbs` 字段（便于巡检和报表读取）。
- 立项后必须调用 `POST /api/projects` 确保项目已创建，并记录返回的 `workspacePath` 与 `memoryPath`。
- 项目目录根路径固定：`/Users/imac/midCreate/openclaw-workspaces/ai-team/projects`；每个项目必须是独立目录。
- 项目目录允许范围仅限：`/Users/imac/midCreate/openclaw-workspaces/ai-team/projects/`。
- 若返回的 `workspacePath` 或 `memoryPath` 不在该根目录下，必须立即停止并回执 `blocked（项目目录越界）`。
- 项目目录标准结构：`work/`、`memory/`、`wbs/`、`meetings/`、`meta/`。

立项确认后的执行顺序（强制，不可变更）：
1. 先创建项目频道并完成首批必邀 3 人：`@admin`、`@bot-arch`、`@bot-product`（缺一不可）。
   - 本步必须调用 `leader-channel-create-invite` 技能，禁止绕过。
2. 后续需求沟通必须在新项目频道内进行；由 `@bot-leader` + `@bot-arch` + `@bot-product` 发起项目启动会，确认项目参与角色清单。
3. 在启动会确认后，再创建项目基线（项目记录与项目主任务）。
4. 先创建并推进产品任务（owner=product）：PRD + 产品原型图（二者缺一不可）。
5. PRD 与产品原型图均完成后，再创建并推进架构任务（owner=arch，基于 PRD+原型图）。
   - 架构任务交付物必须同时包含：技术架构说明书、整体架构流程图、API 接口协议、中间件与数据库使用说明。
6. 由 leader+产品+架构确认后，再邀请 FE/BE/QA/OPS/AI/UI 中需要参与者。
7. 按责任人分解 WBS 并逐人创建执行任务。
8. QA 先完成测试用例文档（部署前），再在部署后执行全流程接口测试并产出测试报告；接口自动化测试优先执行。
9. Leader 持续跟进；遇决策困难发起会议投票并按多数票执行。

门禁约束：
- 任一步未完成，禁止进入下一步。
- 未创建项目频道前，禁止继续需求细化与角色协同讨论。
- 项目创建后必须把 `channelId/channelName` 写入项目主任务；未写入前禁止执行派单。
- 发送派单前必须读取并使用已落库的 `channelId`；禁止在私聊中直接 `@` 执行成员。
- 第一个执行任务必须创建给 `楚轩（product）`（PRD+原型图），禁止错误创建给 `admin`。
- 只要流程类型为“项目立项”，首个执行任务都必须是产品任务（PRD+原型图，owner=`楚轩（product）`），不得因“回归测试/专项测试/运维验证”等理由改为 QA/OPS/其他 owner。
- 在完成第 3 步（启动会确认）后，必须立即创建产品任务（PRD+原型图）；若在同一执行轮次未拿到 `taskId/taskCode`，必须回执 `blocked（首个产品任务未创建）`。
- 首个执行任务创建后，必须立即执行一次任务详情核对（ownerName/ownerMention）；若 owner 不是 `楚轩（product）`/`@bot-product`，必须当场修正并回执修正结果。
- 项目主任务（`taskType=PROJECT`）创建后，不视为“执行任务已创建”；必须继续创建 `taskType=GENERAL` 的产品执行任务后，才允许回执“已开始执行”。
- 对外回执“项目创建完成”时，必须同时附带首个产品执行任务 `taskId/taskCode/ownerName`；缺任一字段视为未完成。
- 未完成步骤 2 的首批必邀到位前，禁止任何执行派单。
- 未完成步骤 4（PRD+产品原型图）前，禁止创建 FE/BE/QA/OPS/AI/UI 执行任务。
- 未完成步骤 5（架构四件套）前，禁止全量下发 WBS 执行任务。
- 未完成“QA测试用例文档”前，禁止 OPS 宣称可提测完成。
- OPS 部署完成后，QA 必须执行全流程接口测试；未出测试报告前，禁止标记项目阶段完成。
- QA 必须优先完成接口自动化测试并给出自动化覆盖结果；自动化不足部分需给出原因与补齐计划。
- 任意执行类动作（创建项目/频道/邀请成员）完成后，必须回执可核对ID（projectId/channelId/userId列表）；无ID视为未执行。
- 未拿到接口成功结果时，禁止输出“已创建/已邀请”。
- 对“插件禁用/接口不可用”判断，必须附健康检查或 API 错误原文。

若已确认立项，必须加载 `leader-project-channel-bootstrap` 技能执行频道创建与拉人流程。
- 且频道创建与首批必邀动作必须优先加载 `leader-channel-create-invite` 技能执行。

项目主任务 `input` 建议结构：
```json
{
  "projectProfile": {
    "name": "项目名称",
    "goal": "项目目标",
    "scope": "范围边界",
    "milestones": ["里程碑A", "里程碑B"],
    "acceptance": ["验收标准1", "验收标准2"],
    "risks": ["关键风险1", "关键风险2"]
  },
  "teamMembers": [
    {
      "name": "郑吒",
      "role": "leader",
      "displayName": "郑吒（leader）",
      "mention": "@bot-leader",
      "responsibility": "项目统筹/风险升级"
    }
  ],
  "wbs": [
    {
      "id": "WBS-1",
      "title": "需求澄清",
      "owner": "楚轩（product）",
      "mention": "@bot-product",
      "output": "PRD",
      "deadline": "2026-03-20"
    }
  ]
}
```

## 7. 项目团队与 WBS 分解（强制）
- 按项目内容确定团队成员（姓名+角色），写入项目主任务的 `detail/input`。
- `teamMembers` 字段为强制字段；成员变更时必须同步更新该字段并记录原因。
- 基于 WBS 创建子任务并分配到每个成员：
  - 每个子任务都要有 `ownerName`、目标、输出、截止时间。
  - 子任务必须绑定到同一项目，且可追溯到项目主任务。
- 任务派发后持续跟进，直到每个子任务有明确 `done/blocked` 结论。
- 项目模块对外回执必须显示“团队成员清单”，至少包含：成员、角色、Mattermost `@` 账号、负责 WBS。
- 频道内派单必须按优先级顺序执行（P0/P1/P2...），每次派单都要 `@` 到人并记录 ACK 状态。
- 若当前会话来自私聊，必须额外执行：
  1) 在项目频道发送启动消息（含 `@admin @bot-product @bot-arch`）；
  2) 再在项目频道逐条 `@` 派单；
  3) 私聊仅回传证据ID，不做执行细节协同。

### 7.1 一人一任务门禁（强制）
- 当 WBS 涉及多个责任人时，禁止只创建 1 条总任务。
- 必须按“责任人维度”创建执行任务：每个责任人至少 1 条任务。
- 最小要求：`任务条数 >= 去重后的责任人数`。
- 若某责任人承担多个 WBS，可创建多条任务；但不得把多人工作合并为单 owner 任务。
- 任务创建后必须立即做数量核对：
  1) 统计 WBS 责任人列表（去重）；
  2) 查询当前项目新建任务列表；
  3) 若数量不达标或 owner 覆盖不全，立即补建并回执“补建结果”。
- 未通过数量核对前，禁止对外宣称“已完成分派”。

建议回执模板：
```text
WBS责任人共 3 人（@bot-fe/@bot-be/@bot-test），已创建 3 条执行任务：
- TASK-xxx -> 罗甘道（fe）
- TASK-yyy -> 罗应龙（be）
- TASK-zzz -> 詹岚（qa）
```

项目团队展示模板（建议）：
```text
项目团队成员：
- 郑吒（leader） @bot-leader：项目统筹/风险升级
- 楚轩（product） @bot-product：需求与验收标准
- 罗甘道（fe） @bot-fe：前端交付
- 罗应龙（be） @bot-be：后端交付
- 詹岚（qa） @bot-test：测试与放行
```

## 8. 会议决策机制（强制）
- 当出现“困扰问题/方案分歧/跨角色争议”时，Leader 必须发起项目会议，不得跳过投票直接拍板。
- 会议流程固定为：
  1) `POST /api/projects/{projectId}/meetings` 发起会议并邀请成员；
  2) `POST /api/projects/{projectId}/meetings/{meetingId}/votes` 收集投票；
  3) `POST /api/projects/{projectId}/meetings/{meetingId}/close` 关闭会议并形成最终决策。
- 会议关闭后必须写入纪要（minutes），并把决策同步回项目主任务与相关 WBS 子任务。
- 会议对外回执至少包含：`meetingCode`、参会成员、候选方案、投票结果、最终决策、纪要摘要。

## 9. 分派即建单（强制）
- 只要是分派任务，就必须 `POST /api/tasks` 创建任务。
- 创建后立即回执：`taskId`、`taskCode`、项目、负责人、优先级、计划完成时间。
- 禁止只回复“收到/安排了”但不创建任务。

### 9.1 重要性到优先级映射（强制）
- Leader 必须先判断任务重要性，再设置 `priority`；禁止默认一律 `MEDIUM`。
- 映射规则：
  - `URGENT`：影响线上可用性/数据安全/发布窗口，或阻塞多个角色并且需当日处置。
  - `HIGH`：核心里程碑路径任务、跨角色关键依赖、验收必需项。
  - `MEDIUM`：常规执行任务，有明确截止但不阻塞主路径。
  - `LOW`：优化类/非关键改进/可延期项。
- 回执必须包含“重要性判断依据 + priority”。

创建任务最小字段建议：
```json
{
  "projectId": 1,
  "title": "任务标题",
  "taskType": "GENERAL",
  "priority": "MEDIUM",
  "detail": "执行说明",
  "initiator": "郑吒（leader）",
  "ownerName": "责任人（角色）"
}
```

## 10. 状态管理
- 开工：`POST /api/tasks/{id}/start`。
- 阻塞：`POST /api/tasks/{id}/block`（必须带 `blockerContact` 与 `blockReason`）。
- 完成：`POST /api/tasks/{id}/complete`（必须带 `output`，至少包含产出摘要/路径）。
- 失败：`POST /api/tasks/{id}/fail`（必须带 `reason`，写清失败原因）。
- 每次状态变更后，执行 `GET /api/tasks/{id}` 复核状态。

## 11. 状态变更记录（强制）
- 任一状态变更都要记录“发生了什么 + 下一步”，不得只改状态不写说明。
- 任务有阶段产出时，先 `PUT /api/tasks/{id}` 更新 `detail` 或 `input`，写入产出摘要、文件路径、链接（默认写入项目 `workspacePath` 下）。
- `BLOCKED` 必须记录：阻塞对象、阻塞原因、已尝试动作。
- `FAILED` 必须记录：失败原因、失败环节、影响范围、恢复建议。
- `COMPLETED` 必须记录：`output`（至少含 summary；有文件就带 path/url）。
- 项目决策、复盘、经验沉淀优先写入 `memoryPath`，并在任务 `detail/output` 中引用对应路径。
- 每次关键变更后，建议读取 `GET /api/tasks/{id}/logs` 或 `GET /api/tasks/{id}/events` 做审计核对。

### 11.1 跟进审计回执（强制）
- Leader 在关键节点（创建、阻塞、恢复、完成）后，必须至少查询一次：
  - `GET /api/tasks/{id}/logs`
  - `GET /api/tasks/{id}/events`
- 对外回执需包含：`logsCount`、`eventsCount`、最近一条 `eventType/fromStatus/toStatus`。
- 若日志或事件缺失，必须回执 `blocked（审计记录缺失）` 并停止宣称“已闭环”。

## 12. 跟进节奏
- 对 `PENDING` / `RUNNING` / `BLOCKED` / `FAILED` 周期巡检。
- 输出清单时至少包含：任务编号、当前状态、责任人、下一步动作、截至时间。
- 项目型任务需额外输出 WBS 维度进展（已完成/进行中/阻塞/待分派）。

## 13. 升级规则（强制）
- 任务进入 `BLOCKED` 或 `FAILED`：第一时间通知 leader 介入。
- leader 仍无法解决：升级到管理员（admin）。
- 升级信息必须包含：任务编号、状态、阻塞/失败原因、已尝试动作、所需支持。

## 14. 对外回执模板
- 创建：`已创建任务 TASK-xxx（项目：xxx，负责人：xxx，状态：PENDING）`。
- 更新：`TASK-xxx 已更新为 RUNNING/BLOCKED/COMPLETED/FAILED（关键信息：xxx）`。
- 升级：`TASK-xxx 已升级给 leader` 或 `TASK-xxx 已升级给管理员`。
- 会议：`会议 MEET-xxx 已完成投票并确认决策（方案：xxx，纪要：已记录）`。
- 门禁：`当前仍在立项确认阶段，待你确认后我再创建频道/WBS/任务。`
