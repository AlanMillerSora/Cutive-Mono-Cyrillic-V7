#!/usr/bin/env python3
"""Render text specimens from font files with PIL/FreeType.

Usage:
    python render.py --font FONT.ttf --out out.png --size 64 --text "..."

Renders one line per --text argument. Optional guidelines draw baseline,
x-height and cap-height taken from the font itself.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont


def metrics(path: str) -> dict:
    f = TTFont(path)
    os2 = f["OS/2"]
    upm = f["head"].unitsPerEm
    return {
        "upm": upm,
        "xheight": os2.sxHeight or upm // 2,
        "capheight": os2.sCapHeight or int(upm * 0.7),
        "ascender": os2.sTypoAscender,
        "descender": os2.sTypoDescender,
    }


def render(
    font_path: str,
    lines: list[str],
    out: str,
    size: int = 64,
    margin: int = 24,
    leading: float = 1.45,
    guidelines: bool = False,
    bg: str = "#fdfcf8",
    fg: str = "#1a1a1a",
    scale: int = 1,
) -> str:
    m = metrics(font_path)
    font = ImageFont.truetype(font_path, size * scale)
    ascent, descent = font.getmetrics()
    line_h = int(size * scale * leading)
    width = max(int(font.getlength(t)) for t in lines) + margin * 2
    height = line_h * len(lines) + margin * 2
    img = Image.new("RGB", (int(width), int(height)), bg)
    d = ImageDraw.Draw(img)
    upm = m["upm"]
    px = (size * scale) / upm

    for i, text in enumerate(lines):
        top = margin + i * line_h
        baseline = top + ascent
        if guidelines:
            for value, color in (
                (m["capheight"], "#f0c0c0"),
                (m["xheight"], "#c0d8f0"),
                (0, "#c8c8c8"),
                (m["descender"], "#e0d0f0"),
            ):
                y = baseline - value * px
                d.line([(margin, y), (img.width - margin, y)], fill=color, width=1)
        d.text((margin, top), text, font=font, fill=fg)
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--font", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--size", type=int, default=64)
    ap.add_argument("--text", action="append", required=True)
    ap.add_argument("--margin", type=int, default=24)
    ap.add_argument("--leading", type=float, default=1.45)
    ap.add_argument("--scale", type=int, default=1)
    ap.add_argument("--guidelines", action="store_true")
    ap.add_argument("--fg", default="#1a1a1a")
    ap.add_argument("--bg", default="#fdfcf8")
    a = ap.parse_args()
    print(
        render(
            a.font,
            a.text,
            a.out,
            size=a.size,
            margin=a.margin,
            leading=a.leading,
            guidelines=a.guidelines,
            fg=a.fg,
            bg=a.bg,
            scale=a.scale,
        )
    )


if __name__ == "__main__":
    main()
