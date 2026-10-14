"""Build the silica-brand exports.

Usage:
    python tools/build.py --inter <Inter-VariableFont_opsz,wght.ttf> [--out exports]

Dependencies: fonttools, uharfbuzz, resvg-py, pillow. The Inter font (OFL, rsms/inter) is not
in the repository.
"""
from __future__ import annotations

import argparse
import io
import json
from pathlib import Path

import resvg_py
from PIL import Image, ImageChops, ImageDraw

import lockup
from geometry import GRID, SMALL, column_x, glass_path, grain_path, master, num
from marks import INK, PAPER, PALETTE, mark_body, mark_for, mark_svg, svg
from text import Inter

PNG_SIZES = (16, 32, 64, 128, 256, 512, 1024)
MUTED = "#4A4F57"
FAINT = "#6A6F78"

REPOS = {
    "silica-desktop": "The desktop: Ossido compositor, shell, daemons and tools",
    "silica-icons": "App and file icons (layered), system symbols in three weights",
    "silica-brand": "Logo, repository banners and release wallpapers",
    "silica-os": "The distro: a bootc image on Fedora Atomic with Silica’s defaults, "
                 "build pipeline and installer ISO",
    "silica-packages": "RPM packages (desktop, apps, Inter, silica-icons) and the Wayland "
                       "session, installable on Fedora",
    "silica-setup": "The first-run setup assistant",
    "mustache": "The file manager",
}


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def render(svg_text: str, width: int, height: int | None = None) -> Image.Image:
    data = resvg_py.svg_to_bytes(svg_string=svg_text, width=width, height=height or width)
    return Image.open(io.BytesIO(bytes(data))).convert("RGBA")


def marks(out: Path) -> None:
    d = out / "mark"
    for mode in ("light", "dark"):
        write(d / f"silica-mark-{mode}.svg", mark_svg(master(), mode))
    write(d / "silica-mark-mono.svg", mark_svg(master(), "mono"))
    write(d / "silica-mark-black.svg", mark_svg(master(), "mono", "#000000"))
    write(d / "silica-mark-white.svg", mark_svg(master(), "mono", "#FFFFFF"))
    for px in SMALL:
        for mode in ("light", "dark", "mono"):
            write(d / f"silica-mark-{px}-{mode}.svg", mark_svg(SMALL[px], mode))
    for mode in ("light", "dark"):
        for px in PNG_SIZES:
            im = render(mark_svg(mark_for(px), mode, px=px), px)
            p = out / "png" / f"silica-mark-{mode}-{px}.png"
            p.parent.mkdir(parents=True, exist_ok=True)
            im.save(p)


def lockups(out: Path, inter: Inter) -> None:
    d = out / "logotype"
    for kind, fn in (("horizontal", lockup.horizontal), ("vertical", lockup.vertical)):
        for mode in ("light", "dark", "mono"):
            body, w, h = fn(inter, mode, 64.0)
            write(d / f"silica-logotype-{kind}-{mode}.svg", svg(w, h, body, "Silica"))
        for name, color in (("black", "#000000"), ("white", "#FFFFFF")):
            body, w, h = fn(inter, "mono", 64.0, color)
            write(d / f"silica-logotype-{kind}-{name}.svg", svg(w, h, body, "Silica"))


def wrap(inter: Inter, text: str, size: float, weight: int, max_w: float) -> list[str]:
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if cur and inter.run(trial, size, weight).width > max_w:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def banner_svg(inter: Inter, repo: str, desc: str) -> str:
    w, h = 1280, 640
    parts = [
        '<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#FFFFFF"/><stop offset="1" stop-color="#EEF1F6"/>'
        '</linearGradient></defs>',
        f'<rect width="{w}" height="{h}" fill="url(#bg)"/>',
    ]
    m = master()
    big = 600.0
    s = big / (2.0 * m.radius)
    parts.append(
        f'<g opacity="0.08" transform="translate({num(1110 - m.cx * s)} {num(380 - m.cy * s)}) '
        f'scale({num(s)})">{mark_body(m, "mono", PALETTE["light"]["glass"])}</g>'
    )
    body, lw, lh = lockup.horizontal(inter, "light", 56.0)
    parts.append(f'<g transform="translate(96 96)">{body}</g>')
    name = inter.run(repo, 96, 600, -0.02, 96, 372, opsz=32)
    parts.append(f'<path fill="{INK}" d="{name.d}"/>')
    lines = wrap(inter, desc, 34, 400, 1000)
    y = 440
    for line in lines:
        r = inter.run(line, 34, 400, -0.01, 96, y)
        parts.append(f'<path fill="{MUTED}" d="{r.d}"/>')
        y += 48
    foot = inter.run(f"github.com/silica-linux/{repo}", 24, 500, 0, 96, 560)
    parts.append(f'<path fill="{FAINT}" d="{foot.d}"/>')
    return svg(w, h, "".join(parts), repo)


def banners(out: Path, inter: Inter) -> None:
    for repo, desc in REPOS.items():
        s = banner_svg(inter, repo, desc)
        write(out / "banners" / f"{repo}.svg", s)
        render(s, 1280, 640).convert("RGB").save(out / "banners" / f"{repo}.png")


def body_mask(size: int) -> Image.Image:
    m = Image.new("L", (size, size), 0)
    k = size / 1024
    ImageDraw.Draw(m).rounded_rectangle((100 * k, 100 * k, 924 * k, 924 * k), radius=215 * k, fill=255)
    return m


ICON_BACKGROUNDS = {
    "": ("#FFFFFF", "#ECEFF4"),
    "-dark": ("#1B2A4A", "#0B1426"),
}
ICON_DIAMETER = 640.0


