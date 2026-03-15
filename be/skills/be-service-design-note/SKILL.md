---
name: be-service-design-note
description: 后端服务设计技能：输出服务拆分、数据模型与性能边界说明。
---

# 用途
- 支持可维护、可扩展的后端设计。

# 触发关键词
- 服务设计
- 数据模型
- 性能优化
- 后端方案

# 标准流程
1. 梳理领域模型与服务职责。
2. 给出表结构与索引建议。
3. 定义缓存、队列、重试策略。
4. 输出性能与容量边界。

# 输出产物
- service-design.md
- db-model-note.md
- performance-budget.md

# 约束
- 优先使用本地文件与离线流程，不调用付费 API。
- 不要求任何额外 KEY（如 OPENAI_API_KEY、第三方云厂商 KEY）。
