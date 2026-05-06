#!/usr/bin/env python3
"""Render colored-circle PNGs into workflow/icons/ for each TablePro color tag.

Pure stdlib (struct + zlib). Run once at build time."""
import os
import struct
import zlib

COLORS = {
    "Red": (220, 53, 69),
    "Orange": (255, 138, 0),
    "Yellow": (255, 204, 0),
    "Green": (52, 199, 89),
    "Mint": (0, 199, 190),
    "Teal": (48, 176, 199),
    "Cyan": (50, 173, 230),
    "Blue": (0, 122, 255),
    "Indigo": (88, 86, 214),
    "Purple": (175, 82, 222),
    "Pink": (255, 45, 85),
    "Brown": (162, 132, 94),
    "Gray": (142, 142, 147),
}

SIZE = 128
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "workflow", "icons")


def png_chunk(tag: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + tag
        + data
        + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    )


def write_png(path: str, w: int, h: int, pixels: bytes) -> None:
    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)
    # filter byte 0 prefix per row
    raw = bytearray()
    stride = w * 4
    for y in range(h):
        raw.append(0)
        raw.extend(pixels[y * stride : (y + 1) * stride])
    idat = zlib.compress(bytes(raw), 9)
    with open(path, "wb") as f:
        f.write(sig)
        f.write(png_chunk(b"IHDR", ihdr))
        f.write(png_chunk(b"IDAT", idat))
        f.write(png_chunk(b"IEND", b""))


def render_circle(size: int, rgb: tuple[int, int, int]) -> bytes:
    cx = cy = (size - 1) / 2
    r = size * 0.42
    r_outer = r + 0.5
    r_inner = r - 0.5
    r_outer_sq = r_outer * r_outer
    r_inner_sq = r_inner * r_inner
    px = bytearray(size * size * 4)
    for y in range(size):
        dy = y - cy
        for x in range(size):
            dx = x - cx
            d_sq = dx * dx + dy * dy
            idx = (y * size + x) * 4
            if d_sq <= r_inner_sq:
                px[idx : idx + 4] = bytes((*rgb, 255))
            elif d_sq <= r_outer_sq:
                d = d_sq**0.5
                alpha = int(255 * max(0.0, min(1.0, r_outer - d)))
                px[idx : idx + 4] = bytes((*rgb, alpha))
            # else fully transparent (default zeros)
    return bytes(px)


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    for name, rgb in COLORS.items():
        out = os.path.join(OUT_DIR, f"{name}.png")
        write_png(out, SIZE, SIZE, render_circle(SIZE, rgb))
        print(f"  {name:8s} -> {out}")
    print(f"Generated {len(COLORS)} icons in {OUT_DIR}")


if __name__ == "__main__":
    main()
