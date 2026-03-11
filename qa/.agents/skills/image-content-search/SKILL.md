---
name: image-content-search
description: 在指定目录中对图片进行 OCR，并按关键词搜索图片内容（适合视频截图/海报/文档图检索）。
metadata:
  {
    "openclaw":
      {
        "emoji": "🔎",
        "requires": { "bins": ["python3", "tesseract"] },
        "install":
          [
            {
              "id": "brew",
              "kind": "brew",
              "formula": "tesseract",
              "bins": ["tesseract"],
              "label": "Install tesseract (brew)",
            },
          ],
      },
  }
---

# Image Content Search

对目录下图片执行 OCR，然后按关键词检索命中结果。

## 使用场景

- “在视频截图目录里找包含‘报错’字样的图片”
- “检索包含某个工单号/设备名的截图”

## 命令

```bash
python3 {baseDir}/scripts/search_images.py \
  --dir "/path/to/video/images" \
  --query "关键字" \
  --limit 20
```

## 依赖安装（首次）

```bash
brew install tesseract
python3 -m pip install --user pillow pytesseract
```
