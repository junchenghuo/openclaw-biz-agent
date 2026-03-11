# Decisions (ADR Style)

Record high-impact decisions here.

## Template

### ADR-XXXX: <Title>
- Date: YYYY-MM-DD
- Status: proposed | accepted | superseded
- Context:
- Decision:
- Consequences:
- Affected tasks:

### ADR-20260305-LOGIN-DEMO: 登录页面先交付纯前端演示版
- Date: 2026-03-05
- Status: accepted
- Context: 当前需求为快速展示登录页面效果，不要求数据库与后端联调。
- Decision: 先交付 Glassmorphism 风格（C）的纯前端登录页面，包含基础输入校验与成功提示。
- Consequences: 可快速演示 UI 与交互；后续如需真实认证，再新增架构与后端任务。
- Affected tasks: TASK-007

### ADR-20260305-LOGIN-MVP-SCOPE: 登录MVP仅支持账号密码
- Date: 2026-03-05
- Status: accepted
- Context: 产品负责人确认“只做简单的账号密码登录即可”，需尽快解锁架构与研发任务。
- Decision: TASK-001 的PRD范围限定为账号+密码登录；短信验证码、第三方登录、忘记密码、注册、风控与MFA均不纳入本期。
- Consequences: 交付速度更快、实现复杂度更低；后续如需扩展登录能力，需要新增需求与架构变更。
- Affected tasks: TASK-001, TASK-002, TASK-003, TASK-004, TASK-005, TASK-006

### ADR-20260305-LOGIN-SECURITY-BASELINE: 登录MVP安全基线纳入TASK-002必做
- Date: 2026-03-05
- Status: accepted
- Context: 架构风险评估显示，若仅按“最小登录闭环”实现而缺少安全基线，将显著增加账号被撞库/会话劫持/不可观测等风险。
- Decision: 将以下能力纳入TASK-002必做范围：生产强制HTTPS、密码安全存储（Argon2id/bcrypt+salt+pepper）、登录限流与短时锁定、会话安全属性（HttpOnly/Secure/SameSite或等价控制）、统一外显错误+内部错误码、最小监控与日志脱敏。
- Consequences: TASK-002设计工作量上升但可显著降低高风险安全隐患；TASK-003/TASK-005可按该基线直接实现与验证。
- Affected tasks: TASK-002, TASK-003, TASK-005, TASK-006

### ADR-20260306-YAJIANG-HR-VUE3-MIGRATION: 雅江HR前端升级采用“先方案后迁移”的分阶段执行
- Date: 2026-03-06
- Status: accepted
- Context: 用户要求启动雅江HR项目，并将前端从Vue2升级到Vue3。为降低迁移风险，需要先冻结架构方案与技术基线，再推进开发与回归。
- Decision: 新增任务链 TASK-008~TASK-013，执行顺序为：PRD -> 架构方案 -> 前后端迁移/兼容 -> 回归测试 -> 发布与回滚。依赖未满足任务统一标记为 blocked。
- Consequences: 能保证迁移过程可追踪、可审计、可回滚；短期任务拆解更细但跨角色协作清晰。
- Affected tasks: TASK-008, TASK-009, TASK-010, TASK-011, TASK-012, TASK-013
