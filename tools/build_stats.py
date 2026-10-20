#!/usr/bin/env python3
"""Calcule les agregats et ecrit _data/stats.yml.

Pourquoi precalculer ? Le constructeur de GitHub Pages est un Jekyll 3.10, dont
le langage de gabarit n'a meme pas de filtre `sum` : croiser 645 participations
avec 3 400 bulletins a la construction du site est hors de portee. Les calculs
sont donc faits ici, une fois, et le resultat est commite. Le site ne fait plus
qu'afficher.

Deux perimetres coexistent partout :
  * `classiques` -- les saisons regulieres achevees, perimetre par defaut ;
  * `toutes`     -- avec les editions speciales, ou les revenants faussent les
                    moyennes d'age et de longevite.

    tools/atelier python3 tools/build_stats.py
"""
import math
import os
import json
import sys
from collections import Counter, defaultdict
from statistics import NormalDist, mean, median

import donnees

RACINE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(RACINE, "tools", "extraction"))
from csp import classer, libelles           # noqa: E402
import analyses
import articles                             # noqa: E402
import modeles                              # noqa: E402
import classement                           # noqa: E402
import prevision                           # noqa: E402
sys.path.insert(0, os.path.join(RACINE, "tools"))
from indicateurs import (eliminations, votes_du_jury,  # noqa: E402
                         indicateurs_individuels, indicateurs_saison,  # noqa: E402
                         fantomes, SEUIL_CONSEILS, SEUIL_EPREUVES, SEUIL_FANTOME)

ENTETE = """# ATTENTION : fichier genere. Ne pas editer a la main.
#
# Produit par tools/build_stats.py a partir de _data/saisons.yml,
# participations.yml, personnes.yml et conseils.yml.
#
#     tools/atelier python3 tools/build_stats.py
#
# Sauf mention contraire, les chiffres portent sur les SAISONS CLASSIQUES
# achevees. Les blocs `toutes` ajoutent les editions speciales.
#
"""

TRANCHES = [(18, 24), (25, 29), (30, 34), (35, 39), (40, 44), (45, 100)]
LIBELLE_TRANCHE = {(18, 24): "18-24 ans", (25, 29): "25-29 ans", (30, 34): "30-34 ans",
                   (35, 39): "35-39 ans", (40, 44): "40-44 ans", (45, 100): "45 ans et plus"}

LIBELLE_SORT = {
    "vainqueur": "Vainqueur", "finaliste": "Finaliste",
    "elimine_conseil": "Éliminé au conseil",
    "elimine_poteaux": "Éliminé aux poteaux",
    "elimine_orientation": "Éliminé à l'orientation",
    "elimine_ambassadeurs": "Éliminé aux ambassadeurs",
    "elimine_duel": "Éliminé en duel", "elimine_exil": "Éliminé sur l'île",
    "abandon_medical": "Abandon médical", "abandon_volontaire": "Abandon volontaire",
    "disqualifie": "Disqualifié",
}


def arrondi(x, n=1):
    return None if x is None else round(float(x), n)


def part(compte, total, n=1):
    return None if not total else round(100.0 * compte / total, n)


def tranche(age):
    for bornes in TRANCHES:
        if bornes[0] <= age <= bornes[1]:
            return LIBELLE_TRANCHE[bornes]
    return None


# --- chargement ------------------------------------------------------------

def charger():
    def lire(nom):
        chemin = os.path.join(RACINE, "_data", nom)
        return donnees.charger(open(chemin, encoding="utf-8")) if os.path.exists(chemin) else []

    saisons = lire("saisons.yml")
    parts = lire("participations.yml")
    personnes = lire("personnes.yml")
    conseils = lire("conseils.yml")
    epreuves = lire("epreuves.yml")
    colliers = lire("colliers.yml")
    finale = lire("finale.yml") or {}

    par_saison = {s["id"]: s for s in saisons}
    for p in parts:
        s = par_saison.get(p["saison"], {})
        p["_saison"] = s
        p["_speciale"] = bool(s.get("speciale"))
        p["_annee"] = s.get("annee")
        p["_duree"] = s.get("duree_jours")
        p["_csp"] = classer(p.get("profession"))
        d = p.get("jour_sortie")
        p["_survie"] = round(100.0 * d / s["duree_jours"], 1) if d and s.get("duree_jours") else None
    return saisons, parts, personnes, conseils, epreuves, colliers, finale, par_saison


def perimetre(parts, avec_speciales):
    out = []
    for p in parts:
        s = p["_saison"]
        if s.get("annulee") or s.get("en_cours"):
            continue
        if not avec_speciales and p["_speciale"]:
            continue
        out.append(p)
    return out


# --- blocs de calcul -------------------------------------------------------

def bloc_vainqueurs(parts):
    v = [p for p in parts if p.get("sort") == "vainqueur"]
    ages = [p["age"] for p in v if p.get("age")]
    if not ages:
        return {}
    return {
        "effectif": len(v),
        "age_moyen": arrondi(mean(ages)),
        "age_median": arrondi(median(ages)),
        "age_min": min(ages),
        "age_max": max(ages),
        "part_40_et_plus": part(sum(1 for a in ages if a >= 40), len(ages)),
        "par_tranche": [
            {"tranche": LIBELLE_TRANCHE[b],
             "effectif": sum(1 for a in ages if b[0] <= a <= b[1]),
             "part": part(sum(1 for a in ages if b[0] <= a <= b[1]), len(ages))}
            for b in TRANCHES],
        "par_genre": [
            {"genre": g, "libelle": "Femmes" if g == "f" else "Hommes",
             "effectif": sum(1 for p in v if p.get("genre") == g),
             "part": part(sum(1 for p in v if p.get("genre") == g), len(v))}
            for g in ("f", "h")],
        "par_couleur": [
            {"couleur": c, "effectif": n, "part": part(n, len(v))}
            for c, n in Counter(p.get("couleur") for p in v if p.get("couleur")).most_common()],
        "par_metier": [
            {"code": c, "libelle": libelles().get(c, c), "effectif": n,
             "part": part(n, len(v))}
            for c, n in Counter(p["_csp"] for p in v if p["_csp"]).most_common()],
    }


def bloc_couleurs(parts):
    out = []
    for couleur in sorted({p.get("couleur") for p in parts if p.get("couleur")}):
        lot = [p for p in parts if p.get("couleur") == couleur]
        survies = [p["_survie"] for p in lot if p["_survie"] is not None]
        finales = sum(1 for p in lot if p.get("sort") in ("vainqueur", "finaliste"))
        out.append({
            "couleur": couleur,
            "effectif": len(lot),
            "survie_moyenne": arrondi(mean(survies)) if survies else None,
            "victoires": sum(1 for p in lot if p.get("sort") == "vainqueur"),
            "finales": finales,
            "taux_finale": part(finales, len(lot)),
        })
    return sorted(out, key=lambda x: (-x["effectif"], x["couleur"]))


def bloc_metiers(parts):
    lib = libelles()
    out = []
    # `sorted` autour de l'ensemble : l'ordre d'iteration d'un set de chaines
    # change d'un processus a l'autre (l'empreinte des chaines est tiree au
    # hasard au demarrage). Sans lui, deux constructions du meme jeu de
    # donnees ne donnaient pas le meme fichier -- et le site changeait tout
    # seul entre deux publications.
    for code in sorted({p["_csp"] for p in parts if p["_csp"]}):
        lot = [p for p in parts if p["_csp"] == code]
        finales = sum(1 for p in lot if p.get("sort") in ("vainqueur", "finaliste"))
        survies = [p["_survie"] for p in lot if p["_survie"] is not None]
        ages = [p["age"] for p in lot if p.get("age")]
        out.append({
            "code": code,
            "libelle": lib.get(code, code),
            "effectif": len(lot),
            "part_du_casting": part(len(lot), len(parts)),
            "victoires": sum(1 for p in lot if p.get("sort") == "vainqueur"),
            "finales": finales,
            "taux_finale": part(finales, len(lot)),
            "survie_moyenne": arrondi(mean(survies)) if survies else None,
            "age_moyen": arrondi(mean(ages)) if ages else None,
        })
    return sorted(out, key=lambda x: (-x["effectif"], x["libelle"]))


def bloc_genre(parts):
    resume = []
    for g, lib in (("f", "Femmes"), ("h", "Hommes")):
        lot = [p for p in parts if p.get("genre") == g]
        survies = [p["_survie"] for p in lot if p["_survie"] is not None]
        jours = [p["jour_sortie"] for p in lot if p.get("jour_sortie")]
        ages = [p["age"] for p in lot if p.get("age")]
        finales = sum(1 for p in lot if p.get("sort") in ("vainqueur", "finaliste"))
        resume.append({
            "genre": g, "libelle": lib, "effectif": len(lot),
            "part_du_casting": part(len(lot), len(parts)),
            "survie_moyenne": arrondi(mean(survies)) if survies else None,
            "jour_moyen": arrondi(mean(jours)) if jours else None,
            "age_moyen": arrondi(mean(ages)) if ages else None,
            "victoires": sum(1 for p in lot if p.get("sort") == "vainqueur"),
            "finales": finales,
            "taux_finale": part(finales, len(lot)),
        })

    decennies = []
    for debut in (2000, 2010, 2020):
        lot = [p for p in parts if p["_annee"] and debut <= p["_annee"] < debut + 10]
        if not lot:
            continue
        ligne = {"decennie": f"{debut}s", "effectif": len(lot)}
        for g, lib in (("f", "femmes"), ("h", "hommes")):
            sous = [p["_survie"] for p in lot if p.get("genre") == g and p["_survie"] is not None]
            ligne[f"survie_{lib}"] = arrondi(mean(sous)) if sous else None
            ligne[f"effectif_{lib}"] = sum(1 for p in lot if p.get("genre") == g)
        decennies.append(ligne)
    return {"resume": resume, "par_decennie": decennies}


def bloc_sorties(parts):
    total = len(parts)
    repartition = [
        {"sort": s, "libelle": LIBELLE_SORT.get(s, s), "effectif": n, "part": part(n, total)}
        for s, n in Counter(p.get("sort") for p in parts if p.get("sort")).most_common()]

    evolution = []
    for debut in (2000, 2010, 2020):
        lot = [p for p in parts if p["_annee"] and debut <= p["_annee"] < debut + 10]
        if not lot:
            continue
        c = Counter(p.get("sort") for p in lot if p.get("sort"))
        evolution.append({
            "decennie": f"{debut}s", "effectif": len(lot),
            "abandons": part(c["abandon_medical"] + c["abandon_volontaire"], len(lot)),
            "conseil": part(c["elimine_conseil"], len(lot)),
            "ambassadeurs": part(c["elimine_ambassadeurs"], len(lot)),
        })
    return {"repartition": repartition, "par_decennie": evolution}


def bloc_age(parts):
    out = []
    for bornes in TRANCHES:
        lot = [p for p in parts if p.get("age") and bornes[0] <= p["age"] <= bornes[1]]
        if not lot:
            continue
        survies = [p["_survie"] for p in lot if p["_survie"] is not None]
        finales = sum(1 for p in lot if p.get("sort") in ("vainqueur", "finaliste"))
        out.append({
            "tranche": LIBELLE_TRANCHE[bornes],
            "effectif": len(lot),
            "part_du_casting": part(len(lot), len(parts)),
            "survie_moyenne": arrondi(mean(survies)) if survies else None,
            "victoires": sum(1 for p in lot if p.get("sort") == "vainqueur"),
            "finales": finales,
            "taux_finale": part(finales, len(lot)),
        })
    return out


def bloc_saisons(saisons, parts):
    par_saison = defaultdict(list)
    for p in parts:
        par_saison[p["saison"]].append(p)
    out = []
    for s in saisons:
        if s.get("annulee"):
            continue
        lot = par_saison.get(s["id"], [])
        ages = [p["age"] for p in lot if p.get("age")]
        femmes = sum(1 for p in lot if p.get("genre") == "f")
        out.append({
            "id": s["id"], "numero": s.get("numero"), "titre": s.get("titre"),
            "annee": s.get("annee"), "speciale": bool(s.get("speciale")),
            "en_cours": bool(s.get("en_cours")),
            "pays": s.get("pays"), "lieu": s.get("lieu"),
            "duree_jours": s.get("duree_jours"),
            "effectif": len(lot),
            "age_moyen": arrondi(mean(ages)) if ages else None,
            "age_min": min(ages) if ages else None,
            "age_max": max(ages) if ages else None,
            "part_femmes": part(femmes, len(lot)) if lot else None,
            "abandons": sum(1 for p in lot
                            if p.get("sort") in ("abandon_medical", "abandon_volontaire")),
            "vainqueurs": s.get("vainqueurs") or [],
        })
    return out


def bloc_records(parts, personnes):
    v = [p for p in parts if p.get("sort") == "vainqueur" and p.get("age")]
    multi = sorted([g for g in personnes if g.get("nb_participations", 0) > 1],
                   key=lambda g: -g["nb_participations"])
    return {
        "plus_jeune_vainqueur": min(v, key=lambda p: p["age"]) if v else None,
        "plus_age_vainqueur": max(v, key=lambda p: p["age"]) if v else None,
        "multi_participants": [
            {"nom": g["nom"], "participations": g["nb_participations"],
             "saisons": g["participations"]}
            for g in multi[:12]],
        "nb_multi_participants": len(multi),
    }


def bloc_conseils(conseils, parts, par_saison):
    # Le vote du jury final est mis de cote : on n'y elimine personne, on y
    # designe un vainqueur. Le melanger aux conseils fausserait le decompte
    # comme la part de conseils serres.
    utiles = [c for c in eliminations(conseils)
              if not par_saison.get(c["saison"], {}).get("en_cours")]
    complets = [c for c in utiles if c.get("complet")]
    avec_decompte = [c for c in utiles if c.get("votes_exprimes")]

    unanimes = [c for c in avec_decompte
                if c["votes_contre"] and c["votes_contre"] == c["votes_exprimes"]]
    serres = [c for c in avec_decompte
              if c["votes_contre"] and c["votes_exprimes"]
              and c["votes_contre"] <= c["votes_exprimes"] / 2 + 0.5]

    # Une voix barree a deux causes possibles, et les confondre attribue aux
    # colliers des annulations qui ne leur doivent rien. Voir la note de
    # `construire_conseils.py` : annulation partielle = un objet a protege
    # quelqu'un ; annulation totale = le tour entier est nul, egalite suivie
    # d'un second vote le plus souvent.
    objets = [c for c in utiles if c.get("annulation") == "partielle"]
    tours_nuls = [c for c in utiles if c.get("annulation") == "totale"]
    voix_objet = sum(c.get("voix_annulees") or 0 for c in objets)
    voix_tour_nul = sum(c.get("voix_annulees") or 0 for c in tours_nuls)

    # Un objet joue sauve-t-il ? On ne peut le dire que lorsqu'un seul
    # aventurier a vu ses voix annulees ; a plusieurs, on ne sait pas laquelle
    # des protections a compte.
    seul, sauves, rates = [], 0, 0
    for c in objets:
        p_ = c.get("proteges") or []
        if len(p_) != 1:
            continue
        seul.append(c)
        if c.get("elimine") == p_[0]:
            rates += 1
        else:
            sauves += 1

    genre = {}
    idx = {(p["saison"], p["id"]): p for p in parts}
    for c in complets:
        for b in c["votes"]:
            v = idx.get((c["saison"], b["votant"]))
            t = idx.get((c["saison"], b["cible"]))
            if v and t and v.get("genre") and t.get("genre"):
                genre[(v["genre"], t["genre"])] = genre.get((v["genre"], t["genre"]), 0) + 1
    total_g = sum(genre.values())

    return {
        "conseils": len(utiles),
        "conseils_avec_decompte": len(avec_decompte),
        "conseils_complets": len(complets),
        # /sources/ : pourquoi un conseil n'est pas complet. Sans decompte
        # annonce, la completude n'est pas verifiable ; avec, le tableau ne le
        # restitue pas -- le plus souvent a un bulletin manquant pres.
        "conseils_sans_decompte": len(utiles) - len(avec_decompte),
        "conseils_decompte_incomplet": sum(
            1 for c in avec_decompte if not c.get("complet")),
        "conseils_un_bulletin_manquant": sum(
            1 for c in avec_decompte if not c.get("complet")
            and c["votes_exprimes"] - len(c.get("votes") or []) == 1),
        "bulletins": sum(len(c["votes"]) for c in utiles),
        "bulletins_conseils_complets": sum(len(c["votes"]) for c in complets),
        # Le compte brut autant que la part : « 0,0 % » ne se lit pas, « aucun
        # conseil sur 404 » se lit.
        "par_periode": periodes_du_conseil(conseils, par_saison),
        "conseils_unanimes": len(unanimes),
        "part_unanimes": part(len(unanimes), len(avec_decompte)),
        "part_serres": part(len(serres), len(avec_decompte)),
        "voix_annulees_par_objet": voix_objet,
        "conseils_avec_objet_joue": len(objets),
        "saisons_avec_objet_joue": len({c["saison"] for c in objets}),
        "voix_annulees_tour_nul": voix_tour_nul,
        "conseils_tour_nul": len(tours_nuls),
        "saisons_tour_nul": len({c["saison"] for c in tours_nuls}),
        "objet_un_seul_protege": len(seul),
        "objet_a_sauve": sauves,
        "objet_n_a_pas_sauve": rates,
        "vote_par_genre": [
            {"votant": g1, "cible": g2, "effectif": n, "part": part(n, total_g)}
            for (g1, g2), n in sorted(genre.items(), key=lambda x: -x[1])],
    }


