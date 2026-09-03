#!/usr/bin/env python3
"""Lee las estadisticas reales de la cuenta desde la API REST de GitHub."""

import json
import os
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone

API = "https://api.github.com"
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("ACCESS_TOKEN", "")
COUNT_LOC = True     # ponlo en False si el workflow tarda demasiado
MAX_LANGS = 5


def get(path, retries=3):
    url = path if path.startswith("http") else API + path
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "readme-svg-updater")
    if TOKEN:
        req.add_header("Authorization", "Bearer " + TOKEN)

    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                body = r.read().decode("utf-8")
                if r.status == 202:            # GitHub esta calculando las stats
                    time.sleep(3 * (attempt + 1))
                    continue
                return json.loads(body) if body else None
        except urllib.error.HTTPError as e:
            if e.code in (403, 429) and attempt < retries - 1:
                time.sleep(5 * (attempt + 1))
                continue
            print("  ! HTTP %s en %s" % (e.code, url), file=sys.stderr)
            return None
        except Exception as e:
            print("  ! %s en %s" % (e, url), file=sys.stderr)
            return None
    return None


def fetch(user):
    print("-> perfil")
    u = get("/users/" + user)
    if not u:
        raise SystemExit("No se pudo leer el perfil. Revisa el token o el nombre de usuario.")

    print("-> repos")
    repos, page = [], 1
    while True:
        data = get("/users/%s/repos?per_page=100&type=owner&page=%d" % (user, page))
        if not data:
            break
        repos.extend(data)
        if len(data) < 100:
            break
        page += 1
    own = [r for r in repos if not r.get("fork")]

    print("-> lenguajes (%d repos)" % len(own))
    langs = Counter()
    for r in own:
        data = get("/repos/%s/languages" % r["full_name"])
        if data:
            langs.update(data)

    print("-> commits")
    commits = None
    data = get("/search/commits?q=author:%s&per_page=1" % user)
    if data and "total_count" in data:
        commits = data["total_count"]

    additions = deletions = 0
    if COUNT_LOC:
        print("-> lineas de codigo")
        for r in own:
            data = get("/repos/%s/stats/contributors" % r["full_name"])
            if not data:
                continue
            for cont in data:
                if (cont.get("author") or {}).get("login", "").lower() == user.lower():
                    for w in cont.get("weeks", []):
                        additions += w.get("a", 0)
                        deletions += w.get("d", 0)

    created = datetime.strptime(u["created_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    years = now.year - created.year
    months = now.month - created.month
    days = now.day - created.day
    if days < 0:
        months -= 1
        days += 30
    if months < 0:
        years -= 1
        months += 12

    return {
        "uptime": "%d years, %d months, %d days" % (max(years, 0), max(months, 0), max(days, 0)),
        "repos": u.get("public_repos", len(repos)),
        "forks_contributed": len(repos) - len(own),
        "stars": sum(r.get("stargazers_count", 0) for r in repos),
        "followers": u.get("followers", 0),
        "commits": commits,
        "additions": additions,
        "deletions": deletions,
        "langs": [k for k, _ in langs.most_common(MAX_LANGS)],
    }
