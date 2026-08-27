#!/usr/bin/env python3
"""Ecrit _data/colliers.yml : le destin de chaque collier d'immunite.

Le collier est la mecanique sur laquelle circulent le plus d'affirmations
invraisemblables -- « 42 % utilises avec succes, 33 % pour rien, 25 % elimines
avec le collier dans le sac ». Ces proportions se calculent, a condition de
savoir pour chaque collier : trouve par qui, joue ou non, sur qui, et combien
de voix annulees.

L'ISSUE est deduite, pas recopiee, et selon une regle simple :

  annulation_efficace  joue, et il annule au moins une voix ;
  joue_pour_rien       joue, et il n'annule aucune voix -- la peur a parle ;
  elimine_avec_collier trouve, jamais joue, et son detenteur est sorti au
                       conseil : le pire scenario du jeu ;
  garde_sans_usage     trouve, jamais joue, mais son detenteur n'en avait pas
                       besoin ;
  non_decouvert        cache, jamais trouve par personne.

    tools/atelier python3 tools/extraction/construire_colliers.py --ecrire
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
from parse_colliers import parse_page    # noqa: E402

SUFFIXES = (".wiki", ".fandom.wiki", ".en.wiki")

ENTETE = """# ATTENTION : fichier genere. Ne pas editer a la main.
#
# Le destin de chaque collier d'immunite : trouve par qui, joue ou non, sur qui,
# et combien de voix annulees. Produit par
# tools/extraction/construire_colliers.py.
#
# `issue` est DEDUITE : annulation_efficace, joue_pour_rien,
# elimine_avec_collier, garde_sans_usage, non_decouvert.
#
# Cette couche ne couvre QUE les colliers d'immunite. Les autres objets --
# armes secretes (2021), totem maudit (2022), talisman du feu sacre (2023) --
# sont des mecaniques distinctes, absentes d'ici.
#
#     tools/atelier python3 tools/extraction/construire_colliers.py --ecrire
#
"""


def resoudre(nom, index):
    cands = index.get(slug(nom or ""))
    if not cands:
        return None, "inconnu"
    if len(cands) > 1:
        return None, "homonyme"
    return cands[0]["id"], None


def construire(saisons, parts, rapport):
    par_saison_part = defaultdict(lambda: defaultdict(list))
    fiches = {}
    for p in parts:
        par_saison_part[p["saison"]][slug(p["nom"])].append(p)
        fiches[(p["saison"], p["id"])] = p

    colliers = []
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
                rapport.append(f"{sid} : lecture des colliers impossible ({suf}) — {e}")
                continue
            if len(lot) > len(meilleur):
                meilleur = lot
        if not meilleur:
            continue

        index = par_saison_part[sid]
        for c in meilleur:
            def rattacher(noms, role):
                out = []
                for n in noms:
                    pid, echec = resoudre(n, index)
                    if echec:
                        rapport.append(f"{sid} : {role} « {n} » non rattache ({echec})")
                    out.append({"libelle": n, "id": pid, "resolu": bool(pid)})
                return out

            detenteurs = rattacher(c["proprietaires"], "detenteur")
            autres = rattacher(c["autres_proprietaires"], "detenteur suivant")
            proteges = rattacher(c["proteges"], "protege")

            statut = c["statut"]
            annules = c["votes_annules"]
            issue = None
            if statut == "non_decouvert":
                issue = "non_decouvert"
            elif statut == "utilise":
                issue = ("annulation_efficace" if (annules or 0) > 0
                         else "joue_pour_rien")
            elif statut in ("non_utilise", None):
                # trouve mais jamais joue : son detenteur est-il sorti au conseil ?
                sortis = [fiches.get((sid, d["id"])) for d in detenteurs if d["id"]]
                sortis = [x for x in sortis if x]
                if sortis and any(x.get("sort") == "elimine_conseil" for x in sortis):
                    issue = "elimine_avec_collier"
                elif sortis:
                    issue = "garde_sans_usage"

            colliers.append({
                "saison": sid,
                "localisation": c["localisation"],
                "detenteurs": detenteurs,
                "detenteurs_suivants": autres,
                "proteges": proteges,
                "statut": statut,
                "issue": issue,
                "jour_trouve": c["jour_trouve"],
                "episode_utilisation": c["episode_utilisation"],
                "votes_annules": annules,
                "votes_exprimes": c["votes_exprimes"],
            })
    return colliers


def main():
    saisons = yaml.safe_load(open(os.path.join(RACINE, "_data", "saisons.yml")))
    parts = yaml.safe_load(open(os.path.join(RACINE, "_data", "participations.yml")))
    rapport = []
    colliers = construire(saisons, parts, rapport)

    cites = sum(len(c["detenteurs"]) + len(c["proteges"]) for c in colliers)
    resolus = sum(1 for c in colliers for x in c["detenteurs"] + c["proteges"]
                  if x["resolu"])
    issues = Counter(c["issue"] for c in colliers)
    saisons_couvertes = sorted({c["saison"] for c in colliers})

    print(f"colliers          : {len(colliers)}")
    print(f"saisons couvertes : {len(saisons_couvertes)} — {', '.join(saisons_couvertes)}")
    print(f"noms cites        : {cites}, dont {resolus} rattaches "
          f"({100*resolus/cites:.0f} %)" if cites else "")
    print("issues            :")
    for k, n in issues.most_common():
        print(f"  {str(k):24s} {n:3d}  {100*n/len(colliers):5.1f} %")
    joues = [c for c in colliers if c["statut"] == "utilise"
             and c["votes_annules"] is not None]
    if joues:
        total = sum(c["votes_annules"] for c in joues)
        print(f"\nvoix annulees     : {total} sur {len(joues)} colliers joues "
              f"({total/len(joues):.1f} par collier)")
    echecs = [r for r in rapport if "non rattache" in r]
    if echecs:
        print(f"\nrattachements manques : {len(echecs)}")
        for r in echecs[:8]:
            print("  " + r)

    if "--ecrire" in sys.argv:
        chemin = os.path.join(RACINE, "_data", "colliers.yml")
        with open(chemin, "w", encoding="utf-8") as f:
            f.write(ENTETE)
            yaml.safe_dump(colliers, f, allow_unicode=True, sort_keys=False, width=100)
        print(f"\necrit : {chemin}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
