#!/usr/bin/env python3
"""Fabrique une page par epreuve nommee.

POURQUOI. Le site comptait ses epreuves mais n'en decrivait aucune. Or « record
poteaux koh lanta », « epreuve orientation koh lanta » sont des recherches que
les gens font, et le site avait la matiere sans jamais l'exposer : quelles
saisons, combien de fois, et qui l'a gagnee.

    tools/atelier python3 tools/build_epreuves.py --ecrire

CE QUI EXPLIQUE LE NOMBRE DE PAGES, ET POURQUOI IL N'EST PAS 53.
`_data/epreuves_nommees.yml` liste 53 noms, mais le raccord entre le nom cite
par le wiki et l'epreuve relevee dans la saison ne tient que sur 14,3 % des
cas. Concretement : quatre noms n'ont AUCUNE apparition datee (« Poteaux » y
compris, la plus connue), et dix-sept n'ont aucun vainqueur nomme. Publier ces
pages-la donnerait des coquilles vides -- exactement ce qu'un moteur compte
contre le site entier, pas seulement contre elles.

Le seuil retenu -- SEUIL_APPARITIONS et SEUIL_VAINQUEURS -- garde donc les
epreuves qui portent un tableau, et laisse les autres dehors. Elles restent
comptees sur /statistiques/epreuves/, qui est leur place : une ligne dans un
tableau n'a pas les memes exigences qu'une page a elle seule.
"""
import argparse
import collections
import os
import sys

import yaml

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
RACINE = os.path.dirname(ICI)
DATA = os.path.join(RACINE, "_data")

from build_fiches import (affichable, assembler, charger, compte,  # noqa: E402
                          ecrire_pages, identifiant, liste,
                          premier_qui_tient)

DOSSIER = os.path.join(RACINE, "epreuves")
SORTIE_DATA = os.path.join(DATA, "epreuves_fiches.yml")

# Une epreuve merite sa page si elle a ete courue assez souvent POUR qu'on
# puisse en dire quelque chose, et si l'on sait qui l'a gagnee au moins
# quelques fois. Les deux ensemble : une epreuve tres courue mais sans aucun
# vainqueur nomme ne donne qu'une liste de saisons.
SEUIL_APPARITIONS = 5
SEUIL_VAINQUEURS = 4

ENTETE = ("# ATTENTION : fichier genere par tools/build_epreuves.py.\n"
          "# Ne pas editer a la main : toute modification sera ecrasee.\n"
          "#\n"
          "# Une entree par epreuve nommee qui passe le seuil, indexee par son\n"
          "# identifiant. Le gabarit `fiche-epreuve` y accede par cle.\n"
          "#\n"
          "#     tools/atelier python3 tools/build_epreuves.py --ecrire\n"
          "#\n")


def fiches_des_epreuves(nommees, saisons, fiches):
    par_id = {s["id"]: s for s in saisons}
    noms = {a: e for a, e in (fiches.get("aventuriers") or {}).items()}

    # palmares : une entree par personne ET par saison, avec les epreuves
    # qu'elle y a gagnees. On l'inverse pour obtenir, par epreuve, qui l'a
    # emportee et quand.
    victoires = collections.defaultdict(list)
    for p in nommees.get("palmares") or []:
        for nom in p.get("epreuves") or []:
            victoires[nom].append((p["id"], p["saison"]))

    out = {}
    for e in nommees.get("epreuves") or []:
        nom = e["nom"]
        gagnees = victoires.get(nom) or []
        if e["apparitions"] < SEUIL_APPARITIONS or len(gagnees) < SEUIL_VAINQUEURS:
            continue

        editions = []
        for sid in e.get("saisons") or []:
            s = par_id.get(sid)
            if s:
                editions.append({"id": sid, "titre": s["titre"], "annee": s["annee"],
                                 "speciale": bool(s.get("speciale"))})
        editions.sort(key=lambda x: (x["annee"], x["id"]))

        # Le palmares de l'epreuve : qui l'a gagnee, et combien de fois.
        par_personne = collections.defaultdict(list)
        for pid, sid in gagnees:
            par_personne[pid].append(sid)
        palmares = []
        for pid, sids in par_personne.items():
            f = noms.get(pid)
            if not f:
                continue
            palmares.append({
                "id": pid, "nom": f["nom"], "victoires": len(sids),
                "saisons": [{"id": s, "titre": (par_id.get(s) or {}).get("titre"),
                             "annee": (par_id.get(s) or {}).get("annee")}
                            for s in sorted(sids)],
            })
        palmares.sort(key=lambda x: (-x["victoires"], x["nom"]))

        annees = [x["annee"] for x in editions]
        out[identifiant(nom)] = {
            "id": identifiant(nom),
            "nom": affichable(nom),
            "type": e.get("type"),
            "natures": e.get("natures") or [],
            "apparitions": e["apparitions"],
            "editions": editions,
            "premiere_annee": min(annees) if annees else None,
            "derniere_annee": max(annees) if annees else None,
            "palmares": palmares,
            "vainqueurs_nommes": len(gagnees),
            "record": palmares[0] if palmares else None,
        }
    return out


