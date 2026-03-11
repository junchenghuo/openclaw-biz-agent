# Project Overview

- Name: 雅江 HR 项目（前端 Vue2 升级 Vue3）
- Goal: 在不影响核心业务可用性的前提下，完成 HR 前端从 Vue2 到 Vue3 的平滑迁移并具备可回滚能力。
- KPI / Acceptance:
  - 核心业务流程可用率 100%
  - P1 缺陷为 0
  - 首屏性能不劣于现网，目标提升 ≥10%
  - 构建耗时目标下降 ≥20%
- Non-goals:
  - 本期不做大规模新功能开发
  - 本期不做全量 UI 改版
  - 本期不做后端协议重构（仅兼容修复）

# Technical Constraints

- Stack: Vue3 + Vue Router（Vue3 版本）+ 状态管理（Vue3 对应版本）
- Runtime environments: dev / staging / prod
- Security / compliance requirements: 发布可回滚、关键日志可观测、灰度可控

# Delivery Plan

- Milestones:
  - M1 迁移方案冻结（架构）
  - M2 公共层迁移完成（前端）
  - M3 核心页面迁移+联调完成（前后端）
  - M4 回归通过并上线（测试/运维）
- Current version: v0.2.0-planning
- Current phase: planning

# Collaboration Rules

- `projects/yajiang-hr-vue3-upgrade/` 是该项目的唯一事实来源。
- 执行前先阅读 `plan/PROJECT.md`、`plan/TASKS.json`、`plan/STATE.json`，再开始角色任务。
- 任何重大范围/架构变更必须记录在 `decisions/DECISIONS.md` 并同步郑吒。
- 对外交付需登记在 `deliverables/ARTIFACTS.md`。

# Canonical Absolute Paths

- Project root: `/Users/imac/midCreate/openclaw-workspaces/ai-team/projects/yajiang-hr-vue3-upgrade`
- Project overview: `/Users/imac/midCreate/openclaw-workspaces/ai-team/projects/yajiang-hr-vue3-upgrade/plan/PROJECT.md`
- Tasks file: `/Users/imac/midCreate/openclaw-workspaces/ai-team/projects/yajiang-hr-vue3-upgrade/plan/TASKS.json`
- Decisions file: `/Users/imac/midCreate/openclaw-workspaces/ai-team/projects/yajiang-hr-vue3-upgrade/decisions/DECISIONS.md`
- Artifacts file: `/Users/imac/midCreate/openclaw-workspaces/ai-team/projects/yajiang-hr-vue3-upgrade/deliverables/ARTIFACTS.md`
- State file: `/Users/imac/midCreate/openclaw-workspaces/ai-team/projects/yajiang-hr-vue3-upgrade/plan/STATE.json`
