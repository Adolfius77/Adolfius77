#!/usr/bin/env python3
"""
Crea dark_mode.svg y light_mode.svg desde cero.

Corre esto solo cuando cambies el arte, las etiquetas o los campos de MANUAL.
El dia a dia lo maneja update_svg.py, que solo parchea los valores.

    python3 scripts/build_svg.py
"""

import os
import sys
from xml.sax.saxutils import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import layout as L

ART_PATH = "assets/art.txt"

STYLE = """<style>
@font-face {{
  src: local('Consolas'), local('Menlo'), local('DejaVu Sans Mono');
  font-family: 'ConsolasFallback';
  font-display: swap;
  size-adjust: 109%;
}}
.key   {{ fill: {key}; }}
.value {{ fill: {value}; }}
.dots  {{ fill: {dots}; }}
.fg    {{ fill: {fg}; }}
.add   {{ fill: {add}; }}
.del   {{ fill: {del_}; }}
.head  {{ fill: {key}; font-weight: bold; }}
.ascii {{ fill: {fg}; }}
text, tspan {{ white-space: pre; }}
</style>"""


def span(cls, text, eid=None):
    attr = ' id="%s"' % eid if eid else ""
    return '<tspan class="%s"%s>%s</tspan>' % (cls, attr, escape(text))


def build(filename, pal):
    art = [l.rstrip("\n") for l in open(ART_PATH, encoding="utf-8")]

    out = []
    out.append('<?xml version="1.0" encoding="UTF-8"?>')
    out.append('<svg xmlns="http://www.w3.org/2000/svg" '
               'font-family="ConsolasFallback,Consolas,Menlo,DejaVu Sans Mono,monospace" '
               'width="%dpx" height="%dpx" font-size="%dpx">'
               % (L.WIDTH, L.HEIGHT, L.INFO_SIZE))
    out.append(STYLE.format(key=pal["key"], value=pal["value"], dots=pal["dots"],
                            fg=pal["fg"], add=pal["add"], del_=pal["del"]))
    out.append('<rect width="%dpx" height="%dpx" fill="%s" rx="15"/>'
               % (L.WIDTH, L.HEIGHT, pal["bg"]))

    # columna izquierda: el arte
    out.append('<text x="%d" y="%d" class="ascii" font-family="ConsolasFallback,Consolas,Menlo,&apos;DejaVu Sans Mono&apos;,monospace" font-size="%dpx">'
               % (L.ART_X, L.ART_Y0, L.ART_SIZE))
    for i, line in enumerate(art):
        out.append('<tspan x="%d" y="%d">%s</tspan>'
                   % (L.ART_X, L.ART_Y0 + i * L.ART_STEP, escape(line)))
    out.append('</text>')

    # columna derecha: los datos
    out.append('<text x="%d" y="%d" font-family="ConsolasFallback,Consolas,Menlo,&apos;DejaVu Sans Mono&apos;,monospace">' % (L.INFO_X, L.INFO_Y0))
    for i, row in enumerate(L.rows(L.PLACEHOLDER)):
        y = L.INFO_Y0 + i * L.INFO_STEP
        parts = ['<tspan x="%d" y="%d">' % (L.INFO_X, y)]

        if row[0] == "head":
            title = row[1]
            parts.append(span("head", title))
            parts.append(span("dots", " " + "\u2500" * max(L.INFO_W - len(title) - 1, 0)))
        elif row[0] == "blank":
            parts.append(span("dots", "."))
        elif row[0] == "static":
            _, label, value = row
            d = L.dots_for(label, len(value))
            parts.append(span("dots", ". "))
            parts.append(span("key", label + ":"))
            parts.append(span("dots", " " + "." * d + " "))
            parts.append(span("value", value))
        else:  # dyn
            _, label, dots_id, segs = row
            rest = "".join(t for _, t, _ in segs)
            d = L.dots_for(label, len(rest))
            parts.append(span("dots", ". "))
            parts.append(span("key", label + ":"))
            parts.append(span("dots", " " + "." * d + " ", dots_id))
            for eid, text, cls in segs:
                parts.append(span(cls, text, eid))

        parts.append('</tspan>')
        out.append("".join(parts))
    out.append('</text>')
    out.append('</svg>')

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print("escrito: " + filename)


if __name__ == "__main__":
    for name, pal in L.PALETTES.items():
        build(name, pal)
