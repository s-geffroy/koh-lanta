#!/usr/bin/env python3
"""Retrouve, dans la prose des sources, QUI est parti en ambassade.

Les tables ne disent que qui en revient elimine. Le nom des ambassadeurs, lui,
n'apparait que dans une note de bas de page accrochee a la ligne d'elimination :
« Les deux ambassadeurs (Léa et Pauline) se mettent d'accord pour éliminer
Ricky. » C'est de la prose, donc une lecture faillible -- et c'est pourquoi ce
script MESURE son taux de reussite au lieu de l'affirmer.

Trois controles, tous verifiables :
  * chaque nom lu doit designer un participant de la saison, sans homonyme ;
  * chaque ambassadeur doit etre encore en jeu a l'episode de l'ambassade ;
  * quand les deux sources nomment les ambassadeurs, elles doivent s'accorder.

    tools/atelier python3 tools/extraction/ambassadeurs.py --ecrire
"""
import argparse
import collections
import os
import re
import sys

import yaml

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
RACINE = os.path.abspath(os.path.join(ICI, "..", ".."))
sys.path.insert(0, os.path.join(RACINE, "tools"))
WIKI = os.path.join(RACINE, "specs", "sources", "wiki")
SORTIE = os.path.join(RACINE, "_data", "ambassadeurs.yml")

from parse_fandom import slug                       # noqa: E402
from indicateurs import _episode_de_sortie          # noqa: E402

RE_REF = re.compile(r"<ref[^>]*>(.*?)</ref>", re.S | re.I)
RE_LIEN = re.compile(r"\[\[\s*([^\]|]+?)\s*(?:\|\s*([^\]]*?)\s*)?\]\]")
NOM = r"[A-ZÀ-ÖØ-Þ][\wÀ-ÖØ-öø-ÿ'’-]+"
LISTE = r"(?:" + NOM + r")(?:\s*,\s*" + NOM + r")*(?:\s*,?\s*et\s+" + NOM + r")?"

# Les tournures rencontrees, de la plus explicite a la plus large. La premiere
# qui rend au moins deux noms valides l'emporte : elles sont classees par
# fiabilite, pas par frequence.
MOTIFS = [
    # « l'ambassadrice secrète (Laure) » : un adjectif peut s'intercaler.
    re.compile(r"ambassad(?:eur|rice)s?\s*(?:[a-zà-ÿ]+e?s?\s*)?\((" + LISTE + r")\)", re.I),
    re.compile(r"ambassad(?:eur|rice)s?\s*,?\s*(?:a\s+savoir|à\s+savoir)\s*:?\s*("
               + LISTE + r")", re.I),
    re.compile(r"(?:les\s+)?(?:deux|trois|quatre)?\s*ambassad(?:eur|rice)s?\s+("
               + LISTE + r")\s+(?:se\s|ne\s|n['’]|ont\s|d[ée]cid|est\s|sont\s)", re.I),
    re.compile(r"par\s+(?:les\s+)?ambassad(?:eur|rice)s?\s+(" + LISTE + r")", re.I),
    # « Cynthia, Johan, Ulrich et Zakariya, les quatre ambassadeurs. » La
    # phrase peut finir la : exiger une virgule apres ferait manquer la moitie
    # des tournures -- et, pire, ferait croire a un accord entre les sources
    # la ou l'une n'a simplement pas ete lue.
    re.compile(r"(" + LISTE + r")\s*,\s*(?:les\s+)?(?:deux|trois|quatre)?\s*"
               r"ambassad(?:eur|rice)s?\s*[,.]", re.I),
    re.compile(r"(" + LISTE + r")\s+ont\s+[ée]t[ée]\s+d[ée]sign[ée]s?\s+ambassad", re.I),
]
RE_COMPTE = re.compile(r"\b(deux|trois|quatre|cinq)\s+ambassad", re.I)
COMPTES = {"deux": 2, "trois": 3, "quatre": 4, "cinq": 5}
RE_TIRAGE = re.compile(r"tirage\s+au\s+sort|boule\s+noire|pas\s+(?:mis|mise)s?\s+d['’]accord"
                       r"|n['’]arrivant\s+pas\s+à\s+se\s+mettre\s+d['’]accord", re.I)


