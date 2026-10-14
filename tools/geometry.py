"""Geometry of the Silica mark (an SiO4 tetrahedron seen from above).

The mark is built from fills only: the silhouette (an equilateral triangle with rounded corners)
minus the three faces. What remains (the outline and the three spokes to the centre) is the
monochrome mark; the colour mark fills the faces and paints the rest in the rim colour.

Units: those of the variant's canvas (64 for the reference drawing, 16/24/32 for the small
variants, where 1 unit = 1 pixel).
"""
from __future__ import annotations

import math
from dataclasses import dataclass

SQ3 = math.sqrt(3.0)


@dataclass(frozen=True)
class Spec:
    canvas: float
    cx: float
    top: float
    bottom: float
    base: float
    side: float
    spoke_v: float
    spoke_d: float
    r_out: float
    r_in: float
    r_center: float


def master(canvas: float = 64.0) -> Spec:
    """Reference drawing on the 64 canvas.

    - silhouette 56 wide (4 margin = 1/16 of the canvas per side);
    - outline 5 thick;
    - spokes to the centre 4.5 (0.9 of the outline: three strokes meeting at 120° make a
      knot that weighs more than an edge);
    - outer corner radius 4 (0.8 of the outline), face radius 1.25 at the acute corners and
      1.5 at the centre;
    - optical centring: the point halfway between the centre of the silhouette's bounding box
      and its centroid sits at the centre of the canvas, so the box rises by h/12.
    """
    k = canvas / 64.0
    width = 56.0 * k
    t = 5.0 * k
    r_out = 4.0 * k
    trim = 2.0 * r_out * math.cos(math.radians(30)) - r_out
    sharp_side = width + 2.0 * trim
    sharp_h = sharp_side * SQ3 / 2.0
    height = sharp_h - r_out
    centroid_from_bottom = sharp_h / 3.0
    bbox_center_from_bottom = height / 2.0
    optical = (bbox_center_from_bottom + centroid_from_bottom) / 2.0
    bottom = canvas / 2.0 + optical
    return Spec(canvas, canvas / 2.0, bottom - height, bottom, t, t, 4.5 * k, 4.5 * k,
                r_out, 1.25 * k, 1.5 * k)


SMALL = {
    16: Spec(16, 7.5, 1.0, 14.0, 1.0, 1.1, 1.0, 1.0, 1.0, 0.2, 0.25),
    24: Spec(24, 12.0, 1.0, 20.0, 2.0, 2.1, 2.0, 1.8, 1.5, 0.35, 0.45),
    32: Spec(32, 16.0, 1.0, 27.0, 2.0, 2.5, 2.0, 2.2, 2.0, 0.45, 0.6),
}


def line(p, q):
    """Line through p and q as (n, c), with n·x = c and n a unit vector."""
    dx, dy = q[0] - p[0], q[1] - p[1]
    n = (-dy, dx)
    ln = math.hypot(*n)
    n = (n[0] / ln, n[1] / ln)
    return n, n[0] * p[0] + n[1] * p[1]


def toward(ln, point, d):
    """Shift the line by d towards the point."""
    n, c = ln
    s = 1.0 if n[0] * point[0] + n[1] * point[1] > c else -1.0
    return n, c + s * d


def meet(a, b):
    (n1, c1), (n2, c2) = a, b
    det = n1[0] * n2[1] - n1[1] * n2[0]
    return ((c1 * n2[1] - c2 * n1[1]) / det, (n1[0] * c2 - n2[0] * c1) / det)


def rounded(points, radii) -> str:
    """Convex polygon with rounded corners, as an SVG path."""
    n = len(points)
    segs = []
    for i in range(n):
        p0, p1, p2 = points[i - 1], points[i], points[(i + 1) % n]
        r = radii[i]
        u = (p0[0] - p1[0], p0[1] - p1[1])
        v = (p2[0] - p1[0], p2[1] - p1[1])
        lu, lv = math.hypot(*u), math.hypot(*v)
        u, v = (u[0] / lu, u[1] / lu), (v[0] / lv, v[1] / lv)
        ang = math.acos(max(-1.0, min(1.0, u[0] * v[0] + u[1] * v[1])))
        d = r / math.tan(ang / 2.0)
        a = (p1[0] + u[0] * d, p1[1] + u[1] * d)
        b = (p1[0] + v[0] * d, p1[1] + v[1] * d)
        cross = u[0] * v[1] - u[1] * v[0]
        sweep = 0 if cross > 0 else 1
        segs.append((a, b, r, sweep))
    out = [f"M{fmt(segs[0][0])}"]
    for i, (a, b, r, sweep) in enumerate(segs):
        if i > 0:
            out.append(f"L{fmt(a)}")
        out.append(f"A{num(r)} {num(r)} 0 0 {sweep} {fmt(b)}")
    out.append("Z")
    return "".join(out)


