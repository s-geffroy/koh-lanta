#!/usr/bin/env python3
"""Ecrit _data/finale.yml : orientation, poteaux, choix du finaliste, victoire.

Rien de tout cela n'est ailleurs dans le jeu de donnees. `epreuves.yml` ne
porte AUCUN nom d'epreuve, et la derniere epreuve d'immunite individuelle
relevee n'est pas les poteaux -- pour huit saisons, son vainqueur est justement
la personne portee `elimine_poteaux`. La deduire serait faux.

Deux sources, croisees :

  * le TABLEAU de deroulement des deux wikis, qui porte deux colonnes titrees
    « Epreuve d'orientation » et « Epreuve des poteaux ». La premiere liste les
    qualifies, la seconde nomme le vainqueur, et la suivante donne le vainqueur
    de la saison -- ce dernier sert de controle : s'il ne coincide pas avec le
    `sort: vainqueur` des participations, la lecture est rejetee en bloc.

  * la PROSE et les notes de bas de page, ou la phrase est stable :
    « Cynthia, vainqueur de l'epreuve des poteaux, decide d'affronter
    Clarisse », « Guillaume n'est pas choisi par Cynthia, gagnante des
    poteaux ». Elle seule ATTESTE le choix : le tableau, lui, ne dit que qui a
    gagne les poteaux.

L'ordre des noms dans la cellule d'orientation est l'ordre d'arrivee. Ce n'est
pas une supposition : la prose de deux saisons le dit independamment (Steeve
« premier a trouver son poignard » en s20, Nicolas « trouve le premier
poignard » en s24), et ils sont ecrits en tete dans les deux cas. Le controle
est refait a chaque passage et son taux est publie ; une contradiction est une
erreur, pas un arrondi.

Aucune valeur n'est devinee. Un champ que les sources ne donnent pas reste
absent.

    tools/atelier python3 tools/extraction/finale.py --ecrire
"""
import os
import re
import sys
from collections import defaultdict

import yaml

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
RACINE = os.path.abspath(os.path.join(ICI, "..", ".."))
WIKI = os.environ.get("KL_WIKI", os.path.join(RACINE, "specs", "sources", "wiki"))

from parse_fandom import plain, slug, split_rows, split_cells

ENTETE = """# ATTENTION : fichier genere. Ne pas editer a la main.
#
# La fin de saison : qui s'est qualifie a l'orientation et dans quel ordre, qui
# a gagne les poteaux, qui il a emmene en finale, et qui a gagne.
#
# Produit par tools/extraction/finale.py, qui croise le tableau de deroulement
# des deux wikis et la prose des notes de bas de page.
#
# `ordre_atteste` dit si une source ENONCE l'ordre d'arrivee a l'orientation ;
# `choix_atteste` dit si une source ENONCE que le vainqueur des poteaux a
# choisi son finaliste. Sans eux, l'ordre reste celui de la cellule et
# `autre_finaliste` reste une simple arithmetique -- pas un choix constate.
#
#     tools/atelier python3 tools/extraction/finale.py --ecrire
#
"""

RE_ENTETE_POTEAUX = re.compile(r"[ée]preuve\s+des\s+poteaux", re.I)
RE_ENTETE_ORIENT = re.compile(r"[ée]preuve\s+d['’\s]*(?:e\s+l['’])?\s*orientation", re.I)
RE_SEPARATEUR = re.compile(r"\s*(?:,|&|/|\bet\b|\bpuis\b)\s*", re.I)

# La phrase du choix. On ne cherche pas a la decouper : on releve les noms dans
# leur ordre d'apparition, et c'est la NEGATION qui dit lequel est lequel.
RE_PHRASE_CHOIX = re.compile(
    r"[^.\n]{0,200}poteaux[^.\n]{0,200}", re.I)
RE_VERBE_CHOIX = re.compile(
    r"choisi|choisit|d[ée]cide|emm[eè]ne|rejoindre|accompagner|affronter|s[ée]lectionn", re.I)
RE_NEGATION = re.compile(r"n['’]\s*(?:est|a|avait)\s+pas\s+(?:[ée]t[ée]\s+)?choisi", re.I)
RE_TITRE_POTEAUX = re.compile(r"(?:gagnant|gagnante|vainqueur|vainqueure|remporte)", re.I)

