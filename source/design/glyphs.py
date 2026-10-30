"""Cyrillic drawings for Cutive Mono Cyrillic — V2.

Bowls are no longer generic superellipses: they are mapped from the
original o/O outlines, so their curvature and terminals are literally the
same DNA as the Latin letters.  Everything else is assembled from the same
stems, capsule serifs and bars as the original.
"""
from __future__ import annotations

from kit import (
    ADVANCE, BAR, BOWL_T, CAP, CENTER, OVER, SERIF_H, SERIF_W, STEM, STEM_LC,
    XH, Glyph,
)

LC = STEM_LC
SW = 396
SW_N = 396
SW_T = 396
LH = 82


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def vstem(g, x, y0, y1, w=STEM):
    g.rect(x, y0, x + w, y1)


def vstem_serif(g, x, y0, y1, w=STEM, sw=SW, top=True, bottom=True):
    vstem(g, x, y0, y1, w)
    if top:
        g.serif_top(x + w / 2, y1, sw)
    if bottom:
        g.serif_bottom(x + w / 2, y0, sw)


def arm(g, p0, p1, w=STEM, cap_start=True, cap_end=False):
    """Stroke with a disc only where two strokes actually meet."""
    g.stroke([p0, p1], w, cap="butt")
    if cap_start:
        g.disc(*p0, w / 2)
    if cap_end:
        g.disc(*p1, w / 2)


def desc_tail(g, xc, top, depth, w=STEM, sw=SW, h=SERIF_H):
    """Descender tail: stem continuing below the body, ending in its serif.

    A central tail (Џ) carries the full stem serif.  A tail on the right
    stem (Ц, Ҷ) carries the same serif cut back to the body's right edge,
    so its foot never grows outside the letter's silhouette.
    """
    vstem(g, xc - w / 2, depth, top, w)
    g.serif_bottom(xc, depth, sw, h)


def side_tail(g, xc, top, depth, w=STEM, sw=SW, h=SERIF_H):
    """Right-stem descender: foot runs from the stem to the body's edge."""
    vstem(g, xc - w / 2, depth, top, w)
    g.capsule(xc - w / 2, depth, xc - w / 2 + sw, depth + h)


def hbar(g, x0, x1, y, h=BAR):
    g.capsule(x0, y, x1, y + h)


def fit_band(pts, lo, hi, w):
    """Scale a centreline vertically so the drawn band fits exactly lo..hi."""
    probe = Glyph("probe")
    probe.curve_band(pts, w)
    _, y0, _, y1 = probe.to_path().bounds
    # the band adds a constant w to the centreline's extent, so scale the
    # centreline range only.
    s = ((hi - lo) - w) / ((y1 - y0) - w)
    c0, c1 = (y0 + y1) / 2, (lo + hi) / 2
    return [(x, c1 + (y - c0) * s) for x, y in pts]


def end_serif(g, x_right, y_top, w=STEM, h=210):
    """Vertical serif at the end of a top arm (E-style)."""
    g.capsule(x_right - w, y_top - h, x_right, y_top)


def bowl(g, d, cap, cx, cy, w, h, t=BOWL_T):
    """Bowl mapped from the original o (lowercase) or O (capitals)."""
    src = "O" if cap else "o"
    d.add_box(g, src, 0, (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2))
    d.add_box(g, src, 1, (cx - (w - 2 * t) / 2, cy - (h - 2 * t) / 2,
                          cx + (w - 2 * t) / 2, cy + (h - 2 * t) / 2))
    return g


def attach_bowl(g, d, cap, stem_edge, cx, cy, w, h, t=BOWL_T, side="right"):
    """Bowl whose outer edge meets the stem's outer edge.

    The original B and b are built this way: the bowl has no wall of its own,
    the stem is the bowl's side, so the counter starts at the stem edge.  The
    bowl is mapped from the o/O donor onto a box that reaches the stem edge,
    keeping the donor width on the other side.
    """
    sw = STEM if cap else LC
    if side == "right":
        x0, x1 = stem_edge - sw, cx + w / 2
    else:
        x0, x1 = cx - w / 2, stem_edge + sw
    return bowl(g, d, cap, (x0 + x1) / 2, cy, x1 - x0, h, t)


