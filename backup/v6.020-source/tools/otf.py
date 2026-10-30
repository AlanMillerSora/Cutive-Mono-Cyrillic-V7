#!/usr/bin/env python3
"""Build the CFF/OTF flavour from the finished TTF.

TrueType quadratics are converted to cubics with qu2cu, components are
decomposed, and all OpenType layout tables are carried over unchanged.
"""
from __future__ import annotations

import sys
from pathlib import Path

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.qu2cuPen import Qu2CuPen
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "fonts" / "CutiveMono-Cyrillic-Regular.ttf"
OUT = ROOT / "fonts" / "CutiveMono-Cyrillic-Regular.otf"


def main(src_path=SRC, out_path=OUT) -> None:
    src = TTFont(src_path)
    order = src.getGlyphOrder()
    glyphset = src.getGlyphSet()
    fb = FontBuilder(src["head"].unitsPerEm, isTTF=False)
    fb.setupGlyphOrder(order)

    charstrings = {}
    for name in order:
        pen = DecomposingRecordingPen(glyphset)
        glyphset[name].draw(pen)
        width = src["hmtx"][name][0]
        t2 = T2CharStringPen(width, None)
        qu = Qu2CuPen(t2, max_err=0.3, all_cubic=True)
        pen.replay(qu)
        t2pen = T2CharStringPen(width, None)
        charstrings[name] = t2.getCharString()

    fb.setupCFF(
        "CutiveMonoCyrillic-Regular",
        {"FullName": "Cutive Mono Cyrillic Regular",
         "FamilyName": "Cutive Mono Cyrillic",
         "Weight": "Regular"},
        charstrings,
        {},
    )
    fb.setupCharacterMap(src.getBestCmap())
    fb.setupHorizontalMetrics({n: src["hmtx"][n] for n in order})
    hhea = src["hhea"]
    fb.setupHorizontalHeader(ascent=hhea.ascent, descent=hhea.descent)
    fb.setupNameTable({})
    fb.font["name"].names = src["name"].names
    fb.setupOS2()
    for attr in ("sTypoAscender", "sTypoDescender", "sTypoLineGap", "usWinAscent",
                 "usWinDescent", "sxHeight", "sCapHeight", "fsSelection", "usWeightClass",
                 "ulUnicodeRange1", "ulUnicodeRange2", "ulUnicodeRange3",
                 "ulUnicodeRange4", "achVendID", "fsType", "panose"):
        setattr(fb.font["OS/2"], attr, getattr(src["OS/2"], attr))
    fb.setupPost(keepGlyphNames=True)
    fb.font["head"].fontRevision = src["head"].fontRevision
    fb.font["head"].macStyle = src["head"].macStyle

    for tag in ("GSUB", "GPOS", "GDEF"):
        if tag in src:
            fb.font[tag] = src[tag]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fb.save(out_path)
    print(f"saved {out_path} ({out_path.stat().st_size/1024:.1f} KB)")


if __name__ == "__main__":
    for name in ("CutiveMono-Cyrillic-Regular", "CutiveMono-Cyrillic-Large"):
        ttf = ROOT / "fonts" / f"{name}.ttf"
        if ttf.exists():
            main(ttf, ROOT / "fonts" / f"{name}.otf")
