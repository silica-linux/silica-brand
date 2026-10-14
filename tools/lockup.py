"""Logotipo: marchio e nome «Silica» in Inter SemiBold (600), spaziatura −0,02 em.

Proporzioni, con H = altezza della sagoma del marchio:
- orizzontale: maiuscola alta H × 0,5, linea di base sulla base del marchio, luce H × 0,3;
- verticale: maiuscola alta H × 0,382 (H / φ²), luce H × 0,3, nome centrato sotto.
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


def placed_mark(mode: str, x: float, y: float, height: float, mono: str) -> tuple[str, float]:
    m = build(master())
    bx0, by0, bx1, by1 = m.bbox
    s = height / (by1 - by0)
    body = mark_body(m, mode, mono)
    g = f'<g transform="translate({num(x - bx0 * s)} {num(y - by0 * s)}) scale({num(s)})">{body}</g>'
    return g, (bx1 - bx0) * s


def text_color(mode: str, mono: str) -> str:
    if mode == "mono":
        return mono
    return INK if mode == "light" else PAPER


def horizontal(inter: Inter, mode: str, height: float = 64.0, mono: str = "currentColor"):
    g, mw = placed_mark(mode, 0.0, 0.0, height, mono)
    size = inter.size_for_cap(height * CAP_H)
    probe = inter.run(NAME, size, WEIGHT, TRACKING, 0.0, height, opsz=32)
    x = mw + height * GAP - probe.left
    run = inter.run(NAME, size, WEIGHT, TRACKING, x, height, opsz=32)
    width = run.right
    bottom = max(height, run.bottom)
    body = g + f'<path fill="{text_color(mode, mono)}" d="{run.d}"/>'
    return body, width, bottom


def vertical(inter: Inter, mode: str, height: float = 64.0, mono: str = "currentColor"):
    size = inter.size_for_cap(height * CAP_V)
    probe = inter.run(NAME, size, WEIGHT, TRACKING, 0.0, 0.0, opsz=32)
    tw = probe.right - probe.left
    m = build(master())
    bx0, by0, bx1, by1 = m.bbox
    mw = (bx1 - bx0) * height / (by1 - by0)
    width = max(tw, mw)
    g, _ = placed_mark(mode, (width - mw) / 2.0, 0.0, height, mono)
    baseline = height + height * GAP + height * CAP_V
    run = inter.run(NAME, size, WEIGHT, TRACKING, (width - tw) / 2.0 - probe.left, baseline, opsz=32)
    body = g + f'<path fill="{text_color(mode, mono)}" d="{run.d}"/>'
    return body, width, max(baseline, run.bottom)
