---
name: ai-model-solution-note
description: AI 方案说明技能：输出模型选型、推理链路与成本估算（离线模板）。
---

# 用途
- 帮助团队快速形成 AI 落地方案。

# 触发关键词
- 模型方案
- 推理链路
- AI 设计
- 成本估算

# 标准流程
1. 明确场景、输入输出、延迟目标。
2. 给出模型与策略选型依据。
3. 设计推理流程与兜底策略。
4. 输出资源估算与风险项。

# 输出产物
- ai-solution-note.md
- inference-flow.md
- risk-and-cost-note.md

# 约束
- 优先使用本地文件与离线流程，不调用付费 API。
- 不要求任何额外 KEY（如 OPENAI_API_KEY、第三方云厂商 KEY）。
