"""Recupere une page Fandom par personne et la met en cache.

Les pages de saison ne portent ni la residence, ni le detail des tribus avec
leurs jours, ni le compte des victoires par edition. Les pages individuelles,
elles, portent une `Infobox Aventuriers` qui donne tout cela, saison par
saison. C'est la seule source connue pour ces champs sur les editions
anciennes.

    tools/atelier python3 tools/extraction/fetch_personnes.py

Les fichiers deja presents ne sont pas redemandes. Le wikitexte brut est
versionne dans specs/sources/personnes/ : c'est la preuve de provenance.
"""
import json, os, re, sys, time, urllib.parse, urllib.request, urllib.error
import yaml

RACINE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SORTIE = os.path.join(RACINE, "specs", "sources", "personnes")
UA = {"User-Agent": "koh-lanta-dataset/1.0 (personal research)"}
LOT = 40  # l'API accepte 50 titres ; on garde une marge


def api(params):
    params.setdefault("format", "json")
    url = "https://kohlanta.fandom.com/fr/api.php?" + urllib.parse.urlencode(params)
    for essai in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code != 429 or essai == 3:
                raise
            time.sleep(6 * (essai + 1))
        except urllib.error.URLError:
            if essai == 3:
                raise
            time.sleep(4 * (essai + 1))


def contenus(titres):
    """Rend {titre demande: wikitexte}. Suit les redirections et la casse."""
    d = api({"action": "query", "prop": "revisions", "rvprop": "content",
             "rvslots": "main", "titles": "|".join(titres), "redirects": "1"})
    q = d.get("query", {})
    # normalized + redirects : de la forme demandee vers la forme finale
    vers = {}
    for etape in ("normalized", "redirects"):
        for m in q.get(etape, []) or []:
            vers[m["from"]] = m["to"]

    def final(t):
        vu = set()
        while t in vers and t not in vu:
            vu.add(t)
            t = vers[t]
        return t

    texte = {}
    for p in (q.get("pages") or {}).values():
        if "revisions" in p:
            texte[p["title"]] = p["revisions"][0]["slots"]["main"]["*"]
    return {t: texte.get(final(t)) for t in titres}


# Les categories de candidats, saison par saison. Le wiki en emploie plusieurs
# graphies -- « Candidats de Koh-Lanta : X », « Koh-Lanta : X », « Koh-Lanta:
# X », avec une casse flottante -- et aucune n'est complete. Plutot que de les
# deviner, on liste TOUTES les categories du wiki et on rattache celles qui
# nomment une saison. Ces listes ne servent qu'a rendre son nom de famille a un
# prenom nu, jamais a ajouter un participant : le rattachement exige une
# correspondance unique.
CATEGORIES = os.path.join(SORTIE, "_categories.json")


def membres(categorie):
    d = api({"action": "query", "list": "categorymembers", "cmnamespace": "0",
             "cmtitle": "Catégorie:" + categorie, "cmlimit": "500"})
    return [x["title"] for x in (d.get("query", {}).get("categorymembers") or [])]


def toutes_categories(prefixe):
    sortie, suite = [], None
    while True:
        p = {"action": "query", "list": "allcategories", "acprefix": prefixe,
             "aclimit": "500"}
        if suite:
            p["acfrom"] = suite
        d = api(p)
        sortie += [c["*"] for c in d["query"]["allcategories"]]
        suite = (d.get("continue") or {}).get("accontinue")
        if not suite:
            return sortie


def recuperer_categories(_=None):
    """Ecrit {sid: [titres de pages classees dans la saison]}."""
    if os.path.exists(CATEGORIES):
        print(f"categories : cache ({CATEGORIES})")
        return
    sys.path.insert(0, os.path.join(RACINE, "tools", "extraction"))
    import parse_personnes as PP

    noms = []
    for prefixe in ("Koh-Lanta", "Koh Lanta", "Candidats", "Les Aventuriers"):
        noms += toutes_categories(prefixe)
        time.sleep(0.6)

    par_saison = {}
    for nom in sorted(set(noms)):
        cle = re.sub(r"^Candidats d[eu]s? ", "", nom)
        sid = PP._saison(re.sub(r"^Koh[- ]Lanta\s*:?\s*", "", cle))
        if not sid:
            continue
        try:
            m = membres(nom)
        except Exception as e:
            print(f"  {nom}: {e}"); continue
        if m:
            par_saison.setdefault(sid, set()).update(m)
            print(f"  {sid:5s} {nom[:44]:46s} {len(m)} pages")
        time.sleep(0.6)
    json.dump({k: sorted(v) for k, v in par_saison.items()},
              open(CATEGORIES, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1, sort_keys=True)
    print(f"{sum(len(v) for v in par_saison.values())} pages classees, "
          f"{len(par_saison)} saisons")


def main():
    os.makedirs(SORTIE, exist_ok=True)
    personnes = yaml.safe_load(open(os.path.join(RACINE, "_data", "personnes.yml"), encoding="utf-8"))
    attente = []
    for p in personnes:
        chemin = os.path.join(SORTIE, p["id"] + ".fandom.wiki")
        if os.path.exists(chemin):
            continue
        if " " not in p["nom"]:
            continue  # un prenom seul ne designe pas une page
        attente.append(p)
    print(f"{len(personnes)} personnes, {len(attente)} a recuperer")

    trouve = manque = 0
    for i in range(0, len(attente), LOT):
        lot = attente[i:i + LOT]
        res = contenus([p["nom"] for p in lot])
        for p in lot:
            t = res.get(p["nom"])
            if t and "Infobox" in t:
                open(os.path.join(SORTIE, p["id"] + ".fandom.wiki"), "w", encoding="utf-8").write(t)
                trouve += 1
            else:
                manque += 1
                print(f"  INTROUVABLE {p['id']:34s} {p['nom']}")
        print(f"  lot {i // LOT + 1}: {trouve} trouves, {manque} manquants")
        time.sleep(1.5)
    print(f"\n{trouve} pages ecrites, {manque} introuvables")
    recuperer_categories(None)


if __name__ == "__main__":
    main()
