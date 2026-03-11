# ARCH_LOGIN（TASK-002）

- Task: TASK-002 Login: architecture and API design  
- Owner: arch  
- Date: 2026-03-05  
- Inputs:  
  - `/Users/imac/midCreate/openclaw-workspaces/ai-team/projects/yajiang-hr-vue3-upgrade/product/PRD_LOGIN.md`  
  - `/Users/imac/midCreate/openclaw-workspaces/ai-team/projects/yajiang-hr-vue3-upgrade/decisions/DECISIONS.md`（已确认安全基线）
- Outputs:  
  - `/Users/imac/midCreate/openclaw-workspaces/ai-team/projects/yajiang-hr-vue3-upgrade/architecture/ARCH_LOGIN.md`  
  - `/Users/imac/midCreate/openclaw-workspaces/ai-team/projects/yajiang-hr-vue3-upgrade/tech/backend/OPENAPI.yaml`

---

## 1. 目标与范围映射（对齐 PRD）

### 1.1 本期目标
提供账号密码登录最小闭环：
1. 登录页提交账号+密码。
2. 后端认证通过后建立会话。
3. 认证失败外显统一文案“账号或密码错误”。
4. 满足已确认安全基线（HTTPS、密码安全存储、限流锁定、会话安全、分层错误码、最小监控与日志脱敏）。

### 1.2 非目标（本期不含）
- 注册、忘记密码、MFA、第三方登录、复杂风控策略。

---

## 2. 逻辑架构

## 2.1 组件
1. **Client（Web）**
   - 登录表单校验（空值不发请求）。
   - 调用 `/v1/auth/login`。
2. **API 服务（Auth 模块）**
   - 入参校验。
   - 认证逻辑、限流、锁定判断。
   - 会话创建/销毁。
3. **User Store（用户表）**
   - 存储账号标识、密码哈希、盐、锁定状态。
4. **Session Store（会话存储，可DB/Redis）**
   - 存储 session_id、user_id、过期时间、创建来源。
5. **Rate Limit Store（Redis 优先）**
   - 基于账号+IP 计数，触发短时锁定。
6. **Observability（日志+指标）**
   - 最小指标：成功率、失败率、锁定次数、429 次数、耗时。
   - 日志脱敏：账号掩码、IP 截断/哈希、不记明文密码。

## 2.2 请求流程（登录）
1. Client 发起 `POST /v1/auth/login`（仅 HTTPS）。
2. 网关/API 校验 TLS；非 HTTPS 拒绝（生产环境）。
3. Auth 校验入参格式。
4. 检查限流与锁定：
   - 若触发，返回 429（统一外显文案），内部错误码 `AUTH_RATE_LIMITED` 或 `AUTH_TEMP_LOCKED`。
5. 按账号查用户，执行密码校验（Argon2id/bcrypt + salt + pepper）。
6. 失败则增加失败计数，必要时进入短时锁定。
7. 成功则清失败计数，创建会话并写入安全 Cookie。
8. 返回成功响应（含用户基础信息，不含敏感字段）。

---

## 3. 关键设计决策（已落地）

### 3.1 生产强制 HTTPS
- 生产仅允许 HTTPS。
- 如部署在反向代理后，要求可信 `X-Forwarded-Proto=https` 校验。
- 结合 HSTS（建议）降低降级风险。

### 3.2 密码存储
- 算法：**Argon2id 优先**，兼容 bcrypt。
- 存储结构：
  - `password_hash`（含算法参数）
  - `salt`（每用户唯一）
  - `pepper_version`（用于轮换）
- pepper 存于 KMS/环境密钥管理，不落库。
- 登录校验统一常量时间比较，降低时序泄露风险。

### 3.3 登录限流 + 短时锁定
- 限流维度建议：
  - IP 维度（全局）
  - 账号+IP 维度（精细）
- 触发策略（建议默认）：
  - 连续失败 5 次锁定 10 分钟。
  - 超过阈值返回 429。
- 锁定期间统一外显失败文案，不暴露状态细节。

### 3.4 会话安全
- Cookie 会话：`HttpOnly` + `Secure` + `SameSite=Lax`（跨站需求再评估 None+CSRF）。
- Session ID 使用高熵随机值。
- 登录成功后必须重建 session（防会话固定攻击）。
- 提供 `POST /v1/auth/logout` 主动失效会话。

