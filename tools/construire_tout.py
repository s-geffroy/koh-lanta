#!/usr/bin/env python3
"""Refaire, dans l'ordre, tout ce qui est derive de `_data/`.

    tools/atelier python3 tools/construire_tout.py            # essai a blanc
    tools/atelier python3 tools/construire_tout.py --lancer   # refait le perime
    tools/atelier python3 tools/construire_tout.py --lancer --depuis build_stats

POURQUOI. L'ordre de construction n'etait ecrit nulle part en entier : le
README en citait cinq etapes sur huit, chaque docstring la sienne. Une etape
oubliee ne casse rien -- le site se construit, avec un fichier d'un jour en
retard sur les autres. C'est arrive a `_data/dependance.yml` et a
`_data/geographie.yml` (revue du 4 nov. 2026).

CE QUI EST REFAIT. Une etape est perimee quand l'une de ses sorties declare,
dans son en-tete, une entree qui a change depuis (voir `donnees.charger`), ou
n'en declare aucune. Les etapes se jugent UNE PAR UNE, apres celles d'amont :
`build_stats` refait a l'identique ne perime pas `dependance`, et on epargne
ses deux heures.

CE QUE L'EMPREINTE NE VOIT PAS : le code. Un generateur modifie ne perime pas
sa sortie, puisque ses entrees n'ont pas bouge. `--depuis <etape>` force alors
cette etape et toutes celles d'aval.

Les extractions qui partent de `specs/sources/` (conseils, colliers, finale...)
ne sont pas dans la chaine : elles ne lisent pas `_data/`, elles l'ecrivent, et
se relancent a la main quand une source change. `geographie_insee` telecharge
le tableau de l'INSEE : il lui faut le reseau.
"""
import argparse
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import donnees  # noqa: E402

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (nom, commande, sorties dont l'en-tete porte les entrees, duree indicative).
ETAPES = [
    ("construire_epreuves", ["tools/extraction/construire_epreuves.py", "--ecrire"],
     ["_data/epreuves.yml"], "quelques secondes"),
    ("geographie_insee", ["tools/extraction/geographie_insee.py", "--ecrire"],
     ["_data/geographie.yml"], "une minute, reseau"),
    ("build_stats", ["tools/build_stats.py"],
     ["_data/stats.yml"], "six minutes"),
    ("dependance", ["tools/dependance.py", "--ecrire"],
     ["_data/dependance.yml"], "deux heures"),
    ("build_fiches", ["tools/build_fiches.py", "--ecrire"],
     ["_data/fiches.yml", "_data/saisons_urls.yml", "_data/tableau_participations.yml"],
     "une minute"),
    ("build_epreuves", ["tools/build_epreuves.py", "--ecrire"],
     ["_data/epreuves_fiches.yml"], "quelques secondes"),
    ("build_graphiques", ["tools/build_graphiques.py"],
     ["tools/entrees/graphiques.txt"], "une minute"),
    # --tout : les cartes par fiche sont commitees, et lisent les fiches.
    ("build_partage", ["tools/build_partage.py", "--tout"],
     ["tools/entrees/partage.txt"], "quelques minutes"),
]
CONTROLES = [["tools/verifie.py"], ["tools/verifie_site.py"]]


def raisons(sorties):
    """Pourquoi l'etape est perimee ; liste vide si elle est a jour."""
    out = []
    for rel in sorties:
        chemin = os.path.join(RACINE, rel)
        if not os.path.exists(chemin):
            out.append(f"{rel} absent")
            continue
        changes = donnees.entrees_changees(chemin)
        if changes is None:
            out.append(f"{rel} sans empreinte")
        elif changes:
            out.append(f"{rel} : {', '.join(changes)} a change")
    return out


def lancer(commande):
    debut = time.time()
    r = subprocess.run([sys.executable] + commande, cwd=RACINE)
    print(f"  -> code {r.returncode}, {time.time() - debut:.0f} s", flush=True)
    return r.returncode


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--lancer", action="store_true",
                    help="refait les etapes perimees (defaut : essai a blanc)")
    ap.add_argument("--depuis", choices=[e[0] for e in ETAPES],
                    help="force cette etape et toutes celles d'aval")
    ap.add_argument("--sans-dependance", action="store_true",
                    help="saute dependance.py (deux heures) ; il restera signale perime")
    a = ap.parse_args()

    force = False
    for nom, commande, sorties, duree in ETAPES:
        force = force or nom == a.depuis
        pourquoi = ["force par --depuis"] if force else raisons(sorties)
        if not pourquoi:
            print(f"a jour   {nom}")
            continue
        if nom == "dependance" and a.sans_dependance:
            print(f"SAUTE    {nom} ({'; '.join(pourquoi)})")
            continue
        print(f"{'LANCE' if a.lancer else 'perime':8} {nom} ({duree}) : {'; '.join(pourquoi)}",
              flush=True)
        if a.lancer and lancer(commande):
            print(f"ARRET : {nom} a echoue, l'aval n'est pas refait")
            return 1

    if not a.lancer:
        print("\nessai a blanc : rien n'est lance (--lancer pour refaire le perime)")
        return 0
    echecs = 0
    for commande in CONTROLES:
        print(f"CONTROLE {commande[0]}", flush=True)
        echecs += bool(lancer(commande))
    return 1 if echecs else 0


if __name__ == "__main__":
    sys.exit(main())