# L'ordre d'arrivee a l'orientation, quand une source l'enonce.
# L'ordre d'arrivee a l'orientation, quand le recit le donne. Le nom n'est pas
# toujours du meme cote du verbe -- « Loic trouve le premier poignard », mais
# « le dernier poignard, qui est finalement trouve par Alexandra » -- donc on
# cherche la tournure d'abord, et le nom le plus proche ensuite.
#
# Un piege a ete paye ici : « Frederic [...] est le premier qualifie POUR
# l'epreuve d'orientation » parle de l'epreuve d'AVANT, pas de l'arrivee.
RANGS = [
    (1, r"trouve\s+le\s+premier\s+poignard"
        r"|est\s+l[ea]\s+premi[eè]re?\s+[àa]\s+trouver\s+(?:son|le)\s+poignard"
        r"|remporte\s+l['’][ée]preuve\s+d['’]orientation"),
    (2, r"trouve\s+le\s+(?:deuxi[eè]me|second)\s+poignard"),
    (3, r"trouve\s+le\s+(?:dernier|troisi[eè]me)\s+poignard"
        r"|(?:dernier|troisi[eè]me)\s+poignard[^.\n]{0,60}?trouv[ée]\s+par"),
]
RE_FAUX_PREMIER = re.compile(r"qualifi[ée]e?s?\s+pour", re.I)
RE_MOT_PROPRE = re.compile(r"[A-ZÉÈÊÀÂÎÔÛÇ][\wÀ-ÿ'’-]+")


def lire(sid):
    """Les deux lectures possibles d'une saison, la plus riche d'abord."""
    out = []
    for suffixe, nom in ((".wiki", "wikipedia"), (".fandom.wiki", "fandom")):
        chemin = os.path.join(WIKI, sid + suffixe)
        if os.path.exists(chemin):
            out.append((nom, open(chemin, encoding="utf-8", errors="replace").read()))
    return out


def index_saison(parts, sid):
    """prenom ou nom complet normalise -> participations de la saison."""
    idx = defaultdict(list)
    for p in parts:
        if p["saison"] != sid:
            continue
        idx[slug(p["nom"])].append(p)
        if p.get("nom_complet"):
            idx[slug(p["nom_complet"])].append(p)
    return idx


def resoudre(nom, idx, restreint=None):
    """Un identifiant, ou None si le nom est inconnu ou porte par deux personnes.

    `restreint` limite la recherche a un sous-ensemble d'identifiants. Ce n'est
    pas une facon de deviner : deux Lea en s25, deux Jerome en s27, et une
    seule des deux est dans le trio des poteaux. La phrase parle du trio ; la
    chercher dans le trio ne cree aucune ambiguite, elle en leve une.
    """
    cands = idx.get(slug(nom or ""))
    if not cands:
        return None
    ids = {p["id"] for p in cands}
    if restreint is not None and len(ids) > 1:
        ids &= set(restreint)
    return ids.pop() if len(ids) == 1 else None


def noms_de_cellule(cellule, idx, autorises):
    """Les identifiants cites par une cellule, dans l'ordre ou elle les ecrit."""
    texte = plain(cellule)
    if not texte or len(texte) > 120:
        return []
    vus = []
    for morceau in RE_SEPARATEUR.split(texte):
        pid = resoudre(morceau.strip(), idx, autorises)
        if pid and pid in autorises and pid not in vus:
            vus.append(pid)
    return vus