### 3.5 错误处理分层
- **外显文案统一**：`账号或密码错误`（认证失败/锁定/账号不存在均统一）。
- **内部错误码分层**：
  - `AUTH_INVALID_CREDENTIALS`
  - `AUTH_RATE_LIMITED`
  - `AUTH_TEMP_LOCKED`
  - `AUTH_SESSION_INVALID`
  - `AUTH_BAD_REQUEST`
- 对前端返回标准化 `error.code`，但 UI 文案统一。

### 3.6 最小监控与日志脱敏
- 指标：
  - `auth_login_attempt_total{result}`
  - `auth_login_latency_ms`
  - `auth_lock_total`
  - `auth_rate_limit_total`
- 日志字段：`trace_id`, `result`, `error_code`, `account_masked`, `ip_hash`。
- 禁止记录：明文密码、完整账号、完整 IP、完整 Cookie。

---

## 4. 数据模型（最小集合）

### 4.1 users
- `id` (uuid)
- `account` (varchar unique)
- `password_hash` (text)
- `salt` (varchar)
- `pepper_version` (varchar)
- `status` (active/disabled)
- `failed_attempts` (int)
- `locked_until` (timestamp nullable)
- `last_login_at` (timestamp nullable)
- `created_at`, `updated_at`

### 4.2 sessions
- `id` (uuid 或随机 token 主键)
- `user_id` (uuid)
- `expires_at` (timestamp)
- `created_at`
- `last_seen_at`
- `ip_hash` (nullable)
- `user_agent_hash` (nullable)
- `revoked_at` (nullable)

---

## 5. API 设计摘要

- `POST /v1/auth/login`：登录并建立会话。
- `POST /v1/auth/logout`：登出并销毁当前会话。
- `GET /v1/auth/session`：查询当前登录态（供前端刷新页面判定）。

详细草案见：`/Users/imac/midCreate/openclaw-workspaces/ai-team/be/api/OPENAPI.yaml`

---

## 6. 可测试验收点（面向 TASK-002 交付）

1. **HTTPS 强制**
   - 生产环境 HTTP 请求被拒绝或 301 到 HTTPS；`Secure` Cookie 仅 HTTPS 下发送。
2. **密码存储安全**
   - 数据库中看不到明文密码；可见 hash+salt；pepper 不在库中。
3. **统一错误文案**
   - 账号不存在/密码错误/锁定中，前端统一显示“账号或密码错误”。
4. **限流与锁定**
   - 连续失败达到阈值后返回 429 或锁定码；在锁定窗口内持续失败且不泄露细节。
5. **会话安全属性**
   - 登录响应 Set-Cookie 包含 `HttpOnly; Secure; SameSite`。
6. **会话有效性**
   - 登录后 `/v1/auth/session` 返回 authenticated=true；登出后失效。
7. **日志脱敏**
   - 日志不含明文密码/完整账号/完整 IP；可按 trace_id 追踪。
8. **最小监控**
   - 成功、失败、锁定、限流指标可被抓取并区分 result 标签。

---

## 7. 灰区与待产品确认

1. **会话 TTL（强相关）**
   - 建议：绝对过期 12h；空闲过期 2h。是否需要“记住我”延长至 7/30 天？
2. **锁定策略参数**
   - 失败阈值、锁定时长是否按用户分层（普通/管理员）？
3. **同账号并发会话数**
   - 是否允许多端同时在线；是否需新登录踢旧会话。
4. **登录成功跳转目标**
   - 固定首页或支持 `return_url` 白名单回跳。
5. **账号字段规范**
   - 账号是否只允许邮箱/用户名之一，是否大小写不敏感。
6. **国际化文案**
   - 是否需要多语言错误提示（当前仅中文）。

---

## 8. 对下游任务影响

- TASK-003（BE）可基于 OpenAPI + 本文安全基线直接实现。
- TASK-004（FE）可按统一错误文案与 session 查询接口接入。
- TASK-005（QA）可直接采用第6节验收点编写自动化用例。
- TASK-006（OPS）需配置 HTTPS、HSTS、日志脱敏、指标采集。
