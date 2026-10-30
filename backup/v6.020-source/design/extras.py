"""Extended Cyrillic, combining marks and precomposed composites.

Everything here is assembled from the same primitives and the already
drawn Cyrillic glyphs, so the extended ranges keep the same voice.
"""
from __future__ import annotations

import copy

from kit import ADVANCE, BAR, BOWL_T, CAP, CENTER, SERIF_H, SERIF_W, STEM, STEM_LC, XH, Glyph
import glyphs as G

LC = STEM_LC
SW = 396
SW_T = 300
LH = 82

# combining mark name, donor latin character, kind ('top'/'bottom'), codepoint
MARKS = {
    "gravecomb": ("\u00e0", "top", 0x0300),
    "acutecomb": ("\u00e1", "top", 0x0301),
    "dotabovecomb": ("\u017c", "top", 0x0307),
    "macroncomb": ("\u0101", "top", 0x0304),
    "brevecomb": ("\u0103", "top", 0x0306),
    "dieresiscomb": ("\u00e4", "top", 0x0308),
    "ringabovecomb": ("\u00e5", "top", 0x030a),
    "hungarumlautcomb": ("\u0151", "top", 0x030b),
    "caroncomb": ("\u010d", "top", 0x030c),
    "cedillacomb": ("\u00e7", "bottom", 0x0327),
    "ogonekcomb": ("\u0105", "bottom", 0x0328),
}


def _extract_mark(d, src: str, kind: str) -> Glyph:
    """Copy the accent of a Latin donor and normalise it to the origin."""
    tmp = Glyph("mark")
    base = d.cmap[ord(src)]
    for c in d.contours(base):
        ys = [c["start"][1]] + [q[1] for s in c["segs"] for q in s[1:]]
        if kind == "top":
            if min(ys) < 900:
                continue
        else:
            if max(ys) > 100:
                continue
        # rebuild contour through the same transform path as DonorSource.add
        segs = []
        for s in c["segs"]:
            if s[0] == "l":
                segs.append(("l", s[1]))
            elif s[0] == "c":
                segs.append(("c", s[1], s[2], s[3]))
            elif s[0] == "q":
                segs.append(("q", *s[1:]))
        tmp._add(c["start"], segs)
    x0, y0, x1, y1 = tmp.bounds()
    if kind == "top":
        tmp.shift(-(x0 + x1) / 2, -y0)
    else:
        tmp.shift(-(x0 + x1) / 2, -y1)
    return tmp


def mark_glyphs(d) -> dict[str, Glyph]:
    out = {}
    for name, (src, kind, cp) in MARKS.items():
        out[name] = _extract_mark(d, src, kind)
    return out