def add_breve(g, d, src, y_min, cx=CENTER, dy=0):
    import copy

    tmp = Glyph("breve")
    d.add_above(tmp, src, y_min)
    x0, _, x1, _ = tmp.bounds()
    tmp = copy.deepcopy(tmp).shift(cx - (x0 + x1) / 2, dy)
    g.contours.extend(tmp.contours)
    return g


def corners(g, cx, cy, pts, w=STEM, sw=250, top=CAP, bottom=0):
    for x, y in pts:
        g.stroke([(cx, cy), (x, y)], w, cap="round")
        if y >= top - 1:
            g.serif_top(x, top, sw)
        else:
            g.serif_bottom(x, bottom, sw)


# ---------------------------------------------------------------------------
# capitals
# ---------------------------------------------------------------------------
def cap_be(g, d=None):
    """Б: stem + top arm + lower bowl"""
    vstem_serif(g, 265, 0, CAP, STEM, SW_N)
    hbar(g, 265, 1030, CAP - BAR)
    end_serif(g, 1030, CAP, STEM, 250)
    g.capsule(300, 0, 1015, BAR)
    attach_bowl(g, d, True, 360, 689, 398, 750, 830, 92)
    return g


def cap_ghe(g, d=None, end=True):
    """Г"""
    vstem_serif(g, 265, 0, CAP, STEM, SW_T)
    hbar(g, 265, 1030, CAP - BAR)
    if end:
        end_serif(g, 1030, CAP, STEM, 250)
    return g


def cap_de(g, d=None):
    """Д: two stems, top bar, baseline bar, short feet"""
    g.capsule(320, CAP - BAR, 975, CAP)
    vstem(g, 880, 0, CAP - BAR + 20, STEM)
    arm(g, (370, CAP - 48), (185, 40))
    g.capsule(165, 0, 1075, BAR)
    return g


def cap_zhe(g, d=None):
    """Ж: vertical stem plus four arms with slab feet"""
    vstem(g, 573, 0, CAP, STEM)
    g.serif_top(620, CAP, 240)
    g.serif_bottom(620, 0, 240)
    arm(g, (573, 585), (168, CAP - 40))
    arm(g, (573, 585), (168, 40))
    arm(g, (668, 585), (1072, CAP - 40))
    arm(g, (668, 585), (1072, 40))
    for x, y in ((155, CAP), (1085, CAP), (155, 0), (1085, 0)):
        if y:
            g.serif_top(x, CAP, 210)
        else:
            g.serif_bottom(x, 0, 210)
    return g


def cap_ze(g, d=None):
    """З: one continuous band with a proper waist turn, fitted to the cap."""
    pts = [
        (263, 1075), (597, 1160), (985, 1085), (1121, 900), (1031, 700),
        (707, 600), (383, 585), (456, 545), (707, 520), (1031, 420),
        (1121, 220), (985, 35), (597, -40), (263, 45),
    ]
    g.curve_band(fit_band(pts, -OVER, CAP + 16, BOWL_T), BOWL_T)
    g.capsule(217, 960, 313, CAP + 16)
    g.capsule(217, -OVER, 313, 220)
    return g


def cap_i(g, d=None):
    """И = mirrored N"""
    d.add(g, "N", mirror=True)
    return g


def cap_short_i(g, d=None):
    cap_i(g, d)
    add_breve(g, d, "\u0102", 1200, dy=-63)
    return g


def cap_ka(g, d=None):
    """К: own kappa construction.

    The Latin K is 1274 units wide with 602/496 serifs and its stem sits at
    the very edge of the cell.  The Cyrillic К is built from the same stems
    and 396 serifs as the rest of the alphabet: a vertical stem, and an arm
    and a leg leaving it at mid-height for a compact, evenly weighted letter.
    """
    vstem_serif(g, 265, 0, CAP, STEM, SW_N)
    j = (313, 585)
    arm(g, j, (1022, CAP - 43))
    arm(g, j, (1022, 43))
    g.serif_top(1022, CAP, SW_N)
    g.serif_bottom(1022, 0, SW_N)
    return g


def cap_el(g, d=None):
    """Л"""
    g.capsule(300, CAP - BAR, 960, CAP)
    vstem_serif(g, 865, 0, CAP - BAR, STEM, 300, top=False)
    arm(g, (340, CAP - 55), (186, 43))
    g.serif_bottom(225, 0, 620)
    return g


