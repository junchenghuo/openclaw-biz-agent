#!/usr/bin/env python3
import argparse
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path


def normalize_src(src: str, cwd: Path) -> Path:
    p = Path(src).expanduser()
    if not p.is_absolute():
        return (cwd / p).resolve()
    return p.resolve()


def safe_name(name: str) -> str:
    n = os.path.basename(name).strip()
    return n or 'file.bin'


def unique_target(dst_dir: Path, base_name: str) -> Path:
    target = dst_dir / base_name
    if not target.exists():
        return target
    stem = target.stem
    suffix = target.suffix
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    return dst_dir / f'{stem}_{ts}{suffix}'


def to_media_token(dst: Path, cwd: Path) -> str:
    rel = dst.relative_to(cwd).as_posix()
    if not rel.startswith('./'):
        rel = f'./{rel}'
    return f'MEDIA:{rel}'


def main() -> int:
    parser = argparse.ArgumentParser(description='Stage file for Mattermost MEDIA send')
    parser.add_argument('--src', required=True, help='Source file path')
    parser.add_argument('--name', help='Optional target file name')
    parser.add_argument('--out-dir', default='./output/im-files', help='Workspace relative output dir')
    parser.add_argument('--max-mb', type=int, default=30, help='Max file size in MB')
    args = parser.parse_args()

    cwd = Path.cwd().resolve()
    src = normalize_src(args.src, cwd)
    if not src.exists() or not src.is_file():
        print(json.dumps({'ok': False, 'error': 'file_not_found', 'message': f'文件不存在: {src}'}, ensure_ascii=False))
        return 1

    max_bytes = max(args.max_mb, 1) * 1024 * 1024
    size = src.stat().st_size
    if size > max_bytes:
        print(json.dumps({'ok': False, 'error': 'file_too_large', 'message': f'文件大小超限: {size} bytes > {max_bytes} bytes', 'size_bytes': size, 'max_bytes': max_bytes}, ensure_ascii=False))
        return 2

    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = (cwd / out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    name = safe_name(args.name or src.name)
    dst = unique_target(out_dir, name)
    try:
        shutil.copy2(src, dst)
    except Exception as exc:
        print(json.dumps({'ok': False, 'error': 'copy_failed', 'message': f'复制失败: {exc}'}, ensure_ascii=False))
        return 3

    print(json.dumps({'ok': True, 'src': str(src), 'dst': str(dst), 'size_bytes': size, 'media_token': to_media_token(dst, cwd)}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
