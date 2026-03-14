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
- 项目目录标准结构：`work/`、`memory/`、`wbs/`、`meetings/`、`meta/`。

立项确认后的执行顺序（强制）：
1. 创建项目基线：创建项目并创建新的项目频道（记录 channelId）。
2. 先邀请 admin：将 `@admin` 拉入项目频道。
3. 细化并执行：细化 WBS -> 邀请对应成员入频道 -> 在项目频道按优先级 `@` 派单并要求 ACK。

若已确认立项，必须加载 `leader-project-channel-bootstrap` 技能执行频道创建与拉人流程。

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
