#!/usr/bin/env python3
"""Fabrique une page par aventurier et une page par saison.

POURQUOI CE SCRIPT EXISTE. Le site est une suite d'essais ; ses 531 personnes
et ses 34 saisons n'y existaient que comme LIGNES de deux grands tableaux.
Aucun nom n'etait cliquable nulle part. Chercher « Teheiura » demandait de
trier une table de 531 lignes -- et repondre a « il est ou au classement ? »
demandait de le faire a la main, une personne a la fois.

COMMENT, EN SAFE MODE. Jekyll ne peut pas engendrer des pages depuis `_data/` :
le greffon qui le ferait n'est pas dans la liste blanche de GitHub Pages, et
`_plugins/` est ignore sans le moindre avertissement. La seule voie propre est
donc celle-ci : Python ecrit des pages COMMITEES, minuscules, qui ne portent
qu'un identifiant, et un gabarit les remplit depuis `_data/fiches.yml`.

    tools/atelier python3 tools/build_fiches.py

Le gabarit lit `site.data.fiches.aventuriers[page.aventurier]` : un acces par
cle, en temps constant. La tentation etait de faire chercher au gabarit sa
propre ligne dans une liste de 531 -- 531 pages parcourant 531 entrees font
282 000 iterations Liquid a chaque construction, pour un resultat identique.

Les fichiers produits sont regeneres a l'identique a chaque execution : ils
sont commites parce que GitHub Pages n'a pas le droit de les fabriquer, pas
parce qu'ils seraient tenus a la main.
"""
import argparse
import collections
import json
import os
import sys

import yaml

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
sys.path.insert(0, os.path.join(ICI, "extraction"))
RACINE = os.path.dirname(ICI)
DATA = os.path.join(RACINE, "_data")

import indicateurs                                            # noqa: E402
from build_stats import LIBELLE_SORT, arrondi                 # noqa: E402

DOSSIER_AVENTURIERS = os.path.join(RACINE, "aventuriers")
DOSSIER_SAISONS = os.path.join(RACINE, "saisons")
SORTIE_DATA = os.path.join(DATA, "fiches.yml")

ENTETE = ("# ATTENTION : fichier genere par tools/build_fiches.py.\n"
          "# Ne pas editer a la main : toute modification sera ecrasee.\n"
          "#\n"
          "# Une entree par aventurier et une par saison, indexees par leur\n"
          "# identifiant. Les gabarits `fiche-aventurier` et `fiche-saison` y\n"
          "# accedent par cle -- jamais en parcourant la liste entiere.\n"
          "#\n"
          "#     tools/atelier python3 tools/build_fiches.py\n"
          "#\n")


def charger(nom):
    with open(os.path.join(DATA, nom + ".yml"), encoding="utf-8") as f:
        return yaml.safe_load(f)


def liste(d, cle):
    """Un fichier de donnees est tantot une liste, tantot un dict qui en porte une."""
    return d[cle] if isinstance(d, dict) else d