def cap_pe(g, d=None):
    """П"""
    vstem_serif(g, 265, 0, CAP - BAR + 20, STEM, SW_N, top=False)
    vstem_serif(g, 901, 0, CAP - BAR + 20, STEM, SW_N, top=False)
    hbar(g, 265, 996, CAP - BAR)
    return g


def cap_u(g, d=None):
    """У"""
    arm(g, (620, 800), (183, CAP - 40))
    arm(g, (620, 800), (1057, CAP - 40))
    g.serif_top(170, CAP, 320)
    g.serif_top(1070, CAP, 320)
    g.curve_band([(620, 800), (620, 200), (612, -70), (560, -230),
                  (460, -310), (360, -323)], STEM)
    return g


def cap_ef(g, d=None):
    """Ф"""
    d.add(g, "O")
    vstem(g, 573, -120, 1300, STEM)
    g.serif_bottom(620, -120, 300)
    g.serif_top(620, 1300, 300)
    return g


def tse_body(g, cap):
    """Ц/ц body: П/п turned over — baseline bar, open top, top serifs.

    The standard Ц construction: the body is П flipped vertically, so the
    bar sits on the baseline and the 396 serifs stand at cap/x-height.
    The tail is added by the caller.
    """
    if cap:
        stems = (265, 901)
        bar = (165, 1075)          # visually close to the top serif edges
        y_top, h, stem_w, sw = CAP, BAR, STEM, SW_T
        centres = (313, 949)
        stem_y0 = BAR - 20
    else:
        stems = (300, 890)
        bar = (200, 1084)
        y_top, h, stem_w, sw = XH, LH, LC, SW_T
        centres = (348, 938)
        stem_y0 = LH - 20
    g.capsule(bar[0], 0, bar[1], h)
    for x in stems:
        vstem(g, x, stem_y0, y_top, stem_w)
    for cx in centres:
        g.serif_top(cx, y_top, sw)
    return g


def cap_tse(g, d=None):
    """Ц: U-shaped body (П flipped) + Щ-style tail."""
    tse_body(g, True)
    side_tail(g, 949, BAR, -350, STEM, 246, h=BAR)
    return g


def cap_che(g, d=None):
    """Ч: the short stem rises from the bar; no serif under the junction."""
    vstem_serif(g, 250, 650, CAP, STEM, SW_T, bottom=False)
    hbar(g, 250, 960, 650)
    vstem_serif(g, 905, 0, CAP, STEM, SW_T)
    return g


def cap_sha(g, d=None, n=3):
    """Ш / Щ"""
    stems = [250, 600, 950] if n == 3 else [215, 490, 765, 1040]
    sw = 235 if n == 3 else 205
    for x in stems:
        vstem(g, x, 0, CAP - BAR + 20, STEM)
        g.serif_top(x + STEM / 2, CAP, sw)
    g.capsule(stems[0] + STEM / 2 - sw / 2, 0, stems[-1] + STEM / 2 + sw / 2, BAR)
    return g


def cap_shcha(g, d=None):
    """Щ: Ш с хвостом от правого стема (три штриха, как у Ш)"""
    cap_sha(g, d, 3)
    desc_tail(g, 998, BAR, -350, STEM, 235, h=BAR)
    return g


def cap_hard(g, d=None):
    """Ъ"""
    vstem_serif(g, 400, 0, CAP, STEM, SW_T)
    hbar(g, 150, 400, CAP - BAR)
    g.capsule(340, 0, 1010, BAR)
    attach_bowl(g, d, True, 495, 760, 398, 730, 830, 92)
    return g


def cap_yeri(g, d=None):
    """Ы"""
    vstem_serif(g, 300, 0, CAP, STEM, SW_T)
    g.capsule(290, 0, 810, BAR)
    attach_bowl(g, d, True, 394, 590, 398, 630, 830, 92)
    vstem_serif(g, 1040, 0, CAP, STEM, SW_T)
    return g


def cap_soft(g, d=None):
    """Ь"""
    vstem_serif(g, 330, 0, CAP, STEM, SW_T)
    g.capsule(290, 0, 880, BAR)
    attach_bowl(g, d, True, 425, 700, 398, 730, 830, 92)
    return g


def cap_e(g, d=None):
    """Э = mirrored C + mid bar"""
    d.add(g, "C", mirror=True)
    hbar(g, 680, 1085, 505)
    g.capsule(680, 473, 766, 623)
    return g


