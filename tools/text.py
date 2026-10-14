"""Testo in tracciati con Inter (OFL), impaginato con HarfBuzz.

Il font non è nel repository: si passa il percorso di Inter variabile (rsms/inter, v4).
"""
from __future__ import annotations

from dataclasses import dataclass

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen

from geometry import num


class _Pen(SVGPathPen):
    def __init__(self, scale: float, dx: float, dy: float):
        super().__init__(None, ntos=num)
        self._s, self._dx, self._dy = scale, dx, dy

    def _t(self, p):
        return (self._dx + p[0] * self._s, self._dy - p[1] * self._s)

    def moveTo(self, p):
        super().moveTo(self._t(p))

    def lineTo(self, p):
        super().lineTo(self._t(p))

    def curveTo(self, *ps):
        super().curveTo(*[self._t(p) for p in ps])

    def qCurveTo(self, *ps):
        super().qCurveTo(*[self._t(p) if p is not None else None for p in ps])


@dataclass
class Run:
    d: str
    width: float
    left: float
    right: float
    top: float
    bottom: float


class Inter:
    def __init__(self, path: str):
        blob = hb.Blob.from_file_path(path)
        self.face = hb.Face(blob)
        self.upem = self.face.upem
        self.cap = 1490

    def run(self, text: str, size: float, weight: int, tracking_em: float = 0.0,
            x: float = 0.0, baseline: float = 0.0, opsz: float | None = None) -> Run:
        font = hb.Font(self.face)
        font.set_variations({"wght": weight, "opsz": opsz if opsz else max(14.0, min(32.0, size))})
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(font, buf, {"kern": True, "liga": True})
        s = size / self.upem
        track = tracking_em * self.upem
        pen_x = 0.0
        parts = []
        left, right, top, bottom = None, None, None, None
        count = len(buf.glyph_infos)
        for i, (info, pos) in enumerate(zip(buf.glyph_infos, buf.glyph_positions)):
            gx = x + (pen_x + pos.x_offset) * s
            pen = _Pen(s, gx, baseline - pos.y_offset * s)
            font.draw_glyph_with_pen(info.codepoint, pen)
            parts.append(pen.getCommands())
            ext = font.get_glyph_extents(info.codepoint)
            if ext and ext.width:
                gl = gx + ext.x_bearing * s
                gr = gl + ext.width * s
                gt = baseline - ext.y_bearing * s
                gb = gt - ext.height * s
                left = gl if left is None else min(left, gl)
                right = gr if right is None else max(right, gr)
                top = gt if top is None else min(top, gt)
                bottom = gb if bottom is None else max(bottom, gb)
            pen_x += pos.x_advance + (track if i < count - 1 else 0.0)
        return Run("".join(parts), pen_x * s, left or x, right or x, top or baseline,
                   bottom or baseline)

    def size_for_cap(self, cap_height: float) -> float:
        return cap_height * self.upem / self.cap
