# 登录/认证技术方案骨架（鉴权选型 + CORS 本地策略 + 联调方案）

> 目标：先把“后端鉴权方式 + 本地跨域 + 联调步骤”骨架定下来，便于前后端立刻对齐；细节后续补全。

## 0. 范围

- 前端：登录页（用户名+密码）
- 后端：认证相关接口（login/me/logout/refresh 可选）
- 环境：本地部署（可能 HTTP）

## 1. 鉴权选型候选

### 1.1 候选 A：**HttpOnly Cookie（Session 或 JWT Cookie）**（推荐默认）

- 载体：`Set-Cookie` 下发；前端请求 `withCredentials: true`
- 优点：
  - JS 取不到 HttpOnly cookie（抗 XSS 直接盗 token 更好）
  - 前端实现最简单（无需存取 token）
- 关键配置：
  - 本地 HTTP：`Secure=false`（否则 cookie 不生效）
  - `SameSite=Lax`（同站点默认推荐）
  - 若必须跨站点：`SameSite=None; Secure=true` + CSRF 防护

### 1.2 候选 B：Bearer Token（Access/Refresh）

- 载体：`Authorization: Bearer <accessToken>`
- 优点：跨端/跨域更直观
- 风险/成本：
  - token 存储与刷新、重放请求更复杂
  - localStorage 风险偏高；更推荐“refresh 在 HttpOnly cookie + access 在内存”

### 1.3 默认建议（先定）

- **默认建议：候选 A（HttpOnly Cookie）**。
- 若后端既有方案无法调整，再降级到候选 B，并明确 refresh 策略与 401 语义。

## 2. CORS 本地策略（最容易踩坑的部分）

### 2.1 是否同源（需要后端确认/或部署策略决定）

- 同源（推荐）：前端静态资源由后端同域提供/反向代理，避免 CORS。
- 不同源：必须配置 CORS；若使用 Cookie，必须允许 credentials。

### 2.2 不同源 + Cookie 的标准配置（建议后端按此落）

- `Access-Control-Allow-Origin: <具体 origin>`（不能是 `*`）
- `Access-Control-Allow-Credentials: true`
- `Access-Control-Allow-Headers: Content-Type, Authorization, X-Requested-With, ...`
- 预检：支持 `OPTIONS` 并返回 200/204

前端：
- axios：`axios.create({ baseURL, withCredentials: true })`
- fetch：`fetch(url, { credentials: 'include' })`

## 3. 联调方案（分三步，先跑通）

### 3.1 Step 1：环境对齐清单

- `{BASE_URL}`：
- 前端 origin：
- 是否同源：是/否
- 鉴权方式：Cookie / Bearer
- 账号（测试用）：
- 错误码（至少：账号密码错误/未登录/token 过期）：

### 3.2 Step 2：最小闭环（必须当天跑通）

1) `POST /auth/login`
   - 成功：
     - Cookie 模式：浏览器能看到 cookie（Application->Cookies）
     - Token 模式：前端拿到 accessToken 并保存（策略见 1.2）
2) `GET /me`
   - 能返回 user（用于 UI 展示/守卫）
3) `POST /auth/logout`
   - 再调用 `/me` 应失败（401 或业务码）

### 3.3 Step 3：异常/边界联调（后续补齐）

- 错误码映射（toast/表单提示）
- Token 过期刷新（如使用 token）
- CSRF（如跨站点且 cookie）

## 4. 产物与引用

- 前端总体方案（含更完整 token/cookie 讨论）：`architecture/SOLUTION.md`
- 认证接口契约（草案）：`tech/backend/AUTH_API_CONTRACT.md`
- **本次新增：接口骨架模板**：`tech/backend/AUTH_API_SKELETON_20260307.md`
