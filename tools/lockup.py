"""Logotype: the mark and the name "Silica" in Inter SemiBold (600), tracking −0.02 em.

The name aligns to the faces of the mark, the part that is visible on every background (the rim
blends into the background in both colour versions). H = height of the mark's silhouette.
- horizontal: cap height 0.5 H; baseline on the bottom edge of the lower face; the name starts
  0.3 H to the right of the faces;
- vertical: cap height 0.382 H (H / φ²); the cap height starts 0.3 H below the lower face; the
  name's ink is centred on the mark's axis.
The same rule holds for the light, dark and monochrome versions.
"""
from __future__ import annotations

from geometry import build, master, num
from marks import INK, PAPER, mark_body
from text import Inter

NAME = "Silica"
TRACKING = -0.02
WEIGHT = 600
CAP_H = 0.5
CAP_V = 0.382
GAP = 0.3


def metrics(height: float):
    """Scale and face block of the reference mark for a silhouette of the given height."""
    m = build(master())
    bx0, by0, bx1, by1 = m.bbox
    s = height / (by1 - by0)
    fx0, fy0, fx1, fy1 = m.faces_bbox
    return m, s, (bx1 - bx0) * s, ((fx0 - bx0) * s, (fy0 - by0) * s, (fx1 - bx0) * s, (fy1 - by0) * s)


def placed_mark(mode: str, x: float, y: float, height: float, mono: str) -> str:
    m, s, _, _ = metrics(height)
    body = mark_body(m, mode, mono)
    return f'<g transform="translate({num(x - m.bbox[0] * s)} {num(y - m.bbox[1] * s)}) scale({num(s)})">{body}</g>'


def text_color(mode: str, mono: str) -> str:
    if mode == "mono":
        return mono
    return INK if mode == "light" else PAPER


def horizontal(inter: Inter, mode: str, height: float = 64.0, mono: str = "currentColor"):
    _, _, mw, faces = metrics(height)
    g = placed_mark(mode, 0.0, 0.0, height, mono)
    size = inter.size_for_cap(height * CAP_H)
    baseline = faces[3]
    probe = inter.run(NAME, size, WEIGHT, TRACKING, 0.0, baseline, opsz=32)
    run = inter.run(NAME, size, WEIGHT, TRACKING, faces[2] + height * GAP - probe.left, baseline, opsz=32)
    body = g + f'<path fill="{text_color(mode, mono)}" d="{run.d}"/>'
    return body, run.right, max(height, run.bottom)


def vertical(inter: Inter, mode: str, height: float = 64.0, mono: str = "currentColor"):
    _, _, mw, faces = metrics(height)
    size = inter.size_for_cap(height * CAP_V)
    probe = inter.run(NAME, size, WEIGHT, TRACKING, 0.0, 0.0, opsz=32)
    tw = probe.right - probe.left
    width = max(tw, mw)
    g = placed_mark(mode, (width - mw) / 2.0, 0.0, height, mono)
    baseline = faces[3] + height * GAP + height * CAP_V
    run = inter.run(NAME, size, WEIGHT, TRACKING, (width - tw) / 2.0 - probe.left, baseline, opsz=32)
    body = g + f'<path fill="{text_color(mode, mono)}" d="{run.d}"/>'
    return body, width, max(baseline, run.bottom)
