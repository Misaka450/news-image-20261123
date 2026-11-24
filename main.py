import os
import shutil
import struct
import sys
import zlib

"""make.fun news-image entrypoint for 23 November 2026.
Validates entry.png (complete PNG, 1024x1024, <=1MiB) then copies it to the output dir."""

MAX_SIZE = 1048576
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def fail(reason):
    print(reason, file=sys.stderr)
    raise SystemExit(1)


def validate_png(path):
    try:
        size = os.path.getsize(path)
    except OSError as exc:
        fail("cannot read entry.png: " + str(exc))
    if size > MAX_SIZE:
        fail("entry.png exceeds 1048576 bytes")
    try:
        with open(path, "rb") as image:
            data = image.read()
    except OSError as exc:
        fail("cannot read entry.png: " + str(exc))
    if len(data) != size:
        fail("entry.png could not be read completely")
    if len(data) < len(PNG_SIGNATURE) or data[:8] != PNG_SIGNATURE:
        fail("invalid PNG signature")

    offset = 8
    saw_ihdr = False
    saw_iend = False
    while offset < len(data):
        if len(data) - offset < 12:
            fail("truncated PNG chunk")
        length = struct.unpack(">I", data[offset:offset + 4])[0]
        chunk_start = offset
        offset += 4
        chunk_type = data[offset:offset + 4]
        offset += 4
        if len(chunk_type) != 4 or length > len(data) - offset - 4:
            fail("truncated PNG chunk data")
        chunk_data = data[offset:offset + length]
        offset += length
        expected_crc = struct.unpack(">I", data[offset:offset + 4])[0]
        offset += 4
        actual_crc = zlib.crc32(chunk_type + chunk_data) & 0xffffffff
        if actual_crc != expected_crc:
            fail("PNG chunk CRC mismatch")
        if chunk_type == b"IHDR":
            if saw_ihdr or length != 13:
                fail("invalid IHDR chunk")
            width, height = struct.unpack(">II", chunk_data[:8])
            if (width, height) != (1024, 1024):
                fail("PNG dimensions are not 1024x1024")
            saw_ihdr = True
        if chunk_type == b"IEND":
            if length != 0:
                fail("invalid IEND chunk")
            saw_iend = True
            if offset != len(data):
                fail("IEND is not the final PNG chunk")
            break
        if chunk_start == offset:
            fail("invalid PNG chunk")
    if not saw_ihdr:
        fail("PNG is missing IHDR")
    if not saw_iend:
        fail("PNG is missing final IEND")


def main():
    source = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    validate_png(source)
    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    destination = os.path.join(output_dir, "entry.png")
    try:
        os.makedirs(output_dir, exist_ok=True)
        shutil.copyfile(source, destination)
        size = os.path.getsize(destination)
    except OSError as exc:
        fail("could not write output: " + str(exc))
    print(destination)
    print(size)


if __name__ == "__main__":
    main()
