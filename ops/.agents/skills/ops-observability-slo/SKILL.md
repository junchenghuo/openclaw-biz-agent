---
name: ops-observability-slo
description: 可观测性与 SLO 技能：制定指标、告警、阈值与巡检规则。
---

# 用途
- 快速建立可观测体系并可量化服务质量。

# 触发关键词
- SLO
- 告警规则
- 监控指标
- 可观测性

# 标准流程
1. 定义可用性/延迟/错误率指标。
2. 建立告警分级与抑制规则。
3. 配置日志、链路、指标关联策略。
4. 输出周报与复盘模板。

# 输出产物
- slo-dashboard-spec.md
- alert-policy.md
- incident-review-template.md

# 约束
- 优先使用本地文件与离线流程，不调用付费 API。
- 不要求任何额外 KEY（如 OPENAI_API_KEY、第三方云厂商 KEY）。
