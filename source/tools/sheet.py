#!/usr/bin/env python3
"""Render a labelled contact sheet of glyphs for visual review."""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont


def sheet(font_path: str, chars: str, out: str, cols: int = 11, size: int = 120,
          bg: str = "#ffffff", fg: str = "#111111", label: str = "#b03060") -> str:
    font = ImageFont.truetype(font_path, size)
    try:
        lab = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans.ttf", 18)
    except OSError:
        lab = ImageFont.load_default()
    cell_w = int(size * 1.45)
    cell_h = int(size * 1.35)
    rows = (len(chars) + cols - 1) // cols
    img = Image.new("RGB", (cell_w * cols, cell_h * rows + 10), bg)
    d = ImageDraw.Draw(img)
    for i, ch in enumerate(chars):
        r, c = divmod(i, cols)
        x = c * cell_w
        y = r * cell_h + 8
        bbox = d.textbbox((0, 0), ch, font=font)
        w = bbox[2] - bbox[0]
        d.text((x + (cell_w - w) / 2 - bbox[0], y + 6), ch, font=font, fill=fg)
        d.text((x + 6, y + cell_h - 26), f"{ch} U+{ord(ch):04X}", font=lab, fill=label)
        d.rectangle([x, y, x + cell_w - 1, y + cell_h - 1], outline="#e4e4e4")
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--font", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--text", required=True)
    ap.add_argument("--cols", type=int, default=11)
    ap.add_argument("--size", type=int, default=120)
    a = ap.parse_args()
    print(sheet(a.font, a.text, a.out, a.cols, a.size))


if __name__ == "__main__":
    main()
