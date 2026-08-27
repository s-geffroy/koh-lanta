#!/usr/bin/env python3
"""Ecrit _data/conseils.yml a partir des matrices de votes des pages sources.

Les tables de votes ne designent les gens que par leur prenom. Ce script les
rattache aux participations deja constituees, pour que chaque bulletin porte un
identifiant utilisable et non une chaine de caracteres.

Un prenom porte par deux personnes d'une meme saison (deux Lea en 25, deux
Cecile en 26, deux Jerome en 27) n'est PAS devine : le bulletin garde le prenom
et signale que le rattachement a echoue.
"""
import os
import sys
from collections import defaultdict

import yaml

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
RACINE = os.path.abspath(os.path.join(ICI, "..", ".."))
WIKI = os.environ.get("KL_WIKI", os.path.join(RACINE, "specs", "sources", "wiki"))

from parse_fandom import slug
from parse_votes import parse_page

ENTETE = """# ATTENTION : fichier genere. Ne pas editer a la main.
#
# Detail des conseils : qui part, avec combien de voix, et le bulletin de
# chacun. Produit par tools/extraction/construire_conseils.py depuis les
# matrices « Detail des votes » du wiki Fandom francophone et de Wikipedia.
#
# `annule: true` sur un bulletin signale une voix rendue nulle par un collier
# d'immunite : c'est ce qui permet de mesurer l'effet reel des colliers.
#
#     tools/atelier python3 tools/extraction/construire_conseils.py --ecrire
#
"""


def index_participations(parts):
    """prenom normalise -> liste de participations, par saison."""
    idx = defaultdict(lambda: defaultdict(list))
    for p in parts:
        idx[p["saison"]][slug(p["nom"])].append(p)
    return idx


def resoudre(nom, index_saison):
    """Rend (identifiant, motif_d_echec)."""
    cands = index_saison.get(slug(nom or ""))
    if not cands:
        return None, "inconnu"
    if len(cands) > 1:
        return None, "homonyme"
    return cands[0]["id"], None


def construire(saisons, parts, rapport):
    index = index_participations(parts)
    conseils = []

    for s in saisons:
        if s.get("annulee"):
            continue
        sid = s["id"]
        # on garde la lecture la plus riche des deux sources
        meilleure, meilleur_score = [], -1
        for suffixe in (".fandom.wiki", ".wiki"):
            chemin = os.path.join(WIKI, sid + suffixe)
            if not os.path.exists(chemin):
                continue
            try:
                lus = parse_page(open(chemin, encoding="utf-8").read(), sid)
            except Exception as e:
                rapport.append(f"{sid} : lecture des votes impossible ({suffixe}) — {e}")
                continue
            score = sum(len(c["votes"]) for c in lus)
            if score > meilleur_score:
                meilleure, meilleur_score = lus, score

        if not meilleure:
            rapport.append(f"{sid} : aucune matrice de votes exploitable")
            continue

        idx = index.get(sid, {})
        for c in meilleure:
            elimine_id, echec = resoudre(c["elimine"], idx)
            if echec:
                rapport.append(f"{sid} conseil {c['numero']} : elimine « {c['elimine']} » "
                               f"non rattache ({echec})")
            bulletins = []
            for b in c["votes"]:
                vid, e1 = resoudre(b["votant"], idx)
                cid, e2 = resoudre(b["cible"], idx)
                if e1 or e2:
                    rapport.append(f"{sid} conseil {c['numero']} : bulletin "
                                   f"« {b['votant']} » -> « {b['cible']} » non rattache "
                                   f"({e1 or ''}{'/' if e1 and e2 else ''}{e2 or ''})")
                bulletins.append({
                    "votant": vid or b["votant"],
                    "votant_rattache": bool(vid),
                    "cible": cid or b["cible"],
                    "cible_rattachee": bool(cid),
                    "annule": b["annule"],
                })
            conseils.append({
                "saison": sid,
                "numero": c["numero"],
                "complet": c.get("complet", False),
                "episode": c["episode"],
                "elimine": elimine_id or c["elimine"],
                "elimine_rattache": bool(elimine_id),
                "votes_contre": c["votes_contre"],
                "votes_exprimes": c["votes_exprimes"],
                "votes": bulletins,
            })
    return conseils


def main():
    saisons = yaml.safe_load(open(os.path.join(RACINE, "_data", "saisons.yml")))
    parts = yaml.safe_load(open(os.path.join(RACINE, "_data", "participations.yml")))
    rapport = []
    conseils = construire(saisons, parts, rapport)

    bulletins = sum(len(c["votes"]) for c in conseils)
    rattaches = sum(1 for c in conseils for b in c["votes"]
                    if b["votant_rattache"] and b["cible_rattachee"])
    print(f"conseils   : {len(conseils)}")
    print(f"bulletins  : {bulletins}")
    print(f"rattaches  : {rattaches}  ({100*rattaches/bulletins:.1f} %)")

    from collections import Counter
    motifs = Counter(r.split("(")[-1].rstrip(")") for r in rapport if "non rattache" in r)
    if motifs:
        print("\nechecs de rattachement :", dict(motifs))
    autres = [r for r in rapport if "non rattache" not in r]
    if autres:
        print(f"\nautres remarques ({len(autres)}) :")
        for r in autres[:12]:
            print("  " + r)

    if "--ecrire" in sys.argv:
        chemin = os.path.join(RACINE, "_data", "conseils.yml")
        with open(chemin, "w", encoding="utf-8") as f:
            f.write(ENTETE)
            yaml.safe_dump(conseils, f, allow_unicode=True, sort_keys=False, width=100)
        print(f"\necrit : {chemin}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
