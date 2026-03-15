---
name: leader-skills-audit
description: Leader 技能审计技能：定期核查角色技能缺口并输出补齐计划。
---

# 触发关键词
- 技能审计
- 技能缺口
- 能力盘点
- 技能补齐

# 标准流程
1. 读取各角色 AGENTS.md 与当前 .agents/skills 清单。
2. 按岗位职责识别缺失的必备技能与优先级。
3. 输出补齐计划（技能名、收益、安装顺序、风险）。
4. 更新 log/skilsLog 形成可追溯记录。

# 输出产物
- skills-gap-report.md
- skills-install-plan.md

# 约束
- 优先使用本地文件和离线流程。
- 不依赖任何付费 API 与额外 KEY。
