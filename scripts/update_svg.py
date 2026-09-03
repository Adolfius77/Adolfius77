#!/usr/bin/env python3
"""
Actualiza los valores dentro de dark_mode.svg y light_mode.svg.

No regenera los archivos: busca cada elemento por su id y le cambia el texto,
recalculando los puntos para que el valor siga alineado a la derecha. Asi
puedes editar colores, posiciones o el arte a mano y esto no te lo borra.

    GITHUB_TOKEN=xxx python3 scripts/update_svg.py
    python3 scripts/update_svg.py --mock            # prueba sin llamar a la API
    python3 scripts/update_svg.py --stats x.json    # aplica valores ya medidos
"""

import json
import os
import sys

from lxml import etree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import layout as L
import github_stats

MOCK = {
    "uptime": "3 years, 2 months, 11 days",
    "langs": ["Java", "Python", "JavaScript", "HTML", "CSS"],
    "repos": 18, "forks_contributed": 2, "stars": 3,
    "commits": 421, "followers": 7,
    "additions": 96120, "deletions": 32330,
}


def patch(filename, stats):
    tree = etree.parse(filename)
    root = tree.getroot()

    def set_text(eid, text):
        el = root.find(".//*[@id='%s']" % eid)
        if el is None:
            print("  ! no existe el id '%s' en %s" % (eid, filename), file=sys.stderr)
            return False
        el.text = text
        return True

    for row in L.rows(stats):
        if row[0] != "dyn":
            continue
        _, label, dots_id, segs = row
        rest = "".join(t for _, t, _ in segs)
        set_text(dots_id, " " + "." * L.dots_for(label, len(rest)) + " ")
        for eid, text, _cls in segs:
            if eid:
                set_text(eid, text)

    tree.write(filename, encoding="utf-8", xml_declaration=True)
    print("actualizado: " + filename)


def chosen_stats(argv):
    if "--mock" in argv:
        return MOCK
    if "--stats" in argv:
        with open(argv[argv.index("--stats") + 1], encoding="utf-8") as f:
            return json.load(f)
    return github_stats.fetch(L.USER)


if __name__ == "__main__":
    stats = chosen_stats(sys.argv)
    for name in L.PALETTES:
        patch(name, stats)
