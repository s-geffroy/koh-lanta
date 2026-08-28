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
# `type` vaut `elimination` ou `jury`. Le dernier scrutin d'une saison n'est
# pas un conseil : c'est le vote du jury final, et le sens du bulletin y est
# INVERSE -- ecrire un nom veut dire « qu'il gagne », pas « qu'il parte ». Une
# ligne `jury` porte donc `laureat` et `votes_pour`, jamais `elimine` ni
# `votes_contre`, pour qu'aucun calcul ne puisse les confondre.
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
    # Le vainqueur d'une saison ne peut pas avoir ete elimine au conseil : si
    # une matrice le donne « sortant », c'est qu'on lit le vote du jury final.
    # La cle porte la saison : l'identifiant seul est celui de la PERSONNE, et
    # un vainqueur qui rejoue une autre saison n'y est pas vainqueur pour
    # autant. Sans la saison, on classerait « jury » des conseils ordinaires.
    vainqueurs = {(p["saison"], p["id"]) for p in parts if p.get("sort") == "vainqueur"}
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
        # Bornes du vote de jury, calculees avant la boucle : le dernier numero
        # de conseil de la saison, et le nombre de vainqueurs declares.
        dernier_conseil = max((c["numero"] for c in meilleure), default=0)
        nb_laureats = max(1, len(s.get("vainqueurs") or []))
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
            # Nommer le vainqueur ne suffit pas a faire un vote de jury : il
            # faut aussi que le conseil soit a sa place. Une saison a k
            # vainqueurs declares tient k scrutins de jury -- un par laureat
            # quand le jury s'est partage -- et ce sont les k derniers. Un
            # conseil de milieu de saison qui donne le vainqueur « sortant »
            # n'est pas un vote de jury : c'est une extraction fautive, et on
            # prefere ne rien affirmer plutot que d'affirmer faux.
            gagnant = bool(elimine_id) and (sid, elimine_id) in vainqueurs
            final = c["numero"] > dernier_conseil - nb_laureats
            jury = gagnant and final
            if gagnant and not final:
                rapport.append(f"{sid} conseil {c['numero']} : ABERRANT — "
                               f"« {c['elimine']} » gagne la saison mais serait "
                               f"sortant au conseil {c['numero']}/{dernier_conseil} ; "
                               f"elimine laisse non rattache")
                elimine_id = None
            if jury:
                rapport.append(f"{sid} conseil {c['numero']} : vote du JURY FINAL "
                               f"(« {c['elimine']} » n'est pas sortant, il gagne)")
            commun = {
                "saison": sid,
                "numero": c["numero"],
                "type": "jury" if jury else "elimination",
                "complet": c.get("complet", False),
                "episode": c["episode"],
            }
            if jury:
                commun.update({
                    "laureat": elimine_id,
                    "laureat_rattache": True,
                    "votes_pour": c["votes_contre"],
                })
            else:
                commun.update({
                    "elimine": elimine_id or c["elimine"],
                    "elimine_rattache": bool(elimine_id),
                    "votes_contre": c["votes_contre"],
                })
            commun["votes_exprimes"] = c["votes_exprimes"]
            # Une voix barree dans la matrice n'a pas toujours la meme cause.
            # Si SEULE une partie des bulletins est barree, c'est qu'un objet
            # d'immunite a protege quelqu'un : les autres voix comptent, et
            # quelqu'un sort. Si TOUS le sont, c'est le tour entier qui est
            # nul -- egalite suivie d'un second vote, le plus souvent. Les
            # confondre, c'est attribuer aux colliers des annulations qui ne
            # leur doivent rien.
            barres = [b for b in bulletins if b["annule"]]
            if barres:
                commun["annulation"] = ("totale" if len(barres) == len(bulletins)
                                        else "partielle")
                commun["voix_annulees"] = len(barres)
                if commun["annulation"] == "partielle":
                    proteges = sorted({b["cible"] for b in barres})
                    commun["proteges"] = proteges
            commun["votes"] = bulletins
            conseils.append(commun)
    return conseils


def main():
    saisons = yaml.safe_load(open(os.path.join(RACINE, "_data", "saisons.yml")))
    parts = yaml.safe_load(open(os.path.join(RACINE, "_data", "participations.yml")))
    rapport = []
    conseils = construire(saisons, parts, rapport)

    bulletins = sum(len(c["votes"]) for c in conseils)
    rattaches = sum(1 for c in conseils for b in c["votes"]
                    if b["votant_rattache"] and b["cible_rattachee"])
    jurys = [c for c in conseils if c["type"] == "jury"]
    print(f"conseils   : {len(conseils)} dont {len(jurys)} votes de jury final")
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
