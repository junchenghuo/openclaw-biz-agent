# 中国风登录页前端实现（V1.1）

## 产物路径
- `projects/iw-chinese-login-20260314-workspace/tech/frontend/login-cn-v1.1/index.html`
- `projects/iw-chinese-login-20260314-workspace/tech/frontend/login-cn-v1.1/styles.css`
- `projects/iw-chinese-login-20260314-workspace/tech/frontend/login-cn-v1.1/script.js`

## 运行方式
```bash
cd projects/iw-chinese-login-20260314-workspace/tech/frontend/login-cn-v1.1
python3 -m http.server 8080
# 浏览器打开 http://localhost:8080
```

## 已实现项（对应验收口径）
- 响应式布局：1280+ 左视觉右表单；768~1279 单列；移动端卡片化。
- 输入校验：账号为空/格式错误、密码为空/长度不足。
- 账号规则：手机号优先，兼容邮箱/用户名。
- 交互：显示/隐藏密码、回车提交、记住我默认不勾选。
- 登录失败提示：统一模糊文案（不泄露账号存在性）。
- 按钮状态：默认/hover/active/disabled/loading。
- 样式规范：主色、强调色、阴影、44px 可触达目标。

## 自测结果
- ✅ Chrome（本机）静态打开正常。
- ✅ 390 / 768 / 1280+ 断点下无重叠，主流程可用。
- ✅ 必填与格式校验提示符合文案口径。
- ✅ 登录提交后展示统一模糊失败提示。

## 边界
- 当前为静态前端实现，未接入真实登录 API。
