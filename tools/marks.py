"""SVG del marchio: colore su chiaro e su scuro, monocromo."""
from __future__ import annotations

from geometry import Mark, Spec, build, master, num, SMALL

FACE_LIGHT = "#A9CCFF"
FACE_MID = "#5B9BFF"
FACE_DEEP = "#2F6FE4"
RIM_LIGHT = ("#FFFFFF", 0.92)
RIM_DARK = ("#16181C", 0.55)
INK = "#16181C"
PAPER = "#F5F6F8"


def rim_path(m: Mark) -> str:
    return m.silhouette + m.faces["left"] + m.faces["right"] + m.faces["bottom"]


def mark_body(m: Mark, mode: str, mono_color: str = "currentColor") -> str:
    if mode == "mono":
        return f'<path fill="{mono_color}" fill-rule="evenodd" d="{rim_path(m)}"/>'
    rim, alpha = RIM_LIGHT if mode == "light" else RIM_DARK
    return (
        f'<path fill="{rim}" fill-opacity="{num(alpha)}" fill-rule="evenodd" d="{rim_path(m)}"/>'
        f'<path fill="{FACE_LIGHT}" d="{m.faces["left"]}"/>'
        f'<path fill="{FACE_MID}" d="{m.faces["right"]}"/>'
        f'<path fill="{FACE_DEEP}" d="{m.faces["bottom"]}"/>'
    )


def svg(width: float, height: float, body: str, title: str, view: str | None = None) -> str:
    vb = view or f"0 0 {num(width)} {num(height)}"
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{num(width)}" height="{num(height)}" '
        f'viewBox="{vb}"><title>{title}</title>{body}</svg>\n'
    )


def mark_svg(spec: Spec, mode: str, mono_color: str = "currentColor", px: float | None = None) -> str:
    m = build(spec)
    size = px or spec.canvas
    return svg(size, size, mark_body(m, mode, mono_color), "Silica",
               view=f"0 0 {num(spec.canvas)} {num(spec.canvas)}")


def spec_for(px: int) -> Spec:
    return SMALL.get(px, master())
