# 认证/登录接口对接约定（草案）

> 说明：若后端已有既定接口/字段/错误码，以既有为准；本文用于把前端对接所需信息“明文化”。

## 1. 基本约定

- Base URL：`{BASE_URL}`（由环境决定）
- Content-Type：优先 `application/json; charset=utf-8`
- 字符编码：UTF-8
- 时间格式：ISO8601（如涉及）

### 1.1 统一响应封装（建议）

```ts
type ApiResponse<T> = {
  code: number;        // 0 表示成功
  message: string;     // 可展示给用户的提示（或用于日志）
  data: T | null;
  traceId?: string;    // 可选：便于排障
}
```

- 成功：`code=0`
- 失败：`code!=0` + 合理的 `message`

> 如果后端不使用该封装，也请明确：成功/失败如何表达（HTTP 状态码 or 业务码）。

## 2. 登录接口

### 2.1 POST /auth/login

#### Request

```json
{
  "username": "string",
  "password": "string"
}
```

> 若后端字段不同（如 `account`/`pwd`），请明确映射。

#### Response（Cookie 模式）

- HTTP 200
- `Set-Cookie: <session or jwt cookie>`
- Body（可选返回 user，便于前端直用）：
```json
{ "code": 0, "message": "ok", "data": { "user": { "id": "u1", "name": "Tom" } } }
```

#### Response（Bearer Token 模式）

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "tokenType": "Bearer",
    "accessToken": "...",
    "expiresIn": 3600,
    "refreshToken": "..." 
  }
}
```

> 安全建议：refreshToken 尽量不要直接下发给 JS，可改为 HttpOnly Cookie。

#### Error（示例）

- 用户名/密码错误：
```json
{ "code": 10001, "message": "用户名或密码错误", "data": null }
```
- 账户锁定：`code=10002`
- 需要验证码/二次验证：`code=10003`

## 3. 刷新 Token（仅 Token 模式）

### 3.1 POST /auth/refresh

#### Request

- 若 refreshToken 在 HttpOnly Cookie：Body 可为空
- 若 refreshToken 在 body：
```json
{ "refreshToken": "..." }
```

#### Response

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "tokenType": "Bearer",
    "accessToken": "...",
    "expiresIn": 3600
  }
}
```

#### Error

- refresh 失效：`code=10101` 或 HTTP 401

## 4. 获取当前用户信息（推荐提供）

### 4.1 GET /me

#### Response

```json
{ "code": 0, "message": "ok", "data": { "id": "u1", "name": "Tom", "roles": ["admin"] } }
```

## 5. 退出/注销

### 5.1 POST /auth/logout

- Cookie 模式：清除 session cookie
- Token 模式：可选使 refresh token 失效

Response:
```json
{ "code": 0, "message": "ok", "data": null }
```

## 6. 鉴权与错误码语义（强制对齐项）

- 未登录/Token 缺失：HTTP 401（推荐）
- Token 过期：
  - 方案 A：HTTP 401 + 特定业务码（如 `code=40101`）
  - 方案 B：HTTP 200 + 业务码（不推荐，前端拦截会更复杂）
- 权限不足：HTTP 403

## 7. CORS / Cookie 配置（本地部署特别重要）

若前后端不同源：
- `Access-Control-Allow-Origin` 不能为 `*`（如果 `Allow-Credentials=true`）
- `Access-Control-Allow-Credentials: true`
- 前端 axios/fetch：`withCredentials: true`

Cookie：
- 本地 http：`Secure=false`
- 同站点：`SameSite=Lax`
- 跨站点：`SameSite=None; Secure=true` + CSRF 防护
