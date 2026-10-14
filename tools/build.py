"""Genera le esportazioni di silica-brand.

Uso:
    python tools/build.py --inter <Inter-VariableFont_opsz,wght.ttf> [--out exports]

Dipendenze: fonttools, uharfbuzz, resvg-py, pillow. Il font Inter (OFL, rsms/inter) non è
nel repository.
"""
from __future__ import annotations

import argparse
import io
import json
from pathlib import Path

import resvg_py
from PIL import Image, ImageChops, ImageDraw

import lockup
from geometry import SMALL, build, master, num
from marks import INK, PAPER, mark_body, mark_svg, spec_for, svg
from text import Inter

PNG_SIZES = (16, 32, 64, 128, 256, 512, 1024)
MUTED = "#4A4F57"
FAINT = "#6A6F78"

REPOS = {
    "silica-desktop": "Il desktop: compositor Ossido, shell, demoni e strumenti",
    "silica-icons": "Icone delle app e dei file (a livelli), simboli di sistema in tre pesi",
    "silica-brand": "Logo, banner dei repository, sfondi delle versioni",
    "silica-os": "La distro: immagine bootc sopra Fedora Atomic con i default di Silica, "
                 "pipeline e ISO di installazione",
    "silica-packages": "I pacchetti RPM (desktop, app, Inter, silica-icons) e la sessione "
                       "Wayland installabile su Fedora",
    "silica-setup": "L’assistente al primo avvio",
    "mustache": "Il gestore dei file",
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
            im = render(mark_svg(spec_for(px), mode, px=px), px)
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
    m = build(master())
    bx0, by0, bx1, by1 = m.bbox
    big = 560.0
    s = big / (by1 - by0)
    parts.append(
        f'<g opacity="0.07" transform="translate({num(1300 - bx1 * s)} {num(150 - by0 * s)}) '
        f'scale({num(s)})">{mark_body(m, "mono", "#2F6FE4")}</g>'
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


def app_icon(out: Path) -> None:
    d = out / "app-icon"
    m = build(master())
    s = 600.0 / (m.bbox[2] - m.bbox[0])
    off = 512.0 - 32.0 * s
    tr = f'translate({num(off)} {num(off)}) scale({num(s)})'
    bgs = {
        "": ("#FFFFFF", "#ECEFF4"),
        "-dark": ("#3A3A3C", "#161618"),
    }
    for suffix, (a, b) in bgs.items():
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
        "format": 1, "id": "silica", "name": "Silica", "kind": "app", "keyline": "square",
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
    sp = master(1024)
    m = build(sp)
    p = []
    p.append('<rect width="1024" height="1024" fill="#FFFFFF"/>')
    for i in range(65):
        v = i * 16
        strong = i % 8 == 0
        c, w = ("#C9D2E0", 2) if strong else ("#E8ECF2", 1)
        p.append(f'<path stroke="{c}" stroke-width="{w}" d="M{v} 0V1024M0 {v}H1024"/>')
    p.append(f'<g opacity="0.35">{mark_body(m, "light")}</g>')
    p.append(f'<path fill="none" stroke="#16181C" stroke-width="2" d="{m.silhouette}"/>')
    for f in m.faces.values():
        p.append(f'<path fill="none" stroke="#2F6FE4" stroke-width="2" d="{f}"/>')
    a, b, c = m.mid
    p.append(f'<path fill="none" stroke="#E5484D" stroke-width="2" stroke-dasharray="10 8" '
             f'd="M{num(a[0])} {num(a[1])}L{num(b[0])} {num(b[1])}L{num(c[0])} {num(c[1])}Z'
             f'M{num(a[0])} {num(a[1])}L{num(m.junction[0])} {num(m.junction[1])}'
             f'L{num(b[0])} {num(b[1])}M{num(m.junction[0])} {num(m.junction[1])}'
             f'L{num(c[0])} {num(c[1])}"/>')
    a, b, c = m.sharp
    p.append(f'<path fill="none" stroke="#16181C" stroke-opacity="0.35" stroke-width="2" '
             f'stroke-dasharray="4 6" d="M{num(a[0])} {num(a[1])}L{num(b[0])} {num(b[1])}'
             f'L{num(c[0])} {num(c[1])}Z"/>')
    x0, y0, x1, y1 = m.bbox
    p.append(f'<rect x="{num(x0)}" y="{num(y0)}" width="{num(x1 - x0)}" height="{num(y1 - y0)}" '
             f'fill="none" stroke="#8E44AD" stroke-width="2" stroke-dasharray="2 6"/>')
    p.append('<path stroke="#E5484D" stroke-width="2" d="M0 512H1024M512 0V1024" opacity="0.6"/>')
    p.append(f'<circle cx="{num(m.junction[0])}" cy="{num(m.junction[1])}" r="8" fill="#E5484D"/>')
    p.append(f'<circle cx="512" cy="{num((y0 + y1) / 2)}" r="8" fill="#8E44AD"/>')
    p.append('<circle cx="512" cy="512" r="8" fill="none" stroke="#16181C" stroke-width="3"/>')
    write(out / "construction" / "silica-mark-construction.svg", svg(1024, 1024, "".join(p), "Costruzione"))


def clear_space(out: Path, inter: Inter) -> None:
    m = build(master())
    x0, y0, x1, y1 = m.bbox
    H = 400.0
    s = H / (y1 - y0)
    pad = H / 4.0
    mw = (x1 - x0) * s
    W, Ht = mw + 2 * pad, H + 2 * pad
    p = [f'<rect width="{num(W)}" height="{num(Ht)}" fill="#E5484D" fill-opacity="0.10"/>',
         f'<rect x="{num(pad)}" y="{num(pad)}" width="{num(mw)}" height="{num(H)}" fill="#FFFFFF"/>',
         f'<g transform="translate({num(pad - x0 * s)} {num(pad - y0 * s)}) scale({num(s)})">'
         f'{mark_body(m, "mono", INK)}</g>',
         f'<rect x="0.5" y="0.5" width="{num(W - 1)}" height="{num(Ht - 1)}" fill="none" '
         f'stroke="#E5484D" stroke-dasharray="6 6"/>']
    write(out / "construction" / "silica-mark-clear-space.svg", svg(W, Ht, "".join(p), "Area di rispetto"))


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
    clear_space(out, inter)


if __name__ == "__main__":
    main()
