#!/usr/bin/env python3
"""Alternative constructions for Д, Ж, Э, Я + comparison sheets.

Each variant is drawn with the same primitives as the shipping font (same
weight).  A single demo font maps the variants to PUA codepoints so whole
words can be rendered with a chosen variant.
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "source" / "design"))

import glyphs as G  # noqa: E402
from kit import CAP, CENTER, Glyph, STEM, STEM_LC, XH, emit  # noqa: E402

LC = STEM_LC
OUT = ROOT / "specimens" / "v4-alternatives"
BASE = ROOT / "fonts" / "CutiveMono-Cyrillic-Regular.ttf"
V3 = ROOT / "backup" / "v3-fonts" / "CutiveMono-Cyrillic-Regular.ttf"

# PUA codepoints for the variants
CODES = {
    ("Д", "A"): 0xE000, ("Д", "B"): 0xE001, ("Д", "C"): 0xE002,
    ("Ж", "A"): 0xE010, ("Ж", "B"): 0xE011, ("Ж", "C"): 0xE012,
    ("Э", "A"): 0xE020, ("Э", "B"): 0xE021, ("Э", "C"): 0xE022,
    ("Я", "A"): 0xE030, ("Я", "B"): 0xE031, ("Я", "C"): 0xE032,
}


# ---------------------------------------------------------------------------
# Д
# ---------------------------------------------------------------------------
def de_a(g, d):
    """A: vertical sides, wide base, short feet with slab serifs."""
    G.vstem(g, 270, -140, CAP - G.BAR)
    G.vstem(g, 850, -140, CAP - G.BAR)
    g.capsule(255, CAP - G.BAR, 960, CAP)
    g.capsule(220, 0, 1000, G.BAR)
    g.serif_bottom(317, -140, 240)
    g.serif_bottom(897, -140, 240)


def de_b(g, d):
    """B: slanted left leg (family with Л), vertical right side."""
    g.capsule(300, CAP - G.BAR, 960, CAP)
    G.vstem_serif(g, 865, 0, CAP - G.BAR, STEM, 300, top=False)
    g.stroke([(350, CAP - 55), (200, 0)], STEM, cap="round")
    g.capsule(175, 0, 1000, G.BAR)
    g.serif_bottom(247, 0, 300)


def de_c(g, d):
    """C: box with inset sides and a bottom slab that overshoots the sides."""
    G.vstem(g, 300, -150, CAP - G.BAR)
    G.vstem(g, 820, -150, CAP - G.BAR)
    g.capsule(280, CAP - G.BAR, 935, CAP)
    g.capsule(150, 0, 1065, G.BAR)
    g.serif_bottom(347, -150, 200)
    g.serif_bottom(867, -150, 200)


# ---------------------------------------------------------------------------
# Ж
# ---------------------------------------------------------------------------
def zhe_a(g, d):
    """A: arms from the stem edges."""
    G.vstem(g, 573, 0, CAP, STEM)
    g.serif_top(620, CAP, 240)
    g.serif_bottom(620, 0, 240)
    g.stroke([(573, 585), (155, CAP)], STEM, cap="round")
    g.stroke([(573, 585), (155, 0)], STEM, cap="round")
    g.stroke([(668, 585), (1085, CAP)], STEM, cap="round")
    g.stroke([(668, 585), (1085, 0)], STEM, cap="round")
    for x, y in ((155, CAP), (1085, CAP), (155, 0), (1085, 0)):
        if y:
            g.serif_top(x, CAP, 230)
        else:
            g.serif_bottom(x, 0, 230)


def zhe_b(g, d):
    """B: one continuous diagonals crossing behind the stem, no stem serifs."""
    G.vstem(g, 573, 0, CAP, STEM)
    g.stroke([(155, CAP), (1085, 0)], STEM, cap="round")
    g.stroke([(1085, CAP), (155, 0)], STEM, cap="round")
    for x, y in ((155, CAP), (1085, CAP), (155, 0), (1085, 0)):
        if y:
            g.serif_top(x, CAP, 230)
        else:
            g.serif_bottom(x, 0, 230)


def zhe_c(g, d):
    """C: arms meet the stem at two heights, leaving a lighter waist."""
    G.vstem(g, 573, 0, CAP, STEM)
    g.serif_top(620, CAP, 240)
    g.serif_bottom(620, 0, 240)
    g.stroke([(573, 700), (155, CAP)], STEM, cap="round")
    g.stroke([(573, 470), (155, 0)], STEM, cap="round")
    g.stroke([(668, 700), (1085, CAP)], STEM, cap="round")
    g.stroke([(668, 470), (1085, 0)], STEM, cap="round")
    for x, y in ((155, CAP), (1085, CAP), (155, 0), (1085, 0)):
        if y:
            g.serif_top(x, CAP, 230)
        else:
            g.serif_bottom(x, 0, 230)


# ---------------------------------------------------------------------------
# Э
# ---------------------------------------------------------------------------
def e_a(g, d):
    """A: mirrored C + plain capsule bar."""
    d.add(g, "C", mirror=True)
    g.capsule(665, 505, 1040, 505 + G.BAR)


def e_b(g, d):
    """B: bar with a vertical serif at its left end."""
    d.add(g, "C", mirror=True)
    g.capsule(665, 505, 1040, 505 + G.BAR)
    g.capsule(665, 460, 751, 636)


def e_c(g, d):
    """C: bar with a rounded hook that turns down into the bowl."""
    d.add(g, "C", mirror=True)
    g.curve_band([(680, 560), (820, 555), (960, 545), (1040, 545)], G.BAR)
    g.curve_band([(690, 560), (660, 620), (650, 700)], 90)


# ---------------------------------------------------------------------------
# Я
# ---------------------------------------------------------------------------
def ya_a(g, d):
    """A: leg leaves from under the bowl (curve)."""
    G.vstem_serif(g, 900, 0, CAP, STEM, 300)
    G.attach_bowl(g, d, True, 900, 690, 880, 600, 500, 92, side="left")
    g.curve_band([(880, 480), (650, 340), (450, 160), (300, 20)], STEM)
    g.serif_bottom(250, 0, 300)


def ya_b(g, d):
    """B: straight diagonal leg from the bowl/stem junction."""
    G.vstem_serif(g, 900, 0, CAP, STEM, 300)
    G.attach_bowl(g, d, True, 900, 690, 880, 600, 500, 92, side="left")
    g.stroke([(820, 560), (250, 0)], STEM, cap="round")
    g.serif_bottom(250, 0, 300)


def ya_c(g, d):
    """C: mirrored R — bowl from R, leg with a slab foot."""
    d.add(g, "R", mirror=True)
    g.serif_bottom(250, 0, 250)


VARIANTS = {
    "Д": {"A": de_a, "B": de_b, "C": de_c},
    "Ж": {"A": zhe_a, "B": zhe_b, "C": zhe_c},
    "Э": {"A": e_a, "B": e_b, "C": e_c},
    "Я": {"A": ya_a, "B": ya_b, "C": ya_c},
}

CAP_NAMES = {"Д": "afii10021", "Ж": "afii10024", "Э": "afii10047", "Я": "afii10049"}


def build_variant_fonts() -> dict:
    """One complete font per variant (target letter replaced)."""
    from kit import DonorSource

    out = {}
    for letter, variants in VARIANTS.items():
        for tag, fn in variants.items():
            font = TTFont(BASE)
            ds = DonorSource(font)
            g = Glyph(letter)
            fn(g, ds)
            g.center_in_cell()
            glyf = font["glyf"]
            name = CAP_NAMES[letter]
            glyf[name] = emit(g)
            glyf[name].recalcBounds(glyf)
            font["hmtx"][name] = (1240, glyf[name].xMin)
            path = Path(f"/tmp/var_{ord(letter):04X}_{tag}.ttf")
            font.save(path)
            out[(letter, tag)] = path
    return out


def text_img(text, size, font):
    f = ImageFont.truetype(str(font), size)
    asc, desc = f.getmetrics()
    im = Image.new("RGB", (int(f.getlength(text)) + 30, asc + desc + 16), "#fdfcf8")
    ImageDraw.Draw(im).text((15, 8), text, font=f, fill="#161616")
    return im


def lab(text, w, size=15):
    im = Image.new("RGB", (w, 26), "#ffffff")
    ImageDraw.Draw(im).text((12, 5), text, font=ImageFont.truetype(
        "/usr/share/fonts/TTF/DejaVuSans.ttf", size), fill="#7a2d4a")
    return im


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    demo = build_variant_fonts()

    # 1. variants grid + V3 reference
    for letter, variants in VARIANTS.items():
        rows = [lab(f"{letter} — V3 (installed)", 900)]
        rows.append(text_img(letter, 150, V3))
        for tag in variants:
            rows.append(lab(f"{letter} — вариант {tag}", 900))
            rows.append(text_img(letter, 150, demo[(letter, tag)]))
        w = max(r.width for r in rows)
        h = sum(r.height for r in rows) + 6 * len(rows)
        sheet = Image.new("RGB", (w, h), "#ffffff")
        y = 0
        for r in rows:
            sheet.paste(r, (0, y))
            y += r.height + 6
        sheet.save(OUT / f"{letter}-variants.png")

    # 2. in-word comparison
    words = {
        "Д": ("Дом", ["Дом", "Дд"]),
        "Ж": ("Жизнь", ["Жизнь", "Жж"]),
        "Э": ("Это", ["Это", "Ээ"]),
        "Я": ("Яблоко", ["Яблоко", "Яя"]),
    }
    for letter, (word, _) in words.items():
        rows = [lab(f"{letter} — V3 and variants in words", 1200)]
        rows.append(lab("V3", 1200))
        rows.append(text_img(word, 52, V3))
        for tag in VARIANTS[letter]:
            rows.append(lab(f"вариант {tag}", 1200))
            rows.append(text_img(word, 52, demo[(letter, tag)]))
        w = max(r.width for r in rows)
        h = sum(r.height for r in rows) + 6 * len(rows)
        sheet = Image.new("RGB", (w, h), "#ffffff")
        y = 0
        for r in rows:
            sheet.paste(r, (0, y))
            y += r.height + 6
        sheet.save(OUT / f"{letter}-in-words.png")
    print("written to", OUT)


if __name__ == "__main__":
    main()
