#!/usr/bin/env python3
"""Ecrit _data/epreuves.yml : qui remporte quelle epreuve, episode par episode.

Une cellule de tableau ne dit qu'un nom. Tout le travail consiste a savoir ce
qu'il designe :

  * un nom de TRIBU declaree pour la saison  -> epreuve collective ;
  * un prenom present dans les participations -> epreuve individuelle ;
  * autre chose -> non resolu, et signale comme tel.

Rien n'est devine : un nom qui ne correspond ni a une tribu ni a une
participation reste tel quel, avec `resolu: false`.

    tools/atelier python3 tools/extraction/construire_epreuves.py --ecrire
"""
import os
import sys
from collections import Counter, defaultdict

import yaml

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
RACINE = os.path.abspath(os.path.join(ICI, "..", ".."))
WIKI = os.environ.get("KL_WIKI", os.path.join(RACINE, "specs", "sources", "wiki"))

from parse_fandom import slug            # noqa: E402
from parse_epreuves import parse_page    # noqa: E402

SUFFIXES = (".wiki", ".fandom.wiki", ".en.wiki")

ENTETE = """# ATTENTION : fichier genere. Ne pas editer a la main.
#
# Vainqueurs des epreuves de confort et d'immunite, episode par episode.
# Produit par tools/extraction/construire_epreuves.py depuis les bilans par
# episode de Wikipedia (fr et en) et du wiki Fandom francophone.
#
# `forme` vaut `collective` quand l'epreuve est remportee par une tribu,
# `individuelle` quand elle l'est par une personne. Les identifiants renvoient
# a participations.yml ; un nom non rattache est conserve en clair avec
# `resolu: false`.
#
#     tools/atelier python3 tools/extraction/construire_epreuves.py --ecrire
#
"""


def index_saison(saison, parts):
    tribus = {}
    for t in saison.get("tribus") or []:
        tribus[slug(t["nom"])] = t["nom"]
    personnes = defaultdict(list)
    for p in parts:
        if p["saison"] == saison["id"]:
            personnes[slug(p["nom"])].append(p)
    return tribus, personnes


def construire(saisons, parts, rapport):
    par_saison = {s["id"]: s for s in saisons}
    epreuves = []

    for s in saisons:
        if s.get("annulee"):
            continue
        sid = s["id"]
        meilleur = []
        for suf in SUFFIXES:
            chemin = os.path.join(WIKI, sid + suf)
            if not os.path.exists(chemin):
                continue
            try:
                lot = parse_page(open(chemin, encoding="utf-8").read(), sid)
            except Exception as e:
                rapport.append(f"{sid} : lecture des epreuves impossible ({suf}) — {e}")
                continue
            if len(lot) > len(meilleur):
                meilleur = lot
        if not meilleur:
            rapport.append(f"{sid} : aucun bilan d'epreuves exploitable")
            continue

        tribus, personnes = index_saison(s, parts)

        def eclater(libelle):
            """« Claude Laurent » : deux vainqueurs, pas un aventurier inconnu.

            Quelques cellules citent plusieurs gagnants sans separateur. On ne
            les coupe que si CHAQUE mot designe un aventurier de la saison et
            que l'ensemble n'en designe pas un -- sinon « Jean Charles » ou
            « Marie France » seraient coupes en deux.
            """
            mots = libelle.split()
            if len(mots) < 2 or slug(libelle) in personnes or slug(libelle) in tribus:
                return [libelle]
            if all(slug(m) in personnes for m in mots):
                return mots
            return [libelle]

        for e in meilleur:
            vainqueurs, formes = [], set()
            libelles = [x for l in e["libelles"] for x in eclater(l)]
            for libelle in libelles:
                cle = slug(libelle)
                if cle in tribus:
                    vainqueurs.append({"libelle": tribus[cle], "type": "tribu",
                                       "id": None, "resolu": True})
                    formes.add("collective")
                elif cle in personnes and len(personnes[cle]) == 1:
                    vainqueurs.append({"libelle": libelle, "type": "personne",
                                       "id": personnes[cle][0]["id"], "resolu": True})
                    formes.add("individuelle")
                elif cle in personnes:
                    vainqueurs.append({"libelle": libelle, "type": "personne",
                                       "id": None, "resolu": False})
                    formes.add("individuelle")
                    rapport.append(f"{sid} ep.{e['episode']} : « {libelle} » est un "
                                   f"homonyme, vainqueur non rattache")
                else:
                    vainqueurs.append({"libelle": libelle, "type": None,
                                       "id": None, "resolu": False})
                    rapport.append(f"{sid} ep.{e['episode']} : « {libelle} » ne "
                                   f"correspond ni a une tribu ni a un aventurier")
            if not vainqueurs:
                continue
            forme = formes.pop() if len(formes) == 1 else (
                "mixte" if len(formes) > 1 else None)
            epreuves.append({
                "saison": sid,
                "episode": e["episode"],
                "type": e["type"],
                "forme": forme,
                "vainqueurs": vainqueurs,
                "source": e["source"],
            })
    return epreuves


def main():
    saisons = yaml.safe_load(open(os.path.join(RACINE, "_data", "saisons.yml")))
    parts = yaml.safe_load(open(os.path.join(RACINE, "_data", "participations.yml")))
    rapport = []
    epreuves = construire(saisons, parts, rapport)

    total = sum(len(e["vainqueurs"]) for e in epreuves)
    resolus = sum(1 for e in epreuves for v in e["vainqueurs"] if v["resolu"])
    formes = Counter(e["forme"] for e in epreuves)
    types = Counter(e["type"] for e in epreuves)
    saisons_couvertes = len({e["saison"] for e in epreuves})

    print(f"epreuves          : {len(epreuves)}")
    print(f"saisons couvertes : {saisons_couvertes} / "
          f"{sum(1 for s in saisons if not s.get('annulee'))}")
    print(f"types             : {dict(types)}")
    print(f"formes            : {dict(formes)}")
    print(f"vainqueurs cites  : {total}, dont {resolus} rattaches "
          f"({100*resolus/total:.1f} %)")

    manques = [r for r in rapport if "aucun bilan" in r]
    if manques:
        print(f"\nsaisons sans bilan ({len(manques)}) :")
        for r in manques:
            print("  " + r)
    autres = Counter(r.split("«")[-1].split("»")[0].strip()
                     for r in rapport if "ne correspond" in r)
    if autres:
        print(f"\nlibelles non rattaches ({sum(autres.values())} citations, "
              f"{len(autres)} distincts) :")
        for nom, n in autres.most_common(14):
            print(f"  {n:4d}  {nom!r}")

    if "--ecrire" in sys.argv:
        chemin = os.path.join(RACINE, "_data", "epreuves.yml")
        with open(chemin, "w", encoding="utf-8") as f:
            f.write(ENTETE)
            yaml.safe_dump(epreuves, f, allow_unicode=True, sort_keys=False, width=100)
        print(f"\necrit : {chemin}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
