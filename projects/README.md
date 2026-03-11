# Projects 目录说明

- 每个获批项目占用一个独立子目录：`projects/<slug>/`。
- 目录内需至少包含：
  - `plan/`：项目概览、计划、任务分解、状态。
  - `meetings/`：会议纪要与沟通记录。
  - `decisions/`：决策日志。
  - `deliverables/`：最终交付索引与文件（含 PRD/PPT/代码包等）。
  - `product/`、`architecture/`、`tech/frontend|backend|ai/`、`qa/`、`ops/`：角色专属设计与说明。
- 立项流程：Leader 必须先询问用户是否立项；仅在得到“立项”回复后创建新目录并记录 `plan/PROJECT.md`。
- 非项目类工作一律登记在 `/Users/imac/midCreate/openclaw-workspaces/ai-team/tasks/TASKS.csv`，不得混入项目目录。
