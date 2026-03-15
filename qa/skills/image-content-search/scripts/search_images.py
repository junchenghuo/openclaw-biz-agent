#!/usr/bin/env python3
import argparse
import os
import re
import sys
from pathlib import Path

try:
    from PIL import Image
    import pytesseract
except Exception:
    print("缺少依赖，请执行: python3 -m pip install --user pillow pytesseract", file=sys.stderr)
    sys.exit(2)


def collect_images(root: Path, max_files: int):
    exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff", ".heic"}
    files = []
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in exts:
            files.append(p)
            if max_files > 0 and len(files) >= max_files:
                break
    return files


def ocr_text(img_path: Path, lang: str):
    try:
        with Image.open(img_path) as im:
            text = pytesseract.image_to_string(im, lang=lang)
            return text or ""
    except Exception:
        return ""


def main():
    parser = argparse.ArgumentParser(description="OCR 搜索目录中图片内容")
    parser.add_argument("--dir", required=True, help="图片目录")
    parser.add_argument("--query", required=True, help="搜索关键字")
    parser.add_argument("--limit", type=int, default=20, help="最多返回条数")
    parser.add_argument("--max-files", type=int, default=2000, help="最多扫描图片数")
    parser.add_argument("--lang", default="eng", help="tesseract 语言包，如 eng / chi_sim / eng+chi_sim")
    args = parser.parse_args()

    base = Path(args.dir).expanduser().resolve()
    if not base.exists() or not base.is_dir():
        print(f"目录不存在: {base}", file=sys.stderr)
        sys.exit(1)

    query = args.query.strip()
    if not query:
        print("query 不能为空", file=sys.stderr)
        sys.exit(1)

    images = collect_images(base, args.max_files)
    if not images:
        print("未找到图片文件")
        return

    q_low = query.lower()
    hits = []

    for img in images:
        txt = ocr_text(img, args.lang)
        if not txt:
            continue

        txt_low = txt.lower()
        if q_low in txt_low:
            freq = txt_low.count(q_low)
            snippet = re.sub(r"\s+", " ", txt).strip()
            if len(snippet) > 120:
                snippet = snippet[:120] + "..."
            hits.append((freq, str(img), snippet))

    hits.sort(key=lambda x: x[0], reverse=True)
    hits = hits[: max(args.limit, 1)]

    if not hits:
        print(f"未命中关键字: {query}")
        return

    print(f"命中 {len(hits)} 条（query={query}）")
    for i, (freq, path, snippet) in enumerate(hits, 1):
        print(f"{i}. freq={freq} | {path}")
        print(f"   OCR: {snippet}")


if __name__ == "__main__":
    main()