def cap_yu(g, d=None):
    """Ю"""
    vstem_serif(g, 150, 0, CAP, STEM, SW_T)
    bowl(g, d, True, 790, 585, 760, 1204, 92)
    hbar(g, 150, 472, 542)
    return g


def cap_ya(g, d=None):
    """Я = right stem + upper bowl + leg"""
    d.add(g, "R", mirror=True)
    g.serif_bottom(250, 0, 260)
    return g


# ---------------------------------------------------------------------------
# lowercase
# ---------------------------------------------------------------------------
def lc_be(g, d=None):
    """б: ascender at b/h height, Б-like top arm, one baseline serif."""
    vstem_serif(g, 300, 0, 1180, LC, SW)
    hbar(g, 300, 1030, 1180 - BAR)
    end_serif(g, 1030, 1180, STEM, 250)
    attach_bowl(g, d, False, 394, 690, 398, 640, 830, 92)
    return g


def lc_ve(g, d=None):
    """в"""
    vstem_serif(g, 300, 0, XH, LC, SW_T)
    attach_bowl(g, d, False, 394, 690, 235, 680, 470, 92)
    attach_bowl(g, d, False, 394, 675, 620, 640, 430, 92)
    return g


def lc_ghe(g, d=None, end=True):
    """г"""
    vstem(g, 300, 0, XH - LH, LC)
    g.serif_bottom(347, 0, 540)
    hbar(g, 300, 900, XH - LH, LH)
    if end:
        end_serif(g, 900, XH, 95, 220)
    return g


def lc_de(g, d=None):
    """д"""
    vstem(g, 240, -140, XH - LH + 20)
    vstem(g, 890, -140, XH - LH + 20)
    g.capsule(225, XH - LH, 975, XH)
    g.capsule(180, 0, 1040, LH)
    g.serif_bottom(287, -140, 260)
    g.serif_bottom(937, -140, 260)
    return g


def lc_zhe(g, d=None):
    vstem(g, 573, 0, XH, LC)
    g.serif_top(620, XH, 230)
    g.serif_bottom(620, 0, 230)
    for x, y in ((255, XH), (985, XH), (255, 0), (985, 0)):
        arm(g, (620, 400), (x + (13 if x < 620 else -13), XH - 36 if y else 36), LC)
        if y:
            g.serif_top(x, XH, 215)
        else:
            g.serif_bottom(x, 0, 215)
    return g


def lc_ze(g, d=None):
    pts = [
        (389, 760), (626, 795), (891, 750), (961, 620), (905, 480),
        (710, 415), (487, 405), (535, 375), (710, 355), (905, 290),
        (961, 150), (891, 25), (626, -20), (389, 20),
    ]
    g.curve_band(fit_band(pts, -OVER, XH, 88), 88)
    g.capsule(343, 640, 431, XH)
    g.capsule(343, -OVER, 431, 160)
    return g


def lc_i(g, d=None):
    """и"""
    vstem_serif(g, 300, 0, XH, LC, SW)
    vstem_serif(g, 890, 0, XH, LC, SW)
    g.stroke([(310, 60), (880, XH - 60)], LC, cap="flat")
    return g


def lc_short_i(g, d=None):
    lc_i(g, d)
    add_breve(g, d, "\u0103", 840, dy=-47)
    return g


def lc_ka(g, d=None):
    """к: kappa at x-height.

    A clipped Latin k keeps the shallow, high Latin arm and reads as a k with
    its ascender sawn off.  The Cyrillic к is built as its own kappa: stem,
    and an arm and a leg leaving it at mid x-height.
    """
    vstem_serif(g, 300, 0, XH, LC, SW)
    j = (348, 400)
    arm(g, j, (938, XH - 43))
    arm(g, j, (938, 43))
    g.serif_top(938, XH, SW)
    g.serif_bottom(938, 0, SW)
    return g


def lc_el(g, d=None):
    """л"""
    g.capsule(320, XH - LH, 940, XH)
    vstem_serif(g, 850, 0, XH - LH, LC, 300, top=False)
    arm(g, (360, XH - 47), (223, 43), LC)
    g.serif_bottom(260, 0, 540)
    return g


def lc_em(g, d=None):
    """м"""
    vstem_serif(g, 230, 0, XH, LC, SW)
    vstem_serif(g, 916, 0, XH, LC, SW)
    g.stroke([(277, XH - 20), (575, 380), (873, XH - 20)], LC, cap="flat")
    return g


