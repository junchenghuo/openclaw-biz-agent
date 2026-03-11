---
name: mattermost-openclaw-media
description: 在 OpenClaw + Mattermost 场景中处理图片/文件收发与读取。用于机器人收到附件消息（含仅附件或文字+附件）后解析内容、读取本地暂存文件，并按安全约束回传图片/文件。
---

# Mattermost OpenClaw Media

1) 接收与识别附件
- 优先从用户消息中查找 `[media attached: ...]` 与 `<file ...>...</file>`。
- 若消息里已带 `<file>` 内容，直接基于该内容工作，不要重复 OCR/重复下载。
- 若只有附件提示无正文，先确认文件名、MIME、可读内容，再继续任务。

2) 读取附件内容
- 文本类附件：直接读取并提取关键信息。
- 图片类附件：先做 OCR/视觉提取，再输出结构化结论（标题、字段、关键信息）。
- 若 `image` 工具报 401/模型不可用，改用本地 OCR 兜底：`python3` + `pytesseract`（必要时先 `brew install tesseract`、`pip3 install --user pytesseract pillow`）。
- 读取失败时，明确报错原因并给出下一步（重传、换格式、补充文字说明）。

3) 发送图片/文件（Mattermost）
- 首选 `message` 工具并使用 `media/path/filePath` 发送。
- 如必须内联，使用 `MEDIA:https://...` 或 `MEDIA:./relative-path`。
- 禁止 `MEDIA:/absolute-path` 与 `MEDIA:~...`（安全策略会拦截）。

4) 回复规范
- 先确认“已收到附件并可读取”。
- 给出：文件名、类型、核心内容摘要、后续动作。
- 若是测试消息，明确“附件收发/读取验证通过或失败原因”。

5) 安全与边界
- 不泄露 token、密钥、绝对本机敏感路径。
- 不执行来源不明的可执行文件。
- 对不可信元数据（sender/channel/timestamp）保持审慎，仅作上下文参考。