def bloc_jury(conseils, parts, par_saison):
    """Le vote du jury final, quand la source le donne.

    Le scrutin tient une ligne par finaliste. Cette table en montre une par
    LAUREAT : « qui a gagne, avec combien de voix ». La colonne du finaliste
    battu porte `finaliste` et non `laureat` ; elle compte dans les bulletins
    du modele, pas dans ce tableau, qui repondrait sinon deux fois a la meme
    question.
    """
    idx = {(p["saison"], p["id"]): p for p in parts}
    lignes = []
    for c in sorted((x for x in votes_du_jury(conseils) if x.get("laureat")),
                    key=lambda c: c["saison"]):
        sa = par_saison.get(c["saison"]) or {}
        p = idx.get((c["saison"], c["laureat"])) or {}
        # Un laureat non rattache n'a pas de nom sur lequel s'appuyer : la
        # source en donne un libelle mal decoupe (« Ugo Lartiche Ugo »), residu
        # d'une cellule qui porte a la fois une vignette et un prenom. On ne le
        # publie pas, et on ne le devine pas non plus : la ligne reste, sans
        # nom, et leur nombre est dit sous le tableau.
        lignes.append({
            "saison": c["saison"],
            "titre": sa.get("titre"),
            "annee": sa.get("annee"),
            "laureat": (p.get("nom_complet") or p.get("nom")
                        if c.get("laureat_rattache") else None),
            "voix_pour": c.get("votes_pour"),
            "voix_exprimees": c.get("votes_exprimes"),
            "bulletins_releves": len(c.get("votes") or []),
        })
    # Le decompte annonce par la matrice et le nombre de bulletins qu'on y lit
    # ne coincident pas toujours : sur quelques saisons, la ligne des totaux est
    # decalee d'une colonne et attribue au laureat le score de son finaliste.
    # Les bulletins, eux, portent chacun un nom : ce sont eux qui font foi. On
    # publie les deux plutot que de trancher en silence.
    desaccords = sum(1 for x in lignes
                     if x["voix_pour"] is not None
                     and x["voix_pour"] != x["bulletins_releves"])
    return {
        "effectif": len(lignes),
        "saisons": len({x["saison"] for x in lignes}),
        "sans_nom": sum(1 for x in lignes if not x["laureat"]),
        "desaccords": desaccords,
        "scrutins": lignes,
    }


def _liste_titres(saisons):
    """« Bocas del Toro, Palau et Johor » : les titres en italique, dans l'ordre
    de diffusion, joints a la francaise."""
    t = [f"<em>{s['titre']}</em>" for s in sorted(saisons, key=lambda s: (s.get("annee") or 0, s["id"]))]
    return t[0] if len(t) == 1 else (", ".join(t[:-1]) + " et " + t[-1] if t else "")


def bloc_epreuves(epreuves, conseils, parts, saisons, par_saison):
    """Victoires d'epreuves, et ratios individuels.

    Le denominateur d'un ratio n'est pas le nombre d'epreuves de la saison mais
    le nombre d'epreuves individuelles disputees TANT QUE la personne etait en
    jeu. Il se calcule a partir de l'episode ou elle sort, lu dans les conseils.
    Une personne dont l'episode de sortie reste inconnu garde ses victoires mais
    n'entre dans aucun ratio : mieux vaut un classement plus court qu'un ratio
    fabrique.
    """
    if not epreuves:
        return {}

    # episode de sortie, par (saison, personne)
    sortie = {}
    for c in conseils or []:
        if c.get("elimine_rattache") and c.get("episode"):
            try:
                sortie[(c["saison"], c["elimine"])] = int(c["episode"])
            except (TypeError, ValueError):
                pass
    dernier_episode = {}
    for e in epreuves:
        d = dernier_episode.get(e["saison"], 0)
        dernier_episode[e["saison"]] = max(d, e.get("episode") or 0)
    for p in parts:
        if p.get("sort") in ("vainqueur", "finaliste"):
            sortie.setdefault((p["saison"], p["id"]), dernier_episode.get(p["saison"], 0))

    # epreuves individuelles par saison, ordonnees
    individuelles = defaultdict(list)
    for e in epreuves:
        if e.get("forme") == "individuelle" and e.get("episode"):
            individuelles[e["saison"]].append(e)

    victoires = Counter()
    victoires_type = defaultdict(Counter)
    for e in epreuves:
        for v in e.get("vainqueurs") or []:
            if v.get("type") == "personne" and v.get("id"):
                cle = (e["saison"], v["id"])
                victoires[cle] += 1
                victoires_type[cle][e["type"]] += 1

    index = {(p["saison"], p["id"]): p for p in parts}
    lignes = []
    for (sid, pid), gagnees in victoires.items():
        p = index.get((sid, pid))
        if not p:
            continue
        ep_sortie = sortie.get((sid, pid))
        disputees = None
        if ep_sortie:
            disputees = sum(1 for e in individuelles.get(sid, [])
                            if e["episode"] <= ep_sortie)
        lignes.append({
            "personne": p.get("nom_complet") or p.get("nom"),
            "id": pid,
            "saison": sid,
            "titre": par_saison.get(sid, {}).get("titre"),
            "annee": par_saison.get(sid, {}).get("annee"),
            "speciale": bool(par_saison.get(sid, {}).get("speciale")),
            "gagnees": gagnees,
            "immunites": victoires_type[(sid, pid)].get("immunite", 0),
            "conforts": victoires_type[(sid, pid)].get("confort", 0),
            "disputees": disputees,
            "ratio": part(gagnees, disputees) if disputees else None,
            "sort": p.get("sort"),
            "genre": p.get("genre"),
            "age": p.get("age"),
            "csp": p["_csp"],
        })

    SEUIL = 8
    classement = sorted([x for x in lignes if x["disputees"] and x["disputees"] >= SEUIL],
                        key=lambda x: (-(x["ratio"] or 0), -x["gagnees"]))

    cumul = Counter()
    for x in lignes:
        cumul[(x["id"], x["personne"])] += x["gagnees"]

    # profil des vainqueurs d'epreuves individuelles
    par_csp, par_genre, par_age = Counter(), Counter(), Counter()
    effectif_csp, effectif_genre, effectif_age = Counter(), Counter(), Counter()
    for x in lignes:
        if x["speciale"]:
            continue
        if x["csp"]:
            par_csp[x["csp"]] += x["gagnees"]
        if x["genre"]:
            par_genre[x["genre"]] += x["gagnees"]
        if x["age"]:
            t = tranche(x["age"])
            if t:
                par_age[t] += x["gagnees"]
    for p in parts:
        if par_saison.get(p["saison"], {}).get("speciale"):
            continue
        if p["_csp"]:
            effectif_csp[p["_csp"]] += 1
        if p.get("genre"):
            effectif_genre[p["genre"]] += 1
        if p.get("age") and tranche(p["age"]):
            effectif_age[tranche(p["age"])] += 1

    lib = libelles()
    return {
        "epreuves": len(epreuves),
        "saisons_couvertes": len({e["saison"] for e in epreuves}),
        "saisons_sans_donnee": sorted({s["id"] for s in saisons
                                       if not s.get("annulee")}
                                      - {e["saison"] for e in epreuves}),
        # Les saisons relevees sur le seul guide d'episodes du wiki Survivor :
        # aucune autre page ne donne leurs epreuves (20 octobre 2026).
        "saisons_source_unique": sorted({e["saison"] for e in epreuves
                                         if e.get("source") == "survivor"}),
        "saisons_source_unique_texte": _liste_titres(
            [s for s in saisons
             if s["id"] in {e["saison"] for e in epreuves if e.get("source") == "survivor"}]),
        "collectives": sum(1 for e in epreuves if e.get("forme") == "collective"),
        "individuelles": sum(1 for e in epreuves if e.get("forme") == "individuelle"),
        "immunites": sum(1 for e in epreuves if e.get("type") == "immunite"),
        "conforts": sum(1 for e in epreuves if e.get("type") == "confort"),
        "seuil_classement": SEUIL,
        "classement_effectif": len(classement),
        "ratio_moyen": arrondi(mean([x["ratio"] for x in classement])) if classement else None,
        "classement_ratio": classement[:15],
        "meilleurs_cumuls": [{"personne": nom, "id": pid, "victoires": n}
                             for (pid, nom), n in cumul.most_common(15)],
        "par_metier": [
            {"code": c, "libelle": lib.get(c, c), "victoires": n,
             "aventuriers": effectif_csp[c],
             "victoires_par_aventurier": arrondi(n / effectif_csp[c], 2)
             if effectif_csp[c] else None}
            for c, n in par_csp.most_common()],
        "par_genre": [
            {"genre": g, "libelle": "Femmes" if g == "f" else "Hommes",
             "victoires": par_genre[g], "aventuriers": effectif_genre[g],
             "victoires_par_aventurier": arrondi(par_genre[g] / effectif_genre[g], 2)
             if effectif_genre[g] else None}
            for g in ("f", "h")],
        "par_age": [
            {"tranche": LIBELLE_TRANCHE[b], "victoires": par_age[LIBELLE_TRANCHE[b]],
             "aventuriers": effectif_age[LIBELLE_TRANCHE[b]],
             "victoires_par_aventurier": arrondi(
                 par_age[LIBELLE_TRANCHE[b]] / effectif_age[LIBELLE_TRANCHE[b]], 2)
             if effectif_age[LIBELLE_TRANCHE[b]] else None}
            for b in TRANCHES],
    }


LIBELLE_ISSUE = {
    "annulation_efficace": "Joué, et il annule des voix",
    "joue_pour_rien": "Joué pour rien",
    "elimine_avec_collier": "Éliminé avec le collier dans le sac",
    "garde_sans_usage": "Gardé sans en avoir besoin",
    "non_decouvert": "Jamais trouvé",
}


def bloc_colliers(colliers, par_saison, parts=None):
    """Le destin des colliers, et deux denominateurs qui changent tout.

    Rapporter les issues a TOUS les colliers ou seulement a ceux qui ont ete
    TROUVES ne raconte pas la meme chose : un collier que personne n'a
    decouvert n'est pas un echec de son detenteur, il n'en a pas eu. Les deux
    lectures sont donnees.
    """
    if not colliers:
        return {}
    total = len(colliers)
    trouves = [c for c in colliers if c.get("issue") != "non_decouvert"]
    compte = Counter(c.get("issue") for c in colliers)
    joues = [c for c in colliers if c.get("statut") == "utilise"
             and c.get("votes_annules") is not None]
    annulees = sum(c["votes_annules"] for c in joues)

    # Le palmares par personne, que la page n'avait pas. Trois comptes, et
    # c'est le troisieme qui vaut : trouver un collier n'est pas le jouer, et
    # le jouer n'est pas annuler des voix. Amri Madani est le seul a faire
    # trois sur trois.
    noms = {}
    for p in (parts or []):
        noms[p["id"]] = p.get("nom_complet") or p.get("nom")
    trouve_par, joue_par, efficace_par = Counter(), Counter(), Counter()
    perdus = []
    for c in colliers:
        for d in (c.get("detenteurs") or []):
            if not d.get("id"):
                continue
            trouve_par[d["id"]] += 1
            if c.get("statut") == "utilise":
                joue_par[d["id"]] += 1
            if c.get("issue") == "annulation_efficace":
                efficace_par[d["id"]] += 1
        if c.get("issue") == "elimine_avec_collier":
            for d in (c.get("detenteurs") or []):
                perdus.append({
                    "nom": noms.get(d.get("id"), d.get("libelle")),
                    "saison": c["saison"],
                    "titre": par_saison.get(c["saison"], {}).get("titre"),
                    "annee": par_saison.get(c["saison"], {}).get("annee")})
    palmares = sorted(
        ({"id": i, "nom": noms.get(i, i), "trouves": n,
          "joues": joue_par[i], "efficaces": efficace_par[i]}
         for i, n in trouve_par.items()),
        key=lambda x: (-x["efficaces"], -x["joues"], -x["trouves"], x["nom"]))

    return {
        "colliers": total,
        "trouves": len(trouves),
        "porteurs": len(trouve_par),
        "colliers_attribues": sum(trouve_par.values()),
        "palmares": palmares[:12],
        "elimines_avec_collier": perdus,
        "jamais_trouves": compte.get("non_decouvert", 0),
        "saisons_couvertes": len({c["saison"] for c in colliers}),
        "voix_annulees": annulees,
        "voix_par_collier_joue": arrondi(annulees / len(joues), 1) if joues else None,
        "issues": [
            {"issue": k, "libelle": LIBELLE_ISSUE.get(k, str(k)), "effectif": n,
             "part_totale": part(n, total),
             "part_des_trouves": part(n, len(trouves)) if k != "non_decouvert" else None}
            for k, n in compte.most_common() if k],
        "par_saison": [
            {"saison": sid, "titre": par_saison.get(sid, {}).get("titre"),
             "annee": par_saison.get(sid, {}).get("annee"),
             "colliers": sum(1 for c in colliers if c["saison"] == sid),
             "joues": sum(1 for c in colliers
                          if c["saison"] == sid and c.get("statut") == "utilise"),
             "voix_annulees": sum(c.get("votes_annules") or 0
                                  for c in colliers if c["saison"] == sid)}
            for sid in sorted({c["saison"] for c in colliers})],
    }


