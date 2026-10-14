"""Geometry of the Silica mark: from sand to glass.

A circle split along its vertical diameter. The right half is solid (glass); the left half is
sand: round grains on a hexagonal grid, clipped whole by the circle, growing towards the
diameter, where they are about to melt into the glass.

Units: those of the variant's canvas (64 for the reference drawing; 16, 24 and 32 for the
small variants, where 1 unit = 1 pixel).
"""
from __future__ import annotations

import math
from dataclasses import dataclass

SQ3 = math.sqrt(3.0)


@dataclass(frozen=True)
class Mark:
    canvas: float
    cx: float
    cy: float
    radius: float
    grains: tuple
    columns: tuple
    pixel: bool = False

    @property
    def bbox(self) -> tuple:
        return (self.cx - self.radius, self.cy - self.radius, self.cx + self.radius, self.cy + self.radius)


@dataclass(frozen=True)
class Grid:
    """Hexagonal grain grid of the reference drawing (canvas 64)."""

    radius: float = 28.0
    pitch: float = 5.2
    columns: int = 6
    first: float = 3.6
    r_first: float = 2.2
    r_last: float = 0.85


GRID = Grid()


def column_x(cx: float, g: Grid, k: int) -> float:
    return cx - g.first - k * g.pitch * SQ3 / 2.0


def grain_radius(g: Grid, k: int) -> float:
    t = k / (g.columns - 1)
    return g.r_first + (g.r_last - g.r_first) * t


def master(canvas: float = 64.0) -> Mark:
    """Reference drawing.

    - circle radius 28 (diameter 56, margin 4 = 1/16 of the canvas per side);
    - grains on a hexagonal grid with pitch 5.2 (rows 5.2 apart, columns 5.2·√3/2 = 4.503
      apart, odd columns shifted by half a pitch): every grain has six neighbours at the same
      distance;
    - six columns; the grain radius falls linearly from 2.2 next to the diameter to 0.85 at
      the outer column (the sand gets coarser as it nears the heat and the glass);
    - the first column is 3.6 from the diameter: a clear gap of 1.4, 1.75 times the gap
      between the grains of that column (5.2 − 2 × 2.2 = 0.8), so the glass reads as one
      body and the grains as separate;
    - a grain is kept only if it lies wholly inside the circle, 0.4 in from the outline.
    """
    g = GRID
    k = canvas / 64.0
    cx = cy = canvas / 2.0
    grains = []
    cols = []
    for c in range(g.columns):
        x = column_x(32.0, g, c)
        r = grain_radius(g, c)
        off = 0.5 if c % 2 else 0.0
        col = []
        for j in range(-8, 9):
            y = 32.0 + (j + off) * g.pitch
            if math.hypot(x - 32.0, y - 32.0) + r <= g.radius - 0.4:
                col.append((x * k, y * k, r * k))
        grains.extend(col)
        cols.append((x * k, r * k, len(col)))
    return Mark(canvas, cx, cy, g.radius * k, tuple(grains), tuple(cols))


def _small(canvas: float, cx: float, cy: float, radius: float, grains) -> Mark:
    return Mark(canvas, cx, cy, radius, tuple(grains), (), True)


# Small variants, drawn on the pixel grid. Grains are squares of whole pixels with rounded
# corners, largest next to the diameter (3 px at 16, 4 px at 24 and 32) and smaller outwards,
# with at least one clear pixel between grains and between the first column and the glass.
# The diameter falls on a pixel edge. 16 px: three grains (2 + 1); 24 px: five (3 + 2);
# 32 px: ten (3 + 4 + 3).
SMALL = {
    16: _small(16, 8.0, 8.0, 7.0, [(5.5, 5.5, 1.5), (5.5, 10.5, 1.5), (2.0, 8.0, 1.0)]),
    24: _small(24, 12.0, 12.0, 10.5, [
        (9.0, 7.0, 2.0), (9.0, 12.0, 2.0), (9.0, 17.0, 2.0),
        (4.5, 9.5, 1.5), (4.5, 14.5, 1.5),
    ]),
    32: _small(32, 16.0, 16.0, 14.0, [
        (13.0, 11.0, 2.0), (13.0, 16.0, 2.0), (13.0, 21.0, 2.0),
        (8.5, 8.5, 1.5), (8.5, 13.5, 1.5), (8.5, 18.5, 1.5), (8.5, 23.5, 1.5),
        (5.0, 11.0, 1.0), (5.0, 16.0, 1.0), (5.0, 21.0, 1.0),
    ]),
}


def num(x: float) -> str:
    s = f"{x:.3f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def glass_path(m: Mark) -> str:
    top = (m.cx, m.cy - m.radius)
    bottom = (m.cx, m.cy + m.radius)
    r = num(m.radius)
    return f"M{num(top[0])} {num(top[1])}A{r} {r} 0 0 1 {num(bottom[0])} {num(bottom[1])}Z"


def grain_path(x: float, y: float, r: float) -> str:
    rr = num(r)
    return (f"M{num(x - r)} {num(y)}A{rr} {rr} 0 1 0 {num(x + r)} {num(y)}"
            f"A{rr} {rr} 0 1 0 {num(x - r)} {num(y)}Z")


def pixel_grain_path(x: float, y: float, r: float) -> str:
    """A grain of the small variants: a square of whole pixels with rounded corners (0.3 × side),
    so that every pixel it covers is almost fully inked."""
    c = 0.6 * r
    x0, y0, x1, y1 = x - r, y - r, x + r, y + r
    cc = num(c)
    return (f"M{num(x0 + c)} {num(y0)}H{num(x1 - c)}A{cc} {cc} 0 0 1 {num(x1)} {num(y0 + c)}"
            f"V{num(y1 - c)}A{cc} {cc} 0 0 1 {num(x1 - c)} {num(y1)}H{num(x0 + c)}"
            f"A{cc} {cc} 0 0 1 {num(x0)} {num(y1 - c)}V{num(y0 + c)}A{cc} {cc} 0 0 1 {num(x0 + c)} {num(y0)}Z")


def sand_path(m: Mark) -> str:
    draw = pixel_grain_path if m.pixel else grain_path
    return "".join(draw(x, y, r) for x, y, r in m.grains if r > 0)
