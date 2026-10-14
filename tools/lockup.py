"""Logotype: the Silica icon and the name "Silica" in Inter SemiBold (600), tracking −0.02 em.

B = side of the icon's body (the 824 square of the 1024 canvas).
- horizontal: cap height 0.42 B; the centre of the x-height sits on the centre of the body; the
  name starts 0.24 B to the right of the body;
- vertical: cap height 0.25 B; the cap height starts 0.2 B below the body; the name's ink is
  centred on the body's vertical axis.
The flat logotype (mark without the body) follows the same rule with D = circle diameter in
place of B: it is used in one colour (black, white, currentColor).
"""
from __future__ import annotations

import icon
from geometry import master, num
from marks import INK, PAPER, mark_body
from text import Inter

NAME = "Silica"
TRACKING = -0.02
WEIGHT = 600
CAP_H = 0.42
CAP_V = 0.25
GAP_H = 0.24
GAP_V = 0.2
X_HEIGHT = 1118 / 1490


def placed_icon(mode: str, x: float, y: float, side: float) -> str:
    s = side / 824.0
    return (f'<g transform="translate({num(x - 100 * s)} {num(y - 100 * s)}) scale({num(s)})">'
            f'{icon.icon(mode, prefix=f"i{mode}")}</g>')


def placed_flat(color: str, x: float, y: float, side: float) -> str:
    m = master()
    s = side / (2.0 * m.radius)
    return (f'<g transform="translate({num(x - (m.cx - m.radius) * s)} {num(y - (m.cy - m.radius) * s)}) '
            f'scale({num(s)})">{mark_body(m, "mono", color)}</g>')


def text_color(mode: str, mono: str) -> str:
    if mode == "mono":
        return mono
    return INK if mode == "light" else PAPER


def _place(mode: str, x: float, y: float, side: float, mono: str) -> str:
    return placed_flat(mono, x, y, side) if mode == "mono" else placed_icon(mode, x, y, side)


def horizontal(inter: Inter, mode: str, side: float = 64.0, mono: str = "currentColor"):
    g = _place(mode, 0.0, 0.0, side, mono)
    cap = side * CAP_H
    size = inter.size_for_cap(cap)
    baseline = side / 2.0 + cap * X_HEIGHT / 2.0
    probe = inter.run(NAME, size, WEIGHT, TRACKING, 0.0, baseline, opsz=32)
    run = inter.run(NAME, size, WEIGHT, TRACKING, side + side * GAP_H - probe.left, baseline, opsz=32)
    return g + f'<path fill="{text_color(mode, mono)}" d="{run.d}"/>', run.right, side


def vertical(inter: Inter, mode: str, side: float = 64.0, mono: str = "currentColor"):
    cap = side * CAP_V
    size = inter.size_for_cap(cap)
    probe = inter.run(NAME, size, WEIGHT, TRACKING, 0.0, 0.0, opsz=32)
    tw = probe.right - probe.left
    width = max(tw, side)
    g = _place(mode, (width - side) / 2.0, 0.0, side, mono)
    baseline = side + side * GAP_V + cap
    run = inter.run(NAME, size, WEIGHT, TRACKING, (width - tw) / 2.0 - probe.left, baseline, opsz=32)
    return g + f'<path fill="{text_color(mode, mono)}" d="{run.d}"/>', width, max(baseline, run.bottom)