def lc_en(g, d=None):
    """н"""
    vstem_serif(g, 300, 0, XH, LC, SW)
    vstem_serif(g, 890, 0, XH, LC, SW)
    g.capsule(300, 380, 984, 380 + LH)
    return g


def lc_pe(g, d=None):
    vstem_serif(g, 300, 0, XH - LH + 20, LC, SW, top=False)
    vstem_serif(g, 890, 0, XH - LH + 20, LC, SW, top=False)
    hbar(g, 300, 984, XH - LH, LH)
    return g


def lc_te(g, d=None):
    """т"""
    hbar(g, 260, 1040, XH - LH, LH)
    vstem(g, 603, 0, XH - LH, LC)
    g.serif_bottom(650, 0, 560)
    return g


def lc_u(g, d=None):
    arm(g, (620, 520), (330, XH - 43), LC)
    arm(g, (620, 520), (910, XH - 43), LC)
    g.serif_top(280, XH, 310)
    g.serif_top(960, XH, 310)
    g.curve_band([(620, 520), (620, 120), (615, -80), (575, -220),
                  (500, -290), (420, -325)], LC)
    return g


def lc_ef(g, d=None):
    d.add(g, "o")
    vstem(g, 573, -260, 960, LC)
    g.serif_bottom(620, -260, 300)
    g.serif_top(620, 960, 300)
    return g


def lc_ha(g, d=None):
    """х: full x-height.

    The Latin x is deliberately drawn 39 units short (774 vs 813) because
    its pointed diagonals would otherwise look oversized.  In Cyrillic the
    lowercase х sits among letters that all reach the x-height, and the
    donor contour visibly sinks.  Same width and stroke weight, redrawn at
    the full height with the same slab terminals.
    """
    g.stroke([(300, 43), (920, XH - 43)], LC, cap="butt")
    g.stroke([(300, XH - 43), (920, 43)], LC, cap="butt")
    for x in (300, 920):
        g.serif_top(x, XH, 300)
        g.serif_bottom(x, 0, 300)
    return g


def lc_tse(g, d=None):
    """ц: U-shaped body (п flipped) + Щ-style tail."""
    tse_body(g, False)
    side_tail(g, 938, LH, -330, LC, 246, h=LH)
    return g


def lc_che(g, d=None):
    vstem_serif(g, 220, 470, XH, LC, SW_T, bottom=False)
    hbar(g, 220, 955, 470, LH)
    vstem(g, 900, 0, XH, LC)
    g.serif_bottom(947, 0, 420)
    g.serif_top(947, XH, SW_T)
    return g


def lc_sha(g, d=None, n=3):
    stems = [280, 620, 960] if n == 3 else [215, 485, 755, 1025]
    sw = 230 if n == 3 else 200
    for x in stems:
        vstem(g, x, 0, XH - LH + 20, LC)
        g.serif_top(x + LC / 2, XH, sw)
    g.capsule(stems[0] + LC / 2 - sw / 2, 0, stems[-1] + LC / 2 + sw / 2, LH)
    return g


def lc_shcha(g, d=None):
    lc_sha(g, d, 3)
    desc_tail(g, 1008, LH, -330, LC, 230, h=LH)
    return g


def lc_hard(g, d=None):
    """ъ"""
    vstem_serif(g, 400, 0, XH, LC, SW)
    hbar(g, 150, 400, XH - LH)
    g.capsule(340, 0, 990, LH)
    attach_bowl(g, d, False, 494, 760, 398, 690, 830, 92)
    return g


def lc_yeri(g, d=None):
    """ы"""
    vstem_serif(g, 330, 0, XH, LC, SW)
    g.capsule(310, 0, 890, LH)
    attach_bowl(g, d, False, 424, 665, 398, 580, 830, 92)
    vstem_serif(g, 1080, 0, XH, LC, SW_T)
    return g


def lc_soft(g, d=None):
    """ь"""
    vstem_serif(g, 315, 0, XH, LC, SW)
    attach_bowl(g, d, False, 409, 700, 398, 690, 830, 92)
    return g


def lc_e(g, d=None):
    """э"""
    d.add(g, "c", mirror=True)
    hbar(g, 700, 1000, 330, LH)
    return g


