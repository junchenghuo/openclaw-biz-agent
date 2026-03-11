# Tasks 目录说明

- 非项目类工作统一登记在 `TASKS.csv`，字段：`id,title,type,start_date,end_date,status,initiator,owner,progress,notes`。
- `type` 取 `task` 或 `incident` 等自定义标签；`progress` 使用百分比（如 `0%/50%/100%`）。
- 行为要求：
  1. 只有在用户明确“不立项”时才使用此表。
  2. 创建/更新记录需由郑吒确认；其他角色只在 `notes` 中补充信息。
  3. 产物仍应存在于责任人目录或公共位置，并写入 `notes` 绝对路径。
- 如任务升级为项目，应在 `notes` 中标记“升级为 <project>`，并在 `projects/` 下创建对应目录后关闭该记录。
