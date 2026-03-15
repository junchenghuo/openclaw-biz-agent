---
name: ai-prompt-eval-kit
description: AI 提示词评测技能：构建离线评测集与对比报告。
---

# 用途
- 不依赖外部付费服务即可评估提示词质量。

# 触发关键词
- 提示词评测
- 评测集
- A/B 对比
- AI 质量

# 标准流程
1. 定义任务目标与评分维度。
2. 构建离线样例集与期望输出。
3. 执行 A/B 对比并记录结果。
4. 输出改进建议与下一轮计划。

# 输出产物
- prompt-eval-dataset.md
- eval-report.md
- iteration-plan.md

# 约束
- 优先使用本地文件与离线流程，不调用付费 API。
- 不要求任何额外 KEY（如 OPENAI_API_KEY、第三方云厂商 KEY）。
