"""Le wiki anglophone de Survivor : troisieme temoin des epreuves.

Quand Wikipedia et le wiki Fandom francophone se contredisent sur le vainqueur
d'une epreuve, ce wiki tranche souvent : chaque saison y a un guide d'episodes
(modele « FRSnepguide ») qui donne, episode par episode, le confort, l'immunite
et l'elimine, et les invites d'une recompense entre crochets. Il est tenu par
d'autres mains que les deux premiers, et il a deja tranche Vanuatu (episode 9),
Caramoan (episode 1) et L'Ile au tresor (episode 9).

On enregistre la page de saison ET le modele qu'elle appelle : la page seule ne
contient que l'appel `{{FRS19epguide}}`, sans le tableau.

    tools/atelier python3 specs/sources/fetch_survivor.py
    tools/atelier python3 specs/sources/fetch_survivor.py --rafraichir sp8

La page web refuse la lecture directe (402) ; l'API repond.
"""
import json, os, re, sys, time, urllib.error, urllib.parse, urllib.request

UA = {"User-Agent": "koh-lanta-dataset/1.0 (personal research)"}
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "survivor")
os.makedirs(OUT, exist_ok=True)


def api(params):
    params.setdefault("format", "json")
    q = urllib.parse.urlencode(params)
    req = urllib.request.Request(f"https://survivor.fandom.com/api.php?{q}", headers=UA)
    for a in range(4):
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code != 429 or a == 3:
                raise
            time.sleep(6 * (a + 1))


def content(title):
    d = api({"action": "query", "prop": "revisions", "rvprop": "content",
             "rvslots": "main", "titles": title, "redirects": "1"})
    for p in d["query"]["pages"].values():
        if "revisions" in p:
            return p["revisions"][0]["slots"]["main"]["*"]
    return None


SEASONS = [
    ("s01", "Les Aventuriers de Koh-Lanta"), ("s02", "Koh-Lanta: Nicoya"),
    ("s03", "Koh-Lanta: Bocas del Toro"), ("s04", "Koh-Lanta: Panama"),
    ("s05", "Koh-Lanta: Pacifique"), ("s06", "Koh-Lanta: Vanuatu"),
    ("s07", "Koh-Lanta: Palawan"), ("s08", "Koh-Lanta: Caramoan"),
    ("s09", "Koh-Lanta: Palau"), ("s10", "Koh-Lanta: Viêtnam"),
    ("s11", "Koh-Lanta: Raja Ampat"), ("s12", "Koh-Lanta: Malaisie"),
    ("s13", "Koh-Lanta 2013"), ("s14", "Koh-Lanta: Johor"),
    ("s15", "Koh-Lanta: Thaïlande"), ("s16", "Koh-Lanta: L'Île au Trésor"),
    ("s17", "Koh-Lanta: Cambodge"), ("s18", "Koh-Lanta: Fidji"),
    ("s19", "Koh-Lanta 2018"), ("s20", "Koh-Lanta: La Guerre des Chefs"),
    ("s21", "Koh-Lanta: Les 4 Terres"), ("s22", "Koh-Lanta: Les Armes Secrètes"),
    ("s23", "Koh-Lanta: Le Totem Maudit"), ("s24", "Koh-Lanta: Le Feu Sacré"),
    ("s25", "Koh-Lanta: Les Chasseurs d'Immunité"), ("s26", "Koh-Lanta: La Tribu Maudite"),
    ("s27", "Koh-Lanta: La Revanche des 4 Terres"), ("s28", "Koh-Lanta: Les Reliques du Destin"),
    ("sp1", "Koh-Lanta: Le Retour des Héros"), ("sp2", "Koh-Lanta: Le Choc des Héros"),
    ("sp3", "Koh-Lanta: La Revanche des Héros"), ("sp4", "Koh-Lanta: La Nouvelle Édition"),
    ("sp5", "Koh-Lanta: Le Combat des Héros"), ("sp6", "Koh-Lanta: L'Île des Héros"),
    ("sp7", "Koh-Lanta: La Légende"), ("sp8", "Koh-Lanta: All Stars"),
]

# Meme regle que fetch.py et fetch_fandom.py : le wikitexte est versionne comme
# preuve de provenance et ne se retelecharge pas, sauf demande explicite.
RAFRAICHIR = set()
if "--rafraichir" in sys.argv:
    RAFRAICHIR.update(sys.argv[sys.argv.index("--rafraichir") + 1:])

for sid, title in SEASONS:
    page = os.path.join(OUT, sid + ".wiki")
    guide = os.path.join(OUT, sid + ".epguide.wiki")
    if os.path.exists(page) and os.path.exists(guide) and sid not in RAFRAICHIR:
        continue
    txt = content(title)
    if not txt:
        print(f"{sid} : page absente — {title}")
        continue
    open(page, "w", encoding="utf-8").write(txt)
    m = re.search(r"\{\{\s*(FRS\d+epguide)\s*\}\}", txt)
    if not m:
        print(f"{sid} : {title} sans guide d'episodes")
        continue
    g = content("Template:" + m.group(1))
    if g:
        open(guide, "w", encoding="utf-8").write(g)
    print(f"{sid} : {title} -> {m.group(1)} ({len(g or '')} o)")
    time.sleep(1)
