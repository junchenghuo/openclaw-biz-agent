---
name: be-openapi-contract-kit
description: 后端接口契约技能：产出 OpenAPI 契约和联调说明。
---

# 用途
- 让前后端并行开发，减少接口反复。

# 触发关键词
- OpenAPI
- 后端接口
- 联调
- 接口契约

# 标准流程
1. 定义接口列表、鉴权、分页、过滤。
2. 给出请求响应 schema 与示例。
3. 定义错误码与异常处理。
4. 输出联调顺序和 Mock 建议。

# 输出产物
- openapi.yaml 草案
- backend-api-guide.md
- integration-checklist.md

# 约束
- 优先使用本地文件与离线流程，不调用付费 API。
- 不要求任何额外 KEY（如 OPENAI_API_KEY、第三方云厂商 KEY）。
