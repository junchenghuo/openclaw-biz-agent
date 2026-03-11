# 本地部署方案（含回滚）— 登录页交付

面向“本地可运行演示”的最省心方案：**前端打包成静态站点 → Docker + Nginx 一键启动**。

> 目标：任何同学在一台 Mac/Windows/Linux 上，装好 Docker（或 Node）后，能用 1-2 条命令跑起来看效果。

---

## 1. 推荐方案 A：Docker + Nginx（静态站点）

### 1.1 拓扑

- 浏览器 → `http://localhost:8080` → Nginx
- Nginx
  - `/`：登录页静态资源（Vite/React/Next 导出产物）
  - `/api/*`（可选）：反代到本地后端或 mock server

### 1.2 前置环境

- Docker Desktop（建议 4.0+）
- （构建阶段可选）Node.js 18/20 + pnpm/npm（用于 `npm run build`）

### 1.3 目录约定

假设前端产物目录：
- Vite/React：`dist/`
- Next.js 静态导出：`out/`

最终将产物复制到 `deploy/nginx/html/`。

### 1.4 配置文件（示例）

`deploy/nginx/nginx.conf`：

```nginx
server {
  listen 80;
  server_name _;

  root /usr/share/nginx/html;
  index index.html;

  location / {
    try_files $uri $uri/ /index.html;
  }

  # 可选：本地后端反代
  location /api/ {
    proxy_pass http://host.docker.internal:3001/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
  }
}
```

`deploy/docker-compose.yml`：

```yaml
services:
  web:
    image: nginx:1.25-alpine
    ports:
      - "8080:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf:ro
      - ./nginx/html:/usr/share/nginx/html:ro
    restart: unless-stopped
```

### 1.5 启动 / 停止

在 `deploy/` 目录：

- 启动：
  - `docker compose up -d`
- 查看状态：
  - `docker compose ps`
- 停止：
  - `docker compose down`

访问：`http://localhost:8080`

### 1.6 回滚策略

静态站点回滚，本质是“回滚构建产物”。建议二选一：

**回滚方式 1：Git Tag + 重新构建**（最通用）
1. `git checkout <tag/commit>`
2. `npm ci && npm run build`
3. 用新产物覆盖 `deploy/nginx/html/`
4. `docker compose restart web`

**回滚方式 2：产物快照**（最快）
- 每次发布前将 `deploy/nginx/html/` 打包备份：
  - `tar -czf backups/login-web_$(date +%Y%m%d%H%M%S).tgz -C deploy/nginx html`
- 回滚时解压覆盖并重启：
  - `tar -xzf backups/<file>.tgz -C deploy/nginx`
  - `docker compose restart web`

> 如果采用“构建镜像”的方式（把静态文件 bake 到镜像里），回滚会更像常规发布：`docker compose` 切换镜像 tag 即可。

---

## 2. 备选方案 B：纯 Node 本地启动（适合研发自测）

### 2.1 Vite/React

- 安装依赖：`npm ci`（或 `pnpm i --frozen-lockfile`）
- 启动开发服务器：`npm run dev`
- 默认端口：`5173`（以项目配置为准）

回滚：`git checkout <tag/commit>` 后重新 `npm ci && npm run dev`。

### 2.2 Next.js

- 开发模式：`npm run dev`（默认 `3000`）
- 演示建议（生产更接近）：
  - `npm run build && npm run start`（默认 `3000`）

---

## 3. 环境信息清单（交付时需要对齐）

### 3.1 端口

建议固定：
- Web（Nginx）：`8080`（宿主机） → 容器 `80`
- 后端 API（如有）：`3001`（宿主机）

### 3.2 域名 / hosts

本地演示可不需要域名：直接 `http://localhost:8080`。

如必须模拟域名（比如 Cookie 域、跳转回调）：
- 在 hosts 中加入：
  - `127.0.0.1 login.local`
- 使用：`http://login.local:8080`

### 3.3 HTTPS

默认 **不需要**（本地演示场景）。

如涉及：
- `SameSite=None` Cookie
- OAuth 回调要求 https

则可加一层 Caddy / mkcert 或 Nginx 自签证书：
- 证书：`mkcert login.local`
- 端口：`8443`（或 `443`）

### 3.4 环境变量（建议交付时明确）

- `VITE_API_BASE_URL` / `NEXT_PUBLIC_API_BASE_URL`：API 基址（`/api` 或 `http://localhost:3001`）
- `VITE_APP_ENV`：dev/demo/prod（影响日志/开关）

---

## 4. 验证清单（跑起来后怎么确认）

- [ ] `http://localhost:8080` 可打开登录页
- [ ] 前端路由刷新不 404（`try_files ... /index.html` 生效）
- [ ] `/api/health`（如有）能正常返回（确认反代/跨域策略）
- [ ] 登录成功/失败提示符合 PRD 与用例

---

## 5. 值班/运维注意事项（本地演示版）

- 端口冲突：若 8080 被占用，改成 `18080:80`
- 容器日志：`docker compose logs -f web`
- 修改配置后需重启：`docker compose restart web`
