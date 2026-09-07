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
import os
import sys
from collections import Counter, defaultdict
from statistics import mean, median

import yaml

RACINE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(RACINE, "tools", "extraction"))
from csp import classer, libelles           # noqa: E402
import analyses
import modeles                              # noqa: E402
import classement                           # noqa: E402
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
        return yaml.safe_load(open(chemin, encoding="utf-8")) if os.path.exists(chemin) else []

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


def bloc_colliers(colliers, par_saison):
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

    return {
        "colliers": total,
        "trouves": len(trouves),
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
        if c.get("type") != "jury":
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
        return yaml.safe_load(f) or {}


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
        "colliers": bloc_colliers(colliers, par_saison),
        "indicateurs": bloc_indicateurs(saisons, parts, conseils, epreuves, colliers,
                                        par_saison),
        "completude": bloc_completude(parts, personnes),
        "palmares": bloc_palmares(parts, epreuves, par_saison),
    }

    # Le classement des joueurs vient AVANT les modeles : son test de
    # stabilite entre dans le meme registre corrige, et un test qu'on
    # n'ajoute qu'apres avoir vu la correction n'est plus un test.
    stats["classement"] = classement.tout(saisons, parts, conseils, epreuves)

    # Les modeles viennent en dernier : ils s'appuient sur les indicateurs de
    # saison calcules juste au-dessus, et ce sont les seuls calculs du fichier
    # a reposer sur un tirage. Leur graine est fixe (modeles.GRAINE) et
    # `tools/verifie_site.py` refuse tout tirage qui n'en derive pas.
    stats["modeles"] = modeles.tout(
        par_saison, parts, conseils, epreuves,
        (stats["indicateurs"] or {}).get("saisons") or [],
        tests_externes=(stats["classement"] or {}).pop("tests", []))

    stats["completude_saisons"] = bloc_completude_saisons(
        saisons, parts, conseils, epreuves, colliers, stats["modeles"], finale)

    # les records renvoient des participations entieres : on n'en garde que l'utile
    for cle in ("plus_jeune_vainqueur", "plus_age_vainqueur"):
        p = stats["records"].get(cle)
        if p:
            stats["records"][cle] = {
                "nom": p.get("nom_complet") or p.get("nom"), "age": p.get("age"),
                "saison": p["saison"], "annee": p["_annee"],
                "titre": p["_saison"].get("titre"),
            }

    chemin = os.path.join(RACINE, "_data", "stats.yml")
    with open(chemin, "w", encoding="utf-8") as f:
        f.write(ENTETE)
        yaml.safe_dump(stats, f, allow_unicode=True, sort_keys=False, width=100)

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
