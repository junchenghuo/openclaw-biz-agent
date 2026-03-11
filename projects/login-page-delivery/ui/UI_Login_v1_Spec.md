# 登录页 UI 规格（v1，可直接落地）

## 1) 视觉风格
- 关键词：简洁、现代、留白、卡片式
- 建议：浅色背景 + 居中卡片 + 主色按钮（蓝/紫系）

## 2) 布局
- 背景：`#F5F7FA`
- 卡片：宽 360~420px；圆角 12px；阴影 `0 10px 30px rgba(0,0,0,0.08)`；内边距 24px
- 内容垂直间距（gap）：16px

## 3) 字体与字号
- 标题：20px / font-weight 600
- 正文与输入：14px / font-weight 400
- 辅助提示：12px

## 4) 颜色（tokens）
- Primary：`#4F46E5`
- Primary Hover：`#4338CA`
- Text：`#111827`
- Muted Text：`#6B7280`
- Border：`#E5E7EB`
- Error：`#EF4444`

## 5) 组件规格
### 输入框
- 高度：44px；圆角：10px
- 边框：1px `#E5E7EB`
- Focus：边框 1px Primary + 轻微外发光（可选）
- Placeholder：Muted Text

### 密码显示/隐藏
- 右侧 icon button（24px 区域），hover 有轻微背景（如 `rgba(79,70,229,0.08)`）

### 主按钮
- 高度：44px；全宽
- 背景：Primary；文字白色
- Hover：Primary Hover
- Disabled：背景 `#A5B4FC`（或透明度 0.6）+ cursor not-allowed
- Loading：按钮内 spinner + 文案“登录中…”

### 错误提示
- 字段级错误：输入框下方 12px，颜色 Error
- 全局错误：按钮上方一条 Alert（背景 `rgba(239,68,68,0.08)`，文字 Error）

## 6) 三种关键状态（必须可见）
- Normal：默认
- Error：字段下方/全局 alert 显示
- Loading：按钮 loading + 禁用输入/按钮

## 7) 资产
- Logo/产品名：若无素材，先用占位文本（不影响交付）
