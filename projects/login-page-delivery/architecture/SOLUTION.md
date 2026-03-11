# 登录页技术方案（前端）+ 接口对齐

> 适用：本地部署环境的「用户名 + 密码」登录页，对接既有后端认证接口。

## 1. 场景与约束

- 目标：快速交付一个稳定的登录页；能正确处理登录成功/失败、加载态、异常提示、登录态保持与退出。
- 约束：
  - 本地部署（可能是 http 非 https）
  - 后端接口已存在（需对齐接口字段、鉴权方式、错误码）
  - 登录页通常是“孤岛页面”，不需要复杂全局状态，但需要可复用的请求层与错误处理约定。

## 2. 推荐前端技术栈（偏“简单可控”）

- 构建：Vite + TypeScript
- UI：任选（Ant Design / Arco / Naive UI / Tailwind）。若无指定：优先 Ant Design（表单/提示现成）。
- 路由：react-router（或 vue-router）
- 状态管理：
  - **首选：不引入重量级全局 store**。登录态（user/token）做成 `authStore` 轻量模块即可。
  - React 可用 Zustand；Vue 可用 Pinia。
- 表单：
  - React：react-hook-form + zod（或 yup）
  - Vue：VeeValidate + zod（或 yup）
- 请求层：axios 或 fetch 封装（建议 axios 便于拦截器处理 token/错误）

> 如果团队已有既定栈（例如 Next.js/Nuxt/umi），直接沿用；本文偏向“最小但工程化”的实现。

## 3. 页面/路由设计

### 3.1 路由

- `/login`：登录页
- `/`：登录后默认页（若本项目只交付登录页，可先跳转到一个占位 `Home` 或回跳 `redirect`）

### 3.2 Redirect 机制

- 进入受保护页面未登录 → 跳 `GET /login?redirect=<encoded>`
- 登录成功后：
  - 若存在 redirect → `navigate(redirect)`
  - 否则 → `navigate('/')`

## 4. 状态管理与登录态

定义统一 Auth 状态（概念上）：

- `isAuthenticated: boolean`
- `user?: { id, name, ... }`（如果后端提供 `/me`）
- `token?: string`（如果采用 Bearer token 方案）

推荐流程：

1) App 启动时执行 `bootstrapAuth()`
- Cookie 模式：直接调用 `/me`，成功则登录态成立；失败则认为未登录
- Token 模式：从存储读取 token → 尝试 `/me` → 失败则清空 token

2) 登录时 `login(username, password)`
- 成功：
  - Cookie 模式：后端 Set-Cookie；前端仅更新 `isAuthenticated` 并拉取 `/me`
  - Token 模式：保存 token（见第 6 节）

3) 退出 `logout()`
- Cookie 模式：调用 `/auth/logout`（后端清 cookie）
- Token 模式：清空本地 token（可选调用后端注销 refresh token）

## 5. 表单校验与交互细节

### 5.1 校验规则（建议）

- username：必填，长度 2~64（或邮箱/手机号正则，按后端约束）
- password：必填，长度 6~128

### 5.2 交互

- 提交时：禁用按钮 + loading
- 错误提示：
  - 表单级：账号/密码错误 → 顶部 Alert 或 toast + 对应字段标红
  - 系统级：网络错误/500 → toast + “请稍后重试”
- 失败后：清空密码（更安全）

## 6. Token / Cookie 处理建议（本地环境优先级）

### 6.1 优先推荐：**HttpOnly Cookie（Session 或 JWT）**

优势：
- 避免 XSS 直接窃取 token（前端拿不到 HttpOnly）
- 前端实现最简单：请求时 `withCredentials: true`

本地部署注意：
- 若是 http（非 https），`Secure` cookie 无法生效，需要后端在 dev/local 下允许 `Secure=false`
- 建议：
  - `SameSite=Lax`（大多数同站点场景足够）
  - 明确 cookie `Path=/`，Domain 按部署域名
- CSRF：
  - 如果是同站点 + SameSite=Lax，多数场景风险低
  - 若存在跨站点（iframe/第三方域）或 SameSite=None：需要 CSRF token 或 double-submit cookie

axios 示例：
```ts
axios.create({ baseURL, withCredentials: true })
```

### 6.2 备选：Bearer Token（Access + Refresh）

仅在后端无法/不愿使用 cookie 时采用。

存储建议（从安全到便捷）：
1) **内存保存 access token + HttpOnly cookie 保存 refresh token**（折中最佳）
2) sessionStorage（关闭 tab 失效）
3) localStorage（最不推荐，XSS 风险更高）

刷新策略：
- access token 过期（401 + code=TOKEN_EXPIRED）→ 调用 `/auth/refresh` 获取新 token → 重放原请求
- refresh 失败 → 清理登录态并跳转 `/login`

## 7. 请求封装与错误处理约定

### 7.1 统一响应结构（建议与后端对齐）

建议后端响应（仅建议，若现有不同则以现有为准）：
```json
{ "code": 0, "message": "ok", "data": { } }
```
错误：
```json
{ "code": 10001, "message": "用户名或密码错误", "data": null }
```

### 7.2 错误分层处理

- 网络/超时：toast “网络异常，请检查连接”
- HTTP 500：toast “服务异常，请稍后重试”
- HTTP 401：
  - 若在登录页提交：提示账号/密码错误（或后端 message）
  - 若在业务页：尝试 refresh；失败则跳登录
- 业务码（code != 0）：统一映射到提示语；可维护 `code → message` 字典

## 8. 接口对接约定（摘要）

接口详见：`tech/backend/AUTH_API_CONTRACT.md`。

前端对接关键点：
- 明确鉴权载体：Cookie 还是 Bearer
- 明确登录成功返回：是否返回 user、token、tokenType、expiresIn
- 明确错误码：账号/密码错误、账户锁定、密码过期、需要二次验证等

## 9. 需要发起人/后端提供的接口信息模板（请按表补齐）

> 目的：把“对接差异”一次性收敛，避免前端反复猜字段。

### 9.1 环境信息

- baseURL：`http(s)://<host>:<port>`
- 是否同域部署（前端与后端是否同 host/port）：是/否
- CORS 配置：允许的 Origin 列表、是否允许 credentials

### 9.2 鉴权方式（必填）

- 鉴权载体：Cookie / Bearer Token
- 若 Cookie：
  - Cookie 名称：
  - HttpOnly：true/false
  - SameSite：Lax/Strict/None
  - Secure：true/false（本地 http 是否允许 false）
- 若 Bearer：
  - Header：`Authorization: Bearer <token>` 是否固定
  - access token 有效期：
  - refresh token 有效期：
  - refresh 机制：是否有 `/auth/refresh`

### 9.3 登录接口

- URL：
- Method：POST/…
- Request（JSON or form）：字段名、类型、约束
- Response：成功 data 结构；是否返回 token/user
- 错误码：账号密码错误 code=？；其他关键错误 code=？

### 9.4 当前用户信息接口（推荐提供）

- URL：例如 `/me`
- Response：user 字段（id/name/roles/permissions）

### 9.5 退出/注销接口（如有）

- URL：
- 行为：清 cookie / token 失效 / refresh token 黑名单

---

## 10. 方案决策与影响范围

- 若后端支持 cookie：优先 cookie（更安全、前端更简单）；本地 http 需放开 Secure 限制。
- 若只能 token：推荐“refresh token 放 HttpOnly cookie + access token 内存”的折中方案。
- 需要后端提供稳定的错误码与 token 过期语义（401 vs 200+业务码），否则前端刷新与提示会变得脆弱。
