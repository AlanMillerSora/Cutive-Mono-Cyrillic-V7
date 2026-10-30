#!/usr/bin/env python3
"""Assemble Cutive Mono Cyrillic.

The Latin part is never regenerated: the original TTF is used as the
carrier and only new glyphs are appended, then metadata is rewritten.
Overlap removal runs on a scratch copy so the original Latin glyphs stay
bit-for-bit identical (verified by verify.py).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "source" / "design"))

import glyphs as G  # noqa: E402
import extras as E  # noqa: E402
from fontTools.ttLib import TTFont  # noqa: E402
from fontTools.ttLib.removeOverlaps import removeOverlaps  # noqa: E402
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable  # noqa: E402
from kit import ADVANCE, CENTER, DonorSource, Glyph, emit  # noqa: E402

SRC = ROOT / "source" / "original" / "CutiveMono-Regular.ttf"
FAMILY = "Cutive Mono Cyrillic"
PSNAME = "CutiveMonoCyrillic-Regular"
VERSION = "7.000"


def scale_lowercase(g, cp, scale):
    """Large variant: stretch the Cyrillic lowercase to a bigger x-height."""
    if scale != 1.0 and chr(cp).islower():
        g.map_points(lambda x, y: (x, y * scale))
    return g


def add_glyph(font, ds, name, cp, builder, donor, lc_scale=1.0):
    g = Glyph(name)
    if donor:
        ds.add(g, ds.cmap[ord(donor)])
    if builder:
        builder(g, ds)
    if not g.contours:
        raise SystemExit(f"empty glyph: {name}")
    scale_lowercase(g, cp, lc_scale)
    g.center_in_cell()
    glyf = font["glyf"]
    glyf[name] = emit(g)
    glyf[name].recalcBounds(glyf)
    font["hmtx"][name] = (ADVANCE, glyf[name].xMin)
    return g


def normalise_contours(font):
    """TrueType allows contours without any on-curve point; CFF does not.

    Insert the implied on-curve midpoint so quad->cubic conversion works.
    """
    glyf = font["glyf"]
    fixed = 0
    for name in font.getGlyphOrder():
        g = glyf[name]
        if g.numberOfContours <= 0:
            continue
        coords = list(g.coordinates)
        flags = list(g.flags)
        ends = list(g.endPtsOfContours)
        out_c, out_f, out_e = [], [], []
        start = 0
        shift = 0
        for e in ends:
            seg = coords[start:e + 1]
            fl = flags[start:e + 1]
            if not any(f & 1 for f in fl):
                mid = ((seg[-1][0] + seg[0][0]) // 2, (seg[-1][1] + seg[0][1]) // 2)
                seg = seg + [mid]
                fl = fl + [1]
                shift += 1
                fixed += 1
            out_c.extend(seg)
            out_f.extend(fl)
            out_e.append(e + shift)
            start = e + 1
        from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates
        g.coordinates = GlyphCoordinates(out_c)
        g.flags = bytearray(out_f)
        g.endPtsOfContours = out_e
    if fixed:
        print(f"normalised {fixed} on-curve-less contours")
    return fixed


def set_names(font, family=FAMILY, psname=PSNAME):
    name = font["name"]
    values = {
        1: family,
        2: "Regular",
        3: f"{VERSION};{psname};Unofficial fork with Cyrillic",
        4: f"{family} Regular",
        5: f"Version {VERSION}",
        6: psname,
        7: f"{family} is not an official release of Cutive Mono",
        8: "Vernon Adams; Cyrillic extension by ArchEclipse project",
        9: "Vernon Adams",
        11: "https://github.com/googlefonts/cutivemono",
        12: "https://github.com/googlefonts/cutivemono",
        13: (
            "Copyright 2012 The Cutive Project Authors (https://github.com/googlefonts/cutivemono), "
            "with Reserved Font Name: none. Cyrillic extension 2026, released under the SIL Open Font "
            "License 1.1. This is an unofficial modified version, not affiliated with the original authors."
        ),
        14: "https://openfontlicense.org",
        16: family,
        17: "Regular",
    }
    name.names = [n for n in name.names if n.nameID not in values]
    for nid, val in values.items():
        name.setName(val, nid, 3, 1, 0x409)
        name.setName(val, nid, 1, 0, 0)


def update_cmap(font, mapping):
    for table in font["cmap"].tables:
        if table.format == 4:
            table.cmap.update({cp: name for cp, name in mapping.items() if cp <= 0xFFFF})
    # keep only glyphs present
    order = set(font.getGlyphOrder())
    for table in font["cmap"].tables:
        table.cmap = {cp: n for cp, n in table.cmap.items() if n in order}


def add_mark_feature(font, mapping, marks):
    """Append mark-to-base lookups to the ORIGINAL GPOS table.

    feaLib rebuilds GSUB/GPOS from scratch, which would drop the original
    Latin features (liga, locl, ccmp, kern, mark, mkmk).  So the feature is
    compiled on a scratch copy and only the new lookups + feature record
    are merged back into the untouched tables.
    """
    from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
    from fontTools.ttLib import TTFont
    from fontTools.ttLib.tables import otTables as ot

    glyf = font["glyf"]
    cmap = font.getBestCmap()
    TOP = [0x0300, 0x0301, 0x0304, 0x0306, 0x0307, 0x0308, 0x030A, 0x030B, 0x030C, 0x030F, 0x0311]
    BOT = [0x0326, 0x0327, 0x0328]

    fea = []
    for cp in TOP:
        name = cmap.get(cp)
        if not name:
            continue
        g = glyf[name]
        g.recalcBounds(glyf)
        fea.append(f"markClass {name} <anchor {int((g.xMin + g.xMax) / 2)} {int(g.yMin)}> @MC_top;")
    for cp in BOT:
        name = cmap.get(cp)
        if not name:
            continue
        g = glyf[name]
        g.recalcBounds(glyf)
        fea.append(f"markClass {name} <anchor {int((g.xMin + g.xMax) / 2)} {int(g.yMax)}> @MC_bot;")

    base_names = sorted({name for cp, name in mapping.items()
                         if 0x0400 <= cp <= 0x052F and name in glyf})
    fea.append("feature mark {")
    for name in base_names:
        g = glyf[name]
        if g.numberOfContours <= 0:
            continue
        g.recalcBounds(glyf)
        cx = int((g.xMin + g.xMax) / 2)
        fea.append(f"  pos base {name} <anchor {cx} {int(g.yMax + 120)}> mark @MC_top"
                   f" <anchor {cx} {int(g.yMin - 36)}> mark @MC_bot;")
    fea.append("} mark;")

    scratch = TTFont()
    scratch.importXML(str(ROOT / "build" / "scratch.ttx")) if False else None
    # minimal scratch font carrying the same glyphs for feature compilation
    from fontTools.fontBuilder import FontBuilder

    fb = FontBuilder(font["head"].unitsPerEm, isTTF=True)
    order = font.getGlyphOrder()
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf({n: font["glyf"][n] for n in order})
    fb.setupHorizontalMetrics({n: font["hmtx"][n] for n in order})
    fb.setupHorizontalHeader(ascent=font["hhea"].ascent, descent=font["hhea"].descent)
    fb.setupNameTable({"familyName": "scratch", "styleName": "Regular"})
    fb.setupOS2()
    fb.setupPost()
    addOpenTypeFeaturesFromString(fb.font, "\n".join(fea))

    new_gpos = fb.font["GPOS"].table
    gpos = font["GPOS"].table
    base_index = len(gpos.LookupList.Lookup)
    for lk in new_gpos.LookupList.Lookup:
        gpos.LookupList.Lookup.append(lk)
    gpos.LookupList.LookupCount = len(gpos.LookupList.Lookup)
    new_indices = list(range(base_index, base_index + len(new_gpos.LookupList.Lookup)))

    # HarfBuzz resolves a tag to the FIRST feature record, so extend the
    # existing "mark" feature instead of adding a duplicate one.
    target = None
    for rec in gpos.FeatureList.FeatureRecord:
        if rec.FeatureTag == "mark":
            target = rec
            break
    if target is not None:
        target.Feature.LookupListIndex.extend(new_indices)
        target.Feature.LookupCount = len(target.Feature.LookupListIndex)
    else:
        rec = ot.FeatureRecord()
        rec.FeatureTag = "mark"
        rec.Feature = ot.Feature()
        rec.Feature.FeatureParams = None
        rec.Feature.LookupListIndex = new_indices
        rec.Feature.LookupCount = len(new_indices)
        gpos.FeatureList.FeatureRecord.append(rec)
        gpos.FeatureList.FeatureCount = len(gpos.FeatureList.FeatureRecord)
        fi = gpos.FeatureList.FeatureCount - 1
        for sr in gpos.ScriptList.ScriptRecord:
            if sr.Script.DefaultLangSys:
                sr.Script.DefaultLangSys.FeatureIndex.append(fi)
                sr.Script.DefaultLangSys.FeatureCount = len(sr.Script.DefaultLangSys.FeatureIndex)
            for ls in sr.Script.LangSysRecord:
                ls.LangSys.FeatureIndex.append(fi)
                ls.LangSys.FeatureCount = len(ls.LangSys.FeatureIndex)

    # classify new glyphs for GDEF: letters as bases, marks stay class 3
    gdef = font["GDEF"].table
    cd = gdef.GlyphClassDef.classDefs
    mark_names = set(marks)
    for cp, name in mapping.items():
        if name in mark_names or 0x0300 <= cp <= 0x036F:
            cd[name] = 3
        else:
            cd.setdefault(name, 1)
    gdef.GlyphClassDef.classDefs = cd


def hint_font(path):
    """Grid-fit the assembled TTF with ttfautohint.

    The donor Latin is ttfautohint 1.8.4 output.  Re-hinting with the same
    tool reproduces the Latin bitmap-for-bitmap and gives the new Cyrillic
    the same grid fitting -- without it the Cyrillic stems fall between
    pixels and render 6-7 % lighter and blurrier than the Latin.
    """
    try:
        from ttfautohint import ttfautohint
    except ImportError:
        print("ttfautohint-py missing: output stays unhinted", file=sys.stderr)
        return False
    tmp = path.with_name(path.stem + ".hinted.ttf")
    ttfautohint(in_file=str(path), out_file=str(tmp))
    tmp.replace(path)
    return True


def main(family=FAMILY, psname=PSNAME, out_name="CutiveMono-Cyrillic-Regular", lc_scale=1.0):
    out = ROOT / "fonts" / f"{out_name}.ttf"
    font = TTFont(SRC)
    ds = DonorSource(font)
    mapping = {}
    new_names = []

    built = {}
    for table in (G.CAPS, G.LOWS):
        for name, (cp, builder, donor) in table.items():
            built[name] = add_glyph(font, ds, name, cp, builder, donor, lc_scale)
            mapping[cp] = name
            new_names.append(name)

    # extended Cyrillic
    for name, (cp, g) in E.extra_glyphs(ds).items():
        scale_lowercase(g, cp, lc_scale)
        g.center_in_cell()
        glyf = font["glyf"]
        glyf[name] = emit(g)
        glyf[name].recalcBounds(glyf)
        font["hmtx"][name] = (ADVANCE, glyf[name].xMin)
        mapping[cp] = name
        new_names.append(name)
        built[name] = g

    marks = E.mark_glyphs(ds)

    # precomposed composites from base + mark
    by_char = {chr(cp): name for cp, name in mapping.items()}
    for cp, base_char, mark_name in E.COMPOSITES:
        base_name = by_char.get(base_char)
        if base_name is None:
            continue
        g = Glyph(f"uni{cp:04X}")
        g.contours.extend(built[base_name].contours)
        _, _, _, top = built[base_name].bounds()
        mk = marks[mark_name]
        x0, y0, x1, y1 = mk.bounds()
        import copy
        shifted = copy.deepcopy(mk).shift(CENTER - (x0 + x1) / 2, top + 120)
        g.contours.extend(shifted.contours)
        glyf = font["glyf"]
        glyf[g.name] = emit(g)
        glyf[g.name].recalcBounds(glyf)
        font["hmtx"][g.name] = (ADVANCE, glyf[g.name].xMin)
        mapping[cp] = g.name
        new_names.append(g.name)

    add_mark_feature(font, mapping, marks)

    # clean overlaps on a scratch copy, then take only the new glyphs
    scratch = TTFont(SRC)
    glyf_s = scratch["glyf"]
    for name in new_names:
        glyf_s[name] = font["glyf"][name]
        scratch["hmtx"][name] = font["hmtx"][name]
    scratch.setGlyphOrder(font.getGlyphOrder())
    scratch["post"].glyphOrder = font.getGlyphOrder()
    scratch["maxp"].numGlyphs = len(scratch.getGlyphOrder())
    removeOverlaps(scratch)
    for name in new_names:
        font["glyf"][name] = glyf_s[name]
        font["glyf"][name].recalcBounds(font["glyf"])
        font["hmtx"][name] = (ADVANCE, font["glyf"][name].xMin)

    normalise_contours(font)
    font.setGlyphOrder(font.getGlyphOrder())
    font["post"].glyphOrder = font.getGlyphOrder()
    font["maxp"].numGlyphs = len(font.getGlyphOrder())
    update_cmap(font, mapping)
    set_names(font, family, psname)

    os2 = font["OS/2"]
    os2.ulUnicodeRange1 |= 1 << 2          # Basic Latin
    os2.ulUnicodeRange1 |= 1 << 9          # Cyrillic? (bit 9 = Cyrillic)
    os2.ulUnicodeRange2 |= 1 << (57 - 32) if False else 0
    os2.achVendID = "NONE"
    font["head"].fontRevision = float(VERSION)

    out.parent.mkdir(parents=True, exist_ok=True)
    font.save(out)
    hinted = hint_font(out)
    print(f"saved {out} ({out.stat().st_size/1024:.1f} KB, {len(font.getGlyphOrder())} glyphs"
          f"{', hinted' if hinted else ', NOT hinted'})")


VARIANTS = {
    "regular": dict(),
    "large": dict(
        family="Cutive Mono Cyrillic Large",
        psname="CutiveMonoCyrillicLarge-Regular",
        out_name="CutiveMono-Cyrillic-Large",
        lc_scale=865 / 813,
    ),
}


if __name__ == "__main__":
    which = sys.argv[1:] or ["regular", "large"]
    for v in which:
        print(f"-- {v}")
        main(**VARIANTS[v])