def lire_tableau(texte, idx, trio, vainqueurs):
    """La ligne qui suit l'en-tete « Epreuve des poteaux ».

    Rend (qualifies, vainqueur_poteaux) ou (None, None). Le vainqueur de la
    saison, lu dans la cellule suivante, sert de controle : s'il ne coincide
    pas, on ne rend rien plutot que de rendre faux.
    """
    lignes = split_rows(texte)
    for i, ligne in enumerate(lignes):
        if not (RE_ENTETE_POTEAUX.search(ligne) and RE_ENTETE_ORIENT.search(ligne)):
            continue
        for suite in lignes[i + 1:i + 3]:
            cellules = split_cells(suite)
            qualifies, poteaux, gagnant, position = None, None, None, None
            for k, cellule in enumerate(cellules):
                trouves = noms_de_cellule(cellule, idx, trio)
                if qualifies is None:
                    if len(trouves) >= 2:
                        qualifies, position = trouves, k
                    continue
                if poteaux is None:
                    if len(trouves) == 1:
                        poteaux = trouves[0]
                    continue
                if gagnant is None and len(trouves) == 1:
                    gagnant = trouves[0]
                    break
            if qualifies and poteaux:
                if gagnant is not None and gagnant not in vainqueurs:
                    return None, None      # colonnes mal alignees : on rejette
                return qualifies, poteaux
    return None, None


def lire_prose(texte, idx, trio):
    """Le choix du finaliste, quand une phrase l'enonce.

    Rend (vainqueur_poteaux, choisi) ou (None, None).
    """
    for m in RE_PHRASE_CHOIX.finditer(texte):
        phrase = re.sub(r"\s+", " ", m.group(0))
        if not RE_VERBE_CHOIX.search(phrase) or not RE_TITRE_POTEAUX.search(phrase):
            continue
        ordre = []
        for mot in re.finditer(r"[A-ZÉÈÊÀÂÎÔÛÇ][\wÀ-ÿ'’-]+(?:[- ][A-ZÉÈÊÀÂÎÔÛÇ][\wÀ-ÿ'’-]+)?", phrase):
            pid = resoudre(mot.group(0), idx, trio)
            if pid and pid in trio and pid not in ordre:
                ordre.append(pid)
        if len(ordre) < 2:
            continue
        if RE_NEGATION.search(phrase):
            return ordre[1], None          # « X n'est pas choisi par Y » : Y gagne
        return ordre[0], ordre[1]
    return None, None


def _nom_le_plus_proche(texte, debut, fin, idx, qualifies):
    """Le nom du trio le plus proche d'une tournure, avant elle puis apres."""
    avant = texte[max(0, debut - 90):debut]
    for m in reversed(list(RE_MOT_PROPRE.finditer(avant))):
        pid = resoudre(m.group(0), idx, qualifies)
        if pid in qualifies:
            return pid
    for m in RE_MOT_PROPRE.finditer(texte[fin:fin + 90]):
        pid = resoudre(m.group(0), idx, qualifies)
        if pid in qualifies:
            return pid
    return None


def rangs_attestes(texte, idx, qualifies):
    """rang d'arrivee -> identifiant, pour les rangs que le recit nomme."""
    trouves = {}
    for rang, motif in RANGS:
        for m in re.finditer(motif, texte, re.I):
            contexte = texte[max(0, m.start() - 60):m.end() + 20]
            if RE_FAUX_PREMIER.search(contexte):
                continue
            pid = _nom_le_plus_proche(texte, m.start(), m.end(), idx, qualifies)
            if pid and pid not in trouves.values():
                trouves[rang] = pid
                break
    return trouves


