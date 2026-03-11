---
name: ops-deploy-runbook
description: 运维部署 Runbook 技能：输出部署步骤、回滚方案和值班手册。
---

# 用途
- 标准化发布流程，降低上线风险。

# 触发关键词
- 部署手册
- 回滚方案
- 上线流程
- 值班手册

# 标准流程
1. 确认环境差异与依赖。
2. 输出部署顺序与健康检查命令。
3. 定义失败回滚路径与时限。
4. 生成值班与应急联系人表。

# 输出产物
- deploy-runbook.md
- rollback-plan.md
- oncall-handbook.md

# 约束
- 优先使用本地文件与离线流程，不调用付费 API。
- 不要求任何额外 KEY（如 OPENAI_API_KEY、第三方云厂商 KEY）。
