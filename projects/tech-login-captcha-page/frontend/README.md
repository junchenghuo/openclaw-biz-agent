# Tech Login + Captcha（前端）

> 目标：按 `architecture/ARCH.md` 契约实现登录页（账号/密码/图形验证码），PC 优先并适配移动端；默认内置 Mock，后端就绪后可切换到真实接口。

## 1. 环境要求

- Node.js 18+（建议 20/22）

## 2. 启动

```bash
cd projects/tech-login-captcha-page/frontend
npm i
npm run dev
```

浏览器打开：`http://localhost:5173`

## 3. 接口切换（Mock / Real API）

本项目默认使用 Mock（无需后端即可跑通交互闭环）。

### 3.1 Mock（默认）

- 默认：`VITE_USE_MOCK=true`
- Demo 账号：`admin` / `admin123`

### 3.2 真实接口

创建 `.env.local`：

```bash
VITE_USE_MOCK=false
VITE_API_BASE=http://localhost:8080
```

接口路径（与 ARCH.md 对齐）：
- `GET /captcha` → `{ captchaId, image(data-url), expireIn, ... }`
- `POST /login`  → **成功返回 `{ token, user, ... }`（登录态基线：JWT）**；失败返回 `{ code, message, details }`

### 3.3 登录态基线（已确认：JWT）

- token 类型：JWT（前端以 `Authorization: Bearer <token>` 使用）
- 存储建议：**优先内存**（页面刷新需重新登录或走 refresh 策略）；如业务要求持久化，可用 `localStorage` 配合 **短期 access token + refresh**（按现网规范落地）。
- 安全要点：JWT 模式一般不走 cookie session，CSRF 风险较低；但需重点防 **XSS**（CSP / 转义 / 禁内联脚本）。

说明：前端请求会自动带 `X-Client-Key` 头（用于验证码弱绑定/风控）。

## 4. 交互说明（验收点映射）

- 登录页：账号/密码/验证码输入
- 验证码：页面加载自动拉取；点击验证码图片刷新（带 600ms 节流）
- Enter 提交：表单内默认支持
- 按钮 loading：提交中显示 spinner 且禁用
- 错误提示：字段级 + 全局
- 失败策略：
  - `CAPTCHA_INVALID / CAPTCHA_EXPIRED / AUTH_INVALID_CREDENTIALS / CAPTCHA_REQUIRED` → 自动刷新验证码
  - `RATE_LIMITED` → **不**自动刷新（避免放大器）
- i18n 预留：文案集中在 `src/utils/i18n.ts`

## 5. 目录结构

```text
frontend/
  src/
    api/        # /captcha /login 调用（含 mock）
    components/ # LoginCard / ParticleBackground
    styles/     # 全局与页面样式
    utils/      # i18n
  screenshots/  # 页面截图（验收用）
```

## 6. 截图

请将验收截图放到：

- `projects/tech-login-captcha-page/frontend/screenshots/`

建议至少：PC 版、移动端（响应式窄屏）各 1 张。
