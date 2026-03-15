---
name: be-schema-migration-guard
description: 后端数据库变更守护技能：提供 schema 变更与回滚安全清单。
---

# 触发关键词
- 数据库迁移
- Schema 变更
- 回滚脚本
- 数据安全

# 标准流程
1. 定义迁移前检查（备份、锁影响、容量）。
2. 生成 forward/revert 执行步骤。
3. 给出灰度发布与回滚触发条件。
4. 输出 DBA 审核清单与风险说明。

# 输出产物
- db-migration-runbook.md
- rollback-conditions.md
- dba-review-checklist.md

# 约束
- 优先使用本地文件和离线流程。
- 不依赖任何付费 API 与额外 KEY。