def app_icon(out: Path) -> None:
    """The mark as a silica-icons app icon.

    The circle is 640 across, 1.067 times the 600 keyline: a circle drawn as wide as a square
    looks smaller (it covers π/4 of the square's area), so it overshoots the keyline.
    """
    d = out / "app-icon"
    m = master()
    s = ICON_DIAMETER / (2.0 * m.radius)
    off = 512.0 - m.cx * s
    tr = f'translate({num(off)} {num(off)}) scale({num(s)})'
    for suffix, (a, b) in ICON_BACKGROUNDS.items():
        bg = (
            '<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{b}"/>'
            '</linearGradient></defs><rect width="1024" height="1024" fill="url(#g)"/>'
        )
        write(d / f"background{suffix}.svg", svg(1024, 1024, bg, "background"))
        mode = "dark" if suffix else "light"
        fg = f'<g transform="{tr}">{mark_body(m, mode)}</g>'
        write(d / f"foreground{suffix}.svg", svg(1024, 1024, fg, "foreground"))
    manifest = {
        "format": 1, "id": "silica", "name": "Silica", "kind": "app", "keyline": "circle",
        "layers": [
            {"role": "background", "file": "background.svg"},
            {"role": "foreground", "file": "foreground.svg", "shadow": "neutral"},
        ],
        "variants": {"dark": {"background": "background-dark.svg", "foreground": "foreground-dark.svg"}},
        "dynamic": None,
    }
    write(d / "icon.json", json.dumps(manifest, indent=2) + "\n")
    for suffix in ("", "-dark"):
        im = render((d / f"background{suffix}.svg").read_text(), 1024)
        im.alpha_composite(render((d / f"foreground{suffix}.svg").read_text(), 1024))
        im.putalpha(ImageChops.multiply(im.split()[3], body_mask(1024)))
        im.resize((256, 256), Image.LANCZOS).save(d / f"preview{suffix}.png")


def construction(out: Path) -> None:
    """Construction drawing on the 1024 canvas (1 u = 16 px)."""
    k = 16.0
    m = master()
    p = ['<rect width="1024" height="1024" fill="#FFFFFF"/>']
    for i in range(65):
        v = i * 16
        c, w = ("#C9D2E0", 2) if i % 8 == 0 else ("#E8ECF2", 1)
        p.append(f'<path stroke="{c}" stroke-width="{w}" d="M{v} 0V1024M0 {v}H1024"/>')
    big = master(1024)
    p.append(f'<g opacity="0.3">{mark_body(big, "light")}</g>')
    r = m.radius * k
    p.append(f'<circle cx="512" cy="512" r="{num(r)}" fill="none" stroke="#16181C" stroke-width="2"/>')
    p.append(f'<path fill="none" stroke="#16181C" stroke-width="2" d="{glass_path(big)}"/>')
    lattice = []
    for c in range(-1, GRID.columns + 1):
        x = column_x(32.0, GRID, c) * k
        off = 0.5 if c % 2 else 0.0
        for j in range(-8, 9):
            y = (32.0 + (j + off) * GRID.pitch) * k
            if (x - 512) ** 2 + (y - 512) ** 2 <= (r + 40) ** 2 and x < 512:
                lattice.append(f'M{num(x - 5)} {num(y)}h10M{num(x)} {num(y - 5)}v10')
    p.append(f'<path stroke="#E5484D" stroke-width="2" d="{"".join(lattice)}"/>')
    for x, y, gr in big.grains:
        p.append(f'<path fill="none" stroke="#A87432" stroke-width="2" d="{grain_path(x, y, gr)}"/>')
    for c in range(GRID.columns):
        x = column_x(32.0, GRID, c) * k
        p.append(f'<path stroke="#8E44AD" stroke-width="1.5" stroke-dasharray="4 6" d="M{num(x)} 40V984"/>')
    p.append('<path stroke="#E5484D" stroke-width="2" d="M0 512H1024M512 0V1024" opacity="0.6"/>')
    p.append('<circle cx="512" cy="512" r="8" fill="none" stroke="#16181C" stroke-width="3"/>')
    write(out / "construction" / "silica-mark-construction.svg", svg(1024, 1024, "".join(p), "Construction"))


def clear_space(out: Path) -> None:
    m = master()
    D = 400.0
    s = D / (2.0 * m.radius)
    pad = D / 4.0
    W = D + 2 * pad
    p = [f'<rect width="{num(W)}" height="{num(W)}" fill="#E5484D" fill-opacity="0.10"/>',
         f'<rect x="{num(pad)}" y="{num(pad)}" width="{num(D)}" height="{num(D)}" fill="#FFFFFF"/>',
         f'<g transform="translate({num(pad - (m.cx - m.radius) * s)} {num(pad - (m.cy - m.radius) * s)}) '
         f'scale({num(s)})">{mark_body(m, "mono", INK)}</g>',
         f'<rect x="0.5" y="0.5" width="{num(W - 1)}" height="{num(W - 1)}" fill="none" '
         f'stroke="#E5484D" stroke-dasharray="6 6"/>']
    write(out / "construction" / "silica-mark-clear-space.svg", svg(W, W, "".join(p), "Clear space"))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--inter", required=True)
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent.parent / "exports"))
    args = ap.parse_args()
    out = Path(args.out)
    inter = Inter(args.inter)
    marks(out)
    lockups(out, inter)
    banners(out, inter)
    app_icon(out)
    construction(out)
    clear_space(out)


if __name__ == "__main__":
    main()