def fiches_des_aventuriers(parts, personnes, saisons, indiv, classement, natures, colliers):
    par_saison = {s["id"]: s for s in saisons}
    par_pid = collections.defaultdict(list)
    for p in parts:
        par_pid[p["id"]].append(p)

    ind = {(x["saison"], x["id"]): x for x in indiv}
    rang = {x["id"]: x for x in classement.get("tous") or []}
    perso = {p["id"]: p for p in personnes}

    # Un collier peut passer de main en main : `detenteurs` porte celles qui
    # l'ont eu, chacune avec son identifiant quand il a pu etre resolu.
    cols = collections.Counter()
    joues = collections.Counter()
    for c in colliers:
        vus = set()
        for d in (c.get("detenteurs") or []) + (c.get("detenteurs_suivants") or []):
            if d.get("resolu") and d.get("id"):
                vus.add(d["id"])
        for pid in vus:
            cols[(c.get("saison"), pid)] += 1
            if c.get("statut") == "utilise":
                joues[(c.get("saison"), pid)] += 1

    nat = {(x["saison"], x["id"]): x for x in natures}

    out = {}
    for pid, lot in par_pid.items():
        lot = sorted(lot, key=lambda p: (par_saison.get(p["saison"], {}).get("annee") or 0,
                                         p["saison"]))
        base = lot[-1]
        r = rang.get(pid) or {}
        participations = []
        for p in lot:
            s = par_saison.get(p["saison"], {})
            i = ind.get((p["saison"], pid)) or {}
            n = nat.get((p["saison"], pid)) or {}
            participations.append({
                "saison": p["saison"],
                "titre": s.get("titre"),
                "annee": s.get("annee"),
                "numero": s.get("numero"),
                "speciale": bool(s.get("speciale")),
                "en_cours": bool(s.get("en_cours")),
                "lieu": s.get("lieu"),
                "effectif": sum(1 for x in parts if x["saison"] == p["saison"]),
                "age": p.get("age"),
                "profession": p.get("profession"),
                "localisation": p.get("localisation"),
                "tribu": p.get("tribu"),
                "couleur": p.get("couleur"),
                "sort": p.get("sort"),
                "libelle_sort": LIBELLE_SORT.get(p.get("sort"), p.get("motif")),
                "jour_sortie": p.get("jour_sortie"),
                "classement": p.get("classement"),
                "voix_recues": p.get("votes_recus"),
                "conseils_assistes": i.get("conseils_assistes"),
                "menace": i.get("menace"),
                # Les COMPTEURS valent 0, jamais nil : le gabarit doit pouvoir
                # ecrire `{% if x > 0 %}` sans risquer une comparaison avec
                # nil, que Liquid ne sait pas faire. Les MESURES, elles,
                # restent nil quand elles n'existent pas -- « 0 % de justesse »
                # et « justesse inconnue » ne sont pas la meme phrase.
                "bulletins_emis": i.get("bulletins_emis") or 0,
                "justesse_vote": i.get("justesse_vote"),
                "conseils_vise": i.get("conseils_vise") or 0,
                "evasion": i.get("evasion"),
                "epreuves_gagnees": i.get("epreuves_gagnees") or 0,
                "epreuves_disputees": i.get("epreuves_disputees") or 0,
                "ratio_epreuves": i.get("ratio_epreuves"),
                "colliers": cols.get((p["saison"], pid)) or 0,
                "colliers_joues": joues.get((p["saison"], pid)) or 0,
                "epreuves_nommees": n.get("epreuves") or [],
                "natures": [{"nature": k, "effectif": v}
                            for k, v in sorted((n.get("natures") or {}).items(),
                                               key=lambda x: (-x[1], x[0]))],
            })

        titres = sum(1 for p in lot if p.get("sort") == "vainqueur")
        finales = sum(1 for p in lot if p.get("sort") in ("vainqueur", "finaliste"))
        voix = [p.get("votes_recus") for p in lot if p.get("votes_recus") is not None]
        jours = [p.get("jour_sortie") for p in lot if p.get("jour_sortie")]
        out[pid] = {
            "id": pid,
            "nom": base.get("nom_complet") or base.get("nom"),
            "prenom": base.get("nom"),
            "genre": base.get("genre"),
            "profession": base.get("profession"),
            "localisation": base.get("localisation"),
            "naissance": (perso.get(pid) or {}).get("naissance"),
            "participations": participations,
            "nb_participations": len(lot),
            "titres": titres,
            "finales": finales,
            "voix_recues": sum(voix) if voix else None,
            "jours_total": sum(jours) if jours else None,
            "jour_max": max(jours) if jours else None,
            # Le rang n'existe que pour les saisons achevees : une saison en
            # cours n'a pas de sort, donc pas de parcours mesurable.
            "rang": r.get("rang"),
            "score": r.get("score"),
            "part_top": r.get("part_top"),
            "rang_p05": r.get("rang_p05"),
            "rang_p95": r.get("rang_p95"),
            "rangs": r.get("rangs") or {},
        }
    return out


