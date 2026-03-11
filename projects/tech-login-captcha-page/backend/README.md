# tech-login-captcha-page｜Backend（Gate-3 实现草案）

本目录提供一个**可本地跑通联调**的最小后端实现（Fastify + SVG captcha + Redis 可选），覆盖 ARCH.md 定稿的：
- `GET /captcha`
- `POST /login`

> 注意：当前仓库未发现“现有线上 Auth 服务代码基座”。因此这里按**独立服务 demo/参考实现**交付；如实际要落地到既有服务，请将本文的模块/逻辑迁移到现有框架（错误码、日志、限流中间件以现有规范为准）。

## 1. 行为与契约对齐点

### 1.1 GET /captcha
- 返回：`captchaId + image(data-url svg) + expireIn`
- 响应头：`Cache-Control: no-store`
- 支持刷新：前端重复调用即可
- 弱绑定（可选）：读取 `X-Client-Key`，在验证码存储中绑定（建议开启）

### 1.2 POST /login
校验顺序（与 ARCH.md 一致）：
1) 先校验 captcha（并**一次性消费 captchaId**：成功/失败都作废，防重放）
2) 再校验用户名密码
3) 成功签发登录态（默认 JWT；可切 Cookie Session）

错误码/HTTP：
- 400 `PARAM_INVALID`
- 401 `CAPTCHA_REQUIRED | CAPTCHA_INVALID | CAPTCHA_EXPIRED | AUTH_INVALID_CREDENTIALS`
- 429 `RATE_LIMITED`

### 1.3 安全基线（本实现包含/留钩子）
- 限流：
  - `/captcha`：60 req/min（示例）
  - `/login`：10 req/min（示例）
  > 生产建议优先放到网关/WAF + 服务端双层限流。
- 审计日志：`captcha_issued` / `login_failed` / `login_success`（结构化日志；不打印 password/captcha 明文）
- 验证码一次性：`verifyOnce()` 无论结果都删除 key

## 2. 登录态基线（待确认项）

ARCH.md 提到关键待确认：JWT vs Cookie Session。

本实现默认：**JWT Bearer**（响应 body 返回 `token`）。
- 如现网基线是 Cookie Session：设置 `SESSION_MODE=cookie`，则使用 `Set-Cookie: sid=...` 下发（示例配置：`HttpOnly; Secure; SameSite=Lax`）。

> 生产环境务必配置稳定的 `JWT_SECRET`（当前 demo 未持久化 secret，会导致重启失效）。

## 3. 运行方式

进入目录：
```bash
cd projects/tech-login-captcha-page/backend
npm i
npm run dev
```

环境变量（可选）：
- `PORT=3000`
- `REDIS_URL=redis://localhost:6379`（不配则走内存，重启会丢）
- `CAPTCHA_TTL_SEC=120`
- `CAPTCHA_ATTEMPTS=1`
- `SESSION_MODE=jwt|cookie`
- `TOKEN_TTL_SEC=7200`
- `JWT_SECRET=...`（生产必配）
- Demo 账号：
  - `DEMO_USER=zhangsan`
  - `DEMO_PASS=123456`

## 4. curl 联调示例

### 4.1 获取验证码
```bash
curl -s -H 'X-Client-Key: demo-client-1' 'http://localhost:3000/captcha' | jq
```

响应示例：
```json
{
  "captchaId": "cpt_xxx",
  "imageType": "svg",
  "image": "data:image/svg+xml;base64,...",
  "expireIn": 120,
  "codeLength": 4,
  "caseSensitive": false
}
```

### 4.2 登录
将上一步的 `captchaId` 与验证码图片对应的 code 填入：
```bash
curl -s -X POST 'http://localhost:3000/login' \
  -H 'content-type: application/json' \
  -H 'X-Client-Key: demo-client-1' \
  -d '{
    "username":"zhangsan",
    "password":"123456",
    "captchaId":"<captchaId>",
    "captchaCode":"<code>"
  }' | jq
```

失败时（示例）：
```json
{
  "code": "CAPTCHA_INVALID",
  "message": "captcha invalid",
  "requestId": "...",
  "details": {
    "captchaRefresh": true
  }
}
```

## 5. 落地到现有服务时的改造清单

1. **接入真实用户体系**：`src/auth.ts::verifyUsernamePassword()` 替换为：
   - 查用户（避免账号枚举，外部统一报 `AUTH_INVALID_CREDENTIALS`）
   - 使用现有密码哈希/加盐/国密算法
2. **统一错误包裹**：替换 `ApiError` 为公司通用错误规范（code 命名与 requestId 注入）
3. **限流/风控**：
   - 网关侧：IP、username、IP+username
   - 服务侧：渐进延迟 / 连续失败锁定（等保常见项）
4. **审计日志落库**：当前是结构化日志；如有审计平台，按字段映射接入
5. **Captcha 存储**：生产建议 Redis，并按 `captchaId` 一次性语义使用 `GET+DEL`（或 Lua 脚本原子性）

---

实现参考：`src/index.ts`（路由/错误码/日志）、`src/captchaStore.ts`（一次性验证码存储/校验）。
