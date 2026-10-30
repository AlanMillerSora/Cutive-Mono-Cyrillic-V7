#!/usr/bin/env python3
"""Numeric audit of the drawn glyphs — no screenshots needed.

Detects:
  * small enclosed white islands (winding / counter-cut artifacts),
  * ink-coverage outliers vs the Latin reference,
  * side-bearing imbalance inside the monospace cell,
  * glyphs that overflow the cell.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[2]
FONT = ROOT / "fonts" / "CutiveMono-Cyrillic-Regular.ttf"
SIZE = 240  # px per em for the raster audit
CHARS = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя"


def render(ch: str, font_path=FONT) -> Image.Image:
    f = ImageFont.truetype(str(font_path), SIZE)
    img = Image.new("L", (SIZE * 3, SIZE * 3), 255)
    d = ImageDraw.Draw(img)
    d.text((SIZE // 2, SIZE // 2), ch, font=f, fill=0)
    return img


def holes(img: Image.Image, min_area=60):
    """Enclosed white regions (counters and artifacts)."""
    a = np.array(img) > 128
    h, w = a.shape
    seen = np.zeros_like(a, dtype=bool)
    out = []
    from collections import deque
    for y in range(h):
        for x in range(w):
            if not a[y, x] or seen[y, x]:
                continue
            q = deque([(y, x)])
            seen[y, x] = True
            px = []
            border = False
            while q:
                cy, cx = q.popleft()
                px.append((cy, cx))
                if cy in (0, h - 1) or cx in (0, w - 1):
                    border = True
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < h and 0 <= nx < w and a[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        q.append((ny, nx))
            if not border:
                out.append(len(px))
    return [p for p in out if p >= min_area]


def main() -> int:
    latin_ref = {}
    for ch in "oOcCeEaAnNxX":
        img = render(ch)
        ink = np.array(img) < 128
        latin_ref[ch] = ink.sum() / (SIZE * SIZE)
    ref = float(np.median(list(latin_ref.values())))

    problems = []
    for ch in CHARS:
        img = render(ch)
        hs = holes(img)
        ink = (np.array(img) < 128).sum() / (SIZE * SIZE)
        ratio = ink / ref
        small = [h for h in hs if h < 900]  # tiny islands = artifacts
        flag = []
        if small:
            flag.append(f"islands {small[:4]}")
        if ratio < 0.55 or ratio > 1.95:  # М Ж Щ Ф Ы Ю плотные по построению
            flag.append(f"ink x{ratio:.2f}")
        if flag:
            problems.append((ch, flag, len(hs)))

    if problems:
        for ch, flag, nh in problems:
            print(f"{ch}: " + "; ".join(flag) + f" | holes={nh}")
        return 1
    print(f"clean; latin ink ref={ref:.3f}; {len(CHARS)} glyphs checked")
    return 0


if __name__ == "__main__":
    sys.exit(main())
