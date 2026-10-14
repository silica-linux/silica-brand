"""Logotype: the mark and the name "Silica" in Inter SemiBold (600), tracking −0.02 em.

D = diameter of the mark's circle.
- horizontal: cap height 0.5 D; the centre of the x-height sits on the centre of the circle
  (the optical centre of a circle is its geometric centre); the name starts 0.25 D to the right
  of the circle;
- vertical: cap height 0.3 D; the cap height starts 0.25 D below the circle; the name's ink is
  centred on the circle's vertical axis.
The same rule holds for the light, dark and monochrome versions.
"""
from __future__ import annotations

from geometry import master, num
from marks import INK, PAPER, mark_body
from text import Inter

NAME = "Silica"
TRACKING = -0.02
WEIGHT = 600
CAP_H = 0.5
CAP_V = 0.3
GAP_H = 0.25
GAP_V = 0.25
X_HEIGHT = 1118 / 1490


def placed_mark(mode: str, x: float, y: float, diameter: float, mono: str) -> str:
    m = master()
    s = diameter / (2.0 * m.radius)
    bx, by = m.cx - m.radius, m.cy - m.radius
    return (f'<g transform="translate({num(x - bx * s)} {num(y - by * s)}) scale({num(s)})">'
            f'{mark_body(m, mode, mono)}</g>')


def text_color(mode: str, mono: str) -> str:
    if mode == "mono":
        return mono
    return INK if mode == "light" else PAPER


def horizontal(inter: Inter, mode: str, diameter: float = 64.0, mono: str = "currentColor"):
    g = placed_mark(mode, 0.0, 0.0, diameter, mono)
    cap = diameter * CAP_H
    size = inter.size_for_cap(cap)
    baseline = diameter / 2.0 + cap * X_HEIGHT / 2.0
    probe = inter.run(NAME, size, WEIGHT, TRACKING, 0.0, baseline, opsz=32)
    run = inter.run(NAME, size, WEIGHT, TRACKING, diameter + diameter * GAP_H - probe.left, baseline, opsz=32)
    body = g + f'<path fill="{text_color(mode, mono)}" d="{run.d}"/>'
    return body, run.right, diameter


def vertical(inter: Inter, mode: str, diameter: float = 64.0, mono: str = "currentColor"):
    cap = diameter * CAP_V
    size = inter.size_for_cap(cap)
    probe = inter.run(NAME, size, WEIGHT, TRACKING, 0.0, 0.0, opsz=32)
    tw = probe.right - probe.left
    width = max(tw, diameter)
    g = placed_mark(mode, (width - diameter) / 2.0, 0.0, diameter, mono)
    baseline = diameter + diameter * GAP_V + cap
    run = inter.run(NAME, size, WEIGHT, TRACKING, (width - tw) / 2.0 - probe.left, baseline, opsz=32)
    body = g + f'<path fill="{text_color(mode, mono)}" d="{run.d}"/>'
    return body, width, max(baseline, run.bottom)
