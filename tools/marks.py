"""Mark SVGs: colour on light and on dark, monochrome."""
from __future__ import annotations

from geometry import Mark, SMALL, glass_path, master, num, sand_path

PALETTE = {
    "light": {"sand": "#A87432", "glass": "#2F6FE4"},
    "dark": {"sand": "#E2BE84", "glass": "#5B9BFF"},
}
INK = "#16181C"
PAPER = "#F5F6F8"


def mark_body(m: Mark, mode: str, mono_color: str = "currentColor") -> str:
    if mode == "mono":
        return f'<path fill="{mono_color}" d="{glass_path(m)}{sand_path(m)}"/>'
    p = PALETTE[mode]
    return f'<path fill="{p["glass"]}" d="{glass_path(m)}"/><path fill="{p["sand"]}" d="{sand_path(m)}"/>'


def svg(width: float, height: float, body: str, title: str, view: str | None = None) -> str:
    vb = view or f"0 0 {num(width)} {num(height)}"
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{num(width)}" height="{num(height)}" '
        f'viewBox="{vb}"><title>{title}</title>{body}</svg>\n'
    )


def mark_svg(m: Mark, mode: str, mono_color: str = "currentColor", px: float | None = None) -> str:
    size = px or m.canvas
    return svg(size, size, mark_body(m, mode, mono_color), "Silica",
               view=f"0 0 {num(m.canvas)} {num(m.canvas)}")


def mark_for(px: int) -> Mark:
    return SMALL.get(px, master())
