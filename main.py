"""make.fun 竞赛提交入口。

校验同目录的 ``entry.png`` 后，将其复制到 ``MAKEFUN_OUTPUT_DIR`` 指定的
目录中；未设置该环境变量时，输出目录默认为 ``/output``。
"""

from __future__ import annotations

import os
import shutil
import struct
from pathlib import Path


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
MAX_FILE_SIZE = 1_048_576
REQUIRED_SIZE = (1024, 1024)


def fail(reason: str) -> None:
    """打印中文失败原因并以失败状态退出。"""

    print(reason)
    raise SystemExit(1)


def validate_png(path: Path) -> None:
    """校验 PNG 文件完整性、IHDR 结构、尺寸及文件大小。"""

    if not path.exists():
        fail(f"校验失败：找不到文件 {path.name}")
    if not path.is_file():
        fail(f"校验失败：{path.name} 不是普通文件")

    try:
        size = path.stat().st_size
        data = path.read_bytes()
    except OSError as exc:
        fail(f"校验失败：无法读取 {path.name}（{exc}）")

    if size > MAX_FILE_SIZE:
        fail(f"校验失败：{path.name} 字节数超过 1048576")
    if len(data) != size:
        fail(f"校验失败：无法完整读取 {path.name}")
    if len(data) < len(PNG_SIGNATURE) + 8:
        fail("校验失败：不是完整的 PNG 文件")
    if data[:8] != PNG_SIGNATURE:
        fail("校验失败：PNG 签名不正确")

    ihdr_offset = 8
    ihdr_length = struct.unpack(">I", data[ihdr_offset : ihdr_offset + 4])[0]
    ihdr_type = data[ihdr_offset + 4 : ihdr_offset + 8]
    if ihdr_length != 13:
        fail(f"校验失败：IHDR chunk 长度应为 13，实际为 {ihdr_length}")
    if ihdr_type != b"IHDR":
        fail("校验失败：第一个 PNG chunk 类型不是 IHDR")

    ihdr_end = ihdr_offset + 8 + ihdr_length + 4
    if len(data) < ihdr_end:
        fail("校验失败：PNG 的 IHDR chunk 不完整")
    width, height = struct.unpack(">II", data[ihdr_offset + 8 : ihdr_offset + 16])
    if (width, height) != REQUIRED_SIZE:
        fail(f"校验失败：图片尺寸必须为 1024x1024，实际为 {width}x{height}")

    # 继续解析所有 chunk，确保文件没有在 IEND 之前截断，并且确实以 IEND 结束。
    offset = 8
    saw_iend = False
    while offset < len(data):
        if len(data) - offset < 12:
            fail("校验失败：PNG chunk 不完整")
        chunk_length = struct.unpack(">I", data[offset : offset + 4])[0]
        chunk_end = offset + 12 + chunk_length
        if chunk_end > len(data):
            fail("校验失败：PNG 文件在 chunk 中被截断")
        chunk_type = data[offset + 4 : offset + 8]
        if chunk_type == b"IEND":
            if chunk_length != 0:
                fail("校验失败：IEND chunk 长度应为 0")
            if chunk_end != len(data):
                fail("校验失败：IEND 后存在多余或不完整数据")
            saw_iend = True
            break
        offset = chunk_end

    if not saw_iend:
        fail("校验失败：PNG 缺少完整的 IEND chunk")


def main() -> None:
    """校验入口图片并将其复制到 make.fun 输出目录。"""

    entry_path = Path(__file__).resolve().parent / "entry.png"
    validate_png(entry_path)

    output_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output")
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        target_path = output_dir / "entry.png"
        shutil.copyfile(entry_path, target_path)
    except OSError as exc:
        fail(f"输出失败：无法复制到 {output_dir}（{exc}）")

    if not target_path.exists():
        fail(f"输出失败：目标文件不存在 {target_path}")
    source_size = entry_path.stat().st_size
    target_size = target_path.stat().st_size
    if target_size != source_size:
        fail(f"输出失败：目标文件大小为 {target_size} bytes，源文件大小为 {source_size} bytes")
    print(f"verified: {REQUIRED_SIZE[0]}x{REQUIRED_SIZE[1]}, {target_size} bytes")
    print(target_path)


if __name__ == "__main__":
    main()