def construire(saisons, parts, rapport):
    par_saison = defaultdict(list)
    for p in parts:
        par_saison[p["saison"]].append(p)

    lignes = []
    for s in saisons:
        if s.get("annulee") or s.get("en_cours"):
            continue
        sid = s["id"]
        gens = par_saison.get(sid) or []
        vainqueurs = {p["id"] for p in gens if p.get("sort") == "vainqueur"}
        finalistes = {p["id"] for p in gens if p.get("sort") == "finaliste"}
        poteaux_elimines = {p["id"] for p in gens if p.get("sort") == "elimine_poteaux"}
        orientation_elimines = sorted(p["id"] for p in gens
                                      if p.get("sort") == "elimine_orientation")
        # Le trio des poteaux : les deux finalistes et celui qu'ils y ont laisse.
        trio = vainqueurs | finalistes | poteaux_elimines
        if len(vainqueurs) != 1 or len(finalistes) != 1 or len(poteaux_elimines) != 1:
            rapport.append(f"{sid} : fin de saison hors format "
                           f"({len(vainqueurs)} vainqueur(s), {len(finalistes)} "
                           f"finaliste(s), {len(poteaux_elimines)} elimine(s) aux "
                           f"poteaux) — saison ecartee")
            continue

        idx = index_saison(parts, sid)
        ligne = {
            "saison": sid, "titre": s.get("titre"), "annee": s.get("annee"),
            "speciale": bool(s.get("speciale")),
            "vainqueur": sorted(vainqueurs)[0],
            "orientation": {"elimines": orientation_elimines},
            "poteaux": {"elimine": sorted(poteaux_elimines)[0]},
        }
        sources = {}
        lectures = {}
        for nom, texte in lire(sid):
            qualifies, poteaux = lire_tableau(texte, idx, trio, vainqueurs)
            if qualifies:
                lectures[nom] = qualifies
            if qualifies and "qualifies" not in ligne["orientation"]:
                ligne["orientation"]["qualifies"] = qualifies
                sources["orientation"] = f"tableau {nom}"
            if poteaux and "vainqueur" not in ligne["poteaux"]:
                ligne["poteaux"]["vainqueur"] = poteaux
                sources["poteaux"] = f"tableau {nom}"
            elif poteaux and ligne["poteaux"].get("vainqueur") not in (None, poteaux):
                rapport.append(f"{sid} : les deux sources ne donnent pas le meme "
                               f"vainqueur des poteaux "
                               f"({ligne['poteaux']['vainqueur']} / {poteaux})")

        for nom, texte in lire(sid):
            gagnant, choisi = lire_prose(texte, idx, trio)
            if gagnant and "vainqueur" not in ligne["poteaux"]:
                ligne["poteaux"]["vainqueur"] = gagnant
                sources["poteaux"] = f"prose {nom}"
            elif gagnant and ligne["poteaux"]["vainqueur"] != gagnant:
                rapport.append(f"{sid} : la prose {nom} donne « {gagnant} » vainqueur "
                               f"des poteaux, le tableau donne "
                               f"« {ligne['poteaux']['vainqueur']} »")
            if choisi and not ligne["poteaux"].get("choix_atteste"):
                ligne["poteaux"]["choisi"] = choisi
                ligne["poteaux"]["choix_atteste"] = True
                sources["choix"] = f"prose {nom}"

        gagnant_poteaux = ligne["poteaux"].get("vainqueur")
        if gagnant_poteaux:
            # Le troisieme larron : celui du trio qui n'a ni gagne les poteaux
            # ni ete elimine dessus. C'est de l'arithmetique, pas un choix
            # constate -- d'ou le champ separe.
            reste = trio - {gagnant_poteaux, ligne["poteaux"]["elimine"]}
            if len(reste) == 1:
                ligne["poteaux"]["autre_finaliste"] = reste.pop()
            if gagnant_poteaux == ligne["poteaux"]["elimine"]:
                rapport.append(f"{sid} : ABERRANT — « {gagnant_poteaux} » gagnerait "
                               f"les poteaux et en serait elimine ; lecture rejetee")
                ligne["poteaux"].pop("vainqueur")
                ligne["poteaux"].pop("autre_finaliste", None)

        # L'epreuve croisee de l'ORDRE. Deux wikis ecrits separement : s'ils
        # rangent les memes noms dans le meme ordre, c'est que l'ordre transcrit
        # quelque chose ; s'ils divergent, il est arbitraire et ne peut servir
        # de classement. C'est la meme methode que pour les bulletins, et elle
        # se publie de la meme facon.
        if len(lectures) == 2:
            a, b = lectures.values()
            if set(a) == set(b):
                ligne["orientation"]["ordre_croise"] = (a == b)

        qualifies = ligne["orientation"].get("qualifies")
        if qualifies:
            manquants = trio - set(qualifies)
            if manquants:
                rapport.append(f"{sid} : la cellule d'orientation ne cite que "
                               f"{len(qualifies)} du trio des poteaux "
                               f"(manque {sorted(manquants)})")
            # Le recit donne parfois un rang, parfois trois. Chacun est
            # confronte a la place que la cellule lui donne : c'est la seule
            # facon de savoir si l'ordre ecrit est l'ordre d'arrivee.
            confirmes, dementis = 0, 0
            for nom, texte in lire(sid):
                for rang, pid in sorted(rangs_attestes(texte, idx, qualifies).items()):
                    if rang > len(qualifies):
                        continue
                    if qualifies[rang - 1] == pid:
                        confirmes += 1
                    else:
                        dementis += 1
                        rapport.append(f"{sid} : la prose {nom} donne « {pid} » "
                                       f"au rang {rang} de l'orientation, la cellule "
                                       f"y ecrit « {qualifies[rang - 1]} »")
                if confirmes or dementis:
                    sources["ordre"] = f"prose {nom}"
                    break
            if confirmes or dementis:
                ligne["orientation"]["rangs_confirmes"] = confirmes
                ligne["orientation"]["rangs_dementis"] = dementis
                ligne["orientation"]["ordre_atteste"] = dementis == 0

        ligne["sources"] = sources
        lignes.append(ligne)
    return lignes