def extra_glyphs(d) -> dict[str, tuple[int, Glyph]]:
    """Returns name -> (codepoint, Glyph) for the extended Cyrillic set."""
    out: dict[str, tuple[int, Glyph]] = {}

    def add(name, cp, builder):
        g = Glyph(name)
        builder(g)
        out[name] = (cp, g)

    # --- Ukrainian ---------------------------------------------------
    def ye(g):  # Є = C + bar
        d.add(g, "C")
        g.capsule(190, 520, 560, 520 + BAR)
    add("uni0404", 0x0404, ye)

    def ye_lc(g):  # є
        d.add(g, "c")
        g.capsule(250, 330, 560, 330 + LH)
    add("uni0454", 0x0454, ye_lc)

    def ghe_upturn(g):  # Ґ
        G.cap_ghe(g, d)
        g.capsule(955, CAP - 86, 1045, CAP + 190)
    add("uni0490", 0x0490, ghe_upturn)

    def ghe_upturn_lc(g):  # ґ
        G.lc_ghe(g, d)
        g.capsule(880, XH - LH, 960, XH + 170)
    add("uni0491", 0x0491, ghe_upturn_lc)

    # І, і, Ї, ї come straight from the Latin I, i, Ï, ï
    out["afii10103"] = (0x0406, _donor_glyph(d, "I", "afii10103"))
    out["afii10104"] = (0x0456, _donor_glyph(d, "i", "afii10104"))
    out["afii10105"] = (0x0407, _donor_glyph(d, "\u00cf", "afii10105"))
    out["afii10106"] = (0x0457, _donor_glyph(d, "\u00ef", "afii10106"))

    # --- Belarusian --------------------------------------------------
    def short_u(g):  # Ў = У + breve
        G.cap_u(g, d)
        G.add_breve(g, d, "\u0102", 1200, dy=-63)
    add("uni040E", 0x040E, short_u)

    def short_u_lc(g):  # ў
        G.lc_u(g, d)
        G.add_breve(g, d, "\u0103", 840, dy=-47)
    add("uni045E", 0x045E, short_u_lc)

    # --- Macedonian / Serbian basics ----------------------------------
    out["uni0408"] = (0x0408, _donor_glyph(d, "J", "uni0408"))
    out["uni0458"] = (0x0458, _donor_glyph(d, "j", "uni0458"))
    out["afii10102"] = (0x0405, _donor_glyph(d, "S", "afii10102"))
    out["afii10101"] = (0x0455, _donor_glyph(d, "s", "afii10101"))

    acute = _extract_mark(d, "\u00e1", "top")

    def with_acute(base_fn, top):
        def build(g):
            base_fn(g, d)
            mk = copy.deepcopy(acute)
            x0, y0, x1, y1 = mk.bounds()
            mk.shift(CENTER - (x0 + x1) / 2, top + 120)
            g.contours.extend(mk.contours)
        return build

    add("uni0403", 0x0403, with_acute(G.cap_ghe, CAP))
    add("uni0453", 0x0453, with_acute(G.lc_ghe, XH))
    add("uni040C", 0x040C, with_acute(G.cap_ka, CAP))
    add("uni045C", 0x045C, with_acute(G.lc_ka, XH))

    # --- Serbian ligature letters -------------------------------------
    def lje(g):  # Љ = Л + Ь
        g.capsule(300, CAP - BAR, 795, CAP)
        g.stroke([(330, CAP - 60), (205, 43)], STEM, cap="round")
        g.serif_bottom(247, 0, SW_T)
        g.rect(700, 0, 700 + STEM, CAP - BAR)
        g.serif_bottom(747, 0, SW_T)
        g.capsule(700, 0, 1220, BAR)
        G.bowl(g, d, True, 960, 290, 520, 580, BOWL_T)
    add("uni0409", 0x0409, lje)

    def lje_lc(g):  # љ
        g.capsule(320, XH - LH, 700, XH)
        g.stroke([(350, XH - 47), (237, 43)], LC, cap="round")
        g.serif_bottom(277, 0, 260)
        g.rect(620, 0, 620 + LC, XH - LH)
        g.serif_bottom(667, 0, 260)
        g.capsule(620, 0, 1100, LH)
        G.bowl(g, d, False, 870, 250, 460, 500, 88)
    add("uni0459", 0x0459, lje_lc)

    def nje(g):  # Њ = Н + Ь
        g.rect(240, 0, 240 + STEM, CAP)
        g.rect(820, 0, 820 + STEM, CAP - BAR)
        g.serif_bottom(287, 0, SW)
        g.serif_top(867, CAP, SW)
        g.capsule(240, CAP - BAR, 915, CAP)
        g.capsule(240, 500, 915, 500 + BAR)
        g.capsule(820, 0, 1180, BAR)
        G.bowl(g, d, True, 1010, 290, 380, 580, BOWL_T)
    add("uni040A", 0x040A, nje)

    def nje_lc(g):  # њ
        g.rect(230, 0, 230 + LC, XH)
        g.rect(790, 0, 790 + LC, XH - LH)
        g.serif_bottom(277, 0, SW)
        g.serif_top(837, XH, SW)
        g.capsule(230, XH - LH, 884, XH)
        g.capsule(230, 400, 884, 400 + LH)
        g.capsule(790, 0, 1120, LH)
        G.bowl(g, d, False, 960, 240, 340, 480, 88)
    add("uni045A", 0x045A, nje_lc)

    def dzhe(g):  # Џ
        g.rect(240, 0, 240 + STEM, CAP - BAR)
        g.rect(870, -300, 870 + STEM, CAP - BAR)
        g.capsule(240, CAP - BAR, 965, CAP)
        g.serif_bottom(287, 0, SW)
        g.capsule(870, -300, 1160, -300 + BAR)
    add("uni040F", 0x040F, dzhe)

    def dzhe_lc(g):  # џ
        g.rect(250, 0, 250 + LC, XH - LH)
        g.rect(840, -280, 840 + LC, XH - LH)
        g.capsule(250, XH - LH, 934, XH)
        g.serif_bottom(297, 0, SW)
        g.capsule(840, -280, 1100, -280 + LH)
    add("uni045F", 0x045F, dzhe_lc)

    add("uni040F", 0x040F, dzhe)

    # --- Serbian Ђ / Ћ -------------------------------------------------
    def dje(g):  # Ђ: descender + crossbar + bowl
        G.vstem(g, 330, -300, CAP)
        g.capsule(120, -300, 425, -300 + BAR)
        G.hbar(g, 190, 900, 830)
        g.serif_top(377, CAP, SW_T)
        G.attach_bowl(g, d, True, 425, 689, 295, 620, 590, 92)
    add("uni0402", 0x0402, dje)

    def dje_lc(g):  # ђ
        G.vstem(g, 330, -300, 1120)
        g.capsule(120, -300, 425, -300 + BAR)
        G.hbar(g, 190, 880, 700)
        g.serif_top(377, 1120, 260)
        G.attach_bowl(g, d, False, 425, 689, 290, 620, 580, 92)
    add("uni0452", 0x0452, dje_lc)

    def tshe(g):  # Ћ: top arm + bowl, no descender
        G.vstem_serif(g, 330, 0, CAP - BAR, STEM, SW_T, top=False)
        g.capsule(330, CAP - BAR, 800, CAP)
        G.end_serif(g, 800, CAP, STEM, 210)
        G.attach_bowl(g, d, True, 425, 689, 295, 620, 590, 92)
    add("uni040B", 0x040B, tshe)

    def tshe_lc(g):  # ћ
        G.vstem_serif(g, 330, 0, 1120 - LH, LC, SW_T, top=False)
        g.capsule(330, 1120 - LH, 780, 1120)
        G.end_serif(g, 780, 1120, LC, 190)
        G.attach_bowl(g, d, False, 425, 689, 290, 620, 580, 92)
    add("uni045B", 0x045B, tshe_lc)

    # --- Russian punctuation -----------------------------------------
    def numero(g):  # №
        d.add(g, "N", sx=0.74, axis=0)
        g.ring(1000, 1000, 130, 145, 64)
        g.capsule(870, 820, 1130, 820 + 56)
    add("uni2116", 0x2116, numero)

    def ruble(g):  # ₽
        d.add(g, "P")
        g.capsule(230, 720, 980, 720 + 86)
    add("uni20BD", 0x20BD, ruble)

    return out


