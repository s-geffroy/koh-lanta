#!/usr/bin/env python3
"""Recupere les pages d'epreuves nommees du wiki Fandom.

Le site a longtemps ecrit que la nature d'une epreuve -- endurance, equilibre,
precision -- n'etait donnee nulle part de facon exploitable. C'etait vrai des
tables de saison, qui ne nomment pas les epreuves. Ce ne l'est pas du wiki :
il tient une page par epreuve recurrente, avec une `Infobox Épreuves` qui en
donne le type, et un tableau « Apparitions et vainqueurs » qui liste chaque
saison ou elle a ete disputee, sa nature (confort ou immunite) et son gagnant.

    tools/atelier python3 tools/extraction/fetch_epreuves.py

Les fichiers deja presents ne sont pas redemandes. Le wikitexte brut est
versionne dans specs/sources/epreuves/ : c'est la preuve de provenance.
"""
import json, os, re, sys, time, urllib.error, urllib.parse, urllib.request

RACINE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SORTIE = os.path.join(RACINE, "specs", "sources", "epreuves")
UA = {"User-Agent": "koh-lanta-dataset/1.0 (personal research)"}
CATEGORIE = "Catégorie:Épreuves"
LOT = 30


def api(params):
    params.setdefault("format", "json")
    url = "https://kohlanta.fandom.com/fr/api.php?" + urllib.parse.urlencode(params)
    for essai in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA),
                                        timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code != 429 or essai == 3:
                raise
            time.sleep(8 * (essai + 1))
        except urllib.error.URLError:
            if essai == 3:
                raise
            time.sleep(5 * (essai + 1))


def fichier(titre):
    """Un nom de fichier sur : les titres portent des apostrophes et des accents."""
    plat = titre.replace("'", "-").replace("’", "-")
    return re.sub(r"[^A-Za-z0-9À-ÿ-]+", "-", plat).strip("-") + ".fandom.wiki"


def main():
    os.makedirs(SORTIE, exist_ok=True)
    d = api({"action": "query", "list": "categorymembers", "cmtitle": CATEGORIE,
             "cmnamespace": "0", "cmlimit": "500"})
    titres = sorted(x["title"] for x in d["query"]["categorymembers"])
    print(f"{len(titres)} epreuves dans « {CATEGORIE} »")

    attente = [t for t in titres if not os.path.exists(os.path.join(SORTIE, fichier(t)))]
    print(f"{len(attente)} a recuperer")

    ecrits = 0
    for i in range(0, len(attente), LOT):
        lot = attente[i:i + LOT]
        d = api({"action": "query", "prop": "revisions", "rvprop": "content",
                 "rvslots": "main", "titles": "|".join(lot), "redirects": "1"})
        q = d.get("query", {})
        vers = {}
        for etape in ("normalized", "redirects"):
            for m in q.get(etape, []) or []:
                vers[m["from"]] = m["to"]

        def final(t):
            vu = set()
            while t in vers and t not in vu:
                vu.add(t); t = vers[t]
            return t

        texte = {p["title"]: p["revisions"][0]["slots"]["main"]["*"]
                 for p in (q.get("pages") or {}).values() if "revisions" in p}
        for t in lot:
            c = texte.get(final(t))
            if c and "Infobox" in c:
                open(os.path.join(SORTIE, fichier(t)), "w", encoding="utf-8").write(c)
                ecrits += 1
            else:
                print(f"  INTROUVABLE {t}")
        time.sleep(1.5)
    print(f"{ecrits} pages ecrites")

    index = os.path.join(SORTIE, "_titres.json")
    json.dump({fichier(t): t for t in titres}, open(index, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1, sort_keys=True)
    print(f"ecrit : {index}")


if __name__ == "__main__":
    sys.exit(main())