def fiches_des_saisons(parts, saisons, conseils, epreuves, audiences, classement, resume):
    par_pid_rang = {x["id"]: x for x in classement.get("tous") or []}
    aud = {a["saison"]: a for a in (audiences.get("saisons") or [])}
    res = {x["id"]: x for x in resume}
    par_saison = collections.defaultdict(list)
    for p in parts:
        par_saison[p["saison"]].append(p)

    cons = collections.defaultdict(list)
    for c in conseils:
        cons[c.get("saison")].append(c)
    epr = collections.defaultdict(list)
    for e in epreuves:
        epr[e.get("saison")].append(e)

    ordre = {"vainqueur": 0, "finaliste": 1}
    out = {}
    for s in saisons:
        sid = s["id"]
        # Deux saisons ont ete ANNULEES avant tournage : elles n'ont ni titre,
        # ni casting, ni un seul conseil. Leur donner une page servirait une
        # fiche vide sous une URL qui semble promettre autre chose ; elles
        # restent listees sur /saisons/, ou leur ligne dit ce qu'elles sont.
        if s.get("annulee"):
            continue
        lot = par_saison.get(sid) or []
        casting = []
        for p in sorted(lot, key=lambda p: (ordre.get(p.get("sort"), 2),
                                            -(p.get("jour_sortie") or 0),
                                            p.get("nom") or "")):
            r = par_pid_rang.get(p["id"]) or {}
            casting.append({
                "id": p["id"],
                "nom": p.get("nom_complet") or p.get("nom"),
                "age": p.get("age"),
                "genre": p.get("genre"),
                "profession": p.get("profession"),
                "tribu": p.get("tribu"),
                "couleur": p.get("couleur"),
                "sort": p.get("sort"),
                "libelle_sort": LIBELLE_SORT.get(p.get("sort"), p.get("motif")),
                "jour_sortie": p.get("jour_sortie"),
                "classement": p.get("classement"),
                "voix_recues": p.get("votes_recus"),
                "rang": r.get("rang"),
            })
        el = [c for c in cons.get(sid) or [] if c.get("type") == "elimination"]
        a = aud.get(sid) or {}
        r = res.get(sid) or {}
        out[sid] = {
            "id": sid,
            "numero": s.get("numero"),
            "titre": s.get("titre"),
            "annee": s.get("annee"),
            "lieu": s.get("lieu"),
            "pays": s.get("pays"),
            "speciale": bool(s.get("speciale")),
            "en_cours": bool(s.get("en_cours")),
            "duree_jours": s.get("duree_jours"),
            "effectif": len(lot),
            "tribus": s.get("tribus") or [],
            "vainqueurs": [c for c in casting if c["sort"] == "vainqueur"],
            "finalistes": [c for c in casting if c["sort"] == "finaliste"],
            "casting": casting,
            "conseils": len(el),
            "conseils_complets": sum(1 for c in el if c.get("complet")),
            "bulletins": sum(len(c.get("votes") or []) for c in el),
            "epreuves": len(epr.get(sid) or []),
            "epreuves_individuelles": sum(1 for e in epr.get(sid) or []
                                          if e.get("forme") == "individuelle"),
            "age_moyen": r.get("age_moyen"),
            "survie_moyenne": r.get("survie_moyenne"),
            "abandons": r.get("abandons"),
            "audience_lancement": a.get("lancement"),
            "audience_finale": a.get("finale"),
            "audience_moyenne": a.get("moyenne"),
            "audience_pdm": a.get("moyenne_pdm"),
        }
    return out


GABARIT = """---
layout: {layout}
title: {titre}
permalink: {permalink}
{cle}: {valeur}
---
"""


