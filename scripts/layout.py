"""
Definicion unica del contenido del SVG.

build_svg.py lo usa para crear los archivos desde cero.
update_svg.py lo usa para saber que ids parchear cada dia.
Asi los dos nunca se desincronizan.
"""

USER = "Adolfius77"
INFO_W = 62          # ancho en caracteres de la columna derecha

# --------------------------------------------------------------------------
# Campos que la API no puede saber. Edita esto.
# --------------------------------------------------------------------------
MANUAL = {
    "OS": "Windows 11, Linux",
    "Host": "Instituto Tecnologico de Sonora",
    "Kernel": "Estudiante de Ing. de Software",
    "IDE": "VS Code, IntelliJ IDEA, NetBeans",
    "Frameworks": "Spring Boot, Jakarta EE, React",
    "Databases": "MySQL, MongoDB",
    "Tools.DevOps": "Git, Docker, Maven",
    "Learning": "Ciberseguridad, Calidad de Software",
    "Email": "ortega.adolfo.cb37@gmail.com",
    "LinkedIn": "linkedin.com/in/jose-adolfo-ortega-ruiz-29a043368",
}

# Valores de arranque: se ven solo hasta que el Action corra por primera vez.
PLACEHOLDER = {
    "uptime": "0 years, 0 months, 0 days",
    "langs": ["Java", "Python", "JavaScript"],
    "repos": 0, "forks_contributed": 0, "stars": 0,
    "commits": 0, "followers": 0,
    "additions": 0, "deletions": 0,
}

PALETTES = {
    "dark_mode.svg": {
        "bg": "#161b22", "fg": "#c9d1d9", "key": "#ffa657",
        "value": "#a5d6ff", "dots": "#616e7f", "add": "#3fb950", "del": "#f85149",
    },
    "light_mode.svg": {
        "bg": "#ffffff", "fg": "#24292f", "key": "#953800",
        "value": "#0550ae", "dots": "#6e7781", "add": "#1a7f37", "del": "#cf222e",
    },
}

# Geometria
WIDTH, HEIGHT = 1080, 520
ART_X, ART_Y0, ART_STEP, ART_SIZE = 15, 100, 12, 10
INFO_X, INFO_Y0, INFO_STEP, INFO_SIZE = 380, 40, 21, 16


def n(v):
    return "{:,}".format(v) if isinstance(v, int) else str(v)


def rows(s):
    """
    Devuelve la lista de renglones. Cada uno es una tupla:
      ("head",  texto)
      ("blank",)
      ("static", etiqueta, valor)
      ("dyn",   etiqueta, id_de_puntos, [(id_o_None, texto, clase), ...])
    Los segmentos con id son los que update_svg.py reemplaza.
    """
    commits = n(s["commits"]) if s["commits"] is not None else "n/a"
    net = s["additions"] - s["deletions"]
    return [
        ("head", USER.lower() + "@github"),
        ("static", "OS", MANUAL["OS"]),
        ("dyn", "Uptime", "age_dots", [("age_data", s["uptime"], "value")]),
        ("static", "Host", MANUAL["Host"]),
        ("static", "Kernel", MANUAL["Kernel"]),
        ("static", "IDE", MANUAL["IDE"]),
        ("blank",),
        ("dyn", "Languages", "lang_dots",
            [("lang_data", ", ".join(s["langs"]) or "n/a", "value")]),
        ("static", "Frameworks", MANUAL["Frameworks"]),
        ("static", "Databases", MANUAL["Databases"]),
        ("static", "Tools.DevOps", MANUAL["Tools.DevOps"]),
        ("static", "Learning", MANUAL["Learning"]),
        ("blank",),
        ("head", "- Contact"),
        ("static", "Email", MANUAL["Email"]),
        ("static", "LinkedIn", MANUAL["LinkedIn"]),
        ("static", "GitHub", "github.com/" + USER),
        ("blank",),
        ("head", "- GitHub Stats"),
        ("dyn", "Repos", "repo_dots", [
            ("repo_data", n(s["repos"]), "value"),
            (None, " {Contributed: ", "fg"),
            ("contrib_data", n(s["forks_contributed"]), "value"),
            (None, "} | Stars: ", "fg"),
            ("star_data", n(s["stars"]), "value"),
        ]),
        ("dyn", "Commits", "commit_dots", [
            ("commit_data", commits, "value"),
            (None, " | Followers: ", "fg"),
            ("follower_data", n(s["followers"]), "value"),
        ]),
        ("dyn", "Lines of Code", "loc_dots", [
            ("loc_data", n(net), "value"),
            (None, " ( ", "fg"),
            ("loc_add", n(s["additions"]) + "++", "add"),
            (None, ",  ", "fg"),
            ("loc_del", n(s["deletions"]) + "--", "del"),
            (None, " )", "fg"),
        ]),
    ]


def dots_for(label, rest_len):
    """Puntos necesarios para que el renglon mida exactamente INFO_W."""
    prefix = ". " + label + ":"
    return max(INFO_W - len(prefix) - rest_len - 2, 1)
