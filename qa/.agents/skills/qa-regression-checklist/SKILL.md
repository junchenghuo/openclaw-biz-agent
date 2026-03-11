---
name: qa-regression-checklist
description: 回归测试清单技能：生成版本回归与冒烟清单。
---

# 用途
- 稳定版本发布质量，避免漏测。

# 触发关键词
- 回归测试
- 冒烟测试
- 发布验证
- 测试清单

# 标准流程
1. 按模块生成回归范围。
2. 定义核心链路冒烟用例。
3. 标注自动化与手工边界。
4. 输出发布前后检查项。

# 输出产物
- regression-checklist.md
- smoke-checklist.md
- release-test-note.md

# 约束
- 优先使用本地文件与离线流程，不调用付费 API。
- 不要求任何额外 KEY（如 OPENAI_API_KEY、第三方云厂商 KEY）。