def couverture(lignes):
    total = len(lignes)
    avec_poteaux = [x for x in lignes if x["poteaux"].get("vainqueur")]
    return {
        "saisons_au_format": total,
        "vainqueur_des_poteaux_connu": len(avec_poteaux),
        "part_poteaux": round(100.0 * len(avec_poteaux) / total, 1) if total else None,
        "choix_atteste": sum(1 for x in lignes if x["poteaux"].get("choix_atteste")),
        "qualifies_connus": sum(1 for x in lignes if x["orientation"].get("qualifies")),
        "saisons_ordre_teste": sum(1 for x in lignes
                                   if x["orientation"].get("rangs_confirmes") is not None),
        "rangs_confirmes": sum(x["orientation"].get("rangs_confirmes") or 0 for x in lignes),
        "rangs_dementis": sum(x["orientation"].get("rangs_dementis") or 0 for x in lignes),
        "ordre_atteste": sum(1 for x in lignes if x["orientation"].get("ordre_atteste")),
        "ordre_croisable": sum(1 for x in lignes
                               if x["orientation"].get("ordre_croise") is not None),
        "ordre_concordant": sum(1 for x in lignes
                                if x["orientation"].get("ordre_croise") is True),
        "saisons_sans_poteaux": sorted(x["saison"] for x in lignes
                                       if not x["poteaux"].get("vainqueur")),
    }


def main():
    saisons = yaml.safe_load(open(os.path.join(RACINE, "_data", "saisons.yml")))
    parts = yaml.safe_load(open(os.path.join(RACINE, "_data", "participations.yml")))
    rapport = []
    lignes = construire(saisons, parts, rapport)
    couv = couverture(lignes)

    print(f"saisons au format 3 aux poteaux : {couv['saisons_au_format']}")
    print(f"vainqueur des poteaux connu     : {couv['vainqueur_des_poteaux_connu']} "
          f"({couv['part_poteaux']} %)")
    print(f"choix du finaliste atteste      : {couv['choix_atteste']}")
    print(f"qualifies a l'orientation connus: {couv['qualifies_connus']}")
    print(f"ordre d'arrivee teste           : {couv['saisons_ordre_teste']} saisons, "
          f"{couv['rangs_confirmes']} rangs confirmes, {couv['rangs_dementis']} dementis")
    print(f"ordre lisible dans les 2 sources: {couv['ordre_croisable']}, "
          f"dont {couv['ordre_concordant']} concordants")
    if couv["saisons_sans_poteaux"]:
        print(f"sans vainqueur de poteaux       : {' '.join(couv['saisons_sans_poteaux'])}")
    if rapport:
        print(f"\nremarques ({len(rapport)}) :")
        for r in rapport[:20]:
            print("  " + r)

    if "--ecrire" in sys.argv:
        chemin = os.path.join(RACINE, "_data", "finale.yml")
        with open(chemin, "w", encoding="utf-8") as f:
            f.write(ENTETE)
            yaml.safe_dump({"couverture": couv, "lignes": lignes}, f,
                           allow_unicode=True, sort_keys=False, width=100)
        print(f"\necrit : {chemin}")


if __name__ == "__main__":
    main()