def _donor_glyph(d, char: str, name: str) -> Glyph:
    g = Glyph(name)
    d.add(g, char)
    return g


# (codepoint, base char, mark glyph name)
COMPOSITES = [
    (0x0400, "\u0415", "gravecomb"),   # Ѐ
    (0x0450, "\u0435", "gravecomb"),   # ѐ
    (0x040D, "\u0418", "gravecomb"),   # Ѝ
    (0x045D, "\u0438", "gravecomb"),   # ѝ
    (0x04D0, "\u0410", "brevecomb"),   # Ӑ
    (0x04D1, "\u0430", "brevecomb"),   # ӑ
    (0x04D2, "\u0410", "dieresiscomb"),  # Ӓ
    (0x04D3, "\u0430", "dieresiscomb"),  # ӓ
    (0x04D6, "\u0415", "brevecomb"),   # Ӗ
    (0x04D7, "\u0435", "brevecomb"),   # ӗ
    (0x04DC, "\u0416", "dieresiscomb"),  # Ӝ
    (0x04DD, "\u0436", "dieresiscomb"),  # ӝ
    (0x04DE, "\u0417", "dieresiscomb"),  # Ӟ
    (0x04DF, "\u0437", "dieresiscomb"),  # ӟ
    (0x04E2, "\u0418", "macroncomb"),  # Ӣ
    (0x04E3, "\u0438", "macroncomb"),  # ӣ
    (0x04E4, "\u0418", "dieresiscomb"),  # Ӥ
    (0x04E5, "\u0438", "dieresiscomb"),  # ӥ
    (0x04E6, "\u041E", "dieresiscomb"),  # Ӧ
    (0x04E7, "\u043E", "dieresiscomb"),  # ӧ
    (0x04EE, "\u0423", "macroncomb"),  # Ӯ
    (0x04EF, "\u0443", "macroncomb"),  # ӯ
    (0x04F0, "\u0423", "dieresiscomb"),  # Ӱ
    (0x04F1, "\u0443", "dieresiscomb"),  # ӱ
    (0x04F2, "\u0423", "hungarumlautcomb"),  # Ӳ
    (0x04F3, "\u0443", "hungarumlautcomb"),  # ӳ
    (0x04F4, "\u0427", "dieresiscomb"),  # Ӵ
    (0x04F5, "\u0447", "dieresiscomb"),  # ӵ
    (0x04F8, "\u042B", "dieresiscomb"),  # Ӹ
    (0x04F9, "\u044B", "dieresiscomb"),  # ӹ
    (0x04B6, "\u0416", "brevecomb"),   # Ҷ-adjacent: Zhe with breve
    (0x04B7, "\u0436", "brevecomb"),
    (0x04C1, "\u0416", "brevecomb"),   # Ӂ
    (0x04C2, "\u0436", "brevecomb"),   # ӂ
]
