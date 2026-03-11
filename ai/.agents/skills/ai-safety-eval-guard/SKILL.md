---
name: ai-safety-eval-guard
description: AI 安全评测守护技能：建立风险评测与防护策略。
---

# 触发关键词
- 安全评测
- 越狱测试
- 提示注入
- AI 风险

# 标准流程
1. 定义越狱、注入、敏感输出等风险场景。
2. 构建离线评测集并执行分级评估。
3. 输出防护策略（提示词约束、工具权限、脱敏规则）。
4. 形成上线前 AI 安全门禁结论。

# 输出产物
- ai-safety-eval-report.md
- guardrail-policy.md

# 约束
- 优先使用本地文件和离线流程。
- 不依赖任何付费 API 与额外 KEY。
