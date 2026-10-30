#!/usr/bin/env python3
"""Dump outline geometry of glyphs from a TTF (quadratic) in readable form."""
from __future__ import annotations

import sys

from fontTools.pens.recordingPen import RecordingPen
from fontTools.ttLib import TTFont


def dump(path: str, chars: str) -> None:
    f = TTFont(path)
    gs = f.getGlyphSet()
    cmap = f.getBestCmap()
    glyf = f["glyf"]
    for ch in chars:
        code = ord(ch)
        if code not in cmap:
            print(f"{ch} U+{code:04X}: MISSING")
            continue
        name = cmap[code]
        g = glyf[name]
        g.recalcBounds(glyf)
        print(f"== {ch} U+{code:04X} {name} advance={f['hmtx'][name][0]}")
        print(f"   bbox=({g.xMin},{g.yMin},{g.xMax},{g.yMax})")
        pen = RecordingPen()
        gs[name].draw(pen)
        for op, args in pen.value:
            pts = ", ".join(f"({x},{y})" for x, y in args)
            print(f"   {op:9s} {pts}")
        print()


if __name__ == "__main__":
    dump(sys.argv[1], sys.argv[2])
