#!/usr/bin/env python3
"""Quality gate for Cutive Mono Cyrillic."""
from __future__ import annotations

import sys
from pathlib import Path

from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[2]
ORIG = ROOT / "source" / "original" / "CutiveMono-Regular.ttf"
NEW = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "fonts" / "CutiveMono-Cyrillic-Regular.ttf"

RU_CAPS = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
RU_LOWS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
UA = "ҐґЄєІіЇї"
BE = "Ўў"
EXTRA = "ЀѐЍѝЈјЅѕЃѓЌќЉљЊњЏџЂђЋћ"
PUNCT = "№₽"
MARKS = [0x0300, 0x0301, 0x0304, 0x0306, 0x0307, 0x0308, 0x030A, 0x030B, 0x030C, 0x0327, 0x0328]


def main() -> int:
    orig = TTFont(ORIG)
    new = TTFont(NEW)
    errors, notes = [], []

    # 1. Latin must be byte-identical in outline data
    og, ng = orig["glyf"], new["glyf"]
    changed = []
    for name in orig.getGlyphOrder():
        a, b = og[name], ng[name]
        same = (a.numberOfContours == b.numberOfContours)
        if same and a.numberOfContours > 0:
            same = (list(a.coordinates) == list(b.coordinates)
                    and list(a.endPtsOfContours) == list(b.endPtsOfContours)
                    and list(a.flags) == list(b.flags))
        if same and a.numberOfContours == -1:
            same = getattr(a, "components", []) == getattr(b, "components", [])
        if not same:
            changed.append(name)
    notes.append(f"Latin glyphs checked: {len(orig.getGlyphOrder())}, changed: {len(changed)}")
    if changed:
        errors.append(f"original outlines changed: {changed[:10]}")

    # 2. advances
    cmap = new.getBestCmap()
    bad_adv = []
    for cp, name in cmap.items():
        adv = new["hmtx"][name][0]
        if 0x0300 <= cp <= 0x036F:
            continue  # combining marks must be zero width
        if cp == 0x00B7:
            continue  # original period-centred spacing, untouched
        if adv != 1240:
            bad_adv.append((hex(cp), name, adv))
    if bad_adv:
        errors.append(f"non-mono advances: {bad_adv[:10]}")
    notes.append(f"advance width 1240 for {sum(1 for n in cmap.values() if new['hmtx'][n][0] == 1240)} glyphs")

    # 3. coverage
    missing = []
    for ch in RU_CAPS + RU_LOWS + UA + BE + EXTRA + PUNCT:
        if ord(ch) not in cmap:
            missing.append(f"U+{ord(ch):04X} {ch}")
    for cp in MARKS:
        if cp not in cmap:
            missing.append(f"U+{cp:04X} combining")
    if missing:
        errors.append(f"missing codepoints: {missing}")
    notes.append(f"cmap entries: {len(cmap)}")

    # 4. empty / broken glyphs, bbox sanity
    empty, out_of_cell = [], []
    for cp, name in cmap.items():
        if cp < 0x0400 or 0x0300 <= cp <= 0x036F:
            continue
        g = new["glyf"][name]
        if g.numberOfContours == 0:
            empty.append((hex(cp), name))
            continue
        g.recalcBounds(new["glyf"])
        if g.xMin < -40 or g.xMax > 1280:
            out_of_cell.append((hex(cp), name, g.xMin, g.xMax))
    if empty:
        errors.append(f"empty glyphs: {empty}")
    if out_of_cell:
        notes.append(f"bbox outside cell: {out_of_cell}")

    # 5. no zero-length contours / degenerate spikes
    zero = []
    for cp, name in cmap.items():
        g = new["glyf"][name]
        if g.numberOfContours <= 0:
            continue
        g.recalcBounds(new["glyf"])
        if (g.xMax - g.xMin) < 10 or (g.yMax - g.yMin) < 10:
            zero.append((hex(cp), name))
    if zero:
        errors.append(f"degenerate glyphs: {zero}")

    # 6. vertical metrics untouched
    a, b = orig["hhea"], new["hhea"]
    if (a.ascent, a.descent) != (b.ascent, b.descent):
        errors.append("vertical metrics changed")
    if orig["head"].unitsPerEm != new["head"].unitsPerEm:
        errors.append("unitsPerEm changed")

    # 6b. hinting: Cyrillic must be grid-fitted like the Latin
    hinted, unhinted = 0, []
    for cp, name in cmap.items():
        if not (0x0400 <= cp <= 0x052F):
            continue
        g = new["glyf"][name]
        if g.numberOfContours == 0:
            continue
        prog = getattr(g, "program", None)
        if prog is not None and prog.getBytecode():
            hinted += 1
        else:
            unhinted.append((hex(cp), name))
    notes.append(f"hinted Cyrillic glyphs: {hinted}, unhinted: {len(unhinted)}")
    if unhinted:
        errors.append(f"unhinted Cyrillic glyphs: {unhinted[:10]}")
    if "fpgm" not in new or "prep" not in new:
        errors.append("hinting tables missing")

    # 7. name table sanity
    for rec in new["name"].names:
        if rec.nameID == 1 and "Cyrillic" not in str(rec):
            errors.append(f"family name not renamed: {rec}")
            break
    if "Cutive Mono" == str(new["name"].getDebugName(1)):
        errors.append("family name equals original - OFL naming problem")

    print("\n".join("- " + n for n in notes))
    if errors:
        print("\nERRORS:")
        for e in errors:
            print(" !", e)
        return 1
    print("\nOK: all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