def ecrire_pages(dossier, layout, cle, entrees, titre_de, permalink_de, rapport):
    """Ecrit une page par entree, et RETIRE celles qui n'ont plus de donnee.

    Sans le retrait, une personne disparue des donnees laisserait derriere elle
    une page orpheline, servie indefiniment et alimentee par un `nil` : le
    gabarit n'echouerait pas, il afficherait une fiche vide.
    """
    os.makedirs(dossier, exist_ok=True)
    voulus = set()
    for cid, e in sorted(entrees.items()):
        nom = cid + ".md"
        voulus.add(nom)
        # json.dumps et non yaml.safe_dump : ce dernier termine un scalaire
        # seul par une ligne « ... », le marqueur de fin de document YAML. Pose
        # au milieu d'un front matter, il coupe la page en deux et Jekyll ne
        # voit plus ni le permalien ni l'identifiant. Une chaine JSON est un
        # scalaire YAML double-quote valide, et rien d'autre.
        contenu = GABARIT.format(layout=layout,
                                 titre=json.dumps(titre_de(e), ensure_ascii=False),
                                 permalink=permalink_de(cid), cle=cle, valeur=cid)
        chemin = os.path.join(dossier, nom)
        ancien = None
        if os.path.exists(chemin):
            with open(chemin, encoding="utf-8") as f:
                ancien = f.read()
        if ancien != contenu:
            with open(chemin, "w", encoding="utf-8") as f:
                f.write(contenu)
            rapport["ecrites"] += 1
    for nom in sorted(os.listdir(dossier)):
        if nom.endswith(".md") and nom not in voulus:
            os.remove(os.path.join(dossier, nom))
            rapport["retirees"] += 1
    return len(voulus)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ecrire", action="store_true",
                    help="ecrit _data/fiches.yml et les pages (defaut : essai a blanc)")
    a = ap.parse_args()

    saisons = liste(charger("saisons"), "saisons")
    parts = charger("participations")
    personnes = liste(charger("personnes"), "personnes")
    conseils = charger("conseils")
    epreuves = charger("epreuves")
    colliers = charger("colliers")
    audiences = charger("audiences")
    stats = charger("stats")
    nommees = charger("epreuves_nommees")

    indiv = indicateurs.indicateurs_individuels(saisons, parts, conseils, epreuves)
    resume = indicateurs.indicateurs_saison(saisons, parts, conseils, epreuves, colliers)

    av = fiches_des_aventuriers(parts, personnes, saisons, indiv,
                                stats.get("classement") or {},
                                nommees.get("palmares") or [], colliers)
    sa = fiches_des_saisons(parts, saisons, conseils, epreuves, audiences,
                            stats.get("classement") or {}, resume)

    print(f"aventuriers : {len(av)}   saisons : {len(sa)}")
    classes = sum(1 for x in av.values() if x.get("rang"))
    print(f"  dont {classes} avec un rang au classement "
          f"({len(av) - classes} sans : saison en cours ou parcours non mesurable)")

    if not a.ecrire:
        print("essai a blanc : rien n'est ecrit (--ecrire pour ecrire)")
        return 0

    with open(SORTIE_DATA, "w", encoding="utf-8") as f:
        f.write(ENTETE)
        yaml.safe_dump({"aventuriers": av, "saisons": sa}, f,
                       allow_unicode=True, sort_keys=True, default_flow_style=False)
    print(f"ecrit : {SORTIE_DATA}")

    rapport = collections.Counter()
    n1 = ecrire_pages(DOSSIER_AVENTURIERS, "fiche-aventurier", "aventurier", av,
                      lambda e: e["nom"], lambda cid: f"/aventuriers/{cid}/", rapport)
    n2 = ecrire_pages(DOSSIER_SAISONS, "fiche-saison", "saison", sa,
                      lambda e: e["titre"], lambda cid: f"/saisons/{cid}/", rapport)
    print(f"pages : {n1} aventuriers + {n2} saisons = {n1 + n2} "
          f"({rapport['ecrites']} ecrites, {rapport['retirees']} retirees)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
