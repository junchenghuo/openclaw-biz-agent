---
name: arch-system-diagram-mermaid
description: 架构图技能：生成系统架构图、部署图、时序图（Mermaid）。
---

# 用途
- 低成本产出标准架构图，便于评审与协作。

# 触发关键词
- 架构图
- 系统图
- 时序图
- 部署图

# 标准流程
1. 梳理业务域、服务边界、依赖关系。
2. 输出 C4/部署/时序三类 Mermaid 图。
3. 标注数据流、鉴权链路和故障域。
4. 补充容量与扩展建议。

# 输出产物
- architecture-diagram.md
- service-boundary.md
- capacity-note.md

# 约束
- 优先使用本地文件与离线流程，不调用付费 API。
- 不要求任何额外 KEY（如 OPENAI_API_KEY、第三方云厂商 KEY）。
