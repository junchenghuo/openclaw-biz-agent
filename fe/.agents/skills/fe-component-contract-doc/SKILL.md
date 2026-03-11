---
name: fe-component-contract-doc
description: 前端组件契约技能：规范 Props、事件、样式覆盖与示例。
---

# 用途
- 减少组件使用歧义，提升复用率。

# 触发关键词
- 组件文档
- props
- 事件
- 前端契约

# 标准流程
1. 定义组件 API（Props/Events/Slots）。
2. 给出边界行为与默认值。
3. 补充样式覆盖与主题策略。
4. 输出示例与反例。

# 输出产物
- component-contract.md
- usage-examples.md
- edge-case-note.md

# 约束
- 优先使用本地文件与离线流程，不调用付费 API。
- 不要求任何额外 KEY（如 OPENAI_API_KEY、第三方云厂商 KEY）。
