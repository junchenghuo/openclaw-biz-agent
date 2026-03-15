---
name: ui-hd-visual-spec
description: UI 高清精致图技能：生成高分辨率视觉稿规范（本地 SVG/PNG 流程）。
---

# 用途
- 保证视觉产出清晰、可切图、可复用。

# 触发关键词
- 高清图
- 视觉稿
- 精致图
- UI 图

# 标准流程
1. 定义画布尺寸、栅格、色彩与字体系统。
2. 输出组件视觉规范与状态样式。
3. 生成本地 SVG 导出策略与命名规范。
4. 给出多分辨率切图建议（1x/2x/3x）。

# 输出产物
- ui-visual-spec.md
- asset-export-guide.md
- color-typography-token.md

# 约束
- 优先使用本地文件与离线流程，不调用付费 API。
- 不要求任何额外 KEY（如 OPENAI_API_KEY、第三方云厂商 KEY）。