def titre_seo(e):
    # L'echelle de repli descend jusqu'au nom nu : « Parcours du combattant »
    # fait deja 22 caracteres, et le suffixe du site en prend 24. Un nom seul
    # reste une bonne cible -- on cherche « parcours du combattant koh lanta »,
    # et le suffixe fournit la marque.
    return premier_qui_tient([
        f"{e['nom']} : le record et les vainqueurs",
        f"{e['nom']} : les vainqueurs",
        f"{e['nom']} : le record",
        e["nom"],
    ])


def description_seo(e):
    tete = (f"L'épreuve « {e['nom'].lower()} » de Koh-Lanta : "
            f"{compte(e['apparitions'], 'apparition', 'apparitions')}")
    clauses = [
        (f"de {e['premiere_annee']} à {e['derniere_annee']}"
         if e["premiere_annee"] and e["derniere_annee"] != e["premiere_annee"]
         else None),
        compte(len(e["editions"]), "édition", "éditions"),
    ]
    r = e.get("record")
    if r and r["victoires"] > 1:
        chute = f"Record : {r['nom']}, {compte(r['victoires'], 'victoire', 'victoires')}."
    elif r:
        chute = "Qui l'a gagnée, et dans quelles éditions."
    else:
        chute = "Les éditions où elle a été courue."
    return assembler(tete, clauses, chute)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ecrire", action="store_true",
                    help="ecrit _data/epreuves_fiches.yml et les pages "
                         "(defaut : essai a blanc)")
    a = ap.parse_args()

    nommees = charger("epreuves_nommees")
    saisons = liste(charger("saisons"), "saisons")
    fiches = charger("fiches")

    ep = fiches_des_epreuves(nommees, saisons, fiches)
    total = len(nommees.get("epreuves") or [])
    print(f"epreuves nommees : {total}   retenues : {len(ep)} "
          f"(seuil : {SEUIL_APPARITIONS} apparitions et "
          f"{SEUIL_VAINQUEURS} vainqueurs nommes)")
    for cle, e in sorted(ep.items(), key=lambda kv: -kv[1]["apparitions"])[:5]:
        print(f"  {e['nom']:30s} {e['apparitions']:3d} apparitions, "
              f"{len(e['palmares']):3d} vainqueurs")

    if not a.ecrire:
        print("essai a blanc : rien n'est ecrit (--ecrire pour ecrire)")
        return 0

    with open(SORTIE_DATA, "w", encoding="utf-8") as f:
        f.write(ENTETE)
        yaml.safe_dump({"epreuves": ep}, f, allow_unicode=True, sort_keys=True,
                       default_flow_style=False)
    print(f"ecrit : {SORTIE_DATA}")

    rapport = collections.Counter()
    n = ecrire_pages(DOSSIER, "fiche-epreuve", "epreuve", ep,
                     titre_seo, description_seo,
                     lambda cid: f"/epreuves/{cid}/", rapport)
    print(f"pages : {n} epreuves ({rapport['ecrites']} ecrites, "
          f"{rapport['retirees']} retirees)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
