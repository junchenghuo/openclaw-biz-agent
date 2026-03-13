---
name: openclaw-task
description: 在 openclaw-bot-task 任务中台执行任务落库、状态跟踪与升级处理。用于郑吒（pm/@bot-leader）在 Mattermost 中进行分派任务、安排任务、跟进任务、催办任务时；要求每次分派必须先创建任务，未指定项目默认“日常工作”，提到“爱你过目”时挂到对应项目，且状态变化时必须记录产出或阻塞/失败原因。
---

# openclaw-task

按以下顺序执行，不要跳步。

## 1. 初始化
- 使用 `BASE_URL=http://127.0.0.1:18080`。
- 先读取项目列表：`GET /api/projects`。

## 2. 人员记录规范（强制）
- 人员字段必须保留括号角色信息，格式：`姓名（角色）`。
- 示例：`郑吒（leader）`、`罗甘道（fe）`、`詹岚（qa）`。
- 适用字段：`initiator`、`ownerName`、`operatorName`、`blockerContact` 以及对外回执中的负责人。
- 如果原消息只写姓名，按团队映射补全括号角色后再入库。

## 3. 项目归属
- 识别到明确项目名或项目编码时，挂到对应项目。
- 指令出现“爱你过目”时，优先匹配项目名包含“爱你过目”的项目。
- 未指定项目时，固定使用默认项目 `日常工作（DAILY_WORK）`。
- 目标项目不存在时，先回退 `日常工作（DAILY_WORK）`；若仍不存在，立即通知 leader 初始化项目后再继续。

## 4. 分派即建单（强制）
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

## 5. 状态管理
- 开工：`POST /api/tasks/{id}/start`。
- 阻塞：`POST /api/tasks/{id}/block`（必须带 `blockerContact` 与 `blockReason`）。
- 完成：`POST /api/tasks/{id}/complete`（必须带 `output`，至少包含产出摘要/路径）。
- 失败：`POST /api/tasks/{id}/fail`（必须带 `reason`，写清失败原因）。
- 每次状态变更后，执行 `GET /api/tasks/{id}` 复核状态。

## 6. 状态变更记录（强制）
- 任一状态变更都要记录“发生了什么 + 下一步”，不得只改状态不写说明。
- 任务有阶段产出时，先 `PUT /api/tasks/{id}` 更新 `detail` 或 `input`，写入产出摘要、文件路径、链接。
- `BLOCKED` 必须记录：阻塞对象、阻塞原因、已尝试动作。
- `FAILED` 必须记录：失败原因、失败环节、影响范围、恢复建议。
- `COMPLETED` 必须记录：`output`（至少含 summary；有文件就带 path/url）。
- 每次关键变更后，建议读取 `GET /api/tasks/{id}/logs` 或 `GET /api/tasks/{id}/events` 做审计核对。

## 7. 跟进节奏
- 对 `PENDING` / `RUNNING` / `BLOCKED` / `FAILED` 周期巡检。
- 输出清单时至少包含：任务编号、当前状态、责任人、下一步动作、截至时间。

## 8. 升级规则（强制）
- 任务进入 `BLOCKED` 或 `FAILED`：第一时间通知 leader 介入。
- leader 仍无法解决：升级到管理员（admin）。
- 升级信息必须包含：任务编号、状态、阻塞/失败原因、已尝试动作、所需支持。

## 9. 对外回执模板
- 创建：`已创建任务 TASK-xxx（项目：xxx，负责人：xxx，状态：PENDING）`。
- 更新：`TASK-xxx 已更新为 RUNNING/BLOCKED/COMPLETED/FAILED（关键信息：xxx）`。
- 升级：`TASK-xxx 已升级给 leader` 或 `TASK-xxx 已升级给管理员`。
