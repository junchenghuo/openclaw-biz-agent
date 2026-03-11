# T5｜登录接口说明模板 + 联调清单（前端对接用）

> 适用：简单登录页（用户名+密码）。若后端已有既定接口/字段/错误码，以既有为准。
> 
> 参考更完整草案：`tech/backend/AUTH_API_CONTRACT.md`

## 1) 登录接口说明模板（请后端填空/确认）

### 基本信息

- **环境 Base URL**：`{BASE_URL}`（示例：`http://localhost:8080` / `https://api.xxx.com`）
- **鉴权方式（二选一）**：
  - A. **Cookie/Session**（前端需要 `withCredentials=true`）
  - B. **Bearer Token**（前端用 `Authorization: Bearer <accessToken>`）

### 接口：登录

- **URL**：`POST /auth/login`（如实际为 `/api/login` 等请明确）
- **Content-Type**：`application/json; charset=utf-8`

#### Headers

- 通用：
  - `Content-Type: application/json`
  - `Accept: application/json`
- 如有：
  - `X-Trace-Id: <uuid>`（可选，便于排障）
  - `X-Tenant-Id: <id>`（若多租户）

#### Body（用户名+密码）

```json
{
  "username": "string",
  "password": "string"
}
```

> 如字段名不同（如 `account`/`pwd`），请给出映射。

#### Success Response（推荐统一封装）

- **HTTP**：200
- **Body**：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "user": { "id": "u1", "name": "Tom" }
  },
  "traceId": "optional"
}
```

#### Cookie 模式补充（若采用）

- **Set-Cookie**：建议 `HttpOnly`（防止 JS 读 token）
- 前端：请求需 `withCredentials: true`

#### Token 模式补充（若采用）

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

### 常见错误码（示例，需后端确认）

| 场景 | HTTP | code（业务码） | message |
|---|---:|---:|---|
| 用户名/密码错误 | 200/401 | 10001 | 用户名或密码错误 |
| 账户锁定 | 200/403 | 10002 | 账户已锁定 |
| 需要验证码/二次验证 | 200/403 | 10003 | 需要进一步验证 |
| 未登录/Token 缺失 | 401 | 40100 | 未登录 |
| Token 过期 | 401 | 40101 | 登录已过期 |

> 建议：鉴权失败直接用 HTTP 401/403；避免“HTTP 200 + 业务码”导致前端拦截复杂化。

## 2) 需要后端配合/确认清单（联调前必答）

1. **接口最终路径/字段**：`/auth/login` 是否正确？字段名 `username/password` 是否一致？
2. **鉴权方式**：Cookie 还是 Bearer Token？（决定前端是否 `withCredentials` / 是否存 token）
3. **CORS（本地最常见坑）**：
   - 是否允许前端本地地址（如 `http://localhost:5173` / `http://127.0.0.1:5173`）
   - 若 Cookie 模式：
     - `Access-Control-Allow-Credentials: true`
     - `Access-Control-Allow-Origin` 不能为 `*`，需指定具体 origin
4. **Cookie 配置（若 Cookie 模式）**：
   - `SameSite`/`Secure`/`Domain` 在本地和线上如何配置？
   - 是否需要 CSRF 防护（如 double submit / csrf token）
5. **测试账号/数据**：提供 1-2 个可用账号（用户名/密码/角色）以及锁定/错误密码的复现账号（可选）
6. **环境信息**：
   - dev/staging/production 的 Base URL
   - 是否有网关前缀（如 `/api`）
7. **联调排障信息**：
   - 是否返回 `traceId/requestId`（便于定位服务端日志）
   - 日志检索方式/关键字（由后端同学提供）

---

### 前端对接建议（可选）

- 登录成功后建议再调一次 `GET /me` 获取当前用户，便于刷新/鉴权一致性。
- 若后端短期无法提供 `/me`，可在登录返回里附带基础 user 信息（id/name/roles）。
