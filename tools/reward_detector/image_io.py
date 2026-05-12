"""Tiny PNG reader/writer used by smoke tests and debug output.

The detector itself works with numpy arrays. Keeping PNG IO here avoids making
Pillow/OpenCV mandatory for the offline smoke tests.
"""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

import numpy as np


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


class PngError(ValueError):
    """Raised when a PNG cannot be decoded by the minimal reader."""


def _paeth_predictor(left: int, up: int, up_left: int) -> int:
    p = left + up - up_left
    pa = abs(p - left)
    pb = abs(p - up)
    pc = abs(p - up_left)
    if pa <= pb and pa <= pc:
        return left
    if pb <= pc:
        return up
    return up_left


def load_png(path: str | Path) -> np.ndarray:
    """Load an 8-bit, non-interlaced PNG into an RGB/RGBA numpy array."""

    raw = Path(path).read_bytes()
    if not raw.startswith(PNG_SIGNATURE):
        raise PngError(f"not a PNG file: {path}")

    offset = len(PNG_SIGNATURE)
    width = height = None
    bit_depth = color_type = interlace = None
    idat = bytearray()

    while offset < len(raw):
        if offset + 8 > len(raw):
            raise PngError("truncated PNG chunk header")
        length = struct.unpack(">I", raw[offset : offset + 4])[0]
        chunk_type = raw[offset + 4 : offset + 8]
        chunk_data = raw[offset + 8 : offset + 8 + length]
        offset += 12 + length

        if chunk_type == b"IHDR":
            width, height, bit_depth, color_type, _compression, _filter, interlace = struct.unpack(
                ">IIBBBBB", chunk_data
            )
        elif chunk_type == b"IDAT":
            idat.extend(chunk_data)
        elif chunk_type == b"IEND":
            break

    if width is None or height is None or bit_depth != 8 or interlace != 0:
        raise PngError("only 8-bit non-interlaced PNGs are supported")

    channel_counts = {0: 1, 2: 3, 6: 4}
    if color_type not in channel_counts:
        raise PngError(f"unsupported PNG color type: {color_type}")

    channels = channel_counts[color_type]
    stride = width * channels
    data = zlib.decompress(bytes(idat))
    expected = (stride + 1) * height
    if len(data) < expected:
        raise PngError("truncated PNG image data")

    rows = np.zeros((height, stride), dtype=np.uint8)
    cursor = 0
    prior = np.zeros(stride, dtype=np.uint8)
    bpp = channels

    for y in range(height):
        filter_type = data[cursor]
        cursor += 1
        scanline = np.frombuffer(data[cursor : cursor + stride], dtype=np.uint8).astype(np.int16)
        cursor += stride
        recon = np.zeros(stride, dtype=np.int16)

        for i, value in enumerate(scanline):
            left = recon[i - bpp] if i >= bpp else 0
            up = int(prior[i])
            up_left = int(prior[i - bpp]) if i >= bpp else 0

            if filter_type == 0:
                predictor = 0
            elif filter_type == 1:
                predictor = left
            elif filter_type == 2:
                predictor = up
            elif filter_type == 3:
                predictor = (left + up) // 2
            elif filter_type == 4:
                predictor = _paeth_predictor(left, up, up_left)
            else:
                raise PngError(f"unsupported PNG filter: {filter_type}")

            recon[i] = (int(value) + predictor) & 0xFF

        rows[y] = recon.astype(np.uint8)
        prior = rows[y]

    image = rows.reshape(height, width, channels)
    if channels == 1:
        image = np.repeat(image, 3, axis=2)
    return image


def write_png(path: str | Path, image: np.ndarray) -> None:
    """Write a uint8 grayscale/RGB/RGBA array as an unfiltered PNG."""

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    arr = np.asarray(image)
    if arr.dtype != np.uint8:
        arr = np.clip(arr, 0, 255).astype(np.uint8)

    if arr.ndim == 2:
        height, width = arr.shape
        color_type = 0
        row_bytes = [bytes(row) for row in arr]
    elif arr.ndim == 3 and arr.shape[2] in (3, 4):
        height, width, channels = arr.shape
        color_type = 2 if channels == 3 else 6
        row_bytes = [arr[y].tobytes() for y in range(height)]
    else:
        raise PngError("image must be grayscale, RGB, or RGBA")

    payload = b"".join(b"\x00" + row for row in row_bytes)

    def chunk(name: bytes, data: bytes) -> bytes:
        crc = zlib.crc32(name + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + name + data + struct.pack(">I", crc)

    ihdr = struct.pack(">IIBBBBB", width, height, 8, color_type, 0, 0, 0)
    png = PNG_SIGNATURE + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(payload)) + chunk(b"IEND", b"")
    path.write_bytes(png)

