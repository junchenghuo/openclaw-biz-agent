---
name: ui-design-token-system
description: UI 设计 Token 技能：构建颜色/间距/字号/圆角 Token。
---

# 用途
- 让设计与前端代码对齐，减少返工。

# 触发关键词
- design token
- 颜色规范
- 字号规范
- 间距规范

# 标准流程
1. 提取基础 token（color/space/radius/type）。
2. 建立语义 token（primary/success/warning）。
3. 定义组件级 token 映射策略。
4. 输出 token 变更与版本规则。

# 输出产物
- design-tokens.json 结构说明
- token-mapping.md
- 组件 token 对照表

# 约束
- 优先使用本地文件与离线流程，不调用付费 API。
- 不要求任何额外 KEY（如 OPENAI_API_KEY、第三方云厂商 KEY）。