def voix_des_vainqueurs(lignes):
    """Combien de voix les vainqueurs ont-ils recues avant de gagner ?

    Le total de voix vient de `participations.yml:votes_recus`, releve pour la
    saison entiere par le tableau des candidats -- et non de la somme des
    conseils dont on a le depouillement complet, qui n'en couvre qu'une partie.
    C'est le choix deja fait par `indicateurs.py` pour l'indicateur `menace`.

    Le piege du sujet est le denominateur. Compare a TOUT le casting, un
    vainqueur parait invisible ; mais on ne gagne pas si on est sorti, et on
    sort quand on est ecrit : l'ecart est alors en grande partie mecanique. La
    comparaison qui apprend quelque chose est celle du FINALISTE, qui a
    traverse exactement les memes conseils. Les deux sont rendues ici, dans cet
    ordre, pour qu'on ne puisse pas lire la premiere sans la seconde.
    """
    v = [x for x in lignes if x["sort"] == "vainqueur" and x["voix_recues"] is not None]
    if not v:
        return {}
    voix = [x["voix_recues"] for x in v]
    sans = sum(1 for n in voix if n == 0)

    def groupe(libelle, lot):
        recues = [x["voix_recues"] for x in lot if x["voix_recues"] is not None]
        menaces = [x["menace"] for x in lot if x["menace"] is not None]
        if not recues:
            return None
        return {
            "libelle": libelle,
            "effectif": len(recues),
            "voix_moyennes": arrondi(mean(recues), 2),
            "voix_medianes": arrondi(median(recues), 1),
            # `menace` = voix recues par conseil traverse. Elle n'existe qu'au
            # dela de SEUIL_CONSEILS : son effectif est donc dit a part, sans
            # quoi on lirait une moyenne sur un denominateur invente.
            "menace_moyenne": arrondi(mean(menaces), 3) if menaces else None,
            "mesures": len(menaces),
        }

    par_sort = [g for g in (
        groupe("Vainqueurs", [x for x in lignes if x["sort"] == "vainqueur"]),
        groupe("Finalistes", [x for x in lignes if x["sort"] == "finaliste"]),
        groupe("Tout le casting", lignes),
    ) if g]

    # La comparaison appariee : un couple par (vainqueur, finaliste) d'une meme
    # saison. Les saisons a double victoire donnent donc deux couples, et celles
    # ou le finaliste manque n'en donnent aucun -- plutot que d'inventer un
    # adversaire.
    par_saison = defaultdict(lambda: {"v": [], "f": []})
    for x in lignes:
        if x["sort"] == "vainqueur":
            par_saison[x["saison"]]["v"].append(x)
        elif x["sort"] == "finaliste":
            par_saison[x["saison"]]["f"].append(x)
    couples = []
    for sid in sorted(par_saison):
        b = par_saison[sid]
        for a in b["v"]:
            for f in b["f"]:
                if a["voix_recues"] is None or f["voix_recues"] is None:
                    continue
                couples.append({
                    "saison": sid, "titre": a["titre"], "annee": a["annee"],
                    "vainqueur": a["nom"], "voix_vainqueur": a["voix_recues"],
                    "finaliste": f["nom"], "voix_finaliste": f["voix_recues"],
                    "conseils": a["conseils_assistes"],
                })
    couples.sort(key=lambda x: (x["annee"], x["saison"]))
    moins = sum(1 for x in couples if x["voix_vainqueur"] < x["voix_finaliste"])
    plus = sum(1 for x in couples if x["voix_vainqueur"] > x["voix_finaliste"])

    return {
        "effectif": len(v),
        "total": sum(voix),
        "moyenne": arrondi(mean(voix), 2),
        "mediane": arrondi(median(voix), 1),
        "maximum": max(voix),
        "sans_aucune_voix": sans,
        "part_sans_voix": part(sans, len(voix)),
        "jamais_ecrits": [{"nom": x["nom"], "titre": x["titre"], "annee": x["annee"]}
                          for x in sorted(v, key=lambda x: x["annee"])
                          if x["voix_recues"] == 0],
        "records": [{"nom": x["nom"], "titre": x["titre"], "annee": x["annee"],
                     "voix": x["voix_recues"]}
                    for x in sorted(v, key=lambda x: (-x["voix_recues"], x["annee"]))
                    if x["voix_recues"] == max(voix)],
        "distribution": [{"voix": n, "effectif": sum(1 for k in voix if k == n)}
                         for n in range(0, max(voix) + 1)],
        "par_sort": par_sort,
        "couples": couples,
        "couples_resume": {
            "effectif": len(couples),
            "vainqueur_moins_vise": moins,
            "egalite": len(couples) - moins - plus,
            "vainqueur_plus_vise": plus,
            "moyenne_vainqueur": arrondi(mean([x["voix_vainqueur"] for x in couples]), 2)
                                 if couples else None,
            "moyenne_finaliste": arrondi(mean([x["voix_finaliste"] for x in couples]), 2)
                                 if couples else None,
        },
    }


NATURES_LIBELLE = {
    "rapidite": "Rapidité", "precision": "Précision", "force": "Force",
    "statique": "Statique", "equilibre": "Équilibre", "reflexion": "Réflexion",
    "logique": "Logique", "aquatique": "Aquatique", "adresse": "Adresse",
    "memoire": "Mémoire", "endurance": "Endurance",
}
SEUIL_NATURE = 30      # sous ce nombre de victoires, une part ne veut rien dire


