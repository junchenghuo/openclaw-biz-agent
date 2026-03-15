---
name: mattermost-openclaw-media
description: 在 OpenClaw + Mattermost 场景中处理图片/文件收发与读取，提供可复用的本地文件暂存与 MEDIA 发送流程，杜绝“假发送”。
---

# Mattermost OpenClaw Media

用于“把本地文件发到 Mattermost 并可预览/下载”的标准化流程。

## 核心原则
1. 先暂存，后发送：任何本地文件先复制到 `./output/im-files/`。
2. 发送必须产出 `MEDIA:` 行（相对路径）。
3. 未拿到发送结果前，禁止说“已发送”。
4. 禁止回复“token 未配置/没有附件发送工具”；必须先尝试发送并回传真实错误。

## 标准发送流程（必走）
1) 先把文件复制到 `./output/im-files/`（如已存在可跳过）：
```bash
cp "/path/to/file" "./output/im-files/"
```

2) 直接用 `message` 工具发送真实附件（推荐）或按 `MEDIA:` 相对路径发送：
```text
已处理完成，请查收：
MEDIA:./output/im-files/xxx.png
（或直接在 message 工具中把 ./output/im-files/xxx.png 作为附件发送）
```

3) 若还需要文字说明，写在 `MEDIA:` 之前或之后均可。

## 读取附件流程
1. 优先从消息中的 `<file ...>...</file>`、`[media attached: ...]` 获取上下文。
2. 图片先 OCR/视觉提取，再总结关键信息。
3. Office 文档优先调用对应技能（`docx`/`pptx`/`xlsx`）后再总结。

## 错误处理
- 文件不存在：明确报错并要求用户给正确路径。
- 文件过大：提示超限并建议压缩/拆分。
- 复制失败：返回原始错误并给出下一步。
- 发送失败：返回失败原因，不得谎报“已发送”。

## 安全边界
- `MEDIA:` 仅允许相对路径（如 `MEDIA:./output/im-files/a.png`）。
- 禁止 `MEDIA:/absolute/path`、`MEDIA:~...`、`MEDIA:../../...`。
- 不泄露 token、密钥与敏感系统路径。


## Token 说明（统一）
- 默认使用 OpenClaw 已配置的 Mattermost 账号发送（无需手工配置环境变量）。
- 只有在明确要求覆盖账号凭证时，才使用 `MATTERMOST_BOT_TOKEN`。
- 若发送失败，必须回传 HTTP 状态码与原始错误体，禁止笼统回复“token 未配置”。
