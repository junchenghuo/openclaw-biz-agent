# 认证接口文档骨架（占位模板）

> 用途：快速对齐 URL/字段名/错误码。若后端已有既定接口，以后端为准；把差异填进本模板即可。

## 0. 全局约定（先占位）

- Base URL：`{BASE_URL}`
- 鉴权方式：`{COOKIE|BEARER}`
- 响应封装：`{是否统一 code/message/data}`
- traceId：`{是否返回}`

## 1) 登录

### POST {LOGIN_URL}

- 建议：`/auth/login`

#### Request

Content-Type：`application/json`

字段占位：

| 字段 | 类型 | 必填 | 约束 | 说明 |
|---|---|---:|---|---|
| username | string | Y | `{min,max,pattern}` | 用户名/账号/邮箱/手机号（按后端） |
| password | string | Y | `{min,max}` | 密码 |
| captcha? | string | N | | 如需要验证码 |

#### Response（成功）

- Cookie 模式：`Set-Cookie: {cookieName}={...}; HttpOnly; ...`
- Token 模式：返回 token：`{tokenType, accessToken, expiresIn, refreshToken?}`

Body 占位：
```json
{ "code": 0, "message": "ok", "data": { } }
```

## 2) 当前用户

### GET {ME_URL}

- 建议：`/me`

#### Response（成功）

字段占位：

| 字段 | 类型 | 说明 |
|---|---|---|
| id | string | 用户 id |
| name | string | 显示名 |
| roles? | string[] | 角色 |
| permissions? | string[] | 权限 |

```json
{ "code": 0, "message": "ok", "data": { "id": "...", "name": "..." } }
```

## 3) 退出

### POST {LOGOUT_URL}

- 建议：`/auth/logout`

#### Response（成功）
```json
{ "code": 0, "message": "ok", "data": null }
```

## 4) 错误码表（占位，务必补齐）

> 目标：前端能稳定映射提示语与处理策略（是否需要跳转登录、是否可重试）。

| 场景 | HTTP | code | message（示例） | 前端处理建议 |
|---|---:|---:|---|---|
| 成功 | 200 | 0 | ok | 正常 |
| 用户名或密码错误 | 200/401 | {LOGIN_FAILED_CODE} | 用户名或密码错误 | 表单提示；不跳转 |
| 未登录/会话失效 | 401 | {UNAUTHORIZED_CODE} | 未登录 | 跳转 /login |
| Token 过期（仅 token 模式） | 401 | {TOKEN_EXPIRED_CODE} | token expired | 触发 refresh/重试一次 |
| 权限不足 | 403 | {FORBIDDEN_CODE} | forbidden | 无权限提示 |
| 账号锁定 | 200/403 | {ACCOUNT_LOCKED_CODE} | 账号已锁定 | 禁止重试/提示联系管理员 |
| 需要验证码/二次验证 | 200 | {MFA_REQUIRED_CODE} | 需要验证 | 引导补充验证 |
| 参数错误 | 400 | {BAD_REQUEST_CODE} | 参数错误 | 表单校验/提示 |
| 服务异常 | 500 | {SERVER_ERROR_CODE} | 服务异常 | toast + 可重试 |

## 5) 与既有契约的关系

- 更完整的接口草案（含 CORS/cookie 建议）：`tech/backend/AUTH_API_CONTRACT.md`
