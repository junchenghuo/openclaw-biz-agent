---
name: arch-api-development-spec
description: 架构开发说明技能：输出标准接口开发说明书（含契约、错误码、鉴权）。
---

# 用途
- 统一研发接口规范，降低前后端对接成本。

# 触发关键词
- 接口文档
- 开发说明书
- API 规范
- 错误码

# 标准流程
1. 定义资源模型、字段约束、状态码。
2. 输出 OpenAPI 结构与示例请求响应。
3. 定义错误码与重试/幂等策略。
4. 给出版本管理与兼容策略。

# 输出产物
- api-dev-spec.md
- openapi.yaml 模板
- error-code-table.md

# 约束
- 优先使用本地文件与离线流程，不调用付费 API。
- 不要求任何额外 KEY（如 OPENAI_API_KEY、第三方云厂商 KEY）。