def periodes_du_conseil(conseils, par_saison):
    """Combien de voix il faut pour partir, epoque par epoque.

    Deux chiffres qui ne racontent pas la meme histoire. Le NOMBRE de voix qui
    sort quelqu'un monte avec les annees -- mais les conseils comptent plus de
    monde qu'avant, et il en faut donc mecaniquement davantage. La PART des
    votants qui ecrivent le meme nom, elle, est la mesure de l'accord : c'est
    elle qu'il faut regarder pour savoir si le camp se resserre ou se divise.
    """
    par = defaultdict(list)
    for c in eliminations(conseils):
        s = par_saison.get(c["saison"]) or {}
        annee, contre, exprimes = s.get("annee"), c.get("votes_contre"), c.get("votes_exprimes")
        if not (annee and contre and exprimes):
            continue
        par[(annee // 5) * 5].append((contre, exprimes))
    lignes = []
    for debut in sorted(par):
        lot = par[debut]
        lignes.append({
            "periode": f"{debut}-{debut + 4}",
            "debut": debut,
            "conseils": len(lot),
            "voix_moyennes": arrondi(mean(v for v, _ in lot)),
            "votants_moyens": arrondi(mean(e for _, e in lot)),
            "part_moyenne": arrondi(100.0 * mean(v / e for v, e in lot)),
        })
    return lignes


def duos_les_plus_alignes(conseils, parts, par_saison, mini=6, combien=12):
    """Les paires qui ont le plus souvent ecrit le meme nom, nommement.

    La page des alliances mesure la persistance en AGREGAT ; elle ne dit jamais
    qui. Deux personnes ne peuvent etre comparees que sur les conseils ou
    toutes deux ont vote et ou le depouillement est complet : c'est le
    denominateur, et il est rarement grand -- d'ou le seuil.
    """
    ensemble, accord = Counter(), Counter()
    for c in eliminations(conseils):
        if not c.get("complet"):
            continue
        bulletins = [b for b in c["votes"]
                     if b.get("votant_rattache") and b.get("cible_rattachee")]
        for i in range(len(bulletins)):
            for j in range(i + 1, len(bulletins)):
                a, b = bulletins[i], bulletins[j]
                cle = (c["saison"],) + tuple(sorted([a["votant"], b["votant"]]))
                ensemble[cle] += 1
                if a["cible"] == b["cible"]:
                    accord[cle] += 1
    noms = {(p["saison"], p["id"]): (p.get("nom_complet") or p.get("nom")) for p in parts}
    lot = [{
        "saison": cle[0],
        "titre": (par_saison.get(cle[0]) or {}).get("titre"),
        "annee": (par_saison.get(cle[0]) or {}).get("annee"),
        "un": noms.get((cle[0], cle[1]), cle[1]),
        "deux": noms.get((cle[0], cle[2]), cle[2]),
        "ensemble": n,
        "accord": accord[cle],
        "part": part(accord[cle], n),
    } for cle, n in ensemble.items() if n >= mini]
    lot.sort(key=lambda x: (-x["accord"], -x["part"], x["annee"] or 0))
    return {"seuil": mini, "paires": len(lot), "meilleures": lot[:combien]}


def bloc_natures(nommees, parts, par_saison):
    """La nature des epreuves gagnees, et ce qu'elle ne separe pas.

    Le site a longtemps ecrit que la nature d'une epreuve -- force, rapidite,
    equilibre -- n'etait exploitable nulle part. Elle l'est desormais : pas au
    niveau de l'EPISODE, ou le rapprochement reste indecidable neuf fois sur
    dix, mais au niveau de la PERSONNE, ou il aboutit presque toujours. La
    question devient donc posable, et c'est tout ce qu'on lui demandait.

    On compte des CITATIONS, pas des victoires distinctes : une epreuve porte
    souvent deux natures -- le parcours du combattant est force ET rapidite --
    et une meme victoire alimente alors deux compteurs. La reference est donc
    la part observee sur l'ensemble de ces citations, jamais le casting.
    """
    palmares = (nommees or {}).get("palmares") or []
    if not palmares:
        return {}
    fiches = {(p["saison"], p["id"]): p for p in parts}
    AU_BOUT = {"vainqueur", "finaliste", "elimine_poteaux"}

    par = defaultdict(lambda: {"n": 0, "femmes": 0, "au_bout": 0, "ages": []})
    for ligne in palmares:
        p = fiches.get((ligne["saison"], ligne["id"]))
        if not p:
            continue
        for nature, k in (ligne.get("natures") or {}).items():
            d = par[nature]
            d["n"] += k
            d["femmes"] += k if p.get("genre") == "f" else 0
            d["au_bout"] += k if p.get("sort") in AU_BOUT else 0
            if p.get("age"):
                d["ages"] += [p["age"]] * k

    total = sum(d["n"] for d in par.values())
    if not total:
        return {}
    ref_f = part(sum(d["femmes"] for d in par.values()), total)
    ref_b = part(sum(d["au_bout"] for d in par.values()), total)
    tous_ages = [a for d in par.values() for a in d["ages"]]

    def issue(succes, n, hasard):
        bas, haut = modeles._wilson(succes, n) if n else (None, None)
        return {"cas": succes, "probabilite": part(succes, n),
                "bas": arrondi(bas) if bas is not None else None,
                "haut": arrondi(haut) if haut is not None else None,
                "hasard": hasard}

    lignes = [{
        "nature": nature,
        "libelle": NATURES_LIBELLE.get(nature, nature.capitalize()),
        "effectif": d["n"],
        "assez": d["n"] >= SEUIL_NATURE,
        "femmes": issue(d["femmes"], d["n"], ref_f),
        "au_bout": issue(d["au_bout"], d["n"], ref_b),
        "age_moyen": arrondi(mean(d["ages"])) if d["ages"] else None,
    } for nature, d in sorted(par.items(), key=lambda x: -x[1]["n"])]

    couv = (nommees or {}).get("couverture_par_personne") or {}
    return {
        "citations": couv.get("citations"),
        "attribuees": couv.get("attribuees"),
        "part": couv.get("part"),
        "personnes": couv.get("personnes"),
        "victoires": total,
        "part_femmes": ref_f,
        "part_au_bout": ref_b,
        "age_moyen": arrondi(mean(tous_ages)) if tous_ages else None,
        "seuil": SEUIL_NATURE,
        "par_nature": lignes,
    }


def bloc_finale(finale, parts, par_saison):
    """La fin de saison : orientation, poteaux, choix du finaliste, victoire.

    Deux questions, et un seul modele nul pour la premiere : entre deux
    finalistes, c'est pile ou face. Pour la seconde, le hasard vaut un tiers --
    trois qualifies a l'orientation, un seul gagne.

    Aucune p-valeur n'est publiee ici. Les tests de ce site sont declares
    d'avance et corriges ensemble (`modeles.registre`) ; en ajouter un
    deplacerait les p ajustees de tous les autres. Une proportion, son
    intervalle de Wilson et la ligne du hasard disent la meme chose sans
    toucher a la correction.
    """
    if not finale:
        return {}
    lignes = finale.get("lignes") or []
    noms = {(p_["saison"], p_["id"]): (p_.get("nom_complet") or p_.get("nom"))
            for p_ in parts}

    def nom(sid, pid):
        return noms.get((sid, pid)) if pid else None

    avec = [x for x in lignes if x["poteaux"].get("vainqueur")]
    gagne = sum(1 for x in avec if x["poteaux"]["vainqueur"] == x["vainqueur"])
    atteste = [x for x in avec if x["poteaux"].get("choix_atteste")]
    gagne_atteste = sum(1 for x in atteste
                        if x["poteaux"]["vainqueur"] == x["vainqueur"])

    def issue(succes, total, hasard):
        bas, haut = modeles._wilson(succes, total) if total else (None, None)
        return {"effectif": total, "cas": succes, "probabilite": part(succes, total),
                "bas": arrondi(bas) if bas is not None else None,
                "haut": arrondi(haut) if haut is not None else None,
                "hasard": hasard}

    # Le rang d'arrivee a l'orientation.
    rangs = {}
    ordonnees = [x for x in lignes
                 if x["orientation"].get("qualifies") and x["poteaux"].get("vainqueur")]
    for x in ordonnees:
        for r, pid in enumerate(x["orientation"]["qualifies"], 1):
            d = rangs.setdefault(r, {"n": 0, "poteaux": 0, "victoire": 0, "elimine": 0})
            d["n"] += 1
            d["poteaux"] += pid == x["poteaux"]["vainqueur"]
            d["victoire"] += pid == x["vainqueur"]
            d["elimine"] += pid == x["poteaux"]["elimine"]

    LIBELLE_RANG = {1: "Premier arrivé", 2: "Deuxième", 3: "Dernier qualifié"}
    par_rang = [{
        "rang": r,
        "libelle": LIBELLE_RANG.get(r, f"Rang {r}"),
        "effectif": d["n"],
        "gagne_les_poteaux": issue(d["poteaux"], d["n"], arrondi(100.0 / 3)),
        "gagne_la_saison": issue(d["victoire"], d["n"], arrondi(100.0 / 3)),
        "elimine_aux_poteaux": issue(d["elimine"], d["n"], arrondi(100.0 / 3)),
    } for r, d in sorted(rangs.items())]

    return {
        "couverture": finale.get("couverture"),
        "poteaux": {
            "effectif": len(avec),
            "vainqueur_des_poteaux": issue(gagne, len(avec), 50.0),
            "autre_finaliste": issue(len(avec) - gagne, len(avec), 50.0),
            "choix_atteste": issue(gagne_atteste, len(atteste), 50.0),
        },
        "par_rang": par_rang,
        "saisons_ordonnees": len(ordonnees),
        "table": [{
            "saison": x["saison"], "titre": x["titre"], "annee": x["annee"],
            "speciale": x["speciale"],
            "qualifies": [nom(x["saison"], i)
                          for i in (x["orientation"].get("qualifies") or [])],
            "poteaux": nom(x["saison"], x["poteaux"].get("vainqueur")),
            "autre_finaliste": nom(x["saison"], x["poteaux"].get("autre_finaliste")),
            "elimine": nom(x["saison"], x["poteaux"].get("elimine")),
            "vainqueur": nom(x["saison"], x["vainqueur"]),
            "choix_atteste": bool(x["poteaux"].get("choix_atteste")),
            "poteaux_gagne": (x["poteaux"].get("vainqueur") == x["vainqueur"]
                              if x["poteaux"].get("vainqueur") else None),
        } for x in sorted(lignes, key=lambda x: (x["annee"], x["saison"]))],
    }


def bloc_indicateurs(saisons, parts, conseils, epreuves, colliers, par_saison):
    """Les indicateurs avances, individuels et par saison."""
    lignes = indicateurs_individuels(saisons, parts, conseils, epreuves)
    classiques = [x for x in lignes if not x["speciale"]]

    def classement(champ, sens=-1, seuil_champ=None, mini=None, n=12):
        lot = [x for x in lignes if x.get(champ) is not None]
        if seuil_champ and mini:
            lot = [x for x in lot if (x.get(seuil_champ) or 0) >= mini]
        lot.sort(key=lambda x: sens * x[champ])
        return [{"nom": x["nom"], "saison": x["saison"], "titre": x["titre"],
                 "annee": x["annee"], "speciale": x["speciale"], "valeur": x[champ],
                 "base": x.get(seuil_champ), "sort": x["sort"]} for x in lot[:n]]

    saisons_avancees = indicateurs_saison(saisons, parts, conseils, epreuves, colliers)
    invisibles = fantomes(lignes)
    # Le groupe de comparaison juste : ceux qui ont traverse autant de conseils
    # qu'un fantome, qu'ils aient ete vises ou non.
    endurants = [x for x in lignes if x["conseils_assistes"] >= SEUIL_FANTOME]

    def moyenne_par(champ, cle):
        groupes = defaultdict(list)
        for x in classiques:
            if x.get(champ) is not None and x.get(cle):
                groupes[x[cle]].append(x[champ])
        return {k: arrondi(mean(v)) for k, v in groupes.items() if len(v) >= 10}

    def rapport_des_moyennes(champ, cle, haut, bas):
        """Combien de fois la moyenne de `haut` vaut celle de `bas`, prise sur
        les moyennes NON arrondies : deux moyennes affichees a 0,9 et 0,2 ne
        disent pas leur rapport."""
        groupes = defaultdict(list)
        for x in classiques:
            if x.get(champ) is not None and x.get(cle) in (haut, bas):
                groupes[x[cle]].append(x[champ])
        if not groupes.get(haut) or not groupes.get(bas) or not mean(groupes[bas]):
            return None
        return arrondi(mean(groupes[haut]) / mean(groupes[bas]))

    return {
        "seuil_conseils": SEUIL_CONSEILS,
        "seuil_epreuves": SEUIL_EPREUVES,
        "mesurables": len([x for x in lignes if x["conseils_assistes"] >= SEUIL_CONSEILS]),
        "meilleure_justesse": classement("justesse_vote", -1, "bulletins_emis", 6),
        "plus_menaces": classement("menace", -1, "conseils_assistes", 6),
        "meilleure_evasion": classement("evasion", -1, "conseils_vise", 3),
        "fantomes": [{"nom": x["nom"], "saison": x["saison"], "titre": x["titre"],
                      "annee": x["annee"], "conseils": x["conseils_assistes"],
                      "sort": x["sort"], "survie": x["survie"]}
                     for x in invisibles[:12]],
        "nb_fantomes": len(invisibles),
        # Etre invisible une saison peut etre un accident de casting. L'etre
        # DEUX FOIS ressemble a une maniere de jouer. Ils sont cinq, et l'une
        # d'elles a gagne une des deux saisons ou personne ne l'a ecrite.
        "fantomes_recidivistes": [
            {"nom": nom, "fois": len(lot),
             "saisons": ", ".join(x["titre"] for x in lot),
             "sorts": ", ".join(LIBELLE_SORT.get(x["sort"], x["sort"]) for x in lot)}
            for nom, lot in sorted(
                ((n, [x for x in invisibles if x["id"] == i])
                 for i, n in sorted({x["id"]: x["nom"] for x in invisibles}.items())),
                key=lambda kv: (-len(kv[1]), kv[0]))
            if len(lot) > 1],
        # Douze fantomes ont GAGNE leur saison : c'est le contre-exemple le plus
        # net a l'idee qu'il faut se faire remarquer pour aller au bout.
        "fantomes_vainqueurs": [
            {"nom": x["nom"], "titre": x["titre"], "annee": x["annee"],
             "conseils": x["conseils_assistes"]}
            for x in invisibles if x["sort"] == "vainqueur"],
        # Ce que devient un aventurier que personne n'a jamais ecrit sur un
        # bulletin, compare a ce que devient un aventurier ordinaire. C'est la
        # comparaison des deux colonnes qui fait le resultat, pas la premiere
        # seule : sans reference, « 8 vainqueurs » ne veut rien dire.
        "fantomes_issue": [
            {"sort": k, "libelle": LIBELLE_SORT.get(k, k), "effectif": n,
             "part_fantomes": part(n, len(invisibles)),
             "part_ensemble": part(
                 sum(1 for x in lignes if x["sort"] == k), len(lignes)),
             # La bonne reference. Un fantome a par definition traverse au
             # moins SEUIL_FANTOME conseils sans etre ecrit : le comparer a
             # TOUS les aventuriers, celui sorti au premier conseil compris,
             # melange deux choses -- ne pas etre vise, et etre alle loin. La
             # comparaison juste se fait a ceux qui ont tenu aussi longtemps.
             "part_endurants": part(
                 sum(1 for x in endurants if x["sort"] == k), len(endurants))}
            for k, n in Counter(x["sort"] for x in invisibles).most_common()],
        "voix_des_vainqueurs": voix_des_vainqueurs(classiques),
        "duos": duos_les_plus_alignes(conseils, parts, par_saison),
        "comparables": len(lignes),
        "endurants": len(endurants),
        "seuil_fantome": SEUIL_FANTOME,
        "justesse_par_sort": moyenne_par("justesse_vote", "sort"),
        "menace_par_sort": moyenne_par("menace", "sort"),
        # /statistiques/jeu-social/ : « N fois moins » de voix pour un
        # vainqueur que pour un elimine au conseil.
        "menace_rapport": rapport_des_moyennes(
            "menace", "sort", "elimine_conseil", "vainqueur"),
        "saisons": saisons_avancees,
    }


# --- assemblage ------------------------------------------------------------

# Les champs dont on suit le remplissage. Ce n'est pas la liste de tous les
# champs : c'est celle de ceux qui peuvent manquer, et dont l'absence se voit
# quelque part sur le site.
CHAMPS_SUIVIS = [
    ("genre", "Sexe"), ("age", "Âge"), ("profession", "Métier"),
    ("localisation", "Département d'origine"), ("tribu", "Tribu de départ"),
    ("couleur", "Couleur de départ"), ("parcours", "Trajectoire de tribus"),
    ("jour_sortie", "Jour de sortie"), ("sort", "Manière de sortir"),
    ("votes_recus", "Voix reçues"), ("classement", "Rang final"),
    ("victoires_collectives", "Victoires collectives"),
    ("victoires_individuelles", "Victoires individuelles"),
]

# La provenance qui designe la troisieme source, arrivee en aout 2026.
PAGE_INDIVIDUELLE = "fandom (page individuelle)"


# Les colonnes de la grille de completude : une par type de donnee, dans
# l'ordre ou on les rencontre en construisant une saison -- d'abord qui joue,
# puis ce qu'on sait de chacun, puis ce qui se passe, puis ce que la chaine en
# fait. `nature` dit comment lire la case : une part de 0 a 100, ou un fait
# present ou absent.
COLONNES_COMPLETUDE = [
    ("casting", "Casting relevé", "Casting", "part"),
    ("age", "Âge", "Âge", "part"),
    ("profession", "Métier", "Métier", "part"),
    ("localisation", "Département d'origine", "Origine", "part"),
    ("couleur", "Bandeau de départ", "Bandeau", "part"),
    ("parcours", "Tribus datées en jours", "Tribus", "part"),
    ("jour_sortie", "Jour de sortie", "Sortie", "part"),
    ("votes_recus", "Voix reçues", "Voix", "part"),
    ("classement", "Rang final", "Rang", "part"),
    ("victoires", "Palmarès d'épreuves", "Palmarès", "part"),
    ("conseils", "Conseils rattachés à un éliminé", "Conseils", "part"),
    ("bulletins", "Conseils au dépouillement complet", "Bulletins", "part"),
    ("epreuves", "Bilan des épreuves par épisode", "Épreuves", "fait"),
    ("colliers", "Destin des colliers", "Colliers", "fait"),
    ("fusion", "Réunification repérée", "Fusion", "fait"),
    ("ambassadeurs", "Ambassadeurs nommés", "Ambassade", "fait"),
    ("audience_saison", "Audience de la saison", "Audience", "fait"),
    ("audience_episode", "Audience par épisode", "Audience/ép.", "fait"),
    ("poteaux", "Vainqueur des poteaux", "Poteaux", "fait"),
]

# Champs de participation dont la part se calcule directement.
PART_DIRECTE = {"age": "age", "profession": "profession",
                "localisation": "localisation", "couleur": "couleur",
                "parcours": "parcours", "jour_sortie": "jour_sortie",
                "votes_recus": "votes_recus", "classement": "classement",
                "victoires": "victoires_individuelles"}


def bloc_completude_saisons(saisons, parts, conseils, epreuves, colliers, modeles, finale):
    """Une ligne par edition, une colonne par type de donnee, une part au croisement.

    C'est la carte des trous. Elle sert a deux choses : voir d'un coup d'oeil
    ou le jeu de donnees est mince, et empecher une page d'affirmer sur une
    saison ce que la saison ne dit pas.

    Une case vide n'a pas toujours le meme sens. « Sans objet » -- la mecanique
    n'existait pas cette annee-la -- n'est pas « manquant », et les deux ne se
    peignent pas pareil.
    """
    par_saison = defaultdict(list)
    for p in parts:
        par_saison[p["saison"]].append(p)
    conseils_par = defaultdict(list)
    for c in conseils:
        if c.get("type", "elimination") == "elimination":
            conseils_par[c["saison"]].append(c)
    epreuves_par = Counter(e["saison"] for e in epreuves)
    colliers_par = Counter(c["saison"] for c in colliers)

    fusion = {l["saison"] for l in ((modeles.get("fusion") or {}).get("lignes") or [])}
    audiences = _fichier_data("audiences.yml")
    aud_saison = {x["saison"] for x in (audiences.get("saisons") or [])}
    aud_episode = set(audiences.get("saisons_par_episode") or [])
    ambassades = _fichier_data("ambassadeurs.yml")
    amb_nommees = {l["saison"] for l in (ambassades.get("lignes") or [])
                   if l.get("ambassadeurs")}
    amb_toutes = {l["saison"] for l in (ambassades.get("lignes") or [])}
    # La fin de saison : la colonne ne vaut que la ou le format des poteaux
    # existe. Une saison dont la fin n'a pas ce format n'a pas de trou, elle a
    # une autre histoire -- « sans objet », pas « manquant ».
    fin_lignes = (finale or {}).get("lignes") or []
    fin_format = {l["saison"] for l in fin_lignes}
    fin_connu = {l["saison"] for l in fin_lignes if l["poteaux"].get("vainqueur")}

    def part(n, total):
        return round(100.0 * n / total, 1) if total else None

    lignes = []
    for s in sorted(saisons, key=lambda x: (x.get("annee") or 0, x["id"])):
        if s.get("annulee"):
            continue
        sid = s["id"]
        membres = par_saison.get(sid) or []
        attendu = s.get("nb_candidats") or len(membres)
        lot = conseils_par.get(sid) or []
        cellules = []
        for cle, _libelle, _court, nature in COLONNES_COMPLETUDE:
            etat, valeur, texte = "manquant", None, "—"
            if cle == "casting":
                valeur = part(len(membres), attendu)
                texte = f"{len(membres)}/{attendu}"
            elif cle in PART_DIRECTE:
                champ = PART_DIRECTE[cle]
                n = sum(1 for p in membres if p.get(champ) not in (None, "", []))
                valeur = part(n, len(membres))
                texte = f"{n}/{len(membres)}" if membres else "—"
            elif cle == "conseils":
                n = sum(1 for c in lot if c.get("elimine_rattache"))
                valeur = part(n, len(lot))
                texte = f"{n}/{len(lot)}" if lot else "—"
            elif cle == "bulletins":
                n = sum(1 for c in lot if c.get("complet"))
                valeur = part(n, len(lot))
                texte = f"{n}/{len(lot)}" if lot else "—"
            elif cle == "epreuves":
                valeur = 100.0 if epreuves_par.get(sid) else 0.0
                texte = f"{epreuves_par.get(sid, 0)} relevées" if epreuves_par.get(sid) else "aucune"
            elif cle == "colliers":
                if "collier_immunite" not in (s.get("mecaniques") or []):
                    etat, valeur, texte = "sans_objet", None, "pas de collier"
                else:
                    valeur = 100.0 if colliers_par.get(sid) else 0.0
                    texte = f"{colliers_par.get(sid, 0)} suivis" if colliers_par.get(sid) else "non détaillés"
            elif cle == "fusion":
                if s.get("speciale"):
                    etat, valeur, texte = "sans_objet", None, "édition spéciale"
                else:
                    valeur = 100.0 if sid in fusion else 0.0
                    texte = "repérée" if sid in fusion else "non repérée"
            elif cle == "ambassadeurs":
                if sid not in amb_toutes:
                    etat, valeur, texte = "sans_objet", None, "pas d'ambassade"
                else:
                    valeur = 100.0 if sid in amb_nommees else 0.0
                    texte = "nommés" if sid in amb_nommees else "non nommés"
            elif cle == "audience_saison":
                valeur = 100.0 if sid in aud_saison else 0.0
                texte = "connue" if sid in aud_saison else "inconnue"
            elif cle == "audience_episode":
                valeur = 100.0 if sid in aud_episode else 0.0
                texte = "connue" if sid in aud_episode else "inconnue"
            elif cle == "poteaux":
                if sid not in fin_format:
                    etat, valeur, texte = "sans_objet", None, "fin hors format"
                else:
                    valeur = 100.0 if sid in fin_connu else 0.0
                    texte = "nommé" if sid in fin_connu else "non nommé"

            if etat != "sans_objet":
                if valeur is None:
                    etat = "manquant"
                elif valeur >= 99.9:
                    etat = "complet"
                elif valeur >= 80:
                    etat = "eleve"
                elif valeur >= 50:
                    etat = "partiel"
                elif valeur > 0:
                    etat = "mince"
                else:
                    etat = "manquant"
            cellules.append({"cle": cle, "valeur": valeur, "texte": texte,
                             "etat": etat, "nature": nature})

        connues = [c for c in cellules if c["etat"] != "sans_objet"]
        lignes.append({
            "saison": sid,
            "numero": s.get("numero"),
            "titre": s.get("titre"),
            "pays": s.get("pays"),
            "lieu": s.get("lieu"),
            "annee": s.get("annee"),
            "speciale": bool(s.get("speciale")),
            "effectif": len(membres),
            "score": round(sum(c["valeur"] or 0 for c in connues) / len(connues), 1)
                     if connues else None,
            "cellules": cellules,
        })

    total = [c for l in lignes for c in l["cellules"] if c["etat"] != "sans_objet"]
    par_colonne = []
    for cle, libelle, court, nature in COLONNES_COMPLETUDE:
        lot = [l for ligne in lignes for l in ligne["cellules"]
               if l["cle"] == cle and l["etat"] != "sans_objet"]
        par_colonne.append({
            "cle": cle, "libelle": libelle, "court": court, "nature": nature,
            "moyenne": round(sum(c["valeur"] or 0 for c in lot) / len(lot), 1) if lot else None,
            "completes": sum(1 for c in lot if c["etat"] == "complet"),
            "concernees": len(lot),
        })
    return {
        "colonnes": [{"cle": c, "libelle": l, "court": k, "nature": n}
                     for c, l, k, n in COLONNES_COMPLETUDE],
        "lignes": lignes,
        "par_colonne": par_colonne,
        "saisons": len(lignes),
        "cases": len(total),
        "moyenne": round(sum(c["valeur"] or 0 for c in total) / len(total), 1) if total else None,
        "meilleure": max(lignes, key=lambda l: l["score"] or 0)["saison"] if lignes else None,
        "pire": min(lignes, key=lambda l: l["score"] or 101)["saison"] if lignes else None,
    }


def _fichier_data(nom):
    """Lit un fichier de _data/ produit par un autre script, ou rend {}."""
    chemin = os.path.join(RACINE, "_data", nom)
    if not os.path.exists(chemin):
        return {}
    with open(chemin, encoding="utf-8") as f:
        return donnees.charger(f) or {}


def bloc_completude(parts, personnes):
    """Ce qui est renseigne, ce qui manque, et d'ou vient ce qui a ete comble.

    Le site affirme partout ce qu'il ne sait pas ; encore faut-il le compter.
    Ce bloc est la mesure, champ par champ, et il se recalcule tout seul : nul
    besoin de reprendre une phrase quand une valeur est trouvee.
    """
    lignes, comblees = [], 0
    for champ, libelle in CHAMPS_SUIVIS:
        remplis = sum(1 for p in parts if p.get(champ) not in (None, "", []))
        depuis_page = sum(1 for p in parts
                          if (p.get("sources") or {}).get(champ) == PAGE_INDIVIDUELLE)
        comblees += depuis_page
        lignes.append({
            "champ": champ, "libelle": libelle,
            "remplis": remplis, "manquants": len(parts) - remplis,
            "part": round(100.0 * remplis / len(parts), 1),
            "depuis_page_individuelle": depuis_page,
        })
    lignes.sort(key=lambda x: (x["manquants"], x["champ"]))
    # Une participation est « sans fiche » si aucun de ses champs ne vient
    # d'une page individuelle : soit la personne n'en a pas, soit la sienne ne
    # dit rien de cette saison-la.
    avec_fiche = sum(1 for p in parts
                     if any(v == PAGE_INDIVIDUELLE
                            for v in (p.get("sources") or {}).values()))
    return {
        "participations": len(parts),
        "avec_fiche": avec_fiche,
        "sans_fiche": len(parts) - avec_fiche,
        "personnes": len(personnes),
        "champs": lignes,
        "champs_complets": sum(1 for x in lignes if x["manquants"] == 0),
        "champs_suivis": len(lignes),
        "trous": sum(x["manquants"] for x in lignes),
        "valeurs_suivies": len(parts) * len(lignes),
        "comblees": comblees,
        "part_remplie": round(100.0 * (1 - sum(x["manquants"] for x in lignes)
                                       / (len(parts) * len(lignes))), 2),
    }


def bloc_palmares(parts, epreuves, par_saison):
    """Le palmares d'epreuves declare par les fiches individuelles.

    _data/epreuves.yml compte ce que le bilan par episode montre, et il ignore
    cinq saisons entieres. Les fiches individuelles, elles, portent un total par
    edition sur presque toutes -- mais ce total est plus large : il compte les
    duels de l'ile des bannis et les epreuves de finale, que le bilan par
    episode n'a pas.

    Les deux comptes ne sont donc pas le meme objet, et ce bloc mesure a quel
    point ils s'accordent la ou les deux existent. C'est ce qui autorise, ou
    non, a lire le premier quand le second manque.
    """
    couvertes = {e["saison"] for e in epreuves}

    # Le compte du bilan par episode, par (personne, saison).
    table = defaultdict(int)
    for e in epreuves:
        if e.get("forme") != "individuelle":
            continue
        for v in e.get("vainqueurs") or []:
            if v.get("type") == "personne" and v.get("id"):
                table[(v["id"], e["saison"])] += 1

    ecarts, identiques, compares = [], 0, 0
    for p in parts:
        n = p.get("victoires_individuelles")
        if n is None or p["saison"] not in couvertes:
            continue
        compares += 1
        d = n - table.get((p["id"], p["saison"]), 0)
        if d == 0:
            identiques += 1
        else:
            ecarts.append(abs(d))

    # Les carrieres, toutes saisons confondues.
    cumul = {}
    for p in parts:
        if p.get("victoires_individuelles") is None:
            continue
        e = cumul.setdefault(p["id"], {
            "personne": p.get("nom_complet") or p["nom"],
            "individuelles": 0, "collectives": 0, "saisons": 0})
        e["individuelles"] += p["victoires_individuelles"]
        e["collectives"] += p.get("victoires_collectives") or 0
        e["saisons"] += 1
    classement = sorted(cumul.values(),
                        key=lambda x: (-x["individuelles"], -x["collectives"],
                                       x["personne"]))

    # Ce que les fiches ajoutent : les saisons que le bilan par episode ignore.
    ajoutees = []
    for sid, s in sorted(par_saison.items(), key=lambda kv: kv[1].get("annee") or 0):
        if sid in couvertes or s.get("annulee"):
            continue
        lignes = [p for p in parts if p["saison"] == sid
                  and p.get("victoires_individuelles") is not None]
        if lignes:
            ajoutees.append({"saison": sid, "titre": s.get("titre"),
                             "annee": s.get("annee"), "aventuriers": len(lignes)})

    return {
        "renseignees": sum(1 for p in parts if p.get("victoires_individuelles") is not None),
        "compares": compares,
        "identiques": identiques,
        "part_identiques": round(100.0 * identiques / compares, 1) if compares else None,
        "ecart_median": round(median(ecarts), 1) if ecarts else 0,
        "saisons_ajoutees": ajoutees,
        "classement": classement[:15],
    }


def _arrondi_entier(x):
    """L'arrondi de Liquid (celui de Ruby) : la demie s'eloigne de zero.
    `round()` de Python arrondit au pair, et 92.5 y donne 92."""
    return int(math.floor(abs(x) + 0.5)) * (1 if x >= 0 else -1)


def _niveau(part):
    """Les cinq niveaux de la grille de completude, pour une part en %."""
    if part >= 99.9:
        return "complet"
    if part >= 80:
        return "eleve"
    if part >= 50:
        return "partiel"
    return "mince"


UNITES = ["zéro", "un", "deux", "trois", "quatre", "cinq", "six", "sept", "huit",
          "neuf", "dix", "onze", "douze", "treize", "quatorze", "quinze", "seize"]
DIZAINES = {2: "vingt", 3: "trente", 4: "quarante", 5: "cinquante", 6: "soixante"}


def en_lettres(n):
    """Un entier de 0 a 99 en toutes lettres, a l'ancienne : « vingt et un »,
    « soixante-dix », « quatre-vingts ». Au-dela, les chiffres."""
    n = int(n)
    if n < 17:
        return UNITES[n]
    if n < 20:
        return "dix-" + UNITES[n - 10]
    if n >= 100:
        return str(n)
    d, u = divmod(n, 10)
    if d in (7, 9):
        base = "soixante" if d == 7 else "quatre-vingt"
        reste = 10 + u
        if d == 7 and u == 1:
            return "soixante et onze"
        return base + "-" + en_lettres(reste)
    base = "quatre-vingt" if d == 8 else DIZAINES[d]
    if u == 0:
        return "quatre-vingts" if d == 8 else base
    if u == 1 and d != 8:
        return base + " et un"
    return base + "-" + UNITES[u]


def ordinal_lettres(n):
    """« cinquieme », « neuvieme » : l'ordinal en toutes lettres, n >= 2."""
    mot = en_lettres(n)
    if mot.endswith("cinq"):
        return mot + "uième"
    if mot.endswith("neuf"):
        return mot[:-1] + "vième"
    if mot.endswith("e"):
        mot = mot[:-1]
    return mot + "ième"


def poser_les_mots(stats, valeurs):
    """`stats.mots` : les comptes que la prose ecrit en toutes lettres.

    Une page ecrivait « quatre facettes » ou « depuis vingt-cinq ans » a la
    main ; le chiffre ne suivait pas les donnees. Le mot est fabrique ici, et
    sa variante a majuscule pour un debut de phrase -- aucune mise en forme en
    Liquid."""
    mots = stats.setdefault("mots", {})
    for cle, v in valeurs.items():
        if v is None:
            continue
        mot = en_lettres(v)
        mots[cle] = mot
        mots[cle + "_maj"] = mot[0].upper() + mot[1:]


def champs_du_texte(stats, saisons, parts):
    """Les comptes que la prose citait a la main (lot 4b), page citee.

    Chaque champ remplace un nombre ecrit dans une phrase ; quand la phrase
    l'ecrit en toutes lettres, le mot est pose dans `stats.mots`."""
    m, g = stats["modeles"], stats["general"]
    mots = {
        # Partout : « depuis vingt-cinq ans », « 34 saisons ».
        "etendue_annees": g["etendue_annees"],
        "saisons_diffusees": g["saisons_diffusees"],
        "saisons_annulees": g["saisons_annulees"],
        "facettes": len(stats["classement"]["facettes"]),
        "saisons_sans_bilan": len(stats["epreuves"].get("saisons_sans_donnee") or []),
        "saisons_source_unique": len(stats["epreuves"].get("saisons_source_unique") or []),
        # /statistiques/grille/ : les indicateurs de la rupture.
        "indicateurs_rupture": len(m["ruptures"]["detail"]),
        # /statistiques/audience/
        "audience_saisons": m["audience"]["saisons"],
        "audience_courbes": len(m["audience"]["courbes"]),
    }

    # /statistiques/grille/ : de combien d'annees la rupture a bouge depuis la
    # premiere datation publiee, 2012 -- un fait d'histoire du site, d'ou la
    # constante.
    r = m["ruptures"]
    mots["rupture_deplacement"] = r["annee_rupture"] - 2012
    ab = next(x for x in r["detail"] if x["libelle"] == "Taux d'abandon")
    r["abandon_rapport"] = round(ab["avant"] / ab["apres"], 1) if ab["apres"] else None

    # /statistiques/audience/ : les annees de vendredi avant la bascule au
    # mardi, comptees depuis la premiere saison diffusee le vendredi.
    a = m["audience"]
    vendredis = [x["annee"] for x in a["serie"] if x.get("jour") == "Vendredi"]
    if vendredis:
        mots["annees_de_vendredi"] = a["bascule_jour"]["annee"] - min(vendredis)

    # /statistiques/force/ : combien de fois le tenant du titre regagne.
    tt = m["tenant_du_titre"]
    tt["rapport"] = round(tt["tenant"]["probabilite"] / tt["autres"]["probabilite"], 1)

    # /statistiques/alliances/ : l'episode median de la fusion, et la plus
    # longue serie de sorties d'un meme bandeau.
    mots["episode_fusion"] = m["fusion"]["episode_median"]
    mots["serie_decimation"] = m["decimation"]["detail"][0]["plus_longue_serie"]

    # /completude/ : la premiere saison a collier, les plus petit et plus grand
    # castings, les annees des editions annulees.
    avec_collier = [s["annee"] for s in saisons
                    if "collier_immunite" in (s.get("mecaniques") or [])]
    g["premiere_annee_collier"] = min(avec_collier) if avec_collier else None
    mots["casting_min"] = m["fusion"]["casting_min"]
    mots["casting_max"] = m["fusion"]["casting_max"]
    annulees = sorted(s["annee"] for s in saisons if s.get("annulee") and s.get("annee"))
    g["annees_annulees_texte"] = (" et de ".join(str(a) for a in annulees))

    # /statistiques/qui-vise-qui/ : l'ancien coequipier vise « N % moins
    # souvent » qu'attendu, apres la fusion.
    for t in m["registre"]:
        if t["cle"] == "vote_bandeau_apres_fusion" and t.get("attendu"):
            t["ecart_relatif"] = _arrondi_entier(100 * (1 - t["observe"] / t["attendu"]))

    # /saisons/ : la saison la plus dominee aux epreuves (classiques) et la
    # plus partagee (toutes), l'ecart maximal a la parite.
    ind = stats["indicateurs"]["saisons"]
    dom = [x for x in ind if x.get("domination_epreuves") is not None]
    classiques = [x for x in dom if not x["speciale"]]
    if classiques:
        dmax = max(classiques, key=lambda x: x["domination_epreuves"])
        stats["indicateurs"]["domination_max"] = dmax
        mots["victoires_domination_max"] = dmax["victoires_du_meilleur"]
    if dom:
        stats["indicateurs"]["domination_min"] = min(dom, key=lambda x: x["domination_epreuves"])
    mots["survie_saisons"] = len(stats["survie_saisons"])
    ecarts = []
    for s in saisons:
        if s.get("annulee") or s.get("speciale") or s.get("en_cours"):
            continue
        gens = [p for p in parts if p["saison"] == s["id"] and p.get("genre")]
        if gens:
            f = sum(1 for p in gens if p["genre"] == "f")
            ecarts.append(abs(f - len(gens) / 2))
    g["parite_ecart_max"] = max(ecarts) if ecarts else None

    # /statistiques/pronostic/ : la taille moyenne d'un casting du modele, et
    # la part des conseils ou le pronostic se trompe de personne.
    pr = m["pronostic"]
    pr["casting_moyen"] = round(pr["effectif"] / pr["saisons"], 1) if pr.get("saisons") else None
    for jeu in stats["prevision"].get("jeux") or []:
        if jeu.get("premiers") is not None:
            jeu["erreurs"] = round(100 - jeu["premiers"], 1)

    # /statistiques/jury/ : le co-vote sur cinq conseils partages.
    jf = m["jury_final"]["coefficients"]
    jf[1]["cinq_conseils"] = round(jf[1]["rapport"] ** 5, 1)

    # /statistiques/vainqueurs/ : egalites du jury, ecart d'age, revenants,
    # rapport des voix recues.
    egalites = sum(1 for s in saisons if not s.get("annulee") and not s.get("speciale")
                   and not s.get("en_cours") and len(s.get("vainqueurs") or []) > 1)
    mots["egalites_jury"] = egalites
    v = stats["vainqueurs"]
    mots["ecart_age_vainqueurs"] = v["age_max"] - v["age_min"]
    rv = stats["revenants"]
    rv["vainqueurs_revenus_autres"] = rv["vainqueurs_revenus"] - len(rv["vainqueurs_multiples"])
    vv = stats["indicateurs"]["voix_des_vainqueurs"]["par_sort"]
    vv_rapport = round(vv[2]["menace_moyenne"] / vv[0]["menace_moyenne"], 1) if vv[0]["menace_moyenne"] else None
    stats["indicateurs"]["voix_des_vainqueurs"]["rapport_ensemble"] = vv_rapport

    # /statistiques/geographie/ : l'outre-mer et la Corse, que le texte nomme.
    chemin_geo = os.path.join(RACINE, "_data", "geographie.yml")
    if os.path.exists(chemin_geo):
        geo = donnees.charger(open(chemin_geo, encoding="utf-8"))
        reg = {x["region"]: x for x in geo.get("regions") or []}
        sg = stats.setdefault("geographie", {})
        sg["outremer_observe"] = (geo.get("outremer") or {}).get("observe")
        sg["reunion_observe"] = (reg.get("La Réunion") or {}).get("observe")
        sg["martinique_observe"] = (reg.get("Martinique") or {}).get("observe")
        sg["premiere_region"] = (geo.get("regions") or [{}])[0].get("region")
        mots["regions_outremer"] = len((geo.get("outremer") or {}).get("regions") or [])

    # /statistiques/finale/ : les saisons ou le vainqueur des poteaux est
    # connu, et celles ou le choix est atteste.
    po = stats["finale"].get("poteaux") or {}
    mots["poteaux_saisons"] = po.get("effectif")
    mots["choix_atteste"] = (po.get("choix_atteste") or {}).get("effectif")

    # /statistiques/top/ : la facette retiree, les corrections du soir du
    # depart, les paires de facettes.
    cl = stats["classement"]
    mots["facettes_initiales"] = len(cl["facettes"]) + 1
    mots["artefacts"] = len(cl["artefacts"])
    mots["paires"] = len(cl["correlations"])

    # /statistiques/casting/ : l'ecart d'etendue des ages en mois, les saisons
    # aux tribus contrastees, les archetypes.
    ca = m["casting"]
    for t in m["registre"]:
        if t["cle"] == "etendue_ages":
            mots["ecart_ages_mois"] = round(12 * (t["observe"] - t["attendu"]))
    mots["tribus_contrastees"] = len(ca["tribus_les_plus_contrastees"])
    mots["tribus_non_contrastees"] = ca["duos_de_tribus"] - len(ca["tribus_les_plus_contrastees"])
    mots["duos_de_tribus"] = ca["duos_de_tribus"]
    mots["archetypes"] = ca["nb_archetypes"]

    # /statistiques/conditionnelles/ : la part des noms rendus qui ne
    # reviennent pas ; les modalites en debut de cellule, sans `capitalize`
    # (qui minusculerait la suite).
    co = m["conditionnelles"]
    co["retour"]["non_rendus"] = round(100 - co["retour"]["probabilite"], 1)
    for x in co.get("par_camp") or []:
        x["modalite_maj"] = x["modalite"][:1].upper() + x["modalite"][1:]

    # /statistiques/fusion/ : les mesures avant/apres, les ambassades nommees
    # par les deux sources.
    aa = m["avant_apres"]
    mots["avant_apres_tests"] = len(aa["tests"])
    ng = aa["negociateurs"]
    if ng.get("sources_accord") is not None:
        ng["sources_communes"] = ng["sources_accord"] + (ng.get("sources_desaccord") or 0)

    # /statistiques/epreuves/ : les 25-34 ans par personne et l'ecart aux
    # 45 ans et plus ; la marge de l'intervalle du confort ; le gain de
    # l'appariement resserre, depuis 11,0 % (fait d'histoire du site).
    ep = stats["epreuves"]
    pa = {x["tranche"]: x for x in ep.get("par_age") or []}
    jeunes = [pa[t] for t in ("25-29 ans", "30-34 ans") if t in pa]
    if jeunes and "45 ans et plus" in pa:
        par_tete = (sum(x["victoires"] for x in jeunes)
                    / sum(x["aventuriers"] for x in jeunes))
        ep["victoires_25_34"] = round(par_tete, 2)
        ep["rapport_45_et_plus"] = round(par_tete / pa["45 ans et plus"]["victoires_par_aventurier"], 1)
    cf = m["confort_maudit"]
    cf["marge"] = _arrondi_entier(max(cf["haut"] - cf["attendu"], cf["attendu"] - cf["bas"]))
    chemin_en = os.path.join(RACINE, "_data", "epreuves_nommees.yml")
    if os.path.exists(chemin_en):
        en = donnees.charger(open(chemin_en, encoding="utf-8"))
        part_r = (en.get("raccord") or {}).get("part_raccordee")
        if part_r is not None:
            ep["gain_appariement"] = round(part_r - 11.0, 1)
        # /epreuves/ : les noms sans apparition datee, et sans vainqueur nomme
        # au palmares du wiki.
        noms = [x["nom"] for x in en.get("epreuves") or []]
        gagnees = {n for x in en.get("palmares") or [] for n in x.get("epreuves") or []}
        mots["noms_sans_apparition"] = sum(1 for x in en.get("epreuves") or []
                                           if not x.get("apparitions"))
        mots["noms_sans_vainqueur"] = sum(1 for n in noms if n not in gagnees)

    # /statistiques/autour-du-feu/ : victoires par couleur, tests de la page.
    couleurs = {x["couleur"]: x for x in stats["couleurs"]}
    mots["victoires_jaunes"] = (couleurs.get("jaune") or {}).get("victoires")
    mots["victoires_rouges"] = (couleurs.get("rouge") or {}).get("victoires")
    aft = m["autour_du_feu"].get("tests") or []
    mots["autour_tests"] = len(aft)
    mots["autour_retenus"] = sum(1 for t in aft if t.get("retenu"))

    # /statistiques/conseils/ : saisons a objet joue rapportees aux saisons
    # dont les colliers sont detailles ; l'etendue des voix pour eliminer.
    cs = stats["conseils"]
    if stats["colliers"].get("saisons_couvertes"):
        cs["rapport_saisons_objets"] = round(cs["saisons_avec_objet_joue"]
                                             / stats["colliers"]["saisons_couvertes"], 1)
    rep_voix = [x["voix"] for x in stats["voix_pour_eliminer"]["repartition"]]
    if rep_voix:
        stats["voix_pour_eliminer"]["voix_min"] = min(rep_voix)
        stats["voix_pour_eliminer"]["voix_max"] = max(rep_voix)

    # /statistiques/revenants/ : rappel du dernier cinquieme contre le premier,
    # les deux lignes d'abandon, l'intervalle entre les deux titres, la duree
    # de survie par tranche d'age, et le coefficient « deja venu ».
    rp = m["rappel"]
    ps = rp["par_survie"]
    if ps[0]["probabilite"]:
        rp["rapport_survie"] = round(ps[4]["probabilite"] / ps[0]["probabilite"], 1)
    rp["abandons_derniers"] = sum(x["effectif"] for x in rp["par_sort"][-2:])
    mots["retours_abandon"] = sum(x["cas"] for x in rp["par_sort"][-2:])
    annee_de = {s.get("titre"): s.get("annee") for s in saisons}
    vm = stats["revenants"]["vainqueurs_multiples"]
    if len(vm) == 1:
        ans = [annee_de.get(t) for t in vm[0]["editions"]]
        if all(ans):
            mots["intervalle_titres"] = max(ans) - min(ans)
    stats["age_survie_max"] = max(stats["age"], key=lambda x: x["survie_moyenne"] or 0)["tranche"]
    stats["age_finale_max"] = max(stats["age"], key=lambda x: x["taux_finale"] or 0)["tranche"]
    cox = {x["variable"]: x for x in m["equilibre"]["cox"]["coefficients"]}
    if cox.get("Déjà venu"):
        m["equilibre"]["cox"]["deja_venu_inverse"] = round(1 / cox["Déjà venu"]["rapport"], 1)

    # /statistiques/sorties/ : le recul des abandons d'une decennie a l'autre.
    pdec = stats["sorties"]["par_decennie"]
    if pdec[-1]["abandons"]:
        stats["sorties"]["abandons_rapport"] = round(pdec[0]["abandons"] / pdec[-1]["abandons"], 1)

    # /statistiques/prenoms/ : la page comptait ses absents en Liquid, et
    # ecrivait a la main le facteur maximal, la decennie du sommet et la part
    # des porteurs absents.
    chemin_pr = os.path.join(RACINE, "_data", "prenoms.yml")
    if os.path.exists(chemin_pr):
        pr = donnees.charger(open(chemin_pr, encoding="utf-8"))
        liste = pr.get("prenoms") or []
        absents = [x for x in liste if x.get("absent_du_fichier")]
        porteurs = sum(x["observe"] for x in absents)
        tableau = [x["indice"] for x in liste if x.get("au_tableau") and x.get("indice") is not None]
        alexandra = next((x for x in liste if x.get("prenom") == "Alexandra"), {})
        stats["prenoms"] = {
            "absents": len(absents),
            "porteurs_absents": porteurs,
            "part_porteurs_absents": part(porteurs, g["participations"]),
            "indice_max_tableau": max(tableau) if tableau else None,
            "alexandra": alexandra.get("observe"),
        }
    gen = stats["casting"].get("generations") or []
    if gen:
        stats["casting"]["decennie_sommet"] = max(gen, key=lambda x: x["effectif"])["decennie"]

    # /statistiques/equilibre/ : les saisons du test des mecaniques.
    mots["mecaniques_saisons"] = m["mecaniques"].get("saisons")

    # /statistiques/jeu-social/ : fantomes recidivistes ; fantomes vainqueurs
    # au-dela des quatre nommes (la page soustrayait en Liquid) ; le plus de
    # conseils traverses sans etre ecrit par un futur vainqueur.
    ind_ = stats["indicateurs"]
    mots["fantomes_recidivistes"] = len(ind_["fantomes_recidivistes"])
    fv = ind_["fantomes_vainqueurs"]
    ind_["fantomes_vainqueurs_autres"] = max(0, len(fv) - 4)
    if fv:
        mots["fantome_vainqueur_conseils"] = max(x["conseils"] for x in fv)

    # /statistiques/ et l'accueil : les entrees du sommaire, celles qui
    # decrivent et celles qui testent (`modeles: true`).
    chemin_nav = os.path.join(RACINE, "_data", "navigation.yml")
    if os.path.exists(chemin_nav):
        nav = donnees.charger(open(chemin_nav, encoding="utf-8")) or []
        entrees = [e for gr in nav if gr.get("fil") for t in gr.get("themes") or []
                   for e in t.get("entrees") or [] if not e.get("hub")]
        testees = sum(1 for e in entrees if e.get("modeles"))
        stats["sommaire"] = {"entrees": len(entrees), "testees": testees,
                             "descriptives": len(entrees) - testees}
        mots["sommaire_entrees"] = len(entrees)
        mots["sommaire_testees"] = testees
        mots["sommaire_descriptives"] = len(entrees) - testees

    # /statistiques/professions/ et /sources/ : les intitules de metier
    # distincts ; /statistiques/tribus/ : la couleur noire.
    g["metiers_distincts"] = len({p["profession"] for p in parts if p.get("profession")})
    mots["effectif_noir"] = (couleurs.get("noir") or {}).get("effectif")

    # /sources/ : les saisons dont la duree annoncee diverge des tables de
    # candidats ; /methode/ : les facettes corrigees du soir du depart.
    divergentes = sum(1 for s in saisons if s.get("duree_annoncee") is not None)
    g["durees_divergentes"] = divergentes
    g["durees_concordantes"] = g["saisons_diffusees"] - divergentes
    mots["durees_divergentes"] = divergentes
    mots["facettes_corrigees"] = len(cl["artefacts"]) - 1
    chemin_cv = os.path.join(RACINE, "_data", "croisement_votes.yml")
    if os.path.exists(chemin_cv):
        stats["croisement_divergents"] = donnees.charger(open(chemin_cv, encoding="utf-8")).get("divergents")

    # Lot 4c. /statistiques/alliances/ : les paires d'aventuriers qu'une meme
    # saison rend possibles (« des milliers »).
    paires = 0
    for s in saisons:
        if s.get("annulee") or s.get("en_cours"):
            continue
        n = sum(1 for p in parts if p["saison"] == s["id"])
        paires += n * (n - 1) // 2
    g["paires_possibles"] = paires
    g["paires_possibles_texte"] = f"{paires:,}".replace(",", "\u00a0")
    # /statistiques/epreuves/ : les pages de la categorie « Epreuves » du wiki,
    # telles que la recuperation les a listees.
    chemin_tit = os.path.join(RACINE, "specs", "sources", "epreuves", "_titres.json")
    if os.path.exists(chemin_tit):
        with open(chemin_tit, encoding="utf-8") as f:
            stats["epreuves"]["pages_categorie"] = len(json.load(f))
    # /statistiques/revenants/ : les anciens vainqueurs engages dans la saison
    # en cours et deja sortis, nommes par la page.
    deja = {p["id"] for p in parts if p.get("sort") == "vainqueur"
            and not any(s.get("en_cours") for s in saisons if s["id"] == p["saison"])}
    en_cours = {s["id"] for s in saisons if s.get("en_cours")}
    sortis = [p for p in parts if p["saison"] in en_cours and p["id"] in deja and p.get("sort")]
    phrases = []
    for p in sortis:
        e = "e" if p.get("genre") == "f" else ""
        phrases.append(f"{p.get('nom_complet') or p.get('nom')} y était aussi engagé{e} "
                       f"et en est sorti{e}")
    stats["revenants"]["vainqueurs_sortis_texte"] = " ; ".join(phrases)

    poser_les_mots(stats, mots)
    stats["mots"]["facette_retiree_rang"] = ordinal_lettres(len(cl["facettes"]) + 1)


def _maj(texte):
    """Premiere lettre en capitale, le reste intact -- ce que `capitalize` de
    Liquid ne fait pas : il minuscule la suite, noms propres compris."""
    return texte[:1].upper() + texte[1:] if texte else texte


def _min(texte):
    """Premiere lettre en minuscule, le reste intact."""
    return texte[:1].lower() + texte[1:] if texte else texte


def _poser_partout(noeud, cle, nouvelle, forme):
    """Pose `nouvelle` = forme(noeud[cle]) dans tout dictionnaire du sous-arbre."""
    if isinstance(noeud, dict):
        if isinstance(noeud.get(cle), str):
            noeud[nouvelle] = forme(noeud[cle])
        for v in list(noeud.values()):
            _poser_partout(v, cle, nouvelle, forme)
    elif isinstance(noeud, list):
        for v in noeud:
            _poser_partout(v, cle, nouvelle, forme)


def _etendue_des_rangs(noeud):
    if isinstance(noeud, dict):
        if isinstance(noeud.get("rang_p05"), (int, float)) and isinstance(noeud.get("rang_p95"), (int, float)):
            noeud["etendue_rangs"] = noeud["rang_p95"] - noeud["rang_p05"]
        for v in list(noeud.values()):
            _etendue_des_rangs(v)
    elif isinstance(noeud, list):
        for v in noeud:
            _etendue_des_rangs(v)


def positions_du_sommaire(nav):
    """Section, theme, rang et voisins de chaque page, d'apres navigation.yml.

    Le gabarit `page.html`, le fil de lecture et les cartes du sommaire
    comptaient en Liquid (`plus: 1`, `minus: 1`) ; ils lisent desormais ce
    tableau, une entree par adresse. L'ordre est celui du sommaire : les
    entrees propres de la section, puis celles de chaque theme."""
    pages = {}
    for g in nav or []:
        toutes = list(g.get("entrees") or [])
        for t in g.get("themes") or []:
            toutes += [dict(e, _theme=t.get("titre")) for e in t.get("entrees") or []]
        rangs = [e for e in toutes if not e.get("hub")]
        for i, e in enumerate(toutes):
            fiche = pages.setdefault(e["url"], {"section": g.get("section")})
            if g.get("fil") and not e.get("hub"):
                fiche["rang"] = rangs.index(e) + 1
                fiche["total"] = len(rangs)
                if e.get("_theme"):
                    fiche["theme"] = e["_theme"]
            if g.get("fil"):
                if i > 0:
                    fiche["precedent"] = {"url": toutes[i - 1]["url"], "titre": toutes[i - 1]["titre"]}
                if i + 1 < len(toutes):
                    fiche["suivant"] = {"url": toutes[i + 1]["url"], "titre": toutes[i + 1]["titre"]}
    return pages


def formes_des_gabarits(stats):
    """Ce que les gabarits calculaient ou mettaient en forme en Liquid.

    `capitalize`, `downcase`, `plus`, `minus` : la regle du depot est l'acces
    par cle seulement. Chaque champ ci-dessous remplace un filtre ; la page
    est citee."""
    m, cl = stats["modeles"], stats["classement"]
    # Majuscule de debut de cellule : pire-place, conditionnelles,
    # autour-du-feu, et les couleurs de tribus et vainqueurs.
    for bloc in (m["pire_place"], m["conditionnelles"], m["autour_du_feu"]):
        _poser_partout(bloc, "modalite", "modalite_maj", _maj)
    _poser_partout(m["conditionnelles"].get("modele") or {}, "libelle", "libelle_maj", _maj)
    for c in list(stats["couleurs"]) + list(stats["vainqueurs"].get("par_couleur") or []):
        c["couleur_maj"] = _maj(c["couleur"])
    # /statistiques/top/ : etendue des rangs (cle de tri), joueurs d'une ou
    # deux saisons, intitules de facette en minuscule, facettes menees par
    # le premier du classement.
    _etendue_des_rangs(cl)
    cl["joueurs_courte_carriere"] = cl["joueurs_classes"] - len(cl.get("carrieres") or [])
    for f in cl["facettes"]:
        f["question_min"] = _min(f.get("question") or "")
        f["libelle_min"] = _min(f.get("libelle") or "")
    premier = (cl.get("top") or [{}])[0].get("id")
    cl["facettes_menees_par_premier"] = sum(
        1 for f in cl["facettes"] if (f.get("top") or [{}])[0].get("id") == premier)
    # /saisons/ : la maniere de sortir du premier des meilleures saisons.
    for x in cl.get("top_saisons") or []:
        if isinstance(x.get("sort"), str):
            x["sort_min"] = _min(x["sort"])
    # /statistiques/epreuves/ : les citations qui reviennent a une tribu.
    n = stats.get("natures") or {}
    if n.get("citations") is not None and n.get("attribuees") is not None:
        n["citations_restantes"] = n["citations"] - n["attribuees"]
    # /statistiques/force/ : les epreuves tentees, retenues ou ecartees.
    fo = m["force"]
    fo["epreuves_tentees"] = fo["epreuves_retenues"] + fo["vainqueur_hors_plateau"]
    # /statistiques/conditionnelles/ : les presences de la chaine a deux pas.
    dp = m["conditionnelles"].get("par_voix_deux_pas") or []
    if len(dp) >= 3:
        m["conditionnelles"]["deux_pas_vises"] = dp[1]["effectif"] + dp[2]["effectif"]
        m["conditionnelles"]["deux_pas_total"] = dp[0]["effectif"] + dp[1]["effectif"] + dp[2]["effectif"]
    # /statistiques/jeu-social/ : la maniere de sortir des fantomes, libellee
    # (la page remplacait les soulignes et capitalisait, sans accents).
    for x in stats["indicateurs"].get("fantomes") or []:
        x["sort_libelle"] = LIBELLE_SORT.get(x.get("sort"), x.get("sort"))
    # /sources/ : les ambassades que les deux sources nomment.
    chemin_amb = os.path.join(RACINE, "_data", "ambassadeurs.yml")
    if os.path.exists(chemin_amb):
        amb = donnees.charger(open(chemin_amb, encoding="utf-8"))
        stats["ambassades_sources_communes"] = ((amb.get("sources_accord") or 0)
                                                + (amb.get("sources_desaccord") or 0))
    # Le sommaire, le fil de lecture et l'oeil-de-boeuf des pages.
    chemin_nav = os.path.join(RACINE, "_data", "navigation.yml")
    if os.path.exists(chemin_nav):
        nav = donnees.charger(open(chemin_nav, encoding="utf-8"))
        stats.setdefault("sommaire", {})["pages"] = positions_du_sommaire(nav)


def champs_d_affichage(stats):
    """Ce que les pages calculaient en Liquid, calcule ici.

    Depuis que `_data/` s'ecrit a la francaise (tools/donnees.py), un decimal y
    est une CHAINE pour Liquid -- « 54,2 » -- et `round`, `divided_by`, `times`
    ou `>=` ne s'y appliquent plus : un `>=` entre une chaine et un nombre fait
    meme echouer la construction. C'etait de toute facon la regle du depot,
    aucun calcul dans un gabarit. Chaque champ ci-dessous remplace un filtre ou
    une comparaison qu'une page appliquait ; la page est citee.
    """
    m, c = stats["modeles"], stats["classement"]

    # `t.observe | round: 1` et `t.attendu | round: 1` : une dizaine de pages
    # de resultats citent l'ecart d'un test arrondi au dixieme.
    for t in m["registre"]:
        for cle in ("observe", "attendu"):
            if isinstance(t.get(cle), (int, float)):
                t[f"{cle}_arrondi"] = round(t[cle], 1)

    # /statistiques/jeu-social/ : l'ecart, en points, entre fantomes et
    # endurants, et leur rapport (« N fois plus »).
    for x in stats["indicateurs"]["fantomes_issue"]:
        x["ecart"] = round(x["part_fantomes"] - x["part_endurants"], 1)
        x["rapport"] = (round(x["part_fantomes"] / x["part_endurants"], 1)
                        if x["part_endurants"] else None)

    # /statistiques/epreuves/ : les familles de metier rangees au nombre de
    # victoires PAR PERSONNE. `par_metier` est range au total, et son premier
    # (l'encadrement, cent aventuriers) n'est pas celui qui domine.
    ep = stats["epreuves"]
    ep["par_metier_par_ratio"] = sorted(
        ep["par_metier"], key=lambda x: -x["victoires_par_aventurier"])
    # L'ecart, en points de saison, entre le vainqueur de la premiere epreuve
    # individuelle et l'ensemble, que le texte ecrivait « neuf points ».
    pe = stats["premiere_epreuve"]
    pe["ecart"] = round(pe["survie_gagnants"] - pe["survie_ensemble"], 1)

    # /statistiques/finale/ : combien de victoires du dernier qualifie il
    # faudrait retirer pour que l'intervalle de Wilson reprenne le hasard.
    if stats["finale"].get("par_rang"):
        g = stats["finale"]["par_rang"][2]["gagne_la_saison"]
        retirees = 0
        while retirees < g["cas"] and modeles._wilson(g["cas"] - retirees, g["effectif"])[0] > g["hasard"]:
            retirees += 1
        g["marge"] = retirees

    # /statistiques/jury/ : « divise la cote par N », l'inverse du rapport de
    # cotes d'avoir ecrit le nom du jure.
    for x in m["jury_final"]["coefficients"]:
        x["inverse"] = round(1.0 / x["rapport"], 1) if x.get("rapport") else None

    # /statistiques/longevite/ : l'ecart, en points, entre le doyen du camp et
    # ceux qui ne sont ni le plus age ni le plus jeune.
    af = m["autour_du_feu"]
    af["age_ecart"] = round(af["age"][0]["probabilite"] - af["age"][1]["probabilite"], 1)

    # /statistiques/pire-place/ : par combien le risque est multiplie entre
    # aucun des deux signaux et les deux a la fois.
    pp = m["pire_place"]
    pp["cumul_rapport"] = round(pp["cumul"][2]["probabilite"] / pp["cumul"][0]["probabilite"], 1)

    # /methode/ : les « resultats » que le seul hasard produirait au seuil de
    # 5 %, sur tous les tests du registre.
    m["faux_positifs_attendus"] = round(0.05 * m["nb_tests"], 1)

    # /saisons/ : les saisons classiques sans aucun abandon, et celle qui en a
    # perdu la plus grande part -- les memes que le graphique, qui ecarte les
    # speciales et la saison en cours. La page les nommait a la main.
    ind = stats["indicateurs"]
    sa = [x for x in ind["saisons"] if not x["speciale"] and not x["en_cours"]]
    nulles = [f"*{x['titre']}* ({x['annee']})" for x in sa if x["abandons"] == 0]
    ind["abandon_nul"] = len(nulles)
    ind["abandon_nul_texte"] = (", ".join(nulles[:-1]) + " et " + nulles[-1]
                                if len(nulles) > 1 else "".join(nulles))
    ind["abandon_max"] = max(sa, key=lambda x: x["taux_abandon"] or 0)

    # /statistiques/sorties/ : les participations classiques que la
    # repartition couvre. La page affichait le total general, speciales
    # comprises, au-dessus d'une repartition qui ne les compte pas.
    so = stats["sorties"]
    so["effectif"] = sum(x["effectif"] for x in so["repartition"])

    # /methode/ : le plus petit effet decelable a 80 % de puissance et au seuil
    # de 5 %, niveau par niveau. Un ecart-type pour une grandeur, des points
    # pour une part (au pire, une part de moitie). Le tableau etait ecrit a la
    # main et ne suivait plus les effectifs.
    z = NormalDist().inv_cdf(0.975) + NormalDist().inv_cdf(0.80)
    niveaux = [
        ("Une grandeur de saison", m["ruptures"]["saisons"], "ecart"),
        ("Une grandeur de saison, audience comprise", m["audience"]["saisons"], "ecart"),
        ("Une grandeur de participation", stats["sorties"]["effectif"], "ecart"),
        ("Une part au niveau du bulletin", m["homophilie"]["bulletins"], "part"),
        ("Une part sur les conseils mixtes", m["homophilie"]["bulletins_mixtes"], "part"),
        ("Une part sur le vote du jury", m["jury_final"]["bulletins"], "part"),
    ]
    m["puissance"] = []
    for libelle, n, nature in niveaux:
        if nature == "ecart":
            texte = f"{donnees.decimal_fr(round(z / math.sqrt(n), 2))} écart-type"
        else:
            texte = f"{donnees.decimal_fr(round(100 * 0.5 * z / math.sqrt(n), 1))} points"
        m["puissance"].append({"libelle": libelle, "observations": n,
                               "observations_texte": f"{n:,}".replace(",", "\u00a0"),
                               "effet_texte": texte})

    # /methode/ : les resultats retenus qui tiennent encore si l'on ajoute
    # vingt tests sans resultat (p = 1) au registre. La page l'affirmait
    # d'apres une verification faite une fois ; elle est refaite ici.
    ps = [t["p"] for t in m["registre"]]
    ajustees = modeles.benjamini_hochberg(ps + [1.0] * 20)
    m["retenus_avec_vingt_nuls"] = sum(
        1 for t, pa in zip(m["registre"], ajustees) if t["retenu"] and pa < 0.05)
    tombes = [f"« {t['libelle']} »" for t, pa in zip(m["registre"], ajustees)
              if t["retenu"] and pa >= 0.05]
    if not tombes:
        m["tombes_avec_vingt_nuls_texte"] = "aucun ne tombe"
    elif len(tombes) == 1:
        m["tombes_avec_vingt_nuls_texte"] = f"seul le plus fragile, {tombes[0]}, tomberait"
    else:
        m["tombes_avec_vingt_nuls_texte"] = (
            f"les {len(tombes)} plus fragiles tomberaient — "
            + ", ".join(tombes[:-1]) + " et " + tombes[-1])

    # /statistiques/audience/ : la part du public perdue d'un regime a l'autre
    # (« la moitie »), sur les moyennes non arrondies.
    au = m["audience"]
    au["perte_regimes"] = _arrondi_entier(100 * (1 - au["moyenne_apres"] / au["moyenne_avant"]))

    # /statistiques/vainqueurs/ : combien de fois le finaliste recoit les voix
    # du vainqueur (« du simple au double »).
    cr = stats["indicateurs"]["voix_des_vainqueurs"]["couples_resume"]
    cr["rapport"] = (round(cr["moyenne_finaliste"] / cr["moyenne_vainqueur"], 1)
                     if cr.get("moyenne_vainqueur") else None)

    # /statistiques/alliances/ et /jeu-social/ : combien de fois etre du bon
    # cote pese plus qu'une voix recue de plus par conseil.
    maj = m["alliances"]["majorite"]
    v0, v1 = maj["variables"][0], maj["variables"][1]
    maj["rapport"] = round(abs(v0["estimation"] / v1["estimation"]), 1) if v1["estimation"] else None

    # /statistiques/top/ : combien de fois l'ecart reel vaut celui du hasard,
    # et l'AUC du palmares en pourcentage.
    h, pl = c["hasard"], c["palmares"]
    h["rapport"] = round(h["reel_ecart"] / h["ecart"], 1) if h.get("ecart") else None
    pl["auc_pourcent"] = round(pl["auc"] * 100, 1) if pl.get("auc") is not None else None

    # /completude/ : la part la plus basse de conseils depouilles, par epoque.
    dep = c["biais_epoque"]["depouillement"]
    c["biais_epoque"]["depouillement_plus_bas"] = min(x["part"] for x in dep) if dep else None

    # /statistiques/revenants/ : « divisent la cote par N », l'inverse du
    # rapport de cotes.
    for x in m["rappel"]["coefficients"]:
        x["inverse"] = round(1.0 / x["rapport"], 2) if x.get("rapport") else None

    # /statistiques/audience/ : les audiences en millions. La page divisait
    # en ENTIERS (`divided_by: 100000`) : elle tronquait au lieu d'arrondir.
    a = m["audience"]
    for bloc in [a["sommet"], a["derniere"]] + list(a["jours"]):
        bloc["moyenne_millions"] = round(bloc["moyenne"] / 1e6, 1)
    for cle in ("moyenne_avant", "moyenne_apres"):
        a[f"{cle}_millions"] = round(a[cle] / 1e6, 1)

    # /statistiques/grille/ : ce que la croissance du casting represente en
    # episodes, puis en joueurs restants, d'apres les deux pentes.
    f = m["fusion"]
    croissance = f["croissance"] = f["casting_max"] - f["casting_min"]
    f["croissance_episode"] = round(croissance * f["pente_episode"]["pente"], 1)
    f["croissance_restants"] = round(croissance * f["pente_restants"]["pente"], 1)
    # « 0,9 episode », « 2 episodes » : le pluriel francais commence a deux.
    mot = "épisodes" if abs(f["croissance_episode"]) >= 2 else "épisode"
    f["croissance_episode_texte"] = f"{donnees.decimal_fr(f['croissance_episode'])} {mot}"
    # Le plateau reuni, en mediane, avec les plus petits puis les plus grands
    # castings : ce que le texte disait « d'une dizaine a une quinzaine ».
    for borne in ("min", "max"):
        restants = [l["restants"] for l in f["lignes"]
                    if l["casting"] == f[f"casting_{borne}"]]
        f[f"restants_casting_{borne}"] = float(median(restants))

    # « 0,9 episode », « 2 episodes » : le pluriel francais commence a deux.
    mot = "épisodes" if abs(f["croissance_episode"]) >= 2 else "épisode"
    f["croissance_episode_texte"] = f"{donnees.decimal_fr(f['croissance_episode'])} {mot}"
    # Le plateau reuni, en mediane, avec les plus petits puis les plus grands
    # castings : ce que le texte disait « d'une dizaine a une quinzaine ».
    for borne in ("min", "max"):
        restants = [l["restants"] for l in f["lignes"]
                    if l["casting"] == f[f"casting_{borne}"]]
        f[f"restants_casting_{borne}"] = float(median(restants))
    # Les bornes de la serie, que le texte ecrivait « de 2001 a 2026 ».
    annees = [l["annee"] for l in f["lignes"]]
    f["annee_min"], f["annee_max"] = min(annees), max(annees)

    # /statistiques/fusion/ : les ambassades dont la prose ne nomme pas les
    # ambassadeurs, que le texte comptait a la main (« les huit muettes »).
    ng = m["avant_apres"]["negociateurs"]
    ng["muettes"] = ng["total"] - ng["lues"]

    # /statistiques/conditionnelles/ : la part des conseils que la chaine
    # retient, que le texte ecrivait « un conseil sur six ».
    co = m["conditionnelles"]
    co["part_des_conseils"] = _arrondi_entier(
        100 * co["conseils"] / stats["conseils"]["conseils"])

    # /statistiques/conseils/ : la page nommait les combinaisons a la main, et
    # le libelle ecrit ne correspondait plus a l'indice affiche.
    qui = {"h": ("un homme", "un homme"), "f": ("une femme", "une femme")}
    vg = stats["conseils"]["vote_par_genre"]
    for x in vg:
        x["libelle"] = f"{qui[x['votant']][0]} contre {qui[x['cible']][1]}"
    parts = [x["part"] for x in vg]
    stats["conseils"]["vote_par_genre_ecart"] = round(max(parts) - min(parts), 1)
    # /completude/ : chaque case affiche sa part arrondie a l'unite, et la
    # derniere colonne prend le niveau du score de la ligne.
    for ligne in stats["completude_saisons"]["lignes"]:
        for x in ligne["cellules"]:
            x["valeur_arrondie"] = _arrondi_entier(x["valeur"] or 0)
        ligne["niveau"] = _niveau(ligne["score"] or 0)

    # Les barres dans les cellules (/saisons/, /statistiques/revenants/) : leur
    # largeur est du CSS, ou « 61,5% » n'est pas une longueur. Un entier suffit
    # a une barre de lecture.
    for x in stats["indicateurs"]["saisons"]:
        if isinstance(x.get("survie_moyenne"), (int, float)):
            x["barre"] = _arrondi_entier(x["survie_moyenne"])
    for x in stats["revenants"]["carrieres"]:
        x["barre"] = _arrondi_entier(x["part_du_temps"])


def poser_les_identifiants(noeud, index):
    """Pose `id` a cote de tout nom d'aventurier deja publie.

    POURQUOI UNE PASSE, ET PAS VINGT-TROIS CORRECTIONS. Vingt-trois listes de
    `_data/stats.yml` publiaient un nom d'aventurier sans son identifiant. Un
    gabarit ne pouvait donc pas construire le lien vers sa fiche, et des
    centaines de noms restaient du texte mort au milieu des tableaux -- alors
    que la page de la personne existe. Poser l'identifiant chez chaque
    producteur demandait vingt-trois retouches, et d'y penser a la
    vingt-quatrieme. Une passe sur l'arbre fini le fait une fois pour toutes,
    y compris pour les blocs ecrits plus tard.

    Elle n'ecrase jamais un `id` deja pose, et ne resout PAS un nom porte par
    deux personnes : mieux vaut un nom sans lien qu'un lien vers la mauvaise
    fiche. Les noms qui ne sont pas ceux d'un aventurier -- un presentateur,
    une tribu -- ne sont simplement pas dans l'index.
    """
    if isinstance(noeud, dict):
        if "id" not in noeud:
            for cle in ("nom", "aventurier"):
                cid = index.get(noeud.get(cle))
                if cid:
                    noeud["id"] = cid
                    break
        for valeur in noeud.values():
            poser_les_identifiants(valeur, index)
    elif isinstance(noeud, list):
        for valeur in noeud:
            poser_les_identifiants(valeur, index)


def index_des_noms(personnes):
    """Nom complet -> identifiant, les homonymes exclus."""
    par_nom = defaultdict(list)
    for g in personnes:
        if g.get("nom") and g.get("id"):
            par_nom[g["nom"]].append(g["id"])
    return {nom: ids[0] for nom, ids in par_nom.items() if len(ids) == 1}


def main():
    saisons, parts, personnes, conseils, epreuves, colliers, finale, par_saison = charger()
    classiques = perimetre(parts, avec_speciales=False)
    toutes = perimetre(parts, avec_speciales=True)

    stats = {
        "general": {
            "saisons_declarees": len(saisons),
            "saisons_diffusees": sum(1 for s in saisons if not s.get("annulee")),
            "saisons_classiques": sum(1 for s in saisons
                                      if not s.get("annulee") and not s.get("speciale")),
            "saisons_speciales": sum(1 for s in saisons
                                     if not s.get("annulee") and s.get("speciale")),
            "saisons_annulees": sum(1 for s in saisons if s.get("annulee")),
            "participations": len(parts),
            "personnes": len(personnes),
            "premiere_annee": min(s["annee"] for s in saisons if s.get("annee")),
            "derniere_annee": max(s["annee"] for s in saisons if s.get("annee")),
            "pays": len({s["pays"] for s in saisons if s.get("pays")}),
        },
        "vainqueurs": bloc_vainqueurs(classiques),
        "vainqueurs_toutes": bloc_vainqueurs(toutes),
        "couleurs": bloc_couleurs(classiques),
        "metiers": bloc_metiers(classiques),
        "metiers_toutes": bloc_metiers(toutes),
        "genre": bloc_genre(classiques),
        "sorties": bloc_sorties(classiques),
        "sorties_toutes": bloc_sorties(toutes),
        "age": bloc_age(classiques),
        "saisons": bloc_saisons(saisons, parts),
        "records": bloc_records(toutes, personnes),
        "conseils": bloc_conseils(conseils, parts, par_saison),
        "jury": bloc_jury(conseils, parts, par_saison),
        "finale": bloc_finale(finale, parts, par_saison),
        "natures": bloc_natures(_fichier_data("epreuves_nommees.yml"), parts, par_saison),
        # --- les analyses ajoutees ensuite. Elles prennent les participations
        # brutes, sans le filtre « saisons classiques » applique plus haut :
        # chacune dit elle-meme sur quel perimetre elle porte.
        "revenants": analyses.revenants(par_saison, parts, personnes),
        "risque": analyses.risque(par_saison, parts),
        "survie_saisons": analyses.survie_par_saison(par_saison, parts),
        "survie_bandeau": analyses.survie_par_bandeau(par_saison, parts),
        "casting": analyses.casting(par_saison, parts),
        "programme": analyses.programme(par_saison),
        "reciprocite": analyses.reciprocite(eliminations(conseils), parts, par_saison),
        "arc_des_votes": analyses.arc_des_votes(eliminations(conseils), parts, par_saison),
        "voix_pour_eliminer": analyses.voix_pour_eliminer(
            [c for c in eliminations(conseils)
             if not par_saison.get(c["saison"], {}).get("en_cours")]),
        "premiere_epreuve": analyses.premiere_epreuve(par_saison, parts, epreuves),
        "epreuves": bloc_epreuves(epreuves, conseils, parts, saisons, par_saison),
        "colliers": bloc_colliers(colliers, par_saison, parts),
        "indicateurs": bloc_indicateurs(saisons, parts, conseils, epreuves, colliers,
                                        par_saison),
        "completude": bloc_completude(parts, personnes),
        "palmares": bloc_palmares(parts, epreuves, par_saison),
    }

    # Le classement des joueurs vient AVANT les modeles : son test de
    # stabilite entre dans le meme registre corrige, et un test qu'on
    # n'ajoute qu'apres avoir vu la correction n'est plus un test.
    stats["classement"] = classement.tout(saisons, parts, conseils, epreuves)

    # Meme regle pour la prevision hors echantillon : son test rejoint le
    # registre commun, donc il doit exister AVANT que la correction de
    # Benjamini-Hochberg soit calculee. Elle a besoin de l'episode de
    # reunification, qu'on lui calcule ici -- `modeles.tout` le refera pour son
    # propre compte, et c'est le prix a payer pour que l'ordre reste celui-la.
    stats["prevision"] = prevision.tout(
        par_saison, parts, conseils, epreuves,
        modeles.fusion(par_saison, parts, conseils, epreuves))

    # Les modeles viennent en dernier : ils s'appuient sur les indicateurs de
    # saison calcules juste au-dessus, et ce sont les seuls calculs du fichier
    # a reposer sur un tirage. Leur graine est fixe (modeles.GRAINE) et
    # `tools/verifie_site.py` refuse tout tirage qui n'en derive pas.
    stats["modeles"] = modeles.tout(
        par_saison, parts, conseils, epreuves,
        (stats["indicateurs"] or {}).get("saisons") or [],
        tests_externes=((stats["classement"] or {}).pop("tests", [])
                        + (stats["prevision"] or {}).pop("tests", [])))

    stats["completude_saisons"] = bloc_completude_saisons(
        saisons, parts, conseils, epreuves, colliers, stats["modeles"], finale)

    # Les articles citent des resultats du registre : ils les lisent apres
    # lui, mis en forme, avec ce que leur texte en affirme. Voir articles.py.
    stats["articles"] = articles.tout(stats, conseils, par_saison)

    # les records renvoient des participations entieres : on n'en garde que l'utile
    for cle in ("plus_jeune_vainqueur", "plus_age_vainqueur"):
        p = stats["records"].get(cle)
        if p:
            stats["records"][cle] = {
                "nom": p.get("nom_complet") or p.get("nom"), "age": p.get("age"),
                "saison": p["saison"], "annee": p["_annee"],
                "titre": p["_saison"].get("titre"),
            }

    # /statistiques/finale/ : les saisons jouees ecartees parce que leur fin
    # n'a pas le format a trois aux poteaux, que le texte comptait « trois ».
    couv = (stats["finale"] or {}).get("couverture")
    if couv:
        jouees = sum(1 for s in saisons if not s.get("annulee") and not s.get("en_cours"))
        couv["hors_format"] = jouees - couv["saisons_au_format"]

    # /statistiques/geographie/ : les saisons classiques dont le casting n'est
    # pas entierement localise, que la page enumerait a la main. Meme
    # definition que la couverture de tools/extraction/geographie_insee.py.
    lacunaires = []
    for s in sorted(saisons, key=lambda x: x.get("annee") or 0):
        if s.get("annulee") or s.get("speciale"):
            continue
        gens = [p for p in parts if p["saison"] == s["id"]]
        localisees = sum(1 for p in gens if p.get("localisation"))
        if gens and localisees < len(gens):
            lacunaires.append({"titre": s.get("titre"), "annee": s.get("annee"),
                               "localisees": localisees, "effectif": len(gens)})
    stats["geographie"] = {"lacunaires": lacunaires}
    # Le grain departemental : personnes par departement (« quatre »).
    chemin_geo = os.path.join(RACINE, "_data", "geographie.yml")
    if os.path.exists(chemin_geo):
        geo = donnees.charger(open(chemin_geo, encoding="utf-8"))
        if geo.get("departements"):
            stats["geographie"]["par_departement"] = round(
                geo["participations"] / len(geo["departements"]), 1)

    # /sources/ : ce que les recits de reparation citent au present. Chaque
    # compte y etait ecrit a la main, au jour de la reparation, et ne suivait
    # plus les donnees.
    hors_jury = [c for c in conseils if c.get("type") != "jury"]
    avec_elimine = [c for c in hors_jury if c.get("elimine")]
    cs = stats["conseils"]
    cs["conseils_hors_jury"] = len(hors_jury)
    cs["elimines_rattaches"] = sum(1 for c in avec_elimine if c.get("elimine_rattache"))
    cs["elimines_non_rattaches"] = len(avec_elimine) - cs["elimines_rattaches"]
    # Les bulletins lus, rapportes aux voix que les matrices annoncent.
    annonces = [c for c in hors_jury if c.get("votes_exprimes")]
    cs["part_bulletins_lus"] = part(sum(len(c.get("votes") or []) for c in annonces),
                                    sum(c["votes_exprimes"] for c in annonces))
    # Les voix que personne n'ecrit : vote noir, penalite, malediction.
    annee = {s["id"]: s.get("annee") for s in saisons}
    sans = [(c["saison"], v["mecanique"]) for c in conseils
            for v in c.get("votes") or [] if v.get("mecanique")]
    if sans:
        par_motif = Counter(m_ for _, m_ in sans).most_common()
        cs["sans_votant"] = {
            "bulletins": len(sans),
            "saisons": len({s for s, _ in sans}),
            "annee_min": min(annee[s] for s, _ in sans),
            "annee_max": max(annee[s] for s, _ in sans),
            "detail_texte": ", ".join(f"{n} « {m_} »" for m_, n in par_motif),
        }
    # Le vote du jury : une colonne par finaliste, et le controle « le
    # decompte annonce egale les bulletins lus » scrutin par scrutin.
    jury = [c for c in conseils if c.get("type") == "jury"]
    par_scrutin = defaultdict(list)
    for c in jury:
        par_scrutin[c["saison"]].append(c)
    # /statistiques/jeu-social/ et /sources/ : la base de la justesse de vote,
    # conseils complets dont l'elimine est rattache (« quelques dizaines »).
    cs["conseils_justesse"] = sum(1 for c in eliminations(conseils)
                                  if c.get("complet") and c.get("elimine_rattache"))
    # /sources/ : les conseils dont l'elimine a pourtant fini la saison -- des
    # retours en jeu, que `sort` ne sait pas dire.
    fin = {(p["saison"], p["id"]) for p in parts if p.get("sort") in ("vainqueur", "finaliste")}
    cs["retours_en_jeu"] = sum(1 for c in eliminations(conseils) if c.get("elimine_rattache")
                               and (c["saison"], c["elimine"]) in fin)
    stats["jury"]["lignes"] = len(jury)
    stats["jury"]["bulletins_lus"] = sum(len(c.get("votes") or []) for c in jury)
    stats["jury"]["decomptes_discordants"] = sum(
        1 for lot in par_scrutin.values()
        if max(c.get("votes_exprimes") or 0 for c in lot)
        and max(c.get("votes_exprimes") or 0 for c in lot)
        != sum(len(c.get("votes") or []) for c in lot))
    # /sources/ : le rattachement des noms -- colliers et vainqueurs d'epreuve.
    cites = [d for c in colliers for cle in ("detenteurs", "detenteurs_suivants", "proteges")
             for d in c.get(cle) or [] if isinstance(d, dict)]
    gagnants = [x for e in epreuves for x in e.get("vainqueurs") or []]
    restants = [x for x in gagnants if not x.get("resolu")]
    stats["rattachement"] = {
        "colliers": len(cites),
        "colliers_rattaches": sum(1 for d in cites if d.get("resolu")),
        "vainqueurs": len(gagnants),
        "vainqueurs_rattaches": len(gagnants) - len(restants),
        "vainqueurs_restants_personnes": sum(1 for x in restants if x.get("type") == "personne"),
        "vainqueurs_restants_texte": ", ".join(sorted({x.get("libelle") or "?" for x in restants})),
    }
    # /sources/ : le palmares des saisons sans bilan d'epreuves, que seules
    # les fiches individuelles donnent.
    sans_bilan = set(stats["epreuves"].get("saisons_sans_donnee") or [])
    gens = [p for p in parts if p["saison"] in sans_bilan]
    stats["epreuves"]["palmares_sans_bilan"] = {
        "participations": len(gens),
        "renseignees": sum(1 for p in gens if p.get("victoires_individuelles") is not None),
    }
    # /sources/ : les saisons ou le rang final et le jour de sortie rangent
    # les aventuriers dans le meme ordre.
    concordantes = comparees = 0
    for s in saisons:
        if s.get("annulee") or s.get("en_cours"):
            continue
        g = [p for p in parts if p["saison"] == s["id"]
             and p.get("classement") and p.get("jour_sortie")]
        if len(g) < 2:
            continue
        comparees += 1
        concordantes += not any(a["classement"] < b["classement"]
                                and a["jour_sortie"] < b["jour_sortie"]
                                for a in g for b in g)
    stats["general"]["rang_concordant"] = concordantes
    stats["general"]["rang_compare"] = comparees
    stats["general"]["etendue_annees"] = (stats["general"]["derniere_annee"]
                                          - stats["general"]["premiere_annee"])

    # /sources/ : le controle des audiences -- la moyenne des mesures par
    # episode confrontee a la moyenne annoncee pour la saison.
    chemin_aud = os.path.join(RACINE, "_data", "audiences.yml")
    if os.path.exists(chemin_aud):
        aud = donnees.charger(open(chemin_aud, encoding="utf-8"))
        mesures = defaultdict(list)
        for e in aud.get("episodes") or []:
            if e.get("telespectateurs"):
                mesures[e["saison"]].append(e["telespectateurs"])
        controle, ecarts, ecart_max = 0, [], 0.0
        for s in aud.get("saisons") or []:
            if s.get("moyenne") and mesures.get(s["saison"]):
                controle += 1
                ecart = mean(mesures[s["saison"]]) / s["moyenne"] - 1
                if abs(ecart) > 0.005:
                    ecarts.append(f"*{s['titre']}*")
                    ecart_max = max(ecart_max, abs(ecart))
        stats["audience_controle"] = {
            "saisons": controle,
            "concordantes": controle - len(ecarts),
            "discordantes_texte": (", ".join(ecarts[:-1]) + " et " + ecarts[-1]
                                   if len(ecarts) > 1 else "".join(ecarts)),
            "ecart_max": _arrondi_entier(100 * ecart_max),
            "recettes": sum(1 for s in aud.get("saisons") or []
                            if s.get("recettes_publicitaires")),
        }

    champs_d_affichage(stats)
    champs_du_texte(stats, saisons, parts)
    formes_des_gabarits(stats)
    poser_les_identifiants(stats, index_des_noms(personnes))

    chemin = os.path.join(RACINE, "_data", "stats.yml")
    with open(chemin, "w", encoding="utf-8") as f:
        f.write(ENTETE)
        donnees.ecrire(stats, f, allow_unicode=True, sort_keys=False, width=100)

    g = stats["general"]
    print(f"ecrit : {chemin}")
    m = stats.get("modeles") or {}
    if m:
        print(f"  modeles : {m['nb_tests']} tests declares, {m['nb_retenus']} retenus "
              f"apres Benjamini-Hochberg ; force estimee sur "
              f"{(m.get('force') or {}).get('epreuves_retenues', 0)} epreuves")
    print(f"  {g['saisons_diffusees']} saisons diffusees "
          f"({g['saisons_classiques']} classiques, {g['saisons_speciales']} speciales), "
          f"{g['participations']} participations, {g['personnes']} personnes")
    v = stats["vainqueurs"]
    print(f"  vainqueurs : age moyen {v['age_moyen']} ans, "
          f"{v['part_40_et_plus']} % de 40 ans et plus")
    c = stats["conseils"]
    print(f"  conseils : {c['conseils']} dont {c['conseils_complets']} complets, "
          f"{c['bulletins']} bulletins, {c['voix_annulees_par_objet']} voix annulees "
          f"par un objet et {c['voix_annulees_tour_nul']} par un tour nul")
    co = stats.get("colliers") or {}
    if co:
        print(f"  colliers : {co['colliers']} sur {co['saisons_couvertes']} saisons, "
              f"{co['voix_annulees']} voix annulees")
    ind = stats.get("indicateurs") or {}
    if ind:
        print(f"  indicateurs : {ind['mesurables']} participations mesurables, "
              f"{ind['nb_fantomes']} fantomes")
    cl = stats.get("classement") or {}
    if cl:
        print(f"  classement : {cl['joueurs_classes']} joueurs, "
              f"{cl['participations_classees']} participations ; "
              f"{cl['robustesse']['candidats']} entrent dans le top "
              f"{cl['taille']} selon les poids, {cl['robustesse']['socle']} y "
              f"sont sous plus de 99 % des ponderations")
    e = stats.get("epreuves") or {}
    if e:
        print(f"  epreuves : {e['epreuves']} sur {e['saisons_couvertes']} saisons, "
              f"{e['individuelles']} individuelles, "
              f"{len(e['classement_ratio'])} ratios calculables")
    return 0


if __name__ == "__main__":
    sys.exit(main())