def lc_yu(g, d=None):
    vstem_serif(g, 230, 0, XH, LC, SW_T)
    bowl(g, d, False, 780, 400, 660, 830, 92)
    hbar(g, 230, 480, 350)
    return g


def lc_ya(g, d=None):
    """я"""
    vstem_serif(g, 930, 0, XH, LC, SW_T)
    attach_bowl(g, d, False, 930, 750, 610, 600, 400, 92, side="left")
    g.curve_band([(840, 470), (640, 330), (470, 160), (369, 47)], LC)
    g.serif_bottom(360, 0, 340)
    return g


# ---------------------------------------------------------------------------
# registry: name -> (codepoint, builder, donor character)
# ---------------------------------------------------------------------------
CAPS = {
    "afii10017": (0x0410, None, "A"),
    "afii10018": (0x0411, cap_be, None),
    "afii10019": (0x0412, None, "B"),
    "afii10020": (0x0413, cap_ghe, None),
    "afii10021": (0x0414, cap_de, None),
    "afii10022": (0x0415, None, "E"),
    "afii10023": (0x0401, None, "\u00cb"),
    "afii10024": (0x0416, cap_zhe, None),
    "afii10025": (0x0417, cap_ze, None),
    "afii10026": (0x0418, cap_i, None),
    "afii10027": (0x0419, cap_short_i, None),
    "afii10028": (0x041A, cap_ka, None),
    "afii10029": (0x041B, cap_el, None),
    "afii10030": (0x041C, None, "M"),
    "afii10031": (0x041D, None, "H"),
    "afii10032": (0x041E, None, "O"),
    "afii10033": (0x041F, cap_pe, None),
    "afii10034": (0x0420, None, "P"),
    "afii10035": (0x0421, None, "C"),
    "afii10036": (0x0422, None, "T"),
    "afii10037": (0x0423, cap_u, None),
    "afii10038": (0x0424, cap_ef, None),
    "afii10039": (0x0425, None, "X"),
    "afii10040": (0x0426, cap_tse, None),
    "afii10041": (0x0427, cap_che, None),
    "afii10042": (0x0428, cap_sha, None),
    "afii10043": (0x0429, cap_shcha, None),
    "afii10044": (0x042A, cap_hard, None),
    "afii10045": (0x042B, cap_yeri, None),
    "afii10046": (0x042C, cap_soft, None),
    "afii10047": (0x042D, cap_e, None),
    "afii10048": (0x042E, cap_yu, None),
    "afii10049": (0x042F, cap_ya, None),
}

LOWS = {
    "afii10065": (0x0430, None, "a"),
    "afii10066": (0x0431, lc_be, None),
    "afii10067": (0x0432, lc_ve, None),
    "afii10068": (0x0433, lc_ghe, None),
    "afii10069": (0x0434, lc_de, None),
    "afii10070": (0x0435, None, "e"),
    "afii10071": (0x0451, None, "\u00eb"),
    "afii10072": (0x0436, lc_zhe, None),
    "afii10073": (0x0437, lc_ze, None),
    "afii10074": (0x0438, lc_i, None),
    "afii10075": (0x0439, lc_short_i, None),
    "afii10076": (0x043A, lc_ka, None),
    "afii10077": (0x043B, lc_el, None),
    "afii10078": (0x043C, lc_em, None),
    "afii10079": (0x043D, lc_en, None),
    "afii10080": (0x043E, None, "o"),
    "afii10081": (0x043F, lc_pe, None),
    "afii10082": (0x0440, None, "p"),
    "afii10083": (0x0441, None, "c"),
    "afii10084": (0x0442, lc_te, None),
    "afii10085": (0x0443, lc_u, None),
    "afii10086": (0x0444, lc_ef, None),
    "afii10087": (0x0445, lc_ha, None),
    "afii10088": (0x0446, lc_tse, None),
    "afii10089": (0x0447, lc_che, None),
    "afii10090": (0x0448, lc_sha, None),
    "afii10091": (0x0449, lc_shcha, None),
    "afii10092": (0x044A, lc_hard, None),
    "afii10093": (0x044B, lc_yeri, None),
    "afii10094": (0x044C, lc_soft, None),
    "afii10095": (0x044D, lc_e, None),
    "afii10096": (0x044E, lc_yu, None),
    "afii10097": (0x044F, lc_ya, None),
}