def nettoie(texte):
    t = RE_LIEN.sub(lambda m: m.group(2) or m.group(1), texte)
    t = t.replace("'''", "").replace("''", "")
    t = re.sub(r"<[^>]*>", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def noms_de(bout):
    return [x for x in re.split(r"\s*,\s*|\s+et\s+", bout.strip()) if re.fullmatch(NOM, x)]


def notes(sid, suffixe):
    """Les notes de bas de page qui parlent d'ambassade, dans une source."""
    chemin = os.path.join(WIKI, sid + suffixe)
    if not os.path.exists(chemin):
        return []
    texte = open(chemin, encoding="utf-8").read()
    sortie = []
    for m in RE_REF.finditer(texte):
        corps = nettoie(m.group(1))
        if re.search(r"ambassad", corps, re.I) and len(corps) < 400 and "http" not in corps:
            sortie.append(corps)
    return sortie


def lire_source(sid, suffixe, membres):
    """Rend (ambassadeurs, tirage, phrase) pour une source, ou (None, ...).

    On reunit les noms trouves par TOUTES les tournures d'une meme note, et
    non ceux de la premiere qui accroche : « Les deux ambassadeurs (Vincent et
    Maxine) et l'ambassadrice secrète (Laure) » en cite trois, en deux
    tournures. S'arreter a la premiere ferait croire a un desaccord entre les
    sources la ou il n'y en a pas.
    """
    for corps in notes(sid, suffixe):
        trouves, vus = [], set()
        for motif in MOTIFS:
            for m in motif.finditer(corps):
                for n in noms_de(m.group(1)):
                    lot = membres.get(slug(n))
                    if not lot or len(lot) > 1:
                        continue                 # inconnu ou homonyme : on s'abstient
                    pid = lot[0]["id"]
                    if pid not in vus:
                        vus.add(pid)
                        trouves.append(pid)
        if len(trouves) >= 2:
            return trouves, bool(RE_TIRAGE.search(corps)), corps
    return None, False, None


def main():
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument("--ecrire", action="store_true")
    a = a.parse_args()

    lire = lambda n: yaml.safe_load(open(os.path.join(RACINE, "_data", n), encoding="utf-8"))
    parts = lire("participations.yml")
    conseils = lire("conseils.yml")
    epreuves = lire("epreuves.yml")
    sortie_ep, _ = _episode_de_sortie(conseils, parts, epreuves)

    par_saison = collections.defaultdict(list)
    for p in parts:
        par_saison[p["saison"]].append(p)

    cibles = [p for p in parts if p.get("sort") == "elimine_ambassadeurs"]
    lignes, rapport = [], []
    accord = desaccord = 0

    for c in sorted(cibles, key=lambda x: x["saison"]):
        sid = c["saison"]
        membres = collections.defaultdict(list)
        for p in par_saison[sid]:
            membres[slug(p["nom"])].append(p)

        lectures = {}
        for suffixe in (".wiki", ".fandom.wiki"):
            noms, tirage, phrase = lire_source(sid, suffixe, membres)
            if noms:
                lectures[suffixe] = (noms, tirage, phrase)

        if not lectures:
            rapport.append(f"{sid} : aucun nom d'ambassadeur lisible")
            lignes.append({"saison": sid, "elimine": c["id"], "ambassadeurs": None,
                           "motif": "non nomme"})
            continue

        if len(lectures) == 2:
            a1 = set(lectures[".wiki"][0])
            a2 = set(lectures[".fandom.wiki"][0])
            if a1 == a2:
                accord += 1
            else:
                desaccord += 1
                rapport.append(f"{sid} : les deux sources ne nomment pas les memes "
                               f"ambassadeurs — {sorted(a1)} contre {sorted(a2)} ; "
                               f"aucun n'est retenu")
                lignes.append({"saison": sid, "elimine": c["id"], "ambassadeurs": None,
                               "motif": "sources en desaccord"})
                continue

        suffixe = ".wiki" if ".wiki" in lectures else ".fandom.wiki"
        noms, tirage, phrase = lectures[suffixe]

        # Controle : un ambassadeur est encore en jeu a l'episode de l'ambassade.
        episode = sortie_ep.get((sid, c["id"]))
        presents = [p["id"] for p in par_saison[sid]
                    if episode is None or sortie_ep.get((sid, p["id"]), -1) >= episode]
        hors = [n for n in noms if n not in presents]
        if hors:
            rapport.append(f"{sid} : {len(hors)} ambassadeur(s) deja sorti(s) a "
                           f"l'episode {episode} — lecture rejetee")
            lignes.append({"saison": sid, "elimine": c["id"], "ambassadeurs": None,
                           "motif": "ambassadeur deja sorti"})
            continue

        # « Trois des quatre ambassadeurs (…) » : c'est le plus grand nombre
        # cite qui donne la taille de l'ambassade, pas le premier.
        annonces = [COMPTES[m.group(1).lower()] for m in RE_COMPTE.finditer(phrase)]
        attendu = max(annonces) if annonces else None
        if attendu and attendu != len(noms):
            rapport.append(f"{sid} : la note annonce {attendu} ambassadeurs, "
                           f"{len(noms)} noms lus — lecture rejetee")
            lignes.append({"saison": sid, "elimine": c["id"], "ambassadeurs": None,
                           "motif": "compte annonce non tenu"})
            continue

        lignes.append({
            "saison": sid, "elimine": c["id"], "episode": episode,
            "ambassadeurs": noms, "nombre": len(noms),
            "tirage_au_sort": tirage,
            "elimine_est_ambassadeur": c["id"] in noms,
            "source": "wikipedia-fr" if suffixe == ".wiki" else "fandom",
            "phrase": phrase,
        })

    nommes = [l for l in lignes if l.get("ambassadeurs")]
    print(f"{len(cibles)} ambassades, {len(nommes)} avec leurs ambassadeurs nommes "
          f"({100.0 * len(nommes) / len(cibles):.0f} %)")
    print(f"  sources d'accord : {accord} ; en desaccord : {desaccord}")
    print(f"  ambassades tranchees par tirage au sort : "
          f"{sum(1 for l in nommes if l['tirage_au_sort'])}")
    print(f"  l'elimine etait lui-meme ambassadeur : "
          f"{sum(1 for l in nommes if l['elimine_est_ambassadeur'])}")
    for r in rapport:
        print("  " + r)

    resultat = {
        "ambassades": len(cibles),
        "nommees": len(nommes),
        "part_nommees": round(100.0 * len(nommes) / len(cibles), 1) if cibles else None,
        "sources_accord": accord,
        "sources_desaccord": desaccord,
        "par_tirage": sum(1 for l in nommes if l["tirage_au_sort"]),
        "elimine_ambassadeur": sum(1 for l in nommes if l["elimine_est_ambassadeur"]),
        "ambassadeurs_distincts": len({a for l in nommes for a in l["ambassadeurs"]}),
        "lignes": lignes,
    }
    if a.ecrire:
        with open(SORTIE, "w", encoding="utf-8") as f:
            f.write("# Fichier genere par tools/extraction/ambassadeurs.py.\n"
                    "# Ne pas editer a la main : toute modification sera ecrasee.\n")
            yaml.safe_dump(resultat, f, allow_unicode=True, sort_keys=False, width=100)
        print(f"\necrit : {SORTIE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
