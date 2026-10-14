"""The Silica logo as an app icon, in the silica-icons format.

Layers on a 1024 canvas: a background that fills the 824 body (the body shape of the
silica-icons spec, smooth corners r 215) and a foreground with the sand and glass circle. Like
the other icons of the set (Mail, Mustache) the parts have their own gradients, a soft shadow
on the background and a light inner edge at the top; the shell adds mask, rim and outer shadow.
"""
from __future__ import annotations

from geometry import Mark, SMALL, glass_path, master, num, pixel_grain_path

BODY = (
    "M444,100 L580,100 C700.411289,100 760.616933,100 806.607957,123.433597 "
    "C847.062807,144.046373 879.953627,176.937193 900.566403,217.392043 "
    "C924,263.383067 924,323.588711 924,444 L924,580 C924,700.411289 924,760.616933 "
    "900.566403,806.607957 C879.953627,847.062807 847.062807,879.953627 806.607957,900.566403 "
    "C760.616933,924 700.411289,924 580,924 L444,924 C323.588711,924 263.383067,924 "
    "217.392043,900.566403 C176.937193,879.953627 144.046373,847.062807 123.433597,806.607957 "
    "C100,760.616933 100,700.411289 100,580 L100,444 C100,323.588711 100,263.383067 "
    "123.433597,217.392043 C144.046373,176.937193 176.937193,144.046373 217.392043,123.433597 "
    "C263.383067,100 323.588711,100 444,100 Z"
)
BODY_BOX = (100.0, 100.0, 924.0, 924.0)
DIAMETER = 640.0

STYLE = {
    "light": {
        "background": ("#FFFFFF", "#DDE3EC"),
        "glass": ("#2F74E8", "#1652D0"),
        "sand": ("#A06A26", "#83541A"),
        "shadow": ("0.043 0.176 0.416", 0.22),
        "grain_shadow": ("0.35 0.22 0.06", 0.30),
        "highlight": 0.55,
        "sheen": 0.28,
    },
    "dark": {
        "background": ("#3A3A3C", "#141416"),
        "glass": ("#6AAAFF", "#4A90FF"),
        "sand": ("#EFCB90", "#C9A060"),
        "shadow": ("0 0 0", 0.40),
        "grain_shadow": ("0 0 0", 0.40),
        "highlight": 0.40,
        "sheen": 0.22,
    },
}


def svg(body: str, title: str, size: int = 1024) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
            f'viewBox="0 0 1024 1024"><title>{title}</title>{body}</svg>\n')


def gradient(gid: str, top: str, bottom: str) -> str:
    return (f'<linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{top}"/><stop offset="1" stop-color="{bottom}"/></linearGradient>')


def background(mode: str, prefix: str = "") -> str:
    a, b = STYLE[mode]["background"]
    g = f"{prefix}bg"
    return f'<defs>{gradient(g, a, b)}</defs><path fill="url(#{g})" d="{BODY}"/>'


def _filter(fid: str, rgb: str, alpha: float, dy: float, blur: float, hl: float, hl_dy: float,
            hl_blur: float) -> str:
    return (
        f'<filter id="{fid}" x="-20%" y="-20%" width="140%" height="150%">'
        f'<feOffset dy="{num(dy)}" in="SourceAlpha" result="o"/>'
        f'<feGaussianBlur stdDeviation="{num(blur)}" in="o" result="b"/>'
        f'<feColorMatrix in="b" type="matrix" values="0 0 0 0 {rgb.split()[0]} 0 0 0 0 {rgb.split()[1]} '
        f'0 0 0 0 {rgb.split()[2]} 0 0 0 {num(alpha)} 0" result="sh"/>'
        f'<feGaussianBlur stdDeviation="{num(hl_blur)}" in="SourceAlpha" result="ib"/>'
        f'<feOffset dy="{num(hl_dy)}" in="ib" result="io"/>'
        f'<feComposite in="io" in2="SourceAlpha" operator="arithmetic" k2="-1" k3="1" result="in"/>'
        f'<feColorMatrix in="in" type="matrix" values="0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 {num(hl)} 0" result="hl"/>'
        f'<feMerge><feMergeNode in="sh"/><feMergeNode in="SourceGraphic"/><feMergeNode in="hl"/></feMerge>'
        f'</filter>'
    )


def foreground(mode: str, prefix: str = "", mark: Mark | None = None, diameter: float = DIAMETER) -> str:
    """Foreground layer: the circle centred on (512, 512)."""
    st = STYLE[mode]
    m = mark or master()
    s = diameter / (2.0 * m.radius)
    tx = 512.0 - m.cx * s
    ty = 512.0 - m.cy * s
    p = prefix
    k = 1.0 / s
    defs = (
        gradient(f"{p}glass", *st["glass"])
        + gradient(f"{p}sand", *st["sand"])
        + f'<linearGradient id="{p}sheen" x1="0" y1="0" x2="0.6" y2="1">'
        f'<stop offset="0" stop-color="#FFFFFF" stop-opacity="{num(st["sheen"])}"/>'
        f'<stop offset="0.55" stop-color="#FFFFFF" stop-opacity="0"/></linearGradient>'
        + _filter(f"{p}gs", st["shadow"][0], st["shadow"][1], 8 * k, 10 * k, st["highlight"], 5 * k, 2 * k)
        + _filter(f"{p}ss", st["grain_shadow"][0], st["grain_shadow"][1], 3 * k, 2.5 * k,
                  st["highlight"], 2 * k, 1 * k)
    )
    tr = f'translate({num(tx)} {num(ty)}) scale({num(s)})'
    glass = glass_path(m)
    grains = []
    for x, y, r in m.grains:
        if r <= 0:
            continue
        if m.pixel:
            grains.append(f'<path fill="url(#{p}sand)" d="{pixel_grain_path(x, y, r)}"/>')
        else:
            grains.append(f'<circle cx="{num(x)}" cy="{num(y)}" r="{num(r)}" fill="url(#{p}sand)"/>')
    return (
        f'<defs>{defs}</defs>'
        f'<g transform="{tr}">'
        f'<g filter="url(#{p}gs)"><path fill="url(#{p}glass)" d="{glass}"/>'
        f'<path fill="url(#{p}sheen)" d="{glass}"/></g>'
        f'<g filter="url(#{p}ss)">{"".join(grains)}</g>'
        f'</g>'
    )


SMALL_ICON = {32: 24}


def icon(mode: str, prefix: str = "", px: int | None = None) -> str:
    """Background and foreground together (the body shape needs no mask).

    At 32 px the grains of the reference drawing vanish: the icon uses the pixel-drawn 24 px
    variant of the mark, scaled so that one of its units is one output pixel (diameter 672 on
    the 1024 canvas, offset 4 px), which keeps its grains on whole pixels.
    """
    if px in SMALL_ICON:
        m = SMALL[SMALL_ICON[px]]
        unit = 1024.0 / px
        return background(mode, prefix) + foreground(mode, prefix, m, 2.0 * m.radius * unit)
    return background(mode, prefix) + foreground(mode, prefix)