def rounded_bbox(points, radii) -> tuple:
    """Bounding box of a convex polygon with rounded corners (arcs sampled)."""
    xs, ys = [], []
    n = len(points)
    for i in range(n):
        p0, p1, p2 = points[i - 1], points[i], points[(i + 1) % n]
        r = radii[i]
        u = (p0[0] - p1[0], p0[1] - p1[1])
        v = (p2[0] - p1[0], p2[1] - p1[1])
        lu, lv = math.hypot(*u), math.hypot(*v)
        u, v = (u[0] / lu, u[1] / lu), (v[0] / lv, v[1] / lv)
        ang = math.acos(max(-1.0, min(1.0, u[0] * v[0] + u[1] * v[1])))
        bis = (u[0] + v[0], u[1] + v[1])
        lb = math.hypot(*bis)
        c = (p1[0] + bis[0] / lb * r / math.sin(ang / 2.0), p1[1] + bis[1] / lb * r / math.sin(ang / 2.0))
        d = r / math.tan(ang / 2.0)
        a = (p1[0] + u[0] * d - c[0], p1[1] + u[1] * d - c[1])
        b = (p1[0] + v[0] * d - c[0], p1[1] + v[1] * d - c[1])
        ta, tb = math.atan2(a[1], a[0]), math.atan2(b[1], b[0])
        delta = (tb - ta + math.pi) % (2 * math.pi) - math.pi
        for k in range(65):
            t = ta + delta * k / 64
            xs.append(c[0] + r * math.cos(t))
            ys.append(c[1] + r * math.sin(t))
    return (min(xs), min(ys), max(xs), max(ys))


def num(x: float) -> str:
    s = f"{x:.3f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def fmt(p) -> str:
    return f"{num(p[0])} {num(p[1])}"


@dataclass
class Mark:
    silhouette: str
    faces: dict[str, str]
    sharp: tuple
    mid: tuple
    junction: tuple
    bbox: tuple
    faces_bbox: tuple


def build(spec: Spec) -> Mark:
    r = spec.r_out
    height = spec.bottom - spec.top
    sharp_h = height + r
    side = sharp_h * 2.0 / SQ3
    apex = (spec.cx, spec.bottom - sharp_h)
    bl = (spec.cx - side / 2.0, spec.bottom)
    br = (spec.cx + side / 2.0, spec.bottom)
    cen = (spec.cx, spec.bottom - sharp_h / 3.0)

    l_left, l_right, l_base = line(apex, bl), line(apex, br), line(bl, br)
    in_left = toward(l_left, cen, spec.side)
    in_right = toward(l_right, cen, spec.side)
    in_base = toward(l_base, cen, spec.base)
    m_left = toward(l_left, cen, spec.side / 2.0)
    m_right = toward(l_right, cen, spec.side / 2.0)
    m_base = toward(l_base, cen, spec.base / 2.0)
    m_apex, m_bl, m_br = meet(m_left, m_right), meet(m_left, m_base), meet(m_right, m_base)
    j = ((m_apex[0] + m_bl[0] + m_br[0]) / 3.0, (m_apex[1] + m_bl[1] + m_br[1]) / 3.0)

    v_left = ((1.0, 0.0), spec.cx - spec.spoke_v / 2.0)
    v_right = ((1.0, 0.0), spec.cx + spec.spoke_v / 2.0)
    s_bl, s_br = line(j, m_bl), line(j, m_br)
    left_ref = ((apex[0] + bl[0]) / 2.0, (apex[1] + bl[1]) / 2.0)
    right_ref = ((apex[0] + br[0]) / 2.0, (apex[1] + br[1]) / 2.0)
    down = (spec.cx, spec.bottom)
    s_bl_up = toward(s_bl, left_ref, spec.spoke_d / 2.0)
    s_bl_dn = toward(s_bl, down, spec.spoke_d / 2.0)
    s_br_up = toward(s_br, right_ref, spec.spoke_d / 2.0)
    s_br_dn = toward(s_br, down, spec.spoke_d / 2.0)

    ri, rc = spec.r_in, spec.r_center
    left = [meet(in_left, v_left), meet(in_left, s_bl_up), meet(s_bl_up, v_left)]
    right = [meet(in_right, v_right), meet(v_right, s_br_up), meet(in_right, s_br_up)]
    bottom = [meet(s_bl_dn, s_br_dn), meet(in_base, s_bl_dn), meet(in_base, s_br_dn)]
    faces = {
        "left": rounded(left, [ri, ri, rc]),
        "right": rounded(right, [ri, rc, ri]),
        "bottom": rounded(bottom, [rc, ri, ri]),
    }
    sil = rounded([apex, br, bl], [r, r, r])
    trim = 2.0 * r * math.cos(math.radians(30)) - r
    bbox = (bl[0] + trim, spec.top, br[0] - trim, spec.bottom)
    boxes = [rounded_bbox(left, [ri, ri, rc]), rounded_bbox(right, [ri, rc, ri]),
             rounded_bbox(bottom, [rc, ri, ri])]
    faces_bbox = (min(b[0] for b in boxes), min(b[1] for b in boxes),
                  max(b[2] for b in boxes), max(b[3] for b in boxes))
    return Mark(sil, faces, (apex, br, bl), (m_apex, m_br, m_bl), j, bbox, faces_bbox)
