"""Design kit for Cutive Mono Cyrillic.

Coordinates are font units (UPM 2048).  Geometry is derived from the
original Cutive Mono Regular:

    cap height       1171        advance          1240
    x-height          813        descender        -350
    overshoot          17        cap stem width     95
    lowercase stem     94        horizontal bar     86
    serif             396 x 86, fully rounded ends (r = 43)
    bowl weight       ~92, superellipse exponent 2.1

Primitives emit separate overlapping contours.  Overlaps are removed once
at the end by fontTools' skia-pathops based removeOverlaps().
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen

UPM = 2048
ADVANCE = 1240

CAP = 1171
XH = 813
OVER = 17
DESC = -350

STEM = 96
STEM_LC = 96
BAR = 86
SERIF_H = 86
SERIF_W = 396
BOWL_N = 2.1
BOWL_T = 92

CENTER = ADVANCE / 2

K = 0.5523


@dataclass
class Contour:
    start: tuple
    segments: list = field(default_factory=list)


class Glyph:
    def __init__(self, name: str, width: int = ADVANCE):
        self.name = name
        self.width = width
        self.contours: list[Contour] = []

    # ------------------------------------------------------------------
    def _add(self, start, segments):
        self.contours.append(Contour(start, list(segments)))

    def poly(self, pts):
        self._add(pts[0], [("l", p) for p in pts[1:]])

    def map_points(self, fn):
        out = []
        for c in self.contours:
            out.append(Contour(fn(*c.start),
                               [(s[0], *[fn(*p) for p in s[1:]]) for s in c.segments]))
        self.contours = out
        return self

    def shift(self, dx=0.0, dy=0.0):
        return self.map_points(lambda x, y: (x + dx, y + dy))

    def bounds(self):
        xs, ys = [], []
        for c in self.contours:
            xs.append(c.start[0])
            ys.append(c.start[1])
            for s in c.segments:
                for p in s[1:]:
                    xs.append(p[0])
                    ys.append(p[1])
        if not xs:
            return (0, 0, 0, 0)
        return min(xs), min(ys), max(xs), max(ys)

    def center_in_cell(self, cx=CENTER):
        x0, _, x1, _ = self.bounds()
        return self.shift(cx - (x0 + x1) / 2)

    def flip_x(self, axis=CENTER):
        return self.map_points(lambda x, y: (2 * axis - x, y))

    def flip_y(self, axis=0.0):
        return self.map_points(lambda x, y: (x, 2 * axis - y))

    # -- primitives ----------------------------------------------------
    def rect(self, x0, y0, x1, y1):
        self.poly([(x0, y0), (x0, y1), (x1, y1), (x1, y0)])
        return self

    def stem(self, x, y0, y1, w=STEM):
        return self.rect(x, y0, x + w, y1)

    def capsule(self, x0, y0, x1, y1):
        w, h = x1 - x0, y1 - y0
        if w <= 0 or h <= 0:
            return self
        if w >= h:
            self._capsule_h(x0, x1, y0, y1)
        else:
            self._capsule_v(x0, x1, y0, y1)
        self._reverse_contour(-1)
        return self

    def _capsule_h(self, x0, x1, y0, y1):
        r = (y1 - y0) / 2
        yc = y0 + r
        k = K * r
        self._add((x0 + r, y0), [
            ("l", (x1 - r, y0)),
            ("c", (x1 - r + k, y0), (x1, yc - r + k), (x1, yc)),
            ("c", (x1, yc + r - k), (x1 - r + k, y1), (x1 - r, y1)),
            ("l", (x0 + r, y1)),
            ("c", (x0 + r - k, y1), (x0, yc + r - k), (x0, yc)),
            ("c", (x0, yc - r + k), (x0 + r - k, y0), (x0 + r, y0)),
        ])

    def _capsule_v(self, x0, x1, y0, y1):
        r = (x1 - x0) / 2
        xc = x0 + r
        k = K * r
        self._add((xc, y0), [
            ("c", (xc + r - k, y0), (x1, y0 + r - k), (x1, y0 + r)),
            ("l", (x1, y1 - r)),
            ("c", (x1, y1 - r + k), (xc + r - k, y1), (xc, y1)),
            ("c", (xc - r + k, y1), (x0, y1 - r + k), (x0, y1 - r)),
            ("l", (x0, y0 + r)),
            ("c", (x0, y0 + r - k), (xc - r + k, y0), (xc, y0)),
        ])

    def bar(self, x0, x1, y, h=BAR):
        return self.capsule(x0, y, x1, y + h)

    def serif(self, xc, y, w=SERIF_W, h=SERIF_H):
        return self.capsule(xc - w / 2, y, xc + w / 2, y + h)

    def serif_top(self, xc, top=CAP, w=SERIF_W, h=SERIF_H):
        return self.serif(xc, top - h, w, h)

    def serif_bottom(self, xc, bottom=0, w=SERIF_W, h=SERIF_H):
        return self.serif(xc, bottom, w, h)

    # -- bowls ---------------------------------------------------------
    def ring(self, cx, cy, a, b, t=BOWL_T, t0=0.0, t1=360.0, n=BOWL_N, steps=None):
        """Superellipse ring or constant-weight arc band."""
        full = abs(t1 - t0) >= 359.999
        if steps is None:
            steps = max(6, int(abs(t1 - t0) / 90 * 6) + 1)
        if full:
            pts, tans = _arc_samples(cx, cy, a, b, n, 0, 360, 20)
            self._add(pts[0], _spline(pts, tans, closed=True))
            pts, tans = _arc_samples(cx, cy, a - t, b - t, n, 0, 360, 20)
            self._add(pts[0], _spline(pts, tans, closed=True))
            self._reverse_contour(-1)
            return self
        pts, tans = _arc_samples(cx, cy, a, b, n, t0, t1, steps)
        c = _band(pts, tans, t)
        self.contours.append(c)
        return self

    def band(self, pts, tans, w=92):
        """Constant-width band with round terminals through a centreline."""
        self.contours.append(_band(pts, tans, w))
        return self

    # -- strokes -------------------------------------------------------
    def _reverse_contour(self, index):
        """Reverse one contour, keeping lines, cubics and TrueType quads."""
        c = self.contours[index]
        nodes = [(c.start, [], "l")]
        for seg in c.segments:
            if seg[0] == "l":
                nodes.append((seg[1], [], "l"))
            elif seg[0] == "c":
                nodes.append((seg[3], [seg[1], seg[2]], "c"))
            elif seg[0] == "q":
                nodes.append((seg[-1], list(seg[1:-1]), "q"))
        rev = []
        for i in range(len(nodes) - 1, 0, -1):
            _, ctrl, kind = nodes[i]
            p_from = nodes[i - 1][0]
            if kind == "l":
                rev.append(("l", p_from))
            elif kind == "c":
                rev.append(("c", ctrl[1], ctrl[0], p_from))
            else:
                rev.append(("q", *reversed(ctrl), p_from))
        self.contours[index] = Contour(nodes[-1][0], rev)

    def stroke(self, pts, w=STEM, cap="round"):
        h = w / 2
        for i in range(len(pts) - 1):
            (x0, y0), (x1, y1) = pts[i], pts[i + 1]
            dx, dy = x1 - x0, y1 - y0
            ln = math.hypot(dx, dy) or 1
            nx, ny = -dy / ln * h, dx / ln * h
            quad = [(x0 - nx, y0 - ny), (x1 - nx, y1 - ny),
                    (x1 + nx, y1 + ny), (x0 + nx, y0 + ny)]
            area = sum(quad[i][0] * quad[(i + 1) % 4][1] - quad[(i + 1) % 4][0] * quad[i][1]
                       for i in range(4))
            if area > 0:
                quad.reverse()
            self.poly(quad)
        for i in range(1, len(pts) - 1):
            self.disc(*pts[i], h)
        if cap == "round":
            self.disc(*pts[0], h)
            self.disc(*pts[-1], h)
        return self

    def stroke_arc(self, cx, cy, a, b, t0, t1, w=92, n=BOWL_N, steps=None, tangent=None):
        """Constant-weight band along a superellipse centreline arc."""
        if steps is None:
            steps = max(6, int(abs(t1 - t0) / 90 * 6) + 1)
        pts, tans = _arc_samples(cx, cy, a, b, n, t0, t1, steps)
        if tangent is not None:
            pts, tans = tangent(pts, tans)
        self.band(pts, tans, w)
        return self

    def curve_band(self, pts, w=STEM):
        """Smooth constant-width band through points (Catmull-Rom tangents)."""
        n = len(pts)
        p = [pts[0]] + list(pts) + [pts[-1]]
        out_p, out_t = [], []
        for i in range(1, n + 1):
            prev, cur, nxt = p[i - 1], p[i], p[i + 1]
            tx = (nxt[0] - prev[0]) / 2
            ty = (nxt[1] - prev[1]) / 2
            ln = math.hypot(tx, ty) or 1
            out_p.append(cur)
            out_t.append((tx / ln, ty / ln))
        return self.band(out_p, out_t, w)

    # -- boolean editing ------------------------------------------------
    def to_path(self):
        import pathops

        p = pathops.Path()
        pen = p.getPen()
        for c in self.contours:
            pen.moveTo(c.start)
            for seg in c.segments:
                if seg[0] == "l":
                    pen.lineTo(seg[1])
                elif seg[0] == "c":
                    pen.curveTo(seg[1], seg[2], seg[3])
                elif seg[0] == "q":
                    pen.qCurveTo(*seg[1:])
            pen.closePath()
        return p

    def from_path(self, p):
        self.contours = []
        cur = None
        last = (0.0, 0.0)
        for verb, pts in p.segments:
            if verb == "moveTo":
                cur = Contour(pts[0], [])
                self.contours.append(cur)
                last = pts[0]
                continue
            if verb in ("closePath", "endPath", "close"):
                cur = None
                continue
            if cur is None:
                cur = Contour(last, [])
                self.contours.append(cur)
            if verb == "lineTo":
                cur.segments.append(("l", pts[0]))
                last = pts[0]
            elif verb in ("curveTo", "cubicTo"):
                cur.segments.append(("c", pts[0], pts[1], pts[2]))
                last = pts[2]
            elif verb in ("qCurveTo", "quadTo"):
                q = [x for x in pts if x is not None]
                if q:
                    cur.segments.append(("q", *q))
                    last = q[-1]
        return self

    def clip(self, x0, y0, x1, y1):
        """Keep only the part of the drawing inside the rectangle."""
        import pathops

        r = pathops.Path()
        pen = r.getPen()
        pen.moveTo((x0, y0))
        pen.lineTo((x1, y0))
        pen.lineTo((x1, y1))
        pen.lineTo((x0, y1))
        pen.closePath()
        out = pathops.Path()
        pathops.intersection([self.to_path()], [r], out.getPen())
        return self.from_path(out)

    def disc(self, cx, cy, r):
        self._capsule_v(cx - r, cx + r, cy - r, cy + r)
        self._reverse_contour(-1)
        return self


# ---------------------------------------------------------------------------
def _arc_samples(cx, cy, a, b, n, deg0, deg1, steps):
    e = 2 / n

    def pt(deg):
        r = math.radians(deg)
        c, s = math.cos(r), math.sin(r)
        return (cx + a * (abs(c) ** e) * (1 if c >= 0 else -1),
                cy + b * (abs(s) ** e) * (1 if s >= 0 else -1))

    if steps <= 0:
        return [pt(deg0)], [(1.0, 0.0)]

    pts, tans = [], []
    h = 1e-4
    for i in range(steps + 1):
        deg = deg0 + (deg1 - deg0) * i / steps
        pts.append(pt(deg))
        p1 = pt(deg + h * 180 / math.pi)
        p0 = pt(deg - h * 180 / math.pi)
        dx, dy = (p1[0] - p0[0]) / (2 * h), (p1[1] - p0[1]) / (2 * h)
        ln = math.hypot(dx, dy) or 1.0
        tans.append((dx / ln, dy / ln))
    return pts, tans


def _band(pts, tans, w):
    """Closed outline of a constant-width band with round end caps."""
    h = w / 2
    outer, ot, inner, it = [], [], [], []
    for p, tn in zip(pts, tans):
        nx, ny = -tn[1], tn[0]
        outer.append((p[0] + nx * h, p[1] + ny * h))
        ot.append(tn)
        inner.append((p[0] - nx * h, p[1] - ny * h))
        it.append(tn)

    def cap(center, a_pt, b_pt, direction, samples=5):
        v = (a_pt[0] - center[0], a_pt[1] - center[1])
        r = math.hypot(*v)
        u = (v[0] / r, v[1] / r)
        wv = direction
        cp, ct = [], []
        for i in range(samples):
            th = math.pi * i / (samples - 1)
            cp.append((center[0] + r * (u[0] * math.cos(th) + wv[0] * math.sin(th)),
                       center[1] + r * (u[1] * math.cos(th) + wv[1] * math.sin(th))))
            ct.append((-u[0] * math.sin(th) + wv[0] * math.cos(th),
                       -u[1] * math.sin(th) + wv[1] * math.cos(th)))
        return cp, ct

    end_c = ((outer[-1][0] + inner[-1][0]) / 2, (outer[-1][1] + inner[-1][1]) / 2)
    cap_end_p, cap_end_t = cap(end_c, outer[-1], inner[-1], tans[-1])
    start_c = ((outer[0][0] + inner[0][0]) / 2, (outer[0][1] + inner[0][1]) / 2)
    cap_start_p, cap_start_t = cap(start_c, inner[0], outer[0], (-tans[0][0], -tans[0][1]))

    all_p = outer + cap_end_p + list(reversed(inner)) + cap_start_p
    all_t = ot + cap_end_t + [(-x, -y) for x, y in reversed(it)] + cap_start_t
    all_t = [(x / (math.hypot(x, y) or 1), y / (math.hypot(x, y) or 1)) for x, y in all_t]
    area = sum(all_p[i][0] * all_p[(i + 1) % len(all_p)][1]
               - all_p[(i + 1) % len(all_p)][0] * all_p[i][1] for i in range(len(all_p)))
    if area > 0:
        all_p.reverse()
        all_t.reverse()
    return Contour(all_p[0], _spline(all_p, all_t, closed=True))


def _spline(pts, tans, closed=True):
    """Cubic segments through points with unit tangents.

    Handle length follows the circular-arc formula, which is also the
    correct limit for smooth curves sampled at a moderate density.
    """
    n = len(pts)
    m = n if closed else n - 1
    segs = []
    for i in range(m):
        p0, p1 = pts[i], pts[(i + 1) % n]
        t0, t1 = tans[i], tans[(i + 1) % n]
        chord = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
        dot = max(-1.0, min(1.0, t0[0] * t1[0] + t0[1] * t1[1]))
        phi = math.acos(dot)
        if chord < 1e-6:
            k = 0.0
        elif phi < 1e-4:
            k = chord / 3
        else:
            denom = 2 * math.sin(phi / 2)
            k = (2 * chord / 3) * (math.tan(phi / 4) / denom) if denom else chord / 3
            k = min(k, chord * 1.2)
        segs.append(("c",
                     (p0[0] + t0[0] * k, p0[1] + t0[1] * k),
                     (p1[0] - t1[0] * k, p1[1] - t1[1] * k),
                     p1))
    return segs


class DonorSource:
    """Reads contours (components decomposed) from the original font."""

    def __init__(self, font):
        self.font = font
        self.glyphset = font.getGlyphSet()
        self.cmap = font.getBestCmap()
        self.glyf = font["glyf"]

    def contours(self, name: str):
        from fontTools.pens.recordingPen import DecomposingRecordingPen

        if len(name) == 1:
            name = self.cmap[ord(name)]
        pen = DecomposingRecordingPen(self.glyphset)
        self.glyphset[name].draw(pen)
        out, cur = [], None
        for op, args in pen.value:
            if op == "moveTo":
                cur = {"start": args[0], "segs": []}
                out.append(cur)
            elif op == "lineTo":
                cur["segs"].append(("l", args[0]))
            elif op == "qCurveTo":
                cur["segs"].append(("q", *[p for p in args if p is not None]))
            elif op == "curveTo":
                cur["segs"].append(("c", *args))
            elif op in ("closePath", "endPath"):
                cur = None
        return out

    def add(self, g: Glyph, name: str, dx=0.0, dy=0.0, mirror=False, axis=CENTER,
            sx=1.0, sy=1.0, y_min=None, index=None):
        def tf(p):
            x, y = p
            if mirror:
                x = 2 * axis - x
            if sx != 1.0:
                x = axis + (x - axis) * sx
            y *= sy
            return (x + dx, y + dy)

        all_contours = self.contours(name)
        if index is not None:
            all_contours = [all_contours[index]]
        first = len(g.contours)
        for c in all_contours:
            ys = [c["start"][1]] + [q[1] for s in c["segs"] for q in s[1:]]
            if y_min is not None and min(ys) < y_min:
                continue
            segs = []
            for s in c["segs"]:
                if s[0] == "l":
                    segs.append(("l", tf(s[1])))
                elif s[0] == "c":
                    segs.append(("c", tf(s[1]), tf(s[2]), tf(s[3])))
                elif s[0] == "q":
                    segs.append(("q", *[tf(p) for p in s[1:]]))
            g._add(tf(c["start"]), segs)
        if mirror or sx < 0:
            # a mirror flips the winding; cut it back so that the kit's
            # clockwise primitives still add instead of cancelling
            for i in range(first, len(g.contours)):
                g._reverse_contour(i)
        return g

    def add_box(self, g: Glyph, name: str, index: int, box, flip_x=False, flip_y=False):
        """Copy one contour and map its bbox onto box=(x0,y0,x1,y1)."""
        cs = self.contours(name)
        c = cs[index]
        xs = [c["start"][0]] + [q[0] for sc in c["segs"] for q in sc[1:]]
        ys = [c["start"][1]] + [q[1] for sc in c["segs"] for q in sc[1:]]
        sx0, sy0, sx1, sy1 = min(xs), min(ys), max(xs), max(ys)
        tx0, ty0, tx1, ty1 = box
        fx = (tx1 - tx0) / ((sx1 - sx0) or 1)
        fy = (ty1 - ty0) / ((sy1 - sy0) or 1)

        def tf(p):
            x = tx0 + (p[0] - sx0) * fx
            y = ty0 + (p[1] - sy0) * fy
            if flip_x:
                x = tx0 + tx1 - x
            if flip_y:
                y = ty0 + ty1 - y
            return (x, y)

        segs = []
        for sc in c["segs"]:
            if sc[0] == "l":
                segs.append(("l", tf(sc[1])))
            elif sc[0] == "c":
                segs.append(("c", tf(sc[1]), tf(sc[2]), tf(sc[3])))
            elif sc[0] == "q":
                segs.append(("q", *[tf(q) for q in sc[1:]]))
        g._add(tf(c["start"]), segs)
        return g

    def add_above(self, g: Glyph, name: str, y_min: float):
        return self.add(g, name, y_min=y_min)


def emit(g: Glyph):
    ttpen = TTGlyphPen(None)
    pen = Cu2QuPen(ttpen, max_err=0.4, reverse_direction=False)
    for c in g.contours:
        pen.moveTo(c.start)
        for s in c.segments:
            if s[0] == "l":
                pen.lineTo(s[1])
            elif s[0] == "c":
                pen.curveTo(s[1], s[2], s[3])
            elif s[0] == "q":
                pen.qCurveTo(*s[1:])
        pen.closePath()
    return ttpen.glyph()
